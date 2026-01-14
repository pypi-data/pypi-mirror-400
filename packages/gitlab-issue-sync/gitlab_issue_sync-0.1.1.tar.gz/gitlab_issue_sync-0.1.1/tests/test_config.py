"""Tests for config module.

Following the "only mock what you don't own" principle:
- We DON'T mock internal config functions (save_config, load_config, etc.)
- We use real file I/O in temp directories
- We only redirect the config directory location for test isolation
"""

from datetime import datetime

import pytest

from gitlab_issue_sync.config import (
    BoardConfig,
    ConfigurationError,
    ProjectConfig,
    get_project_config,
    get_token,
    load_config,
    save_config,
    save_project_config,
)


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    """Create a temporary config directory for test isolation.

    Uses monkeypatch to redirect config directory to temp location.
    This is acceptable because:
    - We're not mocking business logic
    - We're just redirecting file storage location for isolation
    - Real config functions still run with real file I/O
    """
    config_dir = tmp_path / ".config" / "gitlab-issue-sync"
    config_dir.mkdir(parents=True)

    # Redirect config directory to temp location for test isolation
    monkeypatch.setattr("gitlab_issue_sync.config.get_config_dir", lambda: config_dir)

    return config_dir


class TestProjectConfig:
    """Tests for ProjectConfig dataclass properties.

    These are unit tests for dataclass computed properties.
    No external dependencies or mocking needed.
    """

    def test_full_path(self):
        """Test full_path property constructs namespace/project correctly."""
        config = ProjectConfig(
            token="test-token",
            instance_url="https://gitlab.com",
            namespace="my-team",
            project="my-project",
        )

        # Test ProjectConfig's responsibility: correct path construction
        assert config.full_path == "my-team/my-project"

    def test_project_key(self):
        """Test project_key property constructs instance/namespace/project correctly."""
        config = ProjectConfig(
            token="test-token",
            instance_url="https://gitlab.com",
            namespace="my-team",
            project="my-project",
        )

        # Test ProjectConfig's responsibility: correct key construction
        assert config.project_key == "gitlab.com/my-team/my-project"

    def test_project_key_with_self_hosted(self):
        """Test project_key handles self-hosted GitLab instances correctly."""
        config = ProjectConfig(
            token="test-token",
            instance_url="https://gitlab.company.internal",
            namespace="engineering",
            project="backend",
        )

        # Test ProjectConfig's responsibility: works with any GitLab instance
        assert config.project_key == "gitlab.company.internal/engineering/backend"


class TestSaveAndLoadConfig:
    """Tests for config file serialization and persistence.

    These tests validate:
    - TOML serialization/deserialization (save_config/load_config's responsibility)
    - File permissions (save_config's responsibility)
    - Handling missing files (load_config's responsibility)

    All tests use real file I/O in temp directories - NO MOCKING.
    """

    def test_save_and_load_single_project(self, temp_config_dir):
        """Test round-trip serialization of a single project configuration."""
        project_config = ProjectConfig(
            token="glpat-test123",
            instance_url="https://gitlab.com",
            namespace="owner",
            project="repo",
        )

        projects = {"gitlab.com/owner/repo": project_config}

        # Test save_config's responsibility: correct file creation
        save_config(projects)

        # Assert on save_config's behavior: file exists with secure permissions
        config_file = temp_config_dir / "config.toml"
        assert config_file.exists()
        assert oct(config_file.stat().st_mode)[-3:] == "600"

        # Test load_config's responsibility: correct deserialization
        loaded = load_config()

        # Assert on load_config's behavior: correct data restored
        assert len(loaded) == 1
        assert "gitlab.com/owner/repo" in loaded

        loaded_project = loaded["gitlab.com/owner/repo"]
        assert loaded_project.token == "glpat-test123"
        assert loaded_project.instance_url == "https://gitlab.com"
        assert loaded_project.namespace == "owner"
        assert loaded_project.project == "repo"

    def test_save_and_load_with_board_config(self, temp_config_dir):
        """Test serialization of nested BoardConfig structure."""
        board = BoardConfig(
            columns=["backlog", "todo", "in-progress", "done"],
            last_sync=datetime(2025, 1, 2, 12, 0, 0),
        )

        project_config = ProjectConfig(
            token="glpat-test123",
            instance_url="https://gitlab.com",
            namespace="owner",
            project="repo",
            board=board,
        )

        projects = {"gitlab.com/owner/repo": project_config}

        # Test save_config with nested structures
        save_config(projects)

        # Test load_config restores nested structures correctly
        loaded = load_config()
        loaded_project = loaded["gitlab.com/owner/repo"]

        # Assert on correct BoardConfig deserialization
        assert loaded_project.board.columns == ["backlog", "todo", "in-progress", "done"]
        assert loaded_project.board.last_sync == datetime(2025, 1, 2, 12, 0, 0)

    def test_save_and_load_multiple_projects(self, temp_config_dir):
        """Test serialization of multiple projects in one config file."""
        project1 = ProjectConfig(
            token="token1",
            instance_url="https://gitlab.com",
            namespace="org1",
            project="project1",
        )

        project2 = ProjectConfig(
            token="token2",
            instance_url="https://gitlab.internal",
            namespace="org2",
            project="project2",
        )

        projects = {
            "gitlab.com/org1/project1": project1,
            "gitlab.internal/org2/project2": project2,
        }

        # Test save_config with multiple projects
        save_config(projects)

        # Test load_config restores all projects
        loaded = load_config()

        # Assert on correct multi-project handling
        assert len(loaded) == 2
        assert "gitlab.com/org1/project1" in loaded
        assert "gitlab.internal/org2/project2" in loaded

    def test_load_empty_config(self, temp_config_dir):
        """Test load_config handles missing config file gracefully."""
        # Test load_config's responsibility: graceful handling of missing file
        loaded = load_config()

        # Assert on load_config's behavior: returns empty dict, not error
        assert loaded == {}


