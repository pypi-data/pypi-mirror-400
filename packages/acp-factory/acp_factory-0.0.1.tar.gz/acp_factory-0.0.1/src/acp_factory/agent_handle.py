"""
AgentHandle - Represents a running agent with an ACP connection
"""

from __future__ import annotations

import asyncio
from asyncio.subprocess import Process
from typing import Any

from acp_factory.types import (
    AgentConfig,
    ForkSessionOptions,
    SessionOptions,
    SpawnOptions,
)


class AgentHandle:
    """Handle to a running agent process with ACP connection"""

    def __init__(
        self,
        process: Process,
        connection: Any,  # TODO: Type from acp library
        client_handler: Any,  # TODO: Type from acp library
        capabilities: dict[str, Any],
    ) -> None:
        self._process = process
        self._connection = connection
        self._client_handler = client_handler
        self.capabilities = capabilities
        self._sessions: dict[str, "Session"] = {}

    @classmethod
    async def create(
        cls,
        config: AgentConfig,
        options: SpawnOptions,
    ) -> AgentHandle:
        """Create and initialize an agent handle"""
        import os

        # Merge environment variables
        env = {**os.environ, **config.env, **options.env}

        # Spawn subprocess
        process = await asyncio.create_subprocess_exec(
            config.command,
            *config.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=None,  # Inherit stderr
            env=env,
        )

        if process.stdin is None or process.stdout is None:
            process.kill()
            raise RuntimeError("Failed to get agent process stdio streams")

        # TODO: Set up NDJSON streams and ACP connection using agent-client-protocol
        # This is a placeholder - actual implementation will use the acp library
        connection = None
        client_handler = None
        capabilities: dict[str, Any] = {}

        return cls(process, connection, client_handler, capabilities)

    async def create_session(
        self,
        cwd: str,
        options: SessionOptions | None = None,
    ) -> "Session":
        """Create a new session with the agent"""
        from acp_factory.session import Session

        options = options or SessionOptions()

        # TODO: Implement using ACP connection
        # result = await self._connection.new_session(...)
        session_id = ""  # Placeholder
        modes: list[str] = []
        models: list[str] = []

        session = Session(
            session_id=session_id,
            connection=self._connection,
            client_handler=self._client_handler,
            cwd=cwd,
            modes=modes,
            models=models,
        )

        self._sessions[session_id] = session
        return session

    async def load_session(
        self,
        session_id: str,
        cwd: str,
        mcp_servers: list[dict[str, str]] | None = None,
    ) -> "Session":
        """Load an existing session by ID"""
        from acp_factory.session import Session

        mcp_servers = mcp_servers or []

        if not self.capabilities.get("loadSession"):
            raise RuntimeError("Agent does not support loading sessions")

        # TODO: Implement using ACP connection
        modes: list[str] = []
        models: list[str] = []

        session = Session(
            session_id=session_id,
            connection=self._connection,
            client_handler=self._client_handler,
            cwd=cwd,
            modes=modes,
            models=models,
        )

        self._sessions[session_id] = session
        return session

    async def fork_session(
        self,
        session_id: str,
        cwd: str,
        options: ForkSessionOptions | None = None,
    ) -> "Session":
        """Fork an existing session to create a new independent session"""
        from acp_factory.session import Session

        options = options or ForkSessionOptions()

        session_caps = self.capabilities.get("sessionCapabilities", {})
        if not session_caps.get("fork"):
            raise RuntimeError("Agent does not support forking sessions")

        source_session = self._sessions.get(session_id)

        # Determine if flush is needed
        needs_flush = (
            options.force_flush
            or (source_session is not None and source_session.is_processing)
            or source_session is None
        )

        if needs_flush and source_session is not None:
            forked_session = await source_session.fork_with_flush(
                idle_timeout=options.idle_timeout,
                persist_timeout=options.persist_timeout,
            )
            self._sessions[forked_session.id] = forked_session
            return forked_session

        # TODO: Direct fork for persisted idle sessions
        # result = await self._connection.unstable_fork_session(...)
        new_session_id = ""  # Placeholder
        modes: list[str] = []
        models: list[str] = []

        forked_session = Session(
            session_id=new_session_id,
            connection=self._connection,
            client_handler=self._client_handler,
            cwd=cwd,
            modes=modes,
            models=models,
        )

        self._sessions[new_session_id] = forked_session
        return forked_session

    async def close(self) -> None:
        """Close the agent connection and terminate the process"""
        self._process.kill()
        await self._process.wait()

    def get_connection(self) -> Any:
        """Get the underlying connection (for advanced use)"""
        return self._connection

    def is_running(self) -> bool:
        """Check if the agent process is still running"""
        return self._process.returncode is None


# Import Session at runtime to avoid circular imports
from acp_factory.session import Session  # noqa: E402, F401
