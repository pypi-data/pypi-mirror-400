"""Tests for 'gl-issue-sync parent' commands."""

import pytest

from gitlab_issue_sync.cli import main
from tests.test_helpers import in_directory


class TestParentCommand:
    """Tests for 'gl-issue-sync parent' command."""

    def test_parent_show(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test showing current parent."""
        with in_directory(temp_git_repo):
            # Create issues with parent relationship
            from tests.factories import IssueFactory
            parent_issue = IssueFactory(iid=1, title="Parent task")
            parent_issue.save(temp_git_repo)

            child_issue = IssueFactory(iid=2, title="Child task", parent_iid=1)
            child_issue.save(temp_git_repo)

            # Run command
            result = cli_runner.invoke(main, ["parent", "2"])

            # Assertions
            assert result.exit_code == 0
            assert "Parent for Issue #2" in result.output
            assert "#1" in result.output

    def test_parent_show_no_parent(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test showing parent when none is set."""
        with in_directory(temp_git_repo):
            # Create issue without parent
            from tests.factories import IssueFactory
            issue = IssueFactory(iid=1, title="Standalone task", parent_iid=None)
            issue.save(temp_git_repo)

            # Run command
            result = cli_runner.invoke(main, ["parent", "1"])

            # Assertions
            assert result.exit_code == 0
            assert "No parent set" in result.output

    def test_parent_set(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test setting parent."""
        with in_directory(temp_git_repo):
            # Create issues
            from tests.factories import IssueFactory
            parent_issue = IssueFactory(iid=1, title="Parent task")
            parent_issue.save(temp_git_repo)

            child_issue = IssueFactory(iid=2, title="Child task", parent_iid=None)
            child_issue.save(temp_git_repo)

            # Run command - set parent
            result = cli_runner.invoke(main, ["parent", "2", "set", "1"])

            # Assertions
            assert result.exit_code == 0
            assert "Updated parent for issue #2" in result.output

            # Verify parent was set
            from gitlab_issue_sync.storage import Issue
            reloaded = Issue.load(2, temp_git_repo)
            assert reloaded.parent_iid == 1

    def test_parent_unset(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test unsetting parent."""
        with in_directory(temp_git_repo):
            # Create issues with parent
            from tests.factories import IssueFactory
            parent_issue = IssueFactory(iid=1, title="Parent task")
            parent_issue.save(temp_git_repo)

            child_issue = IssueFactory(iid=2, title="Child task", parent_iid=1)
            child_issue.save(temp_git_repo)

            # Verify parent is set
            assert child_issue.parent_iid == 1

            # Run command - unset parent
            result = cli_runner.invoke(main, ["parent", "2", "unset"])

            # Assertions
            assert result.exit_code == 0
            assert "Updated parent for issue #2" in result.output

            # Verify parent was unset
            from gitlab_issue_sync.storage import Issue
            reloaded = Issue.load(2, temp_git_repo)
            assert reloaded.parent_iid is None

    def test_parent_change(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test changing parent from one to another."""
        with in_directory(temp_git_repo):
            # Create issues
            from tests.factories import IssueFactory
            parent1 = IssueFactory(iid=1, title="Parent 1")
            parent1.save(temp_git_repo)

            parent2 = IssueFactory(iid=2, title="Parent 2")
            parent2.save(temp_git_repo)

            child = IssueFactory(iid=3, title="Child task", parent_iid=1)
            child.save(temp_git_repo)

            # Verify initial parent
            assert child.parent_iid == 1

            # Run command - change parent
            result = cli_runner.invoke(main, ["parent", "3", "set", "2"])

            # Assertions
            assert result.exit_code == 0
            assert "Updated parent for issue #3" in result.output

            # Verify parent was changed
            from gitlab_issue_sync.storage import Issue
            reloaded = Issue.load(3, temp_git_repo)
            assert reloaded.parent_iid == 2


# ===== Exit Code Tests =====


