"""Tests for wiki module.

These tests follow the principle "Only Mock What You Don't Own":
- Uses real git repositories via fixtures for local operations
- Mocks GitPython's network operations (clone, pull, push) at the boundary
- Tests validate actual git behavior in isolated temp directories
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from git import GitCommandError, Repo

from gitlab_issue_sync.wiki import (
    WikiAlreadyExistsError,
    WikiCloneError,
    WikiNotClonedError,
    WikiSyncError,
    clone_wiki,
    commit_wiki,
    get_wiki_path,
    get_wiki_status,
    get_wiki_url,
    is_wiki_cloned,
    pull_wiki,
    push_wiki,
)


class TestGetWikiUrl:
    """Tests for wiki URL transformation.

    Tests get_wiki_url()'s responsibility:
    - Converts project URL to wiki URL by appending .wiki.git
    - Handles both SSH and HTTPS formats
    - Handles URLs with and without .git suffix
    """

    def test_ssh_url_with_git_extension(self):
        """Test SSH URL with .git extension."""
        url = "git@gitlab.com:owner/project.git"
        result = get_wiki_url(url)
        assert result == "git@gitlab.com:owner/project.wiki.git"

    def test_ssh_url_without_git_extension(self):
        """Test SSH URL without .git extension."""
        url = "git@gitlab.com:owner/project"
        result = get_wiki_url(url)
        assert result == "git@gitlab.com:owner/project.wiki.git"

    def test_https_url_with_git_extension(self):
        """Test HTTPS URL with .git extension."""
        url = "https://gitlab.com/owner/project.git"
        result = get_wiki_url(url)
        assert result == "https://gitlab.com/owner/project.wiki.git"

    def test_https_url_without_git_extension(self):
        """Test HTTPS URL without .git extension."""
        url = "https://gitlab.com/owner/project"
        result = get_wiki_url(url)
        assert result == "https://gitlab.com/owner/project.wiki.git"

    def test_self_hosted_gitlab(self):
        """Test self-hosted GitLab instance."""
        url = "git@gitlab.company.internal:team/backend.git"
        result = get_wiki_url(url)
        assert result == "git@gitlab.company.internal:team/backend.wiki.git"


class TestGetWikiPath:
    """Tests for wiki path resolution.

    Tests get_wiki_path()'s responsibility:
    - Returns the wiki/ subdirectory path
    """

    def test_returns_wiki_subdirectory(self, temp_git_repo):
        """Test that wiki path is wiki/ inside repo root."""
        path = get_wiki_path(temp_git_repo)
        assert path == temp_git_repo / "wiki"

    def test_returns_path_object(self, temp_git_repo):
        """Test that result is a Path object."""
        path = get_wiki_path(temp_git_repo)
        assert isinstance(path, Path)


class TestIsWikiCloned:
    """Tests for checking if wiki is cloned.

    Tests is_wiki_cloned()'s responsibility:
    - Returns True if wiki/ exists and is a valid git repository
    - Returns False if wiki/ doesn't exist
    - Returns False if wiki/ exists but isn't a git repository
    """

    def test_returns_false_when_wiki_not_exists(self, temp_git_repo):
        """Test returns False when wiki directory doesn't exist."""
        assert is_wiki_cloned(temp_git_repo) is False

    def test_returns_false_when_wiki_is_not_git_repo(self, temp_git_repo):
        """Test returns False when wiki exists but is not a git repo."""
        wiki_path = temp_git_repo / "wiki"
        wiki_path.mkdir()
        (wiki_path / "README.md").write_text("# Wiki")

        assert is_wiki_cloned(temp_git_repo) is False

    def test_returns_true_when_wiki_is_git_repo(self, temp_git_repo):
        """Test returns True when wiki is a valid git repository."""
        wiki_path = temp_git_repo / "wiki"
        Repo.init(wiki_path)

        assert is_wiki_cloned(temp_git_repo) is True


