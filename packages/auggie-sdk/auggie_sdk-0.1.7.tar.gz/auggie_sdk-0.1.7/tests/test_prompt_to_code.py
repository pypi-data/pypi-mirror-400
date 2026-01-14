"""
Tests for the prompt_to_code.py tool.
"""

import sys
from pathlib import Path
import tempfile
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompt_to_code import (
    read_prompt_file,
    save_generated_code,
    ConversionResult,
)


def test_read_prompt_file():
    """Test reading a prompt from a file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("This is a test prompt")
        temp_path = f.name

    try:
        content = read_prompt_file(temp_path)
        assert content == "This is a test prompt"
    finally:
        Path(temp_path).unlink()


def test_read_prompt_file_not_found():
    """Test reading a non-existent file raises an error."""
    with pytest.raises(RuntimeError, match="Failed to read prompt file"):
        read_prompt_file("/nonexistent/file.txt")


def test_save_generated_code():
    """Test saving generated code to a file."""
    code = "#!/usr/bin/env python3\nprint('Hello, world!')\n"

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output.py"
        result_path = save_generated_code(code, str(output_path))

        assert result_path == str(output_path)
        assert output_path.exists()
        assert output_path.read_text() == code

        # Check that file is executable
        assert output_path.stat().st_mode & 0o111  # Has execute permission


def test_save_generated_code_auto_name():
    """Test saving with auto-generated filename."""
    code = "#!/usr/bin/env python3\nprint('Hello, world!')\n"

    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = Path.cwd()
        try:
            # Change to temp directory
            import os

            os.chdir(tmpdir)

            # First save should create generated_sdk_program.py
            result_path1 = save_generated_code(code)
            assert Path(result_path1).name == "generated_sdk_program.py"
            assert Path(result_path1).exists()

            # Second save should create generated_sdk_program_1.py
            result_path2 = save_generated_code(code)
            assert Path(result_path2).name == "generated_sdk_program_1.py"
            assert Path(result_path2).exists()
        finally:
            os.chdir(original_cwd)


def test_conversion_result_success():
    """Test ConversionResult for successful conversion."""
    result = ConversionResult(code="print('hello')", success=True)
    assert result.success
    assert result.code == "print('hello')"
    assert result.error is None


def test_conversion_result_failure():
    """Test ConversionResult for failed conversion."""
    result = ConversionResult(code="", success=False, error="Test error")
    assert not result.success
    assert result.code == ""
    assert result.error == "Test error"


def test_prompt_to_code_imports():
    """Test that all necessary imports work."""
    # This test just verifies the module can be imported
    import prompt_to_code

    assert hasattr(prompt_to_code, "read_prompt_file")
    assert hasattr(prompt_to_code, "convert_prompt_to_code")
    assert hasattr(prompt_to_code, "save_generated_code")
    assert hasattr(prompt_to_code, "ConversionResult")
    assert hasattr(prompt_to_code, "main")


def test_conversion_prompt_format():
    """Test that the conversion prompt template is properly formatted."""
    from prompt_to_code import CONVERSION_PROMPT

    # Check that the prompt has the placeholder
    assert "{prompt_content}" in CONVERSION_PROMPT

    # Check that it can be formatted
    formatted = CONVERSION_PROMPT.format(prompt_content="Test prompt")
    assert "Test prompt" in formatted
    assert "{prompt_content}" not in formatted
