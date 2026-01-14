"""List command for browsing issues."""

import sys

import click

from .display import console_err, display_issues_table
from ..exit_codes import EXIT_GENERAL_ERROR
from ..git_utils import find_project_root
from ..storage import Issue, KanbanColumn, Label
from . import handle_cli_errors


@click.command("list")
@click.option(
    "--state",
    type=click.Choice(["opened", "closed", "all"]),
    default="opened",
    help="Filter by state (default: opened)"
)
@click.option(
    "--column",
    type=str,
    multiple=True,
    help="Filter by kanban column (repeatable, OR logic - name or numeric index, 0=no column)"
)
@click.option(
    "--label",
    multiple=True,
    help="Filter by label (repeatable, AND logic)"
)
@click.option(
    "--milestone",
    multiple=True,
    help="Filter by milestone (repeatable, OR logic)"
)
@click.option(
    "--with-milestone",
    is_flag=True,
    help="Display milestone column in output"
)
@click.option(
    "--with-assignees",
    is_flag=True,
    help="Display assignees column in output"
)
@click.option(
    "--no-column",
    is_flag=True,
    help="Hide kanban column from output"
)
@click.option(
    "--no-labels",
    is_flag=True,
    help="Hide labels column from output"
)
@handle_cli_errors
def list_issues_cmd(
    state: str,
    column: tuple[str, ...],
    label: tuple[str, ...],
    milestone: tuple[str, ...],
    with_milestone: bool,
    with_assignees: bool,
    no_column: bool,
    no_labels: bool,
):
    """List issues with optional filters for browsing.

    Display a table of issues with key metadata, making it easy to browse
    and find issues without viewing full details.

    Examples:

        # List all open issues (default)
        gl-issue-sync list

        # List all issues (open and closed)
        gl-issue-sync list --state all

        # List issues in "In Progress" column
        gl-issue-sync list --column "In Progress"

        # List issues in multiple columns (OR logic)
        gl-issue-sync list --column "In Progress" --column "Doing"

        # List issues by column index (OR logic)
        gl-issue-sync list --column 2 --column 3

        # List issues in backlog (no column)
        gl-issue-sync list --column 0

        # List bugs with urgent label
        gl-issue-sync list --label bug --label urgent

        # List issues in specific milestone
        gl-issue-sync list --milestone "Milestone 1: Foundation"

        # List issues in multiple milestones (OR logic)
        gl-issue-sync list --milestone "Milestone 1: Foundation" --milestone "Milestone 2: Core Sync"

        # Display milestone column
        gl-issue-sync list --with-milestone

        # Combine filters
        gl-issue-sync list --state opened --column "ToDo" --label bug --milestone "Milestone 2: Core Sync"
    """
    repo_root = find_project_root()

    state_filter = None if state == "all" else state

    if column:
        kanban_columns = KanbanColumn.get_column_names(repo_root)

        for col in column:
            if col.isdigit():
                column_index = int(col)
                if not (0 <= column_index <= len(kanban_columns)):
                    console_err.print(f"[bold red]✗ Invalid column index:[/bold red] {column_index}")
                    console_err.print(f"[dim]Valid range: 0-{len(kanban_columns)}[/dim]")
                    sys.exit(EXIT_GENERAL_ERROR)
            elif col not in kanban_columns:
                console_err.print(f"[bold red]✗ Unknown column:[/bold red] {col}")
                console_err.print(f"[dim]Available columns: {', '.join(kanban_columns)}[/dim]")
                sys.exit(EXIT_GENERAL_ERROR)

    issues = Issue.filter(
        state=state_filter,
        column=list(column) if column else None,
        labels=list(label) if label else None,
        milestones=list(milestone) if milestone else None,
        repo_path=repo_root,
    )

    label_colors = Label.get_colors_map(repo_root)
    kanban_columns = KanbanColumn.get_column_names(repo_root)
    display_issues_table(
        issues,
        label_colors,
        kanban_columns,
        no_column=no_column,
        no_labels=no_labels,
        with_milestone=with_milestone,
        with_assignees=with_assignees,
        repo_path=repo_root,
    )
