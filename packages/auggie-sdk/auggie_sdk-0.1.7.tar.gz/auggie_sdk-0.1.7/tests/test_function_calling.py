"""
Test function calling feature of the Agent SDK.
"""

import pytest
from auggie_sdk import Auggie


def test_function_schema_generation():
    """Test that function schemas are generated correctly."""
    from auggie_sdk.function_tools import function_to_schema

    def get_weather(location: str, unit: str = "celsius") -> dict:
        """Get weather for a location.

        Args:
            location: City name or coordinates
            unit: Temperature unit (celsius or fahrenheit)
        """
        pass

    schema = function_to_schema(get_weather)

    assert schema["name"] == "get_weather"
    assert "Get weather for a location" in schema["description"]
    assert "location" in schema["parameters"]["properties"]
    assert "unit" in schema["parameters"]["properties"]
    assert "location" in schema["parameters"]["required"]
    assert "unit" not in schema["parameters"]["required"]  # Has default value


@pytest.mark.integration
def test_function_calling_basic():
    """Test basic function calling with a simple function."""

    # Define a simple function
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together.

        Args:
            a: First number
            b: Second number
        """
        return a + b

    agent = Auggie()

    # Test with function calling
    result = agent.run(
        "What is 15 + 27? Use the add_numbers function.",
        return_type=int,
        functions=[add_numbers],
    )

    assert result == 42


@pytest.mark.integration
def test_function_calling_with_dict_return():
    """Test function calling with a function that returns a dict."""

    def get_user_info(user_id: int) -> dict:
        """Get user information.

        Args:
            user_id: The user ID to look up
        """
        return {"id": user_id, "name": "Test User", "email": "test@example.com"}

    agent = Auggie()

    result = agent.run(
        "Get information for user ID 123 using the get_user_info function",
        return_type=dict,
        functions=[get_user_info],
    )

    assert isinstance(result, dict)
    # The agent may return the dict with "id" or "user_id" key depending on how it formats the response
    assert result.get("id") == 123 or result.get("user_id") == 123
    assert result.get("name") == "Test User"
    assert result.get("email") == "test@example.com"


@pytest.mark.integration
def test_multiple_functions():
    """Test providing multiple functions to the agent."""

    def multiply(a: int, b: int) -> int:
        """Multiply two numbers.

        Args:
            a: First number
            b: Second number
        """
        return a * b

    def divide(a: int, b: int) -> float:
        """Divide two numbers.

        Args:
            a: Numerator
            b: Denominator
        """
        return a / b

    agent = Auggie()

    result = agent.run(
        "Calculate (10 * 5) / 2 using the multiply and divide functions",
        return_type=float,
        functions=[multiply, divide],
    )

    assert result == 25.0


@pytest.mark.integration
def test_function_with_optional_params():
    """Test function with optional parameters."""

    def format_name(first: str, last: str, middle: str = None) -> str:
        """Format a person's name.

        Args:
            first: First name
            last: Last name
            middle: Middle name (optional)
        """
        if middle:
            return f"{first} {middle} {last}"
        return f"{first} {last}"

    agent = Auggie()

    result = agent.run(
        "Format the name John Doe using the format_name function",
        return_type=str,
        functions=[format_name],
    )

    assert "John" in result
    assert "Doe" in result


@pytest.mark.integration
def test_function_error_handling():
    """Test that function errors are handled gracefully."""

    def failing_function(x: int) -> int:
        """A function that always fails.

        Args:
            x: Input number
        """
        raise ValueError("This function always fails")

    agent = Auggie()

    # The agent should handle the error and still return a response
    result = agent.run(
        "Try to call failing_function with x=5",
        return_type=str,
        functions=[failing_function],
    )

    # Should get some response even if function failed
    assert isinstance(result, str)


if __name__ == "__main__":
    # Run a simple manual test
    print("Testing function calling...")

    def get_current_time() -> str:
        """Get the current time."""
        from datetime import datetime

        return datetime.now().strftime("%H:%M:%S")

    agent = Auggie()
    result = agent.run(
        "What time is it? Use the get_current_time function.",
        return_type=str,
        functions=[get_current_time],
    )

    print(f"Result: {result}")
    print("Test completed!")
