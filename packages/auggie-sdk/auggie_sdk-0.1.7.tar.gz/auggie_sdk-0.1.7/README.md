# Auggie Python SDK

[![PyPI version](https://badge.fury.io/py/auggie-sdk.svg)](https://badge.fury.io/py/auggie-sdk)
[![Python Versions](https://img.shields.io/pypi/pyversions/auggie-sdk.svg)](https://pypi.org/project/auggie-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python SDK for interacting with the Augment CLI agent (auggie) programmatically. Build AI-powered coding workflows with type-safe responses, function calling, and real-time event streaming.

## What is Augment?

Augment is an AI-powered coding assistant that helps developers write, refactor, and understand code. The Augment Python SDK allows you to programmatically interact with the Augment CLI agent, enabling you to:

- Automate complex coding workflows
- Build custom AI-powered development tools
- Integrate AI assistance into your existing Python applications
- Create structured, type-safe interactions with AI coding agents

## Features

- **Simple API**: Clean, intuitive interface for agent interactions
- **Typed Results**: Get structured data back from the agent with full type safety
- **Type Inference**: Let the agent choose the appropriate type from a list of options
- **Function Calling**: Provide Python functions the agent can call during execution
- **Success Criteria**: Iteratively verify and correct work against quality standards
- **Event Listeners**: Monitor agent activity with AgentListener interface
- **Automatic Retries**: Parsing failures are automatically retried with feedback to the agent
- **Session Management**: Maintain conversation continuity with context managers
- **Model Selection**: Choose which AI model to use
- **Message Access**: Get the agent's reasoning via `agent.last_model_answer`

## Installation

Install from PyPI:

```bash
pip install auggie-sdk
```

### Prerequisites

- Python 3.8 or higher
- Augment CLI (`auggie`) installed and available in PATH
  - Install with: `npm install -g @augmentcode/auggie@prerelease`
- Access to an Augment workspace

### Optional Dependencies

For development and testing:

```bash
# Install with test dependencies
pip install auggie-sdk[test]

# Install with development dependencies
pip install auggie-sdk[dev]
```

For detailed installation instructions, including platform-specific guides and troubleshooting, see [INSTALL.md](https://github.com/augmentcode/auggie-sdk-python/blob/main/INSTALL.md).

## Quick Start

### Basic Usage

```python
from auggie_sdk import Auggie

# Create an agent
agent = Auggie()

# Automatic type inference (agent chooses the best type)
result, inferred_type = agent.run("What is 15 + 27?")
print(f"Answer: {result} (type: {inferred_type.__name__})")  # Answer: 42 (type: int)

# Explicit typed response
result = agent.run("What is 15 + 27?", return_type=int)
print(f"Answer: {result}")  # Answer: 42
```

### Session Management

**By default, each call is independent:**

```python
from auggie_sdk import Auggie

agent = Auggie()

# Each call creates a fresh session
agent.run("Create a function called add_numbers")
agent.run("Test that function")  # ❌ Won't remember add_numbers!
```

**Use session context manager for conversation continuity:**

```python
agent = Auggie()

# Calls within a session share context
with agent.session() as session:
    session.run("Create a function called add_numbers")
    session.run("Test that function")  # ✅ Remembers add_numbers!
    session.run("Add error handling")  # ✅ Still remembers!
```

### Model Selection

```python
# List available models
from auggie_sdk import Auggie

models = Auggie.get_available_models()
for model in models:
    print(f"{model.name} [{model.id}]")
    print(f"  {model.description}")

# Use specific AI model (with type hints)
# Supported models: "haiku4.5", "sonnet4.5", "sonnet4", "gpt5"
agent = Auggie(model="sonnet4.5")

# Or with workspace and model
agent = Auggie(
    workspace_root="/path/to/project",
    model="gpt5"
)

# Type hints are available for IDE autocomplete
from auggie_sdk import ModelType
# ModelType = Literal["haiku4.5", "sonnet4.5", "sonnet4", "gpt5"]
```

### Automatic Type Inference

When you don't specify a `return_type`, the agent automatically infers the best type from common types (int, float, bool, str, list, dict):

```python
# Agent automatically determines the type
result, inferred_type = agent.run("What is 2 + 2?")
print(f"Result: {result}, Type: {inferred_type.__name__}")  # Result: 4, Type: int

result, inferred_type = agent.run("List the primary colors")
print(f"Result: {result}, Type: {inferred_type.__name__}")  # Result: ['red', 'blue', 'yellow'], Type: list

result, inferred_type = agent.run("Is Python statically typed?")
print(f"Result: {result}, Type: {inferred_type.__name__}")  # Result: False, Type: bool
```

### Typed Results

```python
from dataclasses import dataclass
from enum import Enum

@dataclass
class Task:
    title: str
    priority: str
    estimated_hours: int

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Get structured data back with explicit type
task = agent.run("Create a task: 'Fix login bug', high priority, 8 hours", return_type=Task)
print(f"Task: {task.title}, Priority: {task.priority}")

# Works with lists of objects too
tasks = agent.run("Create 3 example tasks", return_type=list[Task])
for task in tasks:
    print(f"- {task.title}")

# Access the agent's reasoning
print(f"Agent's explanation: {agent.last_model_answer}")
```

### Function Calling

Provide Python functions that the agent can call during execution:

```python
def get_weather(location: str, unit: str = "celsius") -> dict:
    """
    Get the current weather for a location.

    Args:
        location: City name or coordinates
        unit: Temperature unit (celsius or fahrenheit)
    """
    # Your implementation here
    return {"temp": 22, "condition": "sunny"}

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates.

    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
    """
    # Your implementation here
    return 100.5

# Agent can call these functions as needed
result = agent.run(
    "What's the weather in San Francisco and how far is it from Los Angeles?",
    return_type=str,
    functions=[get_weather, calculate_distance]
)
```

**Requirements for functions:**
- Must have type hints for parameters
- Should have docstrings with parameter descriptions
- The agent will automatically call them when needed

### Event Listeners

Monitor what the agent is doing with the `AgentListener` interface. The listener receives events from the underlying ACP (Agent Client Protocol) layer, including tool calls, agent messages, and function calls:

```python
from auggie_sdk import Agent, AgentListener, LoggingAgentListener

# Use the built-in logging listener
listener = LoggingAgentListener(verbose=True)
agent = Auggie(listener=listener)

result = agent.run(
    "What's the weather in San Francisco?",
    return_type=dict,
    functions=[get_weather]
)
# Prints: 📞 Calling function: get_weather(location=San Francisco)
#         ✅ Function get_weather returned: {'temp': 72, ...}

# Or create a custom listener
class MyListener(AgentListener):
    def on_function_call(self, function_name: str, arguments: dict) -> None:
        print(f"Agent is calling {function_name}")

    def on_function_result(self, function_name: str, result, error=None) -> None:
        if error:
            print(f"Function failed: {error}")
        else:
            print(f"Function returned: {result}")

agent = Auggie(listener=MyListener())
```

**Available listener methods:**
- `on_agent_message(message)` - Agent sends a message
- `on_function_call(function_name, arguments)` - Agent calls a function
- `on_function_result(function_name, result, error)` - Function returns
- `on_tool_call(tool_call_id, title, kind, status)` - Agent uses a tool (view, edit, etc.)
- `on_tool_response(tool_call_id, status, content)` - Tool responds
- `on_agent_thought(text)` - Agent shares internal reasoning

All methods are optional - only implement the ones you need.

### Automatic Retries for Parsing Failures

When requesting typed results, the agent automatically retries if parsing fails:

```python
# If the agent's response can't be parsed, it will automatically retry
# up to max_retries times (default: 3)
result = agent.run("What is 2 + 2?", return_type=int)

# Customize retry behavior
result = agent.run(
    "Parse this complex data",
    return_type=MyDataClass,
    max_retries=5  # Try up to 5 times
)
```

**How it works:**
1. Agent sends the instruction
2. If parsing fails, agent is told about the error and asked to fix the output
3. This continues until success or max_retries is exhausted
4. The retry happens in the same session, so the agent has full context

### Success Criteria

Ensure the agent iteratively verifies and corrects its work against quality standards:

```python
# Agent will iteratively work and verify until all criteria are met
agent.run(
    "Create a Python function to calculate fibonacci numbers",
    success_criteria=[
        "Function has type hints for all parameters and return value",
        "Function has a comprehensive docstring with examples",
        "Function handles edge cases (n=0, n=1, negative numbers)",
        "Code follows PEP 8 style guidelines",
    ],
    max_verification_rounds=3  # Optional: control max iterations (default: 3)
)
```

**How it works (iterative loop):**
1. Agent works on the task
2. Agent verifies all success criteria
3. If all criteria met → Done! ✅
4. If not all met → Agent receives specific feedback about what's wrong
5. Agent fixes the identified issues
6. Go back to step 2
7. Repeat until all criteria met or max_verification_rounds reached

**Benefits:**
- Ensures quality standards are automatically met
- Agent receives **structured feedback** on what needs fixing
- Iterative improvement - agent can make multiple passes
- Reduces need for manual review
- Works great for code generation, documentation, and refactoring tasks

**Exception handling:**
If criteria are not met after `max_verification_rounds`, an `AugmentVerificationError` is raised with details about unmet criteria and specific issues.

**See also:** [Success Criteria Documentation](docs/SUCCESS_CRITERIA_LOOP.md) for detailed examples and best practices.

## Supported Types

**Automatic type inference** (when no `return_type` specified):
- `int`, `float`, `bool`, `str`, `list`, `dict`

**Explicit types** (when `return_type` is specified):
- **Built-in types**: `int`, `float`, `str`, `bool`, `list`, `dict`
- **Dataclasses**: Any Python dataclass
- **Enums**: Python enums
- **Generic types**: `list[SomeClass]`, `list[int]`, etc.

## API Reference

### Agent Class

```python
class Agent:
    def __init__(
        self,
        workspace_root: Optional[Union[str, Path]] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize an agent instance.

        Args:
            workspace_root: Path to workspace root (defaults to current directory)
            model: AI model to use (e.g., "claude-3-5-sonnet-latest")
        """

    def run(
        self,
        instruction: str,
        return_type: Type[T] = None,
        timeout: Optional[int] = None,
        max_retries: int = 3,
    ) -> Union[T, tuple[T, Type[T]]]:
        """
        Execute an instruction and return response.

        If return_type is None, automatically infers the type and returns (result, type).
        If return_type is specified, returns the parsed result of that type.
        """

    def session(self, session_id: Optional[str] = None) -> Agent:
        """Create a session context for conversation continuity."""
```

### Session Usage Patterns

```python
# Single task with multiple related steps
with agent.session() as session:
    session.run("Create the main function")
    session.run("Add error handling")
    session.run("Write comprehensive tests")

# Continue the same task automatically
with agent.session() as session:  # Resumes last session
    session.run("Add more features to the function")

# Work on different concerns with explicit session IDs
with agent.session("backend-work") as backend:
    backend.run("Create API endpoints")

with agent.session("frontend-work") as frontend:
    frontend.run("Create React components")

# Return to backend work
with agent.session("backend-work") as backend:
    backend.run("Add authentication to the API")
```

## Testing with Mock Clients

For testing purposes, you can provide your own ACPClient implementation to the Agent:

```python
from auggie_sdk import Auggie
from auggie_sdk.acp import ACPClient

class MockACPClient(ACPClient):
    """A mock client for testing."""

    def __init__(self):
        self._running = False

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def send_message(self, message: str, timeout: float = 30.0) -> str:
        # Return mock responses for testing
        return "Mock response"

    def clear_context(self) -> None:
        pass

    @property
    def is_running(self) -> bool:
        return self._running

# Use the mock client in tests
mock_client = MockACPClient()
agent = Auggie(acp_client=mock_client)

# Now agent.run() will use your mock client
response = agent.run("Test instruction")
```

This is useful for:
- Unit testing code that uses the Agent without calling the real CLI
- Controlling responses for predictable testing
- Faster test execution
- Testing without authentication or network access

## Prompt to Code Converter

Convert complex prompts into structured SDK programs with the `prompt_to_code.py` tool:

```bash
# Convert a prompt file to an SDK program
python prompt_to_code.py my_prompt.txt

# With custom output file
python prompt_to_code.py my_prompt.txt --output my_workflow.py

# With custom model
python prompt_to_code.py my_prompt.txt --model claude-3-5-sonnet-latest
```

**Why convert prompts to SDK programs?**
- ✅ Better control over workflow execution
- ✅ Type safety with Python's type system
- ✅ Debugging capabilities with standard Python tools
- ✅ Reusability - run the same workflow multiple times
- ✅ Maintainability - easier to modify and extend

**Example:** Given a prompt like:
```
Analyze all Python files in src/, identify security issues,
create a report, and generate fixes for critical issues.
```

The tool generates a complete Python program with:
- Proper imports and dataclasses
- Session management for context
- Typed results for decision-making
- Loops for iteration
- Error handling

See [`docs/PROMPT_TO_CODE.md`](docs/PROMPT_TO_CODE.md) for detailed documentation.

## Examples

See the `examples/` directory for more usage examples:
- `examples/basic_usage.py` - Basic agent usage
- `examples/session_usage.py` - Session management examples
- `examples/list_prs.py` - Working with GitHub PRs
- `examples/list_models.py` - List available AI models
- `examples/mock_client_example.py` - Using a mock ACP client for testing
- `examples/event_listener_demo.py` - Interactive demo of event listeners
- `examples/example_prompt.txt` - Example prompt for the prompt-to-code converter

## Event Listeners

The SDK supports real-time event listeners to observe what the agent is doing:

```python
from auggie_sdk import Auggie
from auggie_sdk.acp import AgentEventListener

class MyListener(AgentEventListener):
    def on_agent_message_chunk(self, text: str) -> None:
        """Called when agent sends response chunks (streaming)."""
        print(f"{text}", end="", flush=True)

    def on_agent_message(self, message: str) -> None:
        """Called when agent finishes sending complete message."""
        print(f"\n[Complete: {len(message)} chars]")

    def on_tool_call(self, tool_call_id, title, kind=None, status=None):
        """Called when agent makes a tool call (read file, edit, etc.)."""
        print(f"\n🔧 Using tool: {title}")

    def on_tool_response(self, tool_call_id, status=None, content=None):
        """Called when tool responds."""
        if status == "completed":
            print("✅ Done!")

    def on_agent_thought(self, text: str) -> None:
        """Called when agent shares its reasoning."""
        print(f"💭 Thinking: {text}")

# Use the listener
listener = MyListener()
agent = Auggie(listener=listener)
response = agent.run("Read the README and summarize it")
```

**For detailed explanation of all events, see:** [`docs/AGENT_EVENT_LISTENER.md`](docs/AGENT_EVENT_LISTENER.md)

## API Reference

### Agent.get_available_models()

Get the list of available AI models for your account.

```python
from auggie_sdk import Agent, Model

models = Agent.get_available_models()
# Returns: List[Model]

# Each Model has:
# - id: str          # Model identifier (e.g., "sonnet4.5")
# - name: str        # Human-readable name (e.g., "Claude Sonnet 4.5")
# - description: str # Additional info (e.g., "Anthropic Claude Sonnet 4.5, 200k context")
```

**Example:**
```python
models = Agent.get_available_models()
for model in models:
    print(f"{model.name} [{model.id}]")
    if model.description:
        print(f"  {model.description}")
```

## Error Handling

```python
from auggie_sdk.exceptions import AugmentCLIError, AugmentParseError

try:
    result = agent.run("What is the color blue?", return_type=int)
except AugmentParseError as e:
    print(f"Could not parse as int: {e}")
except AugmentCLIError as e:
    print(f"CLI error: {e}")
```

## Key Features

### Session Management

The Agent class uses the ACP (Agent Client Protocol) client internally for better performance. By default, each `run()` call creates a fresh session. Use the `session()` context manager to maintain conversation continuity:

```python
from auggie_sdk import Auggie

agent = Auggie()

# Use session context for conversation continuity
with agent.session() as session:
    session.run("Create a function")
    session.run("Test it")  # Remembers the function!
    session.run("Optimize it")  # Still remembers!
```

### Real-Time Streaming (Optional)

You can optionally provide an event listener to receive real-time updates:

```python
from auggie_sdk import Auggie
from auggie_sdk.acp import AgentEventListener

class MyListener(AgentEventListener):
    def on_agent_message_chunk(self, text: str):
        print(text, end="", flush=True)

agent = Auggie(listener=MyListener())
agent.run("Create a hello world function")  # See real-time output!
```

## Testing

The SDK includes fast unit tests, quick e2e sanity checks, and comprehensive slow tests.

### Running Tests

**Run fast tests + quick sanity checks (default):**
```bash
pytest
```

This runs:
- All unit tests (tests in `tests/` directory) which use mocks - complete in milliseconds
- Quick e2e sanity checks (3 tests: start/stop, simple math query, context manager) - complete in a few seconds

Total time: ~5-10 seconds

**Run all tests including slow ones:**
```bash
pytest -m ""
```

This runs all 50 tests including slow integration/e2e tests that make extensive real calls to the auggie CLI. These tests can take several minutes.

**Run only slow tests:**
```bash
pytest -m slow
```

**Run with verbose output:**
```bash
pytest -v
```

### Test Organization

**Fast unit tests (always run):**
- `tests/test_agent.py` - Unit tests for Agent class (uses mocks)
- `tests/test_exceptions.py` - Exception handling tests
- `tests/test_utils.py` - Utility function tests (uses mocks)

**Quick e2e sanity checks (always run):**
- `augment/acp/test_client_e2e.py::test_start_and_stop` - Basic client lifecycle
- `augment/acp/test_client_e2e.py::test_simple_math_query` - Single simple query
- `augment/acp/test_client_e2e.py::test_context_manager` - Context manager usage

**Slow comprehensive tests (marked with @pytest.mark.slow):**
- `test_sdk.py` - Integration tests for basic SDK functionality
- `test_e2e_session.py` - End-to-end session management tests
- `augment/acp/test_client_e2e.py` - Most ACP client integration tests

## ACP Client (Advanced)

The SDK includes ACP (Agent Client Protocol) clients for more advanced use cases. ACP clients maintain a long-running connection to agents, providing better performance and real-time streaming of responses.

**Key Difference:** Unlike the `Agent` class which spawns a new process per request, ACP clients maintain a **single persistent session**. All messages sent to the client automatically share context - no need for explicit session management!

### Available ACP Clients

1. **`AuggieACPClient`** - For Augment CLI (default)
2. **`ClaudeCodeACPClient`** - For Claude Code via Anthropic's API

### Augment CLI (AuggieACPClient)

```python
from auggie_sdk.acp import AuggieACPClient

# Create client with model and workspace configuration
client = AuggieACPClient(
    model="claude-3-5-sonnet-latest",
    workspace_root="/path/to/workspace"
)

# Start the agent (creates a persistent session)
client.start()

# Send messages - they all share the same session context!
response1 = client.send_message("Create a function called add_numbers")
print(response1)

response2 = client.send_message("Now test that function")  # Remembers add_numbers!
print(response2)

# Stop the agent
client.stop()
```

### Claude Code (ClaudeCodeACPClient)

Use Claude Code directly via Anthropic's API:

```python
from auggie_sdk.acp import ClaudeCodeACPClient

# Requires: npm install -g @zed-industries/claude-code-acp
# And: export ANTHROPIC_API_KEY=...

client = ClaudeCodeACPClient(
    model="claude-3-5-sonnet-latest",
    workspace_root="/path/to/workspace"
)

client.start()
response = client.send_message("Write a Python function to calculate fibonacci")
print(response)
client.stop()
```

See [Claude Code Client Documentation](docs/CLAUDE_CODE_CLIENT.md) for details.

### ACP with Context Manager

```python
from auggie_sdk.acp import AuggieACPClient

# Automatically starts and stops
with AuggieACPClient(model="claude-3-5-sonnet-latest") as client:
    response = client.send_message("What is 2 + 2?")
    print(response)
```

### ACP with Event Listener

```python
from auggie_sdk.acp import AuggieACPClient, AgentEventListener

class MyListener(AgentEventListener):
    def on_agent_message_chunk(self, text: str):
        print(f"Agent: {text}", end="", flush=True)

    def on_tool_call(self, tool_name: str, tool_input: dict):
        print(f"\n[Tool: {tool_name}]")

client = AuggieACPClient(
    model="claude-3-5-sonnet-latest",
    listener=MyListener()
)
client.start()
response = client.send_message("Create a hello world function")
client.stop()
```

### ACP Client Parameters

- `cli_path`: Path to the Augment CLI (optional, auto-detected)
- `listener`: Event listener for real-time updates (optional)
- `model`: AI model to use (e.g., "claude-3-5-sonnet-latest", "gpt-4o")
- `workspace_root`: Workspace root directory (optional, defaults to current directory)

### Agent vs ACP Client Comparison

**When to use `Agent` (subprocess-based):**
- Simple one-off requests
- Don't need real-time streaming
- Want explicit session control

**When to use `AuggieACPClient` (long-running):**
- Multiple related requests
- Want automatic session continuity
- Need real-time streaming and events
- Better performance (no subprocess overhead)

```python
# Agent - each call is independent by default
agent = Auggie()
agent.run("Create a function")
agent.run("Test it")  # ❌ Doesn't remember the function

# Agent - need explicit session for context
with agent.session() as session:
    session.run("Create a function")
    session.run("Test it")  # ✅ Remembers the function

# ACP Client - automatic session continuity
client = AuggieACPClient()
client.start()
client.send_message("Create a function")
client.send_message("Test it")  # ✅ Automatically remembers!
client.stop()
```

See `augment/acp/example_usage.py` for more examples.

## Requirements

- Python 3.8 or higher
- Augment CLI (`auggie`) installed and available in PATH
  - Install with: `npm install -g @augmentcode/auggie@prerelease`
- Access to an Augment workspace

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

- **Documentation**: [https://docs.augmentcode.com](https://docs.augmentcode.com)
- **GitHub Issues**: [https://github.com/augmentcode/auggie-sdk-python/issues](https://github.com/augmentcode/auggie-sdk-python/issues)
- **Website**: [https://augmentcode.com](https://augmentcode.com)

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- **PyPI**: [https://pypi.org/project/auggie-sdk/](https://pypi.org/project/auggie-sdk/)
- **GitHub**: [https://github.com/augmentcode/auggie-sdk-python](https://github.com/augmentcode/auggie-sdk-python)
- **Documentation**: [https://docs.augmentcode.com](https://docs.augmentcode.com)
