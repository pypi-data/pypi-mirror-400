"""Generic metadata management pattern for issue metadata."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from .storage import Issue, IssueLink


@dataclass
class MetadataChange:
    """Represents a change to metadata."""

    added: list[Any]
    removed: list[Any]
    unchanged: list[Any]


class MetadataHandler(ABC):
    """Abstract base class for metadata handlers."""

    @property
    @abstractmethod
    def metadata_name(self) -> str:
        """Human-readable name (e.g., 'labels', 'assignees', 'linked issues')"""
        pass

    @property
    @abstractmethod
    def metadata_key(self) -> str:
        """Key in Issue dataclass (e.g., 'labels', 'assignees', 'links')"""
        pass

    @abstractmethod
    def get_values(self, issue: Issue) -> list[Any]:
        """Get current metadata values from issue."""
        pass

    @abstractmethod
    def add_values(self, issue: Issue, values: list[Any], **kwargs) -> MetadataChange:
        """Add values to issue metadata. Returns change summary."""
        pass

    @abstractmethod
    def remove_values(self, issue: Issue, values: list[Any]) -> MetadataChange:
        """Remove values from issue metadata. Returns change summary."""
        pass

    @abstractmethod
    def set_values(self, issue: Issue, values: list[Any], **kwargs) -> MetadataChange:
        """Replace all values. Returns change summary."""
        pass

    @abstractmethod
    def unset_values(self, issue: Issue) -> MetadataChange:
        """Clear all values. Returns change summary."""
        pass

    @abstractmethod
    def format_value(self, value: Any) -> str:
        """Format a single value for display."""
        pass

    @abstractmethod
    def validate_values(self, values: list[Any], **kwargs) -> None:
        """Validate values before applying. Raise ValueError if invalid."""
        pass


class LabelHandler(MetadataHandler):
    """Handler for issue labels."""

    @property
    def metadata_name(self) -> str:
        return "labels"

    @property
    def metadata_key(self) -> str:
        return "labels"

    def get_values(self, issue: Issue) -> list[str]:
        return issue.labels.copy()

    def add_values(self, issue: Issue, values: list[str], **kwargs) -> MetadataChange:
        current = set(issue.labels)
        new = set(values)
        added = list(new - current)
        unchanged = list(new & current)

        issue.labels = sorted(current | new)

        return MetadataChange(added=added, removed=[], unchanged=unchanged)

    def remove_values(self, issue: Issue, values: list[str]) -> MetadataChange:
        current = set(issue.labels)
        to_remove = set(values)
        removed = list(current & to_remove)
        not_found = list(to_remove - current)

        issue.labels = sorted(current - to_remove)

        return MetadataChange(added=[], removed=removed, unchanged=not_found)

    def set_values(self, issue: Issue, values: list[str], **kwargs) -> MetadataChange:
        old = set(issue.labels)
        new = set(values)

        added = list(new - old)
        removed = list(old - new)
        unchanged = list(old & new)

        issue.labels = sorted(new)

        return MetadataChange(added=added, removed=removed, unchanged=unchanged)

    def unset_values(self, issue: Issue) -> MetadataChange:
        removed = issue.labels.copy()
        issue.labels = []

        return MetadataChange(added=[], removed=removed, unchanged=[])

    def format_value(self, value: str) -> str:
        return value

    def validate_values(self, values: list[str], **kwargs) -> None:
        if not all(isinstance(v, str) for v in values):
            raise ValueError("All label values must be strings")
        if any(not v.strip() for v in values):
            raise ValueError("Labels cannot be empty strings")


class AssigneeHandler(MetadataHandler):
    """Handler for issue assignees."""

    @property
    def metadata_name(self) -> str:
        return "assignees"

    @property
    def metadata_key(self) -> str:
        return "assignees"

    def get_values(self, issue: Issue) -> list[str]:
        return issue.assignees.copy()

    def add_values(self, issue: Issue, values: list[str], **kwargs) -> MetadataChange:
        current = set(issue.assignees)
        new = set(values)
        added = list(new - current)
        unchanged = list(new & current)

        issue.assignees = sorted(current | new)

        return MetadataChange(added=added, removed=[], unchanged=unchanged)

    def remove_values(self, issue: Issue, values: list[str]) -> MetadataChange:
        current = set(issue.assignees)
        to_remove = set(values)
        removed = list(current & to_remove)
        not_found = list(to_remove - current)

        issue.assignees = sorted(current - to_remove)

        return MetadataChange(added=[], removed=removed, unchanged=not_found)

    def set_values(self, issue: Issue, values: list[str], **kwargs) -> MetadataChange:
        old = set(issue.assignees)
        new = set(values)

        added = list(new - old)
        removed = list(old - new)
        unchanged = list(old & new)

        issue.assignees = sorted(new)

        return MetadataChange(added=added, removed=removed, unchanged=unchanged)

    def unset_values(self, issue: Issue) -> MetadataChange:
        removed = issue.assignees.copy()
        issue.assignees = []

        return MetadataChange(added=[], removed=removed, unchanged=[])

    def format_value(self, value: str) -> str:
        return value

    def validate_values(self, values: list[str], **kwargs) -> None:
        if not all(isinstance(v, str) for v in values):
            raise ValueError("All assignee values must be usernames (strings)")
        if any(not v.strip() for v in values):
            raise ValueError("Assignee usernames cannot be empty strings")


@dataclass
class LinkValue:
    """Represents a link value with optional type."""

    target_iid: int
    link_type: str = "relates_to"  # relates_to, blocks, is_blocked_by


class LinkedIssuesHandler(MetadataHandler):
    """Handler for linked issues."""

    @property
    def metadata_name(self) -> str:
        return "linked issues"

    @property
    def metadata_key(self) -> str:
        return "links"

    def get_values(self, issue: Issue) -> list[IssueLink]:
        return issue.links.copy()

    def add_values(self, issue: Issue, values: list[LinkValue], **kwargs) -> MetadataChange:
        """Add linked issues with optional link types."""
        current_iids = {link.target_issue_iid for link in issue.links}
        added = []
        unchanged = []

        for value in values:
            if value.target_iid not in current_iids:
                # Create new link (will be synced to GitLab on push)
                new_link = IssueLink(
                    link_id=0,  # Temporary, will be set by GitLab
                    target_project_id=0,  # Will be set during push
                    target_issue_iid=value.target_iid,
                    link_type=value.link_type,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
                issue.links.append(new_link)
                added.append(value.target_iid)
            else:
                unchanged.append(value.target_iid)

        return MetadataChange(added=added, removed=[], unchanged=unchanged)

    def remove_values(self, issue: Issue, values: list[int], **kwargs) -> MetadataChange:
        """Remove linked issues by target IID."""
        to_remove = set(values)
        removed = []
        not_found = []

        new_links = []
        for link in issue.links:
            if link.target_issue_iid in to_remove:
                removed.append(link.target_issue_iid)
            else:
                new_links.append(link)

        not_found = list(to_remove - set(removed))
        issue.links = new_links

        return MetadataChange(added=[], removed=removed, unchanged=not_found)

    def set_values(self, issue: Issue, values: list[LinkValue], **kwargs) -> MetadataChange:
        """Replace all links."""
        old_iids = {link.target_issue_iid for link in issue.links}
        new_iids = {v.target_iid for v in values}

        added = list(new_iids - old_iids)
        removed = list(old_iids - new_iids)
        unchanged = list(old_iids & new_iids)

        # Create new links
        issue.links = [
            IssueLink(
                link_id=0,
                target_project_id=0,
                target_issue_iid=value.target_iid,
                link_type=value.link_type,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            for value in values
        ]

        return MetadataChange(added=added, removed=removed, unchanged=unchanged)

    def unset_values(self, issue: Issue) -> MetadataChange:
        """Remove all links."""
        removed = [link.target_issue_iid for link in issue.links]
        issue.links = []

        return MetadataChange(added=[], removed=removed, unchanged=[])

    def format_value(self, value: IssueLink) -> str:
        """Format link for display."""
        return f"#{value.target_issue_iid} ({value.link_type})"

    def validate_values(self, values: list[LinkValue], **kwargs) -> None:
        """Validate link values."""
        valid_types = {"relates_to", "blocks", "is_blocked_by"}

        for value in values:
            if not isinstance(value.target_iid, int) or value.target_iid <= 0:
                raise ValueError(f"Invalid issue IID: {value.target_iid}")
            if value.link_type not in valid_types:
                raise ValueError(f"Invalid link type: {value.link_type}. Must be one of {valid_types}")


class MilestoneHandler(MetadataHandler):
    """Handler for issue milestone."""

    @property
    def metadata_name(self) -> str:
        return "milestone"

    @property
    def metadata_key(self) -> str:
        return "milestone"

    def get_values(self, issue: Issue) -> list[str]:
        """Get current milestone (returns list for consistency, but always 0 or 1 item)."""
        return [issue.milestone] if issue.milestone else []

    def add_values(self, issue: Issue, values: list[str], **kwargs) -> MetadataChange:
        """Not supported - milestone doesn't support 'add' operation."""
        raise ValueError("Milestone does not support 'add' operation. Use 'set' instead.")

    def remove_values(self, issue: Issue, values: list[str]) -> MetadataChange:
        """Not supported - milestone doesn't support 'remove' operation."""
        raise ValueError("Milestone does not support 'remove' operation. Use 'unset' instead.")

    def set_values(self, issue: Issue, values: list[str], **kwargs) -> MetadataChange:
        """Set milestone (expects exactly one value)."""
        if len(values) != 1:
            raise ValueError("Milestone 'set' operation requires exactly one milestone title")

        new_milestone = values[0]
        old_milestone = issue.milestone

        if old_milestone == new_milestone:
            # No change
            return MetadataChange(added=[], removed=[], unchanged=[new_milestone])

        issue.milestone = new_milestone

        if old_milestone:
            # Replaced old milestone
            return MetadataChange(added=[new_milestone], removed=[old_milestone], unchanged=[])
        else:
            # Set milestone (was None)
            return MetadataChange(added=[new_milestone], removed=[], unchanged=[])

    def unset_values(self, issue: Issue) -> MetadataChange:
        """Clear milestone."""
        old_milestone = issue.milestone
        issue.milestone = None

        if old_milestone:
            return MetadataChange(added=[], removed=[old_milestone], unchanged=[])
        else:
            # Already None
            return MetadataChange(added=[], removed=[], unchanged=[])

    def format_value(self, value: str) -> str:
        return value

    def validate_values(self, values: list[str], **kwargs) -> None:
        """Validate milestone value."""
        if not all(isinstance(v, str) for v in values):
            raise ValueError("Milestone value must be a string")
        if len(values) != 1:
            raise ValueError("Milestone 'set' operation requires exactly one milestone title")
        if not values[0].strip():
            raise ValueError("Milestone title cannot be empty")


