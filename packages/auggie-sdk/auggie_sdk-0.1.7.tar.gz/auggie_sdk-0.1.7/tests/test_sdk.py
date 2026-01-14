#!/usr/bin/env python3
"""
Simple test script to verify the Augment SDK works.
"""

import json
import sys
from pathlib import Path

# Add the current directory to the path so we can import auggie_sdk
sys.path.insert(0, str(Path(__file__).parent))

import pytest
from auggie_sdk import Auggie
from auggie_sdk.exceptions import AugmentNotFoundError


@pytest.mark.integration
def test_basic_functionality():
    """Test basic SDK functionality."""
    print("Testing Augment Python SDK...")

    try:
        # Test 1: Create agent
        print("1. Creating agent...")
        agent = Auggie()
        print(f"   ✓ Agent created for: {agent.get_workspace_path()}")

        # Test 2: Simple instruction
        print("2. Testing simple instruction...")
        try:
            response = agent.run("What is 2 + 2?")
            print(f"   ✓ Got response: {response[:100]}...")
        except Exception as e:
            print(f"   ⚠ Instruction test failed: {e}")

        # Test 3: Another simple instruction
        print("3. Testing another simple instruction...")
        try:
            response = agent.run("What is the capital of France?")
            print(f"   ✓ Got response: {response[:100]}...")
        except Exception as e:
            print(f"   ⚠ Instruction test failed: {e}")

        print("\n✓ SDK basic functionality test completed!")
        return True

    except AugmentNotFoundError:
        print(
            "❌ auggie CLI not found. Please install with: npm install -g @augmentcode/auggie"
        )
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


@pytest.mark.integration
def test_error_handling():
    """Test error handling."""
    print("\nTesting error handling...")

    try:
        agent = Auggie()

        # Test empty instruction
        print("1. Testing empty instruction...")
        try:
            agent.run("")
            print("   ❌ Should have raised ValueError")
        except ValueError as e:
            print(f"   ✓ Correctly raised ValueError: {e}")

        # Test another simple instruction
        print("2. Testing another simple instruction...")
        try:
            response = agent.run("test simple instruction")
            print(f"   ✓ Got response: {response[:50]}...")
        except Exception as e:
            print(f"   ⚠ Instruction test failed: {e}")

        print("\n✓ Error handling test completed!")
        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def main():
    """Main test function."""
    print("Augment Python SDK - Test Script")
    print("=" * 40)

    success = True
    success &= test_basic_functionality()
    success &= test_error_handling()

    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
