"""
Configuration management for Nia Local Sync CLI.

Handles:
- Local config storage (~/.nia-sync/config.json)
- Fetching source configuration from cloud API
"""
import os
import json
from pathlib import Path
from typing import Any
import httpx

# Configuration paths
NIA_SYNC_DIR = Path.home() / ".nia-sync"
CONFIG_FILE = NIA_SYNC_DIR / "config.json"

# API configuration
API_BASE_URL = os.getenv("NIA_API_URL", "https://api.trynia.ai")

# Default directories to search for folders (no config needed)
DEFAULT_WATCH_DIRS = [
    "~/Documents",
    "~/Desktop",
    "~/Projects",
    "~/Developer",
    "~/Code",
    "~/dev",
    "~/repos",
    "~/Downloads",
    "~/src",
    "~/work",
    "~/workspace",
    "~/github",
]


def get_watch_dirs() -> list[str]:
    """Get directories to search for folders. Uses defaults + any custom ones."""
    config = load_config()
    custom = config.get("watch_dirs", [])
    # Combine defaults + custom, dedupe
    all_dirs = DEFAULT_WATCH_DIRS + custom
    return list(dict.fromkeys(all_dirs))


def find_folder_path(folder_name: str, max_depth: int = 3) -> str | None:
    """
    Search watch directories recursively for a folder with the given name.
    Returns the full path if found, None otherwise.

    Searches up to max_depth levels deep to avoid scanning entire filesystem.
    """
    def search_dir(base: str, depth: int) -> str | None:
        if depth > max_depth:
            return None

        try:
            for entry in os.scandir(base):
                if not entry.is_dir():
                    continue
                # Skip hidden directories and common large dirs
                if entry.name.startswith('.') or entry.name in ('node_modules', 'venv', '__pycache__', 'build', 'dist'):
                    continue

                if entry.name == folder_name:
                    return entry.path

                # Recurse into subdirectory
                if depth < max_depth:
                    found = search_dir(entry.path, depth + 1)
                    if found:
                        return found
        except PermissionError:
            pass

        return None

    for watch_dir in get_watch_dirs():
        expanded = os.path.expanduser(watch_dir)
        if not os.path.isdir(expanded):
            continue

        # Check direct child first (fast path)
        candidate = os.path.join(expanded, folder_name)
        if os.path.exists(candidate):
            return candidate

        # Search recursively
        found = search_dir(expanded, 1)
        if found:
            return found

    return None


def ensure_config_dir():
    """Ensure the config directory exists."""
    NIA_SYNC_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    """Load configuration from disk."""
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(config: dict[str, Any]):
    """Save configuration to disk."""
    ensure_config_dir()

    # Merge with existing config
    existing = load_config()
    existing.update(config)

    with open(CONFIG_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    # Secure the file (readable only by owner)
    os.chmod(CONFIG_FILE, 0o600)


def clear_config():
    """Clear all stored configuration."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()


def get_api_key() -> str | None:
    """Get the stored API key."""
    config = load_config()
    return config.get("api_key")


def get_sources() -> list[dict[str, Any]]:
    """
    Fetch configured sources from the cloud API.

    Returns list of sources with:
    - local_folder_id: UUID of the local folder
    - path: Local path to sync (e.g., ~/Library/Messages/chat.db)
    - detected_type: Type of source (imessage, safari_history, folder, etc.)
    - cursor: Current sync cursor (for incremental sync)
    - last_synced: ISO timestamp of last sync
    """
    api_key = get_api_key()
    if not api_key:
        return []

    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{API_BASE_URL}/v2/daemon/sources",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            # Invalid/expired API key
            return []
        raise
    except httpx.RequestError:
        # Network error - return empty for now
        return []


def add_source(path: str, detected_type: str | None = None) -> dict[str, Any] | None:
    """
    Add a new source for daemon sync.

    Args:
        path: Local path to sync
        detected_type: Optional detected type

    Returns:
        Created source info or None on failure
    """
    api_key = get_api_key()
    if not api_key:
        return None

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{API_BASE_URL}/v2/daemon/sources",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "path": path,
                    "detected_type": detected_type,
                },
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError:
        return None
    except httpx.RequestError:
        return None


def remove_source(local_folder_id: str) -> bool:
    """
    Remove a source from daemon sync.

    Args:
        local_folder_id: ID of the source to remove

    Returns:
        True on success, False on failure
    """
    api_key = get_api_key()
    if not api_key:
        return False

    try:
        with httpx.Client(timeout=30) as client:
            response = client.delete(
                f"{API_BASE_URL}/v2/daemon/sources/{local_folder_id}",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            return response.status_code == 200

    except httpx.HTTPStatusError:
        return False
    except httpx.RequestError:
        return False


def update_source_cursor(local_folder_id: str, cursor: dict[str, Any]) -> bool:
    """
    Update the sync cursor for a source after successful sync.

    This is called by the sync engine after pushing data to the backend.
    The backend updates the cursor in the database.
    """
    # Note: Cursor is updated by the /daemon/sync endpoint, not a separate call
    # This function is here for potential future use
    return True


def enable_source_sync(local_folder_id: str, path: str) -> bool:
    """
    Enable daemon sync for a source that exists locally.

    Args:
        local_folder_id: ID of the source
        path: Local path where the source exists

    Returns:
        True on success, False on failure
    """
    api_key = get_api_key()
    if not api_key:
        return False

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{API_BASE_URL}/v2/daemon/sources/{local_folder_id}/enable",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"path": path},
            )
            return response.status_code == 200

    except httpx.HTTPStatusError:
        return False
    except httpx.RequestError:
        return False
