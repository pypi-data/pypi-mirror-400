"""
Integration tests for AuggieACPClient.

These tests verify the client works correctly with the actual Augment CLI agent.
Uses pytest for test framework.

By default, integration tests are skipped. To run them: pytest -m integration
Or use tox: tox -e integration
"""

import time

import pytest
from typing import Optional, Any, List, Dict
from auggie_sdk.acp import AuggieACPClient, AgentEventListener


class EventListenerForTesting(AgentEventListener):
    """Event listener that captures all events for testing purposes."""

    def __init__(self):
        self.message_chunks: List[str] = []
        self.complete_messages: List[str] = []
        self.tool_calls: List[Dict[str, Any]] = []
        self.thoughts: List[str] = []

    def on_agent_message_chunk(self, text: str) -> None:
        self.message_chunks.append(text)

    def on_agent_message(self, message: str) -> None:
        self.complete_messages.append(message)

    def on_tool_call(
        self,
        tool_call_id: str,
        title: str,
        kind: Optional[str] = None,
        status: Optional[str] = None,
    ) -> None:
        self.tool_calls.append(
            {
                "type": "call",
                "id": tool_call_id,
                "title": title,
                "kind": kind,
                "status": status,
            }
        )

    def on_tool_response(
        self,
        tool_call_id: str,
        status: Optional[str] = None,
        content: Optional[Any] = None,
    ) -> None:
        self.tool_calls.append(
            {
                "type": "response",
                "id": tool_call_id,
                "status": status,
                "content": content,
            }
        )

    def on_agent_thought(self, text: str) -> None:
        self.thoughts.append(text)

    def reset(self):
        """Reset all captured events."""
        self.message_chunks.clear()
        self.complete_messages.clear()
        self.tool_calls.clear()
        self.thoughts.clear()

    def get_full_message(self) -> str:
        """Get the complete message from all chunks."""
        return "".join(self.message_chunks)


# ============================================================================
# Error Handling Tests
# ============================================================================


def test_invalid_cli_path_raises_file_not_found():
    """Test that providing a non-existent CLI path raises FileNotFoundError on start."""
    client = AuggieACPClient(cli_path="/path/to/nonexistent/cli")
    with pytest.raises(FileNotFoundError):
        client.start()


def test_invalid_cli_path_fails_on_start(tmp_path):
    """Test that starting with an invalid CLI path raises an error quickly."""
    import time

    fake_cli = tmp_path / "fake_cli"
    fake_cli.touch()
    client = AuggieACPClient(cli_path=str(fake_cli))

    # Should raise PermissionError quickly (< 2 seconds), not hang
    start_time = time.time()
    with pytest.raises(PermissionError):
        client.start()
    elapsed = time.time() - start_time

    # Verify it failed quickly
    assert elapsed < 2.0, f"Process exit detection took too long: {elapsed:.2f}s"


# ============================================================================
# Basic Functionality Tests
# ============================================================================


@pytest.mark.integration
def test_start_and_stop():
    """Test basic start and stop functionality."""
    client = AuggieACPClient()

    # Should not be running initially
    assert not client.is_running
    assert client.session_id is None

    # Start the client
    client.start()
    assert client.is_running
    assert client.session_id is not None
    session_id = client.session_id
    assert len(session_id) == 36  # UUID format

    # Stop the client
    client.stop()
    assert not client.is_running


@pytest.mark.integration
def test_simple_math_query():
    """Test sending a simple math query."""
    with AuggieACPClient() as client:
        response = client.send_message("What is 2 + 2? Answer with just the number.")

        # Should contain the answer
        assert "4" in response
        assert len(response) > 0


@pytest.mark.integration
def test_multiple_messages_same_session():
    """Test sending multiple messages in the same session."""
    with AuggieACPClient() as client:
        session_id = client.session_id

        # First message
        response1 = client.send_message("What is 5 + 3?")
        assert "8" in response1

        # Session should remain the same
        assert client.session_id == session_id

        # Second message - agent should remember context
        response2 = client.send_message("What is that number times 2?")
        assert "16" in response2

        # Session should still be the same
        assert client.session_id == session_id


