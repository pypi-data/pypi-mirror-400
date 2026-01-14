"""Board display functions."""

from . import console


def display_board_move_result(
    issue_id: int,
    old_col: str | None,
    new_col: str | None,
    state_info: dict
):
    was_closed = state_info["was_closed"]
    new_state = state_info["new_state"]

    old_desc = f"[magenta]{old_col}[/magenta]" if old_col else "[yellow](no column)[/yellow]"
    new_desc = f"[magenta]{new_col}[/magenta]" if new_col else "[yellow](no column)[/yellow]"

    # Display appropriate message based on state changes
    if was_closed and new_state == "opened":
        console.print(f"[green]✓ Re-opened and moved issue #{issue_id}[/green]")
        console.print(f"[dim]  closed → {new_desc}[/dim]")
    elif new_state == "closed":
        console.print(f"[green]✓ Closed issue #{issue_id}[/green]")
        console.print(f"[dim]  {old_desc} → closed[/dim]")
    else:
        console.print(f"[green]✓ Moved issue #{issue_id}[/green]")
        console.print(f"[dim]  {old_desc} → {new_desc}[/dim]")
