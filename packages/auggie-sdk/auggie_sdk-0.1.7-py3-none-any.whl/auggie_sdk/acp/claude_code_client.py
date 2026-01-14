"""
ACP Client for Claude Code via Zed's ACP Adapter

This module provides a client for communicating with Claude Code through
the @zed-industries/claude-code-acp adapter, which wraps the Claude Code SDK
to speak the Agent Client Protocol.
"""

import asyncio
import os
import shutil
from queue import Empty, Queue
from threading import Thread
from typing import List, Optional

from acp import (
    ClientSideConnection,
    InitializeRequest,
    NewSessionRequest,
    PromptRequest,
    PROTOCOL_VERSION,
    spawn_agent_process,
    text_block,
)
from acp.schema import Implementation

from auggie_sdk.acp.client import ACPClient, AgentEventListener, _InternalACPClient
from auggie_sdk.context.version import get_sdk_version


class ClaudeCodeACPClient(ACPClient):
    """
    Synchronous ACP client for Claude Code via Zed's adapter.

    This client provides a simple interface for:
    - Starting/stopping Claude Code agent
    - Sending messages and getting responses
    - Listening to agent events (messages, tool calls, etc.)
    - Clearing session context

    Example:
        ```python
        # Create a client with API key
        client = ClaudeCodeACPClient(
            api_key="...",
            model="claude-3-5-sonnet-latest"
        )

        # Start the agent
        client.start()

        # Send a message
        response = client.send_message("What is 2 + 2?")
        print(response)

        # Stop the agent
        client.stop()
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        listener: Optional[AgentEventListener] = None,
        model: Optional[str] = None,
        workspace_root: Optional[str] = None,
        adapter_path: Optional[str] = None,
        cli_args: Optional[List[str]] = None,
    ):
        """
        Initialize the Claude Code ACP client.

        Args:
            api_key: Anthropic API key. If None, uses ANTHROPIC_API_KEY env var.
            listener: Optional event listener to receive agent events.
            model: AI model to use (e.g., "claude-3-5-sonnet-latest").
                   If None, uses Claude Code's default model.
            workspace_root: Workspace root directory. If None, uses current directory.
            adapter_path: Path to claude-code-acp executable. If None, uses 'npx @zed-industries/claude-code-acp'.
            cli_args: Optional list of additional command-line arguments to pass to the CLI.
                     These arguments are appended after all other CLI arguments (e.g.,
                     ["--verbose", "--debug"]). Use this for passing custom or experimental
                     CLI flags that aren't exposed as dedicated parameters.

        Raises:
            ValueError: If API key is not provided and not in environment
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY must be provided either as argument or environment variable"
            )

        self.listener = listener
        self.model = model
        self.workspace_root = workspace_root
        self.adapter_path = adapter_path
        self.cli_args = cli_args or []

        self._client: Optional[_InternalACPClient] = None
        self._conn: Optional[ClientSideConnection] = None
        self._session_id: Optional[str] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[Thread] = None
        self._context = None
        self._ready_queue: Optional[Queue] = None

    def start(self, timeout: float = 30.0) -> None:
        """
        Start the Claude Code agent process and establish ACP connection.

        Args:
            timeout: Maximum time to wait for the agent to start (seconds)

        Raises:
            RuntimeError: If the agent is already started
            TimeoutError: If the agent fails to start within the timeout
            Exception: If initialization fails
        """
        if self._thread is not None:
            raise RuntimeError("Agent already started")

        self._ready_queue = Queue()
        self._thread = Thread(target=self._run_async_loop, daemon=True)
        self._thread.start()

        # Wait for initialization with timeout
        try:
            result = self._ready_queue.get(timeout=timeout)
            if isinstance(result, Exception):
                raise result
        except Empty:
            # Queue.get() timed out - no result received within timeout
            raise TimeoutError(
                f"Claude Code agent failed to start within {timeout} seconds. "
                f"Make sure @zed-industries/claude-code-acp is installed: "
                f"npm install -g @zed-industries/claude-code-acp"
            )

    def stop(self) -> None:
        """Stop the Claude Code agent process and cleanup resources."""
        if self._loop is not None:
            asyncio.run_coroutine_threadsafe(self._async_stop(), self._loop)
            self._loop.call_soon_threadsafe(self._loop.stop)
            if self._thread is not None:
                self._thread.join(timeout=2.0)

        self._client = None
        self._conn = None
        self._session_id = None
        self._loop = None
        self._thread = None
        self._context = None

    def send_message(self, message: str, timeout: float = 30.0) -> str:
        """
        Send a message to Claude Code and get the response.

        Args:
            message: The message to send
            timeout: Maximum time to wait for response (seconds)

        Returns:
            The agent's response as a string

        Raises:
            RuntimeError: If the agent is not started
            TimeoutError: If the response takes too long
        """
        if self._loop is None or self._conn is None or self._client is None:
            raise RuntimeError("Agent not started. Call start() first.")

        # Reset the response and completion flag
        self._client.last_response = ""
        self._client.message_complete = False

        # Schedule the async query
        future = asyncio.run_coroutine_threadsafe(
            self._async_send_message(message), self._loop
        )

        # Wait for completion
        future.result(timeout=timeout)

        # Wait for message_complete flag (with timeout)
        import time

        start_time = time.time()
        while not self._client.message_complete:
            if time.time() - start_time > 2.0:  # Max 2 seconds to wait for completion
                # If we don't get message_end event, just return what we have
                break
            time.sleep(0.05)  # Small sleep to avoid busy waiting

        return self._client.get_last_response()

    def clear_context(self) -> None:
        """
        Clear the session context by restarting the agent.

        This stops the current agent and starts a new one with a fresh session.
        """
        self.stop()
        self.start()

    @property
    def session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self._session_id

    @property
    def is_running(self) -> bool:
        """Check if the agent is currently running."""
        return self._thread is not None and self._loop is not None

    def _run_async_loop(self):
        """Run the asyncio event loop in a background thread."""
        try:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._async_start())
            self._ready_queue.put(True)
            self._loop.run_forever()
        except Exception as e:
            self._ready_queue.put(e)

    async def _async_start(self):
        """Async initialization."""
        self._client = _InternalACPClient(self.listener)

        # Build command to spawn claude-code-acp
        if self.adapter_path:
            # Use explicit path if provided
            cli_args = [self.adapter_path]
        else:
            # Use npx to run the package
            cli_args = ["npx", "@zed-industries/claude-code-acp"]

        # Check if npx is available
        if not self.adapter_path and not shutil.which("npx"):
            raise RuntimeError(
                "npx not found. Please install Node.js or provide adapter_path explicitly."
            )

        # Set up environment variables
        env = os.environ.copy()
        env["ANTHROPIC_API_KEY"] = self.api_key

        # Note: The adapter may use different env vars for model configuration
        # We'll need to check the adapter's documentation for the exact variable name
        if self.model:
            # Try common patterns - the adapter will use what it supports
            env["CLAUDE_CODE_MODEL"] = self.model
            env["MODEL"] = self.model

        # Add any additional custom CLI arguments
        if self.cli_args:
            cli_args.extend(self.cli_args)

        # Spawn the agent process with environment variables
        self._context = spawn_agent_process(
            lambda _agent: self._client, *cli_args, env=env
        )

        # Start the process and get connection
        conn_proc = await self._context.__aenter__()
        self._conn, self._proc = conn_proc

        # Create a task to monitor if the process exits early
        async def wait_for_process_exit():
            """Wait for the process to exit and raise an error if it does."""
            await self._proc.wait()
            stderr = ""
            if self._proc.stderr:
                try:
                    stderr_bytes = await asyncio.wait_for(
                        self._proc.stderr.read(), timeout=1.0
                    )
                    stderr = stderr_bytes.decode("utf-8", errors="replace")
                except Exception:
                    pass
            raise RuntimeError(
                f"Claude Code agent process exited with code {self._proc.returncode}.\n"
                f"Stderr: {stderr}"
            )

        # Check if process has already exited
        if self._proc.returncode is not None:
            # Process already exited
            stderr = ""
            if self._proc.stderr:
                stderr_bytes = await self._proc.stderr.read()
                stderr = stderr_bytes.decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Claude Code agent process exited immediately with code {self._proc.returncode}.\n"
                f"Stderr: {stderr}"
            )

        # Create process monitor task
        monitor_task = asyncio.create_task(wait_for_process_exit())

        try:
            # Race between initialization and process exit
            init_task = asyncio.create_task(
                self._conn.initialize(
                    InitializeRequest(
                        protocolVersion=PROTOCOL_VERSION,
                        clientCapabilities=None,
                        clientInfo=Implementation(
                            name="auggie-sdk-python",
                            version=get_sdk_version(),
                        ),
                    )
                )
            )
            done, pending = await asyncio.wait(
                [init_task, monitor_task], return_when=asyncio.FIRST_COMPLETED
            )

            # If monitor task completed first, it means process exited
            if monitor_task in done:
                # Cancel the init task
                init_task.cancel()
                # Re-raise the exception from monitor_task
                await monitor_task

            # Otherwise, initialization succeeded
            await init_task

            # Use workspace_root as cwd if provided, otherwise use current directory
            cwd = self.workspace_root if self.workspace_root else os.getcwd()

            # Race between session creation and process exit
            session_task = asyncio.create_task(
                self._conn.newSession(NewSessionRequest(mcpServers=[], cwd=cwd))
            )
            done, pending = await asyncio.wait(
                [session_task, monitor_task], return_when=asyncio.FIRST_COMPLETED
            )

            # If monitor task completed first, it means process exited
            if monitor_task in done:
                # Cancel the session task
                session_task.cancel()
                # Re-raise the exception from monitor_task
                await monitor_task

            # Otherwise, session creation succeeded
            session = await session_task
            self._session_id = session.sessionId

            # Keep the monitor task running in the background
            # (don't cancel it, it will keep monitoring the process)
        except Exception:
            # If anything fails, cancel the monitor task
            monitor_task.cancel()
            raise

    async def _async_send_message(self, message: str):
        """Async message sending."""
        await self._conn.prompt(
            PromptRequest(
                sessionId=self._session_id,
                prompt=[text_block(message)],
            )
        )

    async def _async_stop(self):
        """Async cleanup."""
        if self._context is not None:
            await self._context.__aexit__(None, None, None)

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
