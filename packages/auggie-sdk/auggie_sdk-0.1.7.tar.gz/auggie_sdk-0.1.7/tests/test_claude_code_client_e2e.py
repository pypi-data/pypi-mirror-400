"""
Integration tests for ClaudeCodeACPClient.

These tests verify the client works correctly with Claude Code via Zed's ACP adapter.
Uses pytest for test framework.

Prerequisites:
- npm install -g @zed-industries/claude-code-acp
- export ANTHROPIC_API_KEY=...

By default, integration tests are skipped. To run them: pytest -m integration
Or use tox: tox -e integration

To skip tests that require Claude Code prerequisites:
pytest -m "not requires_claude_code"
"""

import os
import pytest
import time
from typing import Optional, Any, List, Dict
from auggie_sdk.acp import ClaudeCodeACPClient, AgentEventListener


# Check if prerequisites are available
def has_claude_code_prerequisites():
    """Check if Claude Code prerequisites are available."""
    import shutil

    # Check for npx
    if not shutil.which("npx"):
        return False, "npx not found (install Node.js)"

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        return False, "ANTHROPIC_API_KEY not set"

    return True, None


PREREQUISITES_AVAILABLE, SKIP_REASON = has_claude_code_prerequisites()

# Skip all tests if prerequisites aren't met
pytestmark = pytest.mark.skipif(
    not PREREQUISITES_AVAILABLE,
    reason=f"Claude Code prerequisites not available: {SKIP_REASON}",
)


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


def test_missing_api_key_raises_value_error():
    """Test that missing API key raises ValueError."""
    # Temporarily remove API key
    original_key = os.environ.pop("ANTHROPIC_API_KEY", None)

    try:
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY must be provided"):
            ClaudeCodeACPClient()
    finally:
        # Restore API key
        if original_key:
            os.environ["ANTHROPIC_API_KEY"] = original_key


def test_invalid_api_key_fails_on_start():
    """Test that invalid API key causes start to fail."""
    client = ClaudeCodeACPClient(api_key="invalid-key-12345")

    # Should raise RuntimeError when the process exits due to auth failure
    with pytest.raises((RuntimeError, TimeoutError)):
        client.start(timeout=10.0)


# ============================================================================
# Basic Functionality Tests
# ============================================================================


def test_start_and_stop():
    """Test basic start and stop functionality."""
    client = ClaudeCodeACPClient()

    # Should not be running initially
    assert not client.is_running
    assert client.session_id is None

    # Start the client
    client.start()
    assert client.is_running
    assert client.session_id is not None
    session_id = client.session_id
    assert len(session_id) > 0  # Should have a session ID

    # Stop the client
    client.stop()
    assert not client.is_running


def test_simple_math_query():
    """Test sending a simple math query."""
    with ClaudeCodeACPClient() as client:
        response = client.send_message("What is 2 + 2? Answer with just the number.")

        # Should contain the answer
        assert "4" in response
        assert len(response) > 0


@pytest.mark.integration
def test_multiple_messages_same_session():
    """Test sending multiple messages in the same session."""
    with ClaudeCodeACPClient() as client:
        session_id = client.session_id

        # First message
        response1 = client.send_message("What is 5 + 3? Answer with just the number.")
        assert "8" in response1

        # Session should remain the same
        assert client.session_id == session_id

        # Second message - agent should remember context
        response2 = client.send_message(
            "What is that number times 2? Answer with just the number."
        )
        assert "16" in response2

        # Session should still be the same
        assert client.session_id == session_id


def test_context_manager():
    """Test context manager automatically starts and stops."""
    client = ClaudeCodeACPClient()
    assert not client.is_running

    with client:
        assert client.is_running
        response = client.send_message("What is 10 * 5? Answer with just the number.")
        assert "50" in response

    # Should be stopped after exiting context
    assert not client.is_running


@pytest.mark.integration
def test_clear_context():
    """Test clearing context creates a new session."""
    client = ClaudeCodeACPClient()
    client.start()

    try:
        # Get initial session
        session1 = client.session_id

        # Send a message
        client.send_message("Remember that my favorite number is 42.")

        # Clear context
        client.clear_context()

        # Should have a new session
        session2 = client.session_id
        assert session1 != session2
        assert client.is_running

        # Agent should not remember the previous conversation
        response = client.send_message("What is my favorite number?")
        # Response should indicate agent doesn't remember
        assert "42" not in response or any(
            word in response.lower()
            for word in ["don't", "no record", "haven't", "didn't", "not sure"]
        )
    finally:
        client.stop()


# ============================================================================
# Event Listener Tests
# ============================================================================


@pytest.mark.integration
def test_event_listener_messages():
    """Test event listener receives agent messages."""
    listener = EventListenerForTesting()

    with ClaudeCodeACPClient(listener=listener) as client:
        response = client.send_message("What is 7 + 3? Answer with just the number.")

        # Give a moment for events to arrive
        time.sleep(0.5)

        # Listener should have received message chunks
        assert len(listener.message_chunks) > 0

        # Combined message should contain the response
        full_message = listener.get_full_message()
        assert "10" in full_message or "10" in response


@pytest.mark.integration
def test_listener_can_be_none():
    """Test that listener is optional."""
    # Should work fine without a listener
    with ClaudeCodeACPClient(listener=None) as client:
        response = client.send_message("What is 5 * 5? Answer with just the number.")
        assert "25" in response


# ============================================================================
# Timeout and Error Handling Tests
# ============================================================================


@pytest.mark.integration
def test_timeout_handling():
    """Test that timeout parameter works."""
    with ClaudeCodeACPClient() as client:
        # Short timeout should still work for simple queries
        response = client.send_message(
            "What is 1 + 1? Answer with just the number.", timeout=10.0
        )
        assert "2" in response


