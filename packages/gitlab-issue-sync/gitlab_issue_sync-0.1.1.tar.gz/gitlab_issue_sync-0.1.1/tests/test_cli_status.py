"""Tests for 'gl-issue-sync status' command."""

import pytest

from gitlab_issue_sync.cli import main
from tests.test_helpers import in_directory


class TestStatusCommand:
    """Tests for 'gl-issue-sync status' command."""

    def test_status_success(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test status command displays project info.

        Uses real functions: find_repository_root, get_gitlab_remote_info,
        get_project_config, Issue.list_all, Issue.save.
        Real file I/O in temp directories.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create real issue files with different labels
            issue1 = Issue(
                iid=1,
                title="Backlog Issue",
                state="opened",
                description="Test",
                labels=["ToDo"],
                assignees=[],
                milestone=None,
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/1",
                confidential=False,
                comments=[],
            )
            issue1.save(temp_git_repo)

            issue2 = Issue(
                iid=2,
                title="Todo Issue",
                state="opened",
                description="Test",
                labels=["ToDo"],
                assignees=[],
                milestone=None,
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/2",
                confidential=False,
                comments=[],
            )
            issue2.save(temp_git_repo)

            issue3 = Issue(
                iid=3,
                title="In Progress Issue",
                state="opened",
                description="Test",
                labels=["In Progress"],
                assignees=[],
                milestone=None,
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/3",
                confidential=False,
                comments=[],
            )
            issue3.save(temp_git_repo)

            issue4 = Issue(
                iid=4,
                title="Closed Issue",
                state="closed",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/4",
                confidential=False,
                comments=[],
            )
            issue4.save(temp_git_repo)

            # Run command - all internal functions run normally
            result = cli_runner.invoke(main, ["status"])

            # Assertions
            assert result.exit_code == 0
            assert "GitLab Issue Sync Status" in result.output
            assert "testuser/testrepo" in result.output
            # Verify Kanban column grouping
            assert "ToDo: 2" in result.output  # issue1 and issue2
            assert "In Progress: 1" in result.output  # issue3
            assert "Closed: 1" in result.output
            assert "Total: 4" in result.output

    def test_status_not_initialized(self, cli_runner, tmp_path):
        """Test status command when not initialized.

        Uses a temp directory without git repo to naturally trigger error.
        """
        from gitlab_issue_sync.exit_codes import EXIT_CONFIG_ERROR

        # Create a non-git directory
        non_git_dir = tmp_path / "not_a_git_repo"
        non_git_dir.mkdir()

        with in_directory(non_git_dir):
            result = cli_runner.invoke(main, ["status"])

            assert result.exit_code == EXIT_CONFIG_ERROR
            assert "Git Error" in result.output

    def test_status_without_kanban_columns(
        self,
        cli_runner,
        temp_git_repo,
    ):
        """Test status command when no kanban columns are configured.

        Uses real functions: find_repository_root, get_project_config, Issue.list_all.
        Real file I/O in temp directories.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.config import BoardConfig, ProjectConfig, save_project_config
        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create config without kanban columns
            config = ProjectConfig(
                instance_url="https://gitlab.example.com",
                namespace="testuser",
                project="testrepo",
                token="test-token",
                board=BoardConfig(columns=[]),  # Empty kanban columns
            )
            save_project_config(config)

            # Create some issues
            issue1 = Issue(
                iid=1,
                title="Open Issue",
                state="opened",
                description="Test",
                labels=["bug"],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/1",
                confidential=False,
                comments=[],
            )
            issue1.save(temp_git_repo)

            issue2 = Issue(
                iid=2,
                title="Closed Issue",
                state="closed",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/2",
                confidential=False,
                comments=[],
            )
            issue2.save(temp_git_repo)

            # Run command
            result = cli_runner.invoke(main, ["status"])

            # Assertions
            assert result.exit_code == 0
            # Without kanban columns, should show simple Open/Closed counts
            assert "Open: 1" in result.output
            assert "Closed: 1" in result.output
            # Should indicate no kanban board configured
            assert "Not configured" in result.output


