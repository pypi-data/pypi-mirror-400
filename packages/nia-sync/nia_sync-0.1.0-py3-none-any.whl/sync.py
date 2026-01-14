"""
Sync engine for Nia Local Sync CLI.

Handles:
- Extracting data from local sources (databases, folders)
- Uploading to cloud API
- Cursor management for incremental sync
"""
import os
import logging
from pathlib import Path
from typing import Any
import httpx

from config import API_BASE_URL, get_api_key, enable_source_sync
from extractor import extract_incremental, detect_source_type

logger = logging.getLogger(__name__)

SYNC_TIMEOUT = 120  # 2 minutes per sync request


def sync_all_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Sync all configured sources.

    Args:
        sources: List of source configs from cloud API

    Returns:
        List of results for each source
    """
    results = []

    for source in sources:
        result = sync_source(source)
        results.append(result)

    return results


def sync_source(source: dict[str, Any]) -> dict[str, Any]:
    """
    Sync a single source.

    Args:
        source: Source config from cloud API with:
            - local_folder_id: UUID of the local folder
            - path: Local path to sync
            - detected_type: Type of source
            - cursor: Current sync cursor

    Returns:
        Result dict with status, path, and stats
    """
    local_folder_id = source.get("local_folder_id")
    path = source.get("path", "")
    detected_type = source.get("detected_type")
    cursor = source.get("cursor", {})

    # Expand ~ in path
    path = os.path.expanduser(path)

    # Validate path exists
    if not os.path.exists(path):
        return {
            "path": path,
            "status": "error",
            "error": f"Path does not exist: {path}",
        }

    # Auto-enable sync if source exists locally but sync not enabled
    if not source.get("sync_enabled", False):
        logger.info(f"Auto-enabling sync for {path}")
        enable_source_sync(local_folder_id, path)

    # Auto-detect type if not specified
    if not detected_type:
        detected_type = detect_source_type(path)

    logger.info(f"Syncing {path} (type={detected_type})")

    try:
        # Extract data incrementally
        extraction_result = extract_incremental(
            path=path,
            source_type=detected_type,
            cursor=cursor,
        )

        files = extraction_result.get("files", [])
        new_cursor = extraction_result.get("cursor", {})
        stats = extraction_result.get("stats", {})

        if not files:
            logger.info(f"No new data to sync for {path}")
            return {
                "path": path,
                "status": "success",
                "added": 0,
                "message": "No new data",
            }

        # Upload to backend
        upload_result = upload_sync_data(
            local_folder_id=local_folder_id,
            files=files,
            cursor=new_cursor,
            stats=stats,
        )

        if upload_result.get("status") == "ok":
            # Update source cursor in-place so subsequent syncs use it
            source["cursor"] = new_cursor
            return {
                "path": path,
                "status": "success",
                "added": len(files),
                "chunks_indexed": upload_result.get("chunks_indexed", 0),
                "new_cursor": new_cursor,
            }
        else:
            return {
                "path": path,
                "status": "error",
                "error": upload_result.get("message", "Upload failed"),
            }

    except PermissionError:
        return {
            "path": path,
            "status": "error",
            "error": "Permission denied. Grant Full Disk Access in System Settings > Privacy & Security.",
        }
    except Exception as e:
        logger.error(f"Error syncing {path}: {e}", exc_info=True)
        return {
            "path": path,
            "status": "error",
            "error": str(e),
        }


def upload_sync_data(
    local_folder_id: str,
    files: list[dict[str, Any]],
    cursor: dict[str, Any],
    stats: dict[str, Any],
) -> dict[str, Any]:
    """
    Upload extracted data to the cloud API.

    Args:
        local_folder_id: UUID of the local folder
        files: List of extracted files with path, content, metadata
        cursor: New cursor after extraction
        stats: Extraction stats

    Returns:
        API response dict
    """
    api_key = get_api_key()
    if not api_key:
        return {"status": "error", "message": "Not authenticated"}

    try:
        with httpx.Client(timeout=SYNC_TIMEOUT) as client:
            response = client.post(
                f"{API_BASE_URL}/v2/daemon/sync",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "local_folder_id": local_folder_id,
                    "files": files,
                    "cursor": cursor,
                    "stats": stats,
                },
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"status": "error", "message": "Authentication failed"}
            elif response.status_code == 404:
                return {"status": "error", "message": "Local folder not found"}
            else:
                detail = response.json().get("detail", response.text)
                return {"status": "error", "message": f"API error: {detail}"}

    except httpx.TimeoutException:
        return {"status": "error", "message": "Request timeout"}
    except httpx.RequestError as e:
        return {"status": "error", "message": f"Network error: {e}"}