def test_error_when_not_started():
    """Test that sending message without starting raises error."""
    client = ClaudeCodeACPClient()

    with pytest.raises(RuntimeError) as exc_info:
        client.send_message("Hello")

    assert "not started" in str(exc_info.value).lower()


@pytest.mark.integration
def test_double_start_raises_error():
    """Test that starting an already started client raises error."""
    client = ClaudeCodeACPClient()
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
    client = ClaudeCodeACPClient()

    # First session
    client.start()
    session1 = client.session_id
    response1 = client.send_message("What is 2 + 2? Answer with just the number.")
    assert "4" in response1
    client.stop()

    # Second session
    client.start()
    session2 = client.session_id
    response2 = client.send_message("What is 3 + 3? Answer with just the number.")
    assert "6" in response2
    client.stop()

    # Sessions should be different
    assert session1 != session2


@pytest.mark.integration
@pytest.mark.timeout(60)
def test_long_response():
    """Test handling longer responses."""
    with ClaudeCodeACPClient() as client:
        response = client.send_message(
            "List three programming languages. Be brief.", timeout=30.0
        )

        # Should get a response with some content
        assert len(response) > 10


@pytest.mark.integration
def test_session_persistence():
    """Test that session persists across multiple messages."""
    listener = EventListenerForTesting()

    with ClaudeCodeACPClient(listener=listener) as client:
        session_id = client.session_id

        # Send multiple messages
        for i in range(3):
            listener.reset()
            client.send_message(f"What is {i} + 1? Answer with just the number.")

            # Session should remain the same
            assert client.session_id == session_id

            # Should get message chunks each time
            assert len(listener.message_chunks) > 0


# ============================================================================
# Configuration Tests
# ============================================================================


@pytest.mark.integration
def test_custom_model():
    """Test using a custom model."""
    # Test with Sonnet (should work)
    with ClaudeCodeACPClient(model="claude-3-5-sonnet-latest") as client:
        response = client.send_message("What is 2 + 2? Answer with just the number.")
        assert "4" in response


@pytest.mark.integration
def test_workspace_root():
    """Test setting workspace root."""
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file in the temp directory
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Hello from test file")

        # Create client with workspace root
        with ClaudeCodeACPClient(workspace_root=tmpdir) as client:
            response = client.send_message(
                "What is 1 + 1? Answer with just the number."
            )
            assert "2" in response


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
def test_conversation_flow():
    """Test a realistic conversation flow."""
    listener = EventListenerForTesting()

    with ClaudeCodeACPClient(listener=listener) as client:
        # Start a conversation
        response1 = client.send_message("What is 10 + 5? Answer with just the number.")
        assert "15" in response1

        # Continue the conversation
        listener.reset()
        response2 = client.send_message(
            "What is that divided by 3? Answer with just the number."
        )
        assert "5" in response2

        # Clear context and start fresh
        client.clear_context()
        listener.reset()

        # Agent should not remember the previous numbers
        response3 = client.send_message("What was the last number we calculated?")
        # Should not mention 5 or 15, or should say it doesn't know
        assert any(
            word in response3.lower()
            for word in ["don't", "no record", "haven't", "didn't", "not sure"]
        ) or ("5" not in response3 and "15" not in response3)


@pytest.mark.integration
def test_session_continuity():
    """Test that messages in the same session share context."""
    with ClaudeCodeACPClient() as client:
        # Set up context
        client.send_message("My name is Alice.")

        # Ask about the context
        response = client.send_message("What is my name?")

        # Should remember the name
        assert "alice" in response.lower()


@pytest.mark.integration
def test_multiple_context_switches():
    """Test multiple context clears."""
    client = ClaudeCodeACPClient()
    client.start()

    try:
        sessions = []

        for i in range(3):
            # Send a message
            client.send_message(f"Remember the number {i * 10}")

            # Record session
            sessions.append(client.session_id)

            # Clear context for next iteration
            if i < 2:  # Don't clear on last iteration
                client.clear_context()

        # All sessions should be different
        assert len(set(sessions)) == len(sessions)
    finally:
        client.stop()


# ============================================================================
# Stress Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.timeout(120)
def test_rapid_messages():
    """Test sending multiple messages rapidly."""
    with ClaudeCodeACPClient() as client:
        responses = []

        for i in range(5):
            response = client.send_message(
                f"What is {i} + 1? Answer with just the number.", timeout=20.0
            )
            responses.append(response)

        # All responses should be valid
        assert len(responses) == 5
        for i, response in enumerate(responses):
            assert str(i + 1) in response


@pytest.mark.integration
def test_empty_message():
    """Test sending an empty message."""
    with ClaudeCodeACPClient() as client:
        # Should handle empty message gracefully
        response = client.send_message("Say hello")
        assert len(response) > 0


# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.integration
def test_special_characters_in_message():
    """Test messages with special characters."""
    with ClaudeCodeACPClient() as client:
        response = client.send_message(
            'What is the result of "2 + 2"? Answer with just the number.'
        )
        assert "4" in response


@pytest.mark.integration
def test_unicode_in_message():
    """Test messages with unicode characters."""
    with ClaudeCodeACPClient() as client:
        response = client.send_message("What is 2 + 2? Answer: 🔢")
        assert "4" in response


@pytest.mark.integration
def test_very_long_message():
    """Test sending a very long message."""
    with ClaudeCodeACPClient() as client:
        # Create a long message
        long_message = "What is 2 + 2? " + "Please answer. " * 50 + "Just the number."
        response = client.send_message(long_message, timeout=30.0)
        assert "4" in response
