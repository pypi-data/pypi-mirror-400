"""Miscellaneous display functions."""

from . import console


def display_close_result(issue_id: int, title: str, was_already_closed: bool, kanban_labels: list[str]):
    if was_already_closed:
        console.print(f"[yellow]⚠ Issue #{issue_id} was already closed[/yellow]")
    else:
        console.print(f"[green]✓ Closed issue #{issue_id}[/green]")
        if kanban_labels:
            console.print(f"[dim]  Removed Kanban labels: {', '.join(kanban_labels)}[/dim]")


def display_comment_result(issue_iid: int, comment):
    console.print(f"[green]✓ Comment added to issue #{issue_iid}[/green]")
    console.print(f"[dim]Author: {comment.author}[/dim]")
    console.print(f"[dim]Timestamp: {comment.created_at.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
