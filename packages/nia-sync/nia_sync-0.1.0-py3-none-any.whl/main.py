#!/usr/bin/env python3
"""
Nia - Local Sync Engine

Keep your local folders and databases in sync with Nia cloud.
Real-time file watching with instant sync.

Usage:
    nia              # Start sync engine (default)
    nia login        # Authenticate with Nia
    nia status       # Show what's syncing
    nia link ID PATH # Link a source to local folder
"""
import os
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from auth import login as do_login, logout as do_logout, is_authenticated, get_api_key
from config import get_sources, add_source, remove_source, enable_source_sync, NIA_SYNC_DIR, find_folder_path
from sync import sync_all_sources
from extractor import detect_source_type

app = typer.Typer(
    name="nia",
    help="[cyan]Nia Sync Engine[/cyan] — Keep local folders in sync with Nia cloud",
    no_args_is_help=False,
    rich_markup_mode="rich",
    epilog="[dim]Quick start: [cyan]nia login[/cyan] → [cyan]nia status[/cyan] → [cyan]nia[/cyan][/dim]",
)
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Start the sync daemon if no command specified."""
    if ctx.invoked_subcommand is None:
        # Default: start daemon mode with default values
        daemon(watch=True, fallback_interval=600, refresh_interval=30)


@app.command()
def login():
    """Authenticate with Nia using browser-based login."""
    if is_authenticated():
        console.print("[yellow]Already logged in.[/yellow]")
        console.print(f"Config stored at: {NIA_SYNC_DIR}")
        _check_local_sources()
        return

    console.print(Panel.fit(
        "[bold cyan]Nia[/bold cyan]\n\n"
        "Opening browser to authenticate...",
        border_style="cyan",
    ))

    success = do_login()
    if success:
        console.print("[green]Successfully logged in![/green]")
        _check_local_sources()
    else:
        console.print("[red]Login failed. Please try again.[/red]")
        raise typer.Exit(1)


KNOWN_PATHS = {
    "imessage": "~/Library/Messages/chat.db",
    "safari_history": "~/Library/Safari/History.db",
    "chrome_history": "~/Library/Application Support/Google/Chrome/Default/History",
    "firefox_history": "~/Library/Application Support/Firefox/Profiles/*/places.sqlite",
}


def _check_local_sources():
    """Check for indexed sources that exist locally and can be synced."""
    sources = get_sources()
    if not sources:
        return

    found_locally = []
    need_sync_enable = []

    for src in sources:
        path = src.get("path")
        detected_type = src.get("detected_type")

        # If no path but known type, try standard path
        if not path and detected_type and detected_type in KNOWN_PATHS:
            path = KNOWN_PATHS[detected_type]
            src["_detected_path"] = path

        if not path:
            continue

        expanded = os.path.expanduser(path)
        if os.path.exists(expanded):
            found_locally.append(src)
            src["_local_path"] = expanded
            if not src.get("sync_enabled", False):
                need_sync_enable.append(src)

    if found_locally:
        console.print(f"\n[green]Found {len(found_locally)} source(s) on this machine:[/green]")
        for src in found_locally:
            sync_status = "[green]✓ syncing[/green]" if src.get("sync_enabled") else "[yellow]○ not syncing[/yellow]"
            console.print(f"  • {src.get('display_name', 'Unknown')} {sync_status}")

        if need_sync_enable:
            console.print(f"\n[dim]Enabling sync for {len(need_sync_enable)} source(s)...[/dim]")
            for src in need_sync_enable:
                local_path = src.get("_local_path") or src.get("_detected_path")
                if local_path and enable_source_sync(src["local_folder_id"], local_path):
                    console.print(f"  [green]✓[/green] Enabled sync for {src.get('display_name')}")
            console.print(f"\n[dim]Run [cyan]nia[/cyan] to start syncing.[/dim]")


@app.command()
def logout():
    """Clear stored credentials."""
    do_logout()
    console.print("[green]✓ Logged out[/green]")


@app.command()
def upgrade():
    """Upgrade Nia to the latest version."""
    import subprocess
    import sys

    console.print("[dim]Checking for updates...[/dim]")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "nia-sync"],
            capture_output=True,
            text=True,
        )

        if "Successfully installed" in result.stdout:
            console.print("[green]✓ Upgraded to latest version[/green]")
        elif "Requirement already satisfied" in result.stdout:
            console.print("[green]✓ Already on latest version[/green]")
        else:
            console.print("[yellow]No updates available[/yellow]")

    except Exception as e:
        console.print(f"[red]Upgrade failed: {e}[/red]")
        console.print("[dim]Try manually: pip install --upgrade nia-sync[/dim]")
        raise typer.Exit(1)


@app.command()
def status():
    """Show sync status and configured sources."""
    if not is_authenticated():
        console.print("[red]Not logged in. Run [cyan]nia login[/cyan] first.[/red]")
        raise typer.Exit(1)

    console.print("[bold cyan]Nia Sync Status[/bold cyan]\n")

    sources = get_sources()
    if not sources:
        console.print("[yellow]No sources configured.[/yellow]")
        console.print("\n[dim]Add sources in the Nia web app, or run:[/dim] [cyan]nia add ~/path/to/folder[/cyan]")
        return

    table = Table(show_header=True)
    table.add_column("ID", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Path")
    table.add_column("Type", style="green")
    table.add_column("Status")

    needs_link = []
    for source in sources:
        source_id = source.get("local_folder_id", "")[:8]
        name = source.get("display_name", "")
        path = source.get("path") or ""
        detected_type = source.get("detected_type") or "folder"

        # Check if source can be synced
        if path:
            expanded = os.path.expanduser(path)
            if os.path.exists(expanded):
                status = "[green]✓ ready[/green]"
            else:
                status = "[yellow]○ path not found[/yellow]"
        else:
            # Check if it's a known type we can auto-detect
            if detected_type in KNOWN_PATHS:
                known_path = os.path.expanduser(KNOWN_PATHS[detected_type])
                if os.path.exists(known_path):
                    status = "[green]✓ ready[/green]"
                    path = KNOWN_PATHS[detected_type]
                else:
                    status = "[yellow]○ not found locally[/yellow]"
            else:
                status = "[red]⚠ needs link[/red]"
                needs_link.append(source)

        table.add_row(source_id, name, path or "[dim]not set[/dim]", detected_type, status)

    console.print(table)

    if needs_link:
        console.print(f"\n[yellow]{len(needs_link)} source(s) need to be linked to local paths.[/yellow]")
        console.print("[dim]Use:[/dim] [cyan]nia link <ID> /path/to/folder[/cyan]")
    else:
        console.print("\n[dim]Run [cyan]nia[/cyan] to start syncing • [cyan]nia link <ID> <path>[/cyan] to link[/dim]")


@app.command(name="once")
def sync():
    """Run a one-time sync (then exit)."""
    if not is_authenticated():
        console.print("[red]Not logged in. Run [cyan]nia login[/cyan] first.[/red]")
        raise typer.Exit(1)

    console.print("[bold]Starting sync...[/bold]")

    sources = get_sources()
    if not sources:
        console.print("[yellow]No sources configured.[/yellow]")
        console.print("Add sources in the Nia web app first.")
        return

    results = sync_all_sources(sources)

    for result in results:
        path = result.get("path", "unknown")
        status = result.get("status", "unknown")
        if status == "success":
            added = result.get("added", 0)
            console.print(f"[green]✓ {path}[/green] - {added} items synced")
        else:
            error = result.get("error", "unknown error")
            console.print(f"[red]✗ {path}[/red] - {error}")


@app.command()
def add(path: str = typer.Argument(..., help="Path to sync (folder or database)")):
    """Add a new source to sync."""
    if not is_authenticated():
        console.print("[red]Not logged in. Run [cyan]nia login[/cyan] first.[/red]")
        raise typer.Exit(1)

    # Expand path
    expanded_path = os.path.expanduser(path)

    # Check if path exists
    if not os.path.exists(expanded_path):
        console.print(f"[red]Path does not exist: {expanded_path}[/red]")
        raise typer.Exit(1)

    # Detect source type
    detected_type = detect_source_type(expanded_path)
    console.print(f"Detected type: [cyan]{detected_type}[/cyan]")

    # Add source via API
    result = add_source(path, detected_type)

    if result:
        console.print(f"[green]✓ Added:[/green] {result.get('display_name', path)}")
        console.print(f"[dim]ID: {result.get('local_folder_id')[:8]}[/dim]")
        console.print("\n[dim]Run [cyan]nia[/cyan] to start syncing.[/dim]")
    else:
        console.print("[red]Failed to add source.[/red]")
        raise typer.Exit(1)


@app.command()
def remove(source_id: str = typer.Argument(..., help="Source ID (from 'nia status')")):
    """Remove a source from syncing."""
    if not is_authenticated():
        console.print("[red]Not logged in. Run [cyan]nia login[/cyan] first.[/red]")
        raise typer.Exit(1)

    # Expand partial ID to full UUID
    sources = get_sources()
    matching = [s for s in sources if s.get("local_folder_id", "").startswith(source_id)]

    if not matching:
        console.print(f"[red]Source not found: {source_id}[/red]")
        console.print("[dim]Run [cyan]nia status[/cyan] to see sources.[/dim]")
        raise typer.Exit(1)

    source = matching[0]
    full_id = source["local_folder_id"]
    display_name = source.get("display_name", source_id)

    success = remove_source(full_id)

    if success:
        console.print(f"[green]✓ Removed:[/green] {display_name}")
    else:
        console.print("[red]Failed to remove. Check the ID with [cyan]nia status[/cyan][/red]")
        raise typer.Exit(1)


@app.command()
def link(
    source_id: str = typer.Argument(..., help="Source ID (from 'nia status')"),
    path: str = typer.Argument(..., help="Local path to link"),
):
    """Link a cloud source to a local folder."""
    if not is_authenticated():
        console.print("[red]Not logged in. Run [cyan]nia login[/cyan] first.[/red]")
        raise typer.Exit(1)

    expanded_path = os.path.expanduser(path)

    if not os.path.exists(expanded_path):
        console.print(f"[red]Path not found: {expanded_path}[/red]")
        raise typer.Exit(1)

    sources = get_sources()
    matching = [s for s in sources if s.get("local_folder_id", "").startswith(source_id)]

    if not matching:
        console.print(f"[red]Source not found: {source_id}[/red]")
        console.print("[dim]Run [cyan]nia status[/cyan] to see sources.[/dim]")
        raise typer.Exit(1)

    source = matching[0]
    full_id = source["local_folder_id"]

    if enable_source_sync(full_id, expanded_path):
        console.print(f"[green]✓ Linked:[/green] {source.get('display_name', source_id)} → {expanded_path}")
        console.print("\n[dim]Run [cyan]nia[/cyan] to start syncing.[/dim]")
    else:
        console.print("[red]Failed to link.[/red]")
        raise typer.Exit(1)


def _resolve_sources(sources: list[dict], log_discoveries: bool = False) -> list[dict]:
    """Resolve paths for sources, auto-detecting known types and folders. Deduplicates by path."""
    resolved = []
    seen_paths = set()
    auto_linked = []

    for src in sources:
        path = src.get("path")
        detected_type = src.get("detected_type")
        display_name = src.get("display_name", "")

        # Priority 1: Use explicit path if set
        # Priority 2: Known database types (iMessage, Safari, etc.)
        # Priority 3: Auto-discover by folder name in watch directories

        if not path and detected_type and detected_type in KNOWN_PATHS:
            path = KNOWN_PATHS[detected_type]

        if not path and display_name:
            # Try to find folder by name in ~/Documents, ~/Projects, etc.
            found_path = find_folder_path(display_name)
            if found_path:
                path = found_path
                auto_linked.append((src, found_path))

        if path:
            expanded = os.path.abspath(os.path.expanduser(path))

            if expanded in seen_paths:
                continue

            if os.path.exists(expanded):
                src["path"] = expanded
                resolved.append(src)
                seen_paths.add(expanded)

    # Auto-enable sync for discovered folders (call API to persist the path)
    for src, found_path in auto_linked:
        if src.get("path") == found_path and not src.get("sync_enabled"):
            if enable_source_sync(src["local_folder_id"], found_path):
                if log_discoveries:
                    console.print(f"  [green]✓ Auto-discovered:[/green] {src.get('display_name')} → {found_path}")

    return resolved


@app.command(name="start", hidden=True)
def daemon(
    watch: bool = typer.Option(True, "--watch/--poll", help="File watching (default) or polling"),
    fallback_interval: int = typer.Option(600, "--fallback", "-f", help="Fallback poll interval (seconds)"),
    refresh_interval: int = typer.Option(30, "--refresh", "-r", help="Source refresh interval (seconds)"),
):
    """Start the Nia Sync Engine."""
    import time
    import signal
    import threading
    from sync import sync_source

    if not is_authenticated():
        console.print("[red]Not logged in.[/red] Run [cyan]nia login[/cyan] first.")
        raise typer.Exit(1)

    running = True
    pending_syncs: set[str] = set()  # source_ids pending sync
    sync_lock = threading.Lock()
    sources_by_id: dict[str, dict] = {}

    def handle_signal(signum, frame):
        nonlocal running
        console.print("\n[dim]Stopping...[/dim]")
        running = False

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    def on_source_changed(source_id: str):
        """Called by file watcher when changes detected."""
        with sync_lock:
            pending_syncs.add(source_id)

    def sync_pending_sources():
        """Process any pending syncs."""
        with sync_lock:
            to_sync = list(pending_syncs)
            pending_syncs.clear()

        if not to_sync:
            return

        # Only log if we're syncing
        total_added = 0
        errors = []

        for source_id in to_sync:
            if source_id not in sources_by_id:
                continue

            src = sources_by_id[source_id]
            result = sync_source(src)

            status = result.get("status", "unknown")

            if status == "success":
                added = result.get("added", 0)
                if added > 0:
                    total_added += added
                    console.print(f"[green]✓ {src.get('display_name', 'Unknown')}[/green] - {added} items synced")
            else:
                error = result.get("error", "unknown error")
                errors.append(f"{src.get('display_name', 'Unknown')}: {error}")

        # Log errors
        for err in errors:
            console.print(f"[red]✗ {err}[/red]")

    def refresh_sources(watcher=None, log_discoveries: bool = False) -> tuple[list[dict], list[str]]:
        """Refresh sources from API and update watchers.

        Returns:
            Tuple of (resolved_sources, newly_added_source_ids)
        """
        nonlocal sources_by_id

        sources = get_sources()
        resolved = _resolve_sources(sources, log_discoveries=log_discoveries)

        # Update sources dict
        new_sources_by_id = {src["local_folder_id"]: src for src in resolved}
        newly_added = []

        # Add watchers for new sources
        if watcher:
            current_watching = set(watcher.watching)
            new_source_ids = set(new_sources_by_id.keys())

            # Add new watchers
            for source_id in new_source_ids - current_watching:
                src = new_sources_by_id[source_id]
                if watcher.watch(source_id, src["path"], on_source_changed):
                    console.print(f"  [dim]+ Watching {src.get('display_name', 'Unknown')}[/dim]")
                    newly_added.append(source_id)

            # Remove old watchers (source deleted from UI)
            for source_id in current_watching - new_source_ids:
                old_name = sources_by_id.get(source_id, {}).get("display_name", source_id[:8])
                watcher.unwatch(source_id)
                console.print(f"  [dim]- Stopped watching {old_name}[/dim]")

        sources_by_id = new_sources_by_id
        return resolved, newly_added

    # Mode selection
    if watch:
        try:
            from watcher import FileWatcher, DirectoryWatcher
            watcher = FileWatcher(debounce_sec=2.0)
            dir_watcher = DirectoryWatcher()
        except ImportError:
            console.print("[yellow]watchdog not installed, falling back to polling mode[/yellow]")
            watch = False
            watcher = None
            dir_watcher = None
    else:
        watcher = None
        dir_watcher = None

    # Initial setup - log any auto-discovered folders
    resolved, _ = refresh_sources(watcher, log_discoveries=True)

    # Track unlinked source names for instant folder detection
    def get_unlinked_names() -> set[str]:
        """Get display names of sources without a local path."""
        sources = get_sources()
        return {
            s.get("display_name", "").lower()
            for s in sources
            if not s.get("path") and s.get("display_name")
        }

    unlinked_names = get_unlinked_names()
    refresh_triggered = threading.Event()

    def on_new_folder(folder_name: str, folder_path: str):
        """Called when a new folder is created in watched directories."""
        if folder_name.lower() in unlinked_names:
            console.print(f"[cyan]Detected new folder:[/cyan] {folder_name}")
            refresh_triggered.set()

    if watch and watcher:
        mode_text = "real-time file watching"

        # Start directory watcher for instant folder detection
        if dir_watcher:
            from config import DEFAULT_WATCH_DIRS
            dir_watcher.watch(DEFAULT_WATCH_DIRS, on_new_folder)
            dir_watcher.start()

        console.print(Panel.fit(
            f"[bold cyan]Nia Sync Engine[/bold cyan]\n\n"
            f"[dim]●[/dim] {mode_text}\n"
            f"[dim]●[/dim] {len(resolved)} source(s) active\n"
            f"[dim]●[/dim] Auto-refresh every {refresh_interval}s\n\n"
            f"[dim]Ctrl+C to stop[/dim]",
            border_style="cyan",
        ))

        # Start file watcher
        watcher.start()

        # Do initial sync
        for src in resolved:
            pending_syncs.add(src["local_folder_id"])
        sync_pending_sources()

        # Main loop: process pending syncs + periodic refresh
        last_refresh = time.time()

        while running:
            # Process any pending syncs from file watcher
            sync_pending_sources()

            # Instant refresh if new folder detected matching an unlinked source
            if refresh_triggered.is_set():
                refresh_triggered.clear()
                _, newly_added = refresh_sources(watcher, log_discoveries=True)
                if newly_added:
                    console.print(f"[green]Linked {len(newly_added)} new source(s)[/green]")
                    # Trigger initial sync for new sources
                    for source_id in newly_added:
                        pending_syncs.add(source_id)
                unlinked_names.clear()
                unlinked_names.update(get_unlinked_names())
                last_refresh = time.time()

            # Periodic refresh to pick up new sources from web UI
            elif time.time() - last_refresh > refresh_interval:
                _, newly_added = refresh_sources(watcher, log_discoveries=True)
                if newly_added:
                    console.print(f"[green]Found {len(newly_added)} new source(s)[/green]")
                    # Trigger initial sync for new sources
                    for source_id in newly_added:
                        pending_syncs.add(source_id)
                unlinked_names.clear()
                unlinked_names.update(get_unlinked_names())
                last_refresh = time.time()

            time.sleep(0.5)

        # Cleanup
        watcher.stop()
        if dir_watcher:
            dir_watcher.stop()

    else:
        # Polling mode (fallback)
        console.print(Panel.fit(
            f"[bold cyan]Nia Sync Engine[/bold cyan] [dim](polling)[/dim]\n\n"
            f"[dim]●[/dim] Sync every {fallback_interval // 60} min\n"
            f"[dim]●[/dim] {len(resolved)} source(s) active\n\n"
            f"[dim]Ctrl+C to stop[/dim]",
            border_style="cyan",
        ))

        sync_count = 0
        while running:
            resolved, _ = refresh_sources()

            sync_count += 1
            console.print(f"\n[bold]Sync #{sync_count}[/bold] - {len(resolved)} source(s)")

            if not resolved:
                console.print("[dim]No syncable sources found locally.[/dim]")
            else:
                results = sync_all_sources(resolved)
                for result in results:
                    path = result.get("path", "unknown")
                    status = result.get("status", "unknown")
                    if status == "success":
                        added = result.get("added", 0)
                        if added > 0:
                            console.print(f"  [green]✓ {path}[/green] - {added} items")
                        else:
                            console.print(f"  [dim]- {path}[/dim] - no changes")
                    else:
                        error = result.get("error", "unknown error")
                        console.print(f"  [red]✗ {path}[/red] - {error}")

            for _ in range(fallback_interval):
                if not running:
                    break
                time.sleep(1)

    console.print("[green]✓ Stopped[/green]")


if __name__ == "__main__":
    app()
