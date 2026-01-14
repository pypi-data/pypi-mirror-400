"""Base classes for storage architecture.

IMPORTANT: These classes are internal implementation details and should NOT be
exported in storage/__init__.py. Only entities, result types, and helper functions
should be part of the public API.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

if TYPE_CHECKING:
    from ..config import ProjectConfig

# Type variable for generic storage backend
T = TypeVar("T", bound="Storable")

# Issue state constants (used by MarkdownStorageBackend)
ISSUE_STATE_OPENED = "opened"
ISSUE_STATE_CLOSED = "closed"


class ChangeType(Enum):
    """
    Represents the type of change detected during three-way sync.

    Used by _detect_change_type() to determine sync strategy.
    """
    NO_CHANGE = "NO_CHANGE"
    LOCAL_MODIFIED = "LOCAL_MODIFIED"
    REMOTE_MODIFIED = "REMOTE_MODIFIED"
    BOTH_MODIFIED = "BOTH_MODIFIED"
    NEW_LOCAL = "NEW_LOCAL"
    NEW_REMOTE = "NEW_REMOTE"
    DELETED_LOCAL = "DELETED_LOCAL"
    DELETED_REMOTE = "DELETED_REMOTE"


@dataclass
class SyncResult:
    """Result of sync operation (pull or push)."""

    created: list[str | int] = field(default_factory=list)
    updated: list[str | int] = field(default_factory=list)
    deleted: list[str | int] = field(default_factory=list)
    auto_resolve_details: dict[str | int, str] = field(default_factory=dict)
    conflicts: list[str | int] = field(default_factory=list)
    conflict_details: dict[str | int, str] = field(default_factory=dict)


@dataclass
class Storable(ABC):
    """
    Base class for entities that support local-first sync workflow.

    Each subclass declares a backend that handles all storage and sync operations.
    Provides pull() and push() class methods for git-like sync workflow.
    """

    # Sync metadata (all storables have these)
    status: str = field(default="synced", init=False, repr=False)
    remote_id: int | None = field(default=None, init=False, repr=False)

    # Backend is class variable, set by subclass
    backend: ClassVar["StorageBackend"] = None  # type: ignore

    @abstractmethod
    def compute_content_hash(self) -> str:
        """
        Compute hash of entity content for change detection.

        Should include all user-modifiable fields, exclude sync metadata.
        """
        pass

    @abstractmethod
    def get_identifier(self) -> str | int:
        """
        Get unique identifier for this entity.

        Returns:
            For issues: iid (int)
            For labels: name (str)
        """
        pass

    def has_changed_from(self, original: "Storable") -> bool:
        """Check if this entity has changed from original snapshot."""
        return self.compute_content_hash() != original.compute_content_hash()

    @classmethod
    def load(cls, identifier: str | int, repo_path: Path | None = None) -> "Storable | None":
        """
        Load entity by identifier from local storage.

        Args:
            identifier: Entity identifier (IID for issues, name for labels, etc.)
            repo_path: Path to repository root

        Returns:
            Entity object or None if not found
        """
        if cls.backend is None:
            raise NotImplementedError(f"{cls.__name__} has no backend configured")
        return cls.backend.load(identifier, repo_path or Path.cwd())

    @classmethod
    def load_all(cls, repo_path: Path | None = None) -> list["Storable"]:
        """
        Load all entities from local storage.

        Args:
            repo_path: Path to repository root

        Returns:
            List of entity objects
        """
        if cls.backend is None:
            raise NotImplementedError(f"{cls.__name__} has no backend configured")
        return cls.backend.load_all(repo_path or Path.cwd())

    @classmethod
    def pull(cls, project, repo_path: Path, **kwargs) -> SyncResult:
        """
        Pull entities from GitLab and update local storage.

        Delegates to backend.pull() which handles three-way merge.

        Args:
            project: GitLab project object
            repo_path: Path to repository root
            **kwargs: Additional parameters (e.g., state="opened" for Issue)
        """
        if cls.backend is None:
            raise NotImplementedError(f"{cls.__name__} has no backend configured")
        return cls.backend.pull(cls, project, repo_path, **kwargs)

    @classmethod
    def push(cls, project, repo_path: Path) -> SyncResult:
        """
        Push local changes to GitLab.

        Delegates to backend.push() which handles pending/modified/deleted.
        """
        if cls.backend is None:
            raise NotImplementedError(f"{cls.__name__} has no backend configured")
        return cls.backend.push(cls, project, repo_path)


class StorageBackend(ABC, Generic[T]):
    """
    Abstract storage backend for storable entities.

    Handles:
    - Local file I/O (save, load, delete)
    - Original snapshots (for conflict detection)
    - GitLab sync (pull, push with three-way merge)
    """

    # ===== Local Operations =====

    @abstractmethod
    def save(self, entity: T, repo_path: Path) -> None:
        pass

    @abstractmethod
    def load(self, identifier: str | int, repo_path: Path) -> T | None:
        pass

    @abstractmethod
    def load_all(self, repo_path: Path) -> list[T]:
        pass

    @abstractmethod
    def delete(self, identifier: str | int, repo_path: Path) -> None:
        pass

    # ===== Original Snapshots =====

    @abstractmethod
    def save_original(self, entity: T, repo_path: Path) -> None:
        pass

    @abstractmethod
    def load_original(self, identifier: str | int, repo_path: Path) -> T | None:
        pass

    @abstractmethod
    def load_all_originals(self, repo_path: Path) -> list[T]:
        pass

    # ===== GitLab API Operations =====

    @abstractmethod
    def fetch_from_gitlab(self, project, repo_path: Path) -> list[T]:
        """Returns list of entities with status="synced" and remote_id set."""
        pass

    @abstractmethod
    def create_on_gitlab(self, entity: T, project) -> int:
        """Returns remote_id of created entity."""
        pass

    @abstractmethod
    def update_on_gitlab(self, entity: T, project) -> None:
        pass

    @abstractmethod
    def delete_on_gitlab(self, entity: T, project) -> None:
        pass

    # ===== Sync Operations (Three-Way Merge) =====

    def pull(self, entity_class: type[T], project, repo_path: Path, **kwargs) -> SyncResult:
        """
        Pull entities from GitLab and update local storage.

        Implements three-way merge: local, original, remote.

        Args:
            entity_class: The entity class being pulled
            project: GitLab project object
            repo_path: Path to repository root
            **kwargs: Additional parameters passed to fetch_from_gitlab (e.g., state for Issue)
        """
        # Fetch remote entities (pass through kwargs for entity-specific filtering)
        remote_entities = {e.get_identifier(): e for e in self.fetch_from_gitlab(project, repo_path, **kwargs)}

        # Load local and original
        local_entities = {e.get_identifier(): e for e in self.load_all(repo_path)}
        original_entities = {e.get_identifier(): e for e in self.load_all_originals(repo_path)}

        result = SyncResult()

        # Process all entities (union of local and remote)
        all_ids = set(local_entities.keys()) | set(remote_entities.keys())

        for entity_id in all_ids:
            local = local_entities.get(entity_id)
            original = original_entities.get(entity_id)
            remote = remote_entities.get(entity_id)

            change_type = self._detect_change_type(local, original, remote)

            if change_type == ChangeType.NEW_REMOTE:
                # New from remote, save it
                self.save(remote, repo_path)  # type: ignore
                self.save_original(remote, repo_path)  # type: ignore
                result.created.append(entity_id)

            elif change_type == ChangeType.REMOTE_MODIFIED:
                # Remote changed, local unchanged - update
                self.save(remote, repo_path)  # type: ignore
                self.save_original(remote, repo_path)  # type: ignore
                result.updated.append(entity_id)

            elif change_type == ChangeType.BOTH_MODIFIED:
                # Both modified - try auto-resolution if all three versions exist
                # (BOTH_MODIFIED can also occur for delete/modify conflicts)
                if local and original and remote:
                    # Compute conflicting fields for display
                    entity_class_type = type(local)
                    conflicting_fields = []
                    if hasattr(entity_class_type, 'compute_field_diff'):
                        field_diff = entity_class_type.compute_field_diff(original, local, remote)
                        conflicting_fields = [f for f in field_diff.keys() if not f.startswith("comment_")]

                    # Try auto-resolution via hook (subclasses can override)
                    merged = self._try_auto_resolve(local, original, remote, repo_path)

                    if merged is not None:
                        # Auto-resolved! Update local with merged, original with remote
                        self.save(merged, repo_path)
                        self.save_original(remote, repo_path)
                        result.updated.append(entity_id)
                        result.auto_resolve_details[entity_id] = ", ".join(conflicting_fields)
                    else:
                        # Could not auto-resolve - keep local AND original as-is
                        # Record conflict with cached remote for manual resolution
                        self._record_conflict(entity_id, conflicting_fields, remote, repo_path)
                        result.conflicts.append(entity_id)
                        result.conflict_details[entity_id] = (
                            f"Could not auto-resolve: {', '.join(conflicting_fields)}. "
                            "Run 'conflicts resolve' after manual resolution."
                        )
                else:
                    # Delete/modify conflict - can't auto-resolve
                    result.conflicts.append(entity_id)
                    if not remote:
                        result.conflict_details[entity_id] = "Remote deleted but local modified"
                    else:
                        result.conflict_details[entity_id] = "Local deleted but remote modified"

            elif change_type == ChangeType.LOCAL_MODIFIED:
                # Local changed, remote unchanged - keep local
                # Original snapshot unchanged (will update on push)
                pass

            elif change_type == ChangeType.NO_CHANGE:
                # Sync remote_id and read-only fields if needed
                if local and remote:
                    needs_save = False

                    if local.remote_id != remote.remote_id:
                        local.remote_id = remote.remote_id
                        needs_save = True

                    # Merge read-only fields from remote (e.g., child_iids, updated_at)
                    # These fields are managed by GitLab and should always reflect remote state
                    if hasattr(local, "_read_only_fields"):
                        for field_name in local._read_only_fields:
                            remote_value = getattr(remote, field_name, None)
                            local_value = getattr(local, field_name, None)
                            if remote_value != local_value:
                                setattr(local, field_name, remote_value)
                                needs_save = True

                    if needs_save:
                        self.save(local, repo_path)

        return result

    def push(self, entity_class: type[T], project, repo_path: Path) -> SyncResult:
        """
        Push local changes to GitLab.

        Handles pending (create), modified (update), deleted (delete).
        """
        local_entities = self.load_all(repo_path)
        result = SyncResult()

        for entity in local_entities:
            entity_id = entity.get_identifier()

            # Check if entity has a status - if not, it's an error state
            if not hasattr(entity, 'status') or entity.status is None:
                result.conflicts.append(entity_id)
                result.conflict_details[entity_id] = (
                    "Missing 'status' field - entity state unknown. "
                    "Expected one of: pending, synced, modified, deleted"
                )
                continue

            if entity.status == "pending":
                # Create new entity on GitLab
                try:
                    remote_id = self.create_on_gitlab(entity, project)

                    # Update local state
                    entity.remote_id = remote_id
                    entity.status = "synced"
                    self.save(entity, repo_path)
                    self.save_original(entity, repo_path)
                    result.created.append(entity_id)
                except Exception as e:
                    result.conflicts.append(entity_id)
                    result.conflict_details[entity_id] = f"Failed to create on GitLab: {e}"

            elif entity.status == "modified":
                # Check for conflicts
                original = self.load_original(entity_id, repo_path)

                if original and entity.remote_id:
                    # Fetch current remote state
                    remote_entities = self.fetch_from_gitlab(project, repo_path)
                    remote = next((e for e in remote_entities if e.get_identifier() == entity_id), None)

                    if remote:
                        change_type = self._detect_change_type(entity, original, remote)
                        if change_type == ChangeType.BOTH_MODIFIED:
                            result.conflicts.append(entity_id)
                            result.conflict_details[entity_id] = (
                                "Both local and remote modified since last sync - manual merge required"
                            )
                            continue

                # No conflict, update
                try:
                    self.update_on_gitlab(entity, project)
                    entity.status = "synced"
                    self.save(entity, repo_path)
                    self.save_original(entity, repo_path)
                    result.updated.append(entity_id)
                except Exception as e:
                    result.conflicts.append(entity_id)
                    result.conflict_details[entity_id] = f"Failed to update on GitLab: {e}"

            elif entity.status == "deleted":
                # Delete from GitLab
                try:
                    self.delete_on_gitlab(entity, project)
                    self.delete(entity_id, repo_path)
                    result.deleted.append(entity_id)
                except Exception as e:
                    result.conflicts.append(entity_id)
                    result.conflict_details[entity_id] = f"Failed to delete on GitLab: {e}"

            elif entity.status == "synced":
                # Already synced, no action needed
                pass
            else:
                # Unknown status
                result.conflicts.append(entity_id)
                result.conflict_details[entity_id] = (
                    f"Unknown status '{entity.status}' - expected one of: pending, synced, modified, deleted"
                )

        return result

    def _detect_change_type(self, local: T | None, original: T | None, remote: T | None) -> ChangeType:
        """
        Three-way comparison for conflict detection.

        Returns:
            ChangeType enum value indicating the type of change detected
        """
        if not original:
            # No original snapshot
            if local and remote:
                return ChangeType.BOTH_MODIFIED if local.has_changed_from(remote) else ChangeType.NO_CHANGE
            elif local:
                return ChangeType.NEW_LOCAL
            elif remote:
                return ChangeType.NEW_REMOTE
            else:
                return ChangeType.NO_CHANGE

        # Have original snapshot
        local_changed = local.has_changed_from(original) if local else False
        remote_changed = remote.has_changed_from(original) if remote else False

        if not local and not remote:
            return ChangeType.DELETED_LOCAL
        elif not local:
            return ChangeType.DELETED_LOCAL if not remote_changed else ChangeType.BOTH_MODIFIED
        elif not remote:
            return ChangeType.DELETED_REMOTE if not local_changed else ChangeType.BOTH_MODIFIED
        elif local_changed and remote_changed:
            return ChangeType.BOTH_MODIFIED
        elif local_changed:
            return ChangeType.LOCAL_MODIFIED
        elif remote_changed:
            return ChangeType.REMOTE_MODIFIED
        else:
            return ChangeType.NO_CHANGE

    def _try_auto_resolve(self, local: T, original: T, remote: T, repo_path: Path) -> T | None:
        """
        Hook for automatic conflict resolution during pull.

        Subclasses can override to implement entity-specific merge logic.

        Returns:
            Merged entity if auto-resolution succeeded, None if manual resolution needed
        """
        return None

    def _record_conflict(
        self,
        entity_id: str | int,
        conflicting_fields: list[str],
        remote: T,
        repo_path: Path,
    ) -> None:
        """
        Hook for recording conflict state during pull.

        Subclasses can override to persist conflict information and cache remote.
        """
        pass


class JsonStorageBackend(StorageBackend[T]):
    """
    Storage backend for JSON-based entity collections.

    Stores all entities in single JSON file:
    .issues/.{entity_type}/{entity_type}.json
    """

    def __init__(self, entity_type: str, identifier_field: str = "name"):
        """
        Args:
            entity_type: Type name (e.g., "labels")
            identifier_field: Field name for identifier ("name" for labels)
        """
        self.entity_type = entity_type
        self.identifier_field = identifier_field

    def _get_paths(self, repo_path: Path) -> dict[str, Path]:
        base = repo_path / ".issues" / f".{self.entity_type}"
        return {
            "data_file": base / f"{self.entity_type}.json",
            "originals_file": base / ".sync" / "originals.json",
        }

    # ===== Local Operations =====

    def save(self, entity: T, repo_path: Path) -> None:
        entities = self.load_all(repo_path)
        entity_id = getattr(entity, self.identifier_field)

        # Replace or append
        entities = [e for e in entities if getattr(e, self.identifier_field) != entity_id]
        entities.append(entity)

        self._write_all(entities, repo_path, is_original=False)

    def load(self, identifier: str | int, repo_path: Path) -> T | None:
        entities = self.load_all(repo_path)
        return next((e for e in entities if getattr(e, self.identifier_field) == identifier), None)

    def load_all(self, repo_path: Path) -> list[T]:
        paths = self._get_paths(repo_path)
        return self._read_all(paths["data_file"])

    def delete(self, identifier: str | int, repo_path: Path) -> None:
        entities = self.load_all(repo_path)
        entities = [e for e in entities if getattr(e, self.identifier_field) != identifier]
        self._write_all(entities, repo_path, is_original=False)

    # ===== Original Snapshots =====

    def save_original(self, entity: T, repo_path: Path) -> None:
        originals = self.load_all_originals(repo_path)
        entity_id = getattr(entity, self.identifier_field)

        originals = [e for e in originals if getattr(e, self.identifier_field) != entity_id]
        originals.append(entity)

        self._write_all(originals, repo_path, is_original=True)

    def load_original(self, identifier: str | int, repo_path: Path) -> T | None:
        originals = self.load_all_originals(repo_path)
        return next((e for e in originals if getattr(e, self.identifier_field) == identifier), None)

    def load_all_originals(self, repo_path: Path) -> list[T]:
        paths = self._get_paths(repo_path)
        return self._read_all(paths["originals_file"])

    # ===== Helper Methods =====

    def _read_all(self, file_path: Path) -> list[T]:
        """
        Read entities from JSON file.

        Note: This returns empty list if file doesn't exist.
        Subclasses should override to deserialize to proper entity type.
        """
        if not file_path.exists():
            return []

        with open(file_path) as f:
            data = json.load(f)

        # Return raw data - subclass will override to create instances
        return data  # type: ignore

    def _write_all(self, entities: list[T], repo_path: Path, is_original: bool) -> None:
        paths = self._get_paths(repo_path)
        file_path = paths["originals_file"] if is_original else paths["data_file"]

        file_path.parent.mkdir(parents=True, exist_ok=True)

        data = [asdict(e) for e in entities]
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    # ===== GitLab API Operations (abstract, implemented by entity-specific backends) =====
    # These will be implemented by LabelBackend, MilestoneBackend, etc.


class ConfigStorageBackend(StorageBackend[T], Generic[T]):
    """
    Storage backend for config-based entities.

    Stores entities in ~/.config/gitlab-issue-sync/config.toml (global storage).
    Accepts repo_path parameter for API consistency but uses config internally.
    """

    def __init__(self, entity_type: str, config_section: str):
        """
        Args:
            entity_type: Type name (e.g., "user_profile", "kanban_columns")
            config_section: Section in config (e.g., "username", "board.columns")
        """
        self.entity_type = entity_type
        self.config_section = config_section

    def _get_project_config(self, repo_path: Path) -> "ProjectConfig":
        from ..config import get_project_config_for_repo

        # Load config for this repo
        config = get_project_config_for_repo(repo_path)
        if not config:
            raise ValueError(f"No configuration found for repository at {repo_path}")
        return config

    # ===== Local Operations =====

    def save(self, entity: T, repo_path: Path) -> None:
        raise NotImplementedError("Subclass must implement save")

    def load(self, identifier: str | int, repo_path: Path) -> T | None:
        raise NotImplementedError("Subclass must implement load")

    def load_all(self, repo_path: Path) -> list[T]:
        raise NotImplementedError("Subclass must implement load_all")

    def delete(self, identifier: str | int, repo_path: Path) -> None:
        raise NotImplementedError("Subclass must implement delete")

    # ===== Original Snapshots =====

    def save_original(self, entity: T, repo_path: Path) -> None:
        raise NotImplementedError("Subclass must implement save_original")

    def load_original(self, identifier: str | int, repo_path: Path) -> T | None:
        raise NotImplementedError("Subclass must implement load_original")

    def load_all_originals(self, repo_path: Path) -> list[T]:
        raise NotImplementedError("Subclass must implement load_all_originals")

    # ===== GitLab API Operations =====

    def fetch_from_gitlab(self, project, repo_path: Path) -> list[T]:
        raise NotImplementedError("Subclass must implement fetch_from_gitlab")

    def create_on_gitlab(self, entity: T, project) -> int:
        raise NotImplementedError("Subclass must implement create_on_gitlab")

    def update_on_gitlab(self, entity: T, project) -> None:
        raise NotImplementedError("Subclass must implement update_on_gitlab")

    def delete_on_gitlab(self, entity: T, project) -> None:
        raise NotImplementedError("Subclass must implement delete_on_gitlab")


class MarkdownStorageBackend(StorageBackend[T], Generic[T]):
    """
    Storage backend for markdown-based individual files.

    Each entity is stored in its own .md file with YAML frontmatter.
    Used for entities like Issue and Milestone where each item is a separate document.

    Subclasses should configure:
    - base_dir: Base directory for entities (e.g., ".issues" or ".issues/.milestones")
    - use_state_dirs: Whether to use state-based subdirectories (e.g., open/closed)
    - originals_subpath: Subpath for original snapshots (e.g., ".sync/originals")
    """

    # Class properties to be set by subclasses
    base_dir: str = ".issues"
    use_state_dirs: bool = False  # Whether to organize by state (open/closed)
    originals_subpath: str = ".sync/originals"

    def _get_entity_dir(self, repo_path: Path, state: str | None = None) -> Path:
        base = repo_path / self.base_dir
        if self.use_state_dirs and state:
            return base / state
        return base

    def _get_originals_dir(self, repo_path: Path) -> Path:
        return repo_path / self.base_dir / self.originals_subpath

    def _get_file_path(self, entity: T, repo_path: Path) -> Path:
        state = getattr(entity, 'state', None) if self.use_state_dirs else None
        entity_dir = self._get_entity_dir(repo_path, state)
        return entity_dir / entity.filename

    def _get_original_path(self, entity: T, repo_path: Path) -> Path:
        originals_dir = self._get_originals_dir(repo_path)
        return originals_dir / entity.filename

    def _find_file(self, identifier: int | str, repo_path: Path) -> Path | None:
        if self.use_state_dirs:
            # Check both state directories
            for state in [ISSUE_STATE_OPENED, ISSUE_STATE_CLOSED]:
                entity_dir = self._get_entity_dir(repo_path, state)
                file_path = entity_dir / f"{identifier}.md"
                if file_path.exists():
                    return file_path
        else:
            # Check single directory
            entity_dir = self._get_entity_dir(repo_path)
            file_path = entity_dir / f"{identifier}.md"
            if file_path.exists():
                return file_path
        return None

    # Abstract methods for subclasses to implement
    @abstractmethod
    def _read_one(self, file_path: Path) -> T:
        pass

    @abstractmethod
    def _write_one(self, entity: T, file_path: Path) -> None:
        pass

    # ===== Local Operations =====

    def save(self, entity: T, repo_path: Path) -> None:
        # If using state directories, check for state transitions and clean up old files
        if self.use_state_dirs:
            identifier = entity.get_identifier()
            current_state = getattr(entity, 'state', None)

            # Find if entity exists in a different state directory
            old_file = self._find_file(identifier, repo_path)
            if old_file:
                # Check if state changed by looking at the old file's directory
                old_state = old_file.parent.name
                if old_state != current_state:
                    # State changed - delete old file
                    old_file.unlink()

        # Get new file path and save
        file_path = self._get_file_path(entity, repo_path)

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize and write
        self._write_one(entity, file_path)

    def load(self, identifier: int | str, repo_path: Path) -> T | None:
        file_path = self._find_file(identifier, repo_path)
        if not file_path:
            return None

        return self._read_one(file_path)

    def load_all(self, repo_path: Path) -> list[T]:
        entities = []

        if self.use_state_dirs:
            # Load from both opened and closed directories
            for state in [ISSUE_STATE_OPENED, ISSUE_STATE_CLOSED]:
                entity_dir = self._get_entity_dir(repo_path, state)
                if not entity_dir.exists():
                    continue

                for file_path in entity_dir.glob("*.md"):
                    entity = self._read_one(file_path)
                    entities.append(entity)
        else:
            # Load from single directory
            entity_dir = self._get_entity_dir(repo_path)
            if entity_dir.exists():
                for file_path in entity_dir.glob("*.md"):
                    entity = self._read_one(file_path)
                    entities.append(entity)

        return entities

    def delete(self, identifier: str | int, repo_path: Path) -> None:
        file_path = self._find_file(identifier, repo_path)
        if file_path and file_path.exists():
            file_path.unlink()

    # ===== Original Snapshots =====

    def save_original(self, entity: T, repo_path: Path) -> None:
        original_path = self._get_original_path(entity, repo_path)

        # Ensure directory exists
        original_path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize and write
        self._write_one(entity, original_path)

    def load_original(self, identifier: int | str, repo_path: Path) -> T | None:
        originals_dir = self._get_originals_dir(repo_path)
        if not originals_dir.exists():
            return None

        # Find by identifier
        for file_path in originals_dir.glob("*.md"):
            entity = self._read_one(file_path)
            if entity.get_identifier() == identifier:
                return entity

        return None

    def load_all_originals(self, repo_path: Path) -> list[T]:
        originals_dir = self._get_originals_dir(repo_path)
        if not originals_dir.exists():
            return []

        originals = []
        for file_path in originals_dir.glob("*.md"):
            entity = self._read_one(file_path)
            originals.append(entity)

        return originals

    def update_on_gitlab(self, entity: T, project) -> None:
        raise NotImplementedError("Subclass must implement update_on_gitlab")

    def delete_on_gitlab(self, entity: T, project) -> None:
        raise NotImplementedError("Subclass must implement delete_on_gitlab")
