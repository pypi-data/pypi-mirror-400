"""
Integration tests for the Agent class.

These tests verify the Agent works correctly with the actual Augment CLI agent.
They are marked as integration tests and skipped by default.

To run these tests: pytest -m integration
Or use tox: tox -e integration
"""

import pytest
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from auggie_sdk import Auggie
from auggie_sdk.exceptions import AugmentParseError


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


# ============================================================================
# Basic Functionality Tests (Quick Sanity Checks)
# ============================================================================


def test_agent_creation():
    """Test basic agent creation and properties."""
    agent = Auggie()

    assert agent.workspace_path == Path.cwd()
    assert agent.model is None
    assert not agent._in_session
    assert agent.session_id is None


@pytest.mark.integration
def test_simple_query():
    """Test sending a simple query to the agent with automatic type inference."""
    agent = Auggie()

    # No return_type specified, agent infers the type and returns the result
    result = agent.run(
        "What is 2 + 2? Answer with just the number and a brief explanation."
    )

    # Should contain the answer (result could be int or str depending on inference)
    result_str = str(result)
    assert "4" in result_str
    assert result is not None


@pytest.mark.integration
def test_context_manager():
    """Test using agent with context manager and automatic type inference."""
    agent = Auggie()

    with agent.session() as session:
        result = session.run("What is 5 + 3? Answer with just the number.")
        result_str = str(result)
        assert "8" in result_str


# ============================================================================
# Typed Return Tests (Slow)
# ============================================================================


@pytest.mark.integration
def test_typed_return_int():
    """Test typed return with int."""
    agent = Auggie()

    result = agent.run("What is 15 + 27? Return just the number.", return_type=int)

    assert result == 42
    assert isinstance(result, int)
    assert agent.last_model_answer is not None
    assert len(agent.last_model_answer) > 0


@pytest.mark.integration
def test_typed_return_str():
    """Test typed return with str."""
    agent = Auggie()

    result = agent.run(
        "Say 'Hello, World!' - return exactly that string.", return_type=str
    )

    assert "Hello" in result
    assert isinstance(result, str)


@pytest.mark.integration
def test_typed_return_bool():
    """Test typed return with bool."""
    agent = Auggie()

    result = agent.run(
        "Is Python a programming language? Return true or false.", return_type=bool
    )

    assert result is True
    assert isinstance(result, bool)


@pytest.mark.integration
def test_typed_return_list():
    """Test typed return with list."""
    agent = Auggie()

    result = agent.run(
        "Return a list of the numbers 1, 2, 3, 4, 5 as a JSON array.", return_type=list
    )

    assert isinstance(result, list)
    assert len(result) == 5
    assert 1 in result
    assert 5 in result


@pytest.mark.integration
def test_typed_return_dict():
    """Test typed return with dict."""
    agent = Auggie()

    result = agent.run(
        "Return a JSON object with name='Alice' and age=30", return_type=dict
    )

    assert isinstance(result, dict)
    assert "name" in result
    assert "age" in result


@pytest.mark.integration
def test_typed_return_dataclass():
    """Test typed return with dataclass."""
    agent = Auggie()

    result = agent.run(
        "Create a task with name='Write tests', priority='high', completed=false",
        return_type=Task,
    )

    assert isinstance(result, Task)
    assert result.name == "Write tests"
    assert result.priority == "high"
    assert result.completed is False


@pytest.mark.integration
def test_typed_return_enum():
    """Test typed return with enum."""
    agent = Auggie()

    result = agent.run(
        "Return the priority level 'high' from the options: low, medium, high",
        return_type=Priority,
    )

    assert result == Priority.HIGH
    assert isinstance(result, Priority)


@pytest.mark.integration
def test_typed_return_list_of_dataclass():
    """Test typed return with list of dataclass."""
    agent = Auggie()

    result = agent.run(
        """Create 2 tasks:
        1. name='Task 1', priority='high', completed=true
        2. name='Task 2', priority='low', completed=false
        Return as a JSON array of objects.""",
        return_type=list[Task],
    )

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], Task)
    assert isinstance(result[1], Task)
    assert result[0].name == "Task 1"
    assert result[1].name == "Task 2"


# ============================================================================
# Session Management Tests (Slow)
# ============================================================================


@pytest.mark.integration
def test_no_automatic_session_continuity():
    """
    Test that separate run() calls do NOT maintain context.

    Without a session context manager, each run() call creates a fresh session.
    """
    agent = Auggie()

    # First call - remember a number
    agent.run("Remember the number 42. Just acknowledge you'll remember it.")

    # Second call - should NOT remember (no session context)
    result = agent.run(
        "What number did I ask you to remember? If you don't know, say 'I don't know'."
    )
    response = str(result).lower()

    # The agent should not remember because it's a fresh session
    assert (
        "don't know" in response or "do not know" in response or "not sure" in response
    )


@pytest.mark.integration
def test_session_context_manager_continuity():
    """Test session continuity with context manager."""
    agent = Auggie()

    with agent.session() as session:
        # First call
        session.run("Remember the word 'banana'. Just acknowledge you'll remember it.")

        # Second call - should remember
        result = session.run(
            "What word did I ask you to remember? Return just the word."
        )
        response = str(result).lower()

        assert "banana" in response


