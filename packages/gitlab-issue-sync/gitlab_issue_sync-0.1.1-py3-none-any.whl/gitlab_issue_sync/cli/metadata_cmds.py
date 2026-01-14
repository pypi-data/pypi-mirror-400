"""Metadata management commands for labels, milestones, assignees, and linked issues."""

import sys

import click
from rich.prompt import Confirm

from .display import (
    console,
    console_err,
    display_label_list,
    display_label_operation_result,
    display_milestone_list,
    display_milestone_operation_result,
)
from ..exit_codes import EXIT_GENERAL_ERROR
from ..git_utils import find_project_root
from ..metadata_manager import LinkValue, get_metadata_manager
from ..storage import Issue, Label, Milestone
from . import IID, _format_iid, _try_parse_iid, get_repo_and_config, handle_cli_errors, main


@main.command()
@click.argument("metadata_type")
@click.argument("issue_iid", type=IID)
@click.argument("operation", required=False)
@click.argument("values", required=False)
@click.option(
    "--type",
    "link_type",
    default="relates_to",
    help="Link type for linked issues (relates_to, blocks, is_blocked_by)",
)
@handle_cli_errors
def metadata(metadata_type: str, issue_iid: int | str, operation: str | None, values: str | None, link_type: str):
    """Manage issue metadata (labels, assignees, linked issues).

    \b
    Arguments:
        METADATA_TYPE: Type of metadata (labels, assignees, linked)
        ISSUE_IID: Issue number (e.g., 1 for issue #1, or T1 for temporary issues)
        OPERATION: Optional operation (add, remove, set, unset). Defaults to list if omitted.
        VALUES: Comma-separated values (required for add/remove/set)

    \b
    Examples:
        gl-issue-sync metadata labels 1                  # List
        gl-issue-sync metadata labels 1 add bug,urgent   # Add
        gl-issue-sync metadata labels 1 remove urgent    # Remove
        gl-issue-sync metadata labels 1 set feature      # Replace
        gl-issue-sync metadata labels 1 unset            # Clear
        gl-issue-sync metadata linked 1                  # List
        gl-issue-sync metadata linked 1 add 2,3          # Add
        gl-issue-sync metadata linked 1 add 4 --type blocks
        gl-issue-sync metadata linked 1 remove 2         # Remove
        gl-issue-sync metadata labels T1 add bug
    """
    repo_root = find_project_root()

    # Get metadata manager and handler
    manager = get_metadata_manager()
    try:
        handler = manager.get_handler(metadata_type)
    except ValueError as e:
        console_err.print(f"[bold red]✗ Invalid Metadata Type:[/bold red] {e}")
        console_err.print(f"[dim]Available types: {', '.join(manager.list_types())}[/dim]")
        sys.exit(EXIT_GENERAL_ERROR)

    # Find and load issue
    issue = Issue.load(issue_iid, repo_root)

    if not issue:
        console_err.print(f"[bold red]✗ Issue {_format_iid(issue_iid)} not found locally[/bold red]")
        console_err.print("[dim]Run 'gl-issue-sync pull' to sync issues first[/dim]")
        sys.exit(EXIT_GENERAL_ERROR)

    # Default to "list" operation if not specified
    if operation is None:
        operation = "list"

    # Handle list operation
    if operation == "list":
        header = f"{handler.metadata_name.title()} for Issue {_format_iid(issue_iid)}"
        console.print(f"\n[bold blue]📋 {header}[/bold blue]\n")
        current_values = handler.get_values(issue)

        if current_values:
            for value in current_values:
                formatted = handler.format_value(value)
                console.print(f"  • {formatted}")
        else:
            console.print(f"[dim]No {handler.metadata_name} set[/dim]")

        console.print()
        return

    # All other operations require values (except unset)
    if operation != "unset" and not values:
        console_err.print(f"[bold red]✗ Missing Values:[/bold red] The '{operation}' operation requires values")
        example = f"gl-issue-sync metadata {metadata_type} {issue_iid} {operation} value1,value2"
        console_err.print(f"[dim]Example: {example}[/dim]")
        sys.exit(EXIT_GENERAL_ERROR)

    # Parse values
    value_list = []
    if values:
        if metadata_type in ["linked", "linked issues"]:
            # Parse as IIDs with optional link type
            for val in values.split(","):
                val = val.strip()
                try:
                    iid = int(val)
                    value_list.append(LinkValue(target_iid=iid, link_type=link_type))
                except ValueError:
                    console_err.print(f"[bold red]✗ Invalid IID:[/bold red] '{val}' is not a valid issue number")
                    sys.exit(EXIT_GENERAL_ERROR)
        elif metadata_type == "parent":
            # Parse as single IID (integer)
            val = values.strip()
            try:
                iid = int(val)
                value_list.append(iid)
            except ValueError:
                console_err.print(f"[bold red]✗ Invalid IID:[/bold red] '{val}' is not a valid issue number")
                sys.exit(EXIT_GENERAL_ERROR)
        else:
            # Parse as strings
            value_list = [v.strip() for v in values.split(",") if v.strip()]

    # Validate values
    try:
        if operation != "unset":
            handler.validate_values(value_list, link_type=link_type)
    except ValueError as e:
        console_err.print(f"[bold red]✗ Validation Error:[/bold red] {e}")
        sys.exit(EXIT_GENERAL_ERROR)

    # Execute operation
    header = f"Updating {handler.metadata_name.title()} for Issue {_format_iid(issue_iid)}"
    console.print(f"\n[bold blue]✏️  {header}[/bold blue]\n")

    if operation == "add":
        change = handler.add_values(issue, value_list, link_type=link_type)
    elif operation == "remove":
        # For linked issues, we need just the IIDs for removal
        if metadata_type in ["linked", "linked issues"]:
            iids_to_remove = [v.target_iid for v in value_list]
            change = handler.remove_values(issue, iids_to_remove)
        else:
            change = handler.remove_values(issue, value_list)
    elif operation == "set":
        change = handler.set_values(issue, value_list, link_type=link_type)
    elif operation == "unset":
        change = handler.unset_values(issue)
    else:
        console_err.print(f"[bold red]✗ Invalid Operation:[/bold red] '{operation}'")
        console_err.print("[dim]Valid operations: list, add, remove, set, unset[/dim]")
        sys.exit(EXIT_GENERAL_ERROR)

    # Display changes
    if change.added:
        console.print("[green]✓ Added:[/green]")
        for val in change.added:
            # Format based on type
            if metadata_type in ["linked", "linked issues"]:
                console.print(f"  • #{val}")
            else:
                console.print(f"  • {val}")

    if change.removed:
        console.print("[yellow]✓ Removed:[/yellow]")
        for val in change.removed:
            if metadata_type in ["linked", "linked issues"]:
                console.print(f"  • #{val}")
            else:
                console.print(f"  • {val}")

    if change.unchanged and operation in ["add", "remove"]:
        console.print("[dim]Already present/not found:[/dim]")
        for val in change.unchanged:
            if metadata_type in ["linked", "linked issues"]:
                console.print(f"  • #{val}")
            else:
                console.print(f"  • {val}")

    # Save issue locally
    issue.save(repo_root)

    console.print(f"\n[green]✓ Updated {handler.metadata_name} for issue {_format_iid(issue_iid)}[/green]")
    console.print("[yellow]Run 'gl-issue-sync push' to sync changes to GitLab[/yellow]\n")


