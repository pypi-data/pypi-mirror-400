"""Tests for GitLab client management utilities.

This test module validates GitLab client creation and project access by:
1. Only mocking at the python-gitlab library boundary
2. Testing error handling and authentication flows
"""

from unittest.mock import Mock, patch

import pytest

from gitlab_issue_sync.issue_sync import (
    AuthenticationError,
    SyncError,
    get_gitlab_client,
    get_project,
)


class TestGitLabClient:
    """Tests for GitLab client initialization."""

    @patch("gitlab_issue_sync.issue_sync.gitlab.Gitlab")
    def test_get_gitlab_client_success(self, mock_gitlab_class, project_config):
        """Test successful GitLab client creation."""
        mock_client = Mock()
        mock_gitlab_class.return_value = mock_client

        client = get_gitlab_client(project_config)

        mock_gitlab_class.assert_called_once_with(
            "https://gitlab.example.com",
            private_token="glpat-test-token",
        )
        mock_client.auth.assert_called_once()
        assert client == mock_client

    @patch("gitlab_issue_sync.issue_sync.gitlab.Gitlab")
    def test_get_gitlab_client_auth_failure(self, mock_gitlab_class, project_config):
        """Test GitLab client authentication failure."""
        mock_client = Mock()
        mock_client.auth.side_effect = Exception("Authentication failed")
        mock_gitlab_class.return_value = mock_client

        with pytest.raises(AuthenticationError, match="GitLab authentication failed"):
            get_gitlab_client(project_config)

    @patch("gitlab_issue_sync.issue_sync.gitlab.Gitlab")
    def test_get_project_success(self, mock_gitlab_class, project_config):
        """Test successful project retrieval."""
        mock_client = Mock()
        mock_project = Mock()
        mock_client.projects.get.return_value = mock_project

        project = get_project(mock_client, project_config)

        mock_client.projects.get.assert_called_once_with("testuser/testrepo")
        assert project == mock_project

    @patch("gitlab_issue_sync.issue_sync.gitlab.Gitlab")
    def test_get_project_not_found(self, mock_gitlab_class, project_config):
        """Test project not found."""
        mock_client = Mock()
        mock_client.projects.get.side_effect = Exception("Project not found")

        with pytest.raises(SyncError, match="Failed to access project"):
            get_project(mock_client, project_config)


class TestIssueConversion:
    """Tests for gitlab_issue_to_issue converter (moved to storage/issue.py)."""

    def test_gitlab_issue_to_issue(self, mock_gitlab_issue):
        """Test converting GitLab issue to our Issue model."""
        from gitlab_issue_sync.storage.issue import gitlab_issue_to_issue

        # Customize fixture for this test
        mock_gitlab_issue.labels = ["bug", "urgent"]

        issue = gitlab_issue_to_issue(mock_gitlab_issue)

        assert issue.iid == 1
        assert issue.title == "Test Issue"
        assert issue.state == "opened"
        assert issue.description == "This is a test issue"
        assert issue.labels == ["bug", "urgent"]
        assert issue.assignees == ["testuser"]
        assert issue.milestone == "v1.0"
        assert issue.author == "testuser"
        assert issue.web_url == "https://gitlab.example.com/testuser/testrepo/-/issues/1"
        assert not issue.confidential
        assert len(issue.comments) == 1
        assert issue.comments[0].author == "reviewer"
        assert issue.comments[0].body == "Looks good!"

    def test_gitlab_issue_to_issue_minimal(self):
        """Test converting minimal GitLab issue."""
        from tests.factories import GitLabIssueFactory
        from gitlab_issue_sync.storage.issue import gitlab_issue_to_issue

        issue = GitLabIssueFactory(
            iid=2,
            title="Minimal",
            description=None,
            labels=[],
            assignees=[],
            milestone=None,
            notes_list=[],
        )

        result = gitlab_issue_to_issue(issue)

        assert result.iid == 2
        assert result.description == ""
        assert result.labels == []
        assert result.assignees == []
        assert result.milestone is None
        assert len(result.comments) == 0

    def test_gitlab_issue_to_issue_with_assignee_fallback(self):
        """Test issue with legacy assignee field instead of assignees list."""
        from tests.factories import GitLabIssueFactory
        from gitlab_issue_sync.storage.issue import gitlab_issue_to_issue

        issue = GitLabIssueFactory(
            iid=3,
            assignees=[],  # Empty assignees list
        )
        # Mock the assignee fallback
        issue.assignee = {"username": "fallback_user"}

        result = gitlab_issue_to_issue(issue)

        assert result.assignees == ["fallback_user"]

    def test_gitlab_issue_to_issue_with_links(self):
        """Test issue conversion with issue links."""
        from tests.factories import GitLabIssueFactory, GitLabIssueLinkFactory
        from gitlab_issue_sync.storage.issue import gitlab_issue_to_issue

        # Create link using factory - only specify what we care about
        link = GitLabIssueLinkFactory(
            iid=5,
            link_type="blocks",
        )

        issue = GitLabIssueFactory(
            iid=4,
            links_list=[link],
        )

        result = gitlab_issue_to_issue(issue)

        assert len(result.links) == 1
        assert result.links[0].target_issue_iid == 5
        assert result.links[0].link_type == "blocks"

    def test_gitlab_issue_to_issue_with_multiple_comments(self):
        """Test issue with multiple comments."""
        from tests.factories import GitLabIssueFactory, GitLabNoteFactory
        from gitlab_issue_sync.storage.issue import gitlab_issue_to_issue

        note1 = GitLabNoteFactory(author={"username": "user1"}, body="First comment")
        note2 = GitLabNoteFactory(author={"username": "user2"}, body="Second comment")

        issue = GitLabIssueFactory(
            iid=6,
            notes_list=[note1, note2],
        )

        result = gitlab_issue_to_issue(issue)

        assert len(result.comments) == 2
        assert result.comments[0].author == "user1"
        assert result.comments[0].body == "First comment"
        assert result.comments[1].author == "user2"
        assert result.comments[1].body == "Second comment"
