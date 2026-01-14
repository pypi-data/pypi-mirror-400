"""
Database and folder extractor for Nia Local Sync CLI.

Extracts text content from SQLite databases and folders,
converting them into virtual "files" for indexing.

Supported types:
- iMessage (~/Library/Messages/chat.db)
- Safari History (~/Library/Safari/History.db)
- Chrome/Brave/Edge History
- Firefox History (places.sqlite)
- Telegram (JSON export)
- Regular folders
"""
import os
import re
import json
import sqlite3
import zipfile
import logging
from datetime import datetime, timezone
from typing import Any
from pathlib import Path

logger = logging.getLogger(__name__)

# =============================================================================
# EXCLUSION PATTERNS - Synced with backend/utils/exclusion_patterns.py
# =============================================================================

# Directories to skip entirely (prevents os.walk from descending)
SKIP_DIRS = {
    # VCS
    ".git", ".svn", ".hg", ".bzr",
    # Node/JS
    "node_modules", ".npm", ".pnpm-store", ".yarn", "bower_components",
    ".next", ".nuxt", ".output", ".svelte-kit", ".parcel-cache", ".cache", ".turbo",
    # Python
    "__pycache__", "venv", ".venv", "env", ".tox", ".nox",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".hypothesis", "htmlcov", ".Python",
    # JVM
    "target", ".gradle", ".m2",
    # Rust
    "target",
    # Go
    "vendor",
    # Ruby
    ".bundle",
    # .NET
    "bin", "obj", "packages",
    # iOS/macOS
    "DerivedData", "Pods", ".build",
    # Build outputs
    "dist", "build", "out", "output", "release", "debug", "coverage", ".nyc_output",
    # IDE
    ".idea", ".vscode", ".atom",
    # OS
    ".Spotlight-V100", ".Trashes",
    # Misc
    ".terraform", ".vagrant", ".docker", ".kube",
    "logs", "log", "tmp", "temp",
    ".aws", ".ssh",
}

# File extensions to skip (from backend exclusion_patterns.py)
SKIP_EXTENSIONS = {
    # Security - keys/certs
    ".pem", ".key", ".p12", ".pfx", ".crt", ".cer",
    # Python compiled
    ".pyc", ".pyo", ".pyd", ".egg",
    # JVM
    ".class", ".jar", ".war", ".ear",
    # .NET
    ".exe", ".pdb", ".nupkg",
    # Compiled binaries
    ".so", ".dylib", ".dll", ".o", ".obj", ".a", ".lib", ".wasm",
    # Databases
    ".sqlite", ".sqlite3", ".db", ".sql",
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".bmp", ".tiff", ".tif",
    ".psd", ".ai", ".sketch", ".fig",
    # Videos
    ".mp4", ".avi", ".mov", ".wmv", ".webm", ".mkv", ".flv",
    # Audio
    ".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a",
    # Documents
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    # Archives
    ".zip", ".tar", ".gz", ".tgz", ".rar", ".7z", ".bz2", ".xz",
    # Fonts
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    # Logs/temp
    ".log", ".tmp", ".temp", ".bak", ".backup", ".old", ".swp", ".swo",
    # Coverage
    ".lcov",
    # IDE
    ".code-workspace",
}

# Specific filenames to skip (from backend exclusion_patterns.py)
SKIP_FILES = {
    # Lock files
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
    "poetry.lock", "Pipfile.lock", "Gemfile.lock", "composer.lock",
    "Cargo.lock", "gradle.lockfile", "Package.resolved",
    # OS files
    ".DS_Store", "Thumbs.db", "desktop.ini", "ehthumbs.db",
    # Security - credentials
    ".env", ".envrc", ".npmrc", ".pypirc", ".netrc", ".htpasswd",
    # Logs
    "npm-debug.log", "yarn-debug.log", "yarn-error.log", ".pnpm-debug.log",
    "pip-log.txt",
    # IDE
    ".project", ".classpath",
    # Python
    ".coverage",
}

# Patterns that match anywhere in the path (for files like id_rsa, credentials.json)
SKIP_PATH_PATTERNS = {
    "credentials", "secrets", ".secret", ".secrets",
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
}

# Type identifiers
TYPE_IMESSAGE = "imessage"
TYPE_SAFARI_HISTORY = "safari_history"
TYPE_CHROME_HISTORY = "chrome_history"
TYPE_FIREFOX_HISTORY = "firefox_history"
TYPE_TELEGRAM = "telegram"
TYPE_FOLDER = "folder"
TYPE_GENERIC_DB = "generic"

