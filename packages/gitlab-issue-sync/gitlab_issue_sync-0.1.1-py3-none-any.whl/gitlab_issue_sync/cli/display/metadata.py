"""Metadata (labels and milestones) display functions."""

from rich.table import Table

from . import console


def display_label_list(labels: list, kanban_labels: set, with_kanban: bool):
    label_type = "all" if with_kanban else "non-kanban"

    if not labels:
        if with_kanban:
            console.print("[yellow]⚠ No labels found[/yellow]")
        else:
            console.print(f"[yellow]⚠ No {label_type} labels found[/yellow]")
            if kanban_labels:
                console.print("[dim]Use --with-kanban to see kanban column labels[/dim]")
        return

    console.print(f"\n[bold]Project Labels:[/bold] ({len(labels)} {label_type})")
    console.print()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Label", style="cyan")
    table.add_column("Color", width=10)
    table.add_column("Description", style="dim")

    for lbl in labels:
        color_display = f"[{lbl.color}]███[/{lbl.color}]" if lbl.color else "[dim]none[/dim]"
        description = lbl.description if lbl.description else "[dim]no description[/dim]"
        table.add_row(lbl.name, color_display, description)

    console.print(table)

    if not with_kanban and kanban_labels:
        console.print(f"\n[dim]Kanban column labels ({len(kanban_labels)}) are hidden.[/dim]")
        console.print("[dim]Use --with-kanban to include them.[/dim]")


def display_label_operation_result(operation: str, name: str, color: str | None = None, description: str | None = None):
    if operation == "create":
        console.print(f"[bold green]✓ Created label:[/bold green] [cyan]{name}[/cyan]")
        if color:
            console.print(f"  Color: [{color}]███[/{color}] {color}")
        if description:
            console.print(f"  Description: {description}")
        console.print("\n[dim]Label will be created on GitLab when you run 'gl-issue-sync push'[/dim]")
    elif operation == "update":
        console.print(f"[bold green]✓ Updated label:[/bold green] [cyan]{name}[/cyan]")
        if color:
            console.print(f"  New color: [{color}]███[/{color}] {color}")
        if description:
            console.print(f"  New description: {description}")
        console.print("\n[dim]Changes will be synced to GitLab when you run 'gl-issue-sync push'[/dim]")
    elif operation == "delete":
        console.print(f"[bold green]✓ Deleted label:[/bold green] [cyan]{name}[/cyan]")
        console.print("\n[dim]Label will be deleted from GitLab when you run 'gl-issue-sync push'[/dim]")


def display_milestone_list(milestones: list, state: str):
    if not milestones:
        console.print(f"[yellow]⚠ No {state} milestones found[/yellow]")
        return

    console.print(f"\n[bold]Project Milestones:[/bold] ({len(milestones)} {state})")
    console.print()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Title", style="cyan")
    table.add_column("State", width=10)
    table.add_column("Due Date", width=12)
    table.add_column("Description", style="dim")

    for milestone in milestones:
        state_display = (
            f"[green]{milestone.state}[/green]"
            if milestone.state == "active"
            else f"[dim]{milestone.state}[/dim]"
        )
        due_date_display = milestone.due_date if milestone.due_date else "[dim]none[/dim]"
        description = (
            (milestone.description[:60] + "...")
            if milestone.description and len(milestone.description) > 60
            else (milestone.description or "[dim]no description[/dim]")
        )
        table.add_row(milestone.title, state_display, due_date_display, description)

    console.print(table)


def display_milestone_operation_result(operation: str, title: str, due_date: str | None = None):
    if operation == "create":
        console.print(f"[bold green]✓ Created milestone:[/bold green] [cyan]{title}[/cyan]")
        if due_date:
            console.print(f"[dim]  Due date: {due_date}[/dim]")
        console.print("\n[dim]Milestone will be created on GitLab when you run 'gl-issue-sync push'[/dim]")
    elif operation == "update":
        console.print(f"[bold green]✓ Updated milestone:[/bold green] [cyan]{title}[/cyan]")
        console.print("\n[dim]Changes will be pushed to GitLab when you run 'gl-issue-sync push'[/dim]")
    elif operation == "close":
        console.print(f"[bold green]✓ Closed milestone:[/bold green] [cyan]{title}[/cyan]")
        console.print("\n[dim]Milestone will be closed on GitLab when you run 'gl-issue-sync push'[/dim]")
    elif operation == "delete":
        console.print(f"[bold green]✓ Deleted milestone:[/bold green] [cyan]{title}[/cyan]")
        console.print("\n[dim]Milestone will be deleted from GitLab when you run 'gl-issue-sync push'[/dim]")
