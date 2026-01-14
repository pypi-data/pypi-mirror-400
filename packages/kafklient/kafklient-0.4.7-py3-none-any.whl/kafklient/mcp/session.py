from __future__ import annotations

import logging
from contextlib import asynccontextmanager, nullcontext
from datetime import timedelta
from typing import TYPE_CHECKING, Any, AsyncIterator

import anyio
from anyio.lowlevel import checkpoint
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp.shared.message import SessionMessage

from kafklient.mcp.client import kafka_client_transport
from kafklient.mcp.server import Server

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from mcp.client.session import ClientSession


def _require_client_session() -> type[ClientSession]:
    try:
        from mcp.client.session import ClientSession as _ClientSession
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "MCP ClientSession is not available. Install MCP dependencies, e.g. `pip install kafklient[mcp]`."
        ) from e
    return _ClientSession


@asynccontextmanager
async def kafka_client_session(
    bootstrap_servers: str,
    *,
    consumer_topic: str = "mcp-responses",
    producer_topic: str = "mcp-requests",
    consumer_group_id: str | None = None,
    isolate_session: bool = True,
    auto_create_topics: bool = True,
    assignment_timeout_s: float = 5.0,
    read_timeout_seconds: timedelta | None = None,
    initialize: bool = True,
) -> AsyncIterator[ClientSession]:
    """
    Create an MCP `ClientSession` that communicates over Kafka topics (no subprocess/stdio bridge needed).

    This is the programmatic alternative to:
    - spawning `kafklient mcp-client` via `StdioServerParameters`
    - connecting to that subprocess with `mcp.client.stdio.stdio_client`

    Args:
        bootstrap_servers: Kafka bootstrap servers.
        consumer_topic: Response topic to consume from.
        producer_topic: Request topic to produce to.
        consumer_group_id: Consumer group id for the response consumer.
        isolate_session: If True, filter responses by a per-session id to avoid mixing on shared topics.
        auto_create_topics: Best-effort topic creation.
        assignment_timeout_s: Kafka consumer assignment timeout.
        read_timeout_seconds: Optional MCP client read timeout.
        initialize: If True, call `session.initialize()` before yielding.
    """
    ClientSession = _require_client_session()

    session_id: bytes | None
    if isolate_session:
        # Keep this aligned with `run_client_async` behavior: a stable session id for filtering.
        # Note: uuid4 is imported inside `kafka_client_transport` module; we avoid duplicating it here.
        import uuid

        session_id = uuid.uuid4().hex.encode("utf-8")
    else:
        session_id = None

    async with kafka_client_transport(
        bootstrap_servers=bootstrap_servers,
        consumer_topic=consumer_topic,
        producer_topic=producer_topic,
        consumer_group_id=consumer_group_id,
        auto_create_topics=auto_create_topics,
        assignment_timeout_s=assignment_timeout_s,
        session_id=session_id,
    ) as (read_stream, write_stream):
        session_kwargs: dict[str, Any] = {}
        if read_timeout_seconds is not None:
            session_kwargs["read_timeout_seconds"] = read_timeout_seconds

        async with ClientSession(read_stream, write_stream, **session_kwargs) as session:
            if initialize:
                await session.initialize()
            yield session


@asynccontextmanager
async def inprocess_client_session(
    server: Server,
    *,
    read_timeout_seconds: timedelta | None = None,
    initialize: bool = True,
) -> AsyncIterator[ClientSession]:
    """
    Create an MCP `ClientSession` connected to a Python-native server instance in-process.

    This avoids stringly-typed subprocess configs (`StdioServerParameters`) entirely by wiring the
    client/server streams directly.
    """
    ClientSession = _require_client_session()

    try:
        from fastmcp.server.tasks.capabilities import get_task_capabilities
        from fastmcp.utilities.logging import temporary_log_level
        from mcp.server.lowlevel.server import NotificationOptions
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "In-process MCP session requires MCP server dependencies. Install `kafklient[mcp]`."
        ) from e

    # Mirror `run_server_async` init behavior (capabilities + notifications).
    mcp_server = server._mcp_server  # pyright: ignore[reportPrivateUsage]
    experimental_capabilities = get_task_capabilities()
    init_opts = mcp_server.create_initialization_options(
        notification_options=NotificationOptions(tools_changed=True),
        experimental_capabilities=experimental_capabilities,
    )

    # Some server implementations (external fastmcp) have a lifespan manager; keep behavior consistent.
    try:
        import fastmcp as _fastmcp

        context_manager = server._lifespan_manager() if isinstance(server, _fastmcp.FastMCP) else nullcontext()
    except Exception:
        context_manager = nullcontext()

    # Stream wiring:
    # - client writes -> server reads
    # - server writes -> client reads
    c2s_send, c2s_recv = anyio.create_memory_object_stream[SessionMessage](0)
    s2c_send, s2c_recv = anyio.create_memory_object_stream[SessionMessage](0)

    cancelled_exc = anyio.get_cancelled_exc_class()

    async def run_server_session() -> None:
        try:
            await mcp_server.run(c2s_recv, s2c_send, init_opts)
        except cancelled_exc:
            await checkpoint()
        except BaseException:
            logger.exception("In-process MCP server session crashed")
        finally:
            for s in (c2s_recv, s2c_send):
                try:
                    await s.aclose()
                except Exception:
                    pass

    session_kwargs: dict[str, Any] = {}
    if read_timeout_seconds is not None:
        session_kwargs["read_timeout_seconds"] = read_timeout_seconds

    with temporary_log_level(None):
        async with context_manager:
            async with anyio.create_task_group() as tg:
                tg.start_soon(run_server_session)
                try:
                    async with ClientSession(s2c_recv, c2s_send, **session_kwargs) as session:
                        if initialize:
                            await session.initialize()
                        yield session
                finally:
                    # Ensure the background server task is stopped.
                    tg.cancel_scope.cancel()
                    for s in (c2s_send, s2c_recv):
                        try:
                            await s.aclose()
                        except Exception:
                            pass


