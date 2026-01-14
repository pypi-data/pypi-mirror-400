"""Tests for issue lifecycle commands (new, close, danger-delete)."""

import pytest

from gitlab_issue_sync.cli import main
from tests.test_helpers import in_directory


class TestNewCommand:
    """Tests for 'gl-issue-sync new' command (Issue #21)."""

    def test_new_command_basic(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test creating a new issue with just a title.

        Uses real functions: find_repository_root, Issue.create_new.
        Real file I/O in temp directories.
        """
        with in_directory(temp_git_repo):
            # Run command - create issue with only title
            result = cli_runner.invoke(main, ["new", "Test issue"])

            # Assertions
            assert result.exit_code == 0
            assert "Created issue T1 locally" in result.output
            assert "Test issue" in result.output
            assert "gl-issue-sync push" in result.output

            # Verify issue was actually created
            issue_file = temp_git_repo / ".issues" / "opened" / "T1.md"
            assert issue_file.exists()

            # Verify issue can be loaded
            from gitlab_issue_sync.storage import Issue
            issue = Issue.load("T1", temp_git_repo)
            assert issue is not None
            assert issue.title == "Test issue"
            assert issue.state == "opened"
            assert issue.is_temporary

    def test_new_command_with_labels(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test creating issue with labels.

        Uses real functions and real file I/O.
        """
        with in_directory(temp_git_repo):
            # Run command with labels
            result = cli_runner.invoke(main, ["new", "Bug fix", "--label", "bug", "--label", "urgent"])

            # Assertions
            assert result.exit_code == 0
            assert "Created issue T1 locally" in result.output
            assert "bug, urgent" in result.output

            # Verify labels were added
            from gitlab_issue_sync.storage import Issue
            issue = Issue.load("T1", temp_git_repo)
            assert "bug" in issue.labels
            assert "urgent" in issue.labels

    def test_new_command_with_description(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test creating issue with description.

        Uses real functions and real file I/O.
        """
        with in_directory(temp_git_repo):
            # Run command with description
            result = cli_runner.invoke(main, ["new", "Feature request", "--description", "This is a test description"])

            # Assertions
            assert result.exit_code == 0
            assert "Created issue T1 locally" in result.output
            assert "This is a test description" in result.output

            # Verify description was saved
            from gitlab_issue_sync.storage import Issue
            issue = Issue.load("T1", temp_git_repo)
            assert issue.description == "This is a test description"

    def test_new_command_with_column(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test creating issue with kanban column.

        Uses real functions and real file I/O.
        """
        with in_directory(temp_git_repo):
            # Run command with column
            result = cli_runner.invoke(main, ["new", "New feature", "--column", "ToDo"])

            # Assertions
            assert result.exit_code == 0
            assert "Created issue T1 locally" in result.output
            assert "ToDo" in result.output

            # Verify column was added as a label
            from gitlab_issue_sync.storage import Issue
            issue = Issue.load("T1", temp_git_repo)
            assert "ToDo" in issue.labels

    def test_new_command_with_assignees(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test creating issue with assignees.

        Uses real functions and real file I/O.
        """
        with in_directory(temp_git_repo):
            # Run command with assignees
            result = cli_runner.invoke(main, ["new", "Task", "--assignee", "alice", "--assignee", "bob"])

            # Assertions
            assert result.exit_code == 0
            assert "Created issue T1 locally" in result.output
            assert "alice, bob" in result.output

            # Verify assignees were added
            from gitlab_issue_sync.storage import Issue
            issue = Issue.load("T1", temp_git_repo)
            assert "alice" in issue.assignees
            assert "bob" in issue.assignees

    def test_new_command_with_milestone(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test creating issue with milestone.

        Uses real functions and real file I/O.
        """
        with in_directory(temp_git_repo):
            # Run command with milestone
            result = cli_runner.invoke(main, ["new", "Milestone task", "--milestone", "v1.0"])

            # Assertions
            assert result.exit_code == 0
            assert "Created issue T1 locally" in result.output
            assert "v1.0" in result.output

            # Verify milestone was set
            from gitlab_issue_sync.storage import Issue
            issue = Issue.load("T1", temp_git_repo)
            assert issue.milestone == "v1.0"

    def test_new_command_confidential(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test creating confidential issue.

        Uses real functions and real file I/O.
        """
        with in_directory(temp_git_repo):
            # Run command with confidential flag
            result = cli_runner.invoke(main, ["new", "Secret task", "--confidential"])

            # Assertions
            assert result.exit_code == 0
            assert "Created issue T1 locally" in result.output

            # Verify confidential flag was set
            from gitlab_issue_sync.storage import Issue
            issue = Issue.load("T1", temp_git_repo)
            assert issue.confidential is True

    def test_new_command_multiple_issues(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test creating multiple issues generates sequential temporary IDs.

        Uses real functions and real file I/O.
        """
        with in_directory(temp_git_repo):
            # Create first issue
            result1 = cli_runner.invoke(main, ["new", "First issue"])
            assert result1.exit_code == 0
            assert "Created issue T1 locally" in result1.output

            # Create second issue
            result2 = cli_runner.invoke(main, ["new", "Second issue"])
            assert result2.exit_code == 0
            assert "Created issue T2 locally" in result2.output

            # Create third issue
            result3 = cli_runner.invoke(main, ["new", "Third issue"])
            assert result3.exit_code == 0
            assert "Created issue T3 locally" in result3.output

            # Verify all issues exist
            from gitlab_issue_sync.storage import Issue
            issue1 = Issue.load("T1", temp_git_repo)
            issue2 = Issue.load("T2", temp_git_repo)
            issue3 = Issue.load("T3", temp_git_repo)
            assert issue1.title == "First issue"
            assert issue2.title == "Second issue"
            assert issue3.title == "Third issue"

    def test_new_command_invalid_column(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test error when creating issue with invalid column.

        Uses real functions and naturally triggers error.
        """
        with in_directory(temp_git_repo):
            # Run command with invalid column
            result = cli_runner.invoke(main, ["new", "Task", "--column", "InvalidColumn"])

            # Assertions
            assert result.exit_code == 1
            assert "Column not found" in result.output or "Invalid column" in result.output

    def test_new_command_all_options(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test creating issue with all options combined.

        Uses real functions and real file I/O.
        """
        with in_directory(temp_git_repo):
            # Run command with all options
            result = cli_runner.invoke(
                main,
                [
                    "new",
                    "Complex task",
                    "--label",
                    "feature",
                    "--label",
                    "backend",
                    "--assignee",
                    "alice",
                    "--description",
                    "Detailed description",
                    "--column",
                    "In Progress",
                    "--milestone",
                    "v2.0",
                    "--confidential",
                ],
            )

            # Assertions
            assert result.exit_code == 0
            assert "Created issue T1 locally" in result.output

            # Verify all attributes
            from gitlab_issue_sync.storage import Issue
            issue = Issue.load("T1", temp_git_repo)
            assert issue.title == "Complex task"
            assert "feature" in issue.labels
            assert "backend" in issue.labels
            assert "In Progress" in issue.labels
            assert "alice" in issue.assignees
            assert issue.description == "Detailed description"
            assert issue.milestone == "v2.0"
            assert issue.confidential is True

    def test_new_command_with_parent(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test creating a new issue with --parent option."""
        with in_directory(temp_git_repo):
            # Create parent issue first (regular issue with numeric IID)
            from tests.factories import IssueFactory
            parent_issue = IssueFactory(iid=1, title="Parent task")
            parent_issue.save(temp_git_repo)

            # Run command - create child issue with parent (using integer IID)
            result = cli_runner.invoke(main, ["new", "Child task", "--parent", "1"])

            # Assertions
            assert result.exit_code == 0
            assert "Created issue T1 locally" in result.output
            assert "Parent: #1" in result.output

            # Verify issue was created with parent
            from gitlab_issue_sync.storage import Issue
            child_issue = Issue.load("T1", temp_git_repo)
            assert child_issue is not None
            assert child_issue.title == "Child task"
            assert child_issue.parent_iid == 1



class TestCloseCommand:
    """Tests for 'gl-issue-sync close' command."""

    def test_close_open_issue(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test closing an open issue with kanban labels.

        Uses real functions: find_repository_root, Issue.load, Issue.close, KanbanColumn.get_column_names.
        Real file I/O in temp directories.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create real issue file with kanban label
            issue = Issue(
                iid=1,
                title="Test Issue",
                state="opened",
                description="Test description",
                labels=["ToDo", "bug"],  # "ToDo" is kanban column, "bug" is regular label
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

            # Run command - real Issue.close() will run
            result = cli_runner.invoke(main, ["close", "1"])

            # Assertions
            assert result.exit_code == 0
            assert "Closed issue #1" in result.output

            # Verify issue was actually closed and kanban label removed
            closed_issue = Issue.load(1, temp_git_repo)
            assert closed_issue.state == "closed"
            assert "ToDo" not in closed_issue.labels  # Kanban label removed
            assert "bug" in closed_issue.labels  # Regular label preserved

    def test_close_already_closed_issue(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test closing an already closed issue (idempotent).

        Uses real functions and real file I/O.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create real closed issue file
            issue = Issue(
                iid=2,
                title="Already Closed",
                state="closed",
                description="Test",
                labels=["bug"],
                assignees=[],
                milestone=None,
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/2",
                confidential=False,
                comments=[],
            )
            issue.save(temp_git_repo)

            # Run command
            result = cli_runner.invoke(main, ["close", "2"])

            # Assertions
            assert result.exit_code == 0
            assert "already closed" in result.output.lower() or "Closed issue #2" in result.output

            # Verify issue is still closed
            closed_issue = Issue.load(2, temp_git_repo)
            assert closed_issue.state == "closed"

    def test_close_issue_not_found(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test closing non-existent issue.

        Uses real functions and naturally triggers error when Issue.load() returns None.
        """
        with in_directory(temp_git_repo):
            # Run command - Issue.load() returns None, causing AttributeError
            result = cli_runner.invoke(main, ["close", "999"])

            # Assertions
            assert result.exit_code == 1
            assert "Error" in result.output



class TestDangerDeleteCommand:
    """Tests for 'gl-issue-sync danger-delete' command."""

    def test_danger_delete_with_yes_flag(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
        mock_graphql_execute,
    ):
        """Test deleting issues with --yes flag to skip confirmation.

        Uses real functions: find_repository_root, get_gitlab_remote_info, get_project_config.
        Only mocks python-gitlab library.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create real issue files
            issue1 = Issue(
                iid=1,
                title="Issue to Delete",
                state="opened",
                description="Test",
                labels=[],
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

            # Mock GitLab API responses - use factory
            from tests.factories import GitLabIssueFactory
            mock_issue = GitLabIssueFactory(iid=1)
            mock_gitlab_project.issues.get.return_value = mock_issue

            # Run command with --yes flag
            result = cli_runner.invoke(main, ["danger-delete", "1", "--yes"])

            # Assertions
            assert result.exit_code == 0
            assert "DANGER ZONE" in result.output
            assert "Deleted issue #1" in result.output
            mock_gitlab_project.issues.get.assert_called_once_with(1)
            mock_issue.delete.assert_called_once()

            # Verify local file was deleted
            assert not (temp_git_repo / ".issues" / "opened" / "1.md").exists()

    def test_danger_delete_multiple_issues(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
        mock_graphql_execute,
    ):
        """Test deleting multiple issues at once.

        Uses real functions and real file I/O.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create real issue files
            for iid in [1, 2, 3]:
                issue = Issue(
                    iid=iid,
                    title=f"Issue {iid}",
                    state="opened",
                    description="Test",
                    labels=[],
                    assignees=[],
                    milestone=None,
                    created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                    updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                    author="testuser",
                    web_url=f"https://gitlab.example.com/testuser/testrepo/-/issues/{iid}",
                    confidential=False,
                    comments=[],
                )
                issue.save(temp_git_repo)

            # Mock GitLab API responses - use factory
            from tests.factories import GitLabIssueFactory

            def get_issue(iid):
                return GitLabIssueFactory(iid=iid)

            mock_gitlab_project.issues.get.side_effect = get_issue

            # Run command
            result = cli_runner.invoke(main, ["danger-delete", "1", "2", "3", "--yes"])

            # Assertions
            assert result.exit_code == 0
            assert "Deleted: 3/3" in result.output
            assert mock_gitlab_project.issues.get.call_count == 3

            # Verify local files were deleted
            assert not (temp_git_repo / ".issues" / "opened" / "1.md").exists()
            assert not (temp_git_repo / ".issues" / "opened" / "2.md").exists()
            assert not (temp_git_repo / ".issues" / "opened" / "3.md").exists()

    def test_danger_delete_without_yes_flag_cancelled(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
        mock_graphql_execute,
    ):
        """Test that danger-delete prompts for confirmation without --yes.

        Uses real functions and real file I/O.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create real issue file
            issue = Issue(
                iid=1,
                title="Issue",
                state="opened",
                description="Test",
                labels=[],
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

            # Run command without --yes, simulate "n" input
            result = cli_runner.invoke(main, ["danger-delete", "1"], input="n\n")

            # Assertions
            assert result.exit_code == 0
            assert "DANGER ZONE" in result.output
            assert "Cancelled" in result.output or "cancelled" in result.output.lower()
            # Issue should not be deleted
            mock_gitlab_project.issues.get.assert_not_called()

            # Verify local file still exists
            assert (temp_git_repo / ".issues" / "opened" / "1.md").exists()


