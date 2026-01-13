"""
Session - High-level interface for interacting with an agent session
"""

from __future__ import annotations

from typing import Any, AsyncIterator

from acp_factory.types import (
    ExtendedSessionUpdate,
    FlushOptions,
    FlushResult,
    PromptContent,
)


class Session:
    """Represents an active session with an agent"""

    def __init__(
        self,
        session_id: str,
        connection: Any,  # TODO: Type from acp library
        client_handler: Any,  # TODO: Type from acp library
        cwd: str,
        modes: list[str] | None = None,
        models: list[str] | None = None,
    ) -> None:
        self.id = session_id
        self.cwd = cwd
        self.modes = modes or []
        self.models = models or []
        self._connection = connection
        self._client_handler = client_handler
        self.is_processing = False

    async def prompt(self, content: PromptContent) -> AsyncIterator[ExtendedSessionUpdate]:
        """
        Send a prompt and stream responses.

        In interactive permission mode, this may yield PermissionRequestUpdate objects
        that require a response via respond_to_permission() before the prompt can continue.
        """
        self.is_processing = True

        try:
            # Convert string to ContentBlock list
            prompt_blocks: list[dict[str, Any]]
            if isinstance(content, str):
                prompt_blocks = [{"type": "text", "text": content}]
            else:
                prompt_blocks = content

            # TODO: Implement using ACP connection
            # This is a placeholder - actual implementation will use the acp library
            # stream = self._client_handler.get_session_stream(self.id)
            # prompt_task = asyncio.create_task(
            #     self._connection.prompt(session_id=self.id, prompt=prompt_blocks)
            # )

            # Placeholder: yield nothing for now
            if False:  # pragma: no cover
                yield {}

        finally:
            self.is_processing = False

    async def cancel(self) -> None:
        """Cancel the current prompt"""
        # TODO: Implement using ACP connection
        # await self._connection.cancel(session_id=self.id)
        pass

    async def interrupt_with(
        self, content: PromptContent
    ) -> AsyncIterator[ExtendedSessionUpdate]:
        """
        Interrupt the current prompt and start a new one with additional context.

        This cancels any in-progress prompt and immediately starts a new prompt.
        The agent will restart its work but retains the conversation history.
        """
        await self.cancel()

        # Small delay to allow cancellation to propagate
        import asyncio

        await asyncio.sleep(0.05)

        async for update in self.prompt(content):
            yield update

    async def set_mode(self, mode: str) -> None:
        """Set the session mode"""
        # TODO: Implement using ACP connection
        # await self._connection.set_session_mode(session_id=self.id, mode_id=mode)
        pass

    async def fork(self) -> Session:
        """
        Fork this session to create a new independent session.

        The forked session inherits the conversation history, allowing
        operations like generating summaries without affecting this session.
        """
        # TODO: Implement using ACP connection
        # result = await self._connection.unstable_fork_session(...)
        return Session(
            session_id="",  # Placeholder
            connection=self._connection,
            client_handler=self._client_handler,
            cwd=self.cwd,
            modes=self.modes,
            models=self.models,
        )

    async def fork_with_flush(
        self,
        idle_timeout: int = 5000,
        persist_timeout: int = 5000,
    ) -> Session:
        """
        Fork a running session by flushing it to disk first.

        This method handles forking a session that is currently active.
        """
        # Wait for idle or interrupt
        became_idle = await self._wait_for_idle(idle_timeout)
        if not became_idle and self.is_processing:
            await self.cancel()
            import asyncio

            await asyncio.sleep(0.5)

        # TODO: Call the agent's flush extension method
        # flush_result = await self._connection.ext_method("_session/flush", {...})

        # TODO: Restart original session
        # await self._restart_session()

        # TODO: Create forked session
        # result = await self._connection.unstable_fork_session(...)
        return Session(
            session_id="",  # Placeholder
            connection=self._connection,
            client_handler=self._client_handler,
            cwd=self.cwd,
            modes=self.modes,
            models=self.models,
        )

    def respond_to_permission(self, request_id: str, option_id: str) -> None:
        """
        Respond to a permission request (for interactive permission mode).

        When using permission_mode="interactive", permission requests are emitted
        as session updates. Call this method to allow the prompt to continue.
        """
        # TODO: Implement using client handler
        # self._client_handler.respond_to_permission(request_id, option_id)
        pass

    def cancel_permission(self, request_id: str) -> None:
        """
        Cancel a permission request (for interactive permission mode).

        This will cancel the permission request, which typically aborts the tool call.
        """
        # TODO: Implement using client handler
        # self._client_handler.cancel_permission(request_id)
        pass

    def has_pending_permissions(self) -> bool:
        """Check if there are any pending permission requests for this session"""
        # TODO: Implement using client handler
        # return len(self._client_handler.get_pending_permission_ids(self.id)) > 0
        return False

    def get_pending_permission_ids(self) -> list[str]:
        """Get all pending permission request IDs for this session"""
        # TODO: Implement using client handler
        # return self._client_handler.get_pending_permission_ids(self.id)
        return []

    async def flush(self, options: FlushOptions | None = None) -> FlushResult:
        """
        Flush session to disk, creating a checkpoint without forking.

        Use this for creating checkpoints that can later be forked or restored.
        """
        options = options or FlushOptions()

        try:
            # Wait for idle or timeout
            became_idle = await self._wait_for_idle(options.idle_timeout)
            if not became_idle and self.is_processing:
                await self.cancel()
                import asyncio

                await asyncio.sleep(0.5)

            # TODO: Call the agent's flush extension method
            # flush_result = await self._connection.ext_method("_session/flush", {...})

            # TODO: Restart session
            # await self._restart_session()

            return FlushResult(success=True, file_path=None)

        except Exception as e:
            return FlushResult(success=False, error=str(e))

    async def _wait_for_idle(self, timeout: int = 5000) -> bool:
        """Wait for the session to become idle (not processing a prompt)"""
        import asyncio

        start = asyncio.get_event_loop().time()
        timeout_sec = timeout / 1000

        while asyncio.get_event_loop().time() - start < timeout_sec:
            if not self.is_processing:
                return True
            await asyncio.sleep(0.1)

        return False

    async def _restart_session(self) -> Session:
        """Restart this session after it has been flushed to disk"""
        # TODO: Implement using ACP connection
        # result = await self._connection.load_session(...)
        return Session(
            session_id=self.id,
            connection=self._connection,
            client_handler=self._client_handler,
            cwd=self.cwd,
            modes=self.modes,
            models=self.models,
        )