class TestCloneWiki:
    """Tests for cloning wiki repository.

    Tests clone_wiki()'s responsibility:
    - Clones wiki repository from derived URL
    - Creates wiki/ subdirectory
    - Raises WikiAlreadyExistsError if wiki/ exists
    - Raises WikiCloneError on clone failures
    - Uses GitPython for git operations

    Mocks Repo.clone_from() as it's a network operation.
    """

    def test_raises_error_when_wiki_already_cloned(self, temp_git_repo):
        """Test raises error when wiki is already cloned."""
        wiki_path = temp_git_repo / "wiki"
        Repo.init(wiki_path)

        with pytest.raises(WikiAlreadyExistsError, match="Wiki already cloned"):
            clone_wiki(temp_git_repo)

    def test_raises_error_when_wiki_dir_exists_but_not_repo(self, temp_git_repo):
        """Test raises error when wiki/ exists but isn't a git repo."""
        wiki_path = temp_git_repo / "wiki"
        wiki_path.mkdir()

        with pytest.raises(WikiAlreadyExistsError, match="not a valid git repository"):
            clone_wiki(temp_git_repo)

    @patch("gitlab_issue_sync.wiki.Repo.clone_from")
    def test_clones_from_correct_wiki_url(self, mock_clone_from, temp_git_repo):
        """Test that clone uses correct wiki URL derived from project URL."""
        # Setup mock to simulate successful clone
        mock_wiki_repo = MagicMock()
        mock_clone_from.return_value = mock_wiki_repo

        result = clone_wiki(temp_git_repo)

        # Verify clone was called with correct wiki URL
        expected_wiki_url = "https://gitlab.example.com/testuser/testrepo.wiki.git"
        mock_clone_from.assert_called_once_with(expected_wiki_url, temp_git_repo / "wiki")
        assert result == temp_git_repo / "wiki"

    @patch("gitlab_issue_sync.wiki.Repo.clone_from")
    def test_raises_clone_error_on_repo_not_found(self, mock_clone_from, temp_git_repo):
        """Test raises WikiCloneError when wiki repository not found."""
        mock_clone_from.side_effect = GitCommandError("clone", "Repository not found")

        with pytest.raises(WikiCloneError, match="Wiki repository not found"):
            clone_wiki(temp_git_repo)

    @patch("gitlab_issue_sync.wiki.Repo.clone_from")
    def test_raises_clone_error_on_auth_failure(self, mock_clone_from, temp_git_repo):
        """Test raises WikiCloneError on authentication failure."""
        mock_clone_from.side_effect = GitCommandError("clone", "Authentication failed")

        with pytest.raises(WikiCloneError, match="Authentication failed"):
            clone_wiki(temp_git_repo)

    @patch("gitlab_issue_sync.wiki.Repo.clone_from")
    def test_raises_clone_error_on_generic_error(self, mock_clone_from, temp_git_repo):
        """Test raises WikiCloneError on generic clone failure."""
        mock_clone_from.side_effect = GitCommandError("clone", "Some other error")

        with pytest.raises(WikiCloneError, match="Failed to clone wiki repository"):
            clone_wiki(temp_git_repo)


class TestPullWiki:
    """Tests for pulling wiki changes.

    Tests pull_wiki()'s responsibility:
    - Pulls from remote origin
    - Returns summary message
    - Raises WikiNotClonedError if wiki not cloned
    - Raises WikiSyncError on pull failures

    Uses real git repositories for local operations.
    """

    def test_raises_error_when_wiki_not_cloned(self, temp_git_repo):
        """Test raises error when wiki is not cloned."""
        with pytest.raises(WikiNotClonedError, match="Wiki not cloned"):
            pull_wiki(temp_git_repo)

    @patch("gitlab_issue_sync.wiki.Repo")
    def test_pull_with_cloned_wiki(self, mock_repo_class, temp_git_repo):
        """Test pull on a cloned wiki repository.

        Mocks Repo class since pull is a network operation.
        """
        # Setup: make wiki appear cloned by creating the directory with .git
        wiki_path = temp_git_repo / "wiki"
        wiki_path.mkdir()
        (wiki_path / ".git").mkdir()  # Fake .git directory

        # Mock the repo and remote
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_remote = MagicMock()

        # GitPython's RemoteList supports both dict-like and attribute access
        mock_remotes = MagicMock()
        mock_remotes.__contains__ = lambda self, key: key == "origin"
        mock_remotes.origin = mock_remote
        mock_repo.remotes = mock_remotes

        # Mock pull to return empty list (up to date)
        mock_remote.pull.return_value = []

        result = pull_wiki(temp_git_repo)
        assert "up to date" in result.lower()
        mock_remote.pull.assert_called_once()

    def test_raises_error_when_no_origin_remote(self, temp_git_repo):
        """Test raises error when wiki has no origin remote."""
        wiki_path = temp_git_repo / "wiki"
        wiki_repo = Repo.init(wiki_path)

        # Create initial commit but no remote
        (wiki_path / "Home.md").write_text("# Home")
        wiki_repo.index.add(["Home.md"])
        wiki_repo.index.commit("Initial commit")

        with pytest.raises(WikiSyncError, match="No 'origin' remote"):
            pull_wiki(temp_git_repo)


