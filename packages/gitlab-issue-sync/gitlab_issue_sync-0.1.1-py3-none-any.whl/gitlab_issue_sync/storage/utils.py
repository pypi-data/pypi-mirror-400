"""Helper functions for storage operations."""

import re
from datetime import datetime
from pathlib import Path

import yaml

from .exceptions import StorageError

# Issue state constants (also available in base.py, but duplicated here for convenience)
ISSUE_STATE_OPENED = "opened"
ISSUE_STATE_CLOSED = "closed"


def state_to_dir(state: str) -> str:
    return state


def get_issues_dir(repo_path: Path | None = None) -> Path:
    if repo_path is None:
        repo_path = Path.cwd()

    return repo_path / ".issues"


def ensure_storage_structure(repo_path: Path | None = None) -> None:
    """
    Ensure the issue storage directory structure exists.

    Creates:
    - .issues/open/
    - .issues/closed/
    - .sync/originals/
    - .issues/attachments/

    Args:
        repo_path: Path to repository root (defaults to current directory)
    """
    issues_dir = get_issues_dir(repo_path)

    dirs_to_create = [
        issues_dir / ISSUE_STATE_OPENED,
        issues_dir / ISSUE_STATE_CLOSED,
        issues_dir / ".sync" / "originals",
        issues_dir / "attachments",
    ]

    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)


def get_next_temporary_id(repo_path: Path | None = None) -> str:
    """
    Get the next available temporary issue ID.

    Scans the .issues/open directory for existing temporary IDs (T1, T2, etc.)
    and returns the next available one.

    Args:
        repo_path: Path to repository root

    Returns:
        Next temporary ID (e.g., "T1", "T2", etc.)
    """
    issues_dir = get_issues_dir(repo_path)
    open_dir = issues_dir / ISSUE_STATE_OPENED

    if not open_dir.exists():
        return "T1"

    temp_pattern = re.compile(r"T(\d+)\.md")
    max_temp_id = 0

    for file_path in open_dir.glob("T*.md"):
        match = temp_pattern.match(file_path.name)
        if match:
            temp_id = int(match.group(1))
            max_temp_id = max(max_temp_id, temp_id)

    return f"T{max_temp_id + 1}"


def serialize_issue(issue: "Issue") -> str:  # type: ignore  # noqa: F821
    """
    Serialize an issue to markdown format with YAML frontmatter.

    Args:
        issue: The issue to serialize

    Returns:
        Markdown string with YAML frontmatter
    """
    # Import here to avoid circular dependency
    from .issue import Issue  # noqa: F401

    frontmatter = {
        "iid": issue.iid,
        "title": issue.title,
        "state": issue.state,
        "confidential": issue.confidential,
    }

    if issue.labels:
        frontmatter["labels"] = issue.labels

    if issue.assignees:
        frontmatter["assignees"] = issue.assignees

    if issue.milestone:
        frontmatter["milestone"] = issue.milestone

    if issue.created_at:
        frontmatter["created_at"] = issue.created_at.isoformat()

    if issue.updated_at:
        frontmatter["updated_at"] = issue.updated_at.isoformat()

    if issue.author:
        frontmatter["author"] = issue.author

    if issue.web_url:
        frontmatter["web_url"] = issue.web_url

    if issue.global_id:
        frontmatter["global_id"] = issue.global_id

    if issue.links:
        frontmatter["links"] = [
            {
                "link_id": link.link_id,
                "target_project_id": link.target_project_id,
                "target_issue_iid": link.target_issue_iid,
                "link_type": link.link_type,
                "created_at": link.created_at.isoformat(),
                "updated_at": link.updated_at.isoformat(),
            }
            for link in issue.links
        ]

    # Include work item hierarchy
    if issue.parent_iid is not None:
        frontmatter["parent_iid"] = issue.parent_iid

    if issue.child_iids:
        frontmatter["child_iids"] = issue.child_iids

    # Include work item type (read-only)
    if issue.work_item_type is not None:
        frontmatter["work_item_type"] = {
            "id": issue.work_item_type.id,
            "name": issue.work_item_type.name,
            "icon_name": issue.work_item_type.icon_name,
        }

    frontmatter_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)

    lines = [
        "---",
        frontmatter_str.strip(),
        "---",
        issue.description,
    ]

    if issue.comments:
        lines.extend(["", "## Comments", ""])

        for comment in issue.comments:
            # Use ISO format to preserve microsecond precision (see issue #119)
            timestamp_str = comment.created_at.isoformat()
            lines.extend([f"### {comment.author} - {timestamp_str}", "", comment.body, ""])

    return "\n".join(lines)


