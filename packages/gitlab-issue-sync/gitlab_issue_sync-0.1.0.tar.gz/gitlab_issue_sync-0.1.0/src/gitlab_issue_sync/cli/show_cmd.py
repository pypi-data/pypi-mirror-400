"""Show command for displaying issue details."""

import click

from .display import display_issue
from ..git_utils import find_project_root
from ..storage import Issue, Label, StorageError
from . import IID, _format_iid, handle_cli_errors


@click.command()
@click.argument("iid", type=IID)
@handle_cli_errors
def show(iid: int | str):
    """Display detailed information about a specific issue.

    Args:
        iid: The issue IID (issue number or temporary ID like T1) to display
    """
    repo_root = find_project_root()
    issue = Issue.load(iid, repo_root)

    if not issue:
        raise StorageError(f"Issue {_format_iid(iid)} not found locally")

    label_colors = Label.get_colors_map(repo_root)
    display_issue(issue, label_colors, repo_root)