# Limits
MAX_ROWS = 100_000
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB per file


def detect_source_type(path: str) -> str:
    """
    Auto-detect the type of source based on path and file structure.

    Args:
        path: Path to file or directory

    Returns:
        Type identifier string
    """
    # Check if directory (regular folder or telegram export)
    if os.path.isdir(path):
        if os.path.exists(os.path.join(path, "result.json")):
            return TYPE_TELEGRAM
        return TYPE_FOLDER

    # Check for Telegram JSON export
    if path.endswith(".json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "chats" in data and isinstance(data.get("chats"), dict):
                    return TYPE_TELEGRAM
        except Exception:
            pass

    # Check for ZIP (could be Telegram export)
    if zipfile.is_zipfile(path):
        try:
            with zipfile.ZipFile(path, "r") as zf:
                names = zf.namelist()
                if "result.json" in names or any(n.endswith("/result.json") for n in names):
                    return TYPE_TELEGRAM
        except Exception:
            pass

    # Check SQLite databases
    if not os.path.isfile(path):
        return TYPE_FOLDER

    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0].lower() for row in cursor.fetchall()}
        conn.close()

        # iMessage
        if "message" in tables and "handle" in tables and "chat" in tables:
            return TYPE_IMESSAGE

        # Safari History
        if "history_items" in tables and "history_visits" in tables:
            return TYPE_SAFARI_HISTORY

        # Chrome/Brave/Edge History
        if "urls" in tables and "visits" in tables and "keyword_search_terms" in tables:
            return TYPE_CHROME_HISTORY

        # Firefox History
        if "moz_places" in tables and "moz_historyvisits" in tables:
            return TYPE_FIREFOX_HISTORY

        return TYPE_GENERIC_DB

    except Exception:
        return TYPE_FOLDER


def extract_incremental(
    path: str,
    source_type: str,
    cursor: dict[str, Any] | None = None,
    limit: int = MAX_ROWS,
) -> dict[str, Any]:
    """
    Extract data incrementally from a source.

    Args:
        path: Path to the source
        source_type: Type of source
        cursor: Previous sync cursor (for incremental extraction)
        limit: Maximum items to extract

    Returns:
        Dict with files, new cursor, and stats
    """
    cursor = cursor or {}

    if source_type == TYPE_IMESSAGE:
        return _extract_imessage(path, cursor, limit)
    elif source_type == TYPE_SAFARI_HISTORY:
        return _extract_safari_history(path, cursor, limit)
    elif source_type == TYPE_CHROME_HISTORY:
        return _extract_chrome_history(path, cursor, limit)
    elif source_type == TYPE_FIREFOX_HISTORY:
        return _extract_firefox_history(path, cursor, limit)
    elif source_type == TYPE_TELEGRAM:
        return _extract_telegram(path, cursor, limit)
    elif source_type == TYPE_FOLDER:
        return _extract_folder(path, cursor, limit)
    else:
        return _extract_generic_db(path, cursor, limit)


