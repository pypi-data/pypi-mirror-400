"""Issue entity and backend."""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from ..config import get_project_config_for_repo
from ..graphql.client import GitLabGraphQLClient
from ..issue_sync import SyncError
from .base import ISSUE_STATE_CLOSED, ISSUE_STATE_OPENED, MarkdownStorageBackend, SyncResult, Storable
from .conflicts import Conflict
from .exceptions import StorageError
from .utils import get_issues_dir, parse_issue, serialize_issue

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass

# Issue state constants (re-exported for convenience)
__all__ = [
    "ISSUE_STATE_OPENED", "ISSUE_STATE_CLOSED",
    "WorkItemType", "IssueComment", "IssueLink", "Issue", "IssueBackend",
]


@dataclass
class WorkItemType:
    """Represents a GitLab work item type (Issue, Task, Epic, etc.)."""

    id: str  # e.g., "gid://gitlab/WorkItems::Type/1"
    name: str  # e.g., "Issue", "Task", "Epic"
    icon_name: str | None = None  # e.g., "issue-type-issue"


@dataclass
class IssueComment:
    """Represents a comment on an issue."""

    author: str
    created_at: datetime
    body: str


@dataclass
class IssueLink:
    """Represents a link between issues."""

    link_id: int
    target_project_id: int
    target_issue_iid: int
    link_type: str  # 'relates_to', 'blocks', 'is_blocked_by'
    created_at: datetime
    updated_at: datetime


def _push_parent_changes_if_needed(
    gl_issue,
    issue: "Issue",
    original: "Issue | None",
    repo_path: Path,
    project,
) -> "Issue":
    """
    Push parent changes via GraphQL if needed, with automatic type conversion.

    Automatic Type Conversion:
    - GitLab requires Tasks to be children, not Issues
    - When setting parent: Convert Issue→Task FIRST, then set parent
    - When removing parent: Remove parent FIRST, then convert Task→Issue

    Args:
        gl_issue: GitLab REST API issue object (already created/updated)
        issue: Local issue with desired parent_iid state
        original: Original issue state (None for new issues)
        repo_path: Path to repository root
        project: GitLab project object

    Returns:
        Issue with fresh hierarchy data from GitLab
    """
    from .work_item_types import WorkItemTypeCache

    config = get_project_config_for_repo(repo_path)
    graphql_client = GitLabGraphQLClient(config.instance_url, config.token)

    # Ensure we have global_id (for new issues or old issues during transition)
    if not issue.global_id:
        issue.global_id = graphql_client.get_work_item_global_id(config.full_path, gl_issue.iid)

    # Check if parent changed
    old_parent_iid = original.parent_iid if original else None
    new_parent_iid = issue.parent_iid

    if old_parent_iid != new_parent_iid:
        # Parent changed - do mutation with automatic type conversion
        type_cache = WorkItemTypeCache.ensure_cached(graphql_client, config.full_path, repo_path)
        current_type = issue.work_item_type.name if issue.work_item_type else "Issue"

        # Step 1: Convert to Task if setting parent (Issues cannot be children)
        if new_parent_iid is not None and current_type != "Task":
            task_type_id = type_cache.get_task_type_id()
            if task_type_id:
                logger.debug(f"Converting issue {issue.iid} from {current_type} to Task before setting parent")
                graphql_client.convert_work_item_type(issue.global_id, task_type_id)

        # Step 2: Set parent (None to remove, global_id to set)
        parent_global_id = None
        if new_parent_iid is not None:
            parent_issue = Issue.load(new_parent_iid, repo_path)
            if parent_issue and parent_issue.global_id:
                parent_global_id = parent_issue.global_id
            else:
                parent_global_id = graphql_client.get_work_item_global_id(config.full_path, new_parent_iid)
        graphql_client.update_work_item_parent(issue.global_id, parent_global_id)

        # Step 3: Convert back to Issue if removing parent
        if new_parent_iid is None and current_type == "Task":
            issue_type_id = type_cache.get_issue_type_id()
            if issue_type_id:
                logger.debug(f"Converting issue {issue.iid} from Task to Issue after removing parent")
                graphql_client.convert_work_item_type(issue.global_id, issue_type_id)

    # Fetch with hierarchy to get final state (single fetch whether parent changed or not)
    return fetch_issue_with_hierarchy(gl_issue, project, repo_path)


def fetch_issue_with_hierarchy(gl_issue, project, repo_path: Path) -> "Issue":
    """
    Fetch issue with hierarchy and global ID from GitLab (REST + GraphQL).

    This is a convenience wrapper that:
    1. Takes a REST API issue object
    2. Queries hierarchy and global ID via GraphQL (single query)
    3. Combines both into an Issue object

    Args:
        gl_issue: GitLab REST API issue object (ProjectIssue)
        project: GitLab project object (unused, kept for signature consistency)
        repo_path: Path to repository root (for config access)

    Returns:
        Issue object with hierarchy and global_id populated

    Raises:
        AuthenticationError: If GraphQL authentication fails
        SyncError: If GraphQL queries fail
    """
    # Get config and create GraphQL client
    config = get_project_config_for_repo(repo_path)
    graphql_client = GitLabGraphQLClient(config.instance_url, config.token)

    # Query hierarchy, global ID, and work item type via GraphQL (single query for efficiency)
    parent_iid, child_iids, global_id, work_item_type = graphql_client.query_work_item_hierarchy(
        config.full_path, gl_issue.iid
    )

    return gitlab_issue_to_issue(gl_issue, parent_iid, child_iids, global_id, work_item_type)