@main.command()
@click.argument("issue_iid", type=IID)
@click.argument("operation", required=False)
@click.argument("values", required=False)
def assignees(issue_iid: int | str, operation: str | None, values: str | None):
    """Manage issue assignees (shorthand for 'metadata assignees').

    \b
    Examples:
        gl-issue-sync assignees 1                # List assignees
        gl-issue-sync assignees 1 add emma,john  # Add assignees
        gl-issue-sync assignees 1 remove john    # Remove assignee
        gl-issue-sync assignees 1 set emma       # Replace all
        gl-issue-sync assignees 1 unset          # Clear all
        gl-issue-sync assignees T1 add emma      # Add assignee to temp issue
    """
    # Delegate to metadata command
    from click import Context

    ctx = Context(metadata)
    ctx.invoke(
        metadata,
        metadata_type="assignees",
        issue_iid=issue_iid,
        operation=operation,
        values=values,
        link_type="relates_to",
    )


@main.command()
@click.argument("issue_iid", type=IID)
@click.argument("operation", required=False)
@click.argument("values", required=False)
@click.option("--type", "link_type", default="relates_to", help="Link type (relates_to, blocks, is_blocked_by)")
def linked(issue_iid: int | str, operation: str | None, values: str | None, link_type: str):
    """Manage linked issues (shorthand for 'metadata linked').

    \b
    Examples:
        gl-issue-sync linked 1                          # List linked issues
        gl-issue-sync linked 1 add 2,3                  # Add links (relates_to)
        gl-issue-sync linked 1 add 4 --type blocks      # Add with type
        gl-issue-sync linked 1 remove 2                 # Remove link
        gl-issue-sync linked 1 set 5,6 --type blocks    # Replace all
        gl-issue-sync linked 1 unset                    # Remove all
        gl-issue-sync linked T1 add 2                   # Add link to temp issue
    """
    # Delegate to metadata command
    from click import Context

    ctx = Context(metadata)
    ctx.invoke(
        metadata,
        metadata_type="linked issues",
        issue_iid=issue_iid,
        operation=operation,
        values=values,
        link_type=link_type,
    )