def _extract_imessage(
    db_path: str,
    cursor: dict[str, Any],
    limit: int,
) -> dict[str, Any]:
    """Extract messages from iMessage chat.db."""
    files = []
    max_rowid = cursor.get("last_rowid", 0)
    max_timestamp = cursor.get("last_timestamp", 0)
    since_rowid = cursor.get("last_rowid")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    where_clauses = ["m.text IS NOT NULL", "m.text != ''"]
    params = []

    if since_rowid:
        where_clauses.append("m.ROWID > ?")
        params.append(since_rowid)

    params.append(limit)

    query = f"""
        SELECT
            m.ROWID as row_id,
            m.text,
            m.date,
            m.is_from_me,
            m.service,
            h.id as contact_id,
            COALESCE(h.uncanonicalized_id, h.id) as contact_display
        FROM message m
        LEFT JOIN handle h ON m.handle_id = h.ROWID
        WHERE {' AND '.join(where_clauses)}
        ORDER BY m.ROWID ASC
        LIMIT ?
    """

    cur.execute(query, params)
    rows = cur.fetchall()

    for row in rows:
        row_id = row["row_id"]
        text = row["text"]
        apple_date = row["date"]
        is_from_me = row["is_from_me"]
        contact_display = row["contact_display"] or row["contact_id"] or "unknown"

        max_rowid = max(max_rowid, row_id)
        if apple_date:
            max_timestamp = max(max_timestamp, apple_date)

        if not text or len(text.strip()) < 2:
            continue

        # Convert Apple date to ISO
        try:
            if apple_date:
                unix_ts = (apple_date / 1_000_000_000) + 978307200
                dt = datetime.fromtimestamp(unix_ts, tz=timezone.utc)
                timestamp_str = dt.isoformat()
                date_prefix = dt.strftime("%Y-%m-%d")
            else:
                timestamp_str = None
                date_prefix = "unknown"
        except Exception:
            timestamp_str = None
            date_prefix = "unknown"

        safe_contact = re.sub(r"[^\w\-_]", "_", str(contact_display))[:50]
        direction = "sent" if is_from_me else "received"
        file_path = f"messages/{safe_contact}/{date_prefix}_{row_id}_{direction}.txt"

        files.append({
            "path": file_path,
            "content": text,
            "metadata": {
                "db_type": TYPE_IMESSAGE,
                "row_id": row_id,
                "timestamp": timestamp_str,
                "contact": contact_display,
                "is_from_me": bool(is_from_me),
            },
        })

    conn.close()
    logger.info(f"Extracted {len(files)} messages from iMessage")

    return {
        "files": files,
        "cursor": {"last_rowid": max_rowid, "last_timestamp": max_timestamp},
        "stats": {"extracted": len(files), "db_type": TYPE_IMESSAGE},
    }


def _extract_safari_history(
    db_path: str,
    cursor: dict[str, Any],
    limit: int,
) -> dict[str, Any]:
    """Extract browsing history from Safari History.db."""
    files = []
    max_visit_time = cursor.get("last_visit_time", 0)
    since_visit_time = cursor.get("last_visit_time")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    where_clauses = ["hv.title IS NOT NULL", "hv.title != ''"]
    params = []

    if since_visit_time:
        where_clauses.append("hv.visit_time > ?")
        params.append(since_visit_time)

    params.append(limit)

    query = f"""
        SELECT
            hi.id,
            hi.url,
            hi.domain_expansion,
            hv.title,
            hv.visit_time
        FROM history_visits hv
        JOIN history_items hi ON hi.id = hv.history_item
        WHERE {' AND '.join(where_clauses)}
        ORDER BY hv.visit_time ASC
        LIMIT ?
    """

    cur.execute(query, params)
    rows = cur.fetchall()

    for row in rows:
        item_id = row["id"]
        url = row["url"] or ""
        domain = row["domain_expansion"] or ""
        title = row["title"] or ""
        visit_time = row["visit_time"]

        max_visit_time = max(max_visit_time, visit_time or 0)

        if not title.strip():
            continue

        try:
            if visit_time:
                unix_ts = visit_time + 978307200
                dt = datetime.fromtimestamp(unix_ts, tz=timezone.utc)
                timestamp_str = dt.isoformat()
                date_prefix = dt.strftime("%Y-%m-%d")
            else:
                timestamp_str = None
                date_prefix = "unknown"
        except Exception:
            timestamp_str = None
            date_prefix = "unknown"

        content = f"{title}\n{url}"
        safe_domain = re.sub(r"[^\w\-_]", "_", domain)[:30] if domain else "other"
        file_path = f"history/{safe_domain}/{date_prefix}_{item_id}.txt"

        files.append({
            "path": file_path,
            "content": content,
            "metadata": {
                "db_type": TYPE_SAFARI_HISTORY,
                "row_id": item_id,
                "timestamp": timestamp_str,
                "url": url,
                "domain": domain,
            },
        })

    conn.close()
    logger.info(f"Extracted {len(files)} history items from Safari")

    return {
        "files": files,
        "cursor": {"last_visit_time": max_visit_time},
        "stats": {"extracted": len(files), "db_type": TYPE_SAFARI_HISTORY},
    }


