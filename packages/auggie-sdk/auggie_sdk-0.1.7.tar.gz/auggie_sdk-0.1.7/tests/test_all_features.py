"""
Quick test of all AuggieACPClient features.
"""

from auggie_sdk.acp import AuggieACPClient, AgentEventListener
from typing import Optional, Any


class SimpleListener(AgentEventListener):
    """Simple listener that tracks events."""

    def __init__(self):
        self.tool_calls = []
        self.messages = []

    def on_agent_message(self, text: str) -> None:
        self.messages.append(text)

    def on_tool_call_start(
        self,
        tool_call_id: str,
        title: str,
        kind: Optional[str] = None,
        status: Optional[str] = None,
    ) -> None:
        self.tool_calls.append(
            {
                "type": "start",
                "id": tool_call_id,
                "title": title,
                "kind": kind,
                "status": status,
            }
        )
        print(f"  → Tool call started: {title}")

    def on_tool_call_update(
        self,
        tool_call_id: str,
        status: Optional[str] = None,
        content: Optional[Any] = None,
    ) -> None:
        self.tool_calls.append(
            {
                "type": "update",
                "id": tool_call_id,
                "status": status,
            }
        )
        print(f"  → Tool call updated: {tool_call_id} - {status}")

    def on_agent_thought(self, text: str) -> None:
        pass


def main():
    print("Testing AuggieACPClient Features")
    print("=" * 80)

    # Test 1: Basic start/stop
    print("\n1. Testing start/stop...")
    client = AuggieACPClient()
    client.start()
    assert client.is_running, "Client should be running"
    assert client.session_id is not None, "Should have session ID"
    print(f"   ✓ Started successfully (session: {client.session_id})")
    client.stop()
    assert not client.is_running, "Client should be stopped"
    print("   ✓ Stopped successfully")

    # Test 2: Send message and get response
    print("\n2. Testing send_message...")
    client.start()
    response = client.send_message("What is 2 + 2? Answer in one sentence.")
    assert "4" in response, f"Expected '4' in response, got: {response}"
    print(f"   ✓ Got response: {response}")
    client.stop()

    # Test 3: Event listener
    print("\n3. Testing event listener...")
    listener = SimpleListener()
    client = AuggieACPClient(listener=listener)
    client.start()
    response = client.send_message(
        "Read the file experimental/guy/auggie_sdk/README.md"
    )
    assert len(listener.tool_calls) > 0, "Should have received tool call events"
    print(f"   ✓ Received {len(listener.tool_calls)} tool call events")
    print(f"   ✓ Received {len(listener.messages)} message chunks")
    client.stop()

    # Test 4: Clear context
    print("\n4. Testing clear_context...")
    client = AuggieACPClient()
    client.start()
    old_session = client.session_id
    client.send_message("Remember the number 42")
    client.clear_context()
    new_session = client.session_id
    assert old_session != new_session, "Session ID should change after clear_context"
    print(
        f"   ✓ Context cleared (old: {old_session[:8]}..., new: {new_session[:8]}...)"
    )
    response = client.send_message("What number did I tell you to remember?")
    # Agent shouldn't remember since context was cleared
    print(f"   ✓ Agent response after clear: {response[:50]}...")
    client.stop()

    # Test 5: Context manager
    print("\n5. Testing context manager...")
    with AuggieACPClient() as client:
        assert client.is_running, "Client should be running in context"
        response = client.send_message("What is 10 * 5?")
        assert "50" in response, f"Expected '50' in response, got: {response}"
        print(f"   ✓ Context manager works: {response}")
    assert not client.is_running, "Client should be stopped after context exit"
    print("   ✓ Automatically stopped after context exit")

    # Test 6: Multiple messages in same session
    print("\n6. Testing multiple messages in same session...")
    client = AuggieACPClient()
    client.start()
    session = client.session_id
    response1 = client.send_message("What is 5 + 3?")
    response2 = client.send_message("What is that number times 2?")
    assert client.session_id == session, "Session should remain the same"
    print(f"   ✓ Message 1: {response1}")
    print(f"   ✓ Message 2: {response2}")
    print(f"   ✓ Same session maintained: {session[:8]}...")
    client.stop()

    print("\n" + "=" * 80)
    print("✓ All tests passed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
