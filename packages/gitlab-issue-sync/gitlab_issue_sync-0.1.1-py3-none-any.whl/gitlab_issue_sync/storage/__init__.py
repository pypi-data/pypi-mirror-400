"""Storage module public API.

This module provides the public interface for working with GitLab entities locally.
Base classes and backend implementations are internal details and not exported.
"""

# Entities (public API)
# Result types (public API)
from .base import SyncResult
from .config import KanbanColumn
from .conflicts import Conflict

# Exceptions (public API)
from .exceptions import StorageError
from .issue import ISSUE_STATE_CLOSED, ISSUE_STATE_OPENED, Issue, IssueComment, IssueLink
from .label import Label
from .milestone import Milestone

# Helper functions (public API)
from .utils import (
    ensure_storage_structure,
    get_issues_dir,
    get_next_temporary_id,
    parse_issue,
    serialize_issue,
    state_to_dir,
)
from .work_item_types import WorkItemType, WorkItemTypeCache

__all__ = [
    # Entities
    "Issue",
    "IssueComment",
    "IssueLink",
    "Label",
    "Milestone",
    "KanbanColumn",
    "Conflict",
    "WorkItemType",
    "WorkItemTypeCache",
    # Constants
    "ISSUE_STATE_OPENED",
    "ISSUE_STATE_CLOSED",
    # Results
    "SyncResult",
    # Exceptions
    "StorageError",
    # Utils
    "state_to_dir",
    "get_issues_dir",
    "ensure_storage_structure",
    "get_next_temporary_id",
    "serialize_issue",
    "parse_issue",
]
