#!/usr/bin/env python3
"""
E2E test to reproduce the large response issue.

This test creates a scenario where the agent needs to create a large JSON file
and verifies that it can handle it without hitting ACP protocol limits.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auggie_sdk import Auggie


@pytest.mark.integration
def test_small_json():
    """Test creating a small JSON file (should work)."""
    print("\n" + "=" * 80)
    print("Test 1: Small JSON (10 items)")
    print("=" * 80)

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = Auggie(workspace_root=tmpdir)

        _ = agent.run(
            """Create a JSON file called items.json with 10 items.
            Each item should have: id, title, description.
            Save it to items.json in the current directory.""",
            timeout=30,
        )

        # Verify file was created
        json_file = Path(tmpdir) / "items.json"
        assert json_file.exists(), "JSON file not created"

        # Verify content
        with open(json_file) as f:
            data = json.load(f)

        print(f"✅ Created file with {len(data)} items")
        print(f"   File size: {json_file.stat().st_size} bytes")
        return True


@pytest.mark.integration
def test_medium_json():
    """Test creating a medium JSON file (50 items)."""
    print("\n" + "=" * 80)
    print("Test 2: Medium JSON (50 items)")
    print("=" * 80)

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = Auggie(workspace_root=tmpdir)

        try:
            _ = agent.run(
                """Create a JSON file called items.json with 50 items.
                Each item should have:
                - id (number)
                - title (string)
                - description (a paragraph of text, about 100 words)
                - tags (array of 5 strings)

                Save it to items.json in the current directory.""",
                timeout=60,
            )

            # Verify file was created
            json_file = Path(tmpdir) / "items.json"
            assert json_file.exists(), "JSON file not created"

            # Verify content
            with open(json_file) as f:
                data = json.load(f)

            print(f"✅ Created file with {len(data)} items")
            print(f"   File size: {json_file.stat().st_size} bytes")
            return True

        except Exception as e:
            print(f"❌ Failed with error: {type(e).__name__}: {e}")

            # Check if file was created despite the error
            json_file = Path(tmpdir) / "items.json"
            if json_file.exists():
                with open(json_file) as f:
                    data = json.load(f)
                print(
                    f"⚠️  File WAS created ({len(data)} items, {json_file.stat().st_size} bytes)"
                )
                print("   This means the agent succeeded but failed to report back!")
            else:
                print("   File was NOT created")
            return False


@pytest.mark.integration
def test_large_json():
    """Test creating a large JSON file (100 items)."""
    print("\n" + "=" * 80)
    print("Test 3: Large JSON (100 items)")
    print("=" * 80)

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = Auggie(workspace_root=tmpdir)

        try:
            _ = agent.run(
                """Create a JSON file called items.json with 100 items.
                Each item should have:
                - id (number)
                - title (string)
                - description (a paragraph of text, about 100 words)
                - tags (array of 5 strings)
                - metadata (object with 10 key-value pairs)

                Save it to items.json in the current directory.""",
                timeout=120,
            )

            # Verify file was created
            json_file = Path(tmpdir) / "items.json"
            assert json_file.exists(), "JSON file not created"

            # Verify content
            with open(json_file) as f:
                data = json.load(f)

            print(f"✅ Created file with {len(data)} items")
            print(f"   File size: {json_file.stat().st_size} bytes")
            return True

        except Exception as e:
            print(f"❌ Failed with error: {type(e).__name__}: {e}")

            # Check if file was created despite the error
            json_file = Path(tmpdir) / "items.json"
            if json_file.exists():
                with open(json_file) as f:
                    data = json.load(f)
                print(
                    f"⚠️  File WAS created ({len(data)} items, {json_file.stat().st_size} bytes)"
                )
                print("   This means the agent succeeded but failed to report back!")
            else:
                print("   File was NOT created")
            return False


@pytest.mark.integration
def test_very_large_json():
    """Test creating a very large JSON file (200 items) - expected to fail."""
    print("\n" + "=" * 80)
    print("Test 4: Very Large JSON (200 items) - may fail")
    print("=" * 80)

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = Auggie(workspace_root=tmpdir)

        try:
            _ = agent.run(
                """Create a JSON file called items.json with 200 items.
                Each item should have:
                - id (number)
                - title (string)
                - description (a paragraph of text, about 100 words)
                - tags (array of 5 strings)
                - metadata (object with 10 key-value pairs)

                Save it to items.json in the current directory.""",
                timeout=180,
            )

            # Verify file was created
            json_file = Path(tmpdir) / "items.json"

            if json_file.exists():
                with open(json_file) as f:
                    data = json.load(f)
                print(f"✅ Created file with {len(data)} items")
                print(f"   File size: {json_file.stat().st_size} bytes")
                return True
            else:
                print("❌ File not created (but no exception)")
                return False

        except Exception as e:
            print(f"❌ Failed with error: {type(e).__name__}: {e}")

            # Check if file was created despite the error
            json_file = Path(tmpdir) / "items.json"
            if json_file.exists():
                with open(json_file) as f:
                    data = json.load(f)
                print(
                    f"⚠️  File WAS created ({len(data)} items, {json_file.stat().st_size} bytes)"
                )
                print("   This means the agent succeeded but failed to report back!")
                return False
            else:
                print("   File was NOT created")
                return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("E2E Test: Large Response Handling")
    print("=" * 80)

    tests = [
        ("Small JSON (10 items)", test_small_json),
        ("Medium JSON (50 items)", test_medium_json),
        ("Large JSON (100 items)", test_large_json),
        ("Very Large JSON (200 items)", test_very_large_json),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback

            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")

    # Return exit code
    all_passed = all(success for _, success in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
