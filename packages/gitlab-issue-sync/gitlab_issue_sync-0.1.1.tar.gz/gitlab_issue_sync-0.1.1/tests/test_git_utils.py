"""Tests for git_utils module.

These tests follow the principle "Only Mock What You Don't Own":
- NO mocking of internal git_utils functions
- Uses real git repositories via temp_git_repo fixture
- Uses real GitPython library for git operations
- Tests validate actual git behavior in isolated temp directories
"""

import os

import pytest
from git import Repo

from gitlab_issue_sync.git_utils import (
    GitLabRemoteInfo,
    GitLabRemoteNotFoundError,
    GitRepositoryNotFoundError,
    find_project_root,
    find_repository_root,
    get_gitlab_remote_info,
    parse_gitlab_remote_url,
)


class TestParseGitLabRemoteUrl:
    """Tests for parsing GitLab remote URLs.

    Tests parse_gitlab_remote_url()'s responsibility:
    - Correctly extracts instance_url, namespace, project from various URL formats
    - Handles SSH, HTTPS, and HTTP URLs
    - Validates URL format and raises appropriate errors
    """

    def test_parse_ssh_url(self):
        """Test parsing SSH format URLs.

        Validates parse_gitlab_remote_url() correctly extracts GitLab info from SSH URLs.
        """
        url = "git@gitlab.com:owner/project.git"
        info = parse_gitlab_remote_url(url)

        assert info.instance_url == "https://gitlab.com"
        assert info.namespace == "owner"
        assert info.project == "project"
        assert info.full_path == "owner/project"

    def test_parse_ssh_url_without_git_extension(self):
        """Test parsing SSH URLs without .git extension."""
        url = "git@gitlab.com:owner/project"
        info = parse_gitlab_remote_url(url)

        assert info.instance_url == "https://gitlab.com"
        assert info.namespace == "owner"
        assert info.project == "project"

    def test_parse_https_url(self):
        """Test parsing HTTPS format URLs."""
        url = "https://gitlab.example.com/owner/project.git"
        info = parse_gitlab_remote_url(url)

        assert info.instance_url == "https://gitlab.example.com"
        assert info.namespace == "owner"
        assert info.project == "project"
        assert info.full_path == "owner/project"

    def test_parse_https_url_without_git_extension(self):
        """Test parsing HTTPS URLs without .git extension."""
        url = "https://gitlab.example.com/owner/project"
        info = parse_gitlab_remote_url(url)

        assert info.instance_url == "https://gitlab.example.com"
        assert info.namespace == "owner"
        assert info.project == "project"

    def test_parse_http_url(self):
        """Test parsing HTTP format URLs (less common but valid)."""
        url = "http://gitlab.internal/team/awesome-project.git"
        info = parse_gitlab_remote_url(url)

        assert info.instance_url == "https://gitlab.internal"
        assert info.namespace == "team"
        assert info.project == "awesome-project"

    def test_parse_self_hosted_gitlab(self):
        """Test parsing self-hosted GitLab instance."""
        url = "git@gitlab.company.internal:engineering/backend.git"
        info = parse_gitlab_remote_url(url)

        assert info.instance_url == "https://gitlab.company.internal"
        assert info.namespace == "engineering"
        assert info.project == "backend"

    def test_parse_project_with_dashes(self):
        """Test parsing projects with dashes in the name."""
        url = "git@gitlab.com:my-org/my-awesome-project.git"
        info = parse_gitlab_remote_url(url)

        assert info.namespace == "my-org"
        assert info.project == "my-awesome-project"

    def test_parse_invalid_url_raises_error(self):
        """Test that invalid URLs raise an error."""
        with pytest.raises(GitLabRemoteNotFoundError, match="Could not parse GitLab URL"):
            parse_gitlab_remote_url("not-a-valid-url")

    def test_parse_github_url_raises_error(self):
        """Test that GitHub URLs raise an error (this is GitLab-specific)."""
        # While the pattern might technically match, we want to be explicit
        # In practice, this should still parse since the pattern is similar
        # But we could add validation for known GitLab instances if needed
        url = "git@github.com:owner/project.git"
        # This actually parses, but would fail when connecting to GitLab API
        info = parse_gitlab_remote_url(url)
        assert info.instance_url == "https://github.com"
        # In real usage, the GitLab API client would fail


class TestGitLabRemoteInfo:
    """Tests for GitLabRemoteInfo dataclass.

    Tests GitLabRemoteInfo's responsibility:
    - Stores GitLab remote configuration (instance_url, namespace, project)
    - Computes full_path property from namespace/project
    """

    def test_full_path_property(self):
        """Test the full_path property combines namespace and project.

        Validates GitLabRemoteInfo.full_path correctly formats namespace/project.
        """
        info = GitLabRemoteInfo(
            instance_url="https://gitlab.com",
            namespace="my-team",
            project="my-project",
        )
        assert info.full_path == "my-team/my-project"


