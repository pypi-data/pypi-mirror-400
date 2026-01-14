"""
Main Agent class for the Augment Python SDK.

This implementation uses the ACP (Agent Client Protocol) client for
better performance and real-time streaming.
"""

import json
import os
import re
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from .acp import ACPClient, AuggieACPClient
from .exceptions import (
    AugmentCLIError,
    AugmentNotFoundError,
    AugmentParseError,
    AugmentWorkspaceError,
    AugmentVerificationError,
)
from .listener import AgentListener
from .listener_adapter import AgentListenerAdapter
from .prompt_formatter import AgentPromptFormatter, DEFAULT_INFERENCE_TYPES

T = TypeVar("T")

# Type alias for supported AI models (matching TypeScript SDK)
ModelType = Literal["haiku4.5", "sonnet4.5", "sonnet4", "gpt5"]


@dataclass
class VerificationResult:
    """Result of verifying success criteria."""

    all_criteria_met: bool
    unmet_criteria: List[int]  # Indices of criteria that are not met (1-based)
    issues: List[str]  # Description of each issue found
    overall_assessment: str  # Brief overall assessment


def _get_type_name(type_hint: Any) -> str:
    """
    Safely get the name of a type hint.

    Handles both actual types and string annotations.

    Args:
        type_hint: A type or type annotation

    Returns:
        String name of the type
    """
    if isinstance(type_hint, str):
        return type_hint
    if hasattr(type_hint, "__name__"):
        return type_hint.__name__
    return str(type_hint)


@dataclass
class Model:
    """
    Represents an available AI model.

    Attributes:
        id: The model identifier used with --model flag (e.g., "sonnet4.5")
        name: The human-readable model name (e.g., "Claude Sonnet 4.5")
        description: Additional information about the model (e.g., "Anthropic Claude Sonnet 4.5, 200k context")
    """

    id: str
    name: str
    description: str

    def __str__(self) -> str:
        return f"{self.name} [{self.id}]"


