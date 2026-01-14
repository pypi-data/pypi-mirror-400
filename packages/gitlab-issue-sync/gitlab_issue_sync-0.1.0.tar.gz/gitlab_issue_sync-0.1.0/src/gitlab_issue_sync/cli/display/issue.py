"""Issue display functions."""

from pathlib import Path

from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from ...storage import Issue, Label
from . import console, format_checkboxes


def display_issue_short(issue, repo_path: Path) -> str:
    """Return a short one-line summary: #IID [state, column] - title"""
    state_color = "green" if issue.state == "opened" else "red"
    state_str = f"[{state_color}]{issue.state}[/{state_color}]"

    semantic_labels, kanban_labels = Label.split_semantic_and_kanban(
        issue.labels or [], repo_path
    )
    column_str = f", {kanban_labels[0]}" if kanban_labels else ""

    return f"#{issue.iid} [{state_str}{column_str}] - {issue.title}"


def display_issues_table(
    issues: list,
    label_colors: dict[str, str],
    kanban_columns: list[str],
    no_column: bool = False,
    no_labels: bool = False,
    with_milestone: bool = False,
    with_assignees: bool = False,
    repo_path: Path | None = None,
):
    console.print(f"\n[bold blue]📋 Issues ({len(issues)} found)[/bold blue]\n")

    if not issues:
        console.print("[dim]No issues found matching the specified filters.[/dim]\n")
        return

    table = Table(show_header=True, header_style="bold cyan", expand=True)
    table.add_column("IID", style="cyan", width=6, no_wrap=True)
    table.add_column("Title", style="white", ratio=3)

    if not no_column:
        table.add_column("Column", style="magenta", width=15, no_wrap=True)

    if not no_labels:
        table.add_column("Labels", style="cyan", ratio=1)

    if with_milestone:
        table.add_column("Milestone", style="yellow", ratio=1, no_wrap=True)

    if with_assignees:
        table.add_column("Assignees", style="green", ratio=1, no_wrap=True)

    for issue in issues:
        iid_str = f"#{issue.iid}"
        title = issue.title

        if repo_path:
            semantic_labels, kanban_labels = Label.split_semantic_and_kanban(
                issue.labels or [], repo_path
            )
            column_str = kanban_labels[0] if kanban_labels else "—"
        else:
            # Fallback to inline filtering
            issue_columns = [lbl for lbl in issue.labels if lbl in kanban_columns]
            column_str = issue_columns[0] if issue_columns else "—"
            semantic_labels = [lbl for lbl in issue.labels if lbl not in kanban_columns]

        if semantic_labels:
            formatted_labels = []
            for lbl in semantic_labels[:3]:  # Show max 3 labels
                if lbl in label_colors and label_colors[lbl]:
                    color = label_colors[lbl]
                    formatted_labels.append(f"[{color}]███[/{color}] {lbl}")
                else:
                    formatted_labels.append(lbl)

            labels_str = ", ".join(formatted_labels)
            if len(semantic_labels) > 3:
                labels_str += f", [dim]+{len(semantic_labels) - 3} more[/dim]"
        else:
            labels_str = "—"

        row_data = [iid_str, title]

        if not no_column:
            row_data.append(column_str)

        if not no_labels:
            row_data.append(labels_str)

        if with_milestone:
            milestone_str = issue.milestone if issue.milestone else "—"
            row_data.append(milestone_str)

        if with_assignees:
            assignees_str = ", ".join(issue.assignees) if issue.assignees else "—"
            row_data.append(assignees_str)

        table.add_row(*row_data)

    console.print(table)
    console.print(f"\n[dim]Showing {len(issues)} of {len(issues)} issues[/dim]\n")