class TestGetProjectConfig:
    """Tests for retrieving project-specific configuration.

    Tests get_project_config's responsibility:
    - Finding the right project in the config
    - Returning None for missing projects

    Uses real save/load functions - NO MOCKING.
    """

    def test_get_existing_project(self, temp_config_dir):
        """Test get_project_config retrieves saved project correctly."""
        project_config = ProjectConfig(
            token="test-token",
            instance_url="https://gitlab.com",
            namespace="owner",
            project="repo",
        )

        # Setup: Save a project (let real function run)
        save_project_config(project_config)

        # Test get_project_config's responsibility: finding the project
        retrieved = get_project_config("https://gitlab.com", "owner", "repo")

        # Assert on get_project_config's behavior: correct retrieval
        assert retrieved is not None
        assert retrieved.token == "test-token"
        assert retrieved.namespace == "owner"

    def test_get_nonexistent_project(self, temp_config_dir):
        """Test get_project_config handles missing project gracefully."""
        # Test get_project_config's responsibility: handling missing projects
        retrieved = get_project_config("https://gitlab.com", "owner", "nonexistent")

        # Assert on get_project_config's behavior: returns None, not error
        assert retrieved is None


class TestSaveProjectConfig:
    """Tests for saving project-specific configuration.

    Tests save_project_config's responsibility:
    - Adding new projects to config
    - Updating existing projects in config
    - Preserving other projects when saving

    Uses real save/load functions - NO MOCKING.
    """

    def test_save_new_project(self, temp_config_dir):
        """Test save_project_config adds new project to config."""
        project_config = ProjectConfig(
            token="new-token",
            instance_url="https://gitlab.com",
            namespace="new-owner",
            project="new-repo",
        )

        # Test save_project_config's responsibility: adding new project
        save_project_config(project_config)

        # Assert on save_project_config's behavior: project added to config
        loaded = load_config()
        assert "gitlab.com/new-owner/new-repo" in loaded

    def test_update_existing_project(self, temp_config_dir):
        """Test save_project_config updates existing project in config."""
        # Setup: Save initial config
        project_config = ProjectConfig(
            token="old-token",
            instance_url="https://gitlab.com",
            namespace="owner",
            project="repo",
        )
        save_project_config(project_config)

        # Test save_project_config's responsibility: updating existing project
        project_config.token = "new-token"
        project_config.board = BoardConfig(columns=["todo", "done"])
        save_project_config(project_config)

        # Assert on save_project_config's behavior: project updated in config
        loaded = get_project_config("https://gitlab.com", "owner", "repo")
        assert loaded.token == "new-token"
        assert loaded.board.columns == ["todo", "done"]


class TestGetToken:
    """Tests for token retrieval logic.

    Tests get_token's responsibility:
    - Environment variable takes precedence over config
    - Falls back to config when no environment variable
    - Raises error when token not found anywhere

    Uses real get_token/save_project_config functions - NO MOCKING.
    Only uses monkeypatch to control environment (acceptable for test isolation).
    """

    def test_get_token_from_environment(self, temp_config_dir, monkeypatch):
        """Test get_token prefers environment variable over config."""
        # Setup: Set environment variable
        monkeypatch.setenv("GITLAB_TOKEN", "env-token")

        # Setup: Save config with different token
        project_config = ProjectConfig(
            token="config-token",
            instance_url="https://gitlab.com",
            namespace="owner",
            project="repo",
        )
        save_project_config(project_config)

        # Test get_token's responsibility: environment takes precedence
        token = get_token("https://gitlab.com", "owner", "repo")

        # Assert on get_token's behavior: environment variable wins
        assert token == "env-token"

    def test_get_token_from_config(self, temp_config_dir, monkeypatch):
        """Test get_token falls back to config when no environment variable."""
        # Setup: Ensure no environment variable
        monkeypatch.delenv("GITLAB_TOKEN", raising=False)

        # Setup: Save config with token
        project_config = ProjectConfig(
            token="config-token",
            instance_url="https://gitlab.com",
            namespace="owner",
            project="repo",
        )
        save_project_config(project_config)

        # Test get_token's responsibility: config fallback
        token = get_token("https://gitlab.com", "owner", "repo")

        # Assert on get_token's behavior: reads from config
        assert token == "config-token"

    def test_get_token_not_found(self, temp_config_dir, monkeypatch):
        """Test get_token raises error when token not found."""
        # Setup: Ensure no environment variable or config
        monkeypatch.delenv("GITLAB_TOKEN", raising=False)

        # Test get_token's responsibility: error on missing token
        with pytest.raises(ConfigurationError, match="No token found"):
            get_token("https://gitlab.com", "owner", "nonexistent")
