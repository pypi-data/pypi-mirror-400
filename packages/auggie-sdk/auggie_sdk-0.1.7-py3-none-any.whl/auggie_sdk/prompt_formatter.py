"""
Prompt formatting for agent instructions.
"""

from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional, Type, TypeVar, get_args, get_origin

try:
    from .function_tools import format_function_schemas_for_prompt
except ImportError:
    # When running as a script
    from function_tools import format_function_schemas_for_prompt

T = TypeVar("T")

# Default types for automatic type inference
DEFAULT_INFERENCE_TYPES = [int, float, bool, str, list, dict]


def _get_type_name(type_hint) -> str:
    """Safely get the name of a type hint."""
    if isinstance(type_hint, str):
        return type_hint
    if hasattr(type_hint, "__name__"):
        return type_hint.__name__
    return str(type_hint)


class AgentPromptFormatter:
    """
    Formats prompts for agent instructions.

    Handles:
    - Adding function schemas to instructions
    - Adding type requirements (typed or type inference)
    - Creating retry prompts when parsing fails
    """

    def prepare_instruction_prompt(
        self,
        instruction: str,
        return_type: Optional[Type[T]],
        functions: Optional[List[Callable]] = None,
    ) -> tuple[str, Dict[str, Callable]]:
        """
        Prepare the instruction prompt with function schemas and type requirements.

        Args:
            instruction: The base instruction from the user
            return_type: Expected return type (None for type inference)
            functions: Optional list of functions the agent can call

        Returns:
            Tuple of (prepared instruction, function_map)
        """
        # Add function schemas to instruction if functions are provided
        enhanced_instruction = instruction
        function_map = {}
        if functions:
            function_schemas_text = format_function_schemas_for_prompt(functions)
            enhanced_instruction = f"{instruction}\n\n{function_schemas_text}"
            function_map = {func.__name__: func for func in functions}

        # Determine if we're in type inference mode
        infer_type = return_type is None

        # Build the instruction with type requirements
        if infer_type:
            # Type inference mode - use default inference types
            prepared_instruction = self._build_type_inference_instruction(
                enhanced_instruction, DEFAULT_INFERENCE_TYPES
            )
        else:
            # Explicit type mode
            prepared_instruction = self._build_typed_instruction(
                enhanced_instruction, return_type
            )

        return prepared_instruction, function_map

    def prepare_retry_prompt(
        self,
        return_type: Optional[Type[T]],
        error: str,
        attempt: int,
    ) -> str:
        """
        Prepare a retry prompt asking the agent to fix the output.

        Args:
            return_type: Expected return type (None for type inference)
            error: The error message from the parsing failure
            attempt: The current attempt number

        Returns:
            Retry instruction prompt
        """
        # Determine possible types for type inference mode
        possible_types = DEFAULT_INFERENCE_TYPES if return_type is None else None

        return self._build_retry_instruction(
            return_type,
            possible_types,
            error,
            attempt,
        )

    def _build_typed_instruction(self, instruction: str, return_type: Type[T]) -> str:
        """
        Build instruction with explicit type requirements.

        Args:
            instruction: Base instruction
            return_type: Expected return type

        Returns:
            Instruction with type requirements
        """
        type_name = return_type.__name__

        typed_instruction = f"""{instruction}

IMPORTANT: Provide your response in this EXACT format:

<augment-agent-message>
[Optional: Your explanation or reasoning]
</augment-agent-message>

<augment-agent-result>
[Your {type_name} result here]
</augment-agent-result>

The content inside <augment-agent-result> tags must be a valid {type_name} that can be parsed.
"""
        return typed_instruction

    def _build_type_inference_instruction(
        self, instruction: str, possible_types: List[Type]
    ) -> str:
        """
        Build instruction with type inference requirements.

        Args:
            instruction: Base instruction
            possible_types: List of possible types to choose from

        Returns:
            Instruction with type inference requirements
        """
        type_names = [t.__name__ for t in possible_types]
        types_str = ", ".join(type_names)

        inference_instruction = f"""{instruction}

IMPORTANT: Provide your response in this EXACT format:

<augment-agent-message>
[Optional: Your explanation or reasoning]
</augment-agent-message>

<augment-agent-type>TYPE_NAME</augment-agent-type>

<augment-agent-result>
[Your result here]
</augment-agent-result>

Where TYPE_NAME is one of: {types_str}

Choose the most appropriate type from the list above."""
        return inference_instruction

    def _build_retry_instruction(
        self,
        return_type: Optional[Type[T]],
        possible_types: Optional[List[Type]],
        error: str,
        attempt: int,
    ) -> str:
        """
        Build retry instruction for parsing failures.

        Args:
            return_type: Expected return type (None for type inference)
            possible_types: List of possible types (for type inference mode)
            error: Error message from parsing failure
            attempt: Current attempt number

        Returns:
            Retry instruction
        """
        retry_instruction = f"""The previous response could not be parsed.

Error: {error}

This is attempt {attempt}. Please provide your response again in the correct format.
"""

        # Add detailed schema information for the expected type
        if return_type is not None:
            schema_info = self._get_type_schema_info(return_type)
            if schema_info:
                retry_instruction += f"\n{schema_info}"
        elif possible_types:
            type_names = [t.__name__ for t in possible_types]
            types_str = ", ".join(type_names)
            retry_instruction += f"\nRemember to include <augment-agent-type>TYPE_NAME</augment-agent-type> where TYPE_NAME is one of: {types_str}"

        return retry_instruction

    def _get_type_schema_info(self, return_type: Type) -> str:
        """
        Get detailed schema information for a type to help with retry.

        Args:
            return_type: The expected return type

        Returns:
            Schema information string, or empty string if not applicable
        """
        # Generic types (list[SomeClass], dict[str, SomeClass], etc.)
        if hasattr(return_type, "__origin__") or get_origin(return_type) is not None:
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

                        return f"""
REMINDER: Return a JSON array of objects, each with these EXACT fields:
{chr(10).join(field_info)}

Example:
<augment-agent-result>
[{{"field1": value1, "field2": value2}}, {{"field1": value3, "field2": value4}}]
</augment-agent-result>"""
                    elif hasattr(element_type, "__name__") and issubclass(
                        element_type, Enum
                    ):
                        enum_values = [f'"{e.value}"' for e in element_type]
                        return f"\nREMINDER: Return a JSON array of enum values: {enum_values}"
            elif origin is dict:
                return "\nREMINDER: Return a JSON object with key-value pairs."

        # Dataclass
        elif is_dataclass(return_type):
            field_info = []
            for field in fields(return_type):
                field_info.append(f"  - {field.name}: {_get_type_name(field.type)}")

            return f"""
REMINDER: Return a JSON object with these EXACT fields:
{chr(10).join(field_info)}

Example:
<augment-agent-result>
{{"field1": value1, "field2": value2}}
</augment-agent-result>"""

        # Enum
        elif hasattr(return_type, "__mro__") and Enum in return_type.__mro__:
            enum_values = [f'"{e.value}"' for e in return_type]
            return f"\nREMINDER: Return one of these exact values: {', '.join(enum_values)}"

        return ""