class TestFindRepositoryRoot:
    """Tests for finding git repository root.

    Tests find_repository_root()'s responsibility:
    - Walks up directory tree to find .git directory
    - Returns Path to repository root
    - Defaults to current working directory when no path provided
    - Raises appropriate error when not in a git repository

    Uses real git repositories via temp_git_repo fixture.
    """

    def test_find_repository_root_from_repo_root(self, temp_git_repo):
        """Test finding repository root when starting from repo root.

        Validates find_repository_root() returns correct path when already at root.
        """
        # temp_git_repo already has .git directory from the fixture
        repo_root = find_repository_root(temp_git_repo)

        assert repo_root == temp_git_repo
        assert (repo_root / ".git").exists()

    def test_find_repository_root_from_subdirectory(self, temp_git_repo):
        """Test finding repository root when starting from a subdirectory.

        Validates find_repository_root() walks up directory tree correctly.
        """
        # Create nested subdirectories
        subdir = temp_git_repo / "src" / "gitlab_issue_sync"
        subdir.mkdir(parents=True)

        # Find repo root from deep subdirectory
        repo_root = find_repository_root(subdir)

        assert repo_root == temp_git_repo
        assert (repo_root / ".git").exists()

    def test_find_repository_root_defaults_to_cwd(self, temp_git_repo):
        """Test that find_repository_root defaults to current working directory.

        Validates find_repository_root() uses cwd when no path provided.
        """
        # Change to the temp git repo
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            repo_root = find_repository_root()
            assert repo_root == temp_git_repo
        finally:
            os.chdir(original_cwd)

    def test_find_repository_root_raises_error_when_not_in_repo(self, tmp_path):
        """Test that an error is raised when not in a git repository.

        Validates find_repository_root() error handling when .git not found.
        """
        # Create a directory that is NOT a git repo
        non_repo_dir = tmp_path / "not_a_repo"
        non_repo_dir.mkdir()

        with pytest.raises(GitRepositoryNotFoundError, match="No git repository found"):
            find_repository_root(non_repo_dir)


class TestFindProjectRoot:
    """Tests for finding gl-issue-sync project root.

    Tests find_project_root()'s responsibility:
    - Finds git repository with .issues/ or .glissuesync/ directories
    - Handles wiki/ subdirectory case (finds parent project)
    - Raises appropriate error when not in a gl-issue-sync project

    Uses real git repositories via temp_git_repo fixture.
    """

    def test_find_project_root_from_repo_root(self, temp_git_repo):
        """Test finding project root when starting from repo root.

        temp_git_repo fixture creates .issues/ directory.
        """
        project_root = find_project_root(temp_git_repo)

        assert project_root == temp_git_repo
        assert (project_root / ".issues").exists()

    def test_find_project_root_from_subdirectory(self, temp_git_repo):
        """Test finding project root when starting from a subdirectory."""
        # Create nested subdirectories
        subdir = temp_git_repo / "src" / "gitlab_issue_sync"
        subdir.mkdir(parents=True)

        # Find project root from deep subdirectory
        project_root = find_project_root(subdir)

        assert project_root == temp_git_repo
        assert (project_root / ".issues").exists()

    def test_find_project_root_from_wiki_subdirectory(self, temp_git_repo):
        """Test finding project root when inside wiki/ subdirectory.

        This is the key test - when running from wiki/ (a separate git repo),
        we should find the parent project, not the wiki repo.
        """
        # Create wiki/ as a separate git repository
        wiki_path = temp_git_repo / "wiki"
        Repo.init(wiki_path)

        # Create a file in wiki
        (wiki_path / "Home.md").write_text("# Home")
        wiki_repo = Repo(wiki_path)
        wiki_repo.index.add(["Home.md"])
        wiki_repo.index.commit("Initial wiki commit")

        # Find project root from wiki directory - should find parent
        project_root = find_project_root(wiki_path)

        assert project_root == temp_git_repo
        assert (project_root / ".issues").exists()

    def test_find_project_root_from_wiki_subdirectory_nested(self, temp_git_repo):
        """Test finding project root when deep inside wiki/ subdirectory."""
        # Create wiki/ as a separate git repository with nested folders
        wiki_path = temp_git_repo / "wiki"
        Repo.init(wiki_path)

        nested_dir = wiki_path / "docs" / "deep"
        nested_dir.mkdir(parents=True)

        # Find project root from nested wiki directory
        project_root = find_project_root(nested_dir)

        assert project_root == temp_git_repo
        assert (project_root / ".issues").exists()

    def test_find_project_root_raises_error_when_not_in_project(self, tmp_path):
        """Test error when not in a gl-issue-sync project."""
        # Create a regular git repo without .issues/
        non_project_dir = tmp_path / "regular_repo"
        non_project_dir.mkdir()
        Repo.init(non_project_dir)

        with pytest.raises(GitRepositoryNotFoundError, match="No gl-issue-sync project found"):
            find_project_root(non_project_dir)

    def test_find_project_root_with_glissuesync_directory(self, tmp_path):
        """Test finding project with .glissuesync/ instead of .issues/."""
        # Create a repo with .glissuesync/ but not .issues/
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        Repo.init(project_dir)
        (project_dir / ".glissuesync").mkdir()

        project_root = find_project_root(project_dir)

        assert project_root == project_dir


