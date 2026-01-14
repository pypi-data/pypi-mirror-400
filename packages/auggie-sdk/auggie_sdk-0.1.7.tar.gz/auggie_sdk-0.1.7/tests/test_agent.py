"""
Tests for the Agent class (ACP-based implementation).
"""

import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from auggie_sdk.acp import ACPClient
from auggie_sdk import Auggie, Model
from auggie_sdk.exceptions import (
    AugmentCLIError,
    AugmentNotFoundError,
    AugmentParseError,
    AugmentWorkspaceError,
)


def make_type_inference_response(value, type_name="str", message="Response"):
    """
    Helper to create a type inference response.

    Args:
        value: The value to return (will be JSON-encoded for non-strings)
        type_name: Type name from DEFAULT_INFERENCE_TYPES (int, float, bool, str, list, dict)
        message: The agent message
    """
    import json

    # Note: str values are returned as-is by the parser (no JSON parsing),
    # so we don't JSON-encode them here. Other types are JSON-encoded.
    if isinstance(value, str):
        json_value = value  # Return raw string without JSON encoding
    elif isinstance(value, (int, float, bool)):
        json_value = json.dumps(value)
    elif isinstance(value, (list, dict)):
        json_value = json.dumps(value)
    else:
        json_value = str(value)

    return f"""<augment-agent-message>
{message}
</augment-agent-message>

<augment-agent-type>
{type_name}
</augment-agent-type>

<augment-agent-result>
{json_value}
</augment-agent-result>"""


class Priority(Enum):
    """Test enum for typed responses."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    """Test dataclass for typed responses."""

    name: str
    priority: str
    completed: bool


class TestAgent:
    """Test cases for the Agent class."""

    @staticmethod
    def _create_mock_client(
        return_value="Response", session_id="test-session-123", is_running=False
    ):
        """Helper to create a properly configured mock ACP client."""
        mock_client = MagicMock()
        mock_client.send_message.return_value = return_value
        mock_client.session_id = session_id
        mock_client.is_running = is_running
        return mock_client

    def test_init_default(self):
        """Test agent initialization with default parameters."""
        agent = Auggie()
        assert agent.workspace_path == Path.cwd()
        assert agent.model is None
        assert agent.listener is None
        assert agent._in_session is False

    def test_init_custom(self):
        """Test agent initialization with custom workspace."""
        workspace = "/tmp"  # Use existing directory
        agent = Auggie(workspace_root=workspace)
        assert agent.workspace_path == Path(workspace).resolve()

    def test_init_with_model(self):
        """Test agent initialization with model."""
        agent = Auggie(model="sonnet4.5")
        assert agent.model == "sonnet4.5"

    def test_init_invalid_workspace(self):
        """Test agent initialization with invalid workspace."""
        with pytest.raises(AugmentWorkspaceError):
            Auggie(workspace_root="/nonexistent/path")

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_success(self, mock_acp_client_class):
        """Test successful agent execution - creates client and clears context."""
        # Mock ACP client
        mock_client = MagicMock()

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        # Return type inference format (type name = str from DEFAULT_INFERENCE_TYPES)
        mock_client.send_message.return_value = """<augment-agent-message>
Agent response message
</augment-agent-message>

<augment-agent-type>
str
</augment-agent-type>

<augment-agent-result>
Agent response message
</augment-agent-result>"""
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        result = agent.run("Test instruction")

        assert result == "Agent response message"
        assert isinstance(result, str)
        # Client should be created, started, context cleared, and used
        mock_acp_client_class.assert_called_once()
        mock_client.start.assert_called_once()
        mock_client.clear_context.assert_called_once()
        mock_client.send_message.assert_called_once()

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_typed_int(self, mock_acp_client_class):
        """Test typed response with int."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.send_message.return_value = """
<augment-agent-message>
The answer is 4.
</augment-agent-message>

<augment-agent-result>
4
</augment-agent-result>
"""
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        result = agent.run("What is 2 + 2?", return_type=int)

        assert result == 4
        assert isinstance(result, int)
        assert agent.last_model_answer == "The answer is 4."

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_typed_str(self, mock_acp_client_class):
        """Test typed response with str."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.send_message.return_value = """