@pytest.mark.integration
def test_context_manager():
    """Test context manager automatically starts and stops."""
    client = AuggieACPClient()
    assert not client.is_running

    with client:
        assert client.is_running
        response = client.send_message("What is 10 * 5?")
        assert "50" in response

    # Should be stopped after exiting context
    assert not client.is_running


@pytest.mark.integration
def test_clear_context():
    """Test clearing context creates a new session."""
    client = AuggieACPClient()
    client.start()

    try:
        # Get initial session
        session1 = client.session_id

        # Send a message
        client.send_message("Remember the number 42")

        # Clear context
        client.clear_context()

        # Should have a new session
        session2 = client.session_id
        assert session1 != session2
        assert client.is_running

        # Agent should not remember the previous conversation
        response = client.send_message("What number did I tell you to remember?")
        # Response should indicate agent doesn't remember
        assert any(
            word in response.lower()
            for word in ["don't", "no record", "haven't", "didn't"]
        )
    finally:
        client.stop()


# ============================================================================
# Event Listener Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.skip(reason="CLI does not currently send agent_message_end events")
def test_event_listener_messages():
    """Test event listener receives agent messages."""
    listener = EventListenerForTesting()

    with AuggieACPClient(listener=listener) as client:
        response = client.send_message("What is 7 + 3?")

        # Give a moment for the agent_message_end event to arrive
        # (it may arrive slightly after send_message returns)
        time.sleep(0.5)

        # Listener should have received message chunks
        assert len(listener.message_chunks) > 0

        # Combined message should match response
        full_message = listener.get_full_message()
        assert full_message.strip() == response.strip()

        # Should also have received the complete message
        assert len(listener.complete_messages) > 0
        assert listener.complete_messages[0].strip() == response.strip()


@pytest.mark.integration
@pytest.mark.timeout(30)
@pytest.mark.skip(
    reason="Test times out - tool call events may not be working correctly"
)
def test_event_listener_tool_calls():
    """Test event listener receives tool call events."""
    listener = EventListenerForTesting()

    with AuggieACPClient(listener=listener) as client:
        # Send a message that will trigger a tool call
        client.send_message(
            "Read the file experimental/guy/auggie_sdk/QUICK_START.md", timeout=30.0
        )

        # Should have received tool call events
        assert len(listener.tool_calls) > 0

        # Should have at least one "call" event
        call_events = [tc for tc in listener.tool_calls if tc["type"] == "call"]
        assert len(call_events) > 0

        # Should have at least one "response" event
        response_events = [tc for tc in listener.tool_calls if tc["type"] == "response"]
        assert len(response_events) > 0

        # At least one tool call should be "view" (for reading the file)
        tool_titles = [tc.get("title") for tc in listener.tool_calls]
        assert "view" in tool_titles


# ============================================================================
# Timeout and Error Handling Tests
# ============================================================================


@pytest.mark.integration
def test_timeout_handling():
    """Test that timeout parameter works."""
    with AuggieACPClient() as client:
        # Short timeout should still work for simple queries
        response = client.send_message("What is 1 + 1?", timeout=5.0)
        assert "2" in response


@pytest.mark.integration
def test_error_when_not_started():
    """Test that sending message without starting raises error."""
    client = AuggieACPClient()

    with pytest.raises(RuntimeError) as exc_info:
        client.send_message("Hello")

    assert "not started" in str(exc_info.value).lower()


@pytest.mark.integration
def test_double_start_raises_error():
    """Test that starting an already started client raises error."""
    client = AuggieACPClient()
    client.start()

    try:
        with pytest.raises(RuntimeError) as exc_info:
            client.start()

        assert "already started" in str(exc_info.value).lower()
    finally:
        client.stop()


