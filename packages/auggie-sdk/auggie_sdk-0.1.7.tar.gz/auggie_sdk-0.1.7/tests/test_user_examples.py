"""
Integration tests for user examples from user_examples/user_guide.md.

These tests run the actual example scripts to ensure they work correctly.
They are marked as integration tests (require auggie CLI) and skipped by default.

To run these tests: pytest -m integration
Or use tox: tox -e integration
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
USER_EXAMPLES_DIR = PROJECT_ROOT / "user_examples"


def run_example(script_name: str, timeout: int = 60) -> tuple[int, str, str]:
    """
    Run a user example script and return the result.

    Args:
        script_name: Name of the script file (e.g., "01_quick_start.py")
        timeout: Timeout in seconds

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    script_path = USER_EXAMPLES_DIR / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"Example script not found: {script_path}")

    # Set PYTHONPATH to use local version of the SDK
    import os

    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )

    return result.returncode, result.stdout, result.stderr


# ============================================================================
# User Example Tests (Slow Integration Tests)
# ============================================================================


@pytest.mark.integration
def test_01_quick_start():
    """Test the quick start example."""
    returncode, stdout, stderr = run_example("01_quick_start.py")

    assert returncode == 0, f"Script failed with stderr: {stderr}"
    # The example asks "What is the capital of France?"
    # We expect "Paris" somewhere in the output
    assert (
        "Paris" in stdout or "paris" in stdout.lower()
    ), f"Expected 'Paris' in output, got: {stdout}"


@pytest.mark.integration
def test_02_event_listener_builtin():
    """Test the built-in event listener example."""
    returncode, stdout, stderr = run_example("02_event_listener_builtin.py")

    assert returncode == 0, f"Script failed with stderr: {stderr}"
    # The example uses LoggingAgentListener which prints agent messages
    # We expect to see the result "4" (from 2+2)
    assert "4" in stdout, f"Expected '4' in output, got: {stdout}"


@pytest.mark.integration
def test_03_event_listener_custom():
    """Test the custom event listener example."""
    returncode, stdout, stderr = run_example("03_event_listener_custom.py")

    assert returncode == 0, f"Script failed with stderr: {stderr}"
    # The example uses a custom listener that prints "[Agent Message]"
    assert (
        "[Agent Message]" in stdout
    ), f"Expected '[Agent Message]' in output, got: {stdout}"
    # The example asks "What is 5 * 5?"
    assert "25" in stdout, f"Expected '25' in output, got: {stdout}"


@pytest.mark.integration
def test_04_session_management():
    """Test the session management example."""
    returncode, stdout, stderr = run_example("04_session_management.py")

    assert returncode == 0, f"Script failed with stderr: {stderr}"
    # The example demonstrates session memory by asking about favorite color
    # We expect to see "blue" in the output when using session
    assert "blue" in stdout.lower(), f"Expected 'blue' in output, got: {stdout}"


@pytest.mark.integration
def test_05_type_inference():
    """Test the type inference example."""
    returncode, stdout, stderr = run_example("05_type_inference.py")

    assert returncode == 0, f"Script failed with stderr: {stderr}"
    # The example demonstrates type inference with int and list results
    assert (
        "4" in stdout or "int" in stdout
    ), f"Expected '4' or 'int' in output, got: {stdout}"


@pytest.mark.integration
def test_06_typed_returns():
    """Test the typed returns example.

    The SDK now includes schema information in retry prompts, which helps the LLM
    use the correct field names when parsing fails on the first attempt.
    """
    returncode, stdout, stderr = run_example("06_typed_returns.py", timeout=90)

    assert returncode == 0, f"Script failed with stderr: {stderr}"
    # The example creates a Task dataclass and prints task information
    assert len(stdout) > 0, f"Expected some output, got: {stdout}"


@pytest.mark.integration
def test_07_success_criteria():
    """Test the success criteria example."""
    returncode, stdout, stderr = run_example("07_success_criteria.py", timeout=90)

    assert returncode == 0, f"Script failed with stderr: {stderr}"
    # The example generates a fibonacci function
    assert (
        "fibonacci" in stdout.lower() or "def" in stdout
    ), f"Expected function definition in output, got: {stdout}"


@pytest.mark.integration
def test_08_function_tools():
    """Test the function tools example."""
    returncode, stdout, stderr = run_example("08_function_tools.py")

    assert returncode == 0, f"Script failed with stderr: {stderr}"
    # The example uses custom functions for time and weather
    # We expect to see time and weather information in the output
    assert (
        "time" in stdout.lower() or "weather" in stdout.lower()
    ), f"Expected time/weather info in output, got: {stdout}"