class TestPushWiki:
    """Tests for pushing wiki changes.

    Tests push_wiki()'s responsibility:
    - Pushes to remote origin
    - Returns summary message
    - Raises WikiNotClonedError if wiki not cloned
    - Raises WikiSyncError on push failures

    Uses real git repositories for local operations.
    """

    def test_raises_error_when_wiki_not_cloned(self, temp_git_repo):
        """Test raises error when wiki is not cloned."""
        with pytest.raises(WikiNotClonedError, match="Wiki not cloned"):
            push_wiki(temp_git_repo)

    @patch("gitlab_issue_sync.wiki.Repo")
    def test_push_with_no_changes(self, mock_repo_class, temp_git_repo):
        """Test push when there are no changes to push.

        Mocks Repo class since push is a network operation.
        """
        # Setup: make wiki appear cloned
        wiki_path = temp_git_repo / "wiki"
        wiki_path.mkdir()
        (wiki_path / ".git").mkdir()

        # Mock the repo and remote
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_remote = MagicMock()

        # GitPython's RemoteList supports both dict-like and attribute access
        mock_remotes = MagicMock()
        mock_remotes.__contains__ = lambda self, key: key == "origin"
        mock_remotes.origin = mock_remote
        mock_repo.remotes = mock_remotes

        # Mock tracking branch and no commits ahead
        mock_tracking = MagicMock()
        mock_tracking.name = "origin/main"
        mock_repo.active_branch.tracking_branch.return_value = mock_tracking
        mock_repo.iter_commits.return_value = []  # No commits ahead

        result = push_wiki(temp_git_repo)
        assert "nothing to push" in result.lower()

    @patch("gitlab_issue_sync.wiki.Repo")
    def test_push_with_new_commits(self, mock_repo_class, temp_git_repo):
        """Test push when there are new commits to push.

        Mocks Repo class since push is a network operation.
        """
        # Setup: make wiki appear cloned
        wiki_path = temp_git_repo / "wiki"
        wiki_path.mkdir()
        (wiki_path / ".git").mkdir()

        # Mock the repo and remote
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_remote = MagicMock()

        # GitPython's RemoteList supports both dict-like and attribute access
        mock_remotes = MagicMock()
        mock_remotes.__contains__ = lambda self, key: key == "origin"
        mock_remotes.origin = mock_remote
        mock_repo.remotes = mock_remotes

        # Mock tracking branch with commits ahead
        mock_tracking = MagicMock()
        mock_tracking.name = "origin/main"
        mock_repo.active_branch.tracking_branch.return_value = mock_tracking
        mock_repo.iter_commits.return_value = [MagicMock()]  # One commit ahead

        # Mock push info - use spec to get proper behavior
        mock_push_info = Mock()
        mock_push_info.flags = 0  # Success (no error flags)
        mock_push_info.ERROR = 1 << 5  # Standard git flag value
        mock_push_info.REJECTED = 1 << 6
        mock_push_info.UP_TO_DATE = 1 << 2
        mock_remote.push.return_value = [mock_push_info]

        result = push_wiki(temp_git_repo)
        assert "success" in result.lower()
        mock_remote.push.assert_called_once()


