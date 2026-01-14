"""Augment SDK - Python client for Augment CLI agent"""

__version__ = "0.1.7"

from .agent import Agent, Auggie, Model, ModelType, VerificationResult
from .context import DirectContext, FileSystemContext
from .exceptions import (
    AugmentCLIError,
    AugmentError,
    AugmentJSONError,
    AugmentNotFoundError,
    AugmentParseError,
    AugmentVerificationError,
    AugmentWorkspaceError,
)
from .listener import AgentListener, LoggingAgentListener

__all__ = [
    # Main agent
    "Auggie",
    "Agent",  # Backward compatibility
    "Model",
    "ModelType",
    "VerificationResult",
    # Context (experimental)
    "DirectContext",
    "FileSystemContext",
    # Listeners
    "AgentListener",
    "LoggingAgentListener",
    # Exceptions
    "AugmentError",
    "AugmentCLIError",
    "AugmentJSONError",
    "AugmentNotFoundError",
    "AugmentParseError",
    "AugmentWorkspaceError",
    "AugmentVerificationError",
]
