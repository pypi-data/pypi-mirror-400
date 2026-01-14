"""Test helpers for network isolation and offline testing."""

import os
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from unittest.mock import patch


class NetworkAccessError(Exception):
    """Raised when test attempts network access in offline mode."""

    pass


def block_network(*args, **kwargs):
    """Raise error when network access attempted."""
    raise NetworkAccessError("Network access attempted in offline test. Use @no_network decorator or mock the network call.")


@contextmanager
def offline_mode():
    """Context manager to block all network access."""
    with (
        patch("socket.socket", side_effect=block_network),
        patch("urllib3.PoolManager", side_effect=block_network),
        patch("requests.Session.request", side_effect=block_network),
        patch("gitlab.Gitlab", side_effect=block_network),
    ):
        yield


def no_network(func):
    """
    Decorator to ensure test runs without network access.

    Usage:
        @no_network
        def test_label_create_offline():
            # Cannot make network calls
            label = Label(name="Bug", color="#FF0000")
            label.status = "pending"
            Label.backend.save(label, repo_path)
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        with offline_mode():
            return func(*args, **kwargs)

    return wrapper


@contextmanager
def in_directory(path: str | Path):
    """Context manager that temporarily changes to a directory and restores on exit.

    Usage:
        with in_directory(temp_git_repo):
            # Code runs with temp_git_repo as cwd
            result = cli_runner.invoke(main, ["status"])
        # Original directory is restored here

    Args:
        path: The directory to change to (str or Path)

    Yields:
        None - the context manager just manages the directory change
    """
    original_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_cwd)
