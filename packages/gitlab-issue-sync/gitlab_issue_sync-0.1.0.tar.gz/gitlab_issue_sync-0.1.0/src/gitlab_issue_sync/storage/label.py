"""Label entity and backend."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .base import JsonStorageBackend, Storable
from .exceptions import StorageError


@dataclass
class Label(Storable):
    """GitLab project label with local-first sync."""

    name: str
    color: str | None = None
    description: str | None = None

    def get_identifier(self) -> str:
        return self.name

    def compute_content_hash(self) -> str:
        """Hash name, color, description (exclude status, remote_id)."""
        data = {"name": self.name, "color": self.color, "description": self.description}
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    # ===== Instance Methods (Business Logic) =====

    def save(self, repo_path: Path | None = None) -> None:
        """
        Save this label to local storage.

        Args:
            repo_path: Path to repository root
        """
        if not self.backend:
            raise StorageError("Label backend not configured")

        self.backend.save(self, repo_path or Path.cwd())

    def delete(self, repo_path: Path | None = None) -> None:
        """
        Mark this label as deleted (will be removed on next push).

        Args:
            repo_path: Path to repository root
        """
        self.status = "deleted"
        self.save(repo_path)

    def update(self, color: str | None = None, description: str | None = None, repo_path: Path | None = None) -> None:
        """
        Update label properties.

        Args:
            color: New color (hex code)
            description: New description
            repo_path: Path to repository root
        """
        if color is not None:
            self.color = color
        if description is not None:
            self.description = description

        self.status = "modified"
        self.save(repo_path)

    @classmethod
    def create(
        cls,
        name: str,
        color: str | None = None,
        description: str | None = None,
        repo_path: Path | None = None
    ) -> "Label":
        """
        Create a new label locally (will be created on GitLab on next push).

        Args:
            name: Label name
            color: Label color (hex code)
            description: Label description
            repo_path: Path to repository root

        Returns:
            The created label
        """
        label = cls(name=name, color=color, description=description)
        label.status = "pending"
        label.save(repo_path)
        return label

    @classmethod
    def load(cls, name: str, repo_path: Path | None = None) -> "Label | None":
        """
        Load a label from local storage.

        Args:
            name: Label name
            repo_path: Path to repository root

        Returns:
            The label, or None if not found
        """
        if not cls.backend:
            raise StorageError("Label backend not configured")

        return cls.backend.load(name, repo_path or Path.cwd())

    @classmethod
    def list_all(cls, include_deleted: bool = False, repo_path: Path | None = None) -> list["Label"]:
        """
        List all labels from local storage.

        Args:
            include_deleted: If True, include labels marked as deleted
            repo_path: Path to repository root

        Returns:
            List of labels
        """
        if not cls.backend:
            raise StorageError("Label backend not configured")

        labels = cls.backend.load_all(repo_path or Path.cwd())

        if not include_deleted:
            labels = [label for label in labels if label.status != "deleted"]

        return labels

    @classmethod
    def get_colors_map(cls, repo_path: Path | None = None) -> dict[str, str]:
        """
        Get a mapping of label names to colors.

        Args:
            repo_path: Path to repository root

        Returns:
            Dict mapping label name to hex color
        """
        labels = cls.list_all(repo_path=repo_path)
        return {label.name: label.color for label in labels if label.color}

    @staticmethod
    def split_semantic_and_kanban(
        labels: list[str],
        repo_path: Path | None = None
    ) -> tuple[list[str], list[str]]:
        """
        Split labels into semantic and Kanban column labels in a single pass.

        Semantic labels are regular project labels (bug, feature, priority, etc.)
        while Kanban labels are board column labels (backlog, todo, in-progress, done).

        Args:
            labels: List of all label names
            repo_path: Path to repository root (optional)

        Returns:
            Tuple of (semantic_labels, kanban_labels)

        Note:
            This method performs a single iteration over labels, avoiding duplicate filtering.
            Fetches kanban columns automatically from KanbanColumn.get_column_names().
            TODO: Refactor cli.py to use this method instead of inline filtering
                  (appears in list command line ~918, labels command line ~1781)
        """
        from .config import KanbanColumn

        kanban_columns = KanbanColumn.get_column_names(repo_path)
        kanban_set = set(kanban_columns)  # O(1) lookup

        semantic = []
        kanban = []

        for label in labels:
            if label in kanban_set:
                kanban.append(label)
            else:
                semantic.append(label)

        return semantic, kanban


class LabelBackend(JsonStorageBackend["Label"]):
    """Label-specific storage backend."""

    def __init__(self):
        super().__init__(entity_type="labels", identifier_field="name")

    def _read_all(self, file_path: Path) -> list[Label]:
        """Deserialize JSON to Label instances."""
        if not file_path.exists():
            return []

        with open(file_path) as f:
            data = json.load(f)

        labels = []
        for item in data:
            # Separate Storable fields from Label fields
            status = item.pop("status", "synced")
            remote_id = item.pop("remote_id", None)

            # Create label with Label-specific fields only
            label = Label(**item)

            # Set Storable fields
            label.status = status
            label.remote_id = remote_id

            labels.append(label)

        return labels

    # ===== GitLab API Operations =====

    def fetch_from_gitlab(self, project, repo_path: Path, **kwargs) -> list[Label]:
        """Fetch all labels from GitLab."""
        gl_labels = project.labels.list(get_all=True)

        labels = []
        for gl_label in gl_labels:
            label = Label(
                name=gl_label.name,
                color=getattr(gl_label, "color", None),
                description=getattr(gl_label, "description", None),
            )
            label.status = "synced"
            label.remote_id = gl_label.id
            labels.append(label)

        return labels

    def create_on_gitlab(self, label: Label, project) -> int:
        """Create label on GitLab."""
        gl_label = project.labels.create({"name": label.name, "color": label.color, "description": label.description})
        return gl_label.id

    def update_on_gitlab(self, label: Label, project) -> None:
        """Update label on GitLab."""
        gl_label = project.labels.get(label.remote_id)
        if label.color:
            gl_label.color = label.color
        if label.description is not None:
            gl_label.description = label.description
        gl_label.save()

    def delete_on_gitlab(self, label: Label, project) -> None:
        """Delete label from GitLab."""
        if label.remote_id:
            try:
                gl_label = project.labels.get(label.remote_id)
                gl_label.delete()
            except Exception:
                pass  # Already deleted


# ===== Assign Backend =====

Label.backend = LabelBackend()