def gitlab_issue_to_issue(
    gl_issue,
    parent_iid: int | None = None,
    child_iids: list[int] | None = None,
    global_id: str | None = None,
    work_item_type_data: dict | None = None,
) -> "Issue":
    """Convert GitLab API issue to our Issue model."""
    # Parse timestamps
    created_at = datetime.fromisoformat(gl_issue.created_at.replace("Z", "+00:00"))
    updated_at = datetime.fromisoformat(gl_issue.updated_at.replace("Z", "+00:00"))

    # Extract assignee usernames
    assignees = []
    if hasattr(gl_issue, "assignees") and gl_issue.assignees:
        assignees = [a["username"] for a in gl_issue.assignees]
    elif hasattr(gl_issue, "assignee") and gl_issue.assignee:
        assignees = [gl_issue.assignee["username"]]

    # Get milestone title
    milestone = gl_issue.milestone["title"] if gl_issue.milestone else None

    # Parse comments
    comments = []
    try:
        for note in gl_issue.notes.list(all=True):
            # Skip system notes
            if note.system:
                continue

            note_created = datetime.fromisoformat(note.created_at.replace("Z", "+00:00"))
            comments.append(IssueComment(author=note.author["username"], created_at=note_created, body=note.body))
    except Exception:
        # If we can't fetch comments, continue without them
        pass

    # Parse links
    links = []
    try:
        for link in gl_issue.links.list(all=True):
            link_created = datetime.fromisoformat(link.link_created_at.replace("Z", "+00:00"))
            link_updated = datetime.fromisoformat(link.link_updated_at.replace("Z", "+00:00"))

            links.append(
                IssueLink(
                    link_id=link.issue_link_id,
                    target_project_id=link.project_id,
                    target_issue_iid=link.iid,
                    link_type=link.link_type,
                    created_at=link_created,
                    updated_at=link_updated,
                )
            )
    except Exception:
        # If we can't fetch links, continue without them
        pass

    # Convert work item type dict to dataclass
    work_item_type = None
    if work_item_type_data:
        work_item_type = WorkItemType(
            id=work_item_type_data["id"],
            name=work_item_type_data["name"],
            icon_name=work_item_type_data.get("iconName"),
        )

    return Issue(
        iid=gl_issue.iid,
        title=gl_issue.title,
        state=gl_issue.state,
        description=gl_issue.description or "",
        labels=gl_issue.labels,
        assignees=assignees,
        milestone=milestone,
        created_at=created_at,
        updated_at=updated_at,
        author=gl_issue.author["username"],
        web_url=gl_issue.web_url,
        confidential=gl_issue.confidential,
        global_id=global_id,
        comments=comments,
        links=links,
        parent_iid=parent_iid,
        child_iids=child_iids or [],
        work_item_type=work_item_type,
    )


