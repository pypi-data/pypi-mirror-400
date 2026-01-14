"""Wiki repository management commands."""

import sys

import click
from git import Repo

from .display import console, console_err
from ..exit_codes import EXIT_API_ERROR, EXIT_CONFIG_ERROR, EXIT_GENERAL_ERROR
from ..git_utils import find_project_root, get_gitlab_remote_info
from . import handle_cli_errors, main


@main.group()
def wiki():
    """Manage GitLab project wiki repository.

    GitLab wikis are separate git repositories that can be cloned locally
    as a wiki/ subdirectory. This allows offline editing and standard git
    workflows for documentation.
    """
    pass


@wiki.command(name="clone")
@handle_cli_errors
def wiki_clone():
    """Clone the wiki repository into wiki/ subdirectory.

    Clones the GitLab wiki repository (project.wiki.git) into the wiki/
    directory. The wiki is a separate git repository that contains only
    markdown files.

    After cloning, you can edit wiki files directly and use standard git
    commands, or use the wiki pull/push/commit commands for convenience.

    Example:
        gl-issue-sync wiki clone
    """
    from ..wiki import WikiAlreadyExistsError, WikiCloneError, clone_wiki, get_wiki_url

    repo_root = find_project_root()
    remote_info = get_gitlab_remote_info(repo_root)

    console.print("\n[bold blue]📖 Cloning Wiki Repository[/bold blue]\n")
    console.print(f"[dim]→[/dim] Project: [bold]{remote_info.full_path}[/bold]")

    # Get wiki URL for display
    main_repo = Repo(repo_root)
    project_url = main_repo.remotes.origin.url
    wiki_url = get_wiki_url(project_url)
    console.print(f"[dim]→[/dim] Wiki URL: {wiki_url}")

    try:
        console.print("\n[dim]→[/dim] Cloning wiki repository...")
        wiki_path = clone_wiki(repo_root)
        console.print(f"[green]✓[/green] Wiki cloned successfully to: [bold]{wiki_path}[/bold]")
        console.print("\n[dim]You can now edit wiki files in wiki/ and use:[/dim]")
        console.print("[dim]  • gl-issue-sync wiki commit -m \"message\"[/dim]")
        console.print("[dim]  • gl-issue-sync wiki push[/dim]")
        console.print("[dim]  • Or use standard git commands in wiki/[/dim]\n")
    except WikiAlreadyExistsError as e:
        console_err.print(f"\n[yellow]⚠ Wiki already exists:[/yellow] {e}")
        sys.exit(0)  # Not an error, just informational
    except WikiCloneError as e:
        console_err.print(f"\n[bold red]✗ Clone failed:[/bold red] {e}")
        sys.exit(EXIT_API_ERROR)


@wiki.command(name="pull")
@handle_cli_errors
def wiki_pull():
    """Pull latest wiki changes from GitLab.

    Fetches and merges any changes from the remote wiki repository.
    Equivalent to running 'git pull' in the wiki/ directory.

    Example:
        gl-issue-sync wiki pull
    """
    from ..wiki import WikiNotClonedError, WikiSyncError, pull_wiki

    repo_root = find_project_root()

    console.print("\n[bold blue]⬇️  Pulling Wiki Changes[/bold blue]\n")

    try:
        result = pull_wiki(repo_root)
        console.print(f"[green]✓[/green] {result}\n")
    except WikiNotClonedError as e:
        console_err.print(f"\n[bold red]✗ Wiki not cloned:[/bold red] {e}")
        console_err.print("[dim]Run 'gl-issue-sync wiki clone' first.[/dim]")
        sys.exit(EXIT_CONFIG_ERROR)
    except WikiSyncError as e:
        console_err.print(f"\n[bold red]✗ Pull failed:[/bold red] {e}")
        sys.exit(EXIT_API_ERROR)


