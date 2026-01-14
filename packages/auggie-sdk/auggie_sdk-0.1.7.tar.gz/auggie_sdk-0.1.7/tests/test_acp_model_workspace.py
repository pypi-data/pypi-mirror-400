#!/usr/bin/env python3
"""
Test script to verify model and workspace_root parameters work correctly.
"""

import os
from pathlib import Path

import pytest

from auggie_sdk.acp import AuggieACPClient


@pytest.mark.integration
def test_basic_no_params():
    """Test basic usage without model or workspace params."""
    print("=" * 80)
    print("TEST 1: Basic usage (no model/workspace params)")
    print("=" * 80)

    client = AuggieACPClient()

    print(f"Model: {client.model}")
    print(f"Workspace root: {client.workspace_root}")

    client.start()
    print(f"✓ Agent started! Session ID: {client.session_id}")

    response = client.send_message("What is 2 + 2? Answer with just the number.")
    print(f"✓ Response: {response}")

    client.stop()
    print("✓ Agent stopped\n")


@pytest.mark.integration
def test_with_model():
    """Test with model parameter."""
    print("=" * 80)
    print("TEST 2: With model parameter")
    print("=" * 80)

    client = AuggieACPClient(model="claude-3-5-sonnet-latest")

    print(f"Model: {client.model}")
    print(f"Workspace root: {client.workspace_root}")

    client.start()
    print(f"✓ Agent started! Session ID: {client.session_id}")

    response = client.send_message("What is 3 + 3? Answer with just the number.")
    print(f"✓ Response: {response}")

    client.stop()
    print("✓ Agent stopped\n")


@pytest.mark.integration
def test_with_workspace():
    """Test with workspace_root parameter."""
    print("=" * 80)
    print("TEST 3: With workspace_root parameter")
    print("=" * 80)

    workspace = os.getcwd()
    client = AuggieACPClient(workspace_root=workspace)

    print(f"Model: {client.model}")
    print(f"Workspace root: {client.workspace_root}")

    client.start()
    print(f"✓ Agent started! Session ID: {client.session_id}")

    response = client.send_message("What is 4 + 4? Answer with just the number.")
    print(f"✓ Response: {response}")

    client.stop()
    print("✓ Agent stopped\n")


@pytest.mark.integration
def test_with_both():
    """Test with both model and workspace_root parameters."""
    print("=" * 80)
    print("TEST 4: With both model and workspace_root parameters")
    print("=" * 80)

    workspace = os.getcwd()
    client = AuggieACPClient(model="claude-3-5-sonnet-latest", workspace_root=workspace)

    print(f"Model: {client.model}")
    print(f"Workspace root: {client.workspace_root}")

    client.start()
    print(f"✓ Agent started! Session ID: {client.session_id}")

    response = client.send_message("What is 5 + 5? Answer with just the number.")
    print(f"✓ Response: {response}")

    client.stop()
    print("✓ Agent stopped\n")


@pytest.mark.integration
def test_context_manager():
    """Test with context manager."""
    print("=" * 80)
    print("TEST 5: Context manager with model and workspace")
    print("=" * 80)

    workspace = os.getcwd()

    with AuggieACPClient(
        model="claude-3-5-sonnet-latest", workspace_root=workspace
    ) as client:
        print(f"Model: {client.model}")
        print(f"Workspace root: {client.workspace_root}")
        print(f"✓ Agent started! Session ID: {client.session_id}")

        response = client.send_message("What is 6 + 6? Answer with just the number.")
        print(f"✓ Response: {response}")

    print("✓ Agent automatically stopped\n")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ACP CLIENT - MODEL AND WORKSPACE PARAMETER TESTS")
    print("=" * 80 + "\n")

    try:
        test_basic_no_params()
        input("Press Enter to continue to next test...")

        test_with_model()
        input("Press Enter to continue to next test...")

        test_with_workspace()
        input("Press Enter to continue to next test...")

        test_with_both()
        input("Press Enter to continue to next test...")

        test_context_manager()

        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        import traceback

        traceback.print_exc()