class IssueBackend(MarkdownStorageBackend["Issue"]):
    """
    Storage backend for GitLab issues.

    Handles:
    - Local markdown file storage with YAML frontmatter
    - GitLab API operations (fetch, create, update)
    - Three-way sync via parent class
    """

    # Configure directory structure for issues
    base_dir = ".issues"
    use_state_dirs = True  # Issues are organized into opened/closed subdirectories
    originals_subpath = ".sync/originals"

    def _read_one(self, file_path: Path) -> "Issue":
        """Parse issue from markdown file."""
        content = file_path.read_text(encoding='utf-8')
        return parse_issue(content)

    def _write_one(self, issue: "Issue", file_path: Path) -> None:
        """Serialize issue to markdown file."""
        content = serialize_issue(issue)
        file_path.write_text(content, encoding='utf-8')

    def _try_auto_resolve(
        self,
        local: "Issue",
        original: "Issue",
        remote: "Issue",
        repo_path: Path,
    ) -> "Issue | None":
        """Try automatic conflict resolution using Conflict.attempt_auto_resolution()."""
        # Compute conflicting fields
        field_diff = Issue.compute_field_diff(original, local, remote)
        conflicting_fields = [f for f in field_diff.keys() if not f.startswith("comment_")]

        # Create conflict and try auto-resolution
        conflict = Conflict(
            issue_iid=local.iid,
            fields=conflicting_fields,
        )
        return conflict.attempt_auto_resolution(repo_path, remote=remote)

    def _record_conflict(
        self,
        entity_id: int | str,
        conflicting_fields: list[str],
        remote: "Issue",
        repo_path: Path,
    ) -> None:
        """Record conflict and cache remote for manual resolution."""
        conflict = Conflict(
            issue_iid=entity_id,
            fields=conflicting_fields,
        )
        conflict.save_with_remote(remote, repo_path)

    def fetch_from_gitlab(self, project, repo_path: Path, state: str | None = None) -> list["Issue"]:
        """
        Fetch issues from GitLab with hierarchy information.

        Args:
            project: GitLab project object
            repo_path: Path to repository root
            state: Filter by state ("opened", "closed", or None for all)

        Returns:
            List of Issue objects with status="synced", remote_id set, and hierarchy populated

        Raises:
            AuthenticationError: If GraphQL authentication fails
            SyncError: If GraphQL queries fail
        """
        # Determine which states to fetch
        if state:
            states_to_fetch = [state]
        else:
            states_to_fetch = [ISSUE_STATE_OPENED, ISSUE_STATE_CLOSED]

        all_issues = []
        for fetch_state in states_to_fetch:
            gl_issues = project.issues.list(state=fetch_state, all=True)
            for gl_issue in gl_issues:
                # Fetch issue with hierarchy (REST + GraphQL)
                issue = fetch_issue_with_hierarchy(gl_issue, project, repo_path)
                # Mark as synced from GitLab
                issue.status = "synced"
                issue.remote_id = gl_issue.id
                all_issues.append(issue)

        return all_issues

    def create_on_gitlab(self, issue: "Issue", project) -> int:
        """
        Create a new issue on GitLab.

        Args:
            issue: Issue to create
            project: GitLab project object

        Returns:
            Remote ID of created issue
        """
        # Note: repo_path not available in this context, milestone resolution skipped
        params = issue.to_gitlab_params(repo_path=None)
        gl_issue = project.issues.create(params)
        return gl_issue.id

    def update_on_gitlab(self, issue: "Issue", project) -> None:
        """
        Update an existing issue on GitLab.

        Args:
            issue: Issue with changes to push
            project: GitLab project object
        """
        # Get the GitLab issue
        gl_issue = project.issues.get(issue.iid)

        # Update fields
        # Note: repo_path not available in this context, milestone resolution skipped
        params = issue.to_gitlab_params(repo_path=None)
        gl_issue.title = params["title"]
        gl_issue.description = params["description"]
        gl_issue.labels = issue.labels

        if "state_event" in params:
            gl_issue.state_event = params["state_event"]

        gl_issue.save()

        # Handle comments (only push new ones)
        # This requires comparing with original to find new comments
        # For now, we'll rely on the original being passed separately

    def delete_on_gitlab(self, issue: "Issue", project) -> None:
        """
        Issues are not deleted, only closed.

        This is a no-op for issues.
        """
        pass

    def _refetch_issues_from_gitlab(
        self,
        iids_to_refetch: set[int],
        project,
        repo_path: Path,
    ) -> None:
        """
        Batch fetch issues from GitLab and update local copies + originals.

        Uses project.issues.list(iids=[...]) for efficient batch REST fetching
        instead of individual project.issues.get(iid) calls.

        Note: GraphQL hierarchy queries still need individual calls per issue
        since GitLab's GraphQL API doesn't support batch work item queries by IID.
        Future optimization could use GraphQL query batching (aliased queries).

        Args:
            iids_to_refetch: Set of issue IIDs to refresh from GitLab
            project: GitLab project object
            repo_path: Path to repository root

        See: https://python-gitlab.readthedocs.io/en/stable/gl_objects/issues.html
        """
        if not iids_to_refetch:
            return

        # Batch fetch all issues in single REST API call using iids filter
        try:
            gl_issues = project.issues.list(iids=list(iids_to_refetch), get_all=True)
        except Exception as e:
            logger.warning(f"Failed to batch fetch issues {iids_to_refetch}: {e}")
            return

        for gl_issue in gl_issues:
            try:
                # Fetch hierarchy via GraphQL (still individual calls)
                issue = fetch_issue_with_hierarchy(gl_issue, project, repo_path)

                # Update local copy (preserve user edits to writable fields)
                local = self.load(gl_issue.iid, repo_path)
                if local:
                    # Update only read-only fields from remote
                    for read_only_field in Issue._read_only_fields:
                        setattr(local, read_only_field, getattr(issue, read_only_field))
                    self.save(local, repo_path)
                else:
                    # No local copy - save entire fetched issue
                    self.save(issue, repo_path)

                # Always save fresh original snapshot to prevent false conflicts
                self.save_original(issue, repo_path)

            except SyncError as e:
                # Log warning but continue with other issues
                logger.warning(f"Failed to process issue {gl_issue.iid}: {e}")
            except Exception as e:
                # Re-raise unexpected errors (don't silently swallow per CLAUDE.md)
                raise SyncError(f"Unexpected error processing issue {gl_issue.iid}: {e}") from e

    def _execute_rest_operation(
        self,
        operation: str,
        issue: "Issue",
        remote: "Issue | None",
        project,
        repo_path: Path,
    ):
        """
        Execute REST operation using method dispatch.

        Args:
            operation: "create" or "update"
            issue: Issue to operate on
            remote: Remote issue state (None for create, used as baseline for comments/links)
            project: GitLab project object
            repo_path: Repository path

        Returns:
            For "create": Created GitLab issue object
            For "update": Updated GitLab issue object
        """
        params = issue.to_gitlab_params(repo_path)

        if operation == "create":
            return project.issues.create(params)

        elif operation == "update":
            gl_issue = project.issues.get(issue.iid)
            gl_issue.title = params["title"]
            gl_issue.description = params["description"]
            gl_issue.labels = issue.labels

            if "milestone_id" in params:
                gl_issue.milestone_id = params["milestone_id"]

            if "state_event" in params:
                gl_issue.state_event = params["state_event"]

            gl_issue.save()

            # Push new comments (REST) - remote is source of truth
            if remote:
                remote_comment_count = len(remote.comments)
                new_comments = issue.comments[remote_comment_count:]
                for comment in new_comments:
                    gl_issue.notes.create({"body": comment.body})

            # Push link changes (REST) - remote is source of truth
            local_link_iids = {link.target_issue_iid for link in issue.links}
            remote_link_iids = {link.target_issue_iid for link in remote.links} if remote else set()
            added_link_iids = local_link_iids - remote_link_iids
            removed_link_iids = remote_link_iids - local_link_iids

            # Create new links
            for link in issue.links:
                if link.target_issue_iid in added_link_iids or link.link_id == 0:
                    link_params = {
                        "target_project_id": project.id,
                        "target_issue_iid": link.target_issue_iid,
                        "link_type": link.link_type,
                    }
                    gl_issue.links.create(link_params)

            # Delete removed links
            if remote:
                for link in remote.links:
                    if link.target_issue_iid in removed_link_iids:
                        existing_links = gl_issue.links.list(get_all=True)
                        for existing_link in existing_links:
                            if existing_link.iid == link.target_issue_iid:
                                gl_issue.links.delete(existing_link.issue_link_id)
                                break

            return gl_issue

        else:
            raise ValueError(f"Unknown REST operation: {operation}")

    def _rest_fields_changed(self, issue: "Issue", original: "Issue | None") -> bool:
        """Check if REST-managed fields have changed."""
        if not original:
            return True  # New issue - all fields need to be pushed
        local_rest_hash = issue.compute_content_hash(exclude=("parent_iid",))
        original_rest_hash = original.compute_content_hash(exclude=("parent_iid",))
        return local_rest_hash != original_rest_hash

    def _graphql_fields_changed(self, issue: "Issue", original: "Issue | None") -> bool:
        """Check if GraphQL-managed fields (parent_iid) have changed."""
        if not original:
            return issue.parent_iid is not None  # New issue with parent
        local_graphql_hash = issue.compute_content_hash(only=("parent_iid",))
        original_graphql_hash = original.compute_content_hash(only=("parent_iid",))
        return local_graphql_hash != original_graphql_hash

    def _collect_iids_to_refetch(
        self,
        updated_issue: "Issue",
        local_issue: "Issue",
        original: "Issue | None",
        iids_to_refetch: set[int],
    ) -> None:
        """Collect all IIDs that need to be re-fetched after a push operation.

        Only collects IIDs that changed (added or removed), not unchanged ones.
        Example: original links [1,2,3], local links [2,3,5] → refetch {1,5}

        Args:
            updated_issue: Issue fetched from GitLab after push
            local_issue: The local issue we pushed (may have links not yet on remote)
            original: Original issue before local changes (for detecting removed items)
            iids_to_refetch: Set to accumulate IIDs needing re-fetch
        """
        # Add the issue itself (to get updated timestamps, etc.)
        if isinstance(updated_issue.iid, int):
            iids_to_refetch.add(updated_issue.iid)

        # Add only CHANGED linked issues (symmetric difference)
        # Added links need refetch to get their new reverse link
        # Removed links need refetch to remove their reverse link
        original_link_iids = {link.target_issue_iid for link in original.links} if original else set()
        local_link_iids = {link.target_issue_iid for link in local_issue.links}
        changed_link_iids = original_link_iids.symmetric_difference(local_link_iids)
        iids_to_refetch.update(changed_link_iids)

        # Add parent issues (current and old parent if changed)
        if updated_issue.parent_iid:
            iids_to_refetch.add(updated_issue.parent_iid)
        if original and original.parent_iid and original.parent_iid != updated_issue.parent_iid:
            iids_to_refetch.add(original.parent_iid)

    def _push_single_issue(
        self,
        issue: "Issue",
        project,
        repo_path: Path,
        iids_to_refetch: set[int],
        remote_issues_cache: list["Issue"] | None,
        result: SyncResult,
    ) -> tuple[list["Issue"] | None, bool]:
        """
        Push a single issue using unified flow.

        Flow (same for create and update):
        1. Determine operation type ("create" or "update")
        2. Load original snapshot (None for temporary issues)
        3. Check for conflicts (skip for temporary issues)
        4. Check if REST/GraphQL fields changed
        5. Execute REST operation if needed (via method dispatch)
        6. Execute GraphQL parent update if needed
        7. Collect IIDs to refetch

        Args:
            issue: Issue to push
            project: GitLab project
            repo_path: Repository path
            iids_to_refetch: Set to add IIDs that need re-fetching
            remote_issues_cache: Cached remote issues (for conflict detection)
            result: SyncResult to update

        Returns:
            Tuple of (updated remote_issues_cache, was_pushed)
        """
        # Determine operation type
        operation = "create" if issue.is_temporary else "update"
        original = None if issue.is_temporary else self.load_original(issue.iid, repo_path)
        remote = None  # Will be set during conflict detection if available
        auto_resolved_fields: list[str] | None = None  # Track fields that were auto-resolved

        # Skip issues with existing unresolved conflicts
        if operation == "update" and isinstance(issue.iid, int) and Conflict.has(issue.iid, repo_path):
            result.conflicts.append(issue.iid)
            result.conflict_details[issue.iid] = "Unresolved conflict - run 'conflicts resolve' first"
            return remote_issues_cache, False

        # Conflict detection (existing issues only)
        if operation == "update" and original:
            local_hash = issue.compute_content_hash()
            original_hash = original.compute_content_hash()

            if local_hash == original_hash:
                # No local changes, skip
                return remote_issues_cache, False

            # Lazy load remote issues for conflict detection
            if remote_issues_cache is None:
                remote_issues_cache = self.fetch_from_gitlab(project, repo_path)

            remote = next((i for i in remote_issues_cache if i.iid == issue.iid), None)
            if remote:
                remote_hash = remote.compute_content_hash()
                if remote_hash != original_hash:
                    # Both local and remote modified - BOTH_MODIFIED conflict!
                    field_diff = Issue.compute_field_diff(original, issue, remote)
                    # Filter out synthetic fields (comment_X_timestamp) used for display only
                    conflicting_fields = [
                        f for f in field_diff.keys() if not f.startswith("comment_")
                    ]

                    # Create conflict and try auto-resolution
                    conflict = Conflict(
                        issue_iid=issue.iid,
                        fields=conflicting_fields,
                    )
                    merged = conflict.attempt_auto_resolution(repo_path, remote=remote)

                    if merged:
                        # Auto-resolved! Use merged version and remote as new baseline
                        issue = merged
                        original = remote  # Remote becomes new baseline for REST/GraphQL change detection
                        auto_resolved_fields = conflicting_fields
                    else:
                        # Manual resolution required - save conflict and cache remote
                        conflict.save_with_remote(remote, repo_path)
                        result.conflicts.append(issue.iid)
                        result.conflict_details[issue.iid] = json.dumps(field_diff)
                        return remote_issues_cache, False

        # Check what changed
        rest_changed = self._rest_fields_changed(issue, original)
        graphql_changed = self._graphql_fields_changed(issue, original)

        if not rest_changed and not graphql_changed:
            return remote_issues_cache, False

        # Execute REST operation if needed
        gl_issue = None
        temp_file_path = None  # Track temp file for cleanup after successful creation

        if rest_changed:
            gl_issue = self._execute_rest_operation(operation, issue, remote, project, repo_path)

            # CRITICAL: For new issues, rename file immediately after successful REST creation
            # This prevents duplicates if subsequent operations (like setting parent) fail
            if operation == "create":
                # Save temp file path before it's gone
                temp_file_path = get_issues_dir(repo_path) / ISSUE_STATE_OPENED / f"{issue.iid}.md"

                # Fetch issue with real IID from GitLab (single REST fetch)
                # Preserve parent_iid from original issue (not in REST response)
                created_issue = gitlab_issue_to_issue(gl_issue, parent_iid=issue.parent_iid)

                # Save with real IID and update original snapshot
                self.save(created_issue, repo_path)
                self.save_original(created_issue, repo_path)

                # Clean up temporary file
                if temp_file_path.exists():
                    temp_file_path.unlink()

                # Update issue object for subsequent operations
                issue = created_issue
                result.created.append(issue.iid)

        elif operation == "update":
            # Need gl_issue for GraphQL operations even if REST unchanged
            gl_issue = project.issues.get(issue.iid)

        # Execute GraphQL parent changes if needed
        if gl_issue:
            updated_issue = _push_parent_changes_if_needed(gl_issue, issue, original, repo_path, project)

            # Save locally and update original
            self.save(updated_issue, repo_path)
            self.save_original(updated_issue, repo_path)

            # Update result tracking (only for updates, creates already tracked above)
            if operation != "create":
                result.updated.append(issue.iid)
                if auto_resolved_fields:
                    result.auto_resolve_details[issue.iid] = ", ".join(auto_resolved_fields)
                # Clear any conflict state after successful push
                if isinstance(issue.iid, int):
                    Conflict.clear(issue.iid, repo_path)

            # Collect IIDs for batch re-fetch (using both updated and local issues)
            self._collect_iids_to_refetch(updated_issue, issue, original, iids_to_refetch)

        return remote_issues_cache, True

    def push(self, entity_class: type["Issue"], project, repo_path: Path) -> SyncResult:
        """
        Push local issues to GitLab using unified flow.

        This method:
        1. Iterates through all local issues
        2. Uses a single code path for both create and update operations
        3. Collects all IIDs that need re-fetching
        4. Batch re-fetches related issues at the end

        The unified flow ensures:
        - REST calls are skipped when only GraphQL fields changed
        - All affected issues (parent, children, linked) are refreshed
        - Original snapshots are updated to prevent false conflicts
        """
        local_issues = self.load_all(repo_path)
        result = SyncResult()
        remote_issues_cache = None  # Lazy loaded for conflict detection
        iids_to_refetch: set[int] = set()  # Centralized re-fetch list

        for issue in local_issues:
            was_temporary = issue.is_temporary
            original_iid = issue.iid
            created_count_before = len(result.created)
            try:
                remote_issues_cache, was_pushed = self._push_single_issue(
                    issue=issue,
                    project=project,
                    repo_path=repo_path,
                    iids_to_refetch=iids_to_refetch,
                    remote_issues_cache=remote_issues_cache,
                    result=result,
                )
            except Exception as e:
                # Check if issue was created (new entry in result.created)
                created_count_after = len(result.created)
                if was_temporary and created_count_after > created_count_before:
                    # Issue was created successfully (appears in result.created)
                    real_iid = result.created[-1]  # The most recently added IID
                    result.conflicts.append(real_iid)
                    result.conflict_details[real_iid] = (
                        f"Issue created as #{real_iid} but failed post-creation operations: {e}"
                    )
                else:
                    # Complete failure - use original IID
                    result.conflicts.append(original_iid)
                    error_type = "create" if was_temporary else "update"
                    result.conflict_details[original_iid] = f"Failed to {error_type} issue on GitLab: {e}"

        # Single batch re-fetch after all mutations
        # This is more efficient than re-fetching after each push
        self._refetch_issues_from_gitlab(iids_to_refetch, project, repo_path)

        return result


