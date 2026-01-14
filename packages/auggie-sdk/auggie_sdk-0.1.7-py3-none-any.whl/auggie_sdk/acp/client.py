"""
Synchronous ACP Client for Augment CLI

A clean, easy-to-use wrapper around the Agent Client Protocol for communicating
with the Augment CLI agent.
"""

import asyncio
import os
from abc import ABC, abstractmethod
from queue import Empty, Queue
from threading import Thread
from typing import Optional, Any, List

from typing import Union

from acp import (
    Client,
    ClientSideConnection,
    InitializeRequest,
    NewSessionRequest,
    PromptRequest,
    RequestError,
    text_block,
    PROTOCOL_VERSION,
    spawn_agent_process,
)
from acp.schema import (
    RequestPermissionResponse,
    AllowedOutcome,
    Implementation,
    PermissionOption,
    ToolCallUpdate,
    UserMessageChunk,
    AgentMessageChunk,
    AgentThoughtChunk,
    ToolCallStart,
    ToolCallProgress,
    AgentPlanUpdate,
    AvailableCommandsUpdate,
    CurrentModeUpdate,
    TextContentBlock,
)

from auggie_sdk.context.version import get_sdk_version


class AgentEventListener(ABC):
    """
    Interface for listening to agent events.

    Implement this interface to receive notifications about what the agent is doing.
    """

    @abstractmethod
    def on_agent_message_chunk(self, text: str) -> None:
        """
        Called when the agent sends a message chunk (streaming).

        The agent streams its response in real-time. This method is called
        multiple times with small chunks of text that together form the
        complete message.

        Args:
            text: A chunk of text from the agent's response
        """
        pass

    @abstractmethod
    def on_tool_call(
        self,
        tool_call_id: str,
        title: str,
        kind: Optional[str] = None,
        status: Optional[str] = None,
    ) -> None:
        """
        Called when the agent makes a tool call.

        Args:
            tool_call_id: Unique identifier for this tool call
            title: Human-readable description of what the tool is doing
            kind: Category of tool (read, edit, delete, execute, etc.)
            status: Current status (pending, in_progress, completed, failed)
        """
        pass

    @abstractmethod
    def on_tool_response(
        self,
        tool_call_id: str,
        status: Optional[str] = None,
        content: Optional[Any] = None,
    ) -> None:
        """
        Called when a tool responds with results.

        Args:
            tool_call_id: Unique identifier for this tool call
            status: Response status (completed, failed, etc.)
            content: Response content/results from the tool
        """
        pass

    def on_agent_thought(self, text: str) -> None:
        """
        Called when the agent shares its internal reasoning.

        Args:
            text: The thought content from the agent
        """
        pass

    def on_agent_message(self, message: str) -> None:
        """
        Called when the agent finishes sending a complete message.

        This is called once after all message chunks have been sent,
        with the complete assembled message.

        Args:
            message: The complete message from the agent
        """
        pass


# Type alias for session update types
SessionUpdateType = Union[
    UserMessageChunk,
    AgentMessageChunk,
    AgentThoughtChunk,
    ToolCallStart,
    ToolCallProgress,
    AgentPlanUpdate,
    AvailableCommandsUpdate,
    CurrentModeUpdate,
]


