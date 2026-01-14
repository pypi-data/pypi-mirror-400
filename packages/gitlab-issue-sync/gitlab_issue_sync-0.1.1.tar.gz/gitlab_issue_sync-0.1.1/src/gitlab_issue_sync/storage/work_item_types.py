"""Work item type cache for automatic type conversions.

Work item types (Issue, Task, Epic, etc.) have instance-specific IDs that vary
between GitLab installations. This module provides a local cache for efficient
lookup when performing automatic type conversions during parent operations.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from .exceptions import StorageError

logger = logging.getLogger(__name__)

# Storage directory relative to .issues/
WORK_ITEM_TYPES_DIR = ".work_item_types"
WORK_ITEM_TYPES_FILE = "work_item_types.json"


@dataclass
class WorkItemType:
    """A single work item type from GitLab."""

    id: str  # GraphQL global ID, e.g., "gid://gitlab/WorkItems::Type/1"
    name: str  # e.g., "Issue", "Task", "Epic"
    icon_name: str | None = None  # e.g., "issue-type-issue"


@dataclass
class WorkItemTypeCache:
    """
    Cached work item types for a project.

    Provides efficient lookup of type IDs by name for automatic type conversions.
    """

    types: list[WorkItemType] = field(default_factory=list)
    fetched_at: datetime | None = None

    # ===== Lookup Methods =====

    def get_type_by_name(self, name: str) -> WorkItemType | None:
        """
        Get a work item type by name.

        Args:
            name: Type name (e.g., "Issue", "Task")

        Returns:
            WorkItemType or None if not found
        """
        for wtype in self.types:
            if wtype.name == name:
                return wtype
        return None

    def get_type_id_by_name(self, name: str) -> str | None:
        """
        Get the GraphQL ID for a type by name.

        Args:
            name: Type name (e.g., "Issue", "Task")

        Returns:
            GraphQL ID (e.g., "gid://gitlab/WorkItems::Type/1") or None
        """
        wtype = self.get_type_by_name(name)
        return wtype.id if wtype else None

    def get_type_name_by_id(self, type_id: str) -> str | None:
        """
        Get the type name by GraphQL ID.

        Args:
            type_id: GraphQL ID (e.g., "gid://gitlab/WorkItems::Type/1")

        Returns:
            Type name (e.g., "Issue") or None
        """
        for wtype in self.types:
            if wtype.id == type_id:
                return wtype.name
        return None

    def get_task_type_id(self) -> str | None:
        """Get the GraphQL ID for Task type."""
        return self.get_type_id_by_name("Task")

    def get_issue_type_id(self) -> str | None:
        """Get the GraphQL ID for Issue type."""
        return self.get_type_id_by_name("Issue")

    def get_name_to_id_map(self) -> dict[str, str]:
        """Get a mapping of type names to GraphQL IDs."""
        return {wtype.name: wtype.id for wtype in self.types}

    # ===== Persistence =====

    @classmethod
    def _get_cache_path(cls, repo_path: Path) -> Path:
        """Get the path to the cache file."""
        return repo_path / ".issues" / WORK_ITEM_TYPES_DIR / WORK_ITEM_TYPES_FILE

    @classmethod
    def load(cls, repo_path: Path | None = None) -> "WorkItemTypeCache":
        """
        Load the work item type cache from disk.

        Args:
            repo_path: Path to repository root

        Returns:
            WorkItemTypeCache (empty if file doesn't exist)
        """
        path = repo_path or Path.cwd()
        cache_path = cls._get_cache_path(path)

        if not cache_path.exists():
            logger.debug(f"Work item type cache not found at {cache_path}")
            return cls()

        try:
            with open(cache_path) as f:
                data = json.load(f)

            types = []
            for type_data in data.get("types", []):
                types.append(
                    WorkItemType(
                        id=type_data["id"],
                        name=type_data["name"],
                        icon_name=type_data.get("icon_name"),
                    )
                )

            fetched_at = None
            if data.get("fetched_at"):
                fetched_at = datetime.fromisoformat(data["fetched_at"])

            return cls(types=types, fetched_at=fetched_at)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to load work item type cache: {e}")
            return cls()

    def save(self, repo_path: Path | None = None) -> None:
        """
        Save the work item type cache to disk.

        Args:
            repo_path: Path to repository root
        """
        path = repo_path or Path.cwd()
        cache_path = self._get_cache_path(path)

        # Ensure directory exists
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "types": [
                {
                    "id": wtype.id,
                    "name": wtype.name,
                    "icon_name": wtype.icon_name,
                }
                for wtype in self.types
            ],
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }

        with open(cache_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.debug(f"Saved {len(self.types)} work item types to {cache_path}")

    # ===== Fetch from GitLab =====

    @classmethod
    def fetch_and_save(
        cls,
        graphql_client: "GitLabGraphQLClient",  # noqa: F821
        project_path: str,
        repo_path: Path | None = None,
    ) -> "WorkItemTypeCache":
        """
        Fetch work item types from GitLab and save to cache.

        Args:
            graphql_client: GitLab GraphQL client instance
            project_path: Full project path (e.g., "group/project")
            repo_path: Path to repository root

        Returns:
            WorkItemTypeCache with fetched types
        """
        try:
            type_dicts = graphql_client.get_work_item_types(project_path)

            types = []
            for type_dict in type_dicts:
                types.append(
                    WorkItemType(
                        id=type_dict["id"],
                        name=type_dict["name"],
                        icon_name=type_dict.get("iconName"),
                    )
                )

            cache = cls(types=types, fetched_at=datetime.now(UTC))
            cache.save(repo_path)

            logger.info(f"Cached {len(types)} work item types")
            return cache

        except Exception as e:
            raise StorageError(f"Failed to fetch work item types: {e}") from e

    @classmethod
    def ensure_cached(
        cls,
        graphql_client: "GitLabGraphQLClient",  # noqa: F821
        project_path: str,
        repo_path: Path | None = None,
    ) -> "WorkItemTypeCache":
        """
        Ensure work item types are cached, fetching if necessary.

        Args:
            graphql_client: GitLab GraphQL client instance
            project_path: Full project path (e.g., "group/project")
            repo_path: Path to repository root

        Returns:
            WorkItemTypeCache (from cache or freshly fetched)
        """
        path = repo_path or Path.cwd()
        cache = cls.load(path)

        if not cache.types:
            logger.info("Work item type cache empty, fetching from GitLab")
            cache = cls.fetch_and_save(graphql_client, project_path, path)

        return cache
