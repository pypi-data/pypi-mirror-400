"""
Utilities for converting Python functions to tool schemas for agent function calling.
"""

import inspect
import json
from typing import Any, Callable, Dict, List, Optional, Union, get_args, get_origin


def python_type_to_json_schema_type(py_type: Any) -> Dict[str, Any]:
    """
    Convert a Python type annotation to a JSON schema type.

    Args:
        py_type: Python type annotation

    Returns:
        JSON schema type definition
    """
    # Handle None/NoneType
    if py_type is None or py_type is type(None):
        return {"type": "null"}

    # Get origin for generic types (List, Dict, Optional, etc.)
    origin = get_origin(py_type)
    args = get_args(py_type)

    # Handle Optional[T] (Union[T, None])
    if origin is Union:
        # Filter out None types
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            # This is Optional[T]
            return python_type_to_json_schema_type(non_none_args[0])
        else:
            # Multiple union types - use anyOf
            return {"anyOf": [python_type_to_json_schema_type(arg) for arg in args]}

    # Handle List[T]
    if origin is list or py_type is list:
        if args:
            return {"type": "array", "items": python_type_to_json_schema_type(args[0])}
        return {"type": "array"}

    # Handle Dict[K, V]
    if origin is dict or py_type is dict:
        schema = {"type": "object"}
        if args and len(args) == 2:
            # Dict[str, T] - we can specify value type
            schema["additionalProperties"] = python_type_to_json_schema_type(args[1])
        return schema

    # Handle basic types
    type_mapping = {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
        Any: {},  # No type constraint
    }

    if py_type in type_mapping:
        return type_mapping[py_type]

    # Default to object for unknown types
    return {"type": "object"}


def extract_param_description(
    docstring: Optional[str], param_name: str
) -> Optional[str]:
    """
    Extract parameter description from docstring.

    Supports Google-style and NumPy-style docstrings.

    Args:
        docstring: Function docstring
        param_name: Parameter name to find

    Returns:
        Parameter description if found, None otherwise
    """
    if not docstring:
        return None

    lines = docstring.split("\n")
    in_args_section = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check if we're entering Args/Parameters section
        if stripped.lower() in ["args:", "arguments:", "parameters:", "params:"]:
            in_args_section = True
            continue

        # Check if we're leaving Args section (new section starts)
        if (
            in_args_section
            and stripped.endswith(":")
            and not stripped.startswith(param_name)
        ):
            in_args_section = False
            continue

        # Look for parameter in Args section
        if in_args_section:
            # Google style: "param_name: description" or "param_name (type): description"
            if stripped.startswith(f"{param_name}:") or stripped.startswith(
                f"{param_name} ("
            ):
                # Extract description after colon
                colon_idx = stripped.find(":", stripped.find(param_name))
                if colon_idx != -1:
                    desc = stripped[colon_idx + 1 :].strip()
                    # Check if description continues on next lines
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        # Stop if we hit another parameter or empty line
                        if not next_line or ":" in next_line:
                            break
                        desc += " " + next_line
                        j += 1
                    return desc

    return None


def function_to_schema(func: Callable) -> Dict[str, Any]:
    """
    Convert a Python function to a JSON schema for agent function calling.

    The function should have:
    - Type hints for parameters
    - A docstring with description and parameter descriptions

    Args:
        func: Python function to convert

    Returns:
        JSON schema dictionary with name, description, and parameters

    Example:
        >>> def get_weather(location: str, unit: str = "celsius") -> dict:
        ...     '''Get weather for a location.
        ...
        ...     Args:
        ...         location: City name or coordinates
        ...         unit: Temperature unit (celsius or fahrenheit)
        ...     '''
        ...     pass
        >>> schema = function_to_schema(get_weather)
        >>> schema['name']
        'get_weather'
    """
    sig = inspect.signature(func)
    doc = inspect.getdoc(func)

    # Extract function description (first line/paragraph of docstring)
    description = ""
    if doc:
        # Get everything before Args/Parameters section
        lines = doc.split("\n")
        desc_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.lower() in [
                "args:",
                "arguments:",
                "parameters:",
                "params:",
                "returns:",
                "return:",
            ]:
                break
            desc_lines.append(line)
        description = "\n".join(desc_lines).strip()

    if not description:
        description = f"Call the {func.__name__} function"

    # Build parameters schema
    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        # Skip self, cls, *args, **kwargs
        if param_name in ["self", "cls"] or param.kind in [
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ]:
            continue

        # Get type annotation
        param_type = (
            param.annotation if param.annotation != inspect.Parameter.empty else Any
        )
        param_schema = python_type_to_json_schema_type(param_type)

        # Get parameter description from docstring
        param_desc = extract_param_description(doc, param_name)
        if param_desc:
            param_schema["description"] = param_desc

        properties[param_name] = param_schema

        # Mark as required if no default value
        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    schema = {
        "name": func.__name__,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
        },
    }

    if required:
        schema["parameters"]["required"] = required

    return schema


def format_function_schemas_for_prompt(functions: List[Callable]) -> str:
    """
    Format function schemas as a string for inclusion in agent prompt.

    Args:
        functions: List of Python functions

    Returns:
        Formatted string describing available functions
    """
    if not functions:
        return ""

    schemas = [function_to_schema(func) for func in functions]

    prompt = "You have access to the following functions that you can call:\n\n"

    for schema in schemas:
        prompt += f"Function: {schema['name']}\n"
        prompt += f"Description: {schema['description']}\n"
        prompt += f"Parameters: {json.dumps(schema['parameters'], indent=2)}\n\n"

    prompt += """To call a function, include in your response:
<function-call>
{
  "name": "function_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}
</function-call>

You can call multiple functions by including multiple <function-call> blocks.
After calling functions, you will receive the results and can continue your response.
"""

    return prompt
