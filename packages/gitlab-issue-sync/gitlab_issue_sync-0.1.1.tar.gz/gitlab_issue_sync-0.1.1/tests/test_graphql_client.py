"""Unit tests for GitLabGraphQLClient.

These tests follow the "mock what you don't own" principle by mocking
GraphqlClient.execute (the external library) and testing our client methods'
query construction, response parsing, and error handling.
"""

from unittest.mock import patch

import pytest

from gitlab_issue_sync.graphql.client import GitLabGraphQLClient
from gitlab_issue_sync.issue_sync import AuthenticationError, SyncError


class TestGitLabGraphQLClientInit:
    """Tests for client initialization."""

    def test_init_constructs_graphql_url(self):
        """Test that __init__ constructs the correct GraphQL URL."""
        with patch("gitlab_issue_sync.graphql.client.GraphqlClient.__init__") as mock_init:
            mock_init.return_value = None
            GitLabGraphQLClient("https://gitlab.example.com", "test-token")

            mock_init.assert_called_once()
            call_kwargs = mock_init.call_args[1]
            assert call_kwargs["endpoint"] == "https://gitlab.example.com/api/graphql"
            assert call_kwargs["headers"]["Authorization"] == "Bearer test-token"

    def test_init_strips_trailing_slash(self):
        """Test that trailing slashes in instance_url are handled correctly."""
        with patch("gitlab_issue_sync.graphql.client.GraphqlClient.__init__") as mock_init:
            mock_init.return_value = None
            GitLabGraphQLClient("https://gitlab.example.com/", "test-token")

            call_kwargs = mock_init.call_args[1]
            assert call_kwargs["endpoint"] == "https://gitlab.example.com/api/graphql"


