"""Init command for GitLab issue synchronization."""

import os

import click
from rich import box
from rich.panel import Panel

from .display import console, console_err
from ..config import (
    BoardConfig,
    ProjectConfig,
    get_config_file_path,
    get_project_config_for_repo,
    save_project_config,
)
from ..git_utils import find_project_root, get_gitlab_remote_info
from ..graphql import GitLabGraphQLClient
from ..issue_sync import get_gitlab_client, get_project
from ..storage import (
    Label,
    Milestone,
    WorkItemTypeCache,
    ensure_storage_structure,
)
from . import handle_cli_errors


@click.command()
@click.option("--token", help="GitLab personal access token (or use GITLAB_TOKEN env var)")
@click.option("--url", help="GitLab instance URL (auto-detected from git remote if not provided)")
@handle_cli_errors
def init(token: str | None, url: str | None):
    """Initialize repository for GitLab issue synchronization.

    This command:
    - Detects GitLab instance from .git/config
    - Prompts for personal access token
    - Validates API access
    - Fetches kanban board columns
    - Creates .issues/ directory structure
    - Saves configuration
    """
    console.print("\n[bold blue]🔧 Initializing GitLab Issue Sync[/bold blue]\n")

    # Step 1: Detect git remote
    console.print("[dim]→[/dim] Detecting GitLab remote from .git/config...")
    repo_root = find_project_root()
    remote_info = get_gitlab_remote_info(repo_root)

    instance_url = url or remote_info.instance_url
    namespace = remote_info.namespace
    project_name = remote_info.project

    console.print(f"[green]✓[/green] Found GitLab project: [bold]{namespace}/{project_name}[/bold]")
    console.print(f"[dim]  Instance: {instance_url}[/dim]\n")

    # Step 1.5: Check for existing configuration
    existing_config = get_project_config_for_repo(repo_root)
    is_reinit = existing_config is not None

    if is_reinit:
        console.print("[dim]→[/dim] Found existing configuration")
        console.print("[dim]  Re-initializing will refresh caches and update settings[/dim]\n")

    # Step 2: Get access token
    access_token = token or os.getenv("GITLAB_TOKEN")

    # If no token provided via CLI or env, try existing config
    if not access_token and existing_config:
        access_token = existing_config.token
        console.print("[green]✓[/green] Reusing existing GitLab token from configuration\n")

    if not access_token:
        console.print("[yellow]GitLab Personal Access Token Required[/yellow]")
        console.print(f"[dim]Create one at: {instance_url}/-/profile/personal_access_tokens[/dim]")
        console.print("[dim]Required scope: api[/dim]\n")
        access_token = click.prompt("Enter your GitLab token", hide_input=True)

    # Step 3: Validate token by connecting to GitLab
    console.print("\n[dim]→[/dim] Validating API access...")
    # Create temporary config for validation
    temp_config = ProjectConfig(
        token=access_token,
        instance_url=instance_url,
        namespace=namespace,
        project=project_name,
    )
    gitlab_client = get_gitlab_client(temp_config)
    project = get_project(gitlab_client, temp_config)

    # Fetch username for comment/issue creation
    current_user = gitlab_client.user
    username = current_user.username

    console.print("[green]✓[/green] Successfully connected to GitLab")
    console.print(f"[dim]  Project ID: {project.id}[/dim]")
    console.print(f"[dim]  Project URL: {project.web_url}[/dim]")
    console.print(f"[dim]  Username: {username}[/dim]\n")

    # Step 4: Fetch kanban board columns (if available)
    console.print("[dim]→[/dim] Fetching kanban board configuration...")
    try:
        # Try to get board labels - GitLab API boards endpoint
        boards = project.boards.list()
        columns = []
        if boards:
            board = boards[0]  # Use first board
            for board_list in board.lists.list():
                if hasattr(board_list, 'label') and board_list.label:
                    columns.append(board_list.label['name'])

        if columns:
            console.print(f"[green]✓[/green] Found {len(columns)} kanban columns: {', '.join(columns)}")
        else:
            console.print("[yellow]⚠[/yellow] No kanban board columns found (this is optional)")
            columns = []
    except Exception as e:
        console_err.print(f"[yellow]⚠[/yellow] Could not fetch board columns: {e}")
        console_err.print("[dim]  (Kanban features will be limited)[/dim]")
        columns = []

    # Step 5: Create directory structure
    console_err.print("\n[dim]→[/dim] Creating .issues/ directory structure...")
    ensure_storage_structure(repo_root)
    console_err.print("[green]✓[/green] Directory structure created")

    # Step 5.5: Fetch and cache labels
    console_err.print("\n[dim]→[/dim] Fetching and caching project labels...")
    try:
        label_result = Label.pull(project, repo_root)
        total_labels = len(label_result.created) + len(label_result.updated)
        console_err.print(f"[green]✓[/green] Cached {total_labels} labels")
    except Exception as e:
        console_err.print(f"[yellow]⚠[/yellow] Could not fetch labels: {e}")
        console_err.print("[dim]  (Label features will be limited)[/dim]")

    # Step 5.6: Fetch and cache milestones
    console_err.print("\n[dim]→[/dim] Fetching and caching project milestones...")
    try:
        milestone_result = Milestone.pull(project, repo_root)
        total_milestones = len(milestone_result.created) + len(milestone_result.updated)
        console_err.print(f"[green]✓[/green] Cached {total_milestones} milestones")
    except Exception as e:
        console_err.print(f"[yellow]⚠[/yellow] Could not fetch milestones: {e}")
        console_err.print("[dim]  (Milestone features will be limited)[/dim]")

    # Step 5.7: Fetch and cache work item types (for parent-child hierarchy)
    console_err.print("\n[dim]→[/dim] Fetching and caching work item types...")
    total_work_item_types = 0
    try:
        graphql_client = GitLabGraphQLClient(instance_url, access_token)
        type_cache = WorkItemTypeCache.fetch_and_save(
            graphql_client, f"{namespace}/{project_name}", repo_root
        )
        total_work_item_types = len(type_cache.types)
        console_err.print(f"[green]✓[/green] Cached {total_work_item_types} work item types")
    except Exception as e:
        console_err.print(f"[yellow]⚠[/yellow] Could not fetch work item types: {e}")
        console_err.print("[dim]  (Parent-child hierarchy features may be limited)[/dim]")

    # Step 6: Save configuration
    console_err.print("[dim]→[/dim] Saving configuration...")
    board_config = BoardConfig(columns=columns) if columns else BoardConfig()
    project_config = ProjectConfig(
        token=access_token,
        instance_url=instance_url,
        namespace=namespace,
        project=project_name,
        board=board_config,
        username=username,
    )

    save_project_config(project_config)
    config_path = get_config_file_path()
    console_err.print(f"[green]✓[/green] Configuration saved to: [dim]{config_path}[/dim]\n")

    # Success message
    action = "re-initialized" if is_reinit else "initialized"
    title = "Re-initialization Complete" if is_reinit else "Initialization Complete"

    panel = Panel(
        f"[green]✓ Repository {action} successfully![/green]\n\n"
        f"[bold]Project:[/bold] {namespace}/{project_name}\n"
        f"[bold]Instance:[/bold] {instance_url}\n"
        f"[bold]Kanban Columns:[/bold] {len(columns)} configured\n"
        f"[bold]Labels Cached:[/bold] {total_labels if 'total_labels' in locals() else 0}\n"
        f"[bold]Milestones Cached:[/bold] {total_milestones if 'total_milestones' in locals() else 0}\n"
        f"[bold]Work Item Types:[/bold] {total_work_item_types} cached\n\n"
        f"[dim]Next steps:[/dim]\n"
        f"  • Run [bold cyan]gl-issue-sync pull[/bold cyan] to fetch issues\n"
        f"  • Run [bold cyan]gl-issue-sync status[/bold cyan] to view sync status",
        title=title,
        border_style="green",
        box=box.ROUNDED,
    )
    console_err.print(panel)
