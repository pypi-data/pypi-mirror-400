"""
Credential resolution utilities.

Resolves API credentials from multiple sources with a defined priority order.
"""

import os
from dataclasses import dataclass
from typing import Optional

from .session_reader import read_session_file


@dataclass
class CredentialOptions:
    """Options for credential resolution."""

    api_key: Optional[str] = None
    api_url: Optional[str] = None


@dataclass
class ResolvedCredentials:
    """Resolved credentials."""

    api_key: str
    api_url: str


def resolve_credentials(options: Optional[CredentialOptions] = None) -> ResolvedCredentials:
    """
    Resolve API credentials from options, environment, or session file.

    Priority order:
        1. options.api_key and options.api_url (if provided)
        2. AUGMENT_API_TOKEN and AUGMENT_API_URL environment variables
        3. ~/.augment/session.json (created by `auggie login`)

    Args:
        options: Optional credential options.

    Returns:
        Resolved credentials.

    Raises:
        ValueError: If credentials cannot be resolved.
    """
    if options is None:
        options = CredentialOptions()

    api_key = options.api_key or os.environ.get("AUGMENT_API_TOKEN")
    api_url = options.api_url or os.environ.get("AUGMENT_API_URL")

    # If credentials not provided, try session.json
    if not (api_key and api_url):
        session = read_session_file()
        if session:
            api_key = api_key or session.get("accessToken")
            api_url = api_url or session.get("tenantURL")

    # Validate we have credentials
    if not api_key:
        raise ValueError(
            "API key is required. Provide it via:\n"
            "1. options.api_key parameter\n"
            "2. AUGMENT_API_TOKEN environment variable\n"
            "3. Run 'auggie login' to create ~/.augment/session.json"
        )

    if not api_url:
        raise ValueError(
            "API URL is required. Provide it via:\n"
            "1. options.api_url parameter\n"
            "2. AUGMENT_API_URL environment variable\n"
            "3. Run 'auggie login' to create ~/.augment/session.json"
        )

    return ResolvedCredentials(api_key=api_key, api_url=api_url)