class _InternalACPClient(Client):
    """Internal ACP client implementation."""

    def __init__(self, listener: Optional[AgentEventListener] = None):
        self.listener = listener
        self.last_response = ""

    async def request_permission(
        self,
        options: List[PermissionOption],
        session_id: str,
        tool_call: ToolCallUpdate,
        **kwargs: Any,
    ) -> RequestPermissionResponse:
        """
        Handle permission requests from the CLI (e.g., indexing permission).
        Auto-approves all requests by selecting the first "allow" option.
        """
        # Find the first "allow" option (allow_once or allow_always)
        allow_option = None
        for option in options:
            if option.kind.startswith("allow"):
                allow_option = option
                break

        if not allow_option and options:
            # If no allow option found, just select the first option
            allow_option = options[0]

        if not allow_option:
            # No options available, return a default
            return RequestPermissionResponse(
                outcome=AllowedOutcome(optionId="default", outcome="selected")
            )

        # Return approval response using proper ACP types
        return RequestPermissionResponse(
            outcome=AllowedOutcome(optionId=allow_option.optionId, outcome="selected")
        )

    async def write_text_file(
        self, content: str, path: str, session_id: str, **kwargs: Any
    ) -> None:
        raise RequestError.method_not_found("fs/write_text_file")

    async def read_text_file(
        self,
        path: str,
        session_id: str,
        limit: Optional[int] = None,
        line: Optional[int] = None,
        **kwargs: Any,
    ) -> Any:
        raise RequestError.method_not_found("fs/read_text_file")

    async def create_terminal(
        self,
        command: str,
        session_id: str,
        args: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        env: Optional[List[Any]] = None,
        output_byte_limit: Optional[int] = None,
        **kwargs: Any,
    ) -> Any:
        raise RequestError.method_not_found("terminal/create")

    async def terminal_output(
        self, session_id: str, terminal_id: str, **kwargs: Any
    ) -> Any:
        raise RequestError.method_not_found("terminal/output")

    async def release_terminal(
        self, session_id: str, terminal_id: str, **kwargs: Any
    ) -> None:
        raise RequestError.method_not_found("terminal/release")

    async def wait_for_terminal_exit(
        self, session_id: str, terminal_id: str, **kwargs: Any
    ) -> Any:
        raise RequestError.method_not_found("terminal/wait_for_exit")

    async def kill_terminal(
        self, session_id: str, terminal_id: str, **kwargs: Any
    ) -> None:
        raise RequestError.method_not_found("terminal/kill")

    async def session_update(
        self,
        session_id: str,
        update: SessionUpdateType,
        **kwargs: Any,
    ) -> None:
        """Handle session update notifications from the agent."""
        # Determine the update type and extract content
        if isinstance(update, AgentMessageChunk):
            # Handle agent message chunks - extract text from content block
            text = ""
            if hasattr(update, "content") and isinstance(update.content, TextContentBlock):
                text = update.content.text
            self.last_response += text
            if self.listener:
                self.listener.on_agent_message_chunk(text)

        elif isinstance(update, AgentThoughtChunk):
            # Handle agent thoughts - extract text from content block
            text = ""
            if hasattr(update, "content") and isinstance(update.content, TextContentBlock):
                text = update.content.text
            if self.listener:
                self.listener.on_agent_thought(text)

        elif isinstance(update, ToolCallStart):
            # Handle tool call start
            tool_call_id = getattr(update, "toolCallId", "unknown")
            title = getattr(update, "title", "")
            tool_kind = getattr(update, "kind", None)
            status = getattr(update, "status", None)
            if self.listener:
                self.listener.on_tool_call(tool_call_id, title, tool_kind, status)

        elif isinstance(update, ToolCallProgress):
            # Handle tool call progress/update
            tool_call_id = getattr(update, "toolCallId", "unknown")
            status = getattr(update, "status", None)
            content = getattr(update, "content", None)
            if self.listener:
                self.listener.on_tool_response(tool_call_id, status, content)

    async def ext_method(self, method: str, params: dict) -> dict:  # noqa: ARG002
        raise RequestError.method_not_found(method)

    async def ext_notification(self, method: str, params: dict) -> None:  # noqa: ARG002
        raise RequestError.method_not_found(method)

    def on_connect(self, conn: Any) -> None:
        """Called when the client connects to an agent."""
        pass

    def get_last_response(self) -> str:
        return self.last_response.strip()


class ACPClient:
    """ACP client interface."""

    def start(self) -> None:
        """
        Start the agent process and establish ACP connection.

        Raises:
            RuntimeError: If the agent is already started
            Exception: If initialization fails
        """
        raise NotImplementedError()

    def stop(self) -> None:
        """Stop the agent process and cleanup resources."""
        raise NotImplementedError()

    def send_message(self, message: str, timeout: float = 30.0) -> str:
        """
        Send a message to the agent and get the response.

        Args:
            message: The message to send
            timeout: Maximum time to wait for response (seconds)

        Returns:
            The agent's response as a string

        Raises:
            RuntimeError: If the agent is not started
            TimeoutError: If the response takes too long
        """
        raise NotImplementedError()

    def clear_context(self) -> None:
        """
        Clear the session context by restarting the agent.

        This stops the current agent and starts a new one with a fresh session.
        """
        raise NotImplementedError()

    @property
    def is_running(self) -> bool:
        """Check if the agent is currently running."""
        raise NotImplementedError()


