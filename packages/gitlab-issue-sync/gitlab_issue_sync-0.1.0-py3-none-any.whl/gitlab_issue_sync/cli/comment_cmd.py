"""Comment command for adding comments to issues."""

import click

from .display import display_comment_result
from ..git_utils import find_project_root
from ..storage import Issue, StorageError
from . import IID, _format_iid, handle_cli_errors


@click.command()
@click.argument("issue_iid", type=IID)
@click.argument("message")
@handle_cli_errors
def comment(issue_iid: int | str, message: str):
    """Add a comment to an issue locally.

    Uses the GitLab API to fetch your username and adds a comment with the
    current timestamp. After adding the comment, use 'push' to sync it to GitLab.

    Arguments:
        ISSUE_IID: Issue number (e.g., 1 for issue #1, or T1 for temporary issues)
        MESSAGE: Comment text (use quotes for multi-word messages)

    Example:
        gl-issue-sync comment 1 "This looks good to me!"
        gl-issue-sync comment T1 "Added to local issue before push"
    """
    repo_root = find_project_root()
    issue = Issue.load(issue_iid, repo_root)

    if not issue:
        raise StorageError(f"Issue {_format_iid(issue_iid)} not found locally")

    # Add comment (domain method handles username from config and saving)
    comment_obj = issue.add_comment(body=message, repo_path=repo_root)

    display_comment_result(issue_iid, comment_obj)
