"""Tests for 'gl-issue-sync init' command."""

import pytest

from gitlab_issue_sync.cli import main
from tests.test_helpers import in_directory


class TestInitCommand:
    """Tests for 'gl-issue-sync init' command."""

    def test_init_with_token_option(
        self,
        cli_runner,
        temp_git_repo,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
    ):
        """Test init command with --token option.

        Uses real functions: find_repository_root, get_gitlab_remote_info,
        save_project_config, ensure_storage_structure, KanbanColumnBackend.fetch_from_gitlab.
        Only mocks python-gitlab library.
        """
        from tests.factories import GitLabBoardFactory, GitLabBoardListFactory

        # Change to the temp repo directory so find_repository_root() finds it
        with in_directory(temp_git_repo):
            # Configure mock GitLab project
            mock_gitlab_project.id = 123
            mock_gitlab_project.web_url = "https://gitlab.example.com/testuser/testrepo"

            # Mock board with columns to test fetch_from_gitlab path
            board = GitLabBoardFactory(
                lists_list=[
                    GitLabBoardListFactory(label={"name": "ToDo"}),
                    GitLabBoardListFactory(label={"name": "In Progress"}),
                    GitLabBoardListFactory(label={"name": "Done"}),
                ]
            )
            mock_gitlab_project.boards.list.return_value = [board]
            mock_gitlab_project.labels.list.return_value = []  # Return empty list, not Mock
            mock_gitlab_project.milestones.list.return_value = []  # Return empty list, not Mock

            # Run command - all internal functions run normally
            result = cli_runner.invoke(main, ["init", "--token", "glpat-test-token"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "Successfully connected to GitLab" in result.output
            assert "Found 3 kanban columns" in result.output
            assert ("Initialization Complete" in result.output or "Re-initialization Complete" in result.output)

            # Verify storage structure was created in the repo
            assert (temp_git_repo / ".issues" / "opened").exists()
            assert (temp_git_repo / ".issues" / "closed").exists()

            # Note: Config is saved globally (~/.config/gitlab-issue-sync/config.toml)
            # not in the repo, so we verify success via output messages instead

    def test_init_not_git_repository(self, cli_runner, tmp_path):
        """Test init command fails when not in a git repository.

        Uses a directory without .git/ to naturally trigger GitRepositoryNotFoundError.
        """
        from gitlab_issue_sync.exit_codes import EXIT_CONFIG_ERROR

        # Create a non-git directory
        non_git_dir = tmp_path / "not_a_git_repo"
        non_git_dir.mkdir()

        with in_directory(non_git_dir):
            result = cli_runner.invoke(main, ["init", "--token", "glpat-test"])

            assert result.exit_code == EXIT_CONFIG_ERROR
            assert "Git Error" in result.output

    def test_init_invalid_token(
        self,
        cli_runner,
        temp_git_repo,
        patch_gitlab_class,
        mock_gitlab_client,
    ):
        """Test init command fails with invalid token.

        Uses real find_repository_root and get_gitlab_remote_info.
        Mocks gitlab.Gitlab to raise authentication error.
        """
        from gitlab_issue_sync.exit_codes import EXIT_AUTH_ERROR
        with in_directory(temp_git_repo):
            # Make auth() raise an exception that looks like authentication failure
            mock_gitlab_client.auth.side_effect = Exception("401 Unauthorized")

            result = cli_runner.invoke(main, ["init", "--token", "bad-token"])

            assert result.exit_code == EXIT_AUTH_ERROR
            assert "Authentication Error" in result.output