def display_issue(issue, label_colors: dict[str, str], repo_path: Path):
    # Display header
    console.print(f"\n[bold blue]📋 Issue #{issue.iid}[/bold blue]\n")

    # Display title
    console.print(f"[bold cyan]{issue.title}[/bold cyan]\n")

    # Metadata table
    header_table = Table.grid(padding=(0, 2))
    header_table.add_column(style="bold")
    header_table.add_column()

    header_table.add_row("IID:", f"#{issue.iid}")
    state_color = "green" if issue.state == "opened" else "red"
    header_table.add_row("State:", f"[{state_color}]{issue.state}[/{state_color}]")

    if issue.author:
        header_table.add_row("Author:", issue.author)

    if issue.created_at:
        header_table.add_row("Created:", issue.created_at.strftime("%Y-%m-%d %H:%M:%S"))

    if issue.updated_at:
        header_table.add_row("Updated:", issue.updated_at.strftime("%Y-%m-%d %H:%M:%S"))

    # Separate Kanban column labels from semantic labels (single pass)
    if issue.labels:
        semantic_labels, column_labels = Label.split_semantic_and_kanban(issue.labels, repo_path)

        # Display Kanban column (if any)
        if column_labels:
            column_str = ", ".join(f"[bold magenta]{label}[/bold magenta]" for label in column_labels)
            header_table.add_row("Column:", column_str)

        # Display semantic labels with colors
        if semantic_labels:
            formatted_labels = []
            for label in semantic_labels:
                if label in label_colors and label_colors[label]:
                    color = label_colors[label]
                    formatted_labels.append(f"[{color}]███[/{color}] [cyan]{label}[/cyan]")
                else:
                    formatted_labels.append(f"[cyan]{label}[/cyan]")
            labels_str = ", ".join(formatted_labels)
            header_table.add_row("Labels:", labels_str)

    if issue.assignees:
        assignees_str = ", ".join(issue.assignees)
        header_table.add_row("Assignees:", assignees_str)

    if issue.milestone:
        header_table.add_row("Milestone:", issue.milestone)

    if issue.confidential:
        header_table.add_row("⚠️  Confidential:", "[yellow]Yes[/yellow]")

    if issue.web_url:
        header_table.add_row("URL:", f"[link={issue.web_url}]{issue.web_url}[/link]")

    console.print(header_table)
    console.print()

    # Work Item Hierarchy
    if issue.parent_iid is not None or issue.child_iids:
        console.print("[bold]Hierarchy[/bold]\n")

        if issue.parent_iid is not None:
            console.print("  [cyan]Parent:[/cyan]")
            # Try to load the parent issue and display short summary
            try:
                parent_issue = Issue.load(issue.parent_iid, repo_path)
                if parent_issue:
                    issue_summary = display_issue_short(parent_issue, repo_path)
                    console.print(f"    • {issue_summary}")
                else:
                    console.print(f"    • #{issue.parent_iid}")
            except Exception:
                # If we can't load the issue, just show the IID
                console.print(f"    • #{issue.parent_iid}")

        if issue.child_iids:
            console.print("  [cyan]Children:[/cyan]")
            for child_iid in issue.child_iids:
                # Try to load the child issue and display short summary
                try:
                    child_issue = Issue.load(child_iid, repo_path)
                    if child_issue:
                        issue_summary = display_issue_short(child_issue, repo_path)
                        console.print(f"    • {issue_summary}")
                    else:
                        console.print(f"    • #{child_iid}")
                except Exception:
                    # If we can't load the issue, just show the IID
                    console.print(f"    • #{child_iid}")

        console.print()

    # Linked Issues
    if issue.links:
        # Group links by type
        links_by_type = {}
        for link in issue.links:
            if link.link_type not in links_by_type:
                links_by_type[link.link_type] = []
            links_by_type[link.link_type].append(link)

        console.print("[bold]Linked Issues[/bold]\n")
        for link_type, links in sorted(links_by_type.items()):
            type_display = link_type.replace("_", " ").title()
            console.print(f"  [cyan]{type_display}:[/cyan]")

            for link in links:
                # Try to load the linked issue and display short summary
                try:
                    linked_issue = Issue.load(link.target_issue_iid, repo_path)
                    if linked_issue:
                        issue_summary = display_issue_short(linked_issue, repo_path)
                        console.print(f"    • {issue_summary}")
                    else:
                        console.print(f"    • #{link.target_issue_iid}")
                except Exception:
                    # If we can't load the issue, just show the IID
                    console.print(f"    • #{link.target_issue_iid}")

        console.print()

    # Description
    if issue.description:
        formatted_desc = format_checkboxes(issue.description.strip())
        md = Markdown(formatted_desc)
        console.print(Panel(
            md,
            title="[bold]Description[/bold]",
            border_style="blue",
            box=box.ROUNDED,
        ))
        console.print()

    # Comments
    if issue.comments:
        console.print(f"[bold]Comments ({len(issue.comments)})[/bold]\n")
        for i, comment in enumerate(issue.comments, 1):
            timestamp = comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
            formatted_comment = format_checkboxes(comment.body.strip())
            comment_md = Markdown(formatted_comment)
            console.print(Panel(
                comment_md,
                title=f"[bold]{comment.author}[/bold] - {timestamp}",
                border_style="dim",
                box=box.ROUNDED,
            ))
            if i < len(issue.comments):
                console.print()
    else:
        console.print("[dim]No comments[/dim]")

    console.print()
