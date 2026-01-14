"""Tests for exception handling"""

import pytest
from auggie_sdk.exceptions import (
    AugmentError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
)


def test_augment_error():
    """Test base AugmentError"""
    error = AugmentError("Test error", status_code=500)
    assert str(error) == "Test error"
    assert error.status_code == 500


def test_authentication_error():
    """Test AuthenticationError"""
    error = AuthenticationError()
    assert error.status_code == 401
    assert "Authentication failed" in str(error)


def test_rate_limit_error():
    """Test RateLimitError"""
    error = RateLimitError(retry_after=60)
    assert error.status_code == 429
    assert error.retry_after == 60


def test_not_found_error():
    """Test NotFoundError"""
    error = NotFoundError("Project not found")
    assert error.status_code == 404
    assert "not found" in str(error)


def test_validation_error():
    """Test ValidationError"""
    error = ValidationError("Invalid input")
    assert error.status_code == 400
    assert "Invalid input" in str(error)
