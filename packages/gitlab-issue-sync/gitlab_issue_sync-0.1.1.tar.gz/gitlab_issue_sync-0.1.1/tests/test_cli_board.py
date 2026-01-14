"""Tests for 'gl-issue-sync board' commands."""

import pytest

from gitlab_issue_sync.cli import main
from tests.test_helpers import in_directory


class TestBoardCommands:
    """Tests for 'gl-issue-sync board' commands."""

    def test_board_columns_display(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test displaying board columns without sync.

        Uses real functions: find_repository_root, get_gitlab_remote_info, get_project_config.
        No mocking needed - just reading from config.
        """
        with in_directory(temp_git_repo):
            # Run command - all internal functions run normally
            result = cli_runner.invoke(main, ["board", "columns"])

            # Assertions
            assert result.exit_code == 0
            assert "Kanban Board Columns: (3)" in result.output
            assert "ToDo" in result.output
            assert "In Progress" in result.output
            assert "Done" in result.output

    def test_board_columns_sync(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
        mock_graphql_execute,
    ):
        """Test syncing board columns from GitLab.

        Uses real functions: find_repository_root, get_gitlab_remote_info, get_project_config,
        save_project_config, get_gitlab_client, get_project.
        Only mocks python-gitlab library.
        """
        from tests.factories import GitLabBoardFactory, GitLabBoardListFactory

        with in_directory(temp_git_repo):
            # Mock GitLab board API with factory
            board = GitLabBoardFactory(
                lists_list=[
                    GitLabBoardListFactory(label={"name": "new-column-1"}),
                    GitLabBoardListFactory(label={"name": "new-column-2"}),
                ]
            )
            mock_gitlab_project.boards.list.return_value = [board]

            # Run command - all internal functions run normally
            result = cli_runner.invoke(main, ["board", "columns", "--sync"])

            # Assertions
            assert result.exit_code == 0
            assert "Found 2 kanban columns" in result.output
            assert "Configuration updated" in result.output
            assert "new-column-1" in result.output
            assert "new-column-2" in result.output

            # Verify config was saved to temp repo
            from gitlab_issue_sync.config import get_project_config_for_repo
            updated_config = get_project_config_for_repo(temp_git_repo)
            assert updated_config is not None
            assert "new-column-1" in updated_config.board.columns
            assert "new-column-2" in updated_config.board.columns

    def test_board_move_success(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test successfully moving an issue to a new column.

        Uses real functions: find_repository_root, Issue.load, Issue.move_to_board_column, Issue.save.
        Real file I/O in temp directories.
        """
        with in_directory(temp_git_repo):
            # Create a real issue file with ToDo label
            from datetime import UTC, datetime

            from gitlab_issue_sync.storage import Issue

            issue = Issue(
                iid=1,
                title="Test Issue",
                state="opened",
                description="Test description",
                labels=["ToDo"],  # Start in todo column
                assignees=[],
                milestone=None,
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/1",
                confidential=False,
                comments=[],
            )
            issue.save(temp_git_repo)

            # Run command - real Issue.load() and Issue.move_to_board_column() will run
            result = cli_runner.invoke(main, ["board", "move", "1", "In Progress"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "Moved issue #1" in result.output
            assert "ToDo" in result.output
            assert "In Progress" in result.output

            # Verify the issue was actually moved in the file
            moved_issue = Issue.load(1, temp_git_repo)
            assert "In Progress" in moved_issue.labels
            assert "ToDo" not in moved_issue.labels

    def test_board_move_with_next_flag(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test successfully moving an issue to next column using --next flag.

        Uses real functions: find_repository_root, Issue.load, Issue.move_to_board_column, Issue.save.
        Real file I/O in temp directories.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create real issue file with todo label
            issue = Issue(
                iid=1,
                title="Test Issue",
                state="opened",
                description="Test description",
                labels=["ToDo"],  # Start in todo column
                assignees=[],
                milestone=None,
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/1",
                confidential=False,
                comments=[],
            )
            issue.save(temp_git_repo)

            # Run command with --next flag - real Issue.load() and Issue.move_to_board_column() will run
            result = cli_runner.invoke(main, ["board", "move", "1", "--next"])

            # Assertions
            assert result.exit_code == 0
            assert "Moved issue #1" in result.output

            # Verify the issue was actually moved to the next column
            moved_issue = Issue.load(1, temp_git_repo)
            # Board columns: ["ToDo", "ToDo", "In Progress", "Done"]
            # Moving from todo (index 1) should move to in-progress (index 2)
            assert "In Progress" in moved_issue.labels
            assert "ToDo" not in moved_issue.labels

    def test_board_move_issue_not_found(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test moving non-existent issue.

        Uses real functions and naturally triggers error when Issue.load() returns None.
        """
        with in_directory(temp_git_repo):
            # Run command - Issue.load() returns None, causing AttributeError
            result = cli_runner.invoke(main, ["board", "move", "999", "ToDo"])

            # Assertions
            assert result.exit_code == 1
            # Issue.load() returns None for non-existent issues
            assert "Unexpected Error" in result.output or "Error" in result.output

    def test_board_columns_no_config(
        self,
        cli_runner,
        temp_git_repo,
    ):
        """Test displaying columns when none are configured.

        Uses real functions and creates a config with empty columns.
        """
        from gitlab_issue_sync.config import BoardConfig, ProjectConfig, save_project_config

        with in_directory(temp_git_repo):
            # Create and save config with empty board columns
            empty_config = ProjectConfig(
                instance_url="https://gitlab.example.com",
                namespace="testuser",
                project="testrepo",
                token="glpat-test-token",
                board=BoardConfig(columns=[]),
                username="testuser",
            )
            save_project_config(empty_config)

            # Run command - all internal functions run normally
            result = cli_runner.invoke(main, ["board", "columns"])

            # Assertions
            assert result.exit_code == 0
            assert "No Kanban board columns configured" in result.output
            assert "board columns --sync" in result.output


