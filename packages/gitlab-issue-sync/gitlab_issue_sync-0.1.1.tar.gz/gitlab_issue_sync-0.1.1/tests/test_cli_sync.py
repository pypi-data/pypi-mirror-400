"""Tests for 'gl-issue-sync pull', 'push', and 'sync' commands."""

import pytest

from gitlab_issue_sync.cli import main
from tests.test_helpers import in_directory


class TestPullCommand:
    """Tests for 'gl-issue-sync pull' command."""

    def test_pull_success(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
        mock_gitlab_issue,
        mock_gitlab_label,
        mock_gitlab_milestone,
        mock_graphql_execute,
    ):
        """Test pull command successfully pulls issues.

        Uses real functions: find_repository_root, get_gitlab_remote_info, get_project_config,
        get_gitlab_client, get_project, Issue.pull(), Label.pull(), Milestone.pull().
        Only mocks: python-gitlab library (GitLab API responses).
        """

        with in_directory(temp_git_repo):
            # Configure mock GitLab API responses using factories
            # Factory pattern: Only specify what we care about, everything else has sane defaults!
            from tests.factories import GitLabIssueFactory, GitLabLabelFactory, GitLabMilestoneFactory

            # Create mock issues - only specify the fields we care about for this test
            issue1 = GitLabIssueFactory(
                iid=1,
                title="Issue 1",
                labels=["bug"],
            )

            issue2 = GitLabIssueFactory(
                iid=2,
                title="Issue 2",
                labels=["feature"],
            )

            # Create mock labels - only specify what matters
            label1 = GitLabLabelFactory(
                name="bug",
                color="#FF0000",
                description="Bug reports",
            )

            label2 = GitLabLabelFactory(
                name="feature",
                color="#00FF00",
                description="New features",
            )

            # Create mock milestone - only specify what matters
            milestone1 = GitLabMilestoneFactory(
                title="v1.0",
                id=1,
            )

            # Mock GitLab API calls
            mock_gitlab_project.issues.list.return_value = [issue1, issue2]
            mock_gitlab_project.labels.list.return_value = [label1, label2]
            mock_gitlab_project.milestones.list.return_value = [milestone1]

            # Run command - all internal functions run normally, including pull()!
            result = cli_runner.invoke(main, ["pull"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "Synced 2 labels" in result.output
            assert "Synced 1 milestones" in result.output
            assert "Synced 2 issues" in result.output

            # Verify GitLab API was called (not our pull methods)
            mock_gitlab_project.issues.list.assert_called()
            mock_gitlab_project.labels.list.assert_called()
            mock_gitlab_project.milestones.list.assert_called()

            # Verify files were actually created by real pull() logic
            from gitlab_issue_sync.storage import Issue, Label, Milestone
            assert Issue.load(1, temp_git_repo) is not None
            assert Issue.load(2, temp_git_repo) is not None
            assert Label.load("bug", temp_git_repo) is not None
            assert Label.load("feature", temp_git_repo) is not None
            assert Milestone.load("v1.0", temp_git_repo) is not None

    def test_pull_with_conflicts(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
        mock_graphql_execute,
    ):
        """Test pull command with conflicts.

        Uses real functions including pull(). Only mocks python-gitlab API.
        Uses factories for clean, maintainable test data.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue
        from tests.factories import GitLabIssueFactory

        with in_directory(temp_git_repo):
            # Create local issue with one title
            local_issue = Issue(
                iid=1,
                title="Local Title",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/test/repo/-/issues/1",
                confidential=False,
                comments=[],
            )
            local_issue.save(temp_git_repo)

            # Save as original with different title
            original_issue = Issue(
                iid=1,
                title="Original Title",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/test/repo/-/issues/1",
                confidential=False,
                comments=[],
            )
            Issue.backend.save_original(original_issue, temp_git_repo)

            # Mock GitLab API to return remote with yet another title (conflict!)
            # Using factory - only specify what matters for this test!
            remote_issue = GitLabIssueFactory(
                iid=1,
                title="Remote Title",  # Different from both local and original!
            )

            mock_gitlab_project.issues.list.return_value = [remote_issue]
            mock_gitlab_project.labels.list.return_value = []
            mock_gitlab_project.milestones.list.return_value = []

            # Run command - real pull() will detect conflict
            result = cli_runner.invoke(main, ["pull"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "1 issues conflict" in result.output or "conflict" in result.output.lower()

    def test_pull_not_initialized(self, cli_runner, tmp_path):
        """Test pull command fails when not initialized.

        Uses a temp directory without git repo to naturally trigger error.
        """
        from gitlab_issue_sync.exit_codes import EXIT_CONFIG_ERROR

        # Create a non-git directory
        non_git_dir = tmp_path / "not_a_git_repo"
        non_git_dir.mkdir()

        with in_directory(non_git_dir):
            result = cli_runner.invoke(main, ["pull"])

            assert result.exit_code == EXIT_CONFIG_ERROR
            assert "Git Error" in result.output

    def test_pull_with_state_filter(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
        mock_graphql_execute,
    ):
        """Test pull command with --state option.

        Uses real functions including pull(). Only mocks python-gitlab API.
        Verifies that state filter is passed to GitLab API.
        Uses factories for clean, maintainable test data.
        """
        from tests.factories import GitLabIssueFactory

        with in_directory(temp_git_repo):
            # Create a closed issue to return from API - using factory
            # Only specify what matters: iid and state
            closed_issue = GitLabIssueFactory(
                iid=1,
                state="closed",
            )

            # Mock GitLab API
            mock_gitlab_project.issues.list.return_value = [closed_issue]
            mock_gitlab_project.labels.list.return_value = []
            mock_gitlab_project.milestones.list.return_value = []

            # Run command with state filter
            result = cli_runner.invoke(main, ["pull", "--state", "closed"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"
            # Verify GitLab API was called with state parameter
            mock_gitlab_project.issues.list.assert_called()
            call_kwargs = mock_gitlab_project.issues.list.call_args[1]
            assert call_kwargs.get("state") == "closed"

            # Verify closed issue was pulled
            from gitlab_issue_sync.storage import Issue
            loaded = Issue.load(1, temp_git_repo)
            assert loaded is not None
            assert loaded.state == "closed"

    def test_pull_with_types_flag(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
        mock_graphql_execute,
    ):
        """Test pull command with --types flag refreshes work item types cache.

        Uses real functions including pull(). Only mocks python-gitlab API and GraphQL.
        Verifies that work item types are fetched and cached.
        """
        from tests.factories import GraphQLWorkItemTypesResponseFactory

        with in_directory(temp_git_repo):
            # Mock GitLab API - no issues to pull
            mock_gitlab_project.issues.list.return_value = []
            mock_gitlab_project.labels.list.return_value = []
            mock_gitlab_project.milestones.list.return_value = []

            # Configure GraphQL mock to return work item types
            mock_graphql_execute.return_value = GraphQLWorkItemTypesResponseFactory()

            # Run command with --types flag
            result = cli_runner.invoke(main, ["pull", "--types"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "Refreshing work item types cache" in result.output
            assert "Cached 3 work item types" in result.output



class TestPushCommand:
    """Tests for 'gl-issue-sync push' command."""

    def test_push_success(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
        mock_graphql_execute,
    ):
        """Test successful push operation.

        Uses real functions including push(). Only mocks python-gitlab library.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create local issue with modifications
            modified_issue = Issue(
                iid=1,
                title="Modified Title",  # Changed from original
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/test/repo/-/issues/1",
                confidential=False,
                comments=[],
            )
            modified_issue.save(temp_git_repo)

            # Save original with different title
            original_issue = Issue(
                iid=1,
                title="Original Title",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/test/repo/-/issues/1",
                confidential=False,
                comments=[],
            )
            Issue.backend.save_original(original_issue, temp_git_repo)

            # Mock GitLab API for push - using factory!
            from tests.factories import GitLabIssueFactory
            mock_gl_issue = GitLabIssueFactory(iid=1)

            # Mock get() to return the issue for updating
            mock_gitlab_project.issues.get.return_value = mock_gl_issue
            mock_gitlab_project.labels.list.return_value = []
            mock_gitlab_project.milestones.list.return_value = []

            # Run command - real push() will update the issue
            result = cli_runner.invoke(main, ["push"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "Pushing to GitLab" in result.output
            assert "Synced 1 issues (0 created, 1 updated, 0 deleted)" in result.output

            # Verify GitLab API was called to get and save the issue
            mock_gitlab_project.issues.get.assert_called_with(1)
            mock_gl_issue.save.assert_called_once()

    def test_push_with_conflicts(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
        mock_graphql_execute,
    ):
        """Test push with conflicts.

        Uses real functions including push(). Only mocks python-gitlab library.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create local issue with one title
            local_issue = Issue(
                iid=1,
                title="Local Title",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/test/repo/-/issues/1",
                confidential=False,
                comments=[],
            )
            local_issue.save(temp_git_repo)

            # Save original with different title
            original_issue = Issue(
                iid=1,
                title="Original Title",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/test/repo/-/issues/1",
                confidential=False,
                comments=[],
            )
            Issue.backend.save_original(original_issue, temp_git_repo)

            # Mock GitLab API to return remote with yet another title (conflict!)
            from tests.factories import GitLabIssueFactory
            remote_issue = GitLabIssueFactory(
                iid=1,
                title="Remote Title",  # Different title creates conflict
            )

            # Mock GitLab API
            mock_gitlab_project.issues.list.return_value = [remote_issue]
            mock_gitlab_project.issues.get.return_value = remote_issue
            mock_gitlab_project.labels.list.return_value = []
            mock_gitlab_project.milestones.list.return_value = []

            # Run command - real push() will detect conflict
            result = cli_runner.invoke(main, ["push"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "conflict" in result.output.lower()

    def test_push_no_changes(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
        mock_graphql_execute,
    ):
        """Test push when there are no local changes.

        Uses real functions including push(). Only mocks python-gitlab library.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create local issue
            issue = Issue(
                iid=1,
                title="Test",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/test/repo/-/issues/1",
                confidential=False,
                comments=[],
            )
            issue.save(temp_git_repo)

            # Save exact same issue as original (no changes)
            Issue.backend.save_original(issue, temp_git_repo)

            # Mock GitLab API (shouldn't be called since no changes)
            mock_gitlab_project.issues.list.return_value = []
            mock_gitlab_project.labels.list.return_value = []
            mock_gitlab_project.milestones.list.return_value = []

            # Run command - real push() will skip unchanged issues
            result = cli_runner.invoke(main, ["push"])

            # Assertions
            assert result.exit_code == 0
            assert "No local changes to push" in result.output

    def test_push_dry_run(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
    ):
        """Test push with --dry-run flag shows message but makes no changes.

        Uses real functions: find_repository_root, get_project_config.
        Real file I/O in temp directories.
        """

        with in_directory(temp_git_repo):
            # Run command with --dry-run flag
            result = cli_runner.invoke(main, ["push", "--dry-run"])

            # Assertions
            assert result.exit_code == 0
            assert "DRY RUN MODE" in result.output
            assert "Dry-run mode not yet implemented" in result.output



class TestSyncCommand:
    """Tests for 'gl-issue-sync sync' command."""

    def test_sync_success(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
        mock_graphql_execute,
    ):
        """Test successful sync operation (pull then push).

        Uses real functions including pull() and push(). Only mocks python-gitlab library.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue

        with in_directory(temp_git_repo):
            # Create a remote issue to pull - using factory!
            from tests.factories import GitLabIssueFactory
            remote_issue = GitLabIssueFactory(
                iid=1,
                title="Remote Issue",
            )

            # Create local modified issue to push
            local_issue = Issue(
                iid=2,
                title="Modified Local Issue",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/test/repo/-/issues/2",
                confidential=False,
                comments=[],
            )
            local_issue.save(temp_git_repo)

            # Save original with different title
            original = Issue(
                iid=2,
                title="Original Local Issue",
                state="opened",
                description="Test",
                labels=[],
                assignees=[],
                milestone=None,
                created_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
                author="testuser",
                web_url="https://gitlab.example.com/test/repo/-/issues/2",
                confidential=False,
                comments=[],
            )
            Issue.backend.save_original(original, temp_git_repo)

            # Mock GitLab API for pull
            mock_gitlab_project.issues.list.return_value = [remote_issue]
            mock_gitlab_project.labels.list.return_value = []
            mock_gitlab_project.milestones.list.return_value = []

            # Mock GitLab API for push - using factory!
            mock_gl_issue = GitLabIssueFactory(iid=2)
            mock_gitlab_project.issues.get.return_value = mock_gl_issue

            # Run command - real sync (pull + push) will run
            result = cli_runner.invoke(main, ["sync"])

            # Assertions
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "Syncing with GitLab" in result.output
            assert "Step 1: Pulling from GitLab" in result.output
            assert "Step 2: Pushing to GitLab" in result.output

            # Verify issue was pulled
            pulled = Issue.load(1, temp_git_repo)
            assert pulled is not None
            assert pulled.title == "Remote Issue"

            # Verify modified issue was pushed
            mock_gitlab_project.issues.get.assert_called_with(2)

    def test_sync_with_state_filter(
        self,
        cli_runner,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_gitlab_project,
        mock_graphql_execute,
    ):
        """Test sync with state filter passes to pull.

        Uses real functions including pull() and push(). Only mocks python-gitlab library.
        """

        with in_directory(temp_git_repo):
            # Mock GitLab API (empty responses)
            mock_gitlab_project.issues.list.return_value = []
            mock_gitlab_project.labels.list.return_value = []
            mock_gitlab_project.milestones.list.return_value = []

            # Run command with state filter
            result = cli_runner.invoke(main, ["sync", "--state", "all"])

            # Verify state parameter was passed to GitLab API
            assert result.exit_code == 0
            # The --state all should result in state=None passed to issues.list()
            # (all states are fetched when state is None)
            mock_gitlab_project.issues.list.assert_called()


    def test_sync_help(self, cli_runner):
        """Test sync command help."""
        result = cli_runner.invoke(main, ["sync", "--help"])

        assert result.exit_code == 0
        assert "Bidirectional synchronization" in result.output
        assert "--state" in result.output