def _extract_chrome_history(
    db_path: str,
    cursor: dict[str, Any],
    limit: int,
) -> dict[str, Any]:
    """Extract browsing history from Chrome/Brave/Edge."""
    files = []
    max_visit_time = cursor.get("last_visit_time", 0)
    since_visit_time = cursor.get("last_visit_time")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    where_clauses = ["u.title IS NOT NULL", "u.title != ''"]
    params = []

    if since_visit_time:
        where_clauses.append("v.visit_time > ?")
        params.append(since_visit_time)

    params.append(limit)

    query = f"""
        SELECT
            u.id,
            u.url,
            u.title,
            v.visit_time
        FROM visits v
        JOIN urls u ON u.id = v.url
        WHERE {' AND '.join(where_clauses)}
        ORDER BY v.visit_time ASC
        LIMIT ?
    """

    cur.execute(query, params)
    rows = cur.fetchall()

    for row in rows:
        url_id = row["id"]
        url = row["url"] or ""
        title = row["title"] or ""
        visit_time = row["visit_time"]

        max_visit_time = max(max_visit_time, visit_time or 0)

        if not title.strip():
            continue

        try:
            if visit_time:
                unix_ts = (visit_time / 1_000_000) - 11644473600
                dt = datetime.fromtimestamp(unix_ts, tz=timezone.utc)
                timestamp_str = dt.isoformat()
                date_prefix = dt.strftime("%Y-%m-%d")
            else:
                timestamp_str = None
                date_prefix = "unknown"
        except Exception:
            timestamp_str = None
            date_prefix = "unknown"

        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc or "other"
        except Exception:
            domain = "other"

        content = f"{title}\n{url}"
        safe_domain = re.sub(r"[^\w\-_]", "_", domain)[:30]
        file_path = f"history/{safe_domain}/{date_prefix}_{url_id}.txt"

        files.append({
            "path": file_path,
            "content": content,
            "metadata": {
                "db_type": TYPE_CHROME_HISTORY,
                "row_id": url_id,
                "timestamp": timestamp_str,
                "url": url,
                "domain": domain,
            },
        })

    conn.close()
    logger.info(f"Extracted {len(files)} history items from Chrome")

    return {
        "files": files,
        "cursor": {"last_visit_time": max_visit_time},
        "stats": {"extracted": len(files), "db_type": TYPE_CHROME_HISTORY},
    }


def _extract_firefox_history(
    db_path: str,
    cursor: dict[str, Any],
    limit: int,
) -> dict[str, Any]:
    """Extract browsing history from Firefox places.sqlite."""
    files = []
    max_visit_date = cursor.get("last_visit_date", 0)
    since_visit_date = cursor.get("last_visit_date")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    where_clauses = ["p.title IS NOT NULL", "p.title != ''"]
    params = []

    if since_visit_date:
        where_clauses.append("h.visit_date > ?")
        params.append(since_visit_date)

    params.append(limit)

    query = f"""
        SELECT
            p.id,
            p.url,
            p.title,
            h.visit_date
        FROM moz_places p
        JOIN moz_historyvisits h ON p.id = h.place_id
        WHERE {' AND '.join(where_clauses)}
        ORDER BY h.visit_date ASC
        LIMIT ?
    """

    cur.execute(query, params)
    rows = cur.fetchall()

    for row in rows:
        place_id = row["id"]
        url = row["url"] or ""
        title = row["title"] or ""
        visit_date = row["visit_date"]

        max_visit_date = max(max_visit_date, visit_date or 0)

        if not title.strip():
            continue

        try:
            if visit_date:
                unix_ts = visit_date / 1_000_000
                dt = datetime.fromtimestamp(unix_ts, tz=timezone.utc)
                timestamp_str = dt.isoformat()
                date_prefix = dt.strftime("%Y-%m-%d")
            else:
                timestamp_str = None
                date_prefix = "unknown"
        except Exception:
            timestamp_str = None
            date_prefix = "unknown"

        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc or "other"
        except Exception:
            domain = "other"

        content = f"{title}\n{url}"
        safe_domain = re.sub(r"[^\w\-_]", "_", domain)[:30]
        file_path = f"history/{safe_domain}/{date_prefix}_{place_id}.txt"

        files.append({
            "path": file_path,
            "content": content,
            "metadata": {
                "db_type": TYPE_FIREFOX_HISTORY,
                "row_id": place_id,
                "timestamp": timestamp_str,
                "url": url,
                "domain": domain,
            },
        })

    conn.close()
    logger.info(f"Extracted {len(files)} history items from Firefox")

    return {
        "files": files,
        "cursor": {"last_visit_date": max_visit_date},
        "stats": {"extracted": len(files), "db_type": TYPE_FIREFOX_HISTORY},
    }


