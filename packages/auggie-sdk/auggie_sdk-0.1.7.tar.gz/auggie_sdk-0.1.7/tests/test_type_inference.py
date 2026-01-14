#!/usr/bin/env python3
"""
Quick test to verify automatic type inference works.
"""

import inspect

from auggie_sdk import Auggie
from auggie_sdk.prompt_formatter import DEFAULT_INFERENCE_TYPES


def test_default_inference_types():
    """Test that DEFAULT_INFERENCE_TYPES is defined correctly."""
    print("Testing DEFAULT_INFERENCE_TYPES...")
    assert DEFAULT_INFERENCE_TYPES == [int, float, bool, str, list, dict]
    print(
        f"✓ DEFAULT_INFERENCE_TYPES = {[t.__name__ for t in DEFAULT_INFERENCE_TYPES]}"
    )


def test_run_signature():
    """Test that run() method has correct signature."""
    print("\nTesting run() method signature...")

    sig = inspect.signature(Auggie.run)
    params = sig.parameters

    # Check that infer_type parameter is removed
    assert "infer_type" not in params, "infer_type parameter should be removed"
    print("✓ infer_type parameter removed")

    # Check that return_type is optional
    assert params["return_type"].default is None
    print("✓ return_type parameter is optional (defaults to None)")

    # Check that max_retries exists
    assert "max_retries" in params
    print("✓ max_retries parameter exists")


def test_docstring():
    """Test that docstring is updated."""
    print("\nTesting docstring...")
    docstring = Auggie.run.__doc__

    # Should mention automatic type inference
    assert "automatic" in docstring.lower() or "infer" in docstring.lower()
    print("✓ Docstring mentions automatic type inference")

    # Should not mention infer_type parameter
    assert "infer_type" not in docstring
    print("✓ Docstring doesn't mention infer_type parameter")


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("Testing Automatic Type Inference Changes")
    print("=" * 60)

    try:
        test_default_inference_types()
        test_run_signature()
        test_docstring()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