@main.command()
@click.argument("issue_iid", type=IID)
@click.argument("operation", required=False)
@click.argument("values", required=False)
@handle_cli_errors
def parent(issue_iid: int | str, operation: str | None, values: str | None):
    """Manage issue parent (shorthand for 'metadata parent').

    Set or unset the parent issue for work item hierarchy.
    Only 'set' and 'unset' operations are supported (parent is singular, not a list).

    Examples:
        gl-issue-sync parent 4                # Show parent
        gl-issue-sync parent 4 set 1          # Set parent to #1
        gl-issue-sync parent 4 unset          # Remove parent
        gl-issue-sync parent T1 set 4         # Set parent on temp issue
    """
    # Delegate to metadata command
    from click import Context

    ctx = Context(metadata)
    ctx.invoke(
        metadata,
        metadata_type="parent",
        issue_iid=issue_iid,
        operation=operation,
        values=values,
        link_type="relates_to",  # Not used for parent, but required by metadata signature
    )


@main.command()
@click.argument("iid_or_subcommand")
@click.argument("operation_or_name", required=False)
@click.argument("values", required=False)
@click.option("--with-kanban", is_flag=True, help="Include kanban column labels (for 'list' subcommand)")
@click.option("--color", help="Hex color code (for 'create' and 'update' subcommands)")
@click.option("--description", help="Label description (for 'create' and 'update' subcommands)")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation (for 'delete' subcommand)")
@handle_cli_errors
def label(
    iid_or_subcommand: str,
    operation_or_name: str | None,
    values: str | None,
    with_kanban: bool,
    color: str | None,
    description: str | None,
    yes: bool,
):
    """Manage project labels and issue labels.

    This unified command handles both:
    - Project-level label management (CRUD operations)
    - Issue-level label assignment (add/remove labels to/from issues)

    \b
    Project-level operations (no issue IID):
        gl-issue-sync label list [--with-kanban]
        gl-issue-sync label create <name> [--color <hex>] [--description <text>]
        gl-issue-sync label update <name> [--color <hex>] [--description <text>]
        gl-issue-sync label delete <name> [--yes]

    \b
    Issue-level operations (with issue IID or temporary IID):
        gl-issue-sync label <iid>                 # List labels on issue
        gl-issue-sync label <iid> add <values>    # Add labels to issue
        gl-issue-sync label <iid> remove <values> # Remove labels from issue
        gl-issue-sync label <iid> set <values>    # Replace all labels
        gl-issue-sync label <iid> unset           # Clear all labels

    \b
    Examples:
        # Project-level
        gl-issue-sync label list
        gl-issue-sync label create bug --color "#FF0000"
        gl-issue-sync label update bug --description "Bug reports"
        gl-issue-sync label delete old-label --yes
        # Issue-level
        gl-issue-sync label 42
        gl-issue-sync label 42 add bug,urgent
        gl-issue-sync label 42 remove urgent
        gl-issue-sync label 42 set feature,backend
        gl-issue-sync label 42 unset
        gl-issue-sync label T1 add bug
    """
    # Determine if this is a project-level or issue-level operation
    # Try to parse first argument as an IID (numeric or T-prefixed)
    issue_iid = _try_parse_iid(iid_or_subcommand)
    if issue_iid is not None:
        # This is an issue-level operation
        _handle_issue_label_operation(issue_iid, operation_or_name, values)
    else:
        # This is a project-level operation
        subcommand = iid_or_subcommand
        name = operation_or_name

        if subcommand == "list":
            _handle_project_label_list(with_kanban)
        elif subcommand == "create":
            if not name:
                console_err.print("[bold red]✗ Missing label name[/bold red]")
                console_err.print("[dim]Usage: gl-issue-sync label create <name> [--color] [--description][/dim]")
                sys.exit(EXIT_GENERAL_ERROR)
            _handle_project_label_create(name, color, description)
        elif subcommand == "update":
            if not name:
                console_err.print("[bold red]✗ Missing label name[/bold red]")
                console_err.print("[dim]Usage: gl-issue-sync label update <name> [--color] [--description][/dim]")
                sys.exit(EXIT_GENERAL_ERROR)
            _handle_project_label_update(name, color, description)
        elif subcommand == "delete":
            if not name:
                console_err.print("[bold red]✗ Missing label name[/bold red]")
                console_err.print("[dim]Usage: gl-issue-sync label delete <name> [--yes][/dim]")
                sys.exit(EXIT_GENERAL_ERROR)
            _handle_project_label_delete(name, yes)
        else:
            console_err.print(f"[bold red]✗ Unknown subcommand:[/bold red] {subcommand}")
            console_err.print("[dim]Valid subcommands: list, create, update, delete[/dim]")
            console_err.print("[dim]Or provide an issue IID for issue-level operations[/dim]")
            sys.exit(EXIT_GENERAL_ERROR)