@pytest.mark.integration
def test_session_context_shares_context():
    """
    Test that calls within a session context manager share context.

    When using the session() context manager, all calls within the context
    share the same session and maintain conversation continuity.
    """
    agent = Auggie()

    with agent.session() as session:
        # Call 1: Create something
        session.run("Remember that my favorite color is blue. Just acknowledge.")

        # Call 2: Reference it (should remember within session)
        result = session.run("What is my favorite color? Return just the color.")
        response = str(result).lower()

        assert "blue" in response

        # Call 3: Still remembers (same session)
        result = session.run(
            "What color did I mention earlier? Return just the color."
        )
        response = str(result).lower()

        assert "blue" in response


# ============================================================================
# Model Configuration Tests (Slow)
# ============================================================================


@pytest.mark.integration
def test_agent_with_model():
    """Test agent with specific model."""
    agent = Auggie(model="claude-3-5-sonnet-latest")

    assert agent.model == "claude-3-5-sonnet-latest"

    result = agent.run("What is 7 * 8? Return just the number.", return_type=int)

    assert result == 56


# ============================================================================
# Error Handling Tests (Slow)
# ============================================================================


@pytest.mark.integration
def test_empty_instruction_error():
    """Test that empty instruction raises error."""
    agent = Auggie()

    with pytest.raises(ValueError, match="Instruction cannot be empty"):
        agent.run("")

    with pytest.raises(ValueError, match="Instruction cannot be empty"):
        agent.run("   ")


@pytest.mark.integration
def test_invalid_workspace_error():
    """Test that invalid workspace raises error."""
    from auggie_sdk.exceptions import AugmentWorkspaceError

    with pytest.raises(AugmentWorkspaceError):
        Auggie(workspace_root="/nonexistent/path/that/does/not/exist")


# ============================================================================
# Success Criteria Tests
# ============================================================================


@pytest.mark.integration
def test_success_criteria_basic():
    """Test basic success criteria verification (quick sanity check)."""
    agent = Auggie()

    # Simple task with one criterion
    result = agent.run(
        "What is 10 + 5?",
        return_type=int,
        success_criteria=[
            "The answer is correct",
        ],
    )

    assert result == 15


@pytest.mark.integration
def test_success_criteria_multiple():
    """Test success criteria with multiple criteria."""
    agent = Auggie()

    # Task with multiple criteria
    result = agent.run(
        "List three primary colors",
        return_type=list,
        success_criteria=[
            "The list contains exactly 3 items",
            "All items are primary colors (red, blue, yellow)",
            "No duplicate items in the list",
        ],
    )

    assert isinstance(result, list)
    assert len(result) == 3
    # Check no duplicates (case-insensitive)
    result_lower = [str(c).lower() for c in result]
    assert len(result_lower) == len(set(result_lower))


@pytest.mark.integration
def test_success_criteria_with_type_inference():
    """Test success criteria works with type inference."""
    agent = Auggie()

    # Type inference with success criteria
    result = agent.run(
        "How many days are in a week?",
        success_criteria=[
            "The answer is a number",
            "The answer is correct",
        ],
    )

    # Type inference should return an int
    assert isinstance(result, int), f"Expected int, got {type(result).__name__}"
    assert result == 7


@pytest.mark.integration
def test_success_criteria_with_function_calling():
    """Test success criteria works with function calling."""

    def get_temperature(city: str) -> dict:
        """Get temperature for a city (mock)."""
        temps = {
            "San Francisco": 65,
            "New York": 55,
            "Miami": 80,
        }
        return {"city": city, "temperature": temps.get(city, 70), "unit": "F"}

    agent = Auggie()

    result = agent.run(
        "Get the temperature for San Francisco and tell me if it's warm (above 60F)",
        return_type=bool,
        functions=[get_temperature],
        success_criteria=[
            "The get_temperature function was called",
            "The answer is based on the actual temperature returned",
        ],
    )

    assert isinstance(result, bool)
    assert result is True  # 65F is above 60F


@pytest.mark.integration
def test_success_criteria_correction():
    """Test that success criteria triggers corrections when needed."""
    agent = Auggie()

    # This test verifies the agent can self-correct based on criteria
    # We ask for a list but add criteria that might not be initially met
    result = agent.run(
        "List some fruits",
        return_type=list,
        success_criteria=[
            "The list contains at least 3 items",
            "All items are actual fruits (not vegetables)",
            "No duplicate items in the list",
        ],
    )

    assert isinstance(result, list)
    assert len(result) >= 3
    # Check no duplicates
    assert len(result) == len(set(result))


@pytest.mark.integration
def test_success_criteria_with_session():
    """Test success criteria works within a session."""
    agent = Auggie()

    with agent.session() as session:
        # First call with success criteria
        result1 = session.run(
            "What is 5 + 3?",
            return_type=int,
            success_criteria=["The answer is correct"],
        )
        assert result1 == 8

        # Second call in same session with different criteria
        result2 = session.run(
            "What was the previous answer multiplied by 2?",
            return_type=int,
            success_criteria=["The answer uses the previous result"],
        )
        assert result2 == 16
