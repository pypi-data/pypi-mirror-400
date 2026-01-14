"""Milestone entity and backend."""

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import yaml

from .base import MarkdownStorageBackend, Storable
from .exceptions import StorageError


@dataclass
class Milestone(Storable):
    """GitLab project milestone with local-first sync."""

    title: str
    description: str | None = None
    state: str = "active"  # "active" or "closed"
    due_date: str | None = None  # ISO 8601 date string
    start_date: str | None = None  # ISO 8601 date string
    created_at: datetime | None = None
    updated_at: datetime | None = None
    web_url: str | None = None

    def get_identifier(self) -> str:
        return self.title

    @property
    def filename(self) -> str:
        """Get the filename for this milestone (sanitized title)."""
        # Sanitize title for filesystem (replace spaces and special chars with underscores)
        import re

        safe_title = re.sub(r'[^\w\s-]', '', self.title)  # Remove special chars except spaces and hyphens
        safe_title = re.sub(r'[-\s]+', '_', safe_title)  # Replace spaces/hyphens with underscores
        return f"{safe_title}.md"

    def compute_content_hash(self) -> str:
        """Hash title, description, state, due_date (exclude status, remote_id, timestamps)."""
        data = {
            "title": self.title,
            "description": self.description,
            "state": self.state,
            "due_date": self.due_date,
            "start_date": self.start_date,
        }
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    # ===== Instance Methods (Business Logic) =====

    def save(self, repo_path: Path | None = None) -> None:
        """
        Save this milestone to local storage.

        Args:
            repo_path: Path to repository root
        """
        if not self.backend:
            raise StorageError("Milestone backend not configured")

        self.backend.save(self, repo_path or Path.cwd())

    def delete(self, repo_path: Path | None = None) -> None:
        """
        Mark this milestone as deleted (will be removed on next push).

        Args:
            repo_path: Path to repository root
        """
        self.status = "deleted"
        self.save(repo_path)

    def update(
        self,
        description: str | None = None,
        state: str | None = None,
        due_date: str | None = None,
        start_date: str | None = None,
        repo_path: Path | None = None,
    ) -> None:
        """
        Update milestone properties.

        Args:
            description: New description
            state: New state ("active" or "closed")
            due_date: New due date (ISO 8601)
            start_date: New start date (ISO 8601)
            repo_path: Path to repository root
        """
        if description is not None:
            self.description = description
        if state is not None:
            self.state = state
        if due_date is not None:
            self.due_date = due_date
        if start_date is not None:
            self.start_date = start_date

        self.status = "modified"
        self.save(repo_path)

    def close(self, repo_path: Path | None = None) -> None:
        """
        Close this milestone.

        Args:
            repo_path: Path to repository root
        """
        self.state = "closed"
        self.status = "modified"
        self.save(repo_path)

    @classmethod
    def create(
        cls,
        title: str,
        description: str | None = None,
        due_date: str | None = None,
        start_date: str | None = None,
        repo_path: Path | None = None,
    ) -> "Milestone":
        """
        Create a new milestone locally (will be created on GitLab on next push).

        Args:
            title: Milestone title
            description: Milestone description
            due_date: Due date (ISO 8601 format)
            start_date: Start date (ISO 8601 format)
            repo_path: Path to repository root

        Returns:
            The created milestone
        """
        milestone = cls(
            title=title,
            description=description,
            due_date=due_date,
            start_date=start_date,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        milestone.status = "pending"
        milestone.save(repo_path)
        return milestone

    @classmethod
    def load(cls, title: str, repo_path: Path | None = None) -> "Milestone | None":
        """
        Load a milestone from local storage.

        Args:
            title: Milestone title
            repo_path: Path to repository root

        Returns:
            The milestone, or None if not found
        """
        if not cls.backend:
            raise StorageError("Milestone backend not configured")

        return cls.backend.load(title, repo_path or Path.cwd())

    @classmethod
    def list_all(cls, include_deleted: bool = False, repo_path: Path | None = None) -> list["Milestone"]:
        """
        List all milestones from local storage.

        Args:
            include_deleted: If True, include milestones marked as deleted
            repo_path: Path to repository root

        Returns:
            List of milestones
        """
        if not cls.backend:
            raise StorageError("Milestone backend not configured")

        milestones = cls.backend.load_all(repo_path or Path.cwd())

        if not include_deleted:
            milestones = [m for m in milestones if m.status != "deleted"]

        return milestones

    @classmethod
    def get_title_to_id_map(cls, repo_path: Path | None = None) -> dict[str, int]:
        """
        Get a mapping of milestone titles to GitLab IDs.

        Args:
            repo_path: Path to repository root

        Returns:
            Dict mapping milestone title to remote_id
        """
        milestones = cls.list_all(repo_path=repo_path)
        return {m.title: m.remote_id for m in milestones if m.remote_id}


class MilestoneBackend(MarkdownStorageBackend["Milestone"]):
    """
    Milestone-specific storage backend using markdown files.

    Stores milestones as individual markdown files with YAML frontmatter,
    allowing for rich formatted descriptions.
    """

    # Configure directory structure for milestones
    base_dir = ".issues/.milestones"
    use_state_dirs = False  # Milestones are not organized by state
    originals_subpath = ".sync/originals"

    def _find_file(self, identifier: int | str, repo_path: Path) -> Path | None:
        """
        Find milestone file by title using filename sanitization.

        Override base implementation to apply same filename sanitization
        as Milestone.filename property.
        """
        # Create temporary milestone to get sanitized filename
        temp_milestone = Milestone(title=str(identifier))
        entity_dir = self._get_entity_dir(repo_path)
        file_path = entity_dir / temp_milestone.filename

        if file_path.exists():
            return file_path
        return None

    def _read_one(self, file_path: Path) -> Milestone:
        """
        Parse a milestone from markdown file with YAML frontmatter.

        Format:
        ```
        ---
        title: Milestone 1
        state: active
        due_date: "2026-02-01"
        start_date: "2026-01-01"
        created_at: "2026-01-01T00:00:00+00:00"
        updated_at: "2026-01-01T00:00:00+00:00"
        web_url: "https://gitlab.com/..."
        status: synced
        remote_id: 1
        ---

        # Description

        Detailed milestone description with **markdown** formatting.
        ```
        """
        content = file_path.read_text(encoding="utf-8")

        # Split frontmatter and description
        if not content.startswith("---"):
            raise StorageError(f"Invalid milestone file format: {file_path}")

        parts = content.split("---", 2)
        if len(parts) < 3:
            raise StorageError(f"Invalid milestone file format: {file_path}")

        frontmatter_str = parts[1]
        description = parts[2].strip()

        # Parse YAML frontmatter
        frontmatter = yaml.safe_load(frontmatter_str) or {}

        # Separate Storable fields
        status = frontmatter.pop("status", "synced")
        remote_id = frontmatter.pop("remote_id", None)

        # Parse timestamps
        created_at = None
        if "created_at" in frontmatter and frontmatter["created_at"]:
            created_at = datetime.fromisoformat(str(frontmatter["created_at"]))

        updated_at = None
        if "updated_at" in frontmatter and frontmatter["updated_at"]:
            updated_at = datetime.fromisoformat(str(frontmatter["updated_at"]))

        # Create milestone
        milestone = Milestone(
            title=frontmatter["title"],
            description=description if description else None,
            state=frontmatter.get("state", "active"),
            due_date=frontmatter.get("due_date"),
            start_date=frontmatter.get("start_date"),
            created_at=created_at,
            updated_at=updated_at,
            web_url=frontmatter.get("web_url"),
        )

        # Set Storable fields
        milestone.status = status
        milestone.remote_id = remote_id

        return milestone

    def _write_one(self, milestone: Milestone, file_path: Path) -> None:
        """Serialize a milestone to markdown with YAML frontmatter."""
        # Build frontmatter
        frontmatter = {
            "title": milestone.title,
            "state": milestone.state,
        }

        if milestone.due_date:
            frontmatter["due_date"] = milestone.due_date
        if milestone.start_date:
            frontmatter["start_date"] = milestone.start_date
        if milestone.created_at:
            frontmatter["created_at"] = milestone.created_at.isoformat()
        if milestone.updated_at:
            frontmatter["updated_at"] = milestone.updated_at.isoformat()
        if milestone.web_url:
            frontmatter["web_url"] = milestone.web_url

        # Add sync metadata
        frontmatter["status"] = milestone.status
        if milestone.remote_id:
            frontmatter["remote_id"] = milestone.remote_id

        # Build markdown content
        yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        content = f"---\n{yaml_str}---\n\n{milestone.description or ''}\n"

        # Write to file (parent directory creation handled by parent class)
        file_path.write_text(content, encoding="utf-8")

    # ===== GitLab API Operations =====

    def fetch_from_gitlab(self, project, repo_path: Path, **kwargs) -> list[Milestone]:
        """Fetch all milestones from GitLab."""
        gl_milestones = project.milestones.list(get_all=True)

        milestones = []
        for gl_ms in gl_milestones:
            created_at = (
                datetime.fromisoformat(gl_ms.created_at.replace("Z", "+00:00")) if gl_ms.created_at else None
            )
            updated_at = (
                datetime.fromisoformat(gl_ms.updated_at.replace("Z", "+00:00")) if gl_ms.updated_at else None
            )
            milestone = Milestone(
                title=gl_ms.title,
                description=getattr(gl_ms, "description", None),
                state=getattr(gl_ms, "state", "active"),
                due_date=getattr(gl_ms, "due_date", None),
                start_date=getattr(gl_ms, "start_date", None),
                created_at=created_at,
                updated_at=updated_at,
                web_url=getattr(gl_ms, "web_url", None),
            )
            milestone.status = "synced"
            milestone.remote_id = gl_ms.id
            milestones.append(milestone)

        return milestones

    def create_on_gitlab(self, milestone: Milestone, project) -> int:
        """Create milestone on GitLab."""
        params = {
            "title": milestone.title,
        }
        if milestone.description:
            params["description"] = milestone.description
        if milestone.due_date:
            params["due_date"] = milestone.due_date
        if milestone.start_date:
            params["start_date"] = milestone.start_date

        gl_milestone = project.milestones.create(params)
        return gl_milestone.id

    def update_on_gitlab(self, milestone: Milestone, project) -> None:
        """Update milestone on GitLab."""
        gl_milestone = project.milestones.get(milestone.remote_id)

        if milestone.description is not None:
            gl_milestone.description = milestone.description
        if milestone.state:
            gl_milestone.state_event = "close" if milestone.state == "closed" else "activate"
        if milestone.due_date:
            gl_milestone.due_date = milestone.due_date
        if milestone.start_date:
            gl_milestone.start_date = milestone.start_date

        gl_milestone.save()

    def delete_on_gitlab(self, milestone: Milestone, project) -> None:
        """Delete milestone from GitLab."""
        if milestone.remote_id:
            try:
                gl_milestone = project.milestones.get(milestone.remote_id)
                gl_milestone.delete()
            except Exception:
                pass  # Already deleted


# ===== Assign Backend =====

Milestone.backend = MilestoneBackend()
