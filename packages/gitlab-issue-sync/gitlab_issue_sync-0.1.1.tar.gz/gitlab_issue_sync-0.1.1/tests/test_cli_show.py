"""Tests for 'gl-issue-sync show' command."""

import pytest

from gitlab_issue_sync.cli import main
from tests.test_helpers import in_directory


class TestShowCommand:
    """Tests for the show command."""

    def test_show_open_issue_success(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test showing an open issue works offline with cached label colors.

        Uses real functions: find_repository_root, Issue.load, KanbanColumn.get_column_names,
        Label.get_colors_map.
        Real file I/O in temp directories.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue, IssueComment, Label

        with in_directory(temp_git_repo):
            # Create real label files for colors
            label1 = Label(name="bug", color="#FF0000", description="Bugs")
            label1.status = "synced"
            label1.save(temp_git_repo)

            label2 = Label(name="priority-high", color="#FFA500", description="High priority")
            label2.status = "synced"
            label2.save(temp_git_repo)

            # Create real issue file with Kanban column label and regular labels
            test_issue = Issue(
                iid=1,
                title="Test Issue",
                state="opened",
                description="This is a test issue description",
                labels=["ToDo", "bug", "priority-high"],  # "ToDo" is a Kanban column
                assignees=["alice", "bob"],
                milestone="v1.0",
                created_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 2, 11, 0, 0, tzinfo=UTC),
                author="emma",
                web_url="https://gitlab.example.com/test/project/-/issues/1",
                confidential=False,
                comments=[
                    IssueComment(
                        author="john",
                        created_at=datetime(2026, 1, 1, 14, 30, 0, tzinfo=UTC),
                        body="This is a test comment",
                    )
                ],
            )
            test_issue.save(temp_git_repo)

            # Run command - all internal functions run normally
            result = cli_runner.invoke(main, ["show", "1"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "Test Issue" in result.output
            assert "#1" in result.output
            assert "opened" in result.output
            assert "emma" in result.output
            assert "This is a test issue description" in result.output
            # Check that Kanban column label is separated
            assert "Column:" in result.output
            assert "ToDo" in result.output
            # Check regular labels
            assert "bug" in result.output
            assert "priority-high" in result.output
            assert "alice" in result.output
            assert "v1.0" in result.output
            assert "john" in result.output
            assert "This is a test comment" in result.output

    def test_show_closed_issue_success(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test showing a closed issue.

        Uses real functions and real file I/O.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create real issue file
            test_issue = Issue(
                iid=2,
                title="Closed Issue",
                state="closed",
                description="This issue is closed",
                created_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 2, 11, 0, 0, tzinfo=UTC),
                author="emma",
                web_url="https://gitlab.example.com/test/project/-/issues/2",
                confidential=False,
                assignees=[],
                labels=[],
                milestone=None,
                comments=[],
            )
            test_issue.save(temp_git_repo)

            # Run command
            result = cli_runner.invoke(main, ["show", "2"])

            # Assertions
            assert result.exit_code == 0
            assert "Closed Issue" in result.output
            assert "#2" in result.output
            assert "closed" in result.output

    def test_show_issue_not_found(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test showing a non-existent issue.

        Uses real functions and naturally triggers StorageError.
        """
        with in_directory(temp_git_repo):
            # Run command - Issue.load() will naturally raise StorageError
            result = cli_runner.invoke(main, ["show", "999"])

            # Assertions
            assert result.exit_code == 1
            assert "Storage Error" in result.output
            assert "#999" in result.output

    def test_show_confidential_issue(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test showing a confidential issue.

        Uses real functions and real file I/O.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create real confidential issue file
            test_issue = Issue(
                iid=3,
                title="Confidential Issue",
                state="opened",
                description="This is confidential",
                created_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 2, 11, 0, 0, tzinfo=UTC),
                author="emma",
                confidential=True,
                web_url="https://gitlab.example.com/test/project/-/issues/3",
                assignees=[],
                labels=[],
                milestone=None,
                comments=[],
            )
            test_issue.save(temp_git_repo)

            # Run command
            result = cli_runner.invoke(main, ["show", "3"])

            # Assertions
            assert result.exit_code == 0
            assert "Confidential Issue" in result.output
            assert "Confidential" in result.output
            assert "Yes" in result.output


