"""
Utility for reading Augment session file
"""

import json
from pathlib import Path
from typing import Optional

from typing_extensions import TypedDict


class SessionData(TypedDict, total=False):
    """Structure of the session.json file created by `auggie login`"""

    accessToken: str
    tenantURL: str
    scopes: Optional[list]


def read_session_file() -> Optional[SessionData]:
    """
    Read session data from ~/.augment/session.json.

    Returns:
        Session data if the file exists and is valid, None otherwise.
    """
    session_path = Path.home() / ".augment" / "session.json"

    try:
        data = json.loads(session_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, PermissionError, json.JSONDecodeError):
        return None

    # Validate required fields
    if not (data.get("accessToken") and data.get("tenantURL")):
        return None

    return data

