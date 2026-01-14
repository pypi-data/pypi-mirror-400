"""
Blob name calculator for file hashing
"""

import hashlib
from typing import Optional, Union

BLOB_NAMING_VERSION = 2_023_102_300


class BlobTooLargeError(Exception):
    """Exception raised when a blob exceeds the maximum size."""

    def __init__(self, max_blob_size: int):
        super().__init__(f"content exceeds maximum size of {max_blob_size}")
        self.max_blob_size = max_blob_size


class BlobNameCalculator:
    """Calculator for generating blob names from file paths and contents."""

    def __init__(self, max_blob_size: int):
        self.max_blob_size = max_blob_size

    def _hash(self, path: str, contents: bytes) -> str:
        """Generate SHA-256 hash of path and contents."""
        hasher = hashlib.sha256()
        hasher.update(path.encode("utf-8"))
        hasher.update(contents)
        return hasher.hexdigest()

    def _to_bytes(self, contents: Union[str, bytes]) -> bytes:
        """Convert contents to bytes if necessary."""
        if isinstance(contents, str):
            return contents.encode("utf-8")
        return contents

    def calculate_or_throw(
        self, path: str, contents: Union[str, bytes], *, check_file_size: bool = True
    ) -> str:
        """
        Calculate blob name, raising an exception if the file is too large.

        Args:
            path: File path
            contents: File contents as string or bytes
            check_file_size: Whether to check file size limits (keyword-only)

        Returns:
            Blob name (SHA-256 hash)

        Raises:
            BlobTooLargeError: If file exceeds max_blob_size
        """
        contents_bytes = self._to_bytes(contents)

        if check_file_size and len(contents_bytes) > self.max_blob_size:
            raise BlobTooLargeError(self.max_blob_size)

        return self._hash(path, contents_bytes)

    def calculate(self, path: str, contents: Union[str, bytes]) -> Optional[str]:
        """
        Calculate blob name, returning None if the file is too large.

        Args:
            path: File path
            contents: File contents as string or bytes

        Returns:
            Blob name (SHA-256 hash) or None if file is too large
        """
        try:
            return self.calculate_or_throw(path, contents, check_file_size=True)
        except BlobTooLargeError:
            return None

    def calculate_unchecked(self, path: str, contents: Union[str, bytes]) -> str:
        """
        Calculate blob name without checking file size.

        Args:
            path: File path
            contents: File contents as string or bytes

        Returns:
            Blob name (SHA-256 hash)
        """
        return self.calculate_or_throw(path, contents, check_file_size=False)

