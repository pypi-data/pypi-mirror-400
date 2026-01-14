"""Conflicts commands for managing sync conflicts."""

import sys

import click

from .display import console, console_err, display_conflict_details, display_conflicts
from ..exit_codes import EXIT_GENERAL_ERROR
from ..git_utils import find_project_root
from ..storage import Conflict, Issue
from . import IID, handle_cli_errors


@click.group()
def conflicts():
    """Manage sync conflicts.

    Conflicts occur when both local and remote versions have been modified
    since the last sync (BOTH_MODIFIED state).

    Use 'conflicts list' to see all unresolved conflicts.
    Use 'conflicts resolve <IID>' to mark a conflict as resolved after
    manually editing the issue file.
    """
    pass


@conflicts.command(name="list")
@handle_cli_errors
def conflicts_list():
    """List unresolved conflicts.

    Shows all issues with sync conflicts that require manual resolution.
    Conflicts occur when both local and remote versions have been modified
    since the last sync.
    """
    repo_root = find_project_root()
    conflict_list = Conflict.list_all(repo_path=repo_root)
    display_conflicts(conflict_list, repo_root)


@conflicts.command(name="show")
@click.argument("iid", type=IID)
@handle_cli_errors
def conflicts_show(iid: int | str):
    """Show detailed information about a conflict.

    Displays the local and remote versions of the conflicting issue, making
    it easier to understand what needs to be resolved. Shows file locations
    for all three versions (local, remote cache, original snapshot).
    """
    repo_root = find_project_root()

    # Check if issue is in conflict state
    conflict = Conflict.load(iid, repo_path=repo_root)
    if conflict is None:
        console_err.print(f"[bold red]✗ Error:[/bold red] Issue #{iid} is not in conflict state")
        console_err.print(f"  Run 'gl-issue-sync conflicts list' to see all conflicts")
        sys.exit(EXIT_GENERAL_ERROR)

    # Load all three versions
    local = Issue.load(iid, repo_root)
    remote = conflict.load_cached_remote(repo_root)
    original = Issue.backend.load_original(iid, repo_root)

    if not local or not remote:
        console_err.print(f"[bold red]✗ Error:[/bold red] Cannot load issue data for #{iid}")
        sys.exit(EXIT_GENERAL_ERROR)

    display_conflict_details(conflict, local, remote, original, repo_root)


@conflicts.command(name="resolve")
@click.argument("iid", type=IID)
@handle_cli_errors
def conflicts_resolve(iid: int | str):
    """Mark a conflict as resolved after manual editing.

    After manually editing .issues/opened/<iid>.md to resolve the conflict,
    use this command to update the original snapshot so the next push will
    succeed.

    This command:
    1. Verifies the issue is in conflict state
    2. Loads the cached remote version (works offline)
    3. Updates the original snapshot to match the remote
    4. Removes the issue from conflicts.json
    5. Cleans up cached remote file

    After running this command, you can push your resolved changes with
    'gl-issue-sync push'.

    Args:
        iid: The issue IID to mark as resolved
    """
    repo_root = find_project_root()

    # Convert temporary IDs to real IIDs if needed
    if isinstance(iid, str) and iid.startswith("T"):
        console_err.print("[bold red]✗ Error:[/bold red] Temporary issues (T*) cannot have conflicts")
        console_err.print("  Conflicts only occur for issues that exist on GitLab")
        sys.exit(EXIT_GENERAL_ERROR)

    # 1. Check if issue is in conflict state
    conflict = Conflict.load(iid, repo_path=repo_root)
    if conflict is None:
        console_err.print(f"[bold red]✗ Error:[/bold red] Issue #{iid} is not in conflict state")
        console_err.print(f"  Run 'gl-issue-sync conflicts list' to see all conflicts")
        sys.exit(EXIT_GENERAL_ERROR)

    # 2. Load cached remote (no network!)
    remote = conflict.load_cached_remote(repo_root)
    if remote is None:
        console_err.print(f"[bold red]✗ Error:[/bold red] Remote cache missing for issue #{iid}")
        console_err.print(f"  Re-run 'gl-issue-sync push' to detect and cache the conflict")
        sys.exit(EXIT_GENERAL_ERROR)

    # 3. Verify local issue still exists
    local = Issue.load(iid, repo_root)
    if local is None:
        console_err.print(f"[bold red]✗ Error:[/bold red] Issue #{iid} not found locally")
        console_err.print(f"  Cannot resolve conflict for non-existent issue")
        sys.exit(EXIT_GENERAL_ERROR)

    # 4. Update original snapshot to match cached remote
    Issue.backend.save_original(remote, repo_root)

    # 5. Remove from conflicts.json and delete cached remote
    conflict.delete(repo_root)

    # 6. Report success
    console.print(f"[green]✓[/green] Issue #{iid} marked as resolved")
    console.print(f"  Original snapshot updated to match remote")
    console.print(f"  Conflict state cleared")
    console.print(f"\n[dim]Next steps:[/dim]")
    console.print(f"  Run [bold]gl-issue-sync push[/bold] to sync your changes to GitLab")
