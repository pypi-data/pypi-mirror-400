"""
FileSystem Context - Local directory retrieval via MCP protocol.

This class spawns `auggie --mcp` and communicates with it via the MCP protocol
to provide codebase retrieval from a local directory.
"""

import json
import os
import subprocess
from typing import Any, Dict, Optional

from .internal.api_client import ContextAPIClient, ContextAPIClientOptions
from .internal.credentials import resolve_credentials
from .internal.search_utils import format_search_prompt


class FileSystemContext:
    """FileSystem Context - Local directory retrieval via MCP protocol."""

    def __init__(
        self,
        directory: str,
        auggie_path: str = "auggie",
        debug: bool = False,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
    ):
        """
        Create a new FileSystemContext instance.

        Args:
            directory: Path to the workspace directory to index (required).
            auggie_path: Path to auggie executable (default: "auggie").
            debug: Enable debug logging.
            api_key: API key for authentication.
            api_url: API URL for the tenant.
        """
        self.auggie_path = auggie_path
        self.directory = directory
        self.debug = debug
        self.api_key = api_key
        self.api_url = api_url

        self.mcp_process: Optional[subprocess.Popen[str]] = None
        self.api_client: Optional[ContextAPIClient] = None

    @classmethod
    def create(
        cls,
        directory: str,
        *,
        auggie_path: str = "auggie",
        debug: bool = False,
    ) -> "FileSystemContext":
        """
        Create and initialize a new FileSystemContext instance.

        Args:
            directory: Path to the workspace directory to index (required).
            auggie_path: Path to auggie executable (default: "auggie").
            debug: Enable debug logging.

        Returns:
            A FileSystemContext instance.
        """
        # Resolve credentials, but allow them to be undefined for FileSystemContext
        # since search_and_ask is optional functionality
        api_key: Optional[str] = None
        api_url: Optional[str] = None
        try:
            credentials = resolve_credentials()
            api_key = credentials.api_key
            api_url = credentials.api_url
        except ValueError:
            # Credentials are optional for FileSystemContext
            # They're only required if search_and_ask() is called
            pass

        instance = cls(directory, auggie_path, debug, api_key, api_url)
        instance._connect()
        return instance

    def _log(self, message: str) -> None:
        """Log a debug message if debug mode is enabled."""
        if self.debug:
            print(f"[FileSystemContext] {message}")

    def _connect(self) -> None:
        """Connect to Auggie MCP server."""
        self._log(f"Starting MCP server for directory: {self.directory}")

        command = self.auggie_path.strip()
        if not command:
            raise ValueError("Invalid auggiePath: cannot be empty")

        args = [command, "--mcp", "--workspace-root", self.directory]

        # Build environment variables
        env = os.environ.copy()
        if self.api_key:
            env["AUGMENT_API_TOKEN"] = self.api_key
        if self.api_url:
            env["AUGMENT_API_URL"] = self.api_url

        # Start the MCP process
        # When not debugging, redirect stderr to DEVNULL to prevent pipe buffer deadlock
        # (if auggie writes too much to stderr it can block while waiting for the buffer to drain)
        self.mcp_process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=None if self.debug else subprocess.DEVNULL,
            env=env,
            text=True,
            bufsize=1,
        )

        self._log("Connected to Auggie MCP server")

    def _call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool and return the result.

        Args:
            tool_name: Name of the tool to call.
            params: Parameters to pass to the tool.

        Returns:
            The tool's response.

        Raises:
            RuntimeError: If the MCP process is not running or the call fails.
        """
        if not self.mcp_process or not self.mcp_process.stdin or not self.mcp_process.stdout:
            raise RuntimeError("MCP process not initialized. Call create() first.")

        # Check if process is still alive
        if self.mcp_process.poll() is not None:
            # Process has terminated, try to get error output
            stderr_output = ""
            if self.mcp_process.stderr:
                stderr_output = self.mcp_process.stderr.read()
            raise RuntimeError(
                f"MCP process terminated unexpectedly with exit code {self.mcp_process.returncode}. "
                f"stderr: {stderr_output}"
            )

        # Construct MCP request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": params},
        }

        # Send request
        try:
            request_json = json.dumps(request) + "\n"
            self.mcp_process.stdin.write(request_json)
            self.mcp_process.stdin.flush()
        except BrokenPipeError as e:
            # Process died while we were writing
            stderr_output = ""
            if self.mcp_process.stderr:
                try:
                    stderr_output = self.mcp_process.stderr.read()
                except Exception:
                    pass
            raise RuntimeError(
                f"MCP process closed while sending request (broken pipe). "
                f"Exit code: {self.mcp_process.poll()}. stderr: {stderr_output}"
            ) from e

        # Read response
        response_line = self.mcp_process.stdout.readline()
        if not response_line:
            raise RuntimeError("MCP process closed unexpectedly")

        response = json.loads(response_line)

        if "error" in response:
            raise RuntimeError(f"MCP tool call failed: {response['error']}")

        return response.get("result", {})

    def search(self, query: str) -> str:
        """
        Search the codebase using natural language and return formatted results.

        The results are returned as a formatted string designed for use in LLM prompts.
        The format includes file paths, line numbers, and code content in a structured,
        readable format that can be passed directly to LLM APIs.

        Args:
            query: The search query describing what code you're looking for.

        Returns:
            A formatted string containing the search results, ready for LLM consumption.

        Example:
            ```python
            from auggie_sdk.context import FileSystemContext
            context = FileSystemContext.create("./my-project")
            results = context.search("authentication logic")
            print(results)  # Formatted string with file paths, line numbers, and code
            ```
        """
        self._log(f'Searching for: "{query}"')

        try:
            # Call the codebase-retrieval tool via MCP
            result = self._call_mcp_tool("codebase-retrieval", {"information_request": query})

            # Extract text from MCP result (standard MCP format)
            if "content" not in result or not isinstance(result["content"], list):
                raise RuntimeError(
                    f"Unexpected MCP response format: expected {{'content': [...]}}, "
                    f"got {json.dumps(result)}"
                )

            text = "\n".join(
                item.get("text", "")
                for item in result["content"]
                if item.get("type") == "text"
            )

            self._log(f"Search completed ({len(text)} characters)")

            return text
        except Exception as e:
            raise RuntimeError(
                f"Codebase retrieval failed: {e if isinstance(e, str) else str(e)}"
            ) from e

    def search_and_ask(self, search_query: str, prompt: Optional[str] = None) -> str:
        """
        Search the indexed codebase and ask an LLM a question about the results.

        This is a convenience method that combines search() with an LLM call to answer
        questions about your codebase.

        Args:
            search_query: The semantic search query to find relevant code.
            prompt: Optional prompt to ask the LLM. If not provided, search_query is used.

        Returns:
            The LLM's answer to your question.

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

        # Lazy initialization of API client
        if not self.api_client:
            if not (self.api_key and self.api_url):
                raise ValueError(
                    "API credentials are required for search_and_ask(). Provide them via:\n"
                    "1. AUGMENT_API_TOKEN and AUGMENT_API_URL environment variables\n"
                    "2. Run 'auggie login' to create ~/.augment/session.json"
                )

            self.api_client = ContextAPIClient(
                ContextAPIClientOptions(
                    api_key=self.api_key, api_url=self.api_url, debug=self.debug
                )
            )

        return self.api_client.chat(llm_prompt)

    def close(self) -> None:
        """Close the MCP connection and cleanup resources."""
        self._log("Closing MCP connection")

        if self.mcp_process:
            try:
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.mcp_process.kill()
            except OSError as e:
                print(f"Error closing MCP process: {e}")
            finally:
                self.mcp_process = None

        self._log("MCP connection closed")

    def __enter__(self) -> "FileSystemContext":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