class AuggieACPClient(ACPClient):
    """
    Synchronous ACP client for the Augment CLI agent.

    This client provides a simple interface for:
    - Starting/stopping the agent
    - Sending messages and getting responses
    - Listening to agent events (messages, tool calls, etc.)
    - Clearing session context

    Example:
        ```python
        # Create a client with an event listener
        client = AuggieACPClient(listener=MyListener())

        # Start the agent
        client.start()

        # Send a message
        response = client.send_message("What is 2 + 2?")
        print(response)

        # Clear context and start fresh
        client.clear_context()

        # Stop the agent
        client.stop()
        ```
    """

    def __init__(
        self,
        cli_path: Optional[str] = None,
        listener: Optional[AgentEventListener] = None,
        model: Optional[str] = None,
        workspace_root: Optional[str] = None,
        acp_max_tool_result_bytes: int = 35 * 1024,
        removed_tools: Optional[List[str]] = None,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        rules: Optional[List[str]] = None,
        cli_args: Optional[List[str]] = None,
    ):
        """
        Initialize the ACP client.

        Args:
            cli_path: Path to the Augment CLI. If None, uses default location.
            listener: Optional event listener to receive agent events.
            model: AI model to use (e.g., "claude-3-5-sonnet-latest", "gpt-4o").
                   If None, uses the CLI's default model.
            workspace_root: Workspace root directory. If None, uses current directory.
            acp_max_tool_result_bytes: Maximum bytes for tool results sent through ACP.
                   Default: 35KB (35840 bytes). This prevents Python's asyncio.StreamReader
                   from hitting its 64KB line buffer limit. Set higher if needed, but
                   keep under 64KB to avoid LimitOverrunError.
            removed_tools: List of tool names to remove/disable (e.g., ["github-api", "linear"]).
                   These tools will not be available to the agent.
            api_key: Optional API key for authentication. If provided, sets AUGMENT_API_TOKEN
                   environment variable for the agent process.
            api_url: Optional API URL. If not provided, uses AUGMENT_API_URL environment variable,
                   or defaults to "https://api.augmentcode.com". Sets AUGMENT_API_URL environment
                   variable for the agent process.
            rules: Optional list of rule file paths. Each file path will be passed to the auggie
                  command using the --rules flag.
            cli_args: Optional list of additional command-line arguments to pass to the CLI.
                     These arguments are appended after all other CLI arguments (e.g.,
                     ["--verbose", "--debug"]). Use this for passing custom or experimental
                     CLI flags that aren't exposed as dedicated parameters.
        """
        if cli_path is None:
            # Default to 'auggie' in PATH
            cli_path = "auggie"

        self.cli_path = cli_path

        self.listener = listener
        self.model = model
        self.workspace_root = workspace_root
        self.acp_max_tool_result_bytes = acp_max_tool_result_bytes
        self.removed_tools = removed_tools or []
        self.api_key = api_key
        self.api_url = (
            api_url
            if api_url is not None
            else os.getenv("AUGMENT_API_URL", "https://api.augmentcode.com")
        )
        self.rules = rules or []
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
        Start the agent process and establish ACP connection.

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
                f"Agent failed to start within {timeout} seconds. "
                f"Check that the CLI path is correct and the agent process can start. "
                f"CLI path: {self.cli_path}"
            )

    def stop(self) -> None:
        """Stop the agent process and cleanup resources."""
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
        Send a message to the agent and get the response.

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

        # Reset the response
        self._client.last_response = ""

        # Schedule the async query
        future = asyncio.run_coroutine_threadsafe(
            self._async_send_message(message), self._loop
        )

        # Wait for completion - when prompt() completes, the message is done
        # (per ACP spec, there is no agent_message_end event)
        future.result(timeout=timeout)

        response = self._client.get_last_response()

        # Call listener with complete message now that prompt() has completed
        if self.listener and response:
            self.listener.on_agent_message(response)

        return response

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

        # Build CLI arguments
        cli_path_str = str(self.cli_path)
        if cli_path_str.endswith(".mjs") or cli_path_str.endswith(".js"):
            # It's a JS file, run with node
            cli_args = ["node", cli_path_str]
        else:
            # It's a binary or script (like 'auggie'), run directly
            cli_args = [cli_path_str]

        cli_args.extend(["--acp"])

        # Add model if specified
        if self.model:
            cli_args.extend(["--model", self.model])

        # Add workspace root if specified
        if self.workspace_root:
            cli_args.extend(["--workspace-root", self.workspace_root])

        # Add removed tools if specified and enabled
        if self.removed_tools:
            for tool in self.removed_tools:
                cli_args.extend(["--remove-tool", tool])

        # Add rules if specified
        if self.rules:
            for rule_path in self.rules:
                cli_args.extend(["--rules", rule_path])

        # Add ACP max tool result bytes
        # TODO: Re-enable once --acp-max-tool-result-bytes is in pre-release
        # cli_args.extend(
        #     ["--acp-max-tool-result-bytes", str(self.acp_max_tool_result_bytes)]
        # )

        # Add any additional custom CLI arguments
        if self.cli_args:
            cli_args.extend(self.cli_args)

        # Set environment variables for API authentication
        # Build environment dict to pass to spawn_agent_process
        env = os.environ.copy()
        if self.api_key:
            env["AUGMENT_API_TOKEN"] = self.api_key
        if self.api_url:
            env["AUGMENT_API_URL"] = self.api_url

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
                f"Agent process exited with code {self._proc.returncode}. "
                f"CLI path: {self.cli_path}\n"
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
                f"Agent process exited immediately with code {self._proc.returncode}. "
                f"CLI path: {self.cli_path}\n"
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
