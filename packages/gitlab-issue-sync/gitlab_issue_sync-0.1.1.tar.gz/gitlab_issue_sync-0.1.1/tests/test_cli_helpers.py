"""Tests for CLI helper functions and error handling."""

import pytest

from gitlab_issue_sync.cli import handle_cli_errors, main
from gitlab_issue_sync.config import ConfigurationError
from gitlab_issue_sync.git_utils import GitLabRemoteNotFoundError, GitRepositoryNotFoundError
from gitlab_issue_sync.issue_sync import AuthenticationError, SyncError
from gitlab_issue_sync.storage import StorageError
from tests.test_helpers import in_directory


class TestHandleCliErrors:
    """Tests for the @handle_cli_errors decorator."""

    def test_handles_git_repository_not_found_error(self, capsys):
        """Test decorator handles GitRepositoryNotFoundError."""
        from gitlab_issue_sync.exit_codes import EXIT_CONFIG_ERROR

        @handle_cli_errors
        def test_func():
            raise GitRepositoryNotFoundError("/some/path")

        with pytest.raises(SystemExit) as exc_info:
            test_func()

        assert exc_info.value.code == EXIT_CONFIG_ERROR
        captured = capsys.readouterr()
        assert "Git Error" in captured.err
        assert "Make sure you're in a git repository" in captured.err

    def test_handles_gitlab_remote_not_found_error(self, capsys):
        """Test decorator handles GitLabRemoteNotFoundError."""
        from gitlab_issue_sync.exit_codes import EXIT_CONFIG_ERROR

        @handle_cli_errors
        def test_func():
            raise GitLabRemoteNotFoundError()

        with pytest.raises(SystemExit) as exc_info:
            test_func()

        assert exc_info.value.code == EXIT_CONFIG_ERROR
        captured = capsys.readouterr()
        assert "Git Error" in captured.err

    def test_handles_configuration_error(self, capsys):
        """Test decorator handles ConfigurationError with hint."""
        from gitlab_issue_sync.exit_codes import EXIT_CONFIG_ERROR

        @handle_cli_errors
        def test_func():
            raise ConfigurationError("No config found")

        with pytest.raises(SystemExit) as exc_info:
            test_func()

        assert exc_info.value.code == EXIT_CONFIG_ERROR
        captured = capsys.readouterr()
        assert "Configuration Error" in captured.err
        assert "gl-issue-sync init" in captured.err

    def test_handles_storage_error(self, capsys):
        """Test decorator handles StorageError."""
        @handle_cli_errors
        def test_func():
            raise StorageError("Failed to save file")

        with pytest.raises(SystemExit) as exc_info:
            test_func()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Storage Error" in captured.err
        assert "Failed to save file" in captured.err

    def test_handles_sync_error(self, capsys):
        """Test decorator handles SyncError."""
        from gitlab_issue_sync.exit_codes import EXIT_API_ERROR

        @handle_cli_errors
        def test_func():
            raise SyncError("GitLab API failed")

        with pytest.raises(SystemExit) as exc_info:
            test_func()

        assert exc_info.value.code == EXIT_API_ERROR
        captured = capsys.readouterr()
        assert "Sync Error" in captured.err
        assert "GitLab API failed" in captured.err

    def test_handles_value_error(self, capsys):
        """Test decorator handles ValueError."""
        @handle_cli_errors
        def test_func():
            raise ValueError("Invalid value")

        with pytest.raises(SystemExit) as exc_info:
            test_func()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Validation Error" in captured.err
        assert "Invalid value" in captured.err

    def test_handles_unexpected_exception(self, capsys):
        """Test decorator handles unexpected exceptions with traceback."""
        @handle_cli_errors
        def test_func():
            raise RuntimeError("Something went wrong")

        with pytest.raises(SystemExit) as exc_info:
            test_func()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Unexpected Error" in captured.err
        assert "Something went wrong" in captured.err
        # Traceback should be printed
        assert "Traceback" in captured.err

    def test_decorator_preserves_function_return_value(self):
        """Test decorator allows successful function execution."""
        @handle_cli_errors
        def test_func(x, y):
            return x + y

        result = test_func(2, 3)
        assert result == 5

    def test_decorator_preserves_function_metadata(self):
        """Test decorator preserves function name and docstring."""
        @handle_cli_errors
        def test_func():
            """Test docstring."""
            pass

        assert test_func.__name__ == "test_func"
        assert test_func.__doc__ == "Test docstring."



