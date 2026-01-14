"""Wiki repository management using GitPython.

This module provides utilities for managing GitLab project wikis as git repositories.
GitLab wikis are separate git repositories (.wiki.git) that can be cloned as a
subdirectory within the main project.
"""

from pathlib import Path

from git import GitCommandError, InvalidGitRepositoryError, Repo
from git.exc import NoSuchPathError

from .git_utils import get_gitlab_remote_info


class WikiError(Exception):
    """Base exception for wiki operations."""


class WikiNotClonedError(WikiError):
    """Raised when wiki operations are attempted but wiki is not cloned."""


class WikiAlreadyExistsError(WikiError):
    """Raised when trying to clone wiki but wiki/ directory already exists."""


class WikiCloneError(WikiError):
    """Raised when wiki cloning fails."""


class WikiSyncError(WikiError):
    """Raised when wiki pull/push operations fail."""


def get_wiki_url(project_url: str) -> str:
    """Convert a GitLab project URL to its wiki repository URL.

    GitLab wiki repositories follow the pattern: {project_url}.wiki.git

    Args:
        project_url: The project remote URL (SSH or HTTPS format)

    Returns:
        The wiki repository URL in the same format as the input

    Examples:
        >>> get_wiki_url("git@gitlab.com:owner/project.git")
        'git@gitlab.com:owner/project.wiki.git'
        >>> get_wiki_url("https://gitlab.com/owner/project.git")
        'https://gitlab.com/owner/project.wiki.git'
        >>> get_wiki_url("https://gitlab.com/owner/project")
        'https://gitlab.com/owner/project.wiki.git'
    """
    # Remove .git suffix if present, then add .wiki.git
    if project_url.endswith(".git"):
        base_url = project_url[:-4]  # Remove .git
    else:
        base_url = project_url

    return f"{base_url}.wiki.git"


def get_wiki_path(repo_path: Path) -> Path:
    """Get the path to the wiki subdirectory.

    Args:
        repo_path: Path to the main repository root

    Returns:
        Path to the wiki/ subdirectory
    """
    return repo_path / "wiki"


def is_wiki_cloned(repo_path: Path) -> bool:
    """Check if the wiki repository is cloned.

    Args:
        repo_path: Path to the main repository root

    Returns:
        True if wiki/ exists and is a valid git repository
    """
    wiki_path = get_wiki_path(repo_path)
    if not wiki_path.exists():
        return False

    try:
        Repo(wiki_path)
        return True
    except (InvalidGitRepositoryError, NoSuchPathError):
        return False


def clone_wiki(repo_path: Path, remote_name: str = "origin") -> Path:
    """Clone the wiki repository into the wiki/ subdirectory.

    Args:
        repo_path: Path to the main repository root
        remote_name: Name of the remote to use for wiki URL detection

    Returns:
        Path to the cloned wiki repository

    Raises:
        WikiAlreadyExistsError: If wiki/ directory already exists
        WikiCloneError: If cloning fails (e.g., wiki not enabled, auth issues)
    """
    wiki_path = get_wiki_path(repo_path)

    # Check if wiki already exists
    if wiki_path.exists():
        if is_wiki_cloned(repo_path):
            raise WikiAlreadyExistsError(f"Wiki already cloned at {wiki_path}")
        raise WikiAlreadyExistsError(f"wiki/ directory exists but is not a valid git repository: {wiki_path}")

    # Validate that the remote exists (will raise GitLabRemoteNotFoundError if not)
    get_gitlab_remote_info(repo_path, remote_name)

    # Get the raw URL from the repo to preserve SSH/HTTPS format
    main_repo = Repo(repo_path)
    remote = main_repo.remotes[remote_name]
    project_url = remote.url

    wiki_url = get_wiki_url(project_url)

    # Clone the wiki repository
    try:
        Repo.clone_from(wiki_url, wiki_path)
    except GitCommandError as e:
        # Clean up partial clone if it exists
        if wiki_path.exists():
            import shutil
            shutil.rmtree(wiki_path)

        # Provide helpful error message
        if "Repository not found" in str(e) or "does not exist" in str(e):
            raise WikiCloneError(
                f"Wiki repository not found. Make sure the wiki is enabled for this project.\n"
                f"Wiki URL: {wiki_url}"
            ) from e
        if "Authentication failed" in str(e) or "Permission denied" in str(e):
            raise WikiCloneError(
                f"Authentication failed when cloning wiki. Check your credentials.\n"
                f"Wiki URL: {wiki_url}"
            ) from e
        raise WikiCloneError(f"Failed to clone wiki repository: {e}") from e

    return wiki_path


def pull_wiki(repo_path: Path) -> str:
    """Pull latest changes from the wiki remote.

    Args:
        repo_path: Path to the main repository root

    Returns:
        Summary message describing what happened

    Raises:
        WikiNotClonedError: If wiki is not cloned
        WikiSyncError: If pull fails
    """
    wiki_path = get_wiki_path(repo_path)

    if not is_wiki_cloned(repo_path):
        raise WikiNotClonedError("Wiki not cloned. Run 'gl-issue-sync wiki clone' first.")

    try:
        wiki_repo = Repo(wiki_path)

        # Check if there's a remote to pull from
        if "origin" not in wiki_repo.remotes:
            raise WikiSyncError("No 'origin' remote configured for wiki repository")

        # Pull from origin
        origin = wiki_repo.remotes.origin
        fetch_info = origin.pull()

        # Generate summary message
        if not fetch_info:
            return "Already up to date."

        # Count changes
        changes = []
        for info in fetch_info:
            if info.flags & info.HEAD_UPTODATE:
                continue
            if info.flags & info.NEW_HEAD:
                changes.append("new branch")
            elif info.flags & info.FAST_FORWARD:
                changes.append("updated")

        if changes:
            return f"Wiki updated: {', '.join(changes)}"
        return "Already up to date."

    except GitCommandError as e:
        if "Could not read from remote repository" in str(e):
            raise WikiSyncError("Cannot connect to remote wiki repository. Check your network connection.") from e
        raise WikiSyncError(f"Failed to pull wiki changes: {e}") from e


