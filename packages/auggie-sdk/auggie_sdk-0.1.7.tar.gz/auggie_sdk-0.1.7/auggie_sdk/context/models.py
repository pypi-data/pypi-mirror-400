"""
Types for the Context SDK.

These dataclasses define the API contracts for the SDK. They use snake_case
following Python conventions, with serialization helpers for API boundaries.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class File:
    """Represents a file with path and contents (source-agnostic)."""

    path: str  # Relative path (e.g., "src/main.py")
    contents: str  # File contents as string


@dataclass
class Chunk:
    """A single code chunk from the retrieval results."""

    path: str  # File path relative to workspace root
    start_line: int  # Starting line number (1-based)
    end_line: int  # Ending line number (1-based, inclusive)
    contents: str  # The code content


@dataclass
class SearchResult:
    """Result from a codebase search query."""

    formatted_retrieval: str  # Formatted retrieval results as markdown text
    chunks: List[Chunk]  # Structured list of code chunks


@dataclass
class BlobInfo:
    """Blob information for a file."""

    blob_name: str  # SHA-256 hash of the file path and contents
    relative_path: str  # Relative path from workspace root


# Blob entry in persistent state - tuple of [blobName, path]
BlobEntry = Tuple[str, str]


@dataclass
class Blobs:
    """Blobs payload for API requests."""

    checkpoint_id: Optional[str]  # Optional checkpoint ID from previous indexing
    added_blobs: List[str]  # List of added blob names
    deleted_blobs: List[str]  # List of deleted blob names

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to API-compatible dict."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "added_blobs": self.added_blobs,
            "deleted_blobs": self.deleted_blobs,
        }


@dataclass
class IndexingResult:
    """Result from addToIndex operation."""

    newly_uploaded: List[str]  # Paths that were newly uploaded to the backend
    already_uploaded: List[str]  # Paths that were already uploaded


@dataclass
class DirectContextState:
    """State for Direct Context that can be exported/imported."""

    checkpoint_id: Optional[str]  # Current checkpoint ID
    added_blobs: List[str]  # Array of blob names that have been added
    deleted_blobs: List[str]  # Array of blob names that have been deleted
    blobs: List[BlobEntry]  # List of blobs as [blobName, path] tuples

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "checkpointId": self.checkpoint_id,
            "addedBlobs": self.added_blobs,
            "deletedBlobs": self.deleted_blobs,
            "blobs": self.blobs,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DirectContextState":
        """Create from JSON dict (e.g., from imported state file)."""
        return cls(
            checkpoint_id=data.get("checkpointId"),
            added_blobs=data.get("addedBlobs", []),
            deleted_blobs=data.get("deletedBlobs", []),
            blobs=data.get("blobs", []),
        )

