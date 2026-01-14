"""Tests for 'gl-issue-sync comment' command."""

import pytest

from gitlab_issue_sync.cli import main
from tests.test_helpers import in_directory


class TestCommentCommand:
    """Tests for 'gl-issue-sync comment' command."""

    def test_comment_success(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test adding a comment successfully.

        Uses real functions: find_repository_root, get_gitlab_remote_info,
        get_project_config, Issue.load, Issue.add_comment, Issue.save.
        Real file I/O in temp directories.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create real issue file
            test_issue = Issue(
                iid=1,
                title="Test Issue",
                state="opened",
                description="Test description",
                created_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 2, 11, 0, 0, tzinfo=UTC),
                author="emma",
                web_url="https://gitlab.example.com/testuser/testrepo/-/issues/1",
                confidential=False,
                assignees=[],
                labels=[],
                milestone=None,
                comments=[],
            )
            test_issue.save(temp_git_repo)

            # Run command - all internal functions run normally
            result = cli_runner.invoke(main, ["comment", "1", "Great work!"])

            # Assertions
            assert result.exit_code == 0
            assert "Comment added to issue #1" in result.output
            assert "Author: testuser" in result.output

            # Verify comment was actually added to the file
            loaded_issue = Issue.load(1, temp_git_repo)
            assert len(loaded_issue.comments) == 1
            assert loaded_issue.comments[0].body == "Great work!"
            assert loaded_issue.comments[0].author == "testuser"

    def test_comment_issue_not_found(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test commenting on non-existent issue.

        Uses real functions and naturally triggers error when Issue.load() returns None.
        """
        with in_directory(temp_git_repo):
            # Run command - Issue.load() returns None, causing AttributeError
            result = cli_runner.invoke(main, ["comment", "999", "Test comment"])

            # Assertions
            assert result.exit_code == 1
            # Issue.load() returns None for non-existent issues, which causes
            # AttributeError when trying to call .add_comment() on None
            assert "Unexpected Error" in result.output or "Error" in result.output