class ParentHandler(MetadataHandler):
    """Handler for issue parent (work item hierarchy)."""

    @property
    def metadata_name(self) -> str:
        return "parent"

    @property
    def metadata_key(self) -> str:
        return "parent_iid"

    def get_values(self, issue: Issue) -> list[int]:
        """Get current parent (returns list for consistency, but always 0 or 1 item)."""
        return [issue.parent_iid] if issue.parent_iid else []

    def add_values(self, issue: Issue, values: list[int], **kwargs) -> MetadataChange:
        """Not supported - parent doesn't support 'add' operation."""
        raise ValueError("Parent does not support 'add' operation. Use 'set' instead.")

    def remove_values(self, issue: Issue, values: list[int]) -> MetadataChange:
        """Not supported - parent doesn't support 'remove' operation."""
        raise ValueError("Parent does not support 'remove' operation. Use 'unset' instead.")

    def set_values(self, issue: Issue, values: list[int], **kwargs) -> MetadataChange:
        """Set parent (expects exactly one value)."""
        if len(values) != 1:
            raise ValueError("Parent 'set' operation requires exactly one parent IID")

        new_parent_iid = values[0]
        old_parent_iid = issue.parent_iid

        # Validate: issue cannot be its own parent
        if new_parent_iid == issue.iid:
            raise ValueError(f"Issue #{issue.iid} cannot be its own parent")

        if old_parent_iid == new_parent_iid:
            # No change
            return MetadataChange(added=[], removed=[], unchanged=[new_parent_iid])

        issue.parent_iid = new_parent_iid

        if old_parent_iid:
            # Replaced old parent
            return MetadataChange(added=[new_parent_iid], removed=[old_parent_iid], unchanged=[])
        else:
            # Set parent (was None)
            return MetadataChange(added=[new_parent_iid], removed=[], unchanged=[])

    def unset_values(self, issue: Issue) -> MetadataChange:
        """Clear parent."""
        old_parent_iid = issue.parent_iid
        issue.parent_iid = None

        if old_parent_iid:
            return MetadataChange(added=[], removed=[old_parent_iid], unchanged=[])
        else:
            # Already None
            return MetadataChange(added=[], removed=[], unchanged=[])

    def format_value(self, value: int) -> str:
        return f"#{value}"

    def validate_values(self, values: list[int], **kwargs) -> None:
        """Validate parent IID value."""
        if not all(isinstance(v, int) for v in values):
            raise ValueError("Parent value must be an integer (issue IID)")
        if len(values) != 1:
            raise ValueError("Parent 'set' operation requires exactly one parent IID")
        if values[0] <= 0:
            raise ValueError("Parent IID must be a positive integer")


class MetadataManager:
    """Central manager for all metadata handlers."""

    def __init__(self):
        self._handlers: dict[str, MetadataHandler] = {}

    def register(self, handler: MetadataHandler) -> None:
        """Register a metadata handler."""
        self._handlers[handler.metadata_name] = handler

    def get_handler(self, metadata_name: str) -> MetadataHandler:
        """Get handler by name."""
        if metadata_name not in self._handlers:
            raise ValueError(f"Unknown metadata type: {metadata_name}")
        return self._handlers[metadata_name]

    def list_types(self) -> list[str]:
        """List all registered metadata types."""
        return list(self._handlers.keys())


# Global instance
_manager = MetadataManager()
_manager.register(LabelHandler())
_manager.register(AssigneeHandler())
_manager.register(LinkedIssuesHandler())
_manager.register(MilestoneHandler())
_manager.register(ParentHandler())


def get_metadata_manager() -> MetadataManager:
    """Get the global metadata manager."""
    return _manager