@wiki.command(name="push")
@handle_cli_errors
def wiki_push():
    """Push local wiki changes to GitLab.

    Pushes committed wiki changes to the remote repository.
    Equivalent to running 'git push' in the wiki/ directory.

    Note: Changes must be committed first. Use 'wiki commit' or
    standard git commands to commit before pushing.

    Example:
        gl-issue-sync wiki push
    """
    from ..wiki import WikiNotClonedError, WikiSyncError, push_wiki

    repo_root = find_project_root()

    console.print("\n[bold blue]⬆️  Pushing Wiki Changes[/bold blue]\n")

    try:
        result = push_wiki(repo_root)
        console.print(f"[green]✓[/green] {result}\n")
    except WikiNotClonedError as e:
        console_err.print(f"\n[bold red]✗ Wiki not cloned:[/bold red] {e}")
        console_err.print("[dim]Run 'gl-issue-sync wiki clone' first.[/dim]")
        sys.exit(EXIT_CONFIG_ERROR)
    except WikiSyncError as e:
        console_err.print(f"\n[bold red]✗ Push failed:[/bold red] {e}")
        sys.exit(EXIT_API_ERROR)


@wiki.command(name="commit")
@click.option("-m", "--message", required=True, help="Commit message")
@handle_cli_errors
def wiki_commit(message: str):
    """Commit all wiki changes with a message.

    Stages all changes (new, modified, deleted files) in the wiki/
    directory and commits them with the provided message.

    Equivalent to running 'git add -A && git commit -m "message"'
    in the wiki/ directory.

    Example:
        gl-issue-sync wiki commit -m "Updated documentation"
    """
    from ..wiki import WikiNotClonedError, WikiSyncError, commit_wiki

    repo_root = find_project_root()

    console.print("\n[bold blue]📝 Committing Wiki Changes[/bold blue]\n")

    try:
        result = commit_wiki(repo_root, message)
        console.print(f"[green]✓[/green] {result}\n")
    except WikiNotClonedError as e:
        console_err.print(f"\n[bold red]✗ Wiki not cloned:[/bold red] {e}")
        console_err.print("[dim]Run 'gl-issue-sync wiki clone' first.[/dim]")
        sys.exit(EXIT_CONFIG_ERROR)
    except WikiSyncError as e:
        console_err.print(f"\n[bold red]✗ Commit failed:[/bold red] {e}")
        sys.exit(EXIT_GENERAL_ERROR)
    except ValueError as e:
        console_err.print(f"\n[bold red]✗ Invalid message:[/bold red] {e}")
        sys.exit(EXIT_GENERAL_ERROR)


@wiki.command(name="status")
@handle_cli_errors
def wiki_status():
    """Show wiki repository status.

    Displays information about the wiki repository including:
    - Whether wiki is cloned
    - Current branch
    - Uncommitted changes

    Example:
        gl-issue-sync wiki status
    """
    from ..wiki import get_wiki_status

    repo_root = find_project_root()
    status = get_wiki_status(repo_root)

    console.print("\n[bold blue]📊 Wiki Status[/bold blue]\n")

    if not status["cloned"]:
        console.print("[yellow]Wiki not cloned[/yellow]")
        console.print(f"[dim]Expected path: {status['path']}[/dim]")
        console.print("\n[dim]Run 'gl-issue-sync wiki clone' to clone the wiki.[/dim]\n")
        return

    console.print(f"[bold]Path:[/bold] {status['path']}")
    console.print(f"[bold]Branch:[/bold] {status['branch']}")

    if status["dirty"]:
        console.print("\n[yellow]⚠ Uncommitted changes:[/yellow]")
        if status["modified"]:
            console.print(f"  Modified: {status['modified']} file(s)")
        if status["untracked"]:
            console.print(f"  Untracked: {status['untracked']} file(s)")
        console.print("\n[dim]Use 'gl-issue-sync wiki commit -m \"message\"' to commit changes.[/dim]")
    else:
        console.print("\n[green]✓ Wiki is clean (no uncommitted changes)[/green]")

    console.print()