def _handle_issue_label_operation(issue_iid: int | str, operation: str | None, values: str | None):
    """Handle issue-level label operations."""
    # Delegate to metadata command
    from click import Context

    ctx = Context(metadata)
    ctx.invoke(
        metadata,
        metadata_type="labels",
        issue_iid=issue_iid,
        operation=operation,
        values=values,
        link_type="relates_to",
    )


def _handle_project_label_list(with_kanban: bool):
    """List project labels."""
    repo_root, config = get_repo_and_config()

    all_labels = [lbl for lbl in Label.backend.load_all(repo_root) if lbl.status != "deleted"]
    kanban_labels = set(config.board.columns) if config.board and config.board.columns else set()

    labels_to_display = all_labels if with_kanban else [lbl for lbl in all_labels if lbl.name not in kanban_labels]
    labels_to_display.sort(key=lambda lbl: lbl.name.lower())

    display_label_list(labels_to_display, kanban_labels, with_kanban)


def _handle_project_label_create(name: str, color: str | None, description: str | None):
    """Create a new project label."""
    repo_root = find_project_root()

    # Validate color format if provided
    if color and not color.startswith("#"):
        console_err.print(f"[bold red]✗ Invalid color format:[/bold red] {color}")
        console_err.print("[dim]Color must start with # (e.g., #FF0000)[/dim]")
        sys.exit(EXIT_GENERAL_ERROR)

    # Check if label already exists
    existing = Label.backend.load(name, repo_root)
    if existing and existing.status != "deleted":
        console_err.print(f"[bold red]✗ Label already exists:[/bold red] {name}")
        sys.exit(EXIT_GENERAL_ERROR)

    # Create new label
    new_label = Label(name=name, color=color, description=description)
    new_label.status = "pending"
    Label.backend.save(new_label, repo_root)

    display_label_operation_result("create", name, color, description)


def _handle_project_label_update(name: str, color: str | None, description: str | None):
    """Update an existing label's properties."""
    repo_root = find_project_root()

    if not color and not description:
        console_err.print("[bold red]✗ No updates specified[/bold red]")
        console_err.print("[dim]Provide --color and/or --description[/dim]")
        sys.exit(EXIT_GENERAL_ERROR)

    # Validate color format if provided
    if color and not color.startswith("#"):
        console_err.print(f"[bold red]✗ Invalid color format:[/bold red] {color}")
        console_err.print("[dim]Color must start with # (e.g., #FF0000)[/dim]")
        sys.exit(EXIT_GENERAL_ERROR)

    # Load and validate label
    existing_label = Label.backend.load(name, repo_root)
    if not existing_label or existing_label.status == "deleted":
        console_err.print(f"[bold red]✗ Label not found:[/bold red] {name}")
        sys.exit(EXIT_GENERAL_ERROR)

    # Update properties
    if color:
        existing_label.color = color
    if description:
        existing_label.description = description

    # Mark as modified if not already pending
    if existing_label.status == "synced":
        existing_label.status = "modified"

    Label.backend.save(existing_label, repo_root)
    display_label_operation_result("update", name, color, description)


