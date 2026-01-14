"""Git repository utilities for detecting and parsing GitLab remote information."""

import re
from dataclasses import dataclass
from pathlib import Path

from git import Repo
from git.exc import InvalidGitRepositoryError


@dataclass
class GitLabRemoteInfo:
    """Information extracted from a GitLab remote URL."""

    instance_url: str
    namespace: str
    project: str

    @property
    def full_path(self) -> str:
        """Return the full project path (namespace/project)."""
        return f"{self.namespace}/{self.project}"


class GitRepositoryNotFoundError(Exception):
    """Raised when a git repository cannot be found."""


class GitLabRemoteNotFoundError(Exception):
    """Raised when a GitLab remote cannot be found or parsed."""


def find_repository_root(start_path: Path | None = None) -> Path:
    """
    Find the git repository root by walking up from the start path.

    Args:
        start_path: Directory to start searching from (defaults to current directory)

    Returns:
        Path to the git repository root

    Raises:
        GitRepositoryNotFoundError: If no git repository is found
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # Walk up the directory tree
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    # Check root directory
    if (current / ".git").exists():
        return current

    raise GitRepositoryNotFoundError(f"No git repository found starting from {start_path}")


def find_project_root(start_path: Path | None = None) -> Path:
    """
    Find the gl-issue-sync project root, handling wiki subdirectory case.

    This is similar to find_repository_root() but specifically looks for a
    gl-issue-sync managed project (has .issues/ or .glissuesync/ directories).
    If we're in the wiki/ subdirectory, it will find the parent project.

    Args:
        start_path: Directory to start searching from (defaults to current directory)

    Returns:
        Path to the gl-issue-sync project root

    Raises:
        GitRepositoryNotFoundError: If no gl-issue-sync project is found
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # Walk up the directory tree looking for a gl-issue-sync project
    while current != current.parent:
        if (current / ".git").exists():
            # Check if this is a gl-issue-sync managed project
            if (current / ".issues").exists() or (current / ".glissuesync").exists():
                return current

            # Check if we're in a wiki/ subdirectory of a gl-issue-sync project
            # The parent might be the actual project root
            parent = current.parent
            if (parent / ".git").exists() and current.name == "wiki":
                if (parent / ".issues").exists() or (parent / ".glissuesync").exists():
                    return parent

        current = current.parent

    # Check root directory
    if (current / ".git").exists():
        if (current / ".issues").exists() or (current / ".glissuesync").exists():
            return current

    raise GitRepositoryNotFoundError(
        f"No gl-issue-sync project found starting from {start_path}. "
        "Make sure you're in a directory with .issues/ or .glissuesync/ folders, "
        "or run 'gl-issue-sync init' to set up the project."
    )


def parse_gitlab_remote_url(url: str) -> GitLabRemoteInfo:
    """
    Parse a GitLab remote URL to extract instance, namespace, and project.

    Supports both SSH and HTTPS URLs:
    - SSH: git@gitlab.example.com:namespace/project.git
    - HTTPS: https://gitlab.example.com/namespace/project.git

    Args:
        url: The git remote URL

    Returns:
        GitLabRemoteInfo with extracted information

    Raises:
        GitLabRemoteNotFoundError: If URL cannot be parsed
    """
    # SSH format: git@gitlab.example.com:namespace/project.git
    ssh_pattern = r"git@([^:]+):([^/]+)/(.+?)(?:\.git)?$"
    ssh_match = re.match(ssh_pattern, url)

    if ssh_match:
        host = ssh_match.group(1)
        namespace = ssh_match.group(2)
        project = ssh_match.group(3).removesuffix(".git")
        return GitLabRemoteInfo(
            instance_url=f"https://{host}",
            namespace=namespace,
            project=project,
        )

    # HTTPS format: https://gitlab.example.com/namespace/project.git
    https_pattern = r"https?://([^/]+)/([^/]+)/(.+?)(?:\.git)?$"
    https_match = re.match(https_pattern, url)

    if https_match:
        host = https_match.group(1)
        namespace = https_match.group(2)
        project = https_match.group(3).removesuffix(".git")
        return GitLabRemoteInfo(
            instance_url=f"https://{host}",
            namespace=namespace,
            project=project,
        )

    raise GitLabRemoteNotFoundError(f"Could not parse GitLab URL: {url}")


def get_gitlab_remote_info(repo_path: Path | None = None, remote_name: str = "origin") -> GitLabRemoteInfo:
    """
    Get GitLab remote information for a repository.

    Args:
        repo_path: Path to the git repository (defaults to finding from current directory)
        remote_name: Name of the remote to use (defaults to 'origin')

    Returns:
        GitLabRemoteInfo with instance URL, namespace, and project

    Raises:
        GitRepositoryNotFoundError: If no git repository is found
        GitLabRemoteNotFoundError: If remote doesn't exist or URL cannot be parsed
    """
    if repo_path is None:
        repo_path = find_repository_root()

    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError as e:
        raise GitRepositoryNotFoundError(f"Not a valid git repository: {repo_path}") from e

    # Get the remote
    if remote_name not in repo.remotes:
        available_remotes = [r.name for r in repo.remotes]
        raise GitLabRemoteNotFoundError(
            f"Remote '{remote_name}' not found. Available remotes: {', '.join(available_remotes)}"
        )

    remote = repo.remotes[remote_name]
    url = remote.url

    return parse_gitlab_remote_url(url)
