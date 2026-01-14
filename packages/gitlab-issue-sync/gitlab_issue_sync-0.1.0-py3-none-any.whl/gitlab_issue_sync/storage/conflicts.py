"""Conflict state management for issue synchronization.

This module provides infrastructure for:
- Persisting conflict state in .issues/.sync/conflicts.json
- Caching remote versions for offline resolution
- Auto-resolution stubs (to be implemented in child issue)

See issue #170 for requirements and design.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from .base import JsonStorageBackend, Storable
from .exceptions import StorageError
from .utils import parse_issue, serialize_issue

if False:  # TYPE_CHECKING
    from .issue import Issue

logger = logging.getLogger(__name__)


@dataclass
class Conflict(Storable):
    """Represents a conflict between local and remote versions of an issue.

    A conflict occurs when both local and remote have been modified since
    the last sync (BOTH_MODIFIED state).

    Usage:
        # Create a conflict (fields are computed at creation time)
        conflict = Conflict(
            issue_iid=42,
            fields=["title", "description"],
        )

        # Save with remote cache
        conflict.save_with_remote(remote_issue, repo_path)

        # Later: attempt auto-resolution
        merged = conflict.attempt_auto_resolution(repo_path)
    """

    issue_iid: int  # Conflicts only make sense for real issues, not temporary IDs
    fields: list[str] = field(default_factory=list)  # Which fields conflict
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def get_identifier(self) -> int:
        return self.issue_iid

    def compute_content_hash(self) -> str:
        """Hash issue_iid, fields, detected_at."""
        data = {
            "issue_iid": self.issue_iid,
            "fields": sorted(self.fields),
            "detected_at": self.detected_at.isoformat(),
        }
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    # ===== Remote Cache Operations =====

    def save_with_remote(self, remote: "Issue", repo_path: Path) -> None:
        """Save conflict and cache the remote version for offline resolution.

        Args:
            remote: The remote issue to cache
            repo_path: Path to repository root
        """
        # Save conflict metadata
        self.save(repo_path)

        # Cache remote version
        cache_dir = self._get_cache_dir(repo_path)
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_path = cache_dir / f"{self.issue_iid}_remote.md"
        content = serialize_issue(remote)
        cache_path.write_text(content, encoding="utf-8")

    def load_cached_remote(self, repo_path: Path) -> "Issue | None":
        """Load cached remote version for offline resolution.

        Returns:
            The cached remote issue, or None if not found
        """
        cache_path = self._get_cache_dir(repo_path) / f"{self.issue_iid}_remote.md"

        if not cache_path.exists():
            return None

        try:
            content = cache_path.read_text(encoding="utf-8")
            return parse_issue(content)
        except Exception as e:
            logger.warning(f"Error loading cached remote for issue {self.issue_iid}: {e}")
            return None

    def delete_cached_remote(self, repo_path: Path) -> bool:
        """Delete cached remote version.

        Returns:
            True if file was deleted, False if not found
        """
        cache_path = self._get_cache_dir(repo_path) / f"{self.issue_iid}_remote.md"
        if cache_path.exists():
            cache_path.unlink()
            return True
        return False

    @staticmethod
    def _get_cache_dir(repo_path: Path) -> Path:
        """Get path to conflicts cache directory."""
        return repo_path / ".issues" / ".sync" / "conflicts"

    # ===== Field-Level Resolution Helpers =====

    # Fields that are lists requiring set comparison
    _LIST_FIELDS = frozenset(("labels", "assignees"))

    @staticmethod
    def _field_changed(field: str, issue: "Issue", original: "Issue") -> bool:
        """Check if a specific field changed between issue and original."""
        issue_val = getattr(issue, field)
        original_val = getattr(original, field)

        if field in Conflict._LIST_FIELDS:
            return set(issue_val) != set(original_val)

        if field == "comments":
            def comment_key(c):
                return (c.author, c.body)
            return {comment_key(c) for c in issue_val} != {comment_key(c) for c in original_val}

        if field == "links":
            def link_key(link):
                return (link.target_issue_iid, link.link_type)
            return {link_key(link) for link in issue_val} != {link_key(link) for link in original_val}

        return issue_val != original_val

    def _merge_comments(
        self,
        local_comments: list,
        original_comments: list,
        remote_comments: list,
    ) -> list | None:
        """Merge comments using remote as source of truth, appending new local comments.

        Algorithm:
        1. Start with remote_comments as the base (remote is authoritative)
        2. Append local comments that are NEW (not in original) at the end

        New local comments are appended at the end - GitLab will assign proper
        timestamps when they're pushed.
        """
        def comment_signature(c):
            return (c.author, c.body)

        # Remote is the source of truth
        merged = list(remote_comments)

        # Find and append comments that are new locally (not in original = not yet synced)
        original_signatures = {comment_signature(c) for c in original_comments}

        for comment in local_comments:
            if comment_signature(comment) not in original_signatures:
                merged.append(comment)

        return merged

    def _merge_description(
        self,
        local_text: str,
        original_text: str,
        remote_text: str,
    ) -> str | None:
        """Three-way merge using git merge-file. Returns None if conflicts."""
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', suffix='.local', delete=False) as local_f, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.base', delete=False) as base_f, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.remote', delete=False) as remote_f:

            local_f.write(local_text)
            base_f.write(original_text)
            remote_f.write(remote_text)

            local_path = Path(local_f.name)
            base_path = Path(base_f.name)
            remote_path = Path(remote_f.name)

        try:
            result = subprocess.run(
                ["git", "merge-file", "-p", str(local_path), str(base_path), str(remote_path)],
                capture_output=True,
                text=True,
            )

            # git merge-file returns 0 for clean merge, >0 for number of conflicts
            if result.returncode != 0:
                return None

            return result.stdout

        except (FileNotFoundError, subprocess.SubprocessError) as e:
            logger.warning(f"git merge-file failed: {e}")
            return None
        finally:
            local_path.unlink(missing_ok=True)
            base_path.unlink(missing_ok=True)
            remote_path.unlink(missing_ok=True)

    @staticmethod
    def _copy_field(field: str, source: "Issue", target: "Issue") -> None:
        """Copy a field value from source to target issue."""
        value = getattr(source, field)
        # Make copies of mutable types to avoid shared references
        if isinstance(value, list):
            value = list(value)
        setattr(target, field, value)

    # ===== Resolution =====

    def attempt_auto_resolution(
        self,
        repo_path: Path,
        remote: "Issue | None" = None,
    ) -> "Issue | None":
        """Attempt automatic conflict resolution.

        For each conflicting field in self.fields:
        - If changed only on one side → take that side's value
        - If changed on both sides → use _merge_{field} method if exists, else fail

        Mergeable fields (both sides can change):
        - comments: append-only merge
        - description: git merge-file three-way merge

        Args:
            repo_path: Path to repository root
            remote: Remote issue (if not provided, loads from cache)

        Returns:
            Merged Issue if auto-resolved, None if manual resolution needed
        """
        from copy import deepcopy

        from .issue import Issue

        # Load the three versions
        local = Issue.load(self.issue_iid, repo_path)
        original = Issue.backend.load_original(self.issue_iid, repo_path)
        if remote is None:
            remote = self.load_cached_remote(repo_path)

        if not all([local, original, remote]):
            logger.warning(f"Cannot attempt auto-resolution for {self.issue_iid}: missing version(s)")
            return None

        # Start with a copy of local
        merged = deepcopy(local)

        # Process each conflicting field
        for field_name in self.fields:
            local_changed = self._field_changed(field_name, local, original)
            remote_changed = self._field_changed(field_name, remote, original)

            if local_changed and remote_changed:
                # Both sides modified - try method dispatch for mergeable fields
                merge_method = getattr(self, f"_merge_{field_name}", None)
                if merge_method is None:
                    logger.info(
                        f"Issue {self.issue_iid}: field '{field_name}' modified on both sides, no merge strategy"
                    )
                    return None

                result = merge_method(*(getattr(issue, field_name) for issue in (local, original, remote)))
                if result is None:
                    logger.info(f"Issue {self.issue_iid}: field '{field_name}' merge failed")
                    return None
                setattr(merged, field_name, result)

            elif remote_changed:
                # Only remote changed, take remote value
                self._copy_field(field_name, remote, merged)

            # If only local changed (or neither), merged already has the right value

        logger.info(f"Issue {self.issue_iid}: auto-resolved conflicts in fields: {self.fields}")
        return merged

    # ===== Instance Methods =====

    def save(self, repo_path: Path | None = None) -> None:
        """Save this conflict to local storage."""
        if not self.backend:
            raise StorageError("Conflict backend not configured")
        self.backend.save(self, repo_path or Path.cwd())

    def delete(self, repo_path: Path | None = None) -> None:
        """Delete this conflict and its cached remote."""
        repo_path = repo_path or Path.cwd()

        # Delete cached remote
        self.delete_cached_remote(repo_path)

        # Delete from storage
        if self.backend:
            self.backend.delete(self.issue_iid, repo_path)

    @classmethod
    def load(cls, issue_iid: int, repo_path: Path | None = None) -> "Conflict | None":
        """Load a conflict from local storage."""
        if not cls.backend:
            raise StorageError("Conflict backend not configured")
        return cls.backend.load(issue_iid, repo_path or Path.cwd())

    @classmethod
    def list_all(cls, repo_path: Path | None = None) -> list["Conflict"]:
        """List all conflicts sorted by detection time."""
        if not cls.backend:
            raise StorageError("Conflict backend not configured")
        conflicts = cls.backend.load_all(repo_path or Path.cwd())
        return sorted(conflicts, key=lambda c: c.detected_at)

    @classmethod
    def has(cls, issue_iid: int, repo_path: Path | None = None) -> bool:
        """Check if an issue has an unresolved conflict."""
        return cls.load(issue_iid, repo_path) is not None

    @classmethod
    def clear(cls, issue_iid: int, repo_path: Path | None = None) -> None:
        """Clear conflict state after successful push.

        Unlike delete(), this doesn't fail if conflict doesn't exist.
        Used after successful push to ensure clean state.
        """
        repo_path = repo_path or Path.cwd()
        conflict = cls.load(issue_iid, repo_path)
        if conflict:
            conflict.delete(repo_path)


class ConflictBackend(JsonStorageBackend["Conflict"]):
    """Conflict-specific storage backend.

    Stores conflicts in .issues/.sync/conflicts.json
    """

    def __init__(self):
        super().__init__(entity_type="sync/conflicts", identifier_field="issue_iid")

    def _get_paths(self, repo_path: Path) -> dict[str, Path]:
        """Override to use .issues/.sync/ directory."""
        base = repo_path / ".issues" / ".sync"
        return {
            "data_file": base / "conflicts.json",
            "originals_file": base / "conflicts_originals.json",  # Not really used
        }

    def _read_all(self, file_path: Path) -> list[Conflict]:
        """Deserialize JSON to Conflict instances."""
        if not file_path.exists():
            return []

        with open(file_path) as f:
            data = json.load(f)

        conflicts = []
        for item in data:
            try:
                # Parse datetime
                detected_at = datetime.fromisoformat(item["detected_at"])

                conflict = Conflict(
                    issue_iid=item["issue_iid"],
                    fields=item.get("fields", []),
                    detected_at=detected_at,
                )

                # Set Storable fields
                conflict.status = item.get("status", "synced")
                conflict.remote_id = item.get("remote_id")

                conflicts.append(conflict)
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping invalid conflict entry: {e}")
                continue

        return conflicts

    def _write_all(self, entities: list[Conflict], repo_path: Path, is_original: bool) -> None:
        """Serialize Conflict instances to JSON."""
        paths = self._get_paths(repo_path)
        file_path = paths["originals_file"] if is_original else paths["data_file"]

        file_path.parent.mkdir(parents=True, exist_ok=True)

        data = []
        for conflict in entities:
            data.append({
                "issue_iid": conflict.issue_iid,
                "fields": conflict.fields,
                "detected_at": conflict.detected_at.isoformat(),
                "status": conflict.status,
                "remote_id": conflict.remote_id,
            })

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    # ===== GitLab API Operations (not applicable for conflicts) =====

    def fetch_from_gitlab(self, project, repo_path: Path, **kwargs) -> list[Conflict]:
        """Conflicts are local-only, no GitLab fetch."""
        return []

    def create_on_gitlab(self, entity: Conflict, project) -> int:
        """Conflicts are local-only, no GitLab create."""
        raise NotImplementedError("Conflicts are local-only")

    def update_on_gitlab(self, entity: Conflict, project) -> None:
        """Conflicts are local-only, no GitLab update."""
        raise NotImplementedError("Conflicts are local-only")

    def delete_on_gitlab(self, entity: Conflict, project) -> None:
        """Conflicts are local-only, no GitLab delete."""
        raise NotImplementedError("Conflicts are local-only")


# ===== Assign Backend =====

Conflict.backend = ConflictBackend()