<augment-agent-message>
Here's the greeting.
</augment-agent-message>

<augment-agent-result>
Hello, World!
</augment-agent-result>
"""
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        result = agent.run("Say hello", return_type=str)

        assert result == "Hello, World!"
        assert isinstance(result, str)

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_typed_bool(self, mock_acp_client_class):
        """Test typed response with bool."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.send_message.return_value = """
<augment-agent-message>
Yes, it is.
</augment-agent-message>

<augment-agent-result>
true
</augment-agent-result>
"""
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        result = agent.run("Is this true?", return_type=bool)

        assert result is True
        assert isinstance(result, bool)

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_typed_list(self, mock_acp_client_class):
        """Test typed response with list."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.send_message.return_value = """
<augment-agent-message>
Here are the numbers.
</augment-agent-message>

<augment-agent-result>
[1, 2, 3, 4, 5]
</augment-agent-result>
"""
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        result = agent.run("List numbers 1-5", return_type=list)

        assert result == [1, 2, 3, 4, 5]
        assert isinstance(result, list)

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_typed_dict(self, mock_acp_client_class):
        """Test typed response with dict."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.send_message.return_value = """
<augment-agent-message>
Here's the data.
</augment-agent-message>

<augment-agent-result>
{"name": "Alice", "age": 30}
</augment-agent-result>
"""
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        result = agent.run("Get user data", return_type=dict)

        assert result == {"name": "Alice", "age": 30}
        assert isinstance(result, dict)

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_typed_dataclass(self, mock_acp_client_class):
        """Test typed response with dataclass."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.send_message.return_value = """
<augment-agent-message>
Here's the task.
</augment-agent-message>

<augment-agent-result>
{"name": "Write tests", "priority": "high", "completed": false}
</augment-agent-result>
"""
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        result = agent.run("Create a task", return_type=Task)

        assert isinstance(result, Task)
        assert result.name == "Write tests"
        assert result.priority == "high"
        assert result.completed is False

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_typed_enum(self, mock_acp_client_class):
        """Test typed response with enum."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.send_message.return_value = """
<augment-agent-message>
The priority is high.
</augment-agent-message>

<augment-agent-result>
"high"
</augment-agent-result>
"""
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        result = agent.run("What's the priority?", return_type=Priority)

        assert result == Priority.HIGH
        assert isinstance(result, Priority)

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_typed_list_of_dataclass(self, mock_acp_client_class):
        """Test typed response with list of dataclass."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.send_message.return_value = """
<augment-agent-message>
Here are the tasks.
</augment-agent-message>

