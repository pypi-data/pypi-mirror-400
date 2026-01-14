"""Display utilities for CLI output."""

from rich.console import Console

console = Console()
console_err = Console(stderr=True)


def format_checkboxes(text: str) -> str:
    """Replace markdown checkbox syntax with emoji checkboxes, preserving code blocks."""
    # Split by code blocks (triple backticks)
    parts = text.split("```")

    # Format only parts outside code blocks (even indices)
    # Odd indices are inside code blocks and should be preserved
    for i in range(len(parts)):
        if i % 2 == 0:  # Outside code block
            parts[i] = parts[i].replace("- [x]", "- ✅")
            parts[i] = parts[i].replace("- [X]", "- ✅")
            parts[i] = parts[i].replace("- [ ]", "- ◻️")

    # Rejoin with backticks
    return "```".join(parts)


# Import display functions from submodules
from .board import display_board_move_result
from .conflicts import display_conflict_details, display_conflicts
from .issue import display_issue, display_issue_short, display_issues_table
from .metadata import (
    display_label_list,
    display_label_operation_result,
    display_milestone_list,
    display_milestone_operation_result,
)
from .misc import display_close_result, display_comment_result
from .sync import display_push_conflicts, display_push_result, display_sync_result

__all__ = [
    "console",
    "console_err",
    "format_checkboxes",
    "display_board_move_result",
    "display_close_result",
    "display_comment_result",
    "display_issue",
    "display_issue_short",
    "display_issues_table",
    "display_sync_result",
    "display_push_result",
    "display_push_conflicts",
    "display_label_list",
    "display_label_operation_result",
    "display_milestone_list",
    "display_milestone_operation_result",
    "display_conflicts",
    "display_conflict_details",
]