class TestCommitWiki:
    """Tests for committing wiki changes.

    Tests commit_wiki()'s responsibility:
    - Stages all changes and commits with message
    - Returns summary message
    - Raises WikiNotClonedError if wiki not cloned
    - Raises ValueError if message is empty
    - Raises WikiSyncError on commit failures
    """

    def test_raises_error_when_wiki_not_cloned(self, temp_git_repo):
        """Test raises error when wiki is not cloned."""
        with pytest.raises(WikiNotClonedError, match="Wiki not cloned"):
            commit_wiki(temp_git_repo, "Test message")

    def test_raises_error_on_empty_message(self, temp_git_repo):
        """Test raises ValueError on empty commit message."""
        wiki_path = temp_git_repo / "wiki"
        Repo.init(wiki_path)

        with pytest.raises(ValueError, match="Commit message cannot be empty"):
            commit_wiki(temp_git_repo, "")

    def test_raises_error_on_whitespace_message(self, temp_git_repo):
        """Test raises ValueError on whitespace-only commit message."""
        wiki_path = temp_git_repo / "wiki"
        Repo.init(wiki_path)

        with pytest.raises(ValueError, match="Commit message cannot be empty"):
            commit_wiki(temp_git_repo, "   ")

    def test_commit_with_no_changes(self, temp_git_repo):
        """Test commit when there are no changes."""
        wiki_path = temp_git_repo / "wiki"
        wiki_repo = Repo.init(wiki_path)

        # Create initial commit
        (wiki_path / "Home.md").write_text("# Home")
        wiki_repo.index.add(["Home.md"])
        wiki_repo.index.commit("Initial commit")

        # Try to commit without any changes
        result = commit_wiki(temp_git_repo, "No changes")
        assert "nothing to commit" in result.lower()

    def test_commit_with_new_file(self, temp_git_repo):
        """Test commit with a new file."""
        wiki_path = temp_git_repo / "wiki"
        wiki_repo = Repo.init(wiki_path)

        # Create initial commit
        (wiki_path / "Home.md").write_text("# Home")
        wiki_repo.index.add(["Home.md"])
        wiki_repo.index.commit("Initial commit")

        # Add a new file
        (wiki_path / "NewPage.md").write_text("# New Page")

        # Commit should succeed
        result = commit_wiki(temp_git_repo, "Add new page")
        assert "committed" in result.lower()

    def test_commit_with_modified_file(self, temp_git_repo):
        """Test commit with a modified file."""
        wiki_path = temp_git_repo / "wiki"
        wiki_repo = Repo.init(wiki_path)

        # Create initial commit
        (wiki_path / "Home.md").write_text("# Home")
        wiki_repo.index.add(["Home.md"])
        wiki_repo.index.commit("Initial commit")

        # Modify the file
        (wiki_path / "Home.md").write_text("# Home\n\nUpdated content")

        # Commit should succeed
        result = commit_wiki(temp_git_repo, "Update home page")
        assert "committed" in result.lower()

    def test_commit_with_deleted_file(self, temp_git_repo):
        """Test commit with a deleted file."""
        wiki_path = temp_git_repo / "wiki"
        wiki_repo = Repo.init(wiki_path)

        # Create initial commit with multiple files
        (wiki_path / "Home.md").write_text("# Home")
        (wiki_path / "ToDelete.md").write_text("# To Delete")
        wiki_repo.index.add(["Home.md", "ToDelete.md"])
        wiki_repo.index.commit("Initial commit")

        # Delete a file
        (wiki_path / "ToDelete.md").unlink()

        # Commit should succeed
        result = commit_wiki(temp_git_repo, "Remove old page")
        assert "committed" in result.lower()


class TestGetWikiStatus:
    """Tests for getting wiki status.

    Tests get_wiki_status()'s responsibility:
    - Returns status dictionary with cloned, path, dirty, branch info
    - Handles missing wiki gracefully
    """

    def test_status_when_wiki_not_cloned(self, temp_git_repo):
        """Test status when wiki is not cloned."""
        status = get_wiki_status(temp_git_repo)

        assert status["cloned"] is False
        assert status["path"] == temp_git_repo / "wiki"
        assert status["dirty"] is False
        assert status["branch"] is None

    def test_status_with_clean_wiki(self, temp_git_repo):
        """Test status when wiki is clean (no uncommitted changes)."""
        wiki_path = temp_git_repo / "wiki"
        wiki_repo = Repo.init(wiki_path)

        # Create initial commit
        (wiki_path / "Home.md").write_text("# Home")
        wiki_repo.index.add(["Home.md"])
        wiki_repo.index.commit("Initial commit")

        # Get the current branch name (could be main or master)
        branch_name = wiki_repo.active_branch.name

        status = get_wiki_status(temp_git_repo)

        assert status["cloned"] is True
        assert status["path"] == wiki_path
        assert status["dirty"] is False
        assert status["branch"] == branch_name
        assert status["untracked"] == 0
        assert status["modified"] == 0

    def test_status_with_dirty_wiki(self, temp_git_repo):
        """Test status when wiki has uncommitted changes."""
        wiki_path = temp_git_repo / "wiki"
        wiki_repo = Repo.init(wiki_path)

        # Create initial commit
        (wiki_path / "Home.md").write_text("# Home")
        wiki_repo.index.add(["Home.md"])
        wiki_repo.index.commit("Initial commit")

        # Add untracked file and modify existing
        (wiki_path / "Home.md").write_text("# Home\n\nUpdated")
        (wiki_path / "NewPage.md").write_text("# New Page")

        status = get_wiki_status(temp_git_repo)

        assert status["cloned"] is True
        assert status["dirty"] is True
        assert status["untracked"] == 1
        assert status["modified"] == 1