<augment-agent-result>
[
  {"name": "Task 1", "priority": "high", "completed": true},
  {"name": "Task 2", "priority": "low", "completed": false}
]
</augment-agent-result>
"""
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        result = agent.run("List tasks", return_type=list[Task])

        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Task)
        assert result[0].name == "Task 1"
        assert result[1].name == "Task 2"

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_parse_error_exhausts_retries(self, mock_acp_client_class):
        """Test parse error when result tags are missing after all retries."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.send_message.return_value = "No structured result here"
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()

        # Should retry max_retries times (default 3) + initial attempt = 4 total calls
        with pytest.raises(AugmentParseError, match="No structured result found"):
            agent.run("Test", return_type=int, max_retries=3)

        # Verify it tried 4 times (1 initial + 3 retries)
        assert mock_client.send_message.call_count == 4

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_parse_error_succeeds_on_retry(self, mock_acp_client_class):
        """Test that parsing succeeds on retry after initial failure."""
        # Mock ACP client
        mock_client = MagicMock()
        # First call fails, second call succeeds
        mock_client.send_message.side_effect = [
            "No structured result here",  # First attempt fails
            """<augment-agent-message>
Here's the corrected response.
</augment-agent-message>

<augment-agent-result>
42
</augment-agent-result>""",  # Second attempt succeeds
        ]
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()

        result = agent.run("Test", return_type=int, max_retries=3)

        assert result == 42
        assert isinstance(result, int)
        # Should have called twice (1 initial + 1 retry)
        assert mock_client.send_message.call_count == 2

        # Verify the retry instruction mentions the error
        retry_call = mock_client.send_message.call_args_list[1]
        retry_instruction = retry_call[0][0]
        assert "previous response could not be parsed" in retry_instruction.lower()
        assert "Error:" in retry_instruction

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_custom_max_retries(self, mock_acp_client_class):
        """Test custom max_retries parameter."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.send_message.return_value = "No structured result here"
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()

        # Set max_retries to 1
        with pytest.raises(AugmentParseError):
            agent.run("Test", return_type=int, max_retries=1)

        # Should have called twice (1 initial + 1 retry)
        assert mock_client.send_message.call_count == 2

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_automatic_type_inference(self, mock_acp_client_class):
        """Test that no return_type triggers automatic type inference."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.session_id = "test-session-123"

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        # Agent chooses type int from default types
        mock_client.send_message.return_value = """<augment-agent-message>
The result is 42.
</augment-agent-message>

<augment-agent-type>
int
</augment-agent-type>

<augment-agent-result>
42
</augment-agent-result>"""

        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        result = agent.run("What is 2 + 2?")  # No return_type

        assert result == 42
        assert isinstance(result, int)

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_retry_with_clear_context(self, mock_acp_client_class):
        """Test that retry loop maintains context (doesn't clear between retries)."""
        # Mock ACP client with proper is_running tracking
        mock_client = MagicMock()
        mock_client.session_id = "test-session-123"

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        # First call: bad response (no structured result)
        # Second call: good response (after retry)
        mock_client.send_message.side_effect = [
            "The answer is four",  # First attempt - bad format
            """<augment-agent-message>
Here's the corrected response.
</augment-agent-message>

<augment-agent-result>
4
</augment-agent-result>""",  # Second attempt - good format
        ]

        mock_acp_client_class.return_value = mock_client

        agent = Auggie()

        result = agent.run("What is 2 + 2?", return_type=int, max_retries=3)

        assert result == 4
        assert isinstance(result, int)

        # Verify the flow:
        # 1. Client created and started once
        assert mock_acp_client_class.call_count == 1
        assert mock_client.start.call_count == 1

        # 2. Context cleared once (at the start, not in session)
        assert mock_client.clear_context.call_count == 1

        # 3. Two messages sent (initial + 1 retry)
        assert mock_client.send_message.call_count == 2

        # 4. Verify the retry instruction mentions the error
        retry_call = mock_client.send_message.call_args_list[1]
        retry_instruction = retry_call[0][0]
        assert "previous response could not be parsed" in retry_instruction.lower()
        assert "Error:" in retry_instruction
        # Note: We don't include the previous bad response - the agent already knows what it said

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_retry_in_session_no_clear_context(self, mock_acp_client_class):
        """Test that retry loop in session doesn't clear context."""
        # Mock ACP client with proper is_running tracking
        mock_client = MagicMock()
        mock_client.session_id = "test-session-123"

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        # First call: bad response
        # Second call: good response
        mock_client.send_message.side_effect = [
            "The answer is four",  # Bad format
            """<augment-agent-message>
Corrected.
</augment-agent-message>

<augment-agent-result>
4
</augment-agent-result>""",  # Good format
        ]

        mock_acp_client_class.return_value = mock_client

        agent = Auggie()

        # Run inside a session
        with agent.session() as session:
            result = session.run("What is 2 + 2?", return_type=int, max_retries=3)

        assert result == 4

        # Verify context was NOT cleared (we're in a session)
        mock_client.clear_context.assert_not_called()

        # Two messages sent (initial + 1 retry)
        assert mock_client.send_message.call_count == 2

    def test_run_empty_instruction(self):
        """Test empty instruction validation."""
        agent = Auggie()

        with pytest.raises(ValueError, match="Instruction cannot be empty"):
            agent.run("")

        with pytest.raises(ValueError, match="Instruction cannot be empty"):
            agent.run("   ")

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_automatic_type_inference_int(self, mock_acp_client_class):
        """Test automatic type inference with agent choosing int type."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.session_id = "test-session-123"

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        # Agent chooses type int from DEFAULT_INFERENCE_TYPES and returns 42
        mock_client.send_message.return_value = """<augment-agent-message>
