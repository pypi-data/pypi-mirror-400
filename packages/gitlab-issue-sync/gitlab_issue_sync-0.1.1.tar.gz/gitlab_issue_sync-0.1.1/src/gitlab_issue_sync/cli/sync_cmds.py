"""Synchronization commands for GitLab issue sync (pull, push, sync)."""

import sys

import click
from rich.table import Table

from .display import (
    console,
    console_err,
    display_push_conflicts,
    display_push_result,
    display_sync_result,
)
from ..config import ConfigurationError
from ..git_utils import get_gitlab_remote_info
from ..graphql import GitLabGraphQLClient
from ..storage import (
    ISSUE_STATE_CLOSED,
    ISSUE_STATE_OPENED,
    Issue,
    Label,
    Milestone,
    WorkItemTypeCache,
)
from . import get_repo_and_config, handle_cli_errors, setup_gitlab_client


@click.command()
@click.option(
    "--state", type=click.Choice(["opened", "closed", "all"]), default="opened", help="Filter issues by state"
)
@click.option(
    "--types", is_flag=True, help="Refresh work item types cache (for parent-child hierarchy)"
)
@handle_cli_errors
def pull(state: str, types: bool):
    """Pull issues from GitLab to local files.

    Fetches issues from GitLab and updates local markdown files.
    Detects conflicts when both local and remote have changed.
    """
    console.print("\n[bold blue]⬇️  Pulling from GitLab[/bold blue]\n")

    console.print("[dim]→[/dim] Connecting to GitLab...")
    repo_root, config, _, project = setup_gitlab_client()
    console.print(f"[green]✓[/green] Connected to [bold]{config.full_path}[/bold]\n")

    # Refresh work item types cache if requested
    if types:
        console.print("[dim]→[/dim] Refreshing work item types cache...")
        try:
            graphql_client = GitLabGraphQLClient(config.instance_url, config.token)
            type_cache = WorkItemTypeCache.fetch_and_save(graphql_client, config.full_path, repo_root)
            console.print(f"[green]✓[/green] Cached {len(type_cache.types)} work item types\n")
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Could not refresh work item types: {e}\n")

    # Pull entities in order: Labels, Milestones, Issues
    entities = [
        (Label, "labels", {}),
        (Milestone, "milestones", {}),
        (Issue, "issues", {"state": None if state == "all" else state}),
    ]

    for entity_class, entity_name, pull_kwargs in entities:
        filter_parts = []
        for key, value in pull_kwargs.items():
            if value is not None:
                filter_parts.append(f"{key}={value}")

        filter_desc = f" ({', '.join(filter_parts)})" if filter_parts else ""

        console.print(f"[dim]→[/dim] Fetching {entity_name}{filter_desc}...")
        with console.status(f"[bold green]Syncing {entity_name}..."):
            result = entity_class.pull(project, repo_root, **pull_kwargs)
        display_sync_result(entity_name, result)

        # Display detailed conflict information
        if result.conflicts:
            # Issues get field-by-field diffs, others get identifier + reason
            detailed = (entity_name == "issues")
            display_push_conflicts(entity_name, result, detailed=detailed)


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be pushed without making changes"
)
@handle_cli_errors
def push(dry_run: bool):
    """Push local changes to GitLab.

    Uploads locally modified issues to GitLab. Creates new issues for files
    with temporary IDs (T1, T2, etc.) and updates existing issues that have
    been modified locally.
    """
    console.print("\n[bold blue]📤 Pushing to GitLab[/bold blue]\n")

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")
        console.print("[dim]Dry-run mode not yet implemented[/dim]")
        sys.exit(0)

    console.print("[dim]→[/dim] Connecting to GitLab...")
    repo_root, config, _, project = setup_gitlab_client()
    console.print(f"[green]✓[/green] Connected to [bold]{config.full_path}[/bold]\n")

    entities = [
        (Label, "labels", False),  # (entity_class, entity_name, detailed_conflicts)
        (Milestone, "milestones", False),
        (Issue, "issues", True),  # Issues get detailed conflict display
    ]

    results = []
    for entity_class, entity_name, detailed_conflicts in entities:
        console.print(f"[dim]→[/dim] Pushing {entity_name}...")
        with console.status(f"[bold green]Syncing {entity_name}..."):
            result = entity_class.push(project, repo_root)
        results.append((entity_name, result))

        display_push_result(entity_name, result)
        display_push_conflicts(entity_name, result, detailed=detailed_conflicts)

    # Display push summary
    console.print("\n[bold]Push Summary:[/bold]")
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Metric", style="dim")
    table.add_column("Count", justify="right")

    # Calculate totals from all entity results
    total_changes = 0
    total_conflicts = 0
    for entity_name, result in results:
        entity_changes = len(result.created) + len(result.updated) + len(result.deleted)
        total_changes += entity_changes
        total_conflicts += len(result.conflicts)

        # Add row for this entity
        table.add_row(f"{entity_name.capitalize()} Changed", str(entity_changes))

    table.add_row("Conflicts", str(total_conflicts), style="yellow" if total_conflicts > 0 else "")

    console.print(table)

    # Success message
    if total_changes > 0 and total_conflicts == 0:
        console.print(f"\n[green]✓ Successfully pushed {total_changes} change(s)[/green]")
    elif total_changes == 0 and total_conflicts == 0:
        console.print("\n[dim]No local changes to push[/dim]")
    elif total_conflicts > 0:
        console.print("\n[dim]Resolve conflicts and try pushing again.[/dim]")


@click.command()
@click.option(
    "--state", type=click.Choice(["opened", "closed", "all"]), default="opened", help="Filter issues by state"
)
@click.pass_context
@handle_cli_errors
def sync(ctx, state: str):
    """Bidirectional synchronization (pull then push).

    First pulls issues from GitLab to get latest changes, then pushes
    any local modifications back to GitLab.
    """
    console.print("\n[bold blue]🔄 Syncing with GitLab[/bold blue]\n")

    # Step 1: Pull from GitLab
    console.print("[bold]Step 1: Pulling from GitLab[/bold]")
    ctx.invoke(pull, state=state, types=False)

    # Step 2: Push to GitLab
    console.print("\n[bold]Step 2: Pushing to GitLab[/bold]")
    ctx.invoke(push, dry_run=False)
