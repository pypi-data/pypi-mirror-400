"""Sync operation display functions."""

import difflib
import json

from . import console


def display_sync_result(entity_name: str, result):
    total = len(result.created) + len(result.updated)
    console.print(f"[green]✓[/green] Synced {total} {entity_name}")

    # Show auto-resolved details (these are included in updated count)
    if result.auto_resolve_details:
        console.print(f"[cyan]↺[/cyan] {len(result.auto_resolve_details)} {entity_name} auto-resolved")
        for entity_id, fields in result.auto_resolve_details.items():
            console.print(f"    #{entity_id}: merged {fields}")

    if result.conflicts:
        console.print(f"[yellow]⚠[/yellow] {len(result.conflicts)} {entity_name} conflicts detected")
        for entity_id in result.conflicts:
            detail = result.conflict_details.get(entity_id, "")
            if detail:
                console.print(f"    #{entity_id}: {detail}")


def display_push_result(entity_name: str, result):
    changes = len(result.created) + len(result.updated) + len(result.deleted)
    if changes > 0:
        console.print(f"[green]✓[/green] Synced {changes} {entity_name} "
                    f"({len(result.created)} created, {len(result.updated)} updated, "
                    f"{len(result.deleted)} deleted)")

    # Show auto-resolved details (these are included in updated count)
    if result.auto_resolve_details:
        console.print(f"[cyan]↺[/cyan] {len(result.auto_resolve_details)} {entity_name} auto-resolved")
        for entity_id, fields in result.auto_resolve_details.items():
            console.print(f"    #{entity_id}: merged {fields}")


def display_push_conflicts(entity_name: str, result, detailed: bool = False):
    if not result.conflicts:
        return

    console.print(f"\n[yellow]⚠ {len(result.conflicts)} {entity_name} conflict(s) detected:[/yellow]\n")

    if detailed:
        # Detailed conflict display for issues (field-by-field diff)
        for iid in result.conflicts:
            conflict_data = result.conflict_details.get(iid, "Unknown reason")

            # Try to parse as JSON field diff
            try:
                field_diff = json.loads(conflict_data)

                console.print(f"  [bold yellow]Issue #{iid}:[/bold yellow] Both local and remote modified since last sync\n")

                for field_name, versions in field_diff.items():
                    orig_val = versions.get("original")
                    local_val = versions.get("local")
                    remote_val = versions.get("remote")

                    def format_value(val):
                        if val is None:
                            return ""
                        return str(val)

                    local_str = format_value(local_val)
                    remote_str = format_value(remote_val)

                    local_lines = local_str.splitlines(keepends=True)
                    remote_lines = remote_str.splitlines(keepends=True)

                    diff_lines = list(difflib.unified_diff(
                        remote_lines,
                        local_lines,
                        fromfile=f"remote/{field_name}",
                        tofile=f"local/{field_name}",
                        lineterm=""
                    ))

                    if diff_lines:
                        console.print(f"    [bold cyan]{field_name}:[/bold cyan]")
                        for line in diff_lines:
                            if line.startswith("---") or line.startswith("+++"):
                                console.print(f"      [bold]{line}[/bold]")
                            elif line.startswith("@@"):
                                console.print(f"      [cyan]{line}[/cyan]")
                            elif line.startswith("-"):
                                console.print(f"      [red]{line}[/red]")
                            elif line.startswith("+"):
                                console.print(f"      [green]{line}[/green]")
                            else:
                                console.print(f"      [dim]{line}[/dim]")
                        console.print()

            except (json.JSONDecodeError, TypeError):
                # Fall back to displaying raw message
                console.print(f"  [yellow]#{iid}:[/yellow] {conflict_data}")
    else:
        # Simple conflict display for labels/milestones
        for identifier in result.conflicts:
            reason = result.conflict_details.get(identifier, "Unknown reason")
            console.print(f"  [yellow]{identifier}:[/yellow] {reason}")