@dataclass
class Issue(Storable):
    """Represents a GitLab issue with local-first sync."""

    iid: int | str  # Can be int for real issues or str for temporary (T1, T2, etc.)
    title: str
    state: str  # "opened" or "closed"
    description: str
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    milestone: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    author: str | None = None
    web_url: str | None = None
    confidential: bool = False
    global_id: str | None = None  # GraphQL global ID (e.g., "gid://gitlab/WorkItem/123") - read-only, for mutations
    comments: list[IssueComment] = field(default_factory=list)
    links: list[IssueLink] = field(default_factory=list)
    parent_iid: int | None = None  # Work item hierarchy: parent issue IID (writable via GraphQL)
    child_iids: list[int] = field(default_factory=list)  # Work item hierarchy: child IIDs (read-only)
    work_item_type: WorkItemType | None = None  # Work item type (Issue, Task, Epic) - read-only

    # Read-only fields that should always be updated from remote during sync,
    # even when NO_CHANGE is detected (i.e., even when hash hasn't changed).
    # These fields are:
    # - Managed/computed by GitLab (not writable by users)
    # - Never pushed to GitLab (read-only)
    # - Should be kept in sync with remote to reflect current state
    _read_only_fields: ClassVar[set[str]] = {"child_iids", "updated_at", "global_id", "work_item_type"}

    # Path constants for issue storage (relative to repo_path)
    BASE_ISSUE_PATH: ClassVar[str] = ".issues"
    SYNC_PATH: ClassVar[str] = f"{BASE_ISSUE_PATH}/.sync"
    ORIGINALS_PATH: ClassVar[str] = f"{SYNC_PATH}/originals"
    CONFLICTS_PATH: ClassVar[str] = f"{SYNC_PATH}/conflicts"

    def get_identifier(self) -> int | str:
        """Get unique identifier for this issue (the IID)."""
        return self.iid

    def get_file_path(self, repo_path: Path) -> Path:
        """Get the file path for this issue based on its state."""
        return repo_path / self.BASE_ISSUE_PATH / self.state / f"{self.iid}.md"

    @classmethod
    def get_original_path(cls, iid: int | str, repo_path: Path) -> Path:
        """Get the original snapshot path for an issue."""
        return repo_path / cls.ORIGINALS_PATH / f"{iid}.md"

    @classmethod
    def get_remote_cache_path(cls, iid: int | str, repo_path: Path) -> Path:
        """Get the remote cache path for a conflicted issue."""
        return repo_path / cls.CONFLICTS_PATH / f"{iid}_remote.md"

    def compute_content_hash(
        self,
        exclude: tuple[str, ...] = (),
        only: tuple[str, ...] = (),
    ) -> str:
        """
        Compute hash of issue content for change detection.

        Args:
            exclude: Field names to exclude from hash computation
            only: If provided, only include these field names in hash
                  (mutually exclusive with exclude)

        Excludes sync metadata (status, remote_id) and volatile fields (updated_at).
        Note: child_iids is always excluded (read-only, derived from GraphQL).

        Examples:
            compute_content_hash()  # All fields (for conflict detection)
            compute_content_hash(exclude=('parent_iid',))  # REST-only fields
            compute_content_hash(only=('parent_iid',))  # GraphQL-only fields
        """
        if exclude and only:
            raise ValueError("Cannot specify both 'exclude' and 'only' parameters")

        # Build content dict with all meaningful fields
        content = {
            "iid": self.iid,
            "title": self.title,
            "state": self.state,
            "description": self.description,
            "labels": sorted(self.labels),  # Sort for consistent hashing
            "assignees": sorted(self.assignees),
            "milestone": self.milestone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "author": self.author,
            "web_url": self.web_url,
            "confidential": self.confidential,
            # Include comments
            "comments": [
                {"author": c.author, "created_at": c.created_at.isoformat(), "body": c.body} for c in self.comments
            ],
            # Include links
            "links": [
                {
                    "link_id": link.link_id,
                    "target_project_id": link.target_project_id,
                    "target_issue_iid": link.target_issue_iid,
                    "link_type": link.link_type,
                }
                for link in self.links
            ],
            # Include parent_iid (but not child_iids - that's read-only)
            "parent_iid": self.parent_iid,
        }

        # Apply filtering
        if only:
            content = {k: v for k, v in content.items() if k in only}
        elif exclude:
            content = {k: v for k, v in content.items() if k not in exclude}

        # Convert to JSON string and hash
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    @staticmethod
    def compute_field_diff(original: "Issue", local: "Issue", remote: "Issue") -> dict[str, dict[str, any]]:
        """
        Compute field-by-field differences between three versions of an issue.

        Returns a dict mapping field names to dicts with 'original', 'local', 'remote' values
        for fields that differ across versions.

        Args:
            original: Original synced version
            local: Local modified version
            remote: Remote modified version

        Returns:
            Dict of {field_name: {'original': val, 'local': val, 'remote': val}}
            Only includes fields that differ.
        """
        diff = {}

        # Simple fields to compare
        # NOTE: updated_at is excluded because it's GitLab-managed and changes on every update
        # Including it would show confusing timestamp diffs that aren't actual conflicts
        simple_fields = ["title", "state", "description", "milestone", "confidential", "created_at"]

        for field in simple_fields:
            orig_val = getattr(original, field, None)
            local_val = getattr(local, field, None)
            remote_val = getattr(remote, field, None)

            # Compare - handle datetime specially
            if isinstance(orig_val, datetime) or isinstance(local_val, datetime) or isinstance(remote_val, datetime):
                # Convert to ISO strings for comparison
                orig_str = orig_val.isoformat() if orig_val else None
                local_str = local_val.isoformat() if local_val else None
                remote_str = remote_val.isoformat() if remote_val else None

                if not (orig_str == local_str == remote_str):
                    diff[field] = {"original": orig_str, "local": local_str, "remote": remote_str}
            else:
                if not (orig_val == local_val == remote_val):
                    diff[field] = {"original": orig_val, "local": local_val, "remote": remote_val}

        # List fields - compare as sorted sets
        list_fields = ["labels", "assignees"]
        for field in list_fields:
            orig_val = sorted(getattr(original, field, []))
            local_val = sorted(getattr(local, field, []))
            remote_val = sorted(getattr(remote, field, []))

            if not (orig_val == local_val == remote_val):
                diff[field] = {"original": orig_val, "local": local_val, "remote": remote_val}

        # Comments - compare count and content
        if len(original.comments) != len(local.comments) or len(original.comments) != len(remote.comments):
            diff["comments"] = {
                "original": len(original.comments),
                "local": len(local.comments),
                "remote": len(remote.comments),
            }

        # Check if comment timestamps differ (precision loss issue)
        for i in range(min(len(original.comments), len(local.comments), len(remote.comments))):
            orig_comment = original.comments[i]
            local_comment = local.comments[i]
            remote_comment = remote.comments[i]

            orig_ts = orig_comment.created_at.isoformat() if orig_comment.created_at else None
            local_ts = local_comment.created_at.isoformat() if local_comment.created_at else None
            remote_ts = remote_comment.created_at.isoformat() if remote_comment.created_at else None

            if not (orig_ts == local_ts == remote_ts):
                diff[f"comment_{i}_timestamp"] = {"original": orig_ts, "local": local_ts, "remote": remote_ts}

        # Links - compare count
        if len(original.links) != len(local.links) or len(original.links) != len(remote.links):
            diff["links"] = {
                "original": len(original.links),
                "local": len(local.links),
                "remote": len(remote.links),
            }

        return diff

    @property
    def is_temporary(self) -> bool:
        """Check if this is a temporary (locally created) issue."""
        return isinstance(self.iid, str) and self.iid.startswith("T")

    @property
    def filename(self) -> str:
        """Get the filename for this issue."""
        return f"{self.iid}.md"

    # ===== Instance Methods (Business Logic) =====

    def save(self, repo_path: Path | None = None) -> None:
        """
        Save this issue to local storage.

        State transition cleanup (opened ↔ closed) is handled automatically by the backend.

        Args:
            repo_path: Path to repository root
        """
        if not self.backend:
            raise StorageError("Issue backend not configured")

        # Backend.save() handles state transition cleanup automatically
        self.backend.save(self, repo_path or Path.cwd())

    def add_comment(self, body: str, author: str | None = None, repo_path: Path | None = None) -> IssueComment:
        """
        Add a comment to this issue.

        Args:
            body: Comment text
            author: Comment author (defaults to cached username from config)
            repo_path: Path to repository root

        Returns:
            The created comment

        Raises:
            StorageError: If username not cached in config (user needs to run init)
        """
        # Get author from config if not provided
        if not author:
            from ..config import get_project_config_for_repo
            config = get_project_config_for_repo(repo_path or Path.cwd())
            if not config or not config.username:
                raise StorageError(
                    "Username not cached in configuration. "
                    "Please run 'gl-issue-sync init' to initialize the repository."
                )
            author = config.username

        # Create comment
        comment = IssueComment(
            author=author,
            created_at=datetime.now(UTC),
            body=body
        )

        # Add to issue
        if self.comments is None:
            self.comments = []
        self.comments.append(comment)

        # Save issue
        self.save(repo_path)

        return comment

    def close(self, remove_kanban_labels: bool = True, repo_path: Path | None = None) -> None:
        """
        Close this issue.

        Args:
            remove_kanban_labels: If True, remove kanban column labels
            repo_path: Path to repository root
        """
        # Set state to closed
        self.state = ISSUE_STATE_CLOSED

        # Remove kanban labels if requested
        if remove_kanban_labels:
            from ..config import get_project_config_for_repo
            config = get_project_config_for_repo(repo_path or Path.cwd())
            if config and config.board and config.board.columns:
                self.labels = [label for label in self.labels if label not in config.board.columns]

        # Save issue (will handle file cleanup)
        self.save(repo_path)

    def move_to_column(
        self,
        column: str | None,
        repo_path: Path | None = None
    ) -> tuple[str | None, str | None]:
        """
        Move issue to a kanban column.

        Args:
            column: Target column name, or None to remove from all columns
            repo_path: Path to repository root

        Returns:
            Tuple of (old_column, new_column)
        """
        from ..config import get_project_config_for_repo

        config = get_project_config_for_repo(repo_path or Path.cwd())
        if not config or not config.board or not config.board.columns:
            raise StorageError("No kanban board configured")

        kanban_columns = config.board.columns

        # Find current column
        old_column = None
        for label in self.labels:
            if label in kanban_columns:
                old_column = label
                break

        # Remove old column label
        if old_column:
            self.labels = [label for label in self.labels if label != old_column]

        # Add new column label
        if column and column not in self.labels:
            self.labels.append(column)

        # Save issue
        self.save(repo_path)

        return (old_column, column)

    def move_to_board_column(
        self,
        column: str | None = None,
        direction: str | None = None,
        repo_path: Path | None = None
    ) -> tuple[str | None, str | None, dict]:
        """
        Move issue between kanban board columns with validation and state management.

        Args:
            column: Target column name or number (0 to remove, 1-N for column index)
            direction: "next" (default), "back", or None
            repo_path: Path to repository root

        Returns:
            Tuple of (old_column, new_column, state_info) where state_info contains:
                - was_closed: bool - Whether issue was closed before move
                - new_state: str | None - New state if changed ("opened" or "closed")

        Raises:
            ValueError: If column is invalid
            StorageError: If kanban board not configured
        """
        from .config import KanbanColumn

        repo_path = repo_path or Path.cwd()

        # Get column names
        column_names = KanbanColumn.get_column_names(repo_path)

        # Find current column
        current_col = next((label for label in self.labels if label in column_names), None)
        was_closed = self.state == "closed"

        # Determine target column and new state
        target_col = None
        new_state = None

        if column:
            # Explicit column provided
            if column.isdigit():
                col_num = int(column)
                if col_num == 0:
                    # Remove from all columns
                    target_col = None
                elif 1 <= col_num <= len(column_names):
                    # 1-indexed column number
                    target_col = column_names[col_num - 1]
                else:
                    # Invalid column number
                    raise ValueError(
                        f"Invalid column number: {col_num}. "
                        f"Valid range: 0 (no column) or 1-{len(column_names)}\n"
                        f"Available columns:\n" +
                        "\n".join(f"  {i}. {col}" for i, col in enumerate(column_names, 1))
                    )
            else:
                # Column name provided - validate it
                is_valid, suggestion = KanbanColumn.validate_and_suggest(column, repo_path)
                if is_valid:
                    target_col = column
                elif suggestion:
                    raise ValueError(f"Invalid column: '{column}'. Did you mean '{suggestion}'?")
                else:
                    available = "\n".join(f"  {i}. {col}" for i, col in enumerate(column_names, 1))
                    raise ValueError(
                        f"Column '{column}' not found\n"
                        f"Available columns:\n{available}"
                    )

            # Re-open issue if closed and moving to specific column
            if self.state == "closed" and target_col is not None:
                new_state = "opened"

        elif direction == "back":
            # Move backward
            target_col, new_state = KanbanColumn.get_previous(current_col, self.state, repo_path)
        else:
            # Move forward (default)
            target_col, new_state = KanbanColumn.get_next(current_col, self.state, repo_path)

        # Apply state change if needed
        if new_state:
            self.state = new_state

        # Move issue to target column
        old_col, new_col = self.move_to_column(target_col, repo_path)

        # Return state information for display
        state_info = {
            "was_closed": was_closed,
            "new_state": new_state,
        }

        return (old_col, new_col, state_info)

    def to_gitlab_params(self, repo_path: Path | None = None) -> dict:
        """
        Convert this issue to GitLab API parameters for create/update.

        Args:
            repo_path: Path to repository root (needed for milestone resolution)

        Returns:
            Dictionary of API parameters
        """
        from .milestone import Milestone

        params = {
            "title": self.title,
            "description": self.description,
            "labels": ",".join(self.labels) if self.labels else "",
        }

        if self.assignees:
            # GitLab API accepts assignee_ids, but we can also use assignee_id for the first
            # For simplicity, we'll just use the first assignee
            # Full multi-assignee support would require looking up user IDs
            params["assignee_ids"] = []  # Would need to resolve usernames to IDs

        if self.milestone:
            # Resolve milestone title to ID
            milestone_map = Milestone.get_title_to_id_map(repo_path or Path.cwd())
            if self.milestone in milestone_map:
                params["milestone_id"] = milestone_map[self.milestone]
            # If milestone not found in cache, skip it (will stay as-is on GitLab)

        # Handle state changes
        if self.state == ISSUE_STATE_CLOSED:
            params["state_event"] = "close"
        elif self.state == ISSUE_STATE_OPENED:
            params["state_event"] = "reopen"

        return params

    @classmethod
    def load(cls, iid: int | str, repo_path: Path | None = None) -> "Issue | None":
        """
        Load an issue from local storage.

        Args:
            iid: Issue IID
            repo_path: Path to repository root

        Returns:
            The loaded issue, or None if not found
        """
        if not cls.backend:
            raise StorageError("Issue backend not configured")

        return cls.backend.load(iid, repo_path or Path.cwd())

    @classmethod
    def create_new(
        cls,
        title: str,
        description: str = "",
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
        milestone: str | None = None,
        confidential: bool = False,
        parent_iid: int | None = None,
        repo_path: Path | None = None,
    ) -> "Issue":
        """
        Create a new local issue with temporary ID.

        This creates a new issue locally that will be pushed to GitLab later.
        The issue is assigned a temporary ID (T1, T2, etc.) and marked with
        status="pending" so the push command will create it on GitLab.

        Args:
            title: Issue title (required)
            description: Issue description
            labels: List of label names to apply
            assignees: List of usernames to assign
            milestone: Milestone title
            confidential: Whether issue should be confidential
            parent_iid: Parent issue IID (for work item hierarchy)
            repo_path: Path to repository root

        Returns:
            The created Issue object with temporary IID

        Raises:
            StorageError: If repository not initialized or username not cached
        """
        from ..config import get_project_config_for_repo
        from .utils import get_next_temporary_id

        repo_path = repo_path or Path.cwd()

        # Get username from config for author field
        config = get_project_config_for_repo(repo_path)
        if not config or not config.username:
            raise StorageError(
                "Username not cached in configuration. "
                "Please run 'gl-issue-sync init' to initialize the repository."
            )

        # Generate temporary ID
        temp_iid = get_next_temporary_id(repo_path)

        # Create issue object
        issue = cls(
            iid=temp_iid,
            title=title,
            state=ISSUE_STATE_OPENED,
            description=description,
            labels=labels or [],
            assignees=assignees or [],
            milestone=milestone,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            author=config.username,
            web_url=None,
            confidential=confidential,
            parent_iid=parent_iid,
            comments=[],
            links=[],
        )

        # Mark as pending for creation on next push
        issue.status = "pending"

        # Save locally
        issue.save(repo_path)

        return issue

    @classmethod
    def list_all(cls, state: str | None = None, repo_path: Path | None = None) -> list["Issue"]:
        """
        List all issues from local storage.

        Args:
            state: Filter by state ("opened", "closed", or None for all)
            repo_path: Path to repository root

        Returns:
            List of issues
        """
        if not cls.backend:
            raise StorageError("Issue backend not configured")

        repo_path = repo_path or Path.cwd()
        all_issues = cls.backend.load_all(repo_path)

        # Apply state filter if specified
        if state:
            all_issues = [issue for issue in all_issues if issue.state == state]

        return all_issues

    @classmethod
    def filter(
        cls,
        state: str | None = None,
        column: list[str] | None = None,
        labels: list[str] | None = None,
        milestones: list[str] | None = None,
        repo_path: Path | None = None,
    ) -> list["Issue"]:
        """
        Filter issues from local storage with advanced criteria.

        Args:
            state: Filter by state ("opened", "closed", or None for all)
            column: Filter by Kanban columns (OR logic - issue can be in any column)
            labels: Filter by labels (AND logic - issue must have all labels)
            milestones: Filter by milestones (OR logic - issue can have any milestone)
            repo_path: Path to repository root

        Returns:
            Filtered and sorted list of issues
        """
        from .config import KanbanColumn

        repo_path = repo_path or Path.cwd()

        # Start with all issues (optionally filtered by state)
        issues = cls.list_all(state=state, repo_path=repo_path)

        # Apply column filter if specified (OR logic for multiple columns)
        if column:
            kanban_columns = KanbanColumn.get_column_names(repo_path)

            # Resolve all column specifications to column names
            target_columns = []
            include_no_column = False

            for col in column:
                # Check if column is numeric
                if col.isdigit():
                    column_index = int(col)
                    if column_index == 0:
                        # Include issues with no kanban column
                        include_no_column = True
                    elif 1 <= column_index <= len(kanban_columns):
                        # Add specific column by index
                        target_columns.append(kanban_columns[column_index - 1])
                    # Invalid column index - skip it, continue with others
                else:
                    # Add by column name if it exists
                    if col in kanban_columns:
                        target_columns.append(col)
                    # Unknown column name - skip it, continue with others

            # Filter issues: include if in ANY target column OR no column (if specified)
            filtered_issues = []
            for issue in issues:
                # Get the issue's kanban column (same pattern as move_to_board_column)
                issue_column = next((label for label in (issue.labels or []) if label in kanban_columns), None)

                # Check if issue is in any target column
                if issue_column in target_columns:
                    filtered_issues.append(issue)
                # Check if issue has no column and we're including those
                elif include_no_column and issue_column is None:
                    filtered_issues.append(issue)

            issues = filtered_issues

        # Apply label filter if specified (AND logic)
        if labels:
            for label in labels:
                issues = [
                    issue for issue in issues
                    if label in (issue.labels or [])
                ]

        # Apply milestone filter if specified (OR logic)
        if milestones:
            issues = [
                issue for issue in issues
                if issue.milestone in milestones
            ]

        # Sort by IID ascending (handle both int and str IIDs for temporary issues)
        issues.sort(key=lambda issue: (isinstance(issue.iid, str), issue.iid if isinstance(issue.iid, int) else issue.iid))

        return issues


# ===== Assign Backend =====

Issue.backend = IssueBackend()
