"""Lifecycle commands for creating, closing, and deleting issues."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import click

from .display import console, console_err, display_close_result
from ..config import ConfigurationError
from ..exit_codes import EXIT_CONFIG_ERROR, EXIT_GENERAL_ERROR
from ..git_utils import (
    GitLabRemoteNotFoundError,
    GitRepositoryNotFoundError,
    find_project_root,
)
from ..issue_sync import get_gitlab_client, get_project
from ..storage import Issue, KanbanColumn, StorageError
from . import IID, _format_iid, get_repo_and_config, handle_cli_errors


@click.command()
@click.argument("title")
@click.option("--label", multiple=True, help="Add labels (repeatable)")
@click.option("--assignee", multiple=True, help="Add assignees (repeatable)")
@click.option("--description", help="Issue description (short form)")
@click.option("--editor", "-e", is_flag=True, help="Open $EDITOR to write full description")
@click.option("--column", help="Kanban column to place issue in")
@click.option("--milestone", help="Milestone title")
@click.option("--confidential", is_flag=True, help="Mark issue as confidential")
@click.option("--parent", type=int, help="Parent issue IID (for work item hierarchy)")
@handle_cli_errors
def new(
    title: str,
    label: tuple[str, ...],
    assignee: tuple[str, ...],
    description: str | None,
    editor: bool,
    column: str | None,
    milestone: str | None,
    confidential: bool,
    parent: int | None,
):
    """Create a new issue locally.

    Creates a new local issue with temporary ID (T1, T2, etc.) that will be
    created on GitLab when you run 'push'. This allows offline issue creation
    and batch operations.

    Arguments:
        TITLE: Issue title (required)

    Examples:
        gl-issue-sync new "Fix login bug"
        gl-issue-sync new "Add dark mode" --label feature --label ui --column ToDo
        gl-issue-sync new "Improve performance" --description "Database queries are slow"
        gl-issue-sync new "Refactor authentication" --editor
    """
    repo_root = find_project_root()

    final_description = description or ""
    if editor:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
            tmp.write("<!-- Write your issue description below -->\n")
            tmp.write("<!-- Lines starting with <!-- will be removed -->\n\n")
            tmp_path = tmp.name

        try:
            editor_cmd = os.getenv("VISUAL") or os.getenv("EDITOR") or "vi"
            result = subprocess.run([editor_cmd, tmp_path])
            if result.returncode != 0:
                console_err.print(f"[bold red]✗ Editor exited with error code {result.returncode}[/bold red]")
                sys.exit(EXIT_GENERAL_ERROR)

            with open(tmp_path) as f:
                lines = f.readlines()

            content_lines = [line for line in lines if not line.strip().startswith("<!--")]
            final_description = "".join(content_lines).strip()

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    labels_list = list(label)
    if column:
        is_valid, suggestion = KanbanColumn.validate_and_suggest(column, repo_root)
        if not is_valid:
            if suggestion:
                console_err.print(f"[bold red]✗ Invalid column:[/bold red] '{column}'")
                console_err.print(f"[dim]Did you mean '{suggestion}'?[/dim]")
            else:
                console_err.print(f"[bold red]✗ Column not found:[/bold red] '{column}'")
                columns = KanbanColumn.get_column_names(repo_root)
                console_err.print(f"[dim]Available columns: {', '.join(columns)}[/dim]")
            sys.exit(EXIT_GENERAL_ERROR)

        labels_list.append(column)

    issue = Issue.create_new(
        title=title,
        description=final_description,
        labels=labels_list if labels_list else None,
        assignees=list(assignee) if assignee else None,
        milestone=milestone,
        confidential=confidential,
        parent_iid=parent,
        repo_path=repo_root,
    )

    console.print(f"\n[green]✓ Created issue {issue.iid} locally[/green]")
    console.print(f"[bold]Title:[/bold] {issue.title}")

    if labels_list:
        console.print(f"[bold]Labels:[/bold] {', '.join(labels_list)}")

    if assignee:
        console.print(f"[bold]Assignees:[/bold] {', '.join(assignee)}")

    if column:
        console.print(f"[bold]Column:[/bold] {column}")

    if milestone:
        console.print(f"[bold]Milestone:[/bold] {milestone}")

    if parent:
        console.print(f"[bold]Parent:[/bold] #{parent}")

    if final_description:
        desc_preview = final_description[:100]
        ellipsis = '...' if len(final_description) > 100 else ''
        console.print(f"[bold]Description:[/bold] {desc_preview}{ellipsis}")

    console.print("\n[yellow]Run 'gl-issue-sync push' to create on GitLab[/yellow]\n")


@click.command()
@click.argument("issue_id", type=IID)
@handle_cli_errors
def close(issue_id: int | str):
    """Close an issue and remove all Kanban labels.

    Arguments:
        ISSUE_ID: Issue number (e.g., 1 for issue #1, or T1 for temporary issues)

    This command:
        - Sets the issue state to "closed"
        - Removes all Kanban board column labels
        - Preserves other labels (like "bug", "feature", etc.)
        - Pushes the changes to GitLab
    """
    repo_root = find_project_root()
    issue = Issue.load(issue_id, repo_root)

    if not issue:
        raise StorageError(f"Issue {_format_iid(issue_id)} not found locally")

    # Capture state before closing (for display)
    was_already_closed = issue.state == "closed"
    column_names = KanbanColumn.get_column_names(repo_root)
    kanban_labels = [label for label in issue.labels if label in column_names]

    # Close issue (idempotent - safe to call even if already closed)
    issue.close(remove_kanban_labels=True, repo_path=repo_root)

    display_close_result(issue_id, issue.title, was_already_closed, kanban_labels)


@click.command()
@click.argument("issue_ids", nargs=-1, required=True, type=int)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def danger_delete(issue_ids: tuple[int, ...], yes: bool):
    """🚨 DANGER: Permanently delete issues from GitLab (cannot be undone!).

    Arguments:
        ISSUE_IDS: One or more issue numbers to delete (e.g., 42 43 44)

    ⚠️  WARNING: This permanently deletes issues from GitLab.
    ⚠️  Deleted issues CANNOT be recovered!
    ⚠️  Use with extreme caution!

    Examples:
        gl-issue-sync danger_delete 42        # Delete issue #42 (with confirmation)
        gl-issue-sync danger_delete 42 43 44  # Delete multiple issues
        gl-issue-sync danger_delete 42 --yes  # Skip confirmation
    """
    try:
        # Get repository and config
        repo_root, config = get_repo_and_config()

        if not config:
            console_err.print("[bold red]✗ Configuration Error:[/bold red] No configuration found")
            console_err.print("[dim]Run 'gl-issue-sync init' first.[/dim]")
            sys.exit(EXIT_CONFIG_ERROR)

        # Show warning
        console.print("\n[bold red]🚨 DANGER ZONE 🚨[/bold red]")
        console.print(f"[yellow]You are about to PERMANENTLY DELETE {len(issue_ids)} issue(s):[/yellow]")
        for iid in sorted(issue_ids):
            console.print(f"  • Issue #{iid}")
        console.print("\n[bold red]⚠️  This action CANNOT be undone![/bold red]")

        # Confirmation
        if not yes:
            console.print()
            confirm = click.confirm("Are you absolutely sure you want to delete these issues?", default=False)
            if not confirm:
                console.print("[dim]Cancelled.[/dim]")
                sys.exit(0)

        # Connect to GitLab
        gl = get_gitlab_client(config)
        project = get_project(gl, config)

        # Delete issues
        console.print(f"\n[bold]💀 Deleting {len(issue_ids)} issue(s)...[/bold]\n")

        deleted = []
        failed = []

        for iid in sorted(issue_ids):
            try:
                gl_issue = project.issues.get(iid)
                gl_issue.delete()
                deleted.append(iid)
                console.print(f"[green]✓ Deleted issue #{iid}[/green]")

                # Also delete local file if it exists
                for directory in ["opened", "closed"]:
                    local_path = repo_root / ".issues" / directory / f"{iid}.md"
                    if local_path.exists():
                        local_path.unlink()
                        console.print(f"[dim]  Removed local file: {local_path.name}[/dim]")

                # Delete original snapshot if it exists
                original_path = repo_root / ".issues" / ".sync" / "originals" / f"{iid}.md"
                if original_path.exists():
                    original_path.unlink()

            except Exception as e:
                failed.append((iid, str(e)))
                console_err.print(f"[red]✗ Failed to delete issue #{iid}: {e}[/red]")

        # Summary
        console.print("\n[bold]Summary:[/bold]")
        console.print(f"  Deleted: [green]{len(deleted)}[/green]/{len(issue_ids)}")
        if failed:
            console.print(f"  Failed:  [red]{len(failed)}[/red]")
            for iid, error in failed[:5]:
                console_err.print(f"    #{iid}: {error}")

        if deleted:
            console.print("\n[yellow]💡 Tip: Run 'gl-issue-sync pull' to sync the deletion locally[/yellow]")

    except (GitRepositoryNotFoundError, GitLabRemoteNotFoundError) as e:
        console_err.print(f"[bold red]✗ Git Error:[/bold red] {e}")
        sys.exit(EXIT_CONFIG_ERROR)
    except ConfigurationError as e:
        console_err.print(f"[bold red]✗ Configuration Error:[/bold red] {e}")
        console_err.print("[dim]Run 'gl-issue-sync init' first.[/dim]")
        sys.exit(EXIT_CONFIG_ERROR)
    except Exception as e:
        console_err.print(f"[bold red]✗ Unexpected Error:[/bold red] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(EXIT_GENERAL_ERROR)
