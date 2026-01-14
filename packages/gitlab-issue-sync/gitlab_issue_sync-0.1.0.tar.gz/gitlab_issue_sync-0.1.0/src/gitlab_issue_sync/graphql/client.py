"""GitLab GraphQL client with high-level work item methods."""

from collections.abc import Callable
from functools import wraps
from typing import Any

from python_graphql_client import GraphqlClient

from ..issue_sync import AuthenticationError, SyncError


def _wrap_parse_errors[T](func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that wraps parsing exceptions into SyncError."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except (KeyError, IndexError, TypeError, ValueError) as e:
            raise SyncError(f"Failed to parse GraphQL response: {e}") from e
    return wrapper


class GitLabGraphQLClient(GraphqlClient):
    """GitLab GraphQL client with high-level methods for work item operations."""

    def __init__(self, instance_url: str, token: str):
        graphql_url = f"{instance_url.rstrip('/')}/api/graphql"
        headers = {"Authorization": f"Bearer {token}"}
        super().__init__(endpoint=graphql_url, headers=headers)

    def execute(
        self, query: str, variables: dict[str, Any] | None = None, operation_name: str | None = None
    ) -> dict[str, Any]:
        try:
            result = super().execute(query=query, variables=variables, operation_name=operation_name)
        except Exception as e:
            error_msg = str(e).lower()
            if "401" in error_msg or "unauthorized" in error_msg or "authentication" in error_msg:
                raise AuthenticationError(f"GraphQL authentication failed: {e}") from e
            raise SyncError(f"GraphQL request failed: {e}") from e

        if "errors" in result and result["errors"]:
            error_messages = [err.get("message", str(err)) for err in result["errors"]]
            combined_msg = "; ".join(error_messages)

            if any("unauthorized" in msg.lower() or "permission" in msg.lower() for msg in error_messages):
                raise AuthenticationError(f"GraphQL authorization error: {combined_msg}")

            raise SyncError(f"GraphQL errors: {combined_msg}")

        return result

    @_wrap_parse_errors
    def query_work_item_hierarchy(
        self, project_path: str, iid: int
    ) -> tuple[int | None, list[int], str, dict | None]:
        """Returns (parent_iid, child_iids, global_id, work_item_type) for a work item."""
        query = """
        query($projectPath: ID!, $iid: String!) {
          project(fullPath: $projectPath) {
            workItems(iid: $iid) {
              edges {
                node {
                  id
                  iid
                  workItemType { id, name, iconName }
                  widgets {
                    ... on WorkItemWidgetHierarchy {
                      parent { iid }
                      children { nodes { iid } }
                    }
                  }
                }
              }
            }
          }
        }
        """
        variables = {"projectPath": project_path, "iid": str(iid)}
        result = self.execute(query=query, variables=variables)

        data = result.get("data", {})
        project = data.get("project")
        if not project:
            raise SyncError(f"Project not found: {project_path}")

        work_items = project.get("workItems", {}).get("edges", [])
        if not work_items:
            raise SyncError(f"Work item not found: {iid}")

        node = work_items[0]["node"]
        global_id = node["id"]
        work_item_type = node.get("workItemType")
        widgets = node.get("widgets")
        if widgets is None:
            raise SyncError(f"Malformed response: widgets missing for work item {iid}")

        hierarchy_widget = None
        for widget in widgets:
            if "parent" in widget or "children" in widget:
                hierarchy_widget = widget
                break

        if not hierarchy_widget:
            return (None, [], global_id, work_item_type)

        parent = hierarchy_widget.get("parent")
        parent_iid = int(parent["iid"]) if parent else None

        children = hierarchy_widget.get("children", {}).get("nodes", [])
        child_iids = [int(child["iid"]) for child in children]

        return (parent_iid, child_iids, global_id, work_item_type)

    @_wrap_parse_errors
    def get_work_item_global_id(self, project_path: str, iid: int) -> str:
        """Returns the global ID (gid://gitlab/WorkItem/123) for a work item."""
        query = """
        query($projectPath: ID!, $iid: String!) {
          project(fullPath: $projectPath) {
            workItems(iid: $iid) {
              edges {
                node { id, iid }
              }
            }
          }
        }
        """
        variables = {"projectPath": project_path, "iid": str(iid)}
        result = self.execute(query=query, variables=variables)

        data = result.get("data", {})
        project = data.get("project")
        if not project:
            raise SyncError(f"Project not found: {project_path}")

        work_items = project.get("workItems", {}).get("edges", [])
        if not work_items:
            raise SyncError(f"Work item not found: {iid}")

        return work_items[0]["node"]["id"]

    @_wrap_parse_errors
    def update_work_item_parent(self, child_global_id: str, parent_global_id: str | None) -> None:
        """Sets or removes the parent for a work item."""
        mutation = """
        mutation($input: WorkItemUpdateInput!) {
          workItemUpdate(input: $input) {
            workItem { id, iid }
            errors
          }
        }
        """
        variables = {
            "input": {
                "id": child_global_id,
                "hierarchyWidget": {"parentId": parent_global_id},
            }
        }
        result = self.execute(query=mutation, variables=variables)

        data = result.get("data", {})
        work_item_update = data.get("workItemUpdate", {})
        errors = work_item_update.get("errors", [])

        if errors:
            action = "remove" if parent_global_id is None else "set"
            raise SyncError(f"Failed to {action} parent: {', '.join(errors)}")

    @_wrap_parse_errors
    def create_work_item_with_parent(
        self,
        namespace_path: str,
        title: str,
        parent_global_id: str,
        work_item_type_id: str = "gid://gitlab/WorkItems::Type/5",  # Task default
        description: str | None = None,
        confidential: bool = False,
        milestone_id: str | None = None,
    ) -> dict:
        """Creates a work item as a child of another. Returns created work item data."""
        mutation = """
        mutation createWorkItem($input: WorkItemCreateInput!) {
          workItemCreate(input: $input) {
            workItem {
              id
              iid
              title
              state
              workItemType { id, name, iconName }
              widgets {
                ... on WorkItemWidgetHierarchy {
                  parent { id, iid }
                }
              }
            }
            errors
          }
        }
        """
        input_data: dict[str, Any] = {
            "title": title,
            "workItemTypeId": work_item_type_id,
            "namespacePath": namespace_path,
            "hierarchyWidget": {"parentId": parent_global_id},
            "confidential": confidential,
        }

        if description:
            input_data["descriptionWidget"] = {"description": description}

        if milestone_id:
            input_data["milestoneWidget"] = {"milestoneId": milestone_id}

        result = self.execute(query=mutation, variables={"input": input_data})

        data = result.get("data", {})
        work_item_create = data.get("workItemCreate", {})
        errors = work_item_create.get("errors", [])

        if errors:
            raise SyncError(f"Failed to create work item: {', '.join(errors)}")

        return work_item_create.get("workItem", {})

    @_wrap_parse_errors
    def convert_work_item_type(self, work_item_id: str, target_type_id: str) -> dict:
        """Converts a work item to a different type. Returns converted work item data."""
        mutation = """
        mutation workItemConvert($input: WorkItemConvertInput!) {
          workItemConvert(input: $input) {
            workItem {
              id
              iid
              workItemType { id, name, iconName }
            }
            errors
          }
        }
        """
        variables = {
            "input": {
                "id": work_item_id,
                "workItemTypeId": target_type_id,
            }
        }
        result = self.execute(query=mutation, variables=variables)

        data = result.get("data", {})
        work_item_convert = data.get("workItemConvert", {})
        errors = work_item_convert.get("errors", [])

        if errors:
            raise SyncError(f"Failed to convert work item: {', '.join(errors)}")

        return work_item_convert.get("workItem", {})

    @_wrap_parse_errors
    def get_work_item_types(self, project_path: str) -> list[dict]:
        """Returns available work item types for a project."""
        query = """
        query getWorkItemTypes($fullPath: ID!) {
          project(fullPath: $fullPath) {
            workItemTypes {
              nodes { id, name, iconName }
            }
          }
        }
        """
        result = self.execute(query=query, variables={"fullPath": project_path})

        data = result.get("data", {})
        project = data.get("project")
        if not project:
            raise SyncError(f"Project not found: {project_path}")

        return project.get("workItemTypes", {}).get("nodes", [])