The result is an integer.
</augment-agent-message>

<augment-agent-type>
int
</augment-agent-type>

<augment-agent-result>
42
</augment-agent-result>"""

        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        result = agent.run("What is 2 + 2?")  # No return_type

        assert result == 42
        assert isinstance(result, int)

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_automatic_type_inference_str(self, mock_acp_client_class):
        """Test automatic type inference with agent choosing str type."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.session_id = "test-session-123"

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        # Agent chooses type str from DEFAULT_INFERENCE_TYPES: int, float, bool, str, list, dict
        mock_client.send_message.return_value = """<augment-agent-message>
The result is a string.
</augment-agent-message>

<augment-agent-type>
str
</augment-agent-type>

<augment-agent-result>
hello
</augment-agent-result>"""

        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        result = agent.run("Say hello")  # No return_type

        assert result == "hello"
        assert isinstance(result, str)

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_automatic_type_inference_missing_type_tag(self, mock_acp_client_class):
        """Test automatic type inference when type tag is missing falls back to string."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.session_id = "test-session-123"

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        # Missing type tag - should fall back to returning content as string
        mock_client.send_message.return_value = """<augment-agent-message>
The result.
</augment-agent-message>

<augment-agent-result>
42
</augment-agent-result>"""

        mock_acp_client_class.return_value = mock_client

        agent = Auggie()

        # When type tag is missing but content exists, it falls back to string
        result = agent.run("Test", max_retries=0)
        # Result is the entire response as a string (fallback behavior)
        assert isinstance(result, str)

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_automatic_type_inference_invalid_type_index(
        self, mock_acp_client_class
    ):
        """Test automatic type inference error when type index is out of range."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.session_id = "test-session-123"

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        # Invalid type name (not in DEFAULT_INFERENCE_TYPES)
        mock_client.send_message.return_value = """<augment-agent-message>
The result.
</augment-agent-message>

<augment-agent-type>
InvalidType
</augment-agent-type>

<augment-agent-result>
42
</augment-agent-result>"""

        mock_acp_client_class.return_value = mock_client

        agent = Auggie()

        with pytest.raises(AugmentParseError, match="Invalid type name"):
            agent.run(
                "Test", max_retries=0
            )  # No return_type triggers automatic inference

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_run_automatic_type_inference_with_retry(self, mock_acp_client_class):
        """Test automatic type inference with retry on parse failure (invalid type name)."""
        # Mock ACP client
        mock_client = MagicMock()
        mock_client.session_id = "test-session-123"

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        # First: invalid type name, Second: correct
        mock_client.send_message.side_effect = [
            """<augment-agent-message>
Invalid type name.
</augment-agent-message>

<augment-agent-type>
invalid_type
</augment-agent-type>

<augment-agent-result>
42
</augment-agent-result>""",
            """<augment-agent-message>
Corrected with type.
</augment-agent-message>

<augment-agent-type>
int
</augment-agent-type>

<augment-agent-result>
42
</augment-agent-result>""",
        ]

        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        result = agent.run(
            "Test", max_retries=3
        )  # No return_type triggers automatic inference

        assert result == 42
        assert isinstance(result, int)
        # Should have retried once (first had invalid type name)
        assert mock_client.send_message.call_count == 2

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_session_context_manager(self, mock_acp_client_class):
        """Test session context manager maintains persistent client."""
        # Mock ACP client
        mock_client = MagicMock()

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        mock_client.send_message.return_value = make_type_inference_response("Response")
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()

        with agent.session() as session:
            assert session is agent  # Session returns the same agent
            result = session.run("Test instruction")
            assert result == "Response"
            assert isinstance(result, str)
            # Inside session, client should be persistent
            assert agent._in_session is True
            # Context should NOT be cleared inside session
            mock_client.clear_context.assert_not_called()

        # After session, flag should be cleared but client remains
        assert agent._in_session is False
        assert agent._acp_client is not None  # Client is kept for reuse

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_multiple_run_calls_are_independent(self, mock_acp_client_class):
        """Test that multiple run() calls without session clear context."""
        # Mock ACP client with proper is_running tracking
        mock_client = MagicMock()
        mock_client.send_message.return_value = make_type_inference_response("Response")
        mock_client.session_id = "test-session-123"

        # Track running state properly
        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        mock_acp_client_class.return_value = mock_client

        agent = Auggie()

        # Each call clears context for independence
        result1 = agent.run("First instruction")
        result2 = agent.run("Second instruction")

        assert result1 == "Response"
        assert result2 == "Response"

        # Client should be created once and reused
        assert mock_acp_client_class.call_count == 1
        # Client should be started once (first call)
        assert mock_client.start.call_count == 1
        # Context should be cleared twice (once per call)
        assert mock_client.clear_context.call_count == 2
        # Both messages should be sent
        assert mock_client.send_message.call_count == 2

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_get_workspace_path(self, mock_acp_client_class):
        """Test getting workspace path."""
        workspace = "/tmp"  # Use existing directory
        agent = Auggie(workspace_root=workspace)

        workspace_path = agent.get_workspace_path()
        assert workspace_path == Path(workspace).resolve()

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_session_id_property(self, mock_acp_client_class):
        """Test session_id property - only set inside session context."""
        # Mock ACP client
        mock_client = MagicMock()

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        mock_client.send_message.return_value = make_type_inference_response("Response")
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()

        # Outside session, session_id should be None
        assert agent.session_id is None

        # After standalone run(), session_id should still be None
        agent.run("Test")
        assert agent.session_id is None

        # Inside session, session_id should be set
        with agent.session() as session:
            assert session.session_id == "test-session-123"

    def test_repr(self):
        """Test string representation."""
        agent = Auggie()
        repr_str = repr(agent)
        assert "Agent" in repr_str
        assert str(agent.workspace_path) in repr_str

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_repr_with_session(self, mock_acp_client_class):
        """Test string representation with session - session_id only shown inside session context."""
        # Mock ACP client
        mock_client = MagicMock()

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        mock_client.send_message.return_value = make_type_inference_response("Response")
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()

        # Inside session, repr should include session_id
        with agent.session() as session:
            # Need to trigger client creation by running something
            session.run("Test")
            repr_str = repr(session)
            assert "Agent" in repr_str
            assert "test-session-123" in repr_str

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_cleanup_on_delete(self, mock_acp_client_class):
        """Test cleanup when agent is deleted."""
        # Mock ACP client
        mock_client = MagicMock()

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        mock_client.send_message.return_value = make_type_inference_response("Response")
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        agent.run("Test")

        # Delete agent
        del agent

        # Client should be stopped
        mock_client.stop.assert_called_once()

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_timeout_parameter(self, mock_acp_client_class):
        """Test timeout parameter is passed to ACP client."""
        # Mock ACP client
        mock_client = MagicMock()

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        mock_client.send_message.return_value = make_type_inference_response("Response")
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie()
        agent.run("Test instruction", timeout=60)

        # Verify timeout was passed to send_message
        mock_client.send_message.assert_called_once()
        # Check positional args - timeout is the second positional argument
        call_args = mock_client.send_message.call_args
        assert call_args[0][1] == 60.0  # Second positional arg is timeout

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_model_passed_to_client(self, mock_acp_client_class):
        """Test that model is passed to ACP client."""
        # Mock ACP client
        mock_client = MagicMock()

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        mock_client.send_message.return_value = make_type_inference_response("Response")
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        agent = Auggie(model="claude-3-5-sonnet-latest")
        agent.run("Test")

        # Verify model was passed to ACP client constructor
        mock_acp_client_class.assert_called_once()
        call_kwargs = mock_acp_client_class.call_args[1]
        assert call_kwargs["model"] == "claude-3-5-sonnet-latest"

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_workspace_passed_to_client(self, mock_acp_client_class):
        """Test that workspace_root is passed to ACP client."""
        # Mock ACP client
        mock_client = MagicMock()

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect

        mock_client.send_message.return_value = make_type_inference_response("Response")
        mock_client.session_id = "test-session-123"
        mock_acp_client_class.return_value = mock_client

        workspace = "/tmp"
        agent = Auggie(workspace_root=workspace)
        agent.run("Test")

        # Verify workspace_root was passed to ACP client constructor
        mock_acp_client_class.assert_called_once()
        call_kwargs = mock_acp_client_class.call_args[1]
        assert call_kwargs["workspace_root"] == str(Path(workspace).resolve())


