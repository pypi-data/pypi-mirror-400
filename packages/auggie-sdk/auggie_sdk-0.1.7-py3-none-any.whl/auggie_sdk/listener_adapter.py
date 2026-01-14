"""
Adapter to bridge ACP AgentEventListener to Agent AgentListener.
"""

from typing import Any, Optional

from .acp import AgentEventListener
from .listener import AgentListener


class AgentListenerAdapter(AgentEventListener):
    """
    Adapter that converts ACP events to AgentListener events.

    This class implements AgentEventListener (the ACP interface) and forwards
    relevant events to an AgentListener (the user-facing interface).
    """

    def __init__(self, agent_listener: Optional[AgentListener] = None):
        """
        Initialize the adapter.

        Args:
            agent_listener: The user's AgentListener to forward events to
        """
        self.agent_listener = agent_listener

    def on_agent_message_chunk(self, text: str) -> None:
        """
        Called when the agent sends a message chunk (streaming).

        We don't forward chunks to AgentListener since it doesn't support streaming.
        We'll accumulate them and send the complete message in on_agent_message.
        """
        # AgentListener doesn't support streaming, so we ignore chunks
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

        Forward to AgentListener if present.
        """
        if self.agent_listener:
            self.agent_listener.on_tool_call(tool_call_id, title, kind, status)

    def on_tool_response(
        self,
        tool_call_id: str,
        status: Optional[str] = None,
        content: Optional[Any] = None,
    ) -> None:
        """
        Called when a tool responds with results.

        Forward to AgentListener if present.
        """
        if self.agent_listener:
            self.agent_listener.on_tool_response(tool_call_id, status, content)

    def on_agent_thought(self, text: str) -> None:
        """
        Called when the agent shares its internal reasoning.

        Forward to AgentListener if present.
        """
        if self.agent_listener:
            self.agent_listener.on_agent_thought(text)

    def on_agent_message(self, message: str) -> None:
        """
        Called when the agent finishes sending a complete message.

        Forward to AgentListener if present.
        """
        if self.agent_listener:
            self.agent_listener.on_agent_message(message)
