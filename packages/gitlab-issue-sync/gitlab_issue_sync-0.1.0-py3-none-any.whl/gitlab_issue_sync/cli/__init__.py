"""Command-line interface for GitLab issue synchronization."""

import re
import sys
from functools import wraps

import click

from .display import console_err
from ..config import ConfigurationError
from ..exit_codes import (
    EXIT_API_ERROR,
    EXIT_AUTH_ERROR,
    EXIT_CONFIG_ERROR,
    EXIT_GENERAL_ERROR,
)
from ..git_utils import (
    GitLabRemoteNotFoundError,
    GitRepositoryNotFoundError,
    find_project_root,
    get_gitlab_remote_info,
)
from ..issue_sync import (
    AuthenticationError,
    SyncError,
    get_gitlab_client,
    get_project,
)
from ..storage import StorageError
from ..config import get_project_config


# ===== IID Parameter Type =====


class IIDParamType(click.ParamType):
    """Click parameter type that accepts both numeric IIDs and temporary IIDs (T prefix).

    Examples:
        - "42" -> 42 (int)
        - "T1" -> "T1" (str)
        - "t1" -> "T1" (str, normalized to uppercase)
    """

    name = "iid"

    def convert(self, value, param, ctx):
        if value is None:
            return None

        # Already converted (e.g., from default)
        if isinstance(value, int):
            return value

        value_str = str(value).strip()

        # Check for temporary IID (T prefix)
        if re.match(r"^[Tt]\d+$", value_str):
            return value_str.upper()  # Normalize to uppercase

        # Try to parse as integer
        try:
            return int(value_str)
        except ValueError:
            self.fail(
                f"'{value}' is not a valid issue IID. "
                f"Expected a number (e.g., 42) or temporary IID (e.g., T1).",
                param,
                ctx,
            )


# Singleton instance for convenience
IID = IIDParamType()


def _format_iid(iid: int | str) -> str:
    """Format IID for display in messages.

    Numeric IIDs get # prefix, temporary IIDs stay as-is.

    Examples:
        42 -> "#42"
        "T1" -> "T1"
    """
    if isinstance(iid, int):
        return f"#{iid}"
    return str(iid)


def _try_parse_iid(value: str) -> int | str | None:
    """Try to parse a string as an IID (numeric or T-prefixed).

    Returns:
        - int if the value is a valid numeric IID
        - str if the value is a valid temporary IID (T prefix)
        - None if the value is neither (e.g., a subcommand like "list")

    Examples:
        "42" -> 42
        "T1" -> "T1"
        "list" -> None
    """
    value = value.strip()

    # Check for temporary IID (T prefix)
    if re.match(r"^[Tt]\d+$", value):
        return value.upper()

    # Try to parse as integer
    try:
        return int(value)
    except ValueError:
        return None


# ===== Error Handling =====


def handle_cli_errors(func):
    """Decorator to handle common CLI exceptions uniformly.

    This decorator catches all common exception types and provides
    consistent error messaging and exit codes across all CLI commands.

    Exit codes:
        - EXIT_CONFIG_ERROR (2): Configuration/git errors
        - EXIT_AUTH_ERROR (3): Authentication errors
        - EXIT_API_ERROR (4): GitLab API/sync errors
        - EXIT_GENERAL_ERROR (1): Storage/validation/unexpected errors

    All errors print to stderr.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (GitRepositoryNotFoundError, GitLabRemoteNotFoundError) as e:
            console_err.print(f"\n[bold red]✗ Git Error:[/bold red] {e}")
            console_err.print("[dim]Make sure you're in a git repository with a GitLab remote.[/dim]")
            sys.exit(EXIT_CONFIG_ERROR)
        except ConfigurationError as e:
            console_err.print(f"\n[bold red]✗ Configuration Error:[/bold red] {e}")
            console_err.print("[dim]Run 'gl-issue-sync init' first.[/dim]")
            sys.exit(EXIT_CONFIG_ERROR)
        except AuthenticationError as e:
            console_err.print(f"\n[bold red]✗ Authentication Error:[/bold red] {e}")
            console_err.print("[dim]Check your GitLab token and permissions.[/dim]")
            sys.exit(EXIT_AUTH_ERROR)
        except StorageError as e:
            console_err.print(f"\n[bold red]✗ Storage Error:[/bold red] {e}")
            sys.exit(EXIT_GENERAL_ERROR)
        except SyncError as e:
            console_err.print(f"\n[bold red]✗ Sync Error:[/bold red] {e}")
            sys.exit(EXIT_API_ERROR)
        except ValueError as e:
            console_err.print(f"\n[bold red]✗ Validation Error:[/bold red] {e}")
            sys.exit(EXIT_GENERAL_ERROR)
        except Exception as e:
            console_err.print(f"\n[bold red]✗ Unexpected Error:[/bold red] {e}")
            import traceback
            traceback.print_exc()
            sys.exit(EXIT_GENERAL_ERROR)
    return wrapper


# ===== Helper Functions =====


def get_repo_and_config():
    """Get repository root and project configuration."""
    repo_root = find_project_root()
    remote_info = get_gitlab_remote_info(repo_root)
    config = get_project_config(remote_info.instance_url, remote_info.namespace, remote_info.project)
    return repo_root, config


def setup_gitlab_client():
    """Setup GitLab client and project, ensuring configuration exists."""
    repo_root, config = get_repo_and_config()

    if not config:
        remote_info = get_gitlab_remote_info(repo_root)
        raise ConfigurationError(
            f"No configuration found for {remote_info.full_path}. "
            "Run 'gl-issue-sync init' first."
        )

    gitlab_client = get_gitlab_client(config)
    project = get_project(gitlab_client, config)

    return repo_root, config, gitlab_client, project


# ===== Main CLI Group =====


@click.group()
@click.version_option(version="0.1.0", prog_name="gl-issue-sync")
def main():
    """GitLab issue synchronization tool.

    Sync GitLab issues to local markdown files with bidirectional synchronization.
    """
    pass


# Import and register subcommands
# All commands have been moved to dedicated submodules

from .board_cmds import board
from .comment_cmd import comment
from .conflicts_cmds import conflicts
from .init_cmd import init
from .lifecycle_cmds import close, danger_delete, new
from .list_cmd import list_issues_cmd
from .metadata_cmds import assignees, label, linked, metadata, milestone, parent
from .show_cmd import show
from .status_cmd import status
from .sync_cmds import pull, push, sync
from .wiki_cmds import wiki

# Register all commands with the main group
main.add_command(init)
main.add_command(pull)
main.add_command(status)
main.add_command(conflicts)
main.add_command(show)
main.add_command(list_issues_cmd, name="list")
main.add_command(push)
main.add_command(sync)
main.add_command(comment)
main.add_command(new)
main.add_command(board)
main.add_command(close)
main.add_command(danger_delete)
main.add_command(metadata)
main.add_command(assignees)
main.add_command(linked)
main.add_command(parent)
main.add_command(label)
main.add_command(milestone)
main.add_command(wiki)
