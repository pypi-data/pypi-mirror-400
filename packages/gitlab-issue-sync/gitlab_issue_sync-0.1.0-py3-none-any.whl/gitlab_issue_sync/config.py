"""Configuration management for GitLab issue sync."""

import os
import tomllib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class BoardConfig:
    """Configuration for Kanban board columns."""

    columns: list[str] = field(default_factory=list)
    last_sync: datetime | None = None


@dataclass
class ProjectConfig:
    """Configuration for a GitLab project."""

    token: str
    instance_url: str
    namespace: str
    project: str
    board: BoardConfig = field(default_factory=BoardConfig)
    username: str | None = None  # Cached username from GitLab

    @property
    def full_path(self) -> str:
        """Return the full project path (namespace/project)."""
        return f"{self.namespace}/{self.project}"

    @property
    def project_key(self) -> str:
        """Return the project key used in config file (instance/namespace/project)."""
        # Remove https:// prefix from instance URL for the key
        instance_part = self.instance_url.replace("https://", "").replace("http://", "")
        return f"{instance_part}/{self.namespace}/{self.project}"


class ConfigurationError(Exception):
    """Raised when there's an error with configuration."""


def get_config_dir() -> Path:
    """Returns ~/.config/gitlab-issue-sync/, creating it if needed."""
    config_dir = Path.home() / ".config" / "gitlab-issue-sync"
    config_dir.mkdir(parents=True, exist_ok=True)

    # Ensure the directory has appropriate permissions (0700)
    config_dir.chmod(0o700)

    return config_dir


def get_config_file_path() -> Path:
    return get_config_dir() / "config.toml"


def load_config() -> dict[str, ProjectConfig]:
    """
    Load configuration from disk.

    Returns:
        Dictionary mapping project keys to ProjectConfig objects

    Raises:
        ConfigurationError: If config file cannot be read or parsed
    """
    config_path = get_config_file_path()

    if not config_path.exists():
        return {}

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        raise ConfigurationError(f"Failed to read config file: {e}") from e

    projects = {}

    for project_key, project_data in data.get("project", {}).items():
        board_data = project_data.get("board", {})
        board = BoardConfig(
            columns=board_data.get("columns", []),
            last_sync=datetime.fromisoformat(board_data["last_sync"]) if "last_sync" in board_data else None,
        )

        projects[project_key] = ProjectConfig(
            token=project_data["token"],
            instance_url=project_data["instance_url"],
            namespace=project_data["namespace"],
            project=project_data["project"],
            board=board,
            username=project_data.get("username"),  # Load cached username
        )

    return projects


def save_config(projects: dict[str, ProjectConfig]) -> None:
    """
    Save configuration to disk.

    Args:
        projects: Dictionary mapping project keys to ProjectConfig objects

    Raises:
        ConfigurationError: If config file cannot be written
    """
    config_path = get_config_file_path()
    lines = []

    for project_key, project_config in projects.items():
        lines.append(f'[project."{project_key}"]')
        lines.append(f'token = "{project_config.token}"')
        lines.append(f'instance_url = "{project_config.instance_url}"')
        lines.append(f'namespace = "{project_config.namespace}"')
        lines.append(f'project = "{project_config.project}"')

        if project_config.username:
            lines.append(f'username = "{project_config.username}"')

        lines.append("")

        if project_config.board.columns:
            lines.append(f'[project."{project_key}".board]')
            columns_str = ", ".join(f'"{col}"' for col in project_config.board.columns)
            lines.append(f"columns = [{columns_str}]")

            if project_config.board.last_sync:
                lines.append(f'last_sync = "{project_config.board.last_sync.isoformat()}"')

            lines.append("")

    try:
        with open(config_path, "w") as f:
            f.write("\n".join(lines))

        # Set file permissions to 0600 (owner read/write only)
        config_path.chmod(0o600)
    except Exception as e:
        raise ConfigurationError(f"Failed to write config file: {e}") from e


def get_project_config_for_repo(repo_path: Path) -> ProjectConfig | None:
    """
    Get configuration for the GitLab project at the given repository path.

    Args:
        repo_path: Path to repository (will find root automatically)

    Returns:
        ProjectConfig if found, None otherwise
    """
    from .git_utils import get_gitlab_remote_info

    remote_info = get_gitlab_remote_info(repo_path)
    return get_project_config(remote_info.instance_url, remote_info.namespace, remote_info.project)


def get_project_config(instance_url: str, namespace: str, project: str) -> ProjectConfig | None:
    """
    Get configuration for a specific project.

    Args:
        instance_url: GitLab instance URL
        namespace: Project namespace
        project: Project name

    Returns:
        ProjectConfig if found, None otherwise
    """
    configs = load_config()
    instance_part = instance_url.replace("https://", "").replace("http://", "")
    project_key = f"{instance_part}/{namespace}/{project}"

    return configs.get(project_key)


def save_project_config(project_config: ProjectConfig) -> None:
    """
    Save or update configuration for a specific project.

    Args:
        project_config: The project configuration to save
    """
    configs = load_config()
    configs[project_config.project_key] = project_config
    save_config(configs)


def get_token(instance_url: str, namespace: str, project: str) -> str:
    """
    Get the GitLab access token for a project.

    Checks in order:
    1. GITLAB_TOKEN environment variable
    2. Stored configuration

    Args:
        instance_url: GitLab instance URL
        namespace: Project namespace
        project: Project name

    Returns:
        The access token

    Raises:
        ConfigurationError: If no token is found
    """
    env_token = os.environ.get("GITLAB_TOKEN")
    if env_token:
        return env_token

    config = get_project_config(instance_url, namespace, project)
    if config and config.token:
        return config.token

    raise ConfigurationError(
        f"No token found for {namespace}/{project}. "
        "Set GITLAB_TOKEN environment variable or run 'gl-issue-sync init'"
    )
