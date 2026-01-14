"""Board commands for managing Kanban board columns."""

import sys
from datetime import UTC, datetime

import click

from .display import console, console_err, display_board_move_result
from ..config import BoardConfig, ConfigurationError, save_project_config
from ..exit_codes import EXIT_API_ERROR, EXIT_CONFIG_ERROR, EXIT_GENERAL_ERROR
from ..git_utils import GitLabRemoteNotFoundError, GitRepositoryNotFoundError, find_project_root
from ..issue_sync import get_gitlab_client, get_project
from ..storage import Issue, StorageError
from . import IID, _format_iid, get_repo_and_config, handle_cli_errors


@click.group()
def board():
    """Manage Kanban board columns."""


@board.command(name="columns")
@click.option("--sync", is_flag=True, help="Refresh column configuration from GitLab")
def board_columns(sync: bool):
    """List or sync Kanban board column configuration.

    Without --sync: Display current column configuration (ordered).
    With --sync: Fetch latest columns from GitLab and update config.
    """
    try:
        repo_root, config = get_repo_and_config()

        if sync:
            console.print("[dim]→[/dim] Fetching kanban board configuration from GitLab...")

            gitlab_client = get_gitlab_client(config)
            project = get_project(gitlab_client, config)

            try:
                boards = project.boards.list()
                columns = []
                if boards:
                    board = boards[0]  # Use first board
                    for board_list in board.lists.list():
                        if hasattr(board_list, 'label') and board_list.label:
                            columns.append(board_list.label['name'])

                if columns:
                    console.print(f"[green]✓[/green] Found {len(columns)} kanban columns")

                    config.board = BoardConfig(columns=columns, last_sync=datetime.now(UTC))
                    save_project_config(config)
                    console.print("[green]✓[/green] Configuration updated\n")
                else:
                    console.print("[yellow]⚠[/yellow] No kanban board columns found")
                    columns = []

            except Exception as e:
                console_err.print(f"[bold red]✗ Failed to fetch board columns:[/bold red] {e}")
                sys.exit(EXIT_API_ERROR)

        # Display current configuration
        if config.board.columns:
            console.print(f"[bold]Kanban Board Columns:[/bold] ({len(config.board.columns)})")
            console.print("  [dim]0.[/dim] [yellow](no column)[/yellow]")
            for i, column in enumerate(config.board.columns, 1):
                console.print(f"  [dim]{i}.[/dim] [cyan]{column}[/cyan]")

            if config.board.last_sync:
                sync_time = config.board.last_sync.strftime("%Y-%m-%d %H:%M:%S")
                console.print(f"\n[dim]Last synced: {sync_time}[/dim]")
            console.print("\n[dim]Use column numbers with 'board move' command (e.g., 'board move 1 2')[/dim]")
        else:
            console.print("[yellow]⚠ No Kanban board columns configured[/yellow]")
            console.print("[dim]Run 'gl-issue-sync board columns --sync' to fetch from GitLab[/dim]")

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


@board.command(name="move")
@click.argument("issue_id", type=IID)
@click.argument("column", required=False)
@click.option("--next", "direction", flag_value="next", help="Move to next column (default)")
@click.option("--back", "--previous", "direction", flag_value="back", help="Move to previous column")
@handle_cli_errors
def board_move(issue_id: int | str, column: str | None, direction: str | None):
    """Move issue between Kanban board columns.

    By default (no flags), moves to the next column.

    Arguments:
        ISSUE_ID: Issue number (e.g., 1 for issue #1, or T1 for temporary issues)
        COLUMN: Column name or number (optional)
            - Column name: "ToDo", "In Progress", etc.
            - 0: Remove from all columns (just "open", no kanban label)
            - 1, 2, 3...: 1-indexed column number (1=first column, 2=second, etc.)

    Examples:
        gl-issue-sync board move 1              # Move to next column
        gl-issue-sync board move 1 --next       # Explicitly move to next
        gl-issue-sync board move 1 --back       # Move to previous column
        gl-issue-sync board move 1 "ToDo"       # Move to specific column by name
        gl-issue-sync board move 1 0            # Remove from all columns
        gl-issue-sync board move 1 2            # Move to 2nd column (In Progress)
        gl-issue-sync board move T1 "ToDo"      # Move temporary issue to column

    Special behaviors:
        - Moving forward from last column: closes issue and removes kanban labels
        - Moving backward when closed: re-opens issue and puts in last column
        - Moving backward from first column: removes kanban labels (stays open)
        - Moving to specific column when closed: re-opens issue first
        - Numbers cannot be used to close issues (use --next from last column)
    """
    repo_root = find_project_root()
    issue = Issue.load(issue_id, repo_root)

    if not issue:
        raise StorageError(f"Issue {_format_iid(issue_id)} not found locally")

    old_col, new_col, state_info = issue.move_to_board_column(
        column=column,
        direction=direction,
        repo_path=repo_root
    )

    display_board_move_result(issue_id, old_col, new_col, state_info)
