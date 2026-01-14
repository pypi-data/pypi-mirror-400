"""
Tests for the success criteria verification loop.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from auggie_sdk import Auggie, VerificationResult
from auggie_sdk.exceptions import AugmentParseError, AugmentVerificationError


class TestSuccessCriteriaLoop:
    """Test the iterative verification loop for success criteria."""

    def test_verification_result_dataclass(self):
        """Test that VerificationResult can be created."""
        result = VerificationResult(
            all_criteria_met=True,
            unmet_criteria=[],
            issues=[],
            overall_assessment="All good",
        )
        assert result.all_criteria_met is True
        assert result.unmet_criteria == []
        assert result.issues == []
        assert result.overall_assessment == "All good"

    def test_verification_result_with_issues(self):
        """Test VerificationResult with unmet criteria."""
        result = VerificationResult(
            all_criteria_met=False,
            unmet_criteria=[1, 3],
            issues=["Missing type hints", "No docstring"],
            overall_assessment="Needs work",
        )
        assert result.all_criteria_met is False
        assert result.unmet_criteria == [1, 3]
        assert len(result.issues) == 2

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_success_criteria_passes_first_round(self, mock_client_class):
        """Test that success criteria verification passes on first round."""
        # Setup mock client
        mock_client = Mock()
        mock_client.is_running = False
        mock_client.send_message = Mock(
            side_effect=[
                # First call: task execution
                "<augment-agent-result>\nTask completed\n</augment-agent-result>",
                # Second call: verification (all criteria met)
                """<augment-agent-result>
{
    "all_criteria_met": true,
    "unmet_criteria": [],
    "issues": [],
    "overall_assessment": "All criteria satisfied"
}
</augment-agent-result>""",
            ]
        )
        mock_client_class.return_value = mock_client

        agent = Auggie()

        # Run with success criteria
        agent.run(
            "Do the task",
            success_criteria=["Criterion 1", "Criterion 2"],
            max_verification_rounds=3,
        )

        # Should have called send_message twice (task + verification)
        assert mock_client.send_message.call_count == 2

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_success_criteria_fails_then_passes(self, mock_client_class):
        """Test that verification fails first, then passes after fix."""
        # Setup mock client
        mock_client = Mock()
        mock_client.is_running = False
        mock_client.send_message = Mock(
            side_effect=[
                # Round 1: task execution
                "<augment-agent-result>\nTask completed\n</augment-agent-result>",
                # Round 1: verification (fails)
                """<augment-agent-result>
{
    "all_criteria_met": false,
    "unmet_criteria": [1],
    "issues": ["Missing type hints"],
    "overall_assessment": "Needs type hints"
}
</augment-agent-result>""",
                # Round 2: fix execution
                "<augment-agent-result>\nFixed\n</augment-agent-result>",
                # Round 2: verification (passes)
                """<augment-agent-result>
{
    "all_criteria_met": true,
    "unmet_criteria": [],
    "issues": [],
    "overall_assessment": "All good now"
}
</augment-agent-result>""",
            ]
        )
        mock_client_class.return_value = mock_client

        agent = Auggie()

        # Run with success criteria
        agent.run(
            "Do the task",
            success_criteria=["Has type hints"],
            max_verification_rounds=3,
        )

        # Should have called send_message 4 times (task + verify + fix + verify)
        assert mock_client.send_message.call_count == 4

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_success_criteria_max_rounds_exceeded(self, mock_client_class):
        """Test that we raise exception after max_verification_rounds."""
        # Setup mock client that always fails verification
        mock_client = Mock()
        mock_client.is_running = False

        responses = []
        for i in range(10):  # More than max_verification_rounds
            responses.append(
                "<augment-agent-result>\nTask attempt\n</augment-agent-result>"
            )
            responses.append("""<augment-agent-result>
{
    "all_criteria_met": false,
    "unmet_criteria": [1],
    "issues": ["Still not fixed"],
    "overall_assessment": "Not done yet"
}
</augment-agent-result>""")

        mock_client.send_message = Mock(side_effect=responses)
        mock_client_class.return_value = mock_client

        agent = Auggie()

        # Run with success criteria and max 3 rounds - should raise exception
        with pytest.raises(AugmentVerificationError) as exc_info:
            agent.run(
                "Do the task",
                success_criteria=["Must be perfect"],
                max_verification_rounds=3,
            )

        # Check exception details
        assert exc_info.value.unmet_criteria == [1]
        assert "Still not fixed" in exc_info.value.issues
        assert exc_info.value.rounds_attempted == 3

        # Should have called send_message 6 times (3 rounds * 2 calls each)
        assert mock_client.send_message.call_count == 6

    @patch("auggie_sdk.agent.AuggieACPClient")
    def test_no_success_criteria_skips_verification(self, mock_client_class):
        """Test that without success_criteria, no verification happens."""
        # Setup mock client
        mock_client = Mock()
        mock_client.is_running = False
        mock_client.send_message = Mock(
            return_value="<augment-agent-result>\nDone\n</augment-agent-result>"
        )
        mock_client_class.return_value = mock_client

        agent = Auggie()

        # Run without success criteria
        agent.run("Do the task")

        # Should have called send_message only once (no verification)
        assert mock_client.send_message.call_count == 1

    def test_prepare_fix_instruction(self):
        """Test that fix instruction is properly formatted."""
        agent = Auggie()

        success_criteria = ["Has type hints", "Has docstring", "Handles errors"]

        verification = VerificationResult(
            all_criteria_met=False,
            unmet_criteria=[1, 2],
            issues=["Missing type hints on parameter x", "No docstring present"],
            overall_assessment="Incomplete implementation",
        )

        fix_instruction = agent._prepare_fix_instruction(success_criteria, verification)

        # Check that fix instruction contains the right information
        assert "1. Has type hints" in fix_instruction
        assert "2. Has docstring" in fix_instruction
        assert "3. Handles errors" not in fix_instruction  # This one was met
        assert "Missing type hints on parameter x" in fix_instruction
        assert "No docstring present" in fix_instruction
        assert "Incomplete implementation" in fix_instruction
