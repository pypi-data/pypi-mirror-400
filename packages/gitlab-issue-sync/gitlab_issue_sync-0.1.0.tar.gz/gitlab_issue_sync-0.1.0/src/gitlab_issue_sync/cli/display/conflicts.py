"""Conflict display functions."""

from pathlib import Path

from rich import box
from rich.table import Table

from ...storage import Conflict, Issue
from . import console


def display_conflicts(conflicts: list[Conflict], repo_path: Path) -> None:
    """Display unresolved conflicts in a table.

    Args:
        conflicts: List of Conflict objects to display
        repo_path: Path to repository root (for loading issue titles)
    """
    if not conflicts:
        console.print("[green]No conflicts found.[/green]")
        return

    console.print(f"\n[bold red]⚠ {len(conflicts)} unresolved conflict(s)[/bold red]\n")

    # Create table
    table = Table(box=box.ROUNDED)
    table.add_column("Issue", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Conflicting Fields", style="yellow")
    table.add_column("Detected", style="dim")

    for conflict in conflicts:
        # Load issue to get title
        issue = Issue.load(conflict.issue_iid, repo_path)
        title = issue.title if issue else "[unknown]"

        # Truncate title if too long
        if len(title) > 40:
            title = title[:37] + "..."

        # Format fields
        fields_str = ", ".join(conflict.fields) if conflict.fields else "[unknown]"

        # Format timestamp
        detected_str = conflict.detected_at.strftime("%Y-%m-%d %H:%M")

        table.add_row(
            f"#{conflict.issue_iid}",
            title,
            fields_str,
            detected_str,
        )

    console.print(table)
    console.print("\n[dim]To resolve: Edit the issue file, then run 'conflicts resolve <IID>'[/dim]")
    console.print("[dim]For detailed view: run 'conflicts show <IID>'[/dim]\n")


def display_conflict_details(
    conflict: Conflict,
    local: "Issue",
    remote: "Issue",
    original: "Issue | None",
    repo_path: Path,
) -> None:
    """Display detailed information about a specific conflict."""
    # Display conflict header
    console.print(f"\n[bold red]⚠ Conflict in Issue #{local.iid}[/bold red]")
    console.print(f"[bold]{local.title}[/bold]\n")

    # Show which fields are in conflict
    console.print(f"[bold]Conflicting fields:[/bold] {', '.join(conflict.fields)}")
    console.print(f"[bold]Detected:[/bold] {conflict.detected_at.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Show file locations
    console.print("[bold]File locations:[/bold]")
    local_file = local.get_file_path(repo_path)
    remote_cache = Issue.get_remote_cache_path(local.iid, repo_path)
    original_file = Issue.get_original_path(local.iid, repo_path)

    console.print(f"  [yellow]Local:[/yellow]    {local_file}")
    console.print(f"  [green]Remote:[/green]   {remote_cache}")
    if original:
        console.print(f"  [blue]Original:[/blue]  {original_file}")
    console.print()

    # For each conflicting field, show local vs remote
    for field_name in conflict.fields:
        local_val = getattr(local, field_name, None)
        remote_val = getattr(remote, field_name, None)

        console.print(f"[bold cyan]Field:[/bold cyan] {field_name}")
        console.print(f"[yellow]Local version:[/yellow]")
        _display_field_value(field_name, local_val)
        console.print(f"[green]Remote version:[/green]")
        _display_field_value(field_name, remote_val)
        console.print()

    # Show resolution instructions
    console.print(f"[bold]To resolve this conflict:[/bold]")
    console.print(f"  1. Edit the local file: [cyan]{local_file}[/cyan]")
    console.print(f"  2. Merge changes from local and remote versions")
    console.print(f"  3. Run: [bold]gl-issue-sync conflicts resolve {local.iid}[/bold]")
    console.print(f"  4. Push: [bold]gl-issue-sync push[/bold]\n")


def _display_field_value(field_name: str, value) -> None:
    """Helper to display field values in a readable format."""
    if value is None:
        console.print("  [dim](none)[/dim]")
    elif isinstance(value, str):
        # For text fields, show first few lines with line numbers
        lines = value.split('\n')
        if len(lines) > 10:
            for i, line in enumerate(lines[:10], 1):
                console.print(f"  [dim]{i:3}[/dim] {line}")
            console.print(f"  [dim]    ... ({len(lines) - 10} more lines)[/dim]")
        else:
            for i, line in enumerate(lines, 1):
                console.print(f"  [dim]{i:3}[/dim] {line}")
    elif isinstance(value, list):
        if not value:
            console.print("  [dim](empty)[/dim]")
        else:
            for item in value:
                if hasattr(item, 'author') and hasattr(item, 'body'):
                    # Comment - show preview
                    preview = item.body.replace('\n', ' ')[:70]
                    console.print(f"  • [cyan]{item.author}[/cyan]: {preview}...")
                elif hasattr(item, 'target_issue_iid'):
                    # Link
                    console.print(f"  • #{item.target_issue_iid} ({item.link_type})")
                else:
                    # Generic list item
                    console.print(f"  • {item}")
    else:
        console.print(f"  {value}")