class Auggie:
    """
    Augment CLI agent interface for programmatic access.

    This class provides a Python interface to the Augment CLI agent (auggie),
    using the ACP (Agent Client Protocol) for better performance and
    real-time streaming of responses.

    By default, each run() call creates a fresh session. Use the session()
    context manager to maintain conversation continuity across multiple calls.

    Attributes:
        last_model_answer: The last textual explanation returned by the model
            when using typed results. This contains the agent's reasoning or
            context and may be helpful for logging and debugging. None for
            untyped responses or if no message was provided.
        model: The AI model to use. Options: "haiku4.5", "sonnet4.5", "sonnet4", "gpt5".
               None uses the CLI's default model.
        workspace_path: The resolved workspace path for this agent.
        session_id: The current session ID (only set when inside a session context).
        timeout: Default timeout in seconds for agent operations (defaults to 180 seconds).
    """

    def __init__(
        self,
        workspace_root: Optional[Union[str, Path]] = None,
        model: Optional[ModelType] = None,
        listener: Optional[AgentListener] = None,
        cli_path: Optional[str] = None,
        acp_client: Optional[ACPClient] = None,
        removed_tools: Optional[List[str]] = None,
        timeout: int = 180,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        rules: Optional[List[str]] = None,
        cli_args: Optional[List[str]] = None,
    ):
        """
        Initialize an agent instance.

        Args:
            workspace_root: Path to the workspace root. Defaults to current directory.
            model: The AI model to use. Options: "haiku4.5", "sonnet4.5", "sonnet4", "gpt5".
                   Defaults to the CLI's default model.
            listener: Optional listener for agent events (AgentListener).
            cli_path: Optional path to the Augment CLI. Auto-detected if not provided.
            acp_client: Optional ACP client instance for testing. If provided, this client
                       will be used instead of creating a new one. This is primarily for
                       testing purposes to allow mocking the ACP client.
            removed_tools: List of tool names to remove/disable (e.g., ["github-api", "linear"]).
                          These tools will not be available to the agent.
            timeout: Default timeout in seconds for agent operations. Defaults to 180 seconds (3 minutes).
                    This timeout is used when no timeout is specified in the run() method.
            api_key: Optional API key for authentication. If provided, sets AUGMENT_API_TOKEN
                    environment variable for the agent process.
            api_url: Optional API URL. If not provided, uses AUGMENT_API_URL environment variable,
                    or defaults to "https://api.augmentcode.com". Sets AUGMENT_API_URL environment
                    variable for the agent process.
            rules: Optional list of rule file paths. Each file path will be passed to the auggie
                  command using the --rules flag. Files are validated to exist before the agent starts.
            cli_args: Optional list of additional command-line arguments to pass to the CLI.
                     These arguments are appended after all other CLI arguments (e.g.,
                     ["--verbose", "--debug"]). Use this for passing custom or experimental
                     CLI flags that aren't exposed as dedicated parameters.
        """
        self.workspace_path = self._validate_workspace_path(workspace_root)
        self.model = model
        self.listener = listener
        # Create adapter to bridge ACP events to AgentListener
        self._listener_adapter = AgentListenerAdapter(listener) if listener else None
        self.cli_path = cli_path
        self.removed_tools = removed_tools or []
        self.timeout = timeout
        self.api_key = api_key
        self.api_url = (
            api_url
            if api_url is not None
            else os.getenv("AUGMENT_API_URL", "https://api.augmentcode.com")
        )
        self.rules = self._validate_rules(rules) if rules else []
        self.cli_args = cli_args or []
        self.last_model_answer: Optional[str] = None
        self._acp_client: Optional[ACPClient] = (
            acp_client  # Use provided client or None
        )
        self._provided_client = acp_client is not None  # Track if client was provided
        self._in_session = False  # Track if we're in a session context
        self._prompt_formatter = AgentPromptFormatter()  # Handles prompt formatting

    def run(
        self,
        instruction: str,
        return_type: Optional[Type[T]] = None,
        timeout: Optional[int] = None,
        max_retries: int = 3,
        functions: Optional[List[Callable]] = None,
        success_criteria: Optional[List[str]] = None,
        max_verification_rounds: int = 3,
    ) -> Union[T, Any]:
        """
        Execute an instruction and return the agent's response.

        If a typed response is requested and parsing fails, the agent will be asked
        to correct its output up to max_retries times.

        When no return_type is specified, the agent automatically infers the best type
        from common types (int, float, bool, str, list, dict) and returns the result.

        Args:
            instruction: The instruction to send to the agent
            return_type: Expected return type (int, str, bool, float, list, dict, dataclass, or enum).
                        If None, the agent will automatically infer the type.
            timeout: Optional timeout in seconds
            max_retries: Maximum number of retry attempts for parsing failures (default: 3)
            functions: Optional list of Python functions the agent can call. Functions should
                      have type hints and docstrings describing their parameters.
            success_criteria: Optional list of criteria that must be met after execution.
                            The agent will iteratively work on the task and verify criteria
                            until all are met or max_verification_rounds is reached.
            max_verification_rounds: Maximum number of verification rounds when using
                                   success_criteria (default: 3). Each round consists of
                                   executing/fixing the task and verifying criteria.

        Returns:
            Parsed result (either of requested type, or inferred type)

        Note:
            After execution, self.last_model_answer contains the agent's textual explanation,
            which may be helpful for logging and debugging. This is separate from the
            structured return value and provides the model's reasoning or context.

        Raises:
            ValueError: If instruction is empty or whitespace, or unsupported return_type
            AugmentParseError: If parsing typed response fails after all retries
            AugmentVerificationError: If success_criteria are not met after max_verification_rounds
        """
        # Validate instruction
        if not instruction or not instruction.strip():
            raise ValueError("Instruction cannot be empty or whitespace")

        # Prepare the client
        client = self._prepare_client()

        # If no success criteria, just run the task once
        if not success_criteria:
            return self._run_task(
                client=client,
                instruction=instruction,
                return_type=return_type,
                timeout=timeout,
                max_retries=max_retries,
                functions=functions,
            )

        # With success criteria: loop until verified or max rounds
        current_instruction = instruction

        for round_num in range(max_verification_rounds):
            # Execute the task (or fix issues from previous round)
            result = self._run_task(
                client=client,
                instruction=current_instruction,
                return_type=return_type,
                timeout=timeout,
                max_retries=max_retries,
                functions=functions,
            )

            # Verify success criteria
            verification = self._verify_success_criteria(
                client=client,
                success_criteria=success_criteria,
                timeout=timeout,
            )

            # Check if all criteria are met
            if verification.all_criteria_met:
                # Success! All criteria verified
                return result

            # Not all criteria met - prepare fix instruction for next round
            if round_num < max_verification_rounds - 1:
                # We have more rounds - prepare fix instruction
                current_instruction = self._prepare_fix_instruction(
                    success_criteria=success_criteria,
                    verification=verification,
                )
            else:
                # Last round - raise exception
                raise AugmentVerificationError(
                    f"Success criteria not fully met after {max_verification_rounds} rounds. "
                    f"Unmet criteria: {verification.unmet_criteria}. "
                    f"Issues: {verification.issues}",
                    unmet_criteria=verification.unmet_criteria,
                    issues=verification.issues,
                    rounds_attempted=max_verification_rounds,
                )

        # This should never be reached, but just in case
        return None

    def _prepare_client(self) -> ACPClient:
        """
        Prepare the ACP client for execution.

        This method:
        1. Creates the client if it doesn't exist
        2. Starts the client if it's not running
        3. Clears context if not in a session (for fresh start)

        Returns:
            ACP client instance ready for use
        """
        # Create client if needed
        if self._acp_client is None:
            self._acp_client = AuggieACPClient(
                cli_path=self.cli_path,
                model=self.model,
                workspace_root=str(self.workspace_path),
                listener=self._listener_adapter,  # Pass the adapter to ACP
                removed_tools=self.removed_tools,
                api_key=self.api_key,
                api_url=self.api_url,
                rules=self.rules,
                cli_args=self.cli_args,
            )

        # Start if not running
        if not self._acp_client.is_running:
            self._acp_client.start()

        # If not in a session, clear context for a fresh start
        if not self._in_session:
            self._acp_client.clear_context()

        return self._acp_client

    def _run_task(
        self,
        client: ACPClient,
        instruction: str,
        return_type: Optional[Type[T]],
        timeout: Optional[int],
        max_retries: int,
        functions: Optional[List[Callable]] = None,
    ) -> Union[T, Any]:
        """
        Run a single task: talk to the agent in a loop until the task is complete.

        This method implements a loop that:
        1. Sends the current instruction to the agent
        2. If response contains function calls, executes them and continues
        3. If response can be parsed successfully, returns the result
        4. If parsing fails and retries remain, asks agent to fix output and continues
        5. Repeats until success or max rounds exhausted

        Args:
            client: The ACP client to use
            instruction: The instruction to send
            return_type: Expected return type (None for type inference)
            timeout: Timeout in seconds (None for default)
            max_retries: Maximum number of retry attempts for parsing failures
            functions: Optional list of functions the agent can call

        Returns:
            Parsed result (either of requested type, or inferred type)

        Raises:
            AugmentParseError: If parsing fails after all retries
        """
        # Set effective timeout - use provided timeout, or fall back to instance default
        effective_timeout = (
            float(timeout) if timeout is not None else float(self.timeout)
        )

        # Prepare the instruction prompt
        current_instruction, function_map = (
            self._prompt_formatter.prepare_instruction_prompt(
                instruction, return_type, functions
            )
        )

        # Determine if we're in type inference mode
        infer_type = return_type is None

        # Track retry attempts for parsing failures
        parse_retry_count = 0

        # Maximum total rounds to prevent infinite loops
        # This includes both function calls and parse retries
        max_rounds = 20

        for round_num in range(max_rounds):
            # Send message to agent
            raw_response = client.send_message(current_instruction, effective_timeout)

            # Check if there are function calls to handle
            if function_map:
                function_calls = self._parse_function_calls(raw_response)
                if function_calls:
                    # Execute functions and prepare next instruction with results
                    current_instruction = self._handle_function_calls(
                        raw_response, function_map
                    )
                    # Continue loop to send function results back to agent
                    continue

            # No function calls - try to parse the response
            try:
                if infer_type:
                    result, _ = self._parse_type_inference_response(
                        raw_response, DEFAULT_INFERENCE_TYPES
                    )
                    return result
                else:
                    # At this point, return_type must be a valid type (not None)
                    assert return_type is not None
                    result = self._parse_typed_response(raw_response, return_type)
                    return result  # type: ignore[return-value,no-any-return]

            except AugmentParseError as e:
                # Parsing failed - check if we have retries left
                if parse_retry_count >= max_retries:
                    raise

                # Increment retry count and prepare retry instruction
                parse_retry_count += 1
                current_instruction = self._prompt_formatter.prepare_retry_prompt(
                    return_type,
                    str(e),
                    parse_retry_count,
                )
                # Continue loop to retry with corrected instruction
                continue

        # If we've exhausted all rounds, raise an error
        raise AugmentParseError(
            f"Exceeded maximum rounds ({max_rounds}) without successful completion"
        )

    def _verify_success_criteria(
        self,
        client: ACPClient,
        success_criteria: List[str],
        timeout: Optional[int],
    ) -> VerificationResult:
        """
        Verify that success criteria are met and return structured feedback.

        This method checks each criterion and returns detailed information about
        which criteria are met and which are not, along with specific issues.

        Args:
            client: The ACP client to use
            success_criteria: List of criteria that must be met
            timeout: Timeout in seconds (None for default)

        Returns:
            VerificationResult with detailed verification feedback
        """
        # Build verification instruction
        criteria_list = "\n".join(
            f"{i + 1}. {criterion}" for i, criterion in enumerate(success_criteria)
        )

        verification_instruction = f"""The task has been completed. Please verify that ALL of the following success criteria are met:

{criteria_list}

For each criterion, check if it is satisfied.

Respond with a JSON object with the following structure:
{{
    "all_criteria_met": true/false,
    "unmet_criteria": [list of criterion numbers (1-based) that are NOT met],
    "issues": ["description of each issue found"],
    "overall_assessment": "brief assessment of the current state"
}}

Example:
{{
    "all_criteria_met": false,
    "unmet_criteria": [2, 3],
    "issues": ["Criterion 2: Function is missing type hints for parameter 'x'", "Criterion 3: No docstring present"],
    "overall_assessment": "Function exists but lacks type hints and documentation"
}}"""

        # Run verification and get structured result
        try:
            verification = self._run_task(
                client=client,
                instruction=verification_instruction,
                return_type=VerificationResult,
                timeout=timeout,
                max_retries=2,
                functions=None,
            )
            return verification

        except (AugmentParseError, Exception) as e:
            # If verification fails, return a conservative result
            import warnings

            warnings.warn(
                f"Success criteria verification failed: {e}. "
                "Assuming criteria are not met.",
                UserWarning,
            )
            return VerificationResult(
                all_criteria_met=False,
                unmet_criteria=list(range(1, len(success_criteria) + 1)),
                issues=[f"Verification failed with error: {e}"],
                overall_assessment="Verification could not be completed",
            )

    def _prepare_fix_instruction(
        self,
        success_criteria: List[str],
        verification: VerificationResult,
    ) -> str:
        """
        Prepare an instruction to fix issues identified during verification.

        Args:
            success_criteria: List of all success criteria
            verification: Verification result with issues

        Returns:
            Instruction for the agent to fix the issues
        """
        # Build list of unmet criteria with their descriptions
        unmet_details = []
        for criterion_num in verification.unmet_criteria:
            if 1 <= criterion_num <= len(success_criteria):
                criterion_text = success_criteria[criterion_num - 1]
                unmet_details.append(f"{criterion_num}. {criterion_text}")

        unmet_list = "\n".join(unmet_details)
        issues_list = "\n".join(f"- {issue}" for issue in verification.issues)

        fix_instruction = f"""The following success criteria are NOT yet met:

{unmet_list}

Issues identified:
{issues_list}

Overall assessment: {verification.overall_assessment}

Please fix these issues to ensure ALL success criteria are satisfied."""

        return fix_instruction

    def _handle_function_calls(
        self,
        raw_response: str,
        function_map: Dict[str, Callable],
    ) -> str:
        """
        Execute function calls from the agent's response and prepare next instruction.

        This method:
        1. Parses function calls from the response
        2. Executes the functions
        3. Returns an instruction containing the function results to send back to the agent

        Args:
            raw_response: The agent's response that contains function calls
            function_map: Mapping of function names to callables

        Returns:
            Instruction text with function results to send back to the agent
        """
        # Parse function calls from response
        function_calls = self._parse_function_calls(raw_response)

        # Execute function calls
        function_results = []
        for func_call in function_calls:
            func_name = func_call.get("name")
            func_args = func_call.get("arguments", {})

            # Skip if function name is missing
            if not func_name:
                continue

            if func_name not in function_map:
                result = {"error": f"Function '{func_name}' not found"}
                error = f"Function '{func_name}' not found"
                # Notify listener of error
                if self.listener:
                    self.listener.on_function_result(func_name, None, error)
            else:
                try:
                    func = function_map[func_name]

                    # Notify listener of function call (right before execution)
                    if self.listener:
                        self.listener.on_function_call(func_name, func_args)

                    result = func(**func_args)
                    # Notify listener of success
                    if self.listener:
                        self.listener.on_function_result(func_name, result, None)
                except Exception as e:
                    result = {"error": f"Error calling {func_name}: {str(e)}"}
                    # Notify listener of error
                    if self.listener:
                        self.listener.on_function_result(func_name, None, str(e))

            function_results.append({"function": func_name, "result": result})

        # Build follow-up instruction with function results
        results_text = "Function call results:\n\n"
        for fr in function_results:
            results_text += f"Function: {fr['function']}\n"
            results_text += f"Result: {json.dumps(fr['result'], indent=2)}\n\n"

        results_text += "\nPlease continue with your response based on these results."

        return results_text

    def _parse_function_calls(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse function calls from agent response.

        Looks for <function-call>...</function-call> blocks containing JSON.

        Args:
            response: Agent's response text

        Returns:
            List of function call dictionaries with 'name' and 'arguments' keys
        """
        function_calls = []
        pattern = r"<function-call>\s*(\{.*?\})\s*</function-call>"
        matches = re.findall(pattern, response, re.DOTALL)

        for match in matches:
            try:
                func_call = json.loads(match)
                if "name" in func_call:
                    function_calls.append(func_call)
            except json.JSONDecodeError:
                # Skip invalid JSON
                continue

        return function_calls

    def _parse_type_inference_response(
        self, response: str, possible_types: List[Type[Any]]
    ) -> Tuple[Any, Type[Any]]:
        """
        Parse type inference response.

        Args:
            response: The agent's response
            possible_types: List of possible types

        Returns:
            Tuple of (parsed result, chosen type)

        Raises:
            AugmentParseError: If parsing fails
        """
        # Extract message
        message_match = re.search(
            r"<augment-agent-message>\s*(.*?)\s*</augment-agent-message>",
            response,
            re.DOTALL,
        )
        if message_match:
            self.last_model_answer = message_match.group(1).strip()
        else:
            self.last_model_answer = None

        # Extract type name
        type_match = re.search(
            r"<augment-agent-type>\s*(\w+)\s*</augment-agent-type>", response, re.DOTALL
        )
        if not type_match:
            # If no type tags found, check if response is empty or just whitespace
            # This can happen when agent completes a task (like file creation) successfully
            # but doesn't provide a structured response
            if not response or response.strip() == "":
                # Return empty string as success indicator
                return "", str

            # If there's content but no tags, try to extract it as a string
            # This handles cases where agent responds without proper formatting
            content = response.strip()
            if content:
                # Return the content as a string
                return content, str

            raise AugmentParseError(
                "No type classification found. Expected <augment-agent-type> tags."
            )

        type_name = type_match.group(1).strip()

        # Find the matching type by name
        chosen_type = None
        for t in possible_types:
            if t.__name__ == type_name:
                chosen_type = t
                break

        if chosen_type is None:
            type_names = [t.__name__ for t in possible_types]
            raise AugmentParseError(
                f"Invalid type name '{type_name}'. Must be one of: {', '.join(type_names)}"
            )

        # Extract result
        result_match = re.search(
            r"<augment-agent-result>\s*(.*?)\s*</augment-agent-result>",
            response,
            re.DOTALL,
        )
        if not result_match:
            raise AugmentParseError(
                "No structured result found. Expected <augment-agent-result> tags."
            )

        content = result_match.group(1).strip()

        # Parse the result according to the chosen type
        try:
            parsed_result = self._convert_to_type(content, chosen_type)
            return parsed_result, chosen_type
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            raise AugmentParseError(
                f"Could not parse result as {chosen_type.__name__}: {e}"
            )

    @contextmanager
    def session(
        self, session_id: Optional[str] = None
    ) -> Generator["Agent", None, None]:
        """
        Create a session context for maintaining conversation continuity.

        By default, each run() call creates a fresh session. Use this context
        manager to maintain conversation continuity across multiple calls.

        Usage:
            agent = Auggie()

            # Without session - each call is independent
            agent.run("Create a function")
            agent.run("Test it")  # ❌ Won't remember the function

            # With session - calls remember each other
            with agent.session() as session:
                session.run("Create a function called add_numbers")
                session.run("Now test that function")  # ✅ Remembers add_numbers!

        Args:
            session_id: Optional session ID (currently ignored, auto-generated)

        Yields:
            Agent: This agent instance
        """
        # Mark that we're in a session
        self._in_session = True

        try:
            yield self
        finally:
            # End the session
            self._in_session = False

    def _get_type_description(self, return_type: Type) -> str:
        """Get the JSON structure description for the type."""
        # Built-in types
        if return_type in (int, float, str, bool):
            return "your_result_value"
        elif return_type in (list, dict):
            return "your_result_value"

        # Generic types (list[SomeClass], dict[str, SomeClass], etc.)
        elif hasattr(return_type, "__origin__") or get_origin(return_type) is not None:
            origin = get_origin(return_type)
            args = get_args(return_type)

            if origin is list:
                if args and len(args) == 1:
                    # list[SomeClass] - create example array with one element
                    element_type = args[0]
                    if is_dataclass(element_type):
                        field_names = [f.name for f in fields(element_type)]
                        element_example = {
                            name: f"<{name}_value>" for name in field_names
                        }
                        return json.dumps([element_example], indent=2)
                    elif hasattr(element_type, "__name__") and issubclass(
                        element_type, Enum
                    ):
                        return '["<enum_value>"]'
                    else:
                        return '["<element_value>"]'
                else:
                    return "your_result_value"  # Plain list
            elif origin is dict:
                return "your_result_value"  # For now, treat as plain dict
            else:
                return "your_result_value"  # Other generic types

        # Dataclass
        elif is_dataclass(return_type):
            field_names = [f.name for f in fields(return_type)]
            example = {name: f"<{name}_value>" for name in field_names}
            return json.dumps(example, indent=2)

        # Enum
        elif issubclass(return_type, Enum):
            return "your_enum_value"

        else:
            raise ValueError(f"Unsupported return type: {return_type}")

    def _get_type_instructions(self, return_type: Type) -> str:
        """Get specific instructions for the type."""
        # Built-in types
        if return_type is int:
            return "IMPORTANT: Put your result inside <augment-agent-result> tags. Return just the integer number (no quotes)."
        elif return_type is float:
            return "IMPORTANT: Put your result inside <augment-agent-result> tags. Return just the decimal number (no quotes)."
        elif return_type is str:
            return "IMPORTANT: Put your result inside <augment-agent-result> tags. Return the string value in double quotes."
        elif return_type is bool:
            return "IMPORTANT: Put your result inside <augment-agent-result> tags. Return either true or false (no quotes)."
        elif return_type is list:
            return "IMPORTANT: Put your result inside <augment-agent-result> tags. Return a JSON array: [item1, item2, item3]"
        elif return_type is dict:
            return 'IMPORTANT: Put your result inside <augment-agent-result> tags. Return a JSON object: {"key1": "value1", "key2": "value2"}'

        # Generic types (list[SomeClass], dict[str, SomeClass], etc.)
        elif hasattr(return_type, "__origin__") or get_origin(return_type) is not None:
            origin = get_origin(return_type)
            args = get_args(return_type)

            if origin is list:
                if args and len(args) == 1:
                    element_type = args[0]
                    if is_dataclass(element_type):
                        field_info = []
                        for field in fields(element_type):
                            field_info.append(
                                f"    - {field.name}: {_get_type_name(field.type)}"
                            )

                        return f"""IMPORTANT: Put your JSON array inside <augment-agent-result> tags.

Return a JSON array of objects, each with these fields:
{chr(10).join(field_info)}

Example:
<augment-agent-result>
[{{"field1": value1, "field2": value2}}, {{"field1": value3, "field2": value4}}]
</augment-agent-result>"""
                    elif hasattr(element_type, "__name__") and issubclass(
                        element_type, Enum
                    ):
                        enum_values = [f'"{e.value}"' for e in element_type]
                        return f"IMPORTANT: Put your result inside <augment-agent-result> tags. Return a JSON array of enum values: {enum_values}"
                    else:
                        return f"IMPORTANT: Put your result inside <augment-agent-result> tags. Return a JSON array of {_get_type_name(element_type)} values: [value1, value2, value3]"
                else:
                    return "IMPORTANT: Put your result inside <augment-agent-result> tags. Return a JSON array: [item1, item2, item3]"
            elif origin is dict:
                return 'IMPORTANT: Put your result inside <augment-agent-result> tags. Return a JSON object: {"key1": "value1", "key2": "value2"}'
            else:
                return "IMPORTANT: Put your result inside <augment-agent-result> tags. Return the appropriate JSON structure for your type."

        # Dataclass
        elif is_dataclass(return_type):
            field_info = []
            for field in fields(return_type):
                field_info.append(f"  - {field.name}: {_get_type_name(field.type)}")

            return f"""IMPORTANT: Put your JSON object inside <augment-agent-result> tags.

Return a JSON object with these exact fields:
{chr(10).join(field_info)}

Example:
<augment-agent-result>
{{"field1": value1, "field2": value2}}
</augment-agent-result>"""

        # Enum
        elif issubclass(return_type, Enum):
            enum_values = [f'"{e.value}"' for e in return_type]
            return f"IMPORTANT: Put your result inside <augment-agent-result> tags. Return one of these exact values: {', '.join(enum_values)}"

        else:
            raise ValueError(f"Unsupported return type: {return_type}")

    def _parse_typed_response(self, response: str, return_type: Type[T]) -> T:
        """Parse the agent's structured response into the desired type."""
        # Extract message from <augment-agent-message> tags
        message_match = re.search(
            r"<augment-agent-message>\s*(.*?)\s*</augment-agent-message>",
            response,
            re.DOTALL,
        )
        if message_match:
            self.last_model_answer = message_match.group(1).strip()
        else:
            self.last_model_answer = None

        # Extract content from <augment-agent-result> tags
        result_match = re.search(
            r"<augment-agent-result>\s*(.*?)\s*</augment-agent-result>",
            response,
            re.DOTALL,
        )

        if not result_match:
            raise AugmentParseError(
                "No structured result found. Expected <augment-agent-result> tags in response."
            )

        content = result_match.group(1).strip()

        try:
            return self._convert_to_type(content, return_type)
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            raise AugmentParseError(
                f"Could not parse result as {return_type.__name__}: {e}"
            )

    def _convert_to_type(self, content: str, return_type: Type[T]) -> T:
        """Convert string content to the specified Python type."""

        # Special case for str - don't JSON parse it, just return as-is
        if return_type is str:
            return content  # type: ignore[return-value]

        # Built-in types that need JSON parsing
        if return_type in (int, float, bool, list, dict):
            parsed = json.loads(content)

            if not isinstance(parsed, return_type):
                raise ValueError(
                    f"Expected {return_type.__name__}, got {type(parsed).__name__}"
                )

            return parsed

        # Generic types (list[SomeClass], dict[str, SomeClass], etc.)
        elif hasattr(return_type, "__origin__") or get_origin(return_type) is not None:
            origin = get_origin(return_type)
            args = get_args(return_type)

            if origin is list:
                parsed = json.loads(content)
                if not isinstance(parsed, list):
                    raise ValueError(f"Expected list, got {type(parsed).__name__}")

                if args and len(args) == 1:
                    element_type = args[0]
                    # Convert each element to the specified type
                    result = []
                    for item in parsed:
                        if is_dataclass(element_type):
                            if not isinstance(item, dict):
                                raise ValueError(
                                    f"Expected dict for dataclass element, got {type(item).__name__}"
                                )
                            result.append(element_type(**item))  # type: ignore[misc]
                        elif hasattr(element_type, "__name__") and issubclass(
                            element_type, Enum
                        ):
                            result.append(element_type(item))
                        else:
                            # For basic types, just validate and append
                            if not isinstance(item, element_type):
                                raise ValueError(
                                    f"Expected {element_type.__name__}, got {type(item).__name__}"
                                )
                            result.append(item)
                    return result  # type: ignore[return-value]
                else:
                    # Plain list without type parameter
                    return parsed  # type: ignore[return-value]
            elif origin is dict:
                parsed = json.loads(content)
                if not isinstance(parsed, dict):
                    raise ValueError(f"Expected dict, got {type(parsed).__name__}")
                return parsed  # type: ignore[return-value]
            else:
                # Other generic types - try basic JSON parsing
                return json.loads(content)  # type: ignore[return-value,no-any-return]

        # Dataclass
        elif is_dataclass(return_type):
            parsed = json.loads(content)

            if not isinstance(parsed, dict):
                raise ValueError(
                    f"Expected dict for dataclass, got {type(parsed).__name__}"
                )

            return return_type(**parsed)

        # Enum
        elif issubclass(return_type, Enum):
            # Try JSON parsing first (for quoted values)
            try:
                parsed = json.loads(content)
                return return_type(parsed)  # type: ignore[return-value]
            except json.JSONDecodeError:
                # If JSON parsing fails, try direct string value
                return return_type(content.strip())  # type: ignore[return-value]

        else:
            raise ValueError(f"Unsupported return type: {return_type}")

    def get_workspace_path(self) -> Path:
        """
        Get the workspace path for this agent.

        Returns:
            Path object representing the workspace root
        """
        return self.workspace_path

    @property
    def session_id(self) -> Optional[str]:
        """
        Get the current session ID.

        Returns the session ID only when inside a session context manager.
        Returns None for standalone run() calls.
        """
        if self._in_session and self._acp_client:
            return self._acp_client.session_id  # type: ignore[attr-defined,no-any-return]
        return None

    def __repr__(self) -> str:
        """String representation of the Agent."""
        if self.session_id:
            return f"Agent(workspace_path='{self.workspace_path}', session_id='{self.session_id}')"
        return f"Agent(workspace_path='{self.workspace_path}')"

    def __del__(self) -> None:
        """Cleanup when agent is destroyed."""
        # Check if attributes exist (in case __init__ failed)
        if hasattr(self, "_acp_client") and self._acp_client:
            try:
                self._acp_client.stop()
            except Exception:
                pass  # Ignore errors during cleanup

    @staticmethod
    def _validate_workspace_path(workspace_root: Optional[Union[str, Path]]) -> Path:
        """
        Validate and resolve workspace path.

        Args:
            workspace_root: User-provided workspace path or None

        Returns:
            Resolved Path object

        Raises:
            AugmentWorkspaceError: If path is invalid
        """
        if workspace_root is None:
            return Path.cwd()

        path = Path(workspace_root).resolve()

        if not path.exists():
            raise AugmentWorkspaceError(f"Workspace path does not exist: {path}")

        if not path.is_dir():
            raise AugmentWorkspaceError(f"Workspace path is not a directory: {path}")

        return path

    @staticmethod
    def _validate_rules(rules: List[str]) -> List[str]:
        """
        Validate that all rule files exist.

        Args:
            rules: List of rule file paths

        Returns:
            The validated list of rule file paths

        Raises:
            FileNotFoundError: If any rule file does not exist
        """
        for rule_path in rules:
            path = Path(rule_path)
            if not path.exists():
                raise FileNotFoundError(f"Rule file does not exist: {rule_path}")
            if not path.is_file():
                raise ValueError(f"Rule path is not a file: {rule_path}")

        return rules

    @staticmethod
    def get_available_models() -> List[Model]:
        """
        Get the list of available AI models for the current account.

        This method calls `auggie model list` to retrieve the available models.

        Returns:
            List of Model objects containing id, name, and description

        Raises:
            AugmentNotFoundError: If auggie CLI is not found
            AugmentCLIError: If the CLI command fails

        Example:
            >>> models = Auggie.get_available_models()
            >>> for model in models:
            ...     print(f"{model.name} [{model.id}]")
            ...     print(f"  {model.description}")
            Claude Sonnet 4.5 [sonnet4.5]
              Anthropic Claude Sonnet 4.5, 200k context
        """
        # Check if auggie is available
        try:
            result = subprocess.run(
                ["auggie", "model", "list"],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except FileNotFoundError:
            raise AugmentNotFoundError(
                "auggie CLI not found. Please install auggie and ensure it's in your PATH."
            )
        except subprocess.TimeoutExpired:
            raise AugmentCLIError("Command timed out after 30 seconds", -1, "")

        if result.returncode != 0:
            raise AugmentCLIError(
                f"Failed to get model list: {result.stderr}",
                result.returncode,
                result.stderr,
            )

        # Parse the output
        models = []
        lines = result.stdout.strip().split("\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for lines that start with " - " (model entries)
            if line.startswith("- "):
                # Extract name and id from the format: " - Model Name [model-id]"
                match = re.match(r"^- (.+?)\s+\[([^\]]+)\]$", line)
                if match:
                    name = match.group(1).strip()
                    model_id = match.group(2).strip()

                    # Next line should be the description (indented)
                    description = ""
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not next_line.startswith("- "):
                            description = next_line
                            i += 1  # Skip the description line

                    models.append(
                        Model(id=model_id, name=name, description=description)
                    )

            i += 1

        return models


# Backward compatibility alias
Agent = Auggie