def _handle_project_label_delete(name: str, yes: bool):
    """Delete a project label."""
    repo_root = find_project_root()

    # Load and validate label
    existing_label = Label.backend.load(name, repo_root)
    if not existing_label or existing_label.status == "deleted":
        console_err.print(f"[bold red]✗ Label not found:[/bold red] {name}")
        sys.exit(EXIT_GENERAL_ERROR)

    # Confirm deletion unless --yes flag
    if not yes:
        confirm = Confirm.ask(f"[yellow]⚠[/yellow] Delete label '[cyan]{name}[/cyan]'?")
        if not confirm:
            console.print("[dim]Cancelled[/dim]")
            return

    # Mark label as deleted
    existing_label.status = "deleted"
    Label.backend.save(existing_label, repo_root)

    display_label_operation_result("delete", name)


# ===== Milestone Commands =====


@main.command()
@click.argument("iid_or_subcommand")
@click.argument("operation_or_title", required=False)
@click.argument("value", required=False)
@click.option(
    "--state",
    type=click.Choice(["active", "closed", "all"]),
    default="active",
    help="Filter by state (for 'list' subcommand)",
)
@click.option("--description", help="Milestone description (for 'create' and 'update' subcommands)")
@click.option("--due-date", help="Due date in YYYY-MM-DD format (for 'create' and 'update' subcommands)")
@click.option("--start-date", help="Start date in YYYY-MM-DD format (for 'create' and 'update' subcommands)")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation (for 'delete' subcommand)")
@handle_cli_errors
def milestone(
    iid_or_subcommand: str,
    operation_or_title: str | None,
    value: str | None,
    state: str,
    description: str | None,
    due_date: str | None,
    start_date: str | None,
    yes: bool,
):
    """Manage project milestones and issue milestones.

    This unified command handles both:
    - Project-level milestone management (CRUD operations)
    - Issue-level milestone assignment (set/unset milestone on issues)

    \b
    Project-level operations (no issue IID):
        gl-issue-sync milestone list [--state active|closed|all]
        gl-issue-sync milestone create <title> [--description <text>] [--due-date <YYYY-MM-DD>]
        gl-issue-sync milestone update <title> [--description <text>] [--due-date <YYYY-MM-DD>]
        gl-issue-sync milestone close <title>
        gl-issue-sync milestone delete <title> [--yes]

    \b
    Issue-level operations (with issue IID or temporary IID):
        gl-issue-sync milestone <iid>               # Show milestone on issue
        gl-issue-sync milestone <iid> set <title>   # Set milestone on issue
        gl-issue-sync milestone <iid> unset         # Clear milestone from issue

    \b
    Examples:
        # Project-level
        gl-issue-sync milestone list
        gl-issue-sync milestone create "Sprint 1" --due-date "2026-02-01"
        gl-issue-sync milestone update "Sprint 1" --description "Q1 Sprint"
        gl-issue-sync milestone close "Sprint 1"
        gl-issue-sync milestone delete "Old Milestone" --yes

        # Issue-level
        gl-issue-sync milestone 42                  # Show milestone
        gl-issue-sync milestone 42 set "Sprint 1"   # Set milestone
        gl-issue-sync milestone 42 unset            # Clear milestone
        gl-issue-sync milestone T1 set "Sprint 1"   # Set milestone on temp issue
    """
    # Determine if this is a project-level or issue-level operation
    # Try to parse first argument as an IID (numeric or T-prefixed)
    issue_iid = _try_parse_iid(iid_or_subcommand)
    if issue_iid is not None:
        # This is an issue-level operation
        _handle_issue_milestone_operation(issue_iid, operation_or_title, value)
    else:
        # This is a project-level operation
        subcommand = iid_or_subcommand
        title = operation_or_title

        if subcommand == "list":
            _handle_project_milestone_list(state)
        elif subcommand == "create":
            if not title:
                console_err.print("[bold red]✗ Missing milestone title[/bold red]")
                console_err.print(
                    "[dim]Usage: gl-issue-sync milestone create <title> [options][/dim]"
                )
                sys.exit(EXIT_GENERAL_ERROR)
            _handle_project_milestone_create(title, description, due_date, start_date)
        elif subcommand == "update":
            if not title:
                console_err.print("[bold red]✗ Missing milestone title[/bold red]")
                console_err.print(
                    "[dim]Usage: gl-issue-sync milestone update <title> [options][/dim]"
                )
                sys.exit(EXIT_GENERAL_ERROR)
            _handle_project_milestone_update(title, description, due_date, start_date)
        elif subcommand == "close":
            if not title:
                console_err.print("[bold red]✗ Missing milestone title[/bold red]")
                console_err.print("[dim]Usage: gl-issue-sync milestone close <title>[/dim]")
                sys.exit(EXIT_GENERAL_ERROR)
            _handle_project_milestone_close(title)
        elif subcommand == "delete":
            if not title:
                console_err.print("[bold red]✗ Missing milestone title[/bold red]")
                console_err.print("[dim]Usage: gl-issue-sync milestone delete <title> [--yes][/dim]")
                sys.exit(EXIT_GENERAL_ERROR)
            _handle_project_milestone_delete(title, yes)
        else:
            console_err.print(f"[bold red]✗ Unknown subcommand:[/bold red] {subcommand}")
            console_err.print("[dim]Valid subcommands: list, create, update, close, delete[/dim]")
            console_err.print("[dim]Or provide an issue IID for issue-level operations[/dim]")
            sys.exit(EXIT_GENERAL_ERROR)


