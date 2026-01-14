"""
Unit tests for AgentEventListener interface.

These tests verify that the listener interface works correctly with mocked events.
"""

from unittest.mock import MagicMock

import pytest

from auggie_sdk.acp import AgentEventListener


class TestAgentEventListener:
    """Test cases for AgentEventListener interface."""

    def test_listener_interface_has_required_methods(self):
        """Test that AgentEventListener has all required abstract methods."""
        # These should be abstract methods
        assert hasattr(AgentEventListener, "on_agent_message_chunk")
        assert hasattr(AgentEventListener, "on_tool_call")
        assert hasattr(AgentEventListener, "on_tool_response")

        # These should be optional methods
        assert hasattr(AgentEventListener, "on_agent_thought")
        assert hasattr(AgentEventListener, "on_agent_message")

    def test_listener_can_be_implemented(self):
        """Test that we can implement the listener interface."""

        class TestListener(AgentEventListener):
            def __init__(self):
                self.chunks = []
                self.messages = []
                self.tool_calls = []
                self.tool_responses = []
                self.thoughts = []

            def on_agent_message_chunk(self, text: str) -> None:
                self.chunks.append(text)

            def on_agent_message(self, message: str) -> None:
                self.messages.append(message)

            def on_tool_call(self, tool_call_id, title, kind=None, status=None):
                self.tool_calls.append(
                    {"id": tool_call_id, "title": title, "kind": kind, "status": status}
                )

            def on_tool_response(self, tool_call_id, status=None, content=None):
                self.tool_responses.append(
                    {"id": tool_call_id, "status": status, "content": content}
                )

            def on_agent_thought(self, text: str) -> None:
                self.thoughts.append(text)

        # Should be able to instantiate
        listener = TestListener()

        # Test message chunks
        listener.on_agent_message_chunk("Hello ")
        listener.on_agent_message_chunk("world")
        assert listener.chunks == ["Hello ", "world"]

        # Test complete message
        listener.on_agent_message("Hello world")
        assert listener.messages == ["Hello world"]

        # Test tool call
        listener.on_tool_call("tc_001", "view", kind="read", status="pending")
        assert len(listener.tool_calls) == 1
        assert listener.tool_calls[0]["id"] == "tc_001"
        assert listener.tool_calls[0]["title"] == "view"

        # Test tool response
        listener.on_tool_response("tc_001", status="completed", content="file content")
        assert len(listener.tool_responses) == 1
        assert listener.tool_responses[0]["status"] == "completed"

        # Test thought
        listener.on_agent_thought("I need to read the file")
        assert listener.thoughts == ["I need to read the file"]

    def test_listener_optional_methods_have_defaults(self):
        """Test that optional methods have default implementations."""

        class MinimalListener(AgentEventListener):
            """Listener that only implements required methods."""

            def on_agent_message_chunk(self, text: str) -> None:
                pass

            def on_tool_call(self, tool_call_id, title, kind=None, status=None):
                pass

            def on_tool_response(self, tool_call_id, status=None, content=None):
                pass

        # Should be able to instantiate without implementing optional methods
        listener = MinimalListener()

        # Optional methods should not raise errors
        listener.on_agent_thought("test")  # Should not raise
        listener.on_agent_message("test")  # Should not raise

    def test_listener_receives_events_in_order(self):
        """Test that listener receives events in the expected order."""

        class OrderTrackingListener(AgentEventListener):
            def __init__(self):
                self.events = []

            def on_agent_message_chunk(self, text: str) -> None:
                self.events.append(("chunk", text))

            def on_agent_message(self, message: str) -> None:
                self.events.append(("complete", message))

            def on_tool_call(self, tool_call_id, title, kind=None, status=None):
                self.events.append(("tool_call", tool_call_id, title))

            def on_tool_response(self, tool_call_id, status=None, content=None):
                self.events.append(("tool_response", tool_call_id, status))

            def on_agent_thought(self, text: str) -> None:
                self.events.append(("thought", text))

        listener = OrderTrackingListener()

        # Simulate a typical event sequence
        listener.on_agent_thought("I'll read the file")
        listener.on_tool_call("tc_001", "view", kind="read", status="pending")
        listener.on_tool_response("tc_001", status="completed", content="...")
        listener.on_agent_message_chunk("The file ")
        listener.on_agent_message_chunk("contains...")
        listener.on_agent_message("The file contains...")

        # Verify order
        assert listener.events[0] == ("thought", "I'll read the file")
        assert listener.events[1] == ("tool_call", "tc_001", "view")
        assert listener.events[2] == ("tool_response", "tc_001", "completed")
        assert listener.events[3] == ("chunk", "The file ")
        assert listener.events[4] == ("chunk", "contains...")
        assert listener.events[5] == ("complete", "The file contains...")

    def test_listener_can_accumulate_chunks(self):
        """Test that listener can accumulate message chunks."""

        class ChunkAccumulator(AgentEventListener):
            def __init__(self):
                self.accumulated = ""
                self.complete_message = None

            def on_agent_message_chunk(self, text: str) -> None:
                self.accumulated += text

            def on_agent_message(self, message: str) -> None:
                self.complete_message = message

            def on_tool_call(self, tool_call_id, title, kind=None, status=None):
                pass

            def on_tool_response(self, tool_call_id, status=None, content=None):
                pass

        listener = ChunkAccumulator()

        # Send chunks
        chunks = ["The ", "answer ", "is ", "42."]
        for chunk in chunks:
            listener.on_agent_message_chunk(chunk)

        # Verify accumulation
        assert listener.accumulated == "The answer is 42."

        # Send complete message
        listener.on_agent_message("The answer is 42.")

        # Verify they match
        assert listener.accumulated == listener.complete_message

    def test_listener_can_track_tool_calls(self):
        """Test that listener can track tool calls and their responses."""

        class ToolCallTracker(AgentEventListener):
            def __init__(self):
                self.active_tools = {}
                self.completed_tools = []

            def on_agent_message_chunk(self, text: str) -> None:
                pass

            def on_tool_call(self, tool_call_id, title, kind=None, status=None):
                self.active_tools[tool_call_id] = {
                    "title": title,
                    "kind": kind,
                    "status": status,
                }

            def on_tool_response(self, tool_call_id, status=None, content=None):
                if tool_call_id in self.active_tools:
                    tool_info = self.active_tools.pop(tool_call_id)
                    tool_info["final_status"] = status
                    tool_info["content"] = content
                    self.completed_tools.append(tool_info)

        listener = ToolCallTracker()

        # Simulate tool calls
        listener.on_tool_call("tc_001", "view", kind="read", status="pending")
        listener.on_tool_call(
            "tc_002", "str-replace-editor", kind="edit", status="pending"
        )

        assert len(listener.active_tools) == 2
        assert len(listener.completed_tools) == 0

        # Complete first tool
        listener.on_tool_response("tc_001", status="completed", content="file content")

        assert len(listener.active_tools) == 1
        assert len(listener.completed_tools) == 1
        assert listener.completed_tools[0]["title"] == "view"
        assert listener.completed_tools[0]["final_status"] == "completed"

        # Complete second tool
        listener.on_tool_response("tc_002", status="completed", content=None)

        assert len(listener.active_tools) == 0
        assert len(listener.completed_tools) == 2

    def test_listener_methods_can_be_mocked(self):
        """Test that listener methods can be mocked for testing."""

        # Create a mock listener
        mock_listener = MagicMock(spec=AgentEventListener)

        # Call methods
        mock_listener.on_agent_message_chunk("test")
        mock_listener.on_agent_message("complete test")
        mock_listener.on_tool_call("tc_001", "view", kind="read")
        mock_listener.on_tool_response("tc_001", status="completed")
        mock_listener.on_agent_thought("thinking...")

        # Verify calls
        mock_listener.on_agent_message_chunk.assert_called_once_with("test")
        mock_listener.on_agent_message.assert_called_once_with("complete test")
        mock_listener.on_tool_call.assert_called_once_with(
            "tc_001", "view", kind="read"
        )
        mock_listener.on_tool_response.assert_called_once_with(
            "tc_001", status="completed"
        )
        mock_listener.on_agent_thought.assert_called_once_with("thinking...")
