#!/usr/bin/env python3
"""
End-to-end test for session continuity in the Augment SDK.

This test verifies that:
1. Session context manager works with real CLI calls
2. Session memory persists between calls within a session
3. The agent can recall information from previous messages in the session
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path.cwd()))

import pytest
from auggie_sdk import Auggie
from auggie_sdk.exceptions import AugmentError


@pytest.mark.integration
def test_session_memory():
    """Test that session memory works end-to-end with real CLI calls."""
    print("🧪 Running end-to-end session memory test...")

    try:
        # Create agent
        agent = Auggie()
        print(f"✅ Created agent: {agent}")

        # Test session with memory
        with agent.session() as session:
            print("\n📝 Starting session...")
            print(f"   Session ID: {session.session_id}")

            # First message - establish the number
            print("   Message 1: Telling the agent about number 57")
            response1 = session.run("i'm thinking of a number, 57")
            print(f"   Response 1: {response1[:100]}...")
            print(f"   Session ID after first call: {session.last_session_id}")

            # Second message - test if it remembers
            print("   Message 2: Asking what number I'm thinking of")
            response2 = session.run("what is the number I'm thinking of?")
            print(f"   Response 2: {response2}")
            print(f"   Session ID after second call: {session.last_session_id}")

            # Check if the response contains 57
            if "57" in response2:
                print("✅ SUCCESS: Agent remembered the number 57!")
                return True
            else:
                print(f"❌ FAILURE: Agent did not remember 57. Response: {response2}")
                return False

    except AugmentError as e:
        print(f"❌ FAILURE: Augment error occurred: {e}")
        return False
    except Exception as e:
        print(f"❌ FAILURE: Unexpected error: {e}")
        return False


@pytest.mark.integration
def test_session_isolation():
    """Test that different sessions are isolated from each other."""
    print("\n🧪 Running session isolation test...")

    try:
        agent1 = Agent()
        agent2 = Agent()

        # First agent/session with number 42
        with agent1.session() as session1:
            print("   Agent 1 Session: Telling agent about number 42")
            session1.run("i'm thinking of a number, 42")

        # Second agent/session with number 99 (completely separate)
        with agent2.session() as session2:
            print("   Agent 2 Session: Telling agent about number 99")
            session2.run("i'm thinking of a number, 99")

            # Ask about the number in session 2
            response = session2.run("what is the number I'm thinking of?")
            print(f"   Agent 2 Session response: {response}")

            # Since this is a new session, it shouldn't know about any number
            # But let's check it doesn't mention 42 from the other agent
            if "42" not in response:
                print("✅ SUCCESS: Sessions are properly isolated!")
                return True
            else:
                print(
                    f"❌ FAILURE: Session isolation failed - mentioned 42. Response: {response}"
                )
                return False

    except Exception as e:
        print(f"❌ FAILURE: Error in isolation test: {e}")
        return False


@pytest.mark.integration
def test_session_resume():
    """Test that sessions can be resumed correctly."""
    print("\n🧪 Running session resume test...")

    try:
        agent = Auggie()
        session_id = None

        # First session - establish number
        with agent.session() as session:
            print("   First session: Establishing number 123")
            session.run("i'm thinking of a number, 123")
            session_id = session.last_session_id
            print(f"   Session ID: {session_id}")

        # Resume the same session
        if session_id:
            with agent.session(session_id) as session:
                print("   Resumed session: Asking about the number")
                response = session.run("what is the number I'm thinking of?")
                print(f"   Resumed session response: {response}")

                # Handle both raw response and JSON response
                response_text = response
                if response.startswith('{"type"'):
                    # This is still JSON, extract the result
                    import json

                    try:
                        json_data = json.loads(response)
                        response_text = json_data.get("result", response)
                    except (json.JSONDecodeError, ValueError, TypeError):
                        response_text = response

                if "123" in response_text:
                    print("✅ SUCCESS: Session resume works correctly!")
                    return True
                else:
                    print(
                        f"❌ FAILURE: Session resume failed. Response: {response_text}"
                    )
                    return False
        else:
            print("❌ FAILURE: No session ID was generated")
            return False

    except Exception as e:
        print(f"❌ FAILURE: Error in resume test: {e}")
        return False


@pytest.mark.integration
def test_no_session_isolation():
    """Test that WITHOUT explicit session management, calls should NOT remember each other."""
    print("\n🧪 Running No Session Isolation test...")

    try:
        agent = Auggie()

        # First call: tell agent about number 57
        print("   First call: Telling agent about number 57")
        response1 = agent.run("i'm thinking of a number, 57")
        print(f"   Response 1: {response1[:100]}...")

        # Second call: ask what number (should NOT remember 57)
        print("   Second call: Asking what number I'm thinking of")
        response2 = agent.run("what is the number I'm thinking of?")
        print(f"   Response 2: {response2}")

        # Check that the agent does NOT remember the number
        if "57" not in response2:
            print(
                "✅ SUCCESS: Agent correctly does NOT remember between separate calls!"
            )
            return True
        else:
            print(
                f"❌ FAIL: Agent incorrectly remembered the number from previous call. Response: {response2}"
            )
            return False

    except Exception as e:
        print(f"❌ FAILURE: Error in no session isolation test: {e}")
        return False


def main():
    """Run all end-to-end tests."""
    print("🚀 Starting Augment SDK End-to-End Session Tests")
    print("=" * 60)

    tests = [
        ("Session Memory", test_session_memory),
        ("Session Isolation", test_session_isolation),
        ("Session Resume", test_session_resume),
        ("No Session Isolation", test_no_session_isolation),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1

    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Session functionality is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the session implementation.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