def _extract_telegram(
    export_path: str,
    cursor: dict[str, Any],
    limit: int,
) -> dict[str, Any]:
    """Extract messages from Telegram export (JSON or ZIP)."""
    files = []
    max_message_id = cursor.get("last_message_id", 0)
    since_message_id = cursor.get("last_message_id")
    extracted_count = 0

    # Handle different input types
    if zipfile.is_zipfile(export_path):
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(export_path, "r") as zf:
                zf.extractall(temp_dir)
            result_file = os.path.join(temp_dir, "result.json")
            if not os.path.exists(result_file):
                for item in os.listdir(temp_dir):
                    subdir = os.path.join(temp_dir, item)
                    if os.path.isdir(subdir):
                        candidate = os.path.join(subdir, "result.json")
                        if os.path.exists(candidate):
                            result_file = candidate
                            break
            return _extract_telegram_json(result_file, cursor, limit)
    elif os.path.isdir(export_path):
        result_file = os.path.join(export_path, "result.json")
    else:
        result_file = export_path

    return _extract_telegram_json(result_file, cursor, limit)


def _extract_telegram_json(
    result_file: str,
    cursor: dict[str, Any],
    limit: int,
) -> dict[str, Any]:
    """Extract from Telegram result.json file."""
    files = []
    max_message_id = cursor.get("last_message_id", 0)
    since_message_id = cursor.get("last_message_id")
    extracted_count = 0

    with open(result_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    chats_data = data.get("chats", {})
    chats = chats_data.get("list", []) if isinstance(chats_data, dict) else []

    for chat in chats:
        if extracted_count >= limit:
            break

        chat_name = chat.get("name", "Unknown Chat")
        chat_type = chat.get("type", "personal_chat")
        chat_id = chat.get("id", 0)

        messages = chat.get("messages", [])

        for msg in messages:
            if extracted_count >= limit:
                break

            msg_id = msg.get("id")
            msg_type = msg.get("type", "message")

            if since_message_id and msg_id and msg_id <= since_message_id:
                continue

            if msg_type != "message":
                continue

            # Handle text (can be string or list)
            text_content = msg.get("text", "")
            if isinstance(text_content, list):
                parts = []
                for item in text_content:
                    if isinstance(item, dict):
                        parts.append(item.get("text", ""))
                    elif isinstance(item, str):
                        parts.append(item)
                text_content = "".join(parts)

            if not text_content or not text_content.strip():
                continue

            if msg_id:
                max_message_id = max(max_message_id, msg_id)

            date_str = msg.get("date", "")
            try:
                if date_str:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    timestamp_str = dt.isoformat()
                    date_prefix = dt.strftime("%Y-%m-%d")
                else:
                    timestamp_str = None
                    date_prefix = "unknown"
            except Exception:
                timestamp_str = date_str
                date_prefix = "unknown"

            from_name = msg.get("from", "") or msg.get("actor", "") or "Unknown"

            safe_chat = re.sub(r"[^\w\-_]", "_", chat_name)[:50]
            file_path = f"telegram/{safe_chat}/{date_prefix}_{msg_id}.txt"

            files.append({
                "path": file_path,
                "content": text_content,
                "metadata": {
                    "db_type": TYPE_TELEGRAM,
                    "chat_name": chat_name,
                    "chat_type": chat_type,
                    "message_id": msg_id,
                    "timestamp": timestamp_str,
                    "from_name": from_name,
                },
            })
            extracted_count += 1

    logger.info(f"Extracted {len(files)} messages from Telegram")

    return {
        "files": files,
        "cursor": {"last_message_id": max_message_id},
        "stats": {"extracted": len(files), "db_type": TYPE_TELEGRAM},
    }


def _extract_folder(
    folder_path: str,
    cursor: dict[str, Any],
    limit: int,
) -> dict[str, Any]:
    """Extract text files from a regular folder with proper exclusion patterns."""
    files = []
    last_mtime = cursor.get("last_mtime", 0)
    max_mtime = last_mtime
    extracted_count = 0

    # Allowed text file extensions
    text_extensions = {
        ".txt", ".md", ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml",
        ".html", ".css", ".scss", ".less", ".xml", ".csv", ".sh", ".bash", ".zsh",
        ".rs", ".go", ".java", ".c", ".cpp", ".h", ".hpp", ".rb", ".vue", ".svelte",
        ".php", ".swift", ".kt", ".scala", ".r", ".sql", ".toml", ".ini", ".cfg",
        ".makefile", ".dockerfile", ".gitignore", ".editorconfig",
    }

    for root, dirs, filenames in os.walk(folder_path, topdown=True):
        if extracted_count >= limit:
            break

        # Filter out excluded directories IN-PLACE to prevent os.walk from descending
        dirs[:] = [
            d for d in dirs
            if d not in SKIP_DIRS
            and not d.startswith(".")
            and not d.endswith(".egg-info")
        ]

        for filename in filenames:
            if extracted_count >= limit:
                break

            # Skip by filename
            if filename in SKIP_FILES:
                continue

            # Skip hidden files
            if filename.startswith("."):
                continue

            # Skip files matching security patterns (credentials, secrets, keys)
            filename_lower = filename.lower()
            if any(pattern in filename_lower for pattern in SKIP_PATH_PATTERNS):
                continue

            ext = Path(filename).suffix.lower()

            # Skip by extension
            if ext in SKIP_EXTENSIONS:
                continue

            # Only include known text extensions
            if ext and ext not in text_extensions:
                continue

            file_path = os.path.join(root, filename)

            try:
                stat = os.stat(file_path)
                mtime = stat.st_mtime

                # Skip if not modified since last sync
                if mtime <= last_mtime:
                    continue

                # Skip large files
                if stat.st_size > MAX_FILE_SIZE_BYTES:
                    continue

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                if not content.strip():
                    continue

                max_mtime = max(max_mtime, mtime)

                # Relative path from folder root
                rel_path = os.path.relpath(file_path, folder_path)

                files.append({
                    "path": rel_path,
                    "content": content,
                    "metadata": {
                        "db_type": TYPE_FOLDER,
                        "extension": ext,
                        "mtime": mtime,
                    },
                })
                extracted_count += 1

            except (PermissionError, IOError) as e:
                logger.warning(f"Could not read {file_path}: {e}")
                continue

    logger.info(f"Extracted {len(files)} files from folder")

    return {
        "files": files,
        "cursor": {"last_mtime": max_mtime},
        "stats": {"extracted": len(files), "db_type": TYPE_FOLDER},
    }


def _extract_generic_db(
    db_path: str,
    cursor: dict[str, Any],
    limit: int,
) -> dict[str, Any]:
    """Extract from generic SQLite database."""
    files = []
    total_extracted = 0

    skip_tables = {"sqlite_sequence", "sqlite_stat1", "sqlite_stat4"}

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]

    for table_name in tables:
        if table_name.lower() in skip_tables:
            continue

        if total_extracted >= limit:
            break

        try:
            cur.execute(f'PRAGMA table_info("{table_name}")')
            columns = cur.fetchall()

            text_columns = [
                col[1]
                for col in columns
                if col[2].upper() in ("TEXT", "VARCHAR", "CHAR", "CLOB")
            ]

            if not text_columns:
                continue

            pk_column = next((col[1] for col in columns if col[5] == 1), "rowid")

            select_cols = [f'"{pk_column}"'] + [f'"{col}"' for col in text_columns]
            remaining = limit - total_extracted
            query = f'SELECT {", ".join(select_cols)} FROM "{table_name}" LIMIT ?'

            cur.execute(query, (remaining,))
            rows = cur.fetchall()

            for row in rows:
                pk_value = row[0]
                text_values = row[1:]

                combined = []
                for col_name, value in zip(text_columns, text_values):
                    if value and isinstance(value, str) and value.strip():
                        combined.append(f"{col_name}: {value}")

                if not combined:
                    continue

                content = "\n".join(combined)
                safe_table = re.sub(r"[^\w\-_]", "_", table_name)
                file_path = f"{safe_table}/row_{pk_value}.txt"

                files.append({
                    "path": file_path,
                    "content": content,
                    "metadata": {
                        "db_type": TYPE_GENERIC_DB,
                        "table": table_name,
                        "row_id": pk_value,
                    },
                })
                total_extracted += 1

        except Exception as e:
            logger.warning(f"Error extracting from table {table_name}: {e}")
            continue

    conn.close()
    logger.info(f"Extracted {len(files)} rows from generic database")

    return {
        "files": files,
        "cursor": {},
        "stats": {"extracted": len(files), "db_type": TYPE_GENERIC_DB},
    }