# ============================================================================
# Session Management Tests
# ============================================================================


@pytest.mark.integration
def test_multiple_sequential_sessions():
    """Test starting and stopping multiple times."""
    client = AuggieACPClient()

    # First session
    client.start()
    session1 = client.session_id
    response1 = client.send_message("What is 2 + 2?")
    assert "4" in response1
    client.stop()

    # Second session
    client.start()
    session2 = client.session_id
    response2 = client.send_message("What is 3 + 3?")
    assert "6" in response2
    client.stop()

    # Sessions should be different
    assert session1 != session2


@pytest.mark.integration
@pytest.mark.timeout(30)
def test_long_response():
    """Test handling longer responses."""
    with AuggieACPClient() as client:
        response = client.send_message(
            "List three programming languages. Be brief.", timeout=30.0
        )

        # Should get a response with some content
        assert len(response) > 10


@pytest.mark.integration
@pytest.mark.timeout(30)
@pytest.mark.skip(reason="Tool call events not being received from CLI")
def test_file_operation_tool_call():
    """Test that file operations trigger appropriate tool calls."""
    listener = EventListenerForTesting()

    with AuggieACPClient(listener=listener) as client:
        response = client.send_message(
            "What is in the file experimental/guy/auggie_sdk/QUICK_START.md? Summarize in one sentence.",
            timeout=30.0,
        )

        # Should have triggered a view tool call
        tool_titles = [
            tc.get("title") for tc in listener.tool_calls if tc["type"] == "start"
        ]
        assert "view" in tool_titles

        # Response should mention something about the file
        assert len(response) > 20


@pytest.mark.integration
def test_listener_can_be_none():
    """Test that listener is optional."""
    # Should work fine without a listener
    with AuggieACPClient(listener=None) as client:
        response = client.send_message("What is 5 * 5?")
        assert "25" in response


@pytest.mark.integration
def test_session_persistence():
    """Test that session persists across multiple messages."""
    listener = EventListenerForTesting()

    with AuggieACPClient(listener=listener) as client:
        session_id = client.session_id

        # Send multiple messages
        for i in range(3):
            listener.reset()
            client.send_message(f"What is {i} + 1?")

            # Session should remain the same
            assert client.session_id == session_id

            # Should get message chunks each time
            assert len(listener.message_chunks) > 0


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
def test_conversation_flow():
    """Test a realistic conversation flow."""
    listener = EventListenerForTesting()

    with AuggieACPClient(listener=listener) as client:
        # Start a conversation
        response1 = client.send_message("What is 10 + 5?")
        assert "15" in response1

        # Continue the conversation
        listener.reset()
        response2 = client.send_message("What is that divided by 3?")
        assert "5" in response2

        # Clear context and start fresh
        client.clear_context()
        listener.reset()

        # Agent should not remember the previous numbers
        response3 = client.send_message("What was the last number we calculated?")
        assert any(
            word in response3.lower() for word in ["don't", "no record", "haven't"]
        )


@pytest.mark.integration
@pytest.mark.timeout(30)
@pytest.mark.skip(reason="Tool call events not being received from CLI")
def test_tool_usage_workflow():
    """Test a workflow that involves tool usage."""
    listener = EventListenerForTesting()

    with AuggieACPClient(listener=listener) as client:
        # Ask agent to read a file
        response = client.send_message(
            "Read experimental/guy/auggie_sdk/QUICK_START.md and tell me what it's about in 5 words or less.",
            timeout=30.0,
        )

        # Should have used the view tool
        tool_titles = [
            tc.get("title") for tc in listener.tool_calls if tc["type"] == "start"
        ]
        assert "view" in tool_titles

        # Should have gotten a response
        assert len(response) > 5

        # Should have received completion status
        statuses = [
            tc.get("status") for tc in listener.tool_calls if tc["type"] == "update"
        ]
        assert "completed" in statuses