class TestGetAvailableModels:
    """Test cases for get_available_models static method."""

    @patch("auggie_sdk.agent.subprocess.run")
    def test_get_available_models_success(self, mock_run):
        """Test successful retrieval of available models."""
        # Mock successful command execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """Available models:
 - Claude Haiku 4.5 [haiku4.5]
     Anthropic Claude Haiku 4.5
 - Claude Sonnet 4.5 [sonnet4.5]
     Anthropic Claude Sonnet 4.5, 200k context
 - GPT-5 Codex [gpt5-codex]
     OpenAI GPT-5 codex, 200k context
"""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        models = Auggie.get_available_models()

        assert len(models) == 3
        assert all(isinstance(m, Model) for m in models)

        # Check first model
        assert models[0].id == "haiku4.5"
        assert models[0].name == "Claude Haiku 4.5"
        assert models[0].description == "Anthropic Claude Haiku 4.5"

        # Check second model
        assert models[1].id == "sonnet4.5"
        assert models[1].name == "Claude Sonnet 4.5"
        assert models[1].description == "Anthropic Claude Sonnet 4.5, 200k context"

        # Check third model
        assert models[2].id == "gpt5-codex"
        assert models[2].name == "GPT-5 Codex"
        assert models[2].description == "OpenAI GPT-5 codex, 200k context"

        # Verify subprocess was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args == ["auggie", "model", "list"]

    @patch("auggie_sdk.agent.subprocess.run")
    def test_get_available_models_not_found(self, mock_run):
        """Test when auggie CLI is not found."""
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(AugmentNotFoundError, match="auggie CLI not found"):
            Auggie.get_available_models()

    @patch("auggie_sdk.agent.subprocess.run")
    def test_get_available_models_timeout(self, mock_run):
        """Test timeout handling."""
        mock_run.side_effect = subprocess.TimeoutExpired("auggie", 30)

        with pytest.raises(AugmentCLIError, match="timed out"):
            Auggie.get_available_models()

    @patch("auggie_sdk.agent.subprocess.run")
    def test_get_available_models_cli_error(self, mock_run):
        """Test CLI error handling."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error: Authentication failed"
        mock_run.return_value = mock_result

        with pytest.raises(AugmentCLIError, match="Failed to get model list"):
            Auggie.get_available_models()

    @patch("auggie_sdk.agent.subprocess.run")
    def test_get_available_models_empty_list(self, mock_run):
        """Test handling of empty model list."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Available models:\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        models = Auggie.get_available_models()

        assert models == []

    @patch("auggie_sdk.agent.subprocess.run")
    def test_get_available_models_no_description(self, mock_run):
        """Test model without description."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """Available models:
 - Test Model [test-model]
