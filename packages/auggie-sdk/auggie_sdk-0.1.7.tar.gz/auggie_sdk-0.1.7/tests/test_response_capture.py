#!/usr/bin/env python3
"""
Test to capture agent responses and see what's actually being sent.

Uses the AgentEventListener interface to log all messages and see where
the 64KB limit is being exceeded.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auggie_sdk import Auggie
from auggie_sdk.listener import AgentListener


class ResponseCapturingListener(AgentListener):
    """Listener that captures all agent responses."""

    def __init__(self, output_file: Path):
        self.output_file = output_file
        self.messages = []
        self.tool_calls = []
        self.tool_responses = []

    def on_agent_message(self, message: str):
        """Capture the complete agent message."""
        message_size = len(message.encode("utf-8"))
        self.messages.append(message)

        # Log to file
        with open(self.output_file, "a") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"AGENT MESSAGE ({message_size} bytes)\n")
            f.write(f"{'='*80}\n")
            f.write(message)
            f.write("\n")

        print(f"  📝 Agent message: {message_size} bytes")

    def on_tool_call(self, tool_call_id: str, title: str, kind=None, status=None):
        """Log tool calls."""
        self.tool_calls.append((tool_call_id, title, kind, status))

        with open(self.output_file, "a") as f:
            f.write(f"\n[TOOL CALL] {title} (kind={kind}, status={status})\n")

        print(f"  🔧 Tool call: {title}")

    def on_tool_response(self, tool_call_id: str, status=None, content=None):
        """Log tool responses."""
        content_size = len(str(content).encode("utf-8")) if content else 0
        self.tool_responses.append((tool_call_id, status, content))

        with open(self.output_file, "a") as f:
            f.write(f"\n[TOOL RESPONSE] status={status}, size={content_size} bytes\n")
            if content:
                content_str = str(content)[:500]  # Truncate long content
                f.write(f"Content preview: {content_str}...\n")

        print(f"  ✅ Tool response: {status}, {content_size} bytes")

    def on_agent_thought(self, text: str):
        """Log agent thoughts."""
        with open(self.output_file, "a") as f:
            f.write(f"\n[AGENT THOUGHT] {text}\n")

    def get_total_message_size(self) -> int:
        """Get total size of all messages."""
        return sum(len(msg.encode("utf-8")) for msg in self.messages)


def _run_with_listener(date: str, expected_count: int):
    """Run PR summary with response capturing (not a pytest test - run as script)."""
    print(f"\n{'='*80}")
    print(f"Test: PR Summary for {date} (expected: {expected_count} PRs)")
    print(f"{'='*80}")

    # Create output file for captured responses
    output_file = Path(f"/tmp/agent_response_{date}.log")
    output_file.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone repo
        print("Cloning repository...")
        subprocess.run(
            [
                "git",
                "clone",
                "--depth=1",
                "https://github.com/elastic/elasticsearch.git",
                tmpdir,
            ],
            capture_output=True,
            check=True,
        )

        # Create listener
        listener = ResponseCapturingListener(output_file)

        # Create agent with listener
        agent = Auggie(workspace_root=tmpdir, listener=listener)

        prompt = f"""Create a summary of ALL pull requests created on {date} in JSON format.

Save to: pr_summary.json

Include for each PR:
- number, title, author, status, created_date, description

Also include:
- summary_date (when this summary was created)
- date_range (start: {date}, end: {date})
- total_prs (count)

Make sure to include ALL PRs created on {date} (not other dates)."""

        print("Running agent with listener...")
        print(f"Capturing responses to: {output_file}")

        try:
            _ = agent.run(prompt, timeout=300)

            # Get stats
            total_message_size = listener.get_total_message_size()

            print("\n✅ Agent completed successfully")
            print(f"   Total messages: {len(listener.messages)}")
            print(f"   Total message bytes: {total_message_size}")
            print(f"   Tool calls: {len(listener.tool_calls)}")
            print(f"   Tool responses: {len(listener.tool_responses)}")
            print(f"   64KB limit: {64 * 1024} bytes")
            print(f"   Over limit: {total_message_size > 64 * 1024}")

            # Check file
            json_file = Path(tmpdir) / "pr_summary.json"
            if json_file.exists():
                file_size = json_file.stat().st_size
                with open(json_file) as f:
                    data = json.load(f)
                pr_count = data.get("total_prs", len(data.get("pull_requests", [])))
                print(f"   JSON file: {file_size} bytes, {pr_count} PRs")

            print(f"\n📄 Full response saved to: {output_file}")
            return True

        except Exception as e:
            print(f"\n❌ Failed with error: {type(e).__name__}: {e}")

            # Get stats even on failure
            total_message_size = listener.get_total_message_size()

            print(f"   Total messages received: {len(listener.messages)}")
            print(f"   Total message bytes: {total_message_size}")
            print(f"   Tool calls: {len(listener.tool_calls)}")
            print(f"   Tool responses: {len(listener.tool_responses)}")
            print(f"   64KB limit: {64 * 1024} bytes")
            print(f"   Over limit: {total_message_size > 64 * 1024}")

            # Check if file was created
            json_file = Path(tmpdir) / "pr_summary.json"
            if json_file.exists():
                file_size = json_file.stat().st_size
                with open(json_file) as f:
                    data = json.load(f)
                pr_count = data.get("total_prs", len(data.get("pull_requests", [])))
                print(f"   JSON file: {file_size} bytes, {pr_count} PRs")

            print(f"\n📄 Partial response saved to: {output_file}")
            return False


def main():
    """Run tests with different PR counts."""
    print(f"\n{'='*80}")
    print("Response Capture Test")
    print(f"{'='*80}")

    # Test with different dates
    test_cases = [
        ("2025-10-26", 4),  # Small - should work
        ("2025-10-23", 66),  # Large - should fail
    ]

    for date, expected_count in test_cases:
        _run_with_listener(date, expected_count)

    print(f"\n{'='*80}")
    print("Check the log files in /tmp/agent_response_*.log")
    print(f"{'='*80}")


if __name__ == "__main__":
    sys.exit(main())
