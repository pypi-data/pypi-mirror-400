"""
API client for Context operations.

Handles both indexing endpoints and LLM chat endpoint.
"""

import json
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

from ..models import Blobs
from ..version import get_sdk_version
from .retry_utils import retry_chat, retry_with_backoff


class APIError(Exception):
    """
    Error raised when an API request fails.

    Includes the HTTP status code to enable retry logic for transient failures.
    """

    def __init__(self, status: int, status_text: str, message: str):
        super().__init__(message)
        self.status = status
        self.status_text = status_text


@dataclass
class UploadBlob:
    """Blob to upload to the backend."""

    blob_name: str
    path_name: str
    text: str
    metadata: List[str]


@dataclass
class FindMissingResult:
    """Result from findMissing API call."""

    unknown_blob_names: List[str]
    nonindexed_blob_names: List[str]


@dataclass
class CheckpointBlobsResult:
    """Result from checkpointBlobs API call."""

    new_checkpoint_id: str


@dataclass
class BatchUploadResult:
    """Result from batchUpload API call."""

    blob_names: List[str]


@dataclass
class AgentCodebaseRetrievalResult:
    """Result from agentCodebaseRetrieval API call."""

    formatted_retrieval: str


# Default timeout for HTTP requests in seconds.
# This is the (connect_timeout, read_timeout) tuple format accepted by the requests library.
DEFAULT_REQUEST_TIMEOUT = (10, 60)


@dataclass
class ContextAPIClientOptions:
    """Options for ContextAPIClient."""

    api_key: str
    api_url: str
    debug: bool = False
    # Timeout as (connect_timeout, read_timeout) in seconds
    timeout: tuple = DEFAULT_REQUEST_TIMEOUT


def _get_user_agent() -> str:
    """Get user agent string for Context API requests."""
    return f"augment.sdk.context/{get_sdk_version()} (python)"


