#!/usr/bin/env python3
"""
Simple test to reproduce the PR summary issue without the full eval harness.

This test simulates querying GitHub and creating a PR summary JSON file.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auggie_sdk import Auggie


def get_pr_count(date: str) -> int:
    """Get actual PR count from GitHub for a date."""
    cmd = [
        "gh",
        "pr",
        "list",
        "--repo",
        "elastic/elasticsearch",
        "--state",
        "all",
        "--search",
        f"created:{date}..{date}",
        "--limit",
        "1000",
        "--json",
        "number",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    prs = json.loads(result.stdout)
    return len(prs)


def _run_pr_summary(date: str, expected_count: int):
    """Run a PR summary for a specific date (not a pytest test - run as script)."""
    print(f"\n{'='*80}")
    print(f"Test: PR Summary for {date} (expected: {expected_count} PRs)")
    print(f"{'='*80}")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone repo (minimal - just need a git repo)
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

        agent = Auggie(workspace_root=tmpdir)

        prompt = f"""Create a summary of ALL pull requests created on {date} in JSON format.

Save to: pr_summary.json

Include for each PR:
- number, title, author, status, created_date, description

Also include:
- summary_date (when this summary was created)
- date_range (start: {date}, end: {date})
- total_prs (count)

Make sure to include ALL PRs created on {date} (not other dates)."""

        try:
            _ = agent.run(prompt, timeout=1200)  # 20 minutes for large PR counts

            # Verify file was created
            json_file = Path(tmpdir) / "pr_summary.json"
            if not json_file.exists():
                print("❌ File not created")
                return False

            # Verify content
            with open(json_file) as f:
                data = json.load(f)

            pr_count = data.get("total_prs", len(data.get("pull_requests", [])))
            file_size = json_file.stat().st_size

            print("✅ Created file successfully")
            print(f"   PRs in summary: {pr_count}")
            print(f"   Expected PRs: {expected_count}")
            print(f"   File size: {file_size} bytes")
            print(
                f"   Coverage: {pr_count}/{expected_count} ({pr_count/expected_count*100:.1f}%)"
            )

            return pr_count == expected_count

        except Exception as e:
            print(f"❌ Failed with error: {type(e).__name__}: {e}")

            # Check if file was created despite the error
            json_file = Path(tmpdir) / "pr_summary.json"
            if json_file.exists():
                with open(json_file) as f:
                    data = json.load(f)
                pr_count = data.get("total_prs", len(data.get("pull_requests", [])))
                file_size = json_file.stat().st_size
                print("⚠️  File WAS created despite error!")
                print(f"   PRs in summary: {pr_count}")
                print(f"   Expected PRs: {expected_count}")
                print(f"   File size: {file_size} bytes")
                print("   This means the agent succeeded but failed to report back!")
            else:
                print("   File was NOT created")

            return False


def main():
    """Run tests with different PR counts."""
    print(f"\n{'='*80}")
    print("E2E Test: PR Summary with Real GitHub Data")
    print(f"{'='*80}")

    # Test dates with different PR counts
    test_cases = [
        ("2025-10-26", 4),  # Weekend - low count
        ("2025-10-25", 3),  # Weekend - low count
        ("2025-10-23", 66),  # Weekday - high count (expected to fail)
    ]

    results = []
    for date, expected_count in test_cases:
        # Verify expected count
        actual_count = get_pr_count(date)
        if actual_count != expected_count:
            print(
                f"⚠️  Warning: Expected {expected_count} PRs for {date}, but GitHub has {actual_count}"
            )
            expected_count = actual_count

        success = _run_pr_summary(date, expected_count)
        results.append((date, expected_count, success))

    # Summary
    print(f"\n{'='*80}")
    print("Test Summary")
    print(f"{'='*80}")
    for date, count, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {date} ({count} PRs)")

    # Return exit code
    all_passed = all(success for _, _, success in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