class TestCLIHelp:
    """Tests for CLI help messages."""

    def test_main_help(self, cli_runner):
        """Test main help message."""
        result = cli_runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "GitLab issue synchronization tool" in result.output
        assert "init" in result.output
        assert "pull" in result.output
        assert "status" in result.output

    def test_init_help(self, cli_runner):
        """Test init command help."""
        result = cli_runner.invoke(main, ["init", "--help"])

        assert result.exit_code == 0
        assert "Initialize repository" in result.output
        assert "--token" in result.output

    def test_pull_help(self, cli_runner):
        """Test pull command help."""
        result = cli_runner.invoke(main, ["pull", "--help"])

        assert result.exit_code == 0
        assert "Pull issues from GitLab" in result.output
        assert "--state" in result.output

    def test_status_help(self, cli_runner):
        """Test status command help."""
        result = cli_runner.invoke(main, ["status", "--help"])

        assert result.exit_code == 0
        assert "synchronization status" in result.output



# ===== Standalone Tests for Error Handling =====

def test_handle_cli_errors_git_repository_not_found():
    """Test that GitRepositoryNotFoundError returns EXIT_CONFIG_ERROR."""
    from gitlab_issue_sync.exit_codes import EXIT_CONFIG_ERROR

    @handle_cli_errors
    def test_func():
        raise GitRepositoryNotFoundError("Not in a git repository")

    with pytest.raises(SystemExit) as exc_info:
        test_func()

    assert exc_info.value.code == EXIT_CONFIG_ERROR


def test_handle_cli_errors_gitlab_remote_not_found():
    """Test that GitLabRemoteNotFoundError returns EXIT_CONFIG_ERROR."""
    from gitlab_issue_sync.exit_codes import EXIT_CONFIG_ERROR

    @handle_cli_errors
    def test_func():
        raise GitLabRemoteNotFoundError("No GitLab remote found")

    with pytest.raises(SystemExit) as exc_info:
        test_func()

    assert exc_info.value.code == EXIT_CONFIG_ERROR


def test_handle_cli_errors_configuration_error():
    """Test that ConfigurationError returns EXIT_CONFIG_ERROR."""
    from gitlab_issue_sync.exit_codes import EXIT_CONFIG_ERROR

    @handle_cli_errors
    def test_func():
        raise ConfigurationError("Configuration not found")

    with pytest.raises(SystemExit) as exc_info:
        test_func()

    assert exc_info.value.code == EXIT_CONFIG_ERROR


def test_handle_cli_errors_storage_error():
    """Test that StorageError returns EXIT_GENERAL_ERROR."""
    from gitlab_issue_sync.exit_codes import EXIT_GENERAL_ERROR

    @handle_cli_errors
    def test_func():
        raise StorageError("Failed to read file")

    with pytest.raises(SystemExit) as exc_info:
        test_func()

    assert exc_info.value.code == EXIT_GENERAL_ERROR


def test_handle_cli_errors_authentication_error():
    """Test that AuthenticationError returns EXIT_AUTH_ERROR."""
    from gitlab_issue_sync.exit_codes import EXIT_AUTH_ERROR

    @handle_cli_errors
    def test_func():
        raise AuthenticationError("Invalid GitLab token")

    with pytest.raises(SystemExit) as exc_info:
        test_func()

    assert exc_info.value.code == EXIT_AUTH_ERROR


def test_handle_cli_errors_sync_error():
    """Test that SyncError returns EXIT_API_ERROR."""
    from gitlab_issue_sync.exit_codes import EXIT_API_ERROR

    @handle_cli_errors
    def test_func():
        raise SyncError("GitLab API request failed")

    with pytest.raises(SystemExit) as exc_info:
        test_func()

    assert exc_info.value.code == EXIT_API_ERROR


