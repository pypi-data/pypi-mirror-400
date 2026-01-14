"""
Direct Context - API-based indexing with import/export state

This class provides explicit file indexing via API calls with the ability
to export and restore state to avoid re-indexing between sessions.

## Creating a Context

**Start fresh:**
```python
context = DirectContext.create()
```

**Restore from saved state:**
```python
context = DirectContext.import_from_file("state.json")
# or
context = DirectContext.import_state(state_object)
```

## Indexing Flow

Files are uploaded to the backend and then indexed asynchronously. You have
explicit control over when to wait for indexing:

**Option 1: Wait after each upload**
```python
context.add_to_index(files)  # waits for indexing by default
context.search("query")      # files are already indexed
```

**Option 2: Batch uploads then wait**
```python
context.add_to_index(files1, wait_for_indexing=False)
context.add_to_index(files2, wait_for_indexing=False)
context.wait_for_indexing()  # wait for all files to be indexed
context.search("query")      # files are now indexed
```

Note: `search()` and `search_and_ask()` do not wait for indexing automatically.

## State Persistence

**Export state:**
```python
state = context.export()
# or save to file
context.export_to_file("state.json")
```

**Import state:**
```python
context = DirectContext.import_from_file("state.json")
```
"""

import json
import time
from typing import Dict, List, Optional, Set

from .internal.api_client import ContextAPIClient, ContextAPIClientOptions, UploadBlob
from .internal.blob_name_calculator import BlobNameCalculator
from .internal.credentials import CredentialOptions, resolve_credentials

from .internal.search_utils import format_search_prompt
from .models import (
    Blobs,
    DirectContextState,
    File,
    IndexingResult,
)