class TestGitLabGraphQLClientExecute:
    """Tests for the execute method's error handling."""

    def test_execute_raises_auth_error_on_401(self, mock_graphql_execute):
        """Test that 401 errors from parent are converted to AuthenticationError."""
        mock_graphql_execute.side_effect = Exception("HTTP 401 Unauthorized")

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(AuthenticationError, match="GraphQL authentication failed"):
            client.execute("query { test }")

    def test_execute_raises_auth_error_on_unauthorized(self, mock_graphql_execute):
        """Test that 'unauthorized' in error message triggers AuthenticationError."""
        mock_graphql_execute.side_effect = Exception("Request unauthorized by server")

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(AuthenticationError, match="GraphQL authentication failed"):
            client.execute("query { test }")

    def test_execute_raises_auth_error_on_authentication(self, mock_graphql_execute):
        """Test that 'authentication' in error message triggers AuthenticationError."""
        mock_graphql_execute.side_effect = Exception("Authentication required")

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(AuthenticationError, match="GraphQL authentication failed"):
            client.execute("query { test }")

    def test_execute_raises_sync_error_on_other_exceptions(self, mock_graphql_execute):
        """Test that other exceptions are converted to SyncError."""
        mock_graphql_execute.side_effect = Exception("Network timeout")

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="GraphQL request failed"):
            client.execute("query { test }")

    def test_execute_raises_auth_error_on_graphql_permission_error(self, mock_graphql_execute):
        """Test that GraphQL errors with 'permission' trigger AuthenticationError."""
        mock_graphql_execute.return_value = {
            "errors": [{"message": "You don't have permission to access this resource"}]
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(AuthenticationError, match="GraphQL authorization error"):
            client.execute("query { test }")

    def test_execute_raises_auth_error_on_graphql_unauthorized_error(self, mock_graphql_execute):
        """Test that GraphQL errors with 'unauthorized' trigger AuthenticationError."""
        mock_graphql_execute.return_value = {
            "errors": [{"message": "Unauthorized access to this project"}]
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(AuthenticationError, match="GraphQL authorization error"):
            client.execute("query { test }")

    def test_execute_raises_sync_error_on_other_graphql_errors(self, mock_graphql_execute):
        """Test that other GraphQL errors are converted to SyncError."""
        mock_graphql_execute.return_value = {
            "errors": [{"message": "Field 'foo' not found on type 'Query'"}]
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="GraphQL errors"):
            client.execute("query { test }")

    def test_execute_combines_multiple_error_messages(self, mock_graphql_execute):
        """Test that multiple GraphQL errors are combined in the error message."""
        mock_graphql_execute.return_value = {
            "errors": [
                {"message": "Error 1"},
                {"message": "Error 2"},
            ]
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Error 1; Error 2"):
            client.execute("query { test }")


class TestQueryWorkItemHierarchy:
    """Tests for query_work_item_hierarchy method."""

    def test_query_work_item_hierarchy_success(self, mock_graphql_execute):
        """Test successful hierarchy query with parent and children."""
        from tests.factories import GraphQLHierarchyResponseFactory

        mock_graphql_execute.return_value = GraphQLHierarchyResponseFactory(
            iid=4, parent_iid=1, child_iids=[5, 6]
        )

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        parent_iid, child_iids, global_id, work_item_type = client.query_work_item_hierarchy(
            "group/project", 4
        )

        assert parent_iid == 1
        assert child_iids == [5, 6]
        assert global_id == "gid://gitlab/WorkItem/4"
        assert work_item_type["name"] == "Issue"

    def test_query_work_item_hierarchy_no_hierarchy(self, mock_graphql_execute):
        """Test hierarchy query for item with no parent or children."""
        mock_graphql_execute.return_value = {
            "data": {
                "project": {
                    "workItems": {
                        "edges": [{
                            "node": {
                                "id": "gid://gitlab/WorkItem/1",
                                "iid": "1",
                                "workItemType": {
                                    "id": "gid://gitlab/WorkItems::Type/1",
                                    "name": "Issue",
                                    "iconName": "issue-type-issue",
                                },
                                "widgets": []  # No hierarchy widget
                            }
                        }]
                    }
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        parent_iid, child_iids, global_id, work_item_type = client.query_work_item_hierarchy(
            "group/project", 1
        )

        assert parent_iid is None
        assert child_iids == []
        assert global_id == "gid://gitlab/WorkItem/1"

    def test_query_work_item_hierarchy_project_not_found(self, mock_graphql_execute):
        """Test that project not found raises SyncError."""
        mock_graphql_execute.return_value = {
            "data": {"project": None}
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Project not found"):
            client.query_work_item_hierarchy("nonexistent/project", 1)

    def test_query_work_item_hierarchy_work_item_not_found(self, mock_graphql_execute):
        """Test that work item not found raises SyncError."""
        mock_graphql_execute.return_value = {
            "data": {
                "project": {
                    "workItems": {"edges": []}
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Work item not found"):
            client.query_work_item_hierarchy("group/project", 999)

    def test_query_work_item_hierarchy_parse_error(self, mock_graphql_execute):
        """Test that parse errors are wrapped in SyncError."""
        # Malformed response that will cause KeyError
        mock_graphql_execute.return_value = {
            "data": {
                "project": {
                    "workItems": {
                        "edges": [{
                            "node": {
                                # Missing 'id' field - will cause KeyError
                                "iid": "1",
                                "widgets": []
                            }
                        }]
                    }
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Failed to parse GraphQL response"):
            client.query_work_item_hierarchy("group/project", 1)

    def test_query_work_item_hierarchy_missing_widgets_key(self, mock_graphql_execute):
        """Test that missing 'widgets' key raises SyncError (issue #142)."""
        mock_graphql_execute.return_value = {
            "data": {
                "project": {
                    "workItems": {
                        "edges": [{
                            "node": {
                                "id": "gid://gitlab/WorkItem/1",
                                "iid": "1",
                                "workItemType": {
                                    "id": "gid://gitlab/WorkItems::Type/1",
                                    "name": "Issue",
                                    "iconName": "issue-type-issue",
                                },
                                # 'widgets' key intentionally missing - malformed response
                            }
                        }]
                    }
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Malformed response: widgets missing for work item 1"):
            client.query_work_item_hierarchy("group/project", 1)


class TestGetWorkItemGlobalId:
    """Tests for get_work_item_global_id method."""

    def test_get_work_item_global_id_success(self, mock_graphql_execute):
        """Test successful global ID retrieval."""
        mock_graphql_execute.return_value = {
            "data": {
                "project": {
                    "workItems": {
                        "edges": [{
                            "node": {"id": "gid://gitlab/WorkItem/42", "iid": "42"}
                        }]
                    }
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        global_id = client.get_work_item_global_id("group/project", 42)

        assert global_id == "gid://gitlab/WorkItem/42"

    def test_get_work_item_global_id_project_not_found(self, mock_graphql_execute):
        """Test that project not found raises SyncError."""
        mock_graphql_execute.return_value = {
            "data": {"project": None}
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Project not found"):
            client.get_work_item_global_id("nonexistent/project", 1)

    def test_get_work_item_global_id_work_item_not_found(self, mock_graphql_execute):
        """Test that work item not found raises SyncError."""
        mock_graphql_execute.return_value = {
            "data": {
                "project": {
                    "workItems": {"edges": []}
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Work item not found"):
            client.get_work_item_global_id("group/project", 999)


class TestUpdateWorkItemParent:
    """Tests for update_work_item_parent method."""

    def test_update_work_item_parent_set_parent(self, mock_graphql_execute):
        """Test setting a parent via GraphQL mutation."""
        mock_graphql_execute.return_value = {
            "data": {
                "workItemUpdate": {
                    "workItem": {"id": "gid://gitlab/WorkItem/4", "iid": "4"},
                    "errors": [],
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        client.update_work_item_parent(
            child_global_id="gid://gitlab/WorkItem/4",
            parent_global_id="gid://gitlab/WorkItem/1",
        )

        mock_graphql_execute.assert_called_once()
        call_args = mock_graphql_execute.call_args
        variables = call_args[1]["variables"]

        assert variables["input"]["id"] == "gid://gitlab/WorkItem/4"
        assert variables["input"]["hierarchyWidget"]["parentId"] == "gid://gitlab/WorkItem/1"

    def test_update_work_item_parent_remove_parent(self, mock_graphql_execute):
        """Test removing a parent via GraphQL mutation."""
        mock_graphql_execute.return_value = {
            "data": {
                "workItemUpdate": {
                    "workItem": {"id": "gid://gitlab/WorkItem/4", "iid": "4"},
                    "errors": [],
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        client.update_work_item_parent(
            child_global_id="gid://gitlab/WorkItem/4",
            parent_global_id=None,
        )

        mock_graphql_execute.assert_called_once()
        call_args = mock_graphql_execute.call_args
        variables = call_args[1]["variables"]

        assert variables["input"]["id"] == "gid://gitlab/WorkItem/4"
        assert variables["input"]["hierarchyWidget"]["parentId"] is None

    def test_update_work_item_parent_handles_errors(self, mock_graphql_execute):
        """Test error handling in GraphQL mutation."""
        mock_graphql_execute.return_value = {
            "data": {
                "workItemUpdate": {
                    "workItem": None,
                    "errors": ["Parent work item not found"],
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Parent work item not found"):
            client.update_work_item_parent(
                child_global_id="gid://gitlab/WorkItem/4",
                parent_global_id="gid://gitlab/WorkItem/999",
            )

    def test_update_work_item_parent_error_message_for_set(self, mock_graphql_execute):
        """Test error message mentions 'set' when setting parent."""
        mock_graphql_execute.return_value = {
            "data": {
                "workItemUpdate": {
                    "workItem": None,
                    "errors": ["Cannot add child"],
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Failed to set parent"):
            client.update_work_item_parent(
                child_global_id="gid://gitlab/WorkItem/4",
                parent_global_id="gid://gitlab/WorkItem/1",
            )

    def test_update_work_item_parent_error_message_for_remove(self, mock_graphql_execute):
        """Test error message mentions 'remove' when removing parent."""
        mock_graphql_execute.return_value = {
            "data": {
                "workItemUpdate": {
                    "workItem": None,
                    "errors": ["Cannot remove parent"],
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Failed to remove parent"):
            client.update_work_item_parent(
                child_global_id="gid://gitlab/WorkItem/4",
                parent_global_id=None,
            )


class TestCreateWorkItemWithParent:
    """Tests for create_work_item_with_parent method."""

    def test_create_work_item_with_parent_success(self, mock_graphql_execute):
        """Test successful work item creation with parent."""
        from tests.factories import GraphQLWorkItemCreateResponseFactory

        mock_graphql_execute.return_value = GraphQLWorkItemCreateResponseFactory(
            iid=42, title="New Task", work_item_type="Task", parent_iid=1
        )

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        result = client.create_work_item_with_parent(
            namespace_path="group/project",
            title="New Task",
            parent_global_id="gid://gitlab/WorkItem/1",
        )

        assert result["iid"] == "42"
        assert result["title"] == "New Task"
        assert result["workItemType"]["name"] == "Task"

    def test_create_work_item_with_parent_and_description(self, mock_graphql_execute):
        """Test work item creation with description."""
        mock_graphql_execute.return_value = {
            "data": {
                "workItemCreate": {
                    "workItem": {
                        "id": "gid://gitlab/WorkItem/42",
                        "iid": "42",
                        "title": "New Task",
                        "state": "OPEN",
                        "workItemType": {
                            "id": "gid://gitlab/WorkItems::Type/5",
                            "name": "Task",
                            "iconName": "issue-type-task",
                        },
                        "widgets": [],
                    },
                    "errors": [],
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        client.create_work_item_with_parent(
            namespace_path="group/project",
            title="New Task",
            parent_global_id="gid://gitlab/WorkItem/1",
            description="Task description here",
        )

        # Verify description widget was included
        call_args = mock_graphql_execute.call_args
        input_data = call_args[1]["variables"]["input"]
        assert input_data["descriptionWidget"]["description"] == "Task description here"

    def test_create_work_item_with_parent_and_milestone(self, mock_graphql_execute):
        """Test work item creation with milestone."""
        mock_graphql_execute.return_value = {
            "data": {
                "workItemCreate": {
                    "workItem": {
                        "id": "gid://gitlab/WorkItem/42",
                        "iid": "42",
                        "title": "New Task",
                        "state": "OPEN",
                        "workItemType": {
                            "id": "gid://gitlab/WorkItems::Type/5",
                            "name": "Task",
                            "iconName": "issue-type-task",
                        },
                        "widgets": [],
                    },
                    "errors": [],
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        client.create_work_item_with_parent(
            namespace_path="group/project",
            title="New Task",
            parent_global_id="gid://gitlab/WorkItem/1",
            milestone_id="gid://gitlab/Milestone/5",
        )

        # Verify milestone widget was included
        call_args = mock_graphql_execute.call_args
        input_data = call_args[1]["variables"]["input"]
        assert input_data["milestoneWidget"]["milestoneId"] == "gid://gitlab/Milestone/5"

    def test_create_work_item_with_parent_confidential(self, mock_graphql_execute):
        """Test confidential work item creation."""
        mock_graphql_execute.return_value = {
            "data": {
                "workItemCreate": {
                    "workItem": {
                        "id": "gid://gitlab/WorkItem/42",
                        "iid": "42",
                        "title": "Confidential Task",
                        "state": "OPEN",
                        "workItemType": {
                            "id": "gid://gitlab/WorkItems::Type/5",
                            "name": "Task",
                            "iconName": "issue-type-task",
                        },
                        "widgets": [],
                    },
                    "errors": [],
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        client.create_work_item_with_parent(
            namespace_path="group/project",
            title="Confidential Task",
            parent_global_id="gid://gitlab/WorkItem/1",
            confidential=True,
        )

        # Verify confidential flag was included
        call_args = mock_graphql_execute.call_args
        input_data = call_args[1]["variables"]["input"]
        assert input_data["confidential"] is True

    def test_create_work_item_with_parent_custom_type(self, mock_graphql_execute):
        """Test work item creation with custom type ID."""
        mock_graphql_execute.return_value = {
            "data": {
                "workItemCreate": {
                    "workItem": {
                        "id": "gid://gitlab/WorkItem/42",
                        "iid": "42",
                        "title": "Custom Item",
                        "state": "OPEN",
                        "workItemType": {
                            "id": "gid://gitlab/WorkItems::Type/10",
                            "name": "Custom",
                            "iconName": "issue-type-custom",
                        },
                        "widgets": [],
                    },
                    "errors": [],
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        client.create_work_item_with_parent(
            namespace_path="group/project",
            title="Custom Item",
            parent_global_id="gid://gitlab/WorkItem/1",
            work_item_type_id="gid://gitlab/WorkItems::Type/10",
        )

        # Verify custom type ID was used
        call_args = mock_graphql_execute.call_args
        input_data = call_args[1]["variables"]["input"]
        assert input_data["workItemTypeId"] == "gid://gitlab/WorkItems::Type/10"

    def test_create_work_item_with_parent_handles_errors(self, mock_graphql_execute):
        """Test error handling for work item creation."""
        mock_graphql_execute.return_value = {
            "data": {
                "workItemCreate": {
                    "workItem": None,
                    "errors": ["Parent cannot accept children"],
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Failed to create work item"):
            client.create_work_item_with_parent(
                namespace_path="group/project",
                title="New Task",
                parent_global_id="gid://gitlab/WorkItem/1",
            )


class TestConvertWorkItemType:
    """Tests for convert_work_item_type method."""

    def test_convert_work_item_type_success(self, mock_graphql_execute):
        """Test successful work item type conversion."""
        from tests.factories import GraphQLWorkItemConvertResponseFactory

        mock_graphql_execute.return_value = GraphQLWorkItemConvertResponseFactory(
            iid=42, work_item_type="Task"
        )

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        result = client.convert_work_item_type(
            work_item_id="gid://gitlab/WorkItem/42",
            target_type_id="gid://gitlab/WorkItems::Type/5",
        )

        assert result["workItemType"]["name"] == "Task"

    def test_convert_work_item_type_issue_to_task(self, mock_graphql_execute):
        """Test converting Issue to Task type."""
        from tests.factories import GraphQLWorkItemConvertResponseFactory

        mock_graphql_execute.return_value = GraphQLWorkItemConvertResponseFactory(
            iid=42, work_item_type="Task"
        )

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        client.convert_work_item_type(
            work_item_id="gid://gitlab/WorkItem/42",
            target_type_id="gid://gitlab/WorkItems::Type/5",
        )

        # Verify correct mutation was sent
        call_args = mock_graphql_execute.call_args
        input_data = call_args[1]["variables"]["input"]
        assert input_data["id"] == "gid://gitlab/WorkItem/42"
        assert input_data["workItemTypeId"] == "gid://gitlab/WorkItems::Type/5"

    def test_convert_work_item_type_handles_errors(self, mock_graphql_execute):
        """Test error handling for type conversion."""
        from tests.factories import GraphQLWorkItemConvertResponseFactory

        mock_graphql_execute.return_value = GraphQLWorkItemConvertResponseFactory(
            iid=42, errors=["Cannot convert to this type"]
        )

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Failed to convert work item"):
            client.convert_work_item_type(
                work_item_id="gid://gitlab/WorkItem/42",
                target_type_id="gid://gitlab/WorkItems::Type/7",
            )


class TestGetWorkItemTypes:
    """Tests for get_work_item_types method."""

    def test_get_work_item_types_success(self, mock_graphql_execute):
        """Test successful work item types retrieval."""
        from tests.factories import GraphQLWorkItemTypesResponseFactory

        mock_graphql_execute.return_value = GraphQLWorkItemTypesResponseFactory()

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        types = client.get_work_item_types("group/project")

        assert len(types) == 3
        assert types[0]["name"] == "Issue"
        assert types[1]["name"] == "Task"
        assert types[2]["name"] == "Epic"

    def test_get_work_item_types_project_not_found(self, mock_graphql_execute):
        """Test that project not found raises SyncError."""
        mock_graphql_execute.return_value = {
            "data": {"project": None}
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Project not found"):
            client.get_work_item_types("nonexistent/project")

    def test_get_work_item_types_empty(self, mock_graphql_execute):
        """Test handling of project with no work item types."""
        from tests.factories import GraphQLWorkItemTypesResponseFactory

        mock_graphql_execute.return_value = GraphQLWorkItemTypesResponseFactory(types=[])

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        types = client.get_work_item_types("group/project")

        assert types == []
