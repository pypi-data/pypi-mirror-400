"""Config-stored entities (KanbanColumn)."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .base import ConfigStorageBackend, Storable
from .exceptions import StorageError


@dataclass
class KanbanColumn(Storable):
    """Kanban board column (ordered workflow stage)."""

    name: str
    position: int  # Order in workflow (0, 1, 2, ...)

    def get_identifier(self) -> int:
        return self.position

    def compute_content_hash(self) -> str:
        """Hash name and position (exclude status, remote_id)."""
        data = {"name": self.name, "position": self.position}
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    @classmethod
    def get_columns(cls, repo_path: Path | None = None) -> list["KanbanColumn"]:
        """
        Get all kanban columns from local cache.

        Args:
            repo_path: Path to repository root

        Returns:
            List of KanbanColumn objects ordered by position

        Raises:
            StorageError: If backend not configured or no columns found
        """
        if not cls.backend:
            raise StorageError("KanbanColumn backend not configured")

        columns = cls.backend.load_all(repo_path or Path.cwd())
        if not columns:
            raise StorageError("No kanban board columns configured. Run 'gl-issue-sync init' first.")

        return sorted(columns, key=lambda c: c.position)

    @classmethod
    def get_column_names(cls, repo_path: Path | None = None) -> list[str]:
        """
        Get list of column names in order.

        Args:
            repo_path: Path to repository root

        Returns:
            List of column names ordered by position
        """
        columns = cls.get_columns(repo_path)
        return [col.name for col in columns]

    @classmethod
    def get_next(
        cls,
        current_name: str | None,
        current_state: str,
        repo_path: Path | None = None
    ) -> tuple[str | None, str | None]:
        """
        Get next column in workflow progression.

        Args:
            current_name: Current column name (None if not in any column)
            current_state: Current issue state ("opened" or "closed")
            repo_path: Path to repository root

        Returns:
            Tuple of (column_name, new_state):
                - (column_name, None): Move to column_name, keep state
                - (None, "closed"): Close issue (moved past last column)
                - (last_column, "opened"): Re-open to last column (if currently closed)

        Examples:
            - get_next(None, "opened") -> ("ToDo", None) - Enter first column
            - get_next("ToDo", "opened") -> ("In Progress", None) - Progress forward
            - get_next("Done", "opened") -> (None, "closed") - Close after last column
            - get_next(None, "closed") -> ("Done", "opened") - Re-open to last column
        """
        columns = cls.get_columns(repo_path)

        # If closed, re-open to last column
        if current_state == "closed":
            if columns:
                return (columns[-1].name, "opened")
            else:
                return (None, "opened")

        # If not in any column, move to first column
        if not current_name:
            if columns:
                return (columns[0].name, None)
            else:
                return (None, None)

        # Find current position
        current_pos = next((col.position for col in columns if col.name == current_name), None)
        if current_pos is None:
            # Current column not found, move to first column
            if columns:
                return (columns[0].name, None)
            else:
                return (None, None)

        # Move to next position
        next_pos = current_pos + 1
        if next_pos < len(columns):
            # Move to next column
            return (columns[next_pos].name, None)
        else:
            # Past last column - close issue
            return (None, "closed")

    @classmethod
    def get_previous(
        cls,
        current_name: str | None,
        current_state: str,
        repo_path: Path | None = None
    ) -> tuple[str | None, str | None]:
        """
        Get previous column in workflow (moving backward).

        Args:
            current_name: Current column name (None if not in any column)
            current_state: Current issue state ("opened" or "closed")
            repo_path: Path to repository root

        Returns:
            Tuple of (column_name, new_state):
                - (column_name, None): Move to column_name, keep state
                - (None, None): Remove from all columns (moved before first)
                - (last_column, "opened"): Re-open to last column (if currently closed)

        Examples:
            - get_previous("In Progress", "opened") -> ("ToDo", None) - Go back
            - get_previous("ToDo", "opened") -> (None, None) - Remove from columns
            - get_previous(None, "opened") -> (None, None) - Already not in column
            - get_previous(None, "closed") -> ("Done", "opened") - Re-open to last
        """
        columns = cls.get_columns(repo_path)

        # If closed, re-open to last column
        if current_state == "closed":
            if columns:
                return (columns[-1].name, "opened")
            else:
                return (None, "opened")

        # If not in any column, can't go back further
        if not current_name:
            return (None, None)

        # Find current position
        current_pos = next((col.position for col in columns if col.name == current_name), None)
        if current_pos is None:
            # Current column not found, remove from all columns
            return (None, None)

        # Move to previous position
        prev_pos = current_pos - 1
        if prev_pos >= 0:
            # Move to previous column
            return (columns[prev_pos].name, None)
        else:
            # Before first column - remove from all columns
            return (None, None)

    @classmethod
    def validate_and_suggest(
        cls,
        column_name: str,
        repo_path: Path | None = None
    ) -> tuple[bool, str | None]:
        """
        Validate column name and provide suggestion if invalid.

        Args:
            column_name: Column name to validate
            repo_path: Path to repository root

        Returns:
            Tuple of (is_valid, suggestion):
                - (True, None): Valid column name
                - (False, suggestion): Invalid, with suggested column name (or None)

        Uses simple case-insensitive matching and basic fuzzy matching.
        """
        columns = cls.get_columns(repo_path)
        column_names = [col.name for col in columns]

        # Exact match (case-sensitive)
        if column_name in column_names:
            return (True, None)

        # Case-insensitive match
        lower_name = column_name.lower()
        for name in column_names:
            if name.lower() == lower_name:
                return (False, name)  # Suggest correct casing

        # Simple fuzzy match: check if it's a substring (case-insensitive)
        for name in column_names:
            if lower_name in name.lower() or name.lower() in lower_name:
                return (False, name)

        # No good match found
        return (False, None)


class KanbanColumnBackend(ConfigStorageBackend["KanbanColumn"]):
    """Backend for kanban columns stored in config."""

    def __init__(self):
        super().__init__(entity_type="kanban_columns", config_section="board.columns")

    # ===== Local Operations =====

    # def save(self, entity: "KanbanColumn", repo_path: Path) -> None:
    #     """Save kanban column to config."""
    #     from ..config import BoardConfig, save_project_config

    #     config = self._get_project_config(repo_path)

    #     # Update board config with new/updated column
    #     if config.board is None:
    #         config.board = BoardConfig(columns=[])

    #     # Find and update or append
    #     existing_idx = next((i for i, col in enumerate(config.board.columns) if i == entity.position), None)

    #     if existing_idx is not None:
    #         config.board.columns[existing_idx] = entity.name
    #     else:
    #         # Extend list if needed
    #         while len(config.board.columns) <= entity.position:
    #             config.board.columns.append("")
    #         config.board.columns[entity.position] = entity.name

    #     save_project_config(config)

    # def load(self, identifier: str | int, repo_path: Path) -> "KanbanColumn | None":
    #     """Load column by position."""
    #     columns = self.load_all(repo_path)
    #     return next((c for c in columns if c.position == identifier), None)

    def load_all(self, repo_path: Path) -> list["KanbanColumn"]:
        """Load all kanban columns from config."""

        config = self._get_project_config(repo_path)

        if not config.board or not config.board.columns:
            return []

        columns = []
        for i, name in enumerate(config.board.columns):
            column = KanbanColumn(name=name, position=i)
            column.status = "synced"
            columns.append(column)

        return columns

    # def delete(self, identifier: str | int, repo_path: Path) -> None:
    #     """Delete kanban column from config."""
    #     from ..config import save_project_config

    #     config = self._get_project_config(repo_path)

    #     if config.board and config.board.columns:
    #         # Remove column at position
    #         if 0 <= identifier < len(config.board.columns):
    #             config.board.columns.pop(identifier)
    #             save_project_config(config)

    # ===== Original Snapshots =====
    # For KanbanColumn, we don't maintain separate originals

    def save_original(self, entity: "KanbanColumn", repo_path: Path) -> None:
        """No-op: KanbanColumn doesn't need separate original snapshots."""
        pass

    def load_original(self, identifier: str | int, repo_path: Path) -> "KanbanColumn | None":
        """Return current column as original (no separate snapshots)."""
        columns = self.load_all(repo_path)
        return next((c for c in columns if c.position == identifier), None)

    def load_all_originals(self, repo_path: Path) -> list["KanbanColumn"]:
        """Return current columns as originals (no separate snapshots)."""
        return self.load_all(repo_path)

    # ===== GitLab API Operations =====

    def fetch_from_gitlab(self, project, repo_path: Path) -> list["KanbanColumn"]:
        """Fetch board columns from GitLab."""
        boards = project.boards.list()
        if not boards:
            return []

        board = boards[0]
        lists = board.lists.list()

        columns = []
        for i, board_list in enumerate(lists):
            # board_list.label is a dict with 'name' key
            label_name = board_list.label["name"] if isinstance(board_list.label, dict) else board_list.label.name
            column = KanbanColumn(name=label_name, position=i)
            column.status = "synced"
            column.remote_id = board_list.id
            columns.append(column)

        return columns

    def create_on_gitlab(self, entity: "KanbanColumn", project) -> int:
        """Board columns are managed via board configuration, not created individually."""
        raise NotImplementedError("Kanban columns are managed via board configuration")

    def update_on_gitlab(self, entity: "KanbanColumn", project) -> None:
        """Board columns are managed via board configuration, not updated individually."""
        raise NotImplementedError("Kanban columns are managed via board configuration")

    def delete_on_gitlab(self, entity: "KanbanColumn", project) -> None:
        """Board columns are managed via board configuration, not deleted individually."""
        raise NotImplementedError("Kanban columns are managed via board configuration")

    # ===== Helper Methods =====

    def get_column_names(self, repo_path: Path) -> list[str]:
        """Get ordered list of column names."""
        columns = self.load_all(repo_path)
        columns.sort(key=lambda c: c.position)
        return [c.name for c in columns]


# ===== Assign Backends =====

KanbanColumn.backend = KanbanColumnBackend()