class DirectContext:
    """Direct Context - API-based indexing with import/export state."""

    MAX_FILE_SIZE_BYTES = 1_048_576  # 1MB
    MAX_BATCH_UPLOAD_SIZE = 1000
    MAX_BATCH_CONTENT_BYTES = 2 * 1024 * 1024  # 2MB
    MAX_FIND_MISSING_SIZE = 1000
    CHECKPOINT_THRESHOLD = 1000

    def __init__(self, api_key: str, api_url: str, debug: bool = False):
        """
        Private constructor - use DirectContext.create() instead.

        Args:
            api_key: API key for authentication.
            api_url: API URL for the tenant.
            debug: Enable debug logging.
        """
        self.debug = debug

        # Initialize API client
        self.api_client = ContextAPIClient(
            ContextAPIClientOptions(api_key=api_key, api_url=api_url, debug=debug)
        )

        # Initialize blob calculator
        self.blob_calculator = BlobNameCalculator(self.MAX_FILE_SIZE_BYTES)

        # State management
        self.blob_map: Dict[str, str] = {}  # path -> blobName
        self.checkpoint_id: Optional[str] = None
        self.pending_added: Set[str] = set()
        self.pending_deleted: Set[str] = set()

    @classmethod
    def create(
        cls,
        *,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        debug: bool = False,
    ) -> "DirectContext":
        """
        Create and initialize a new DirectContext instance.

        Authentication priority:
            1. api_key / api_url parameters
            2. AUGMENT_API_TOKEN / AUGMENT_API_URL environment variables
            3. ~/.augment/session.json (created by `auggie login`)

        Args:
            api_key: API key for authentication.
            api_url: API URL for your Augment tenant.
            debug: Enable debug logging to console.

        Returns:
            A DirectContext instance.
        """
        cred_options = CredentialOptions(api_key=api_key, api_url=api_url)
        credentials = resolve_credentials(cred_options)
        return cls(credentials.api_key, credentials.api_url, debug)

    @classmethod
    def import_state(
        cls,
        state: DirectContextState,
        *,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        debug: bool = False,
    ) -> "DirectContext":
        """
        Import a DirectContext instance from a saved state object.

        Args:
            state: The state object to restore from.
            api_key: API key for authentication.
            api_url: API URL for your Augment tenant.
            debug: Enable debug logging to console.

        Returns:
            A DirectContext instance with restored state.
        """
        cred_options = CredentialOptions(api_key=api_key, api_url=api_url)
        credentials = resolve_credentials(cred_options)
        instance = cls(credentials.api_key, credentials.api_url, debug)
        instance._do_import(state)
        return instance

    @classmethod
    def import_from_file(
        cls,
        file_path: str,
        *,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        debug: bool = False,
    ) -> "DirectContext":
        """
        Import a DirectContext instance from a saved state file.

        Args:
            file_path: Path to the state file.
            api_key: API key for authentication.
            api_url: API URL for your Augment tenant.
            debug: Enable debug logging to console.

        Returns:
            A DirectContext instance with restored state.
        """
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        state = DirectContextState.from_dict(data)
        return cls.import_state(state, api_key=api_key, api_url=api_url, debug=debug)

    def log(self, message: str) -> None:
        """Log a debug message if debug mode is enabled"""
        if self.debug:
            print(f"[DirectContext] {message}")

    def _maybe_checkpoint(self) -> None:
        """Create a checkpoint if threshold is reached"""
        pending_changes = len(self.pending_added) + len(self.pending_deleted)

        if pending_changes < self.CHECKPOINT_THRESHOLD:
            self.log(
                f"Skipping checkpoint: {pending_changes} pending changes "
                f"(threshold: {self.CHECKPOINT_THRESHOLD})"
            )
            return

        # Get blob names for checkpoint
        added_blobs = sorted(list(self.pending_added))
        deleted_blobs = sorted(list(self.pending_deleted))

        self.log(
            f"Creating checkpoint: {len(added_blobs)} added, {len(deleted_blobs)} deleted blobs"
        )

        blobs = Blobs(
            checkpoint_id=self.checkpoint_id,
            added_blobs=added_blobs,
            deleted_blobs=deleted_blobs,
        )

        result = self.api_client.checkpoint_blobs(blobs)
        self.checkpoint_id = result.new_checkpoint_id
        self.log(f"Checkpoint created: {self.checkpoint_id}")

        # Clear pending changes after successful checkpoint
        self.pending_added.clear()
        self.pending_deleted.clear()

    def get_indexed_paths(self) -> List[str]:
        """Get the list of indexed file paths"""
        return list(self.blob_map.keys())

    def _find_missing_blobs(
        self, blob_names: List[str], include_non_indexed: bool = False
    ) -> List[str]:
        """
        Check which blobs are missing or not yet indexed on the server

        Args:
            blob_names: Array of blob names to check
            include_non_indexed: If true, includes blobs that are uploaded but not yet indexed

        Returns:
            Array of blob names that are either missing or not indexed
        """
        all_missing: List[str] = []

        for i in range(0, len(blob_names), self.MAX_FIND_MISSING_SIZE):
            batch = blob_names[i : i + self.MAX_FIND_MISSING_SIZE]
            result = self.api_client.find_missing(batch)

            all_missing.extend(result.unknown_blob_names)

            if include_non_indexed:
                all_missing.extend(result.nonindexed_blob_names)

        return all_missing

    def _batch_upload_files(self, files_to_upload: List[UploadBlob]) -> None:
        """Upload files in batches respecting backend limits"""
        batches: List[List[UploadBlob]] = []
        current_batch: List[UploadBlob] = []
        current_batch_size = 0

        for file in files_to_upload:
            file_size = len(file.text.encode("utf-8"))

            would_exceed_count = len(current_batch) >= self.MAX_BATCH_UPLOAD_SIZE
            would_exceed_size = current_batch_size + file_size > self.MAX_BATCH_CONTENT_BYTES

            if would_exceed_count or would_exceed_size:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [file]
                current_batch_size = file_size
            else:
                current_batch.append(file)
                current_batch_size += file_size

        if current_batch:
            batches.append(current_batch)

        for batch in batches:
            self.api_client.batch_upload(batch)

    def _validate_file_sizes(self, files: List[File]) -> None:
        """Validate that all files are within size limits"""
        for file in files:
            size_bytes = len(file.contents.encode("utf-8"))
            if size_bytes > self.MAX_FILE_SIZE_BYTES:
                raise ValueError(
                    f"File {file.path} is too large ({size_bytes} bytes). "
                    f"Maximum size is {self.MAX_FILE_SIZE_BYTES} bytes (1MB)."
                )

    def _prepare_blobs_for_upload(self, files: List[File]) -> dict:
        """
        Calculate blob names and prepare upload data for files
        Returns files that need uploading, new blob entries, and already uploaded files
        """
        files_to_upload: List[UploadBlob] = []
        new_blob_entries: List[tuple] = []  # [(path, blobName), ...]
        already_uploaded: List[str] = []

        for file in files:
            blob_name = self.blob_calculator.calculate(file.path, file.contents)
            if blob_name:
                existing_blob_name = self.blob_map.get(file.path)
                if existing_blob_name and existing_blob_name == blob_name:
                    # File content hasn't changed
                    already_uploaded.append(file.path)
                    continue

                # Handle file replacement
                if existing_blob_name:
                    self._handle_blob_replacement(existing_blob_name)

                new_blob_entries.append((file.path, blob_name))
                files_to_upload.append(
                    UploadBlob(
                        blob_name=blob_name,
                        path_name=file.path,
                        text=file.contents,
                        metadata=[],
                    )
                )

        return {
            "filesToUpload": files_to_upload,
            "newBlobEntries": new_blob_entries,
            "alreadyUploaded": already_uploaded,
        }

    def _handle_blob_replacement(self, old_blob_name: str) -> None:
        """Handle replacing an existing blob (track deletion of old blob)"""
        # Check if the old blob is in pending_added
        if old_blob_name in self.pending_added:
            # Old blob was added in this session, just remove it from pending_added
            self.pending_added.discard(old_blob_name)
        else:
            # Old blob was from a previous checkpoint, add to deleted_blobs
            self.pending_deleted.add(old_blob_name)

    def _categorize_files(
        self, new_blob_entries: List[tuple], missing_blob_set: Set[str]
    ) -> dict:
        """
        Categorize files into newly uploaded vs already on server based on server response
        """
        newly_uploaded: List[str] = []
        already_on_server: List[str] = []

        for path, blob_name in new_blob_entries:
            if blob_name in missing_blob_set:
                newly_uploaded.append(path)
            else:
                already_on_server.append(path)

        return {"newlyUploaded": newly_uploaded, "alreadyOnServer": already_on_server}

    def _do_add_to_index(self, files: List[File]) -> IndexingResult:
        """Internal implementation of add_to_index"""
        self.log(f"Adding {len(files)} files to index")

        # Validate file sizes
        self._validate_file_sizes(files)

        # Calculate blob names and prepare uploads
        prep_result = self._prepare_blobs_for_upload(files)
        files_to_upload = prep_result["filesToUpload"]
        new_blob_entries = prep_result["newBlobEntries"]
        already_uploaded = prep_result["alreadyUploaded"]

        if not new_blob_entries:
            return IndexingResult(newly_uploaded=[], already_uploaded=already_uploaded)

        # Check which blobs the server already has
        blob_names_to_check = [blob_name for _, blob_name in new_blob_entries]
        self.log(f"Checking {len(blob_names_to_check)} blobs with server")
        missing_blob_names = self._find_missing_blobs(blob_names_to_check)
        missing_blob_set = set(missing_blob_names)
        self.log(f"Server is missing {len(missing_blob_names)} blobs")

        # Categorize files
        categorized = self._categorize_files(new_blob_entries, missing_blob_set)
        newly_uploaded = categorized["newlyUploaded"]
        already_on_server = categorized["alreadyOnServer"]

        # Upload only missing files
        files_to_actually_upload = [
            file for file in files_to_upload if file.blob_name in missing_blob_set
        ]

        if files_to_actually_upload:
            self.log(f"Uploading {len(files_to_actually_upload)} files to backend")
            self._batch_upload_files(files_to_actually_upload)
            self.log("Upload complete")

        # Update blob tracking state
        for path, blob_name in new_blob_entries:
            self.pending_added.add(blob_name)
            self.pending_deleted.discard(blob_name)
            self.blob_map[path] = blob_name

        self._maybe_checkpoint()

        return IndexingResult(
            newly_uploaded=newly_uploaded,
            already_uploaded=already_uploaded + already_on_server,
        )

    def _wait_for_specific_blobs(self, blob_names: List[str]) -> None:
        """
        Wait for specific blobs to be indexed on the backend.
        """
        if not blob_names:
            self.log("No blobs to wait for")
            return

        self.log(f"Waiting for {len(blob_names)} blobs to be indexed on backend")

        # Timing constants (in seconds for cleaner Python code)
        initial_poll_interval = 3.0
        backoff_threshold = 60.0
        backoff_poll_interval = 60.0
        max_wait_time = 600.0  # 10 minutes

        start_time = time.monotonic()

        while True:
            # Check for blobs that are not yet indexed
            still_pending = self._find_missing_blobs(blob_names, include_non_indexed=True)

            if not still_pending:
                self.log("All blobs indexed successfully")
                return

            elapsed = time.monotonic() - start_time
            self.log(
                f"Still waiting for {len(still_pending)} blobs to be indexed "
                f"(elapsed: {elapsed:.0f}s)"
            )

            if elapsed >= max_wait_time:
                raise TimeoutError(
                    f"Indexing timeout: Backend did not finish indexing within "
                    f"{max_wait_time:.0f} seconds"
                )

            poll_interval = (
                initial_poll_interval
                if elapsed < backoff_threshold
                else backoff_poll_interval
            )

            time.sleep(poll_interval)

    def add_to_index(
        self, files: List[File], wait_for_indexing: bool = True
    ) -> IndexingResult:
        """
        Add files to the index by uploading them to the backend.

        By default, this method waits for the uploaded files to be fully indexed
        on the backend before returning. Set `wait_for_indexing=False` to return
        immediately after upload completes (indexing will continue asynchronously).

        Args:
            files: Array of files to add to the index
            wait_for_indexing: If True (default), waits for newly added files to be indexed

        Returns:
            Result indicating which files were newly uploaded vs already uploaded
        """
        result = self._do_add_to_index(files)

        if wait_for_indexing and result.newly_uploaded:
            # Wait for the newly uploaded files to be indexed
            newly_uploaded_blob_names = [
                self.blob_map[path]
                for path in result.newly_uploaded
                if path in self.blob_map
            ]
            self._wait_for_specific_blobs(newly_uploaded_blob_names)

        return result

    def _do_remove_from_index(self, paths: List[str]) -> None:
        """Internal implementation of remove_from_index"""
        for path in paths:
            blob_name = self.blob_map.get(path)
            if blob_name:
                if blob_name in self.pending_added:
                    self.pending_added.discard(blob_name)
                else:
                    self.pending_deleted.add(blob_name)
                del self.blob_map[path]

        self._maybe_checkpoint()

    def remove_from_index(self, paths: List[str]) -> None:
        """Remove paths from the index"""
        self._do_remove_from_index(paths)

    def _do_clear_index(self) -> None:
        """Internal implementation of clear_index"""
        self.log(f"Clearing index ({len(self.blob_map)} files)")

        self.checkpoint_id = None
        self.blob_map.clear()
        self.pending_added.clear()
        self.pending_deleted.clear()

        self.log("Index cleared")

    def clear_index(self) -> None:
        """Clear the entire index"""
        self._do_clear_index()

    def wait_for_indexing(self) -> None:
        """
        Wait for all indexed files to be fully indexed on the backend.

        This method polls the backend until all files that have been added to the index
        are confirmed to be indexed and searchable.

        Raises:
            TimeoutError: If indexing times out (default: 10 minutes)
        """
        blob_names = list(self.blob_map.values())
        self._wait_for_specific_blobs(blob_names)

    def search(self, query: str, max_output_length: Optional[int] = None) -> str:
        """
        Search the codebase using natural language and return formatted results.

        The results are returned as a formatted string designed for use in LLM prompts.
        The format includes file paths, line numbers, and code content in a structured,
        readable format that can be passed directly to LLM APIs.

        Note: This method does not wait for indexing. Ensure files are indexed before
        searching by either:
        - Using `add_to_index()` with `wait_for_indexing=True` (default)
        - Calling `wait_for_indexing()` explicitly before searching

        Args:
            query: The search query describing what code you're looking for
            max_output_length: Maximum character length of the formatted output
                              (default: 20000, max: 80000)

        Returns:
            A formatted string containing the search results, ready for LLM consumption
        """
        self.log(f'Searching for: "{query}"')

        if not self.blob_map:
            raise ValueError(
                "Index not initialized. Add files to index first using add_to_index()."
            )

        blobs = Blobs(
            checkpoint_id=self.checkpoint_id,
            added_blobs=sorted(list(self.pending_added)),
            deleted_blobs=sorted(list(self.pending_deleted)),
        )

        self.log(
            f"Executing search with checkpoint {self.checkpoint_id or '(none)'}, "
            f"{len(self.blob_map)} indexed files"
        )

        result = self.api_client.agent_codebase_retrieval(
            query, blobs, max_output_length
        )

        self.log("Search completed successfully")

        return result.formatted_retrieval

    def search_and_ask(self, search_query: str, prompt: Optional[str] = None) -> str:
        """
        Search the indexed codebase and ask an LLM a question about the results.

        This is a convenience method that combines search() with an LLM call to answer
        questions about your codebase.

        Note: This method does not wait for indexing. Ensure files are indexed before
        searching by either:
        - Using `add_to_index()` with `wait_for_indexing=True` (default)
        - Calling `wait_for_indexing()` explicitly before searching

        Args:
            search_query: The semantic search query to find relevant code
            prompt: Optional prompt to ask the LLM. If not provided, search_query is used.

        Returns:
            The LLM's answer to your question

        Example:
            ```python
            answer = context.search_and_ask(
                "How does the authentication flow work?"
            )
            print(answer)
            ```
        """
        results = self.search(search_query)
        llm_prompt = format_search_prompt(prompt or search_query, results)

        return self.api_client.chat(llm_prompt)

    def export(self) -> DirectContextState:
        """Export the current state to a dataclass object"""
        # Convert blob_map to array of [blobName, path] tuples
        blobs = [(blob_name, path) for path, blob_name in self.blob_map.items()]

        return DirectContextState(
            checkpoint_id=self.checkpoint_id,
            added_blobs=sorted(self.pending_added),
            deleted_blobs=sorted(self.pending_deleted),
            blobs=sorted(blobs),
        )

    def _do_import(self, state: DirectContextState) -> None:
        """Internal method to import state from a DirectContextState object"""
        self.checkpoint_id = state.checkpoint_id
        self.blob_map.clear()
        self.pending_added.clear()
        self.pending_deleted.clear()

        # Restore blob_map from blobs array [blobName, path]
        for blob_name, path in state.blobs:
            self.blob_map[path] = blob_name

        # Restore pending added blobs
        if state.added_blobs:
            self.pending_added = set(state.added_blobs)

        # Restore pending deleted blobs
        if state.deleted_blobs:
            self.pending_deleted = set(state.deleted_blobs)

        self.log(
            f"State imported: checkpoint {self.checkpoint_id}, "
            f"{len(self.blob_map)} files, {len(self.pending_added)} pending added, "
            f"{len(self.pending_deleted)} pending deleted"
        )

    def export_to_file(self, file_path: str) -> None:
        """Export state to a file"""
        state = self.export()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2)
        self.log(f"State saved to {file_path}")