def _handle_issue_milestone_operation(issue_iid: int | str, operation: str | None, value: str | None):
    """Handle issue-level milestone operations."""
    # Delegate to metadata command
    from click import Context

    ctx = Context(metadata)
    ctx.invoke(
        metadata,
        metadata_type="milestone",
        issue_iid=issue_iid,
        operation=operation,
        values=value,
        link_type="relates_to",
    )


def _handle_project_milestone_list(state: str):
    """List project milestones."""
    repo_root = find_project_root()

    # Load and filter milestones
    all_milestones = [m for m in Milestone.backend.load_all(repo_root) if m.status != "deleted"]

    # Filter by state
    if state == "active":
        milestones_to_display = [m for m in all_milestones if m.state == "active"]
    elif state == "closed":
        milestones_to_display = [m for m in all_milestones if m.state == "closed"]
    else:  # all
        milestones_to_display = all_milestones

    # Sort by due date, then by title
    milestones_to_display.sort(key=lambda m: (m.due_date or "9999-99-99", m.title.lower()))

    display_milestone_list(milestones_to_display, state)


def _handle_project_milestone_create(title: str, description: str | None, due_date: str | None, start_date: str | None):
    """Create a new project milestone."""
    repo_root = find_project_root()

    # Check if milestone already exists
    existing = Milestone.backend.load(title, repo_root)
    if existing and existing.status != "deleted":
        console_err.print(f"[bold red]✗ Milestone already exists:[/bold red] {title}")
        sys.exit(EXIT_GENERAL_ERROR)

    # Create milestone locally
    Milestone.create(
        title=title,
        description=description,
        due_date=due_date,
        start_date=start_date,
        repo_path=repo_root,
    )

    display_milestone_operation_result("create", title, due_date)


def _handle_project_milestone_update(title: str, description: str | None, due_date: str | None, start_date: str | None):
    """Update an existing milestone."""
    repo_root = find_project_root()

    # Load and validate milestone
    ms = Milestone.backend.load(title, repo_root)
    if not ms or ms.status == "deleted":
        console_err.print(f"[bold red]✗ Milestone not found:[/bold red] {title}")
        sys.exit(EXIT_GENERAL_ERROR)

    # Update milestone
    ms.update(
        description=description,
        due_date=due_date,
        start_date=start_date,
        repo_path=repo_root,
    )

    display_milestone_operation_result("update", title, due_date)


def _handle_project_milestone_close(title: str):
    """Close a milestone."""
    repo_root = find_project_root()

    # Load and validate milestone
    ms = Milestone.backend.load(title, repo_root)
    if not ms or ms.status == "deleted":
        console_err.print(f"[bold red]✗ Milestone not found:[/bold red] {title}")
        sys.exit(EXIT_GENERAL_ERROR)

    # Close milestone
    ms.close(repo_path=repo_root)

    display_milestone_operation_result("close", title)


def _handle_project_milestone_delete(title: str, yes: bool):
    """Delete a milestone."""
    repo_root = find_project_root()

    # Load and validate milestone
    ms = Milestone.backend.load(title, repo_root)
    if not ms or ms.status == "deleted":
        console_err.print(f"[bold red]✗ Milestone not found:[/bold red] {title}")
        sys.exit(EXIT_GENERAL_ERROR)

    # Confirm deletion unless --yes flag
    if not yes:
        confirm = Confirm.ask(f"[yellow]⚠[/yellow] Delete milestone '[cyan]{title}[/cyan]'?")
        if not confirm:
            console.print("[dim]Cancelled[/dim]")
            return

    # Mark milestone as deleted
    ms.delete(repo_path=repo_root)

    display_milestone_operation_result("delete", title)