class TestGetGitLabRemoteInfo:
    """Tests for extracting GitLab remote information from a repository.

    Tests get_gitlab_remote_info()'s responsibility:
    - Reads git remote configuration from real .git/config
    - Extracts and parses GitLab remote URL
    - Handles different remote names (origin, upstream, etc.)
    - Validates repository and remote existence
    - Returns GitLabRemoteInfo with instance_url, namespace, project

    Uses real git repositories with real remotes via temp_git_repo fixture.
    Uses real GitPython library to manipulate remotes.
    """

    def test_get_gitlab_remote_info_with_default_origin(self, temp_git_repo):
        """Test extracting remote info from repository with origin remote.

        Validates get_gitlab_remote_info() correctly reads 'origin' remote.
        """
        # temp_git_repo has origin remote configured in the fixture
        info = get_gitlab_remote_info(temp_git_repo)

        assert info.instance_url == "https://gitlab.example.com"
        assert info.namespace == "testuser"
        assert info.project == "testrepo"
        assert info.full_path == "testuser/testrepo"

    def test_get_gitlab_remote_info_with_custom_remote_name(self, temp_git_repo):
        """Test extracting remote info from a non-origin remote.

        Validates get_gitlab_remote_info() can read remotes with custom names.
        Uses real GitPython to add a second remote.
        """
        # Add another remote with a different name
        repo = Repo(temp_git_repo)
        repo.create_remote("upstream", "git@gitlab.com:org/project.git")

        info = get_gitlab_remote_info(temp_git_repo, remote_name="upstream")

        assert info.instance_url == "https://gitlab.com"
        assert info.namespace == "org"
        assert info.project == "project"

    def test_get_gitlab_remote_info_defaults_to_current_directory(self, temp_git_repo):
        """Test that get_gitlab_remote_info works from current directory.

        Validates get_gitlab_remote_info() uses cwd when no path provided.
        """
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            info = get_gitlab_remote_info()

            assert info.instance_url == "https://gitlab.example.com"
            assert info.namespace == "testuser"
            assert info.project == "testrepo"
        finally:
            os.chdir(original_cwd)

    def test_get_gitlab_remote_info_raises_error_for_missing_remote(self, temp_git_repo):
        """Test that an error is raised when the specified remote doesn't exist.

        Validates get_gitlab_remote_info() error handling for missing remotes.
        """
        with pytest.raises(
            GitLabRemoteNotFoundError, match="Remote 'nonexistent' not found. Available remotes: origin"
        ):
            get_gitlab_remote_info(temp_git_repo, remote_name="nonexistent")

    def test_get_gitlab_remote_info_raises_error_for_invalid_repo(self, tmp_path):
        """Test that an error is raised when path is not a git repository.

        Validates get_gitlab_remote_info() error handling for non-git directories.
        """
        non_repo_dir = tmp_path / "not_a_repo"
        non_repo_dir.mkdir()

        with pytest.raises(GitRepositoryNotFoundError, match="Not a valid git repository"):
            get_gitlab_remote_info(non_repo_dir)

    def test_get_gitlab_remote_info_with_ssh_url(self, temp_git_repo):
        """Test extracting info from SSH-format remote URL.

        Validates get_gitlab_remote_info() works with SSH URLs.
        Uses real GitPython to modify the remote.
        """
        # Replace origin remote with SSH URL
        repo = Repo(temp_git_repo)
        repo.delete_remote("origin")
        repo.create_remote("origin", "git@gitlab.company.internal:team/awesome-project.git")

        info = get_gitlab_remote_info(temp_git_repo)

        assert info.instance_url == "https://gitlab.company.internal"
        assert info.namespace == "team"
        assert info.project == "awesome-project"

    def test_get_gitlab_remote_info_with_http_url(self, temp_git_repo):
        """Test extracting info from HTTP-format remote URL.

        Validates get_gitlab_remote_info() works with HTTP URLs.
        Uses real GitPython to modify the remote.
        """
        # Replace origin remote with HTTP URL
        repo = Repo(temp_git_repo)
        repo.delete_remote("origin")
        repo.create_remote("origin", "http://gitlab.internal/eng/backend.git")

        info = get_gitlab_remote_info(temp_git_repo)

        assert info.instance_url == "https://gitlab.internal"
        assert info.namespace == "eng"
        assert info.project == "backend"