def push_wiki(repo_path: Path) -> str:
    """Push local wiki changes to the remote.

    Args:
        repo_path: Path to the main repository root

    Returns:
        Summary message describing what happened

    Raises:
        WikiNotClonedError: If wiki is not cloned
        WikiSyncError: If push fails
    """
    wiki_path = get_wiki_path(repo_path)

    if not is_wiki_cloned(repo_path):
        raise WikiNotClonedError("Wiki not cloned. Run 'gl-issue-sync wiki clone' first.")

    try:
        wiki_repo = Repo(wiki_path)

        # Check if there's a remote to push to
        if "origin" not in wiki_repo.remotes:
            raise WikiSyncError("No 'origin' remote configured for wiki repository")

        # Check if there are commits to push
        origin = wiki_repo.remotes.origin

        # Fetch first to check if we're ahead
        origin.fetch()

        # Get the tracking branch
        tracking_branch = wiki_repo.active_branch.tracking_branch()
        if tracking_branch is None:
            # No tracking branch, try to push and set upstream
            push_info = origin.push(set_upstream=True)
        else:
            # Check if we have commits to push
            commits_ahead = list(wiki_repo.iter_commits(f"{tracking_branch.name}..HEAD"))
            if not commits_ahead:
                return "Nothing to push."

            push_info = origin.push()

        # Check push results
        if push_info:
            for info in push_info:
                if info.flags & info.ERROR:
                    raise WikiSyncError(f"Push failed: {info.summary}")
                if info.flags & info.REJECTED:
                    raise WikiSyncError(f"Push rejected: {info.summary}. Try pulling first.")
                if info.flags & info.UP_TO_DATE:
                    return "Nothing to push."

        return "Wiki changes pushed successfully."

    except GitCommandError as e:
        if "Could not read from remote repository" in str(e):
            raise WikiSyncError("Cannot connect to remote wiki repository. Check your network connection.") from e
        if "rejected" in str(e).lower():
            raise WikiSyncError("Push rejected. Try pulling first to merge remote changes.") from e
        raise WikiSyncError(f"Failed to push wiki changes: {e}") from e


def commit_wiki(repo_path: Path, message: str) -> str:
    """Commit all changes in the wiki repository.

    Args:
        repo_path: Path to the main repository root
        message: Commit message

    Returns:
        Summary message describing what happened

    Raises:
        WikiNotClonedError: If wiki is not cloned
        WikiSyncError: If commit fails
        ValueError: If commit message is empty
    """
    if not message or not message.strip():
        raise ValueError("Commit message cannot be empty")

    wiki_path = get_wiki_path(repo_path)

    if not is_wiki_cloned(repo_path):
        raise WikiNotClonedError("Wiki not cloned. Run 'gl-issue-sync wiki clone' first.")

    try:
        wiki_repo = Repo(wiki_path)

        # Check for changes
        if not wiki_repo.is_dirty(untracked_files=True):
            return "Nothing to commit, wiki is clean."

        # Stage all changes (new, modified, deleted)
        wiki_repo.git.add(A=True)

        # Commit
        commit = wiki_repo.index.commit(message.strip())

        # Generate summary
        stats = commit.stats.total
        files = stats.get('files', 0)
        insertions = stats.get('insertions', 0)
        deletions = stats.get('deletions', 0)
        return f"Committed: {files} file(s) changed, {insertions} insertions(+), {deletions} deletions(-)"

    except GitCommandError as e:
        raise WikiSyncError(f"Failed to commit wiki changes: {e}") from e


def get_wiki_status(repo_path: Path) -> dict:
    """Get the status of the wiki repository.

    Args:
        repo_path: Path to the main repository root

    Returns:
        Dictionary with wiki status information:
        - cloned: bool - Whether wiki is cloned
        - path: Path - Path to wiki directory
        - dirty: bool - Whether there are uncommitted changes (if cloned)
        - branch: str - Current branch name (if cloned)
        - untracked: int - Number of untracked files (if cloned)
        - modified: int - Number of modified files (if cloned)
    """
    wiki_path = get_wiki_path(repo_path)

    status = {
        "cloned": False,
        "path": wiki_path,
        "dirty": False,
        "branch": None,
        "untracked": 0,
        "modified": 0,
    }

    if not is_wiki_cloned(repo_path):
        return status

    try:
        wiki_repo = Repo(wiki_path)
        status["cloned"] = True
        status["dirty"] = wiki_repo.is_dirty(untracked_files=True)
        status["branch"] = wiki_repo.active_branch.name

        # Count untracked and modified files
        status["untracked"] = len(wiki_repo.untracked_files)
        status["modified"] = len([item.a_path for item in wiki_repo.index.diff(None)])

    except Exception:
        # If we can't get status, just return what we have
        pass

    return status
