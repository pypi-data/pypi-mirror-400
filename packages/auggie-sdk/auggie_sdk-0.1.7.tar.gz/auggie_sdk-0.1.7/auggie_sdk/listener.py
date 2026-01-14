"""
Agent listener interface for receiving notifications about agent activity.
"""

from abc import ABC
from typing import Any, Optional


class AgentListener(ABC):
    """
    Interface for listening to agent events.

    Implement this interface to receive notifications about what the agent is doing
    during execution. This is useful for logging, debugging, or providing user feedback.

    All methods are optional - you only need to implement the ones you care about.
    """

    def on_agent_message(self, message: str) -> None:
        """
        Called when the agent sends a complete message.

        This is called with the agent's textual response, which may include
        reasoning, explanations, or other context.

        Args:
            message: The complete message from the agent
        """
        pass

    def on_tool_call(
        self,
        tool_call_id: str,
        title: str,
        kind: Optional[str] = None,
        status: Optional[str] = None,
    ) -> None:
        """
        Called when the agent makes a tool call.

        Tools are things like:
        - "view" - reading a file
        - "str-replace-editor" - editing a file
        - "launch-process" - running a command
        - "save-file" - creating a new file
        - "codebase-retrieval" - searching the codebase

        Args:
            tool_call_id: Unique identifier for this tool call
            title: Human-readable description of what the tool is doing
            kind: Category of tool (read, edit, delete, execute, etc.)
            status: Current status (pending, in_progress, completed, failed)
        """
        pass

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

        This provides insight into how the agent is thinking about the problem.

        Args:
            text: The thought content from the agent
        """
        pass

    def on_function_call(
        self,
        function_name: str,
        arguments: dict,
    ) -> None:
        """
        Called when the agent calls a user-provided function.

        Args:
            function_name: Name of the function being called
            arguments: Arguments passed to the function
        """
        pass

    def on_function_result(
        self,
        function_name: str,
        result: Any,
        error: Optional[str] = None,
    ) -> None:
        """
        Called when a user-provided function returns a result or error.

        Args:
            function_name: Name of the function that was called
            result: The return value from the function (None if error)
            error: Error message if the function raised an exception
        """
        pass


class LoggingAgentListener(AgentListener):
    """
    Simple logging implementation of AgentListener.

    Prints all events to stdout with timestamps and formatting.
    Useful for debugging and understanding what the agent is doing.
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the logging listener.

        Args:
            verbose: If True, logs all events. If False, only logs major events.
        """
        self.verbose = verbose

    def on_agent_message(self, message: str) -> None:
        """Log agent messages."""
        print(f"\n💬 Agent: {message[:200]}{'...' if len(message) > 200 else ''}")

    def on_tool_call(
        self,
        tool_call_id: str,
        title: str,
        kind: Optional[str] = None,
        status: Optional[str] = None,
    ) -> None:
        """Log tool calls."""
        if self.verbose or status in ["pending", None]:
            icon = "🔧" if kind != "read" else "📖"
            print(f"{icon} Tool: {title} ({kind or 'unknown'})")

    def on_tool_response(
        self,
        tool_call_id: str,
        status: Optional[str] = None,
        content: Optional[Any] = None,
    ) -> None:
        """Log tool responses."""
        if self.verbose:
            icon = "✅" if status == "completed" else "❌"
            print(f"  {icon} Tool response: {status}")

    def on_agent_thought(self, text: str) -> None:
        """Log agent thoughts."""
        if self.verbose:
            print(f"💭 Thinking: {text[:100]}{'...' if len(text) > 100 else ''}")

    def on_function_call(
        self,
        function_name: str,
        arguments: dict,
    ) -> None:
        """Log function calls."""
        print(
            f"📞 Calling function: {function_name}({', '.join(f'{k}={v}' for k, v in arguments.items())})"
        )

    def on_function_result(
        self,
        function_name: str,
        result: Any,
        error: Optional[str] = None,
    ) -> None:
        """Log function results."""
        if error:
            print(f"  ❌ Function {function_name} failed: {error}")
        else:
            result_str = str(result)
            if len(result_str) > 100:
                result_str = result_str[:100] + "..."
            print(f"  ✅ Function {function_name} returned: {result_str}")
