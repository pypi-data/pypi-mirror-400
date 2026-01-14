"""
Version information for the Auggie Python SDK

This module provides the SDK version using importlib.metadata,
which reads from the installed package metadata.
"""

from importlib.metadata import PackageNotFoundError, version


def get_sdk_version() -> str:
    """
    Get the SDK version from installed package metadata.

    This function uses importlib.metadata to read the version from the
    installed package. This works reliably in both development (editable install)
    and production environments.

    Returns:
        The version string, or "unknown" if the package is not installed
    """
    try:
        return version("auggie-sdk")
    except PackageNotFoundError:
        return "unknown"