def test_handle_cli_errors_value_error():
    """Test that ValueError returns EXIT_GENERAL_ERROR."""
    from gitlab_issue_sync.exit_codes import EXIT_GENERAL_ERROR

    @handle_cli_errors
    def test_func():
        raise ValueError("Invalid input")

    with pytest.raises(SystemExit) as exc_info:
        test_func()

    assert exc_info.value.code == EXIT_GENERAL_ERROR


def test_handle_cli_errors_unexpected_error():
    """Test that unexpected errors return EXIT_GENERAL_ERROR."""
    from gitlab_issue_sync.exit_codes import EXIT_GENERAL_ERROR

    @handle_cli_errors
    def test_func():
        raise RuntimeError("Unexpected error")

    with pytest.raises(SystemExit) as exc_info:
        test_func()

    assert exc_info.value.code == EXIT_GENERAL_ERROR


def test_handle_cli_errors_success():
    """Test that successful execution returns normally."""
    @handle_cli_errors
    def test_func():
        return "success"

    result = test_func()
    assert result == "success"



class TestTemporaryIIDSupport:
    """Tests for temporary IID (T prefix) support in CLI commands.

    These tests verify that commands accept both numeric IIDs (e.g., 42)
    and temporary IIDs (e.g., T1) for locally created issues.
    """

    def test_show_temp_issue_success(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test showing a temporary issue works."""
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create a temp issue (simulating what 'new' command creates)
            test_issue = Issue(
                iid="T1",
                title="New Feature Request",
                state="opened",
                description="This is a locally created issue",
                labels=["feature"],
                assignees=["emma"],
                milestone=None,
                created_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                author="emma",
                web_url=None,
                confidential=False,
                comments=[],
            )
            test_issue.status = "pending"
            test_issue.save(temp_git_repo)

            # Run command with temp IID
            result = cli_runner.invoke(main, ["show", "T1"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "New Feature Request" in result.output
            assert "T1" in result.output
            assert "emma" in result.output

    def test_show_temp_issue_lowercase(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test that lowercase 't' prefix is normalized to uppercase."""
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create a temp issue
            test_issue = Issue(
                iid="T1",
                title="Test Issue",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                author="emma",
                web_url=None,
                confidential=False,
                comments=[],
            )
            test_issue.save(temp_git_repo)

            # Run command with lowercase 't'
            result = cli_runner.invoke(main, ["show", "t1"])

            # Should still find the issue
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "Test Issue" in result.output

    def test_show_temp_issue_not_found(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test showing a non-existent temp issue."""
        with in_directory(temp_git_repo):
            result = cli_runner.invoke(main, ["show", "T99"])

            assert result.exit_code == 1
            assert "Storage Error" in result.output
            assert "T99" in result.output

    def test_label_add_to_temp_issue(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test adding labels to a temporary issue."""
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create a temp issue
            test_issue = Issue(
                iid="T1",
                title="Test Issue",
                state="opened",
                description="Test",
                labels=["bug"],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                author="emma",
                web_url=None,
                confidential=False,
                comments=[],
            )
            test_issue.save(temp_git_repo)

            # Add labels to temp issue
            result = cli_runner.invoke(main, ["label", "T1", "add", "urgent,feature"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "Added:" in result.output
            assert "urgent" in result.output
            assert "feature" in result.output

            # Verify labels were added
            updated_issue = Issue.load("T1", temp_git_repo)
            assert "bug" in updated_issue.labels
            assert "urgent" in updated_issue.labels
            assert "feature" in updated_issue.labels

    def test_comment_on_temp_issue(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test adding a comment to a temporary issue."""
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create a temp issue
            test_issue = Issue(
                iid="T1",
                title="Test Issue",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                author="emma",
                web_url=None,
                confidential=False,
                comments=[],
            )
            test_issue.save(temp_git_repo)

            # Add comment
            result = cli_runner.invoke(main, ["comment", "T1", "This is a progress update"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "Comment added" in result.output

            # Verify comment was added
            updated_issue = Issue.load("T1", temp_git_repo)
            assert len(updated_issue.comments) == 1
            assert "This is a progress update" in updated_issue.comments[0].body

    def test_board_move_temp_issue(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test moving a temporary issue on kanban board."""
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create a temp issue
            test_issue = Issue(
                iid="T1",
                title="Test Issue",
                state="opened",
                description="Test",
                labels=[],  # No kanban column
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                author="emma",
                web_url=None,
                confidential=False,
                comments=[],
            )
            test_issue.save(temp_git_repo)

            # Move to ToDo column
            result = cli_runner.invoke(main, ["board", "move", "T1", "ToDo"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"

            # Verify issue was moved
            updated_issue = Issue.load("T1", temp_git_repo)
            assert "ToDo" in updated_issue.labels

    def test_close_temp_issue(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test closing a temporary issue."""
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create a temp issue
            test_issue = Issue(
                iid="T1",
                title="Test Issue",
                state="opened",
                description="Test",
                labels=["ToDo"],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                author="emma",
                web_url=None,
                confidential=False,
                comments=[],
            )
            test_issue.save(temp_git_repo)

            # Close the issue
            result = cli_runner.invoke(main, ["close", "T1"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"

            # Verify issue was closed
            updated_issue = Issue.load("T1", temp_git_repo)
            assert updated_issue.state == "closed"
            # Kanban labels should be removed
            assert "ToDo" not in updated_issue.labels

    def test_milestone_set_on_temp_issue(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test setting milestone on a temporary issue."""
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue, Milestone

        with in_directory(temp_git_repo):
            # Create a milestone
            milestone = Milestone(
                title="Sprint 1",
                state="active",
                description="First sprint",
            )
            milestone.status = "synced"
            milestone.save(temp_git_repo)

            # Create a temp issue
            test_issue = Issue(
                iid="T1",
                title="Test Issue",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC),
                author="emma",
                web_url=None,
                confidential=False,
                comments=[],
            )
            test_issue.save(temp_git_repo)

            # Set milestone
            result = cli_runner.invoke(main, ["milestone", "T1", "set", "Sprint 1"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"

            # Verify milestone was set
            updated_issue = Issue.load("T1", temp_git_repo)
            assert updated_issue.milestone == "Sprint 1"

    def test_invalid_iid_format(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test that invalid IID format gives appropriate error."""
        with in_directory(temp_git_repo):
            # Try invalid format
            result = cli_runner.invoke(main, ["show", "invalid"])

            assert result.exit_code != 0
            assert "not a valid issue IID" in result.output

    def test_iid_param_type_conversion(self):
        """Test IIDParamType converts values correctly."""
        from gitlab_issue_sync.cli import IIDParamType

        iid_type = IIDParamType()

        # Numeric string -> int
        assert iid_type.convert("42", None, None) == 42

        # T-prefix -> normalized uppercase
        assert iid_type.convert("T1", None, None) == "T1"
        assert iid_type.convert("t1", None, None) == "T1"
        assert iid_type.convert("T99", None, None) == "T99"

        # Already int -> passthrough
        assert iid_type.convert(42, None, None) == 42

    def test_format_iid_helper(self):
        """Test _format_iid helper function."""
        from gitlab_issue_sync.cli import _format_iid

        # Numeric -> "#N"
        assert _format_iid(42) == "#42"
        assert _format_iid(1) == "#1"

        # Temp IID -> stays as-is
        assert _format_iid("T1") == "T1"
        assert _format_iid("T99") == "T99"

    def test_try_parse_iid_helper(self):
        """Test _try_parse_iid helper function."""
        from gitlab_issue_sync.cli import _try_parse_iid

        # Numeric string -> int
        assert _try_parse_iid("42") == 42

        # T-prefix -> normalized uppercase
        assert _try_parse_iid("T1") == "T1"
        assert _try_parse_iid("t1") == "T1"

        # Non-IID string -> None
        assert _try_parse_iid("list") is None
        assert _try_parse_iid("create") is None