class ContextAPIClient:
    """API client for Context operations."""

    def __init__(self, options: ContextAPIClientOptions):
        self.api_key = options.api_key
        self.api_url = options.api_url.rstrip("/")  # Normalize URL once
        self.session_id = str(uuid.uuid4())
        self.debug = options.debug
        self.timeout = options.timeout

    def _log(self, message: str) -> None:
        """Log a debug message if debug mode is enabled."""
        if self.debug:
            print(f"[ContextAPI] {message}")

    def _create_request_id(self) -> str:
        """Create a unique request ID."""
        return str(uuid.uuid4())

    def _call_api(
        self, endpoint: str, payload: Dict[str, Any], request_id: str
    ) -> Dict[str, Any]:
        """Make an API call to the backend."""
        url = f"{self.api_url}/{endpoint}"

        self._log(f"POST {url}")
        self._log(f"Request ID: {request_id}")
        self._log(f"Request: {json.dumps(payload, indent=2)}")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Request-Session-Id": self.session_id,
            "X-Request-Id": request_id,
            "User-Agent": _get_user_agent(),
        }

        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)

        if not response.ok:
            raise APIError(
                response.status_code,
                response.reason,
                f"API request failed: {response.status_code} {response.reason} - {response.text}",
            )

        result = response.json()
        self._log(f"Response: {json.dumps(result, indent=2)}")
        return result

    def _call_api_with_retry(
        self, endpoint: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call API with automatic retry logic and stable request ID across retries."""
        request_id = self._create_request_id()
        return retry_with_backoff(
            lambda: self._call_api(endpoint, payload, request_id), self.debug
        )

    def find_missing(self, blob_names: List[str]) -> FindMissingResult:
        """Find which blobs are missing or not yet indexed on the server."""
        result = self._call_api_with_retry("find-missing", {"mem_object_names": blob_names})

        return FindMissingResult(
            unknown_blob_names=result.get("unknown_memory_names", []),
            nonindexed_blob_names=result.get("nonindexed_blob_names", []),
        )

    def batch_upload(self, blobs: List[UploadBlob]) -> BatchUploadResult:
        """Upload blobs to the backend."""
        payload = {
            "blobs": [
                {"blob_name": blob.blob_name, "path": blob.path_name, "content": blob.text}
                for blob in blobs
            ]
        }

        result = self._call_api_with_retry("batch-upload", payload)
        return BatchUploadResult(blob_names=result.get("blob_names", []))

    def checkpoint_blobs(self, blobs: Blobs) -> CheckpointBlobsResult:
        """Create a checkpoint of the current blob set."""
        payload = {
            "blobs": {
                "checkpoint_id": blobs.checkpoint_id,
                "added_blobs": blobs.added_blobs,
                "deleted_blobs": blobs.deleted_blobs,
            }
        }

        result = self._call_api_with_retry("checkpoint-blobs", payload)
        return CheckpointBlobsResult(new_checkpoint_id=result["new_checkpoint_id"])

    def agent_codebase_retrieval(
        self,
        query: str,
        blobs: Blobs,
        max_output_length: Optional[int] = None,
    ) -> AgentCodebaseRetrievalResult:
        """Perform codebase retrieval using the agent API."""
        payload: Dict[str, Any] = {
            "information_request": query,
            "blobs": {
                "checkpoint_id": blobs.checkpoint_id,
                "added_blobs": blobs.added_blobs,
                "deleted_blobs": blobs.deleted_blobs,
            },
            "dialog": [],
        }

        if max_output_length is not None:
            payload["max_output_length"] = max_output_length

        result = self._call_api_with_retry("agents/codebase-retrieval", payload)
        return AgentCodebaseRetrievalResult(formatted_retrieval=result["formatted_retrieval"])

    def _parse_stream_line(self, line: str) -> Optional[str]:
        """Parse a single JSON line from the stream and extract text if present."""
        trimmed = line.strip()
        if not trimmed:
            return None

        try:
            parsed = json.loads(trimmed)
            return parsed.get("text")
        except json.JSONDecodeError:
            self._log(f"Failed to parse stream line: {trimmed}")
            return None

    def _parse_sse_stream(self, response: requests.Response) -> str:
        """Parse streaming response and accumulate text chunks."""
        chunks: List[str] = []

        for line in response.iter_lines(decode_unicode=True):
            if line:
                text = self._parse_stream_line(line)
                if text:
                    chunks.append(text)

        return "".join(chunks)

    def _chat_request(self, prompt: str, request_id: str) -> str:
        """
        Make a chat request (used by retry logic).

        Args:
            prompt: The formatted prompt to send to the LLM
            request_id: The request ID to use for this request

        Returns:
            The LLM's response text
        """
        url = f"{self.api_url}/chat-stream"

        self._log(f"POST {url}")
        self._log(f"Request ID: {request_id}")

        # Use nodes array format for chat-stream (newer API format)
        # Note: type is an integer enum where 0 = TEXT node
        payload = {
            "nodes": [
                {
                    "id": 0,
                    "type": 0,  # ChatRequestNodeType.TEXT = 0
                    "text_node": {"content": prompt},
                }
            ],
            "chat_history": [],
            "conversation_id": self.session_id,
        }

        self._log(f"Request: {json.dumps(payload, indent=2)}")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Request-Session-Id": self.session_id,
            "X-Request-Id": request_id,
            "conversation-id": self.session_id,
            "X-Mode": "sdk",
            "User-Agent": _get_user_agent(),
        }

        response = requests.post(
            url, json=payload, headers=headers, stream=True, timeout=self.timeout
        )

        if not response.ok:
            raise APIError(
                response.status_code,
                response.reason,
                f"API request failed: {response.status_code} {response.reason} - {response.text}",
            )

        accumulated_text = self._parse_sse_stream(response)

        self._log(f"Response: {accumulated_text}")
        return accumulated_text

    def chat(self, prompt: str) -> str:
        """
        Call the LLM chat streaming API with a formatted prompt.

        This method includes automatic retry logic for transient failures,
        including chat-specific status codes like 429 (rate limit) and 529 (overloaded).

        Args:
            prompt: The formatted prompt to send to the LLM

        Returns:
            The LLM's response text
        """
        request_id = self._create_request_id()
        return retry_chat(
            lambda: self._chat_request(prompt, request_id), self.debug
        )