def main():
    """Demo the prompt formatter by generating sample prompts."""
    formatter = AgentPromptFormatter()

    print("=" * 80)
    print("PROMPT FORMATTER DEMO")
    print("=" * 80)

    # Example 1: Simple typed instruction
    print("\n" + "=" * 80)
    print("Example 1: Typed Instruction (return_type=int)")
    print("=" * 80)
    instruction = "What is 2 + 2?"
    prompt, _ = formatter.prepare_instruction_prompt(instruction, int, None)
    print(prompt)

    # Example 2: Type inference instruction
    print("\n" + "=" * 80)
    print("Example 2: Type Inference Instruction (return_type=None)")
    print("=" * 80)
    instruction = "What is the capital of France?"
    prompt, _ = formatter.prepare_instruction_prompt(instruction, None, None)
    print(prompt)

    # Example 3: Instruction with functions
    print("\n" + "=" * 80)
    print("Example 3: Instruction with Functions")
    print("=" * 80)

    def get_weather(location: str, unit: str = "celsius") -> dict:
        """
        Get weather for a location.

        Args:
            location: City name
            unit: Temperature unit
        """
        return {"temp": 72, "condition": "sunny"}

    instruction = "What's the weather in San Francisco?"
    prompt, func_map = formatter.prepare_instruction_prompt(
        instruction, dict, [get_weather]
    )
    print(prompt)
    print(f"\nFunction map: {list(func_map.keys())}")

    # Example 4: Retry prompt
    print("\n" + "=" * 80)
    print("Example 4: Retry Prompt (after parsing failure)")
    print("=" * 80)
    error = "Could not parse 'forty-two' as int"
    retry_prompt = formatter.prepare_retry_prompt(int, error, 1)
    print(retry_prompt)

    # Example 5: Type inference retry prompt
    print("\n" + "=" * 80)
    print("Example 5: Type Inference Retry Prompt")
    print("=" * 80)
    error = "Missing <response_type> tag"
    retry_prompt = formatter.prepare_retry_prompt(None, error, 2)
    print(retry_prompt)

    print("\n" + "=" * 80)
    print("END OF DEMO")
    print("=" * 80)


if __name__ == "__main__":
    main()
