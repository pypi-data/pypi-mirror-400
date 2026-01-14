"""Tests for 'gl-issue-sync list' command."""

import pytest

from gitlab_issue_sync.cli import main
from tests.test_helpers import in_directory


class TestListCommand:
    """Tests for 'gl-issue-sync list' command."""

    def test_list_default(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test list command with default options works offline with cached labels.

        Uses real functions: find_repository_root, Issue.filter, KanbanColumn.get_column_names,
        Label.get_colors_map.
        Real file I/O in temp directories.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue, Label

        with in_directory(temp_git_repo):
            # Create real label files for colors
            label1 = Label(name="bug", color="#FF0000", description="Bugs")
            label1.status = "synced"
            label1.save(temp_git_repo)

            label2 = Label(name="feature", color="#00FF00", description="Features")
            label2.status = "synced"
            label2.save(temp_git_repo)

            # Create real issue files
            issue1 = Issue(
                iid=1,
                title="Test Issue 1",
                state="opened",
                description="Test",
                labels=["ToDo", "bug"],
                assignees=["user1"],
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
                title="Test Issue 2",
                state="opened",
                description="Test",
                labels=["In Progress", "feature"],
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

            # Run command - all internal functions run normally
            result = cli_runner.invoke(main, ["list"])

            # Assertions
            assert result.exit_code == 0
            assert "Issues (2 found)" in result.output
            assert "#1" in result.output
            assert "#2" in result.output
            assert "Test Issue 1" in result.output
            assert "Test Issue 2" in result.output

    def test_list_with_state_filter(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test list command with --state filter.

        Uses real functions: find_repository_root, Issue.filter, KanbanColumn.get_column_names,
        Label.get_colors_map.
        Real file I/O in temp directories.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create real closed issue file
            closed_issue = Issue(
                iid=5,
                title="Closed Issue",
                state="closed",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/5",
                confidential=False,
                comments=[],
            )
            closed_issue.save(temp_git_repo)

            # Create an open issue to verify filtering works
            open_issue = Issue(
                iid=6,
                title="Open Issue",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/6",
                confidential=False,
                comments=[],
            )
            open_issue.save(temp_git_repo)

            # Run command - all internal functions run normally
            result = cli_runner.invoke(main, ["list", "--state", "closed"])

            # Assertions
            assert result.exit_code == 0
            assert "Issues (1 found)" in result.output
            assert "#5" in result.output
            assert "Closed Issue" in result.output
            # Verify open issue is not shown
            assert "#6" not in result.output

    def test_list_with_column_filter_by_name(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test list command with --column filter by name.

        Uses real functions: find_repository_root, Issue.filter, KanbanColumn.get_column_names,
        Label.get_colors_map.
        Real file I/O in temp directories.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue, Label

        with in_directory(temp_git_repo):
            # Create real label file for colors
            label1 = Label(name="feature", color="#00FF00", description="Features")
            label1.status = "synced"
            label1.save(temp_git_repo)

            # Create issues with different columns
            issue1 = Issue(
                iid=1,
                title="In Progress Issue",
                state="opened",
                description="Test",
                labels=["In Progress", "feature"],
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

            # Run command - all internal functions run normally
            result = cli_runner.invoke(main, ["list", "--column", "In Progress"])

            # Assertions
            assert result.exit_code == 0
            assert "Issues (1 found)" in result.output
            assert "#1" in result.output
            assert "In Progress Issue" in result.output
            # Verify other issue is not shown
            assert "#2" not in result.output

    def test_list_with_column_filter_by_index(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test list command with --column filter by numeric index.

        Uses real functions: find_repository_root, Issue.filter, KanbanColumn.get_column_names,
        Label.get_colors_map.
        Real file I/O in temp directories.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create issues with different column assignments
            # Column 0 = "ToDo" (no label)
            issue1 = Issue(
                iid=1,
                title="Backlog Issue",
                state="opened",
                description="Test",
                labels=[],  # No kanban column = backlog
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

            # Column 1 = "ToDo"
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

            # Run command - filter by column 0 (backlog)
            result = cli_runner.invoke(main, ["list", "--column", "0"])

            # Assertions
            assert result.exit_code == 0
            assert "Issues (1 found)" in result.output
            assert "#1" in result.output
            assert "Backlog Issue" in result.output
            # Verify other issue is not shown
            assert "#2" not in result.output

    def test_list_with_multiple_column_filter(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test list command with multiple --column filters (OR logic)."""
        from tests.factories import IssueFactory

        with in_directory(temp_git_repo):
            # Only specify what we care about: iid, title, labels
            IssueFactory(iid=1, title="In Progress Issue", labels=["In Progress"]).save(temp_git_repo)
            IssueFactory(iid=2, title="Done Issue", labels=["Done"]).save(temp_git_repo)
            IssueFactory(iid=3, title="Todo Issue", labels=["ToDo"]).save(temp_git_repo)

            # Test: OR logic - issues in EITHER column should be included
            result = cli_runner.invoke(main, ["list", "--column", "In Progress", "--column", "Done"])

            if result.exit_code != 0:
                print(f"Output: {result.output}")
                print(f"Exception: {result.exception}")
            assert result.exit_code == 0
            assert "Issues (2 found)" in result.output
            assert "#1" in result.output
            assert "#2" in result.output
            assert "#3" not in result.output

    def test_list_with_label_filter(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test list command with --label filter (AND logic).

        Uses real functions: find_repository_root, Issue.filter, KanbanColumn.get_column_names,
        Label.get_colors_map.
        Real file I/O in temp directories.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create issue with both labels
            issue1 = Issue(
                iid=1,
                title="Bug + Urgent",
                state="opened",
                description="Test",
                labels=["bug", "urgent"],
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

            # Create issue with only one label
            issue2 = Issue(
                iid=2,
                title="Just Bug",
                state="opened",
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
            issue2.save(temp_git_repo)

            # Run command - filter by bug AND urgent (AND logic)
            result = cli_runner.invoke(main, ["list", "--label", "bug", "--label", "urgent"])

            # Assertions
            assert result.exit_code == 0
            assert "Issues (1 found)" in result.output
            assert "#1" in result.output
            assert "Bug + Urgent" in result.output
            # Verify other issue is not shown
            assert "#2" not in result.output

    def test_list_empty_results(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test list command with no matching issues.

        Uses real functions: find_repository_root, Issue.filter, KanbanColumn.get_column_names,
        Label.get_colors_map.
        Real file I/O in temp directories.
        """
        with in_directory(temp_git_repo):
            # Don't create any issues - directory is empty
            # Run command - all internal functions run normally
            result = cli_runner.invoke(main, ["list"])

            # Assertions
            assert result.exit_code == 0
            assert "Issues (0 found)" in result.output
            assert "No issues found matching the specified filters" in result.output

    def test_list_sorts_by_iid(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test list command sorts results by IID ascending.

        Uses real functions: find_repository_root, Issue.filter, KanbanColumn.get_column_names,
        Label.get_colors_map.
        Real file I/O in temp directories.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create issues in non-sorted order to verify sorting
            # Issue.filter() should sort them by IID
            issue3 = Issue(
                iid=15,
                title="Issue 15",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/15",
                confidential=False,
                comments=[],
            )
            issue3.save(temp_git_repo)

            issue1 = Issue(
                iid=5,
                title="Issue 5",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/5",
                confidential=False,
                comments=[],
            )
            issue1.save(temp_git_repo)

            issue2 = Issue(
                iid=10,
                title="Issue 10",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/10",
                confidential=False,
                comments=[],
            )
            issue2.save(temp_git_repo)

            # Run command - all internal functions run normally
            result = cli_runner.invoke(main, ["list"])

            # Assertions
            assert result.exit_code == 0
            # Check that issues appear in sorted order in output
            output_lines = result.output.split("\n")
            iid_5_index = next(i for i, line in enumerate(output_lines) if "#5" in line)
            iid_10_index = next(i for i, line in enumerate(output_lines) if "#10" in line)
            iid_15_index = next(i for i, line in enumerate(output_lines) if "#15" in line)
            assert iid_5_index < iid_10_index < iid_15_index