"""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        models = Auggie.get_available_models()

        assert len(models) == 1
        assert models[0].id == "test-model"
        assert models[0].name == "Test Model"
        assert models[0].description == ""

    def test_model_dataclass(self):
        """Test Model dataclass."""
        model = Model(
            id="sonnet4.5",
            name="Claude Sonnet 4.5",
            description="Anthropic Claude Sonnet 4.5, 200k context",
        )

        assert model.id == "sonnet4.5"
        assert model.name == "Claude Sonnet 4.5"
        assert model.description == "Anthropic Claude Sonnet 4.5, 200k context"
        assert str(model) == "Claude Sonnet 4.5 [sonnet4.5]"


class TestProvidedACPClient:
    """Test cases for using a provided ACP client."""

    def test_agent_with_provided_client(self):
        """Test creating an agent with a provided ACP client."""
        # Create a mock ACP client
        mock_client = MagicMock(spec=ACPClient)
        mock_client.is_running = False
        mock_client.send_message.return_value = "Test response"

        # Create agent with the mock client
        agent = Auggie(acp_client=mock_client)

        # Verify the client was stored
        assert agent._acp_client is mock_client
        assert agent._provided_client is True

    def test_run_with_provided_client(self):
        """Test that run() uses the provided client."""
        # Create a mock ACP client
        mock_client = MagicMock(spec=ACPClient)
        mock_client.is_running = False
        mock_client.send_message.return_value = make_type_inference_response(
            42, type_name="int"
        )

        # Create agent with the mock client
        agent = Auggie(acp_client=mock_client)

        # Run a command
        result = agent.run("What is 2 + 2?")

        # Verify the mock client was used
        assert result == 42
        assert isinstance(result, int)
        mock_client.start.assert_called_once()
        mock_client.send_message.assert_called_once()
        # Provided client should NOT be stopped
        mock_client.stop.assert_not_called()

    def test_run_with_provided_running_client(self):
        """Test that run() doesn't restart an already running provided client."""
        # Create a mock ACP client that's already running
        mock_client = MagicMock(spec=ACPClient)
        mock_client.is_running = True
        mock_client.send_message.return_value = make_type_inference_response("Response")

        # Create agent with the mock client
        agent = Auggie(acp_client=mock_client)

        # Run a command
        result = agent.run("Test")

        # Verify the mock client was used but not restarted
        assert result == "Response"
        assert isinstance(result, str)
        mock_client.start.assert_not_called()
        mock_client.send_message.assert_called_once()
        mock_client.stop.assert_not_called()

    def test_session_with_provided_client(self):
        """Test that session() uses the provided client."""
        # Create a mock ACP client with proper is_running tracking
        mock_client = MagicMock(spec=ACPClient)

        def start_side_effect():
            mock_client.is_running = True

        mock_client.is_running = False
        mock_client.start.side_effect = start_side_effect
        mock_client.send_message.side_effect = [
            make_type_inference_response("First"),
            make_type_inference_response("Second"),
        ]

        # Create agent with the mock client
        agent = Auggie(acp_client=mock_client)

        # Use session
        with agent.session() as session:
            result1 = session.run("First message")
            result2 = session.run("Second message")

        # Verify the mock client was used
        assert result1 == "First"
        assert result2 == "Second"
        assert mock_client.send_message.call_count == 2
        # Client should be started once (when first run() is called)
        assert mock_client.start.call_count == 1
        # Provided client should NOT be stopped after session
        mock_client.stop.assert_not_called()

    def test_session_with_provided_running_client(self):
        """Test session with an already running provided client."""
        # Create a mock ACP client that's already running
        mock_client = MagicMock(spec=ACPClient)
        mock_client.is_running = True
        mock_client.send_message.return_value = make_type_inference_response("Response")

        # Create agent with the mock client
        agent = Auggie(acp_client=mock_client)

        # Use session
        with agent.session() as session:
            result = session.run("Test")

        # Verify the mock client was used but not restarted
        assert result == "Response"
        assert isinstance(result, str)
        mock_client.start.assert_not_called()
        mock_client.stop.assert_not_called()

    def test_provided_client_not_stopped_on_error(self):
        """Test that provided client is not stopped even if an error occurs."""
        # Create a mock ACP client that raises an error
        mock_client = MagicMock(spec=ACPClient)
        mock_client.is_running = False
        mock_client.send_message.side_effect = RuntimeError("Test error")

        # Create agent with the mock client
        agent = Auggie(acp_client=mock_client)

        # Run should raise the error
        with pytest.raises(RuntimeError, match="Test error"):
            agent.run("Test")

        # Provided client should NOT be stopped even on error
        mock_client.stop.assert_not_called()

    def test_agent_without_provided_client_creates_own(self):
        """Test that agent without provided client creates its own."""
        # Create agent without provided client
        agent = Auggie()

        # Verify no client was provided
        assert agent._acp_client is None
        assert agent._provided_client is False