def parse_issue(content: str) -> "Issue":  # type: ignore  # noqa: F821
    """
    Parse an issue from markdown format with YAML frontmatter.

    Args:
        content: Markdown content with YAML frontmatter

    Returns:
        Parsed Issue object

    Raises:
        StorageError: If content cannot be parsed
    """
    # Import here to avoid circular dependency
    from .issue import Issue, IssueComment, IssueLink, WorkItemType  # noqa: E501

    frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if not match:
        raise StorageError("Invalid issue format: missing YAML frontmatter")

    frontmatter_str = match.group(1)
    body_str = match.group(2)

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        raise StorageError(f"Invalid YAML frontmatter: {e}") from e

    # Find ## Comments section, skipping code blocks (even indices are outside code blocks)
    parts = body_str.split("```")
    comments_pos = -1
    char_offset = 0

    for i, part in enumerate(parts):
        if i % 2 == 0:  # Outside code block
            pos = part.find("\n## Comments\n")
            if pos != -1:
                comments_pos = char_offset + pos
                break
        char_offset += len(part) + 3  # +3 for "```"

    if comments_pos != -1:
        description_part = body_str[:comments_pos].strip()
        comments_part = body_str[comments_pos + len("\n## Comments\n"):]
    else:
        description_part = body_str.strip()
        comments_part = ""
    description_lines = description_part.split("\n")
    if description_lines and description_lines[0].startswith("# "):
        description_lines = description_lines[1:]

    description = "\n".join(description_lines).strip()

    comments = []
    if comments_part:
        # Match comment sections: ### author - timestamp
        # Author must not contain newlines: [^\n]+?
        # Timestamp supports both formats:
        #   - Old format: YYYY-MM-DD HH:MM:SS
        #   - ISO format: YYYY-MM-DDTHH:MM:SS.microseconds+timezone
        # This prevents false matches on markdown headers (e.g., "### Section\n - bullet")
        comment_pattern = r"### ([^\n]+?) - (\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d{6})?(?:[+-]\d{2}:\d{2})?)\n\n(.*?)(?=\n### [^\n]+? - \d{4}|\Z)"

        # Track matched ranges to detect unparsed content
        matched_ranges: list[tuple[int, int]] = []

        for match in re.finditer(comment_pattern, comments_part, re.DOTALL):
            matched_ranges.append((match.start(), match.end()))

            author = match.group(1)
            timestamp_str = match.group(2)
            body = match.group(3).strip()

            try:
                created_at = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Fallback to ISO format
                created_at = datetime.fromisoformat(timestamp_str)

            comments.append(IssueComment(author=author, created_at=created_at, body=body))

        # Check for unparsed content between/around matched comments
        # Build a string of all unmatched content
        unmatched_parts = []
        pos = 0
        for start, end in sorted(matched_ranges):
            if pos < start:
                unmatched_parts.append(comments_part[pos:start])
            pos = end
        if pos < len(comments_part):
            unmatched_parts.append(comments_part[pos:])

        unparsed_content = "".join(unmatched_parts).strip()
        if unparsed_content:
            raise StorageError(
                f"Unparsed content found under '## Comments' section:\n\n"
                f"{unparsed_content[:200]}{'...' if len(unparsed_content) > 200 else ''}\n\n"
                f"Comments must follow the format '### author - YYYY-MM-DDTHH:MM:SS' followed by a blank line.\n"
                f"Use 'gl-issue-sync comment <iid> \"message\"' to add comments instead of manual editing."
            )

    links = []
    if "links" in frontmatter and frontmatter["links"]:
        for link_data in frontmatter["links"]:
            link = IssueLink(
                link_id=link_data["link_id"],
                target_project_id=link_data["target_project_id"],
                target_issue_iid=link_data["target_issue_iid"],
                link_type=link_data["link_type"],
                created_at=datetime.fromisoformat(link_data["created_at"]),
                updated_at=datetime.fromisoformat(link_data["updated_at"]),
            )
            links.append(link)

    work_item_type = None
    if wit_data := frontmatter.get("work_item_type"):
        work_item_type = WorkItemType(
            id=wit_data["id"],
            name=wit_data["name"],
            icon_name=wit_data.get("icon_name"),
        )

    issue = Issue(
        iid=frontmatter["iid"],
        title=frontmatter["title"],
        state=frontmatter["state"],
        description=description,
        confidential=frontmatter.get("confidential", False),
        labels=frontmatter.get("labels", []),
        assignees=frontmatter.get("assignees", []),
        milestone=frontmatter.get("milestone"),
        author=frontmatter.get("author"),
        web_url=frontmatter.get("web_url"),
        global_id=frontmatter.get("global_id"),
        comments=comments,
        links=links,
        parent_iid=frontmatter.get("parent_iid"),
        child_iids=frontmatter.get("child_iids", []),
        work_item_type=work_item_type,
    )

    if "created_at" in frontmatter and frontmatter["created_at"]:
        created_at_value = frontmatter["created_at"]
        if isinstance(created_at_value, datetime):
            issue.created_at = created_at_value
        else:
            issue.created_at = datetime.fromisoformat(created_at_value)

    if "updated_at" in frontmatter and frontmatter["updated_at"]:
        updated_at_value = frontmatter["updated_at"]
        if isinstance(updated_at_value, datetime):
            issue.updated_at = updated_at_value
        else:
            issue.updated_at = datetime.fromisoformat(updated_at_value)

    return issue
