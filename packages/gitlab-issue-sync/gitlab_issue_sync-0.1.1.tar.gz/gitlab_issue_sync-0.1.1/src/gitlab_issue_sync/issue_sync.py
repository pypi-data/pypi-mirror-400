"""Core synchronization utilities for GitLab client management.

This module provides GitLab client creation and project access utilities.
The actual sync logic lives in the storage layer (storage/base.py and storage/issue.py).
"""

import gitlab

from .config import ProjectConfig


class SyncError(Exception):
    """Raised when there's an error during synchronization."""


class AuthenticationError(Exception):
    """Raised when GitLab authentication fails."""


def get_gitlab_client(config: ProjectConfig) -> gitlab.Gitlab:
    try:
        gl = gitlab.Gitlab(config.instance_url, private_token=config.token)
        gl.auth()
        return gl
    except gitlab.exceptions.GitlabAuthenticationError as e:
        raise AuthenticationError(f"GitLab authentication failed: {e}") from e
    except Exception as e:
        # Check if error message indicates auth issues
        error_msg = str(e).lower()
        if "401" in error_msg or "unauthorized" in error_msg or "authentication" in error_msg:
            raise AuthenticationError(f"GitLab authentication failed: {e}") from e
        raise SyncError(f"Failed to connect to GitLab: {e}") from e


def get_project(gl: gitlab.Gitlab, config: ProjectConfig):
    try:
        return gl.projects.get(config.full_path)
    except Exception as e:
        raise SyncError(f"Failed to access project {config.full_path}: {e}") from e
