"""Status command for GitLab issue synchronization."""

import sys

import click

from .display import console, console_err
from ..config import ConfigurationError, get_config_file_path
from ..exit_codes import EXIT_CONFIG_ERROR, EXIT_GENERAL_ERROR
from ..git_utils import GitLabRemoteNotFoundError, GitRepositoryNotFoundError, get_gitlab_remote_info
from ..storage import ISSUE_STATE_CLOSED, ISSUE_STATE_OPENED, Issue, StorageError
from . import get_repo_and_config


@click.command()
def status():
    """Show synchronization status and configuration.

    Displays:
    - GitLab instance and project info
    - Number of local issues (open/closed)
    - Kanban board columns
    - Configuration location
    """
    console.print("\n[bold blue]📊 GitLab Issue Sync Status[/bold blue]\n")

    try:
        repo_root, config = get_repo_and_config()

        if not config:
            remote_info = get_gitlab_remote_info(repo_root)
            raise ConfigurationError(
                f"No configuration found for {remote_info.full_path}. "
                "Run 'gl-issue-sync init' first."
            )

        # Project info
        console.print("[bold]Project Information:[/bold]")
        console.print(f"  Instance: [cyan]{config.instance_url}[/cyan]")
        console.print(f"  Project: [cyan]{config.full_path}[/cyan]")
        console.print(f"  Repository: [dim]{repo_root}[/dim]\n")

        # Count local issues
        open_issues = Issue.list_all(state=ISSUE_STATE_OPENED, repo_path=repo_root)
        closed_issues = Issue.list_all(state=ISSUE_STATE_CLOSED, repo_path=repo_root)

        console.print("[bold]Local Issues:[/bold]")

        # Group open issues by Kanban column
        if config.board.columns:
            columns_dict = {col: [] for col in config.board.columns}
            no_column_issues = []

            for issue in open_issues:
                issue_columns = [label for label in issue.labels if label in config.board.columns]
                if issue_columns:
                    # Issue has a kanban column label
                    columns_dict[issue_columns[0]].append(issue)
                else:
                    # Issue has no kanban column
                    no_column_issues.append(issue)

            # Display backlog first
            if no_column_issues:
                console.print(f"  Backlog: [yellow]{len(no_column_issues)}[/yellow]")

            # Display issues by column in order
            for column in config.board.columns:
                count = len(columns_dict[column])
                if count > 0:
                    console.print(f"  {column}: [cyan]{count}[/cyan]")

            # Display closed last
            if closed_issues:
                console.print(f"  Closed: [dim]{len(closed_issues)}[/dim]")
        else:
            console.print(f"  Open: [green]{len(open_issues)}[/green]")
            console.print(f"  Closed: [dim]{len(closed_issues)}[/dim]")

        console.print(f"  Total: {len(open_issues) + len(closed_issues)}\n")

        # Kanban board columns
        if config.board.columns:
            columns = config.board.columns
            console.print(f"[bold]Kanban Board Columns:[/bold] ({len(columns)})")
            for i, column in enumerate(columns, 1):
                console.print(f"  {i}. [cyan]{column}[/cyan]")
        else:
            console.print("[bold]Kanban Board:[/bold] [dim]Not configured[/dim]")

        console.print()

        # Configuration file location
        config_path = get_config_file_path()
        console.print(f"[dim]Configuration: {config_path}[/dim]\n")

    except (GitRepositoryNotFoundError, GitLabRemoteNotFoundError) as e:
        console_err.print(f"[bold red]✗ Git Error:[/bold red] {e}")
        console_err.print("[dim]Make sure you're in a git repository with a GitLab remote.[/dim]")
        sys.exit(EXIT_CONFIG_ERROR)
    except ConfigurationError as e:
        console_err.print(f"[bold red]✗ Not Initialized:[/bold red] {e}")
        console_err.print("\n[dim]Run 'gl-issue-sync init' to initialize this repository.[/dim]")
        sys.exit(EXIT_CONFIG_ERROR)
    except StorageError as e:
        console_err.print(f"[bold red]✗ Storage Error:[/bold red] {e}")
        sys.exit(EXIT_GENERAL_ERROR)
    except Exception as e:
        console_err.print(f"[bold red]✗ Unexpected Error:[/bold red] {e}")
        sys.exit(EXIT_GENERAL_ERROR)
