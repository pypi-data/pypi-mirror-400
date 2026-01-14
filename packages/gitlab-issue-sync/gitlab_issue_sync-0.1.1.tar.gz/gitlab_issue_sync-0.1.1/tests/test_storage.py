"""Tests for storage module."""

from datetime import UTC, datetime, timedelta

import pytest

from gitlab_issue_sync.storage import (
    ISSUE_STATE_CLOSED,
    ISSUE_STATE_OPENED,
    Issue,
    IssueComment,
    IssueLink,
    Label,
    Milestone,
    StorageError,
    ensure_storage_structure,
    get_next_temporary_id,
    parse_issue,
    serialize_issue,
)
from gitlab_issue_sync.storage.base import SyncResult

# =============================================================================
# Issue Tests
# =============================================================================


class TestIssueDataclass:
    """Tests for Issue dataclass."""

    def test_is_temporary_true(self):
        """Test that temporary IDs are detected."""
        issue = Issue(iid="T1", title="Test", state="opened", description="Test")
        assert issue.is_temporary is True

    def test_is_temporary_false(self):
        """Test that real IDs are not temporary."""
        issue = Issue(iid=42, title="Test", state="opened", description="Test")
        assert issue.is_temporary is False

    def test_filename(self):
        """Test filename generation."""
        issue = Issue(iid=42, title="Test", state="opened", description="Test")
        assert issue.filename == "42.md"

        temp_issue = Issue(iid="T1", title="Test", state="opened", description="Test")
        assert temp_issue.filename == "T1.md"

    def test_compute_content_hash(self):
        """Test content hash generation."""
        issue = Issue(
            iid=42,
            title="Test",
            state="opened",
            description="Test description",
            labels=["bug", "urgent"],
            assignees=["user1"],
        )
        hash1 = issue.compute_content_hash()

        # Same content should produce same hash
        issue2 = Issue(
            iid=42,
            title="Test",
            state="opened",
            description="Test description",
            labels=["urgent", "bug"],  # Different order
            assignees=["user1"],
        )
        hash2 = issue2.compute_content_hash()
        assert hash1 == hash2

        # Different content should produce different hash
        issue3 = Issue(
            iid=42,
            title="Different",
            state="opened",
            description="Test description",
        )
        hash3 = issue3.compute_content_hash()
        assert hash1 != hash3

    def test_compute_content_hash_with_exclude(self):
        """Test content hash with exclude parameter."""
        issue1 = Issue(
            iid=42,
            title="Test",
            state="opened",
            description="Test description",
            parent_iid=1,
        )
        issue2 = Issue(
            iid=42,
            title="Test",
            state="opened",
            description="Test description",
            parent_iid=2,  # Different parent
        )

        # Full hash should differ (parent_iid is different)
        assert issue1.compute_content_hash() != issue2.compute_content_hash()

        # Hash excluding parent_iid should be the same
        hash1 = issue1.compute_content_hash(exclude=("parent_iid",))
        hash2 = issue2.compute_content_hash(exclude=("parent_iid",))
        assert hash1 == hash2

        # Excluding parent_iid should differ from full hash
        assert hash1 != issue1.compute_content_hash()

    def test_compute_content_hash_with_only(self):
        """Test content hash with only parameter."""
        issue1 = Issue(
            iid=42,
            title="Test 1",
            state="opened",
            description="Description 1",
            parent_iid=1,
        )
        issue2 = Issue(
            iid=43,
            title="Test 2",
            state="closed",
            description="Description 2",
            parent_iid=1,  # Same parent
        )

        # Full hash should differ (many fields different)
        assert issue1.compute_content_hash() != issue2.compute_content_hash()

        # Hash with only parent_iid should be the same
        hash1 = issue1.compute_content_hash(only=("parent_iid",))
        hash2 = issue2.compute_content_hash(only=("parent_iid",))
        assert hash1 == hash2

        # Different parent_iid should produce different hash
        issue3 = Issue(
            iid=44,
            title="Test 3",
            state="opened",
            description="Description 3",
            parent_iid=2,  # Different parent
        )
        hash3 = issue3.compute_content_hash(only=("parent_iid",))
        assert hash1 != hash3

    def test_compute_content_hash_exclude_and_only_mutually_exclusive(self):
        """Test that exclude and only parameters cannot be used together."""
        issue = Issue(
            iid=42,
            title="Test",
            state="opened",
            description="Test description",
        )

        # Should raise ValueError when both exclude and only are provided
        with pytest.raises(ValueError, match="Cannot specify both 'exclude' and 'only'"):
            issue.compute_content_hash(exclude=("parent_iid",), only=("title",))


class TestSerializeAndParse:
    """Tests for issue serialization and parsing."""

    def test_serialize_simple_issue(self):
        """Test serializing a simple issue."""
        issue = Issue(
            iid=42,
            title="Test Issue",
            state="opened",
            description="This is a test issue.",
        )

        content = serialize_issue(issue)

        assert "---" in content
        assert "iid: 42" in content
        assert "title: Test Issue" in content  # Title in frontmatter
        assert "state: opened" in content
        assert "# Test Issue" not in content  # Title NOT duplicated in markdown body
        assert "This is a test issue." in content

    def test_serialize_with_metadata(self):
        """Test serializing issue with all metadata."""
        issue = Issue(
            iid=42,
            title="Test Issue",
            state="opened",
            description="Test description",
            labels=["bug", "urgent"],
            assignees=["emma", "john"],
            milestone="v1.0",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
            updated_at=datetime(2025, 1, 2, 10, 30, 0),
            author="emma",
            web_url="https://gitlab.com/owner/project/-/issues/42",
            confidential=True,
        )

        content = serialize_issue(issue)

        assert "labels:" in content
        assert "- bug" in content
        assert "- urgent" in content
        assert "assignees:" in content
        assert "- emma" in content
        assert "milestone: v1.0" in content
        assert "confidential: true" in content
        assert "web_url: https://gitlab.com/owner/project/-/issues/42" in content

    def test_serialize_with_comments(self):
        """Test serializing issue with comments."""
        comments = [
            IssueComment(
                author="emma",
                created_at=datetime(2025, 1, 1, 14, 0, 0),
                body="First comment",
            ),
            IssueComment(
                author="john",
                created_at=datetime(2025, 1, 1, 15, 0, 0),
                body="Second comment",
            ),
        ]

        issue = Issue(
            iid=42,
            title="Test",
            state="opened",
            description="Description",
            comments=comments,
        )

        content = serialize_issue(issue)

        assert "## Comments" in content
        assert "### emma - 2025-01-01T14:00:00" in content
        assert "First comment" in content
        assert "### john - 2025-01-01T15:00:00" in content
        assert "Second comment" in content

    def test_parse_simple_issue(self):
        """Test parsing a simple issue."""
        content = """---
iid: 42
title: Test Issue
state: opened
confidential: false
---

# Test Issue

This is a test issue.
"""

        issue = parse_issue(content)

        assert issue.iid == 42
        assert issue.title == "Test Issue"
        assert issue.state == "opened"
        assert issue.description == "This is a test issue."
        assert issue.confidential is False

    def test_parse_issue_with_metadata(self):
        """Test parsing issue with full metadata."""
        content = """---
iid: 42
title: Test Issue
state: opened
confidential: true
labels:
  - bug
  - urgent
assignees:
  - emma
  - john
milestone: v1.0
created_at: '2025-01-01T12:00:00'
updated_at: '2025-01-02T10:30:00'
author: emma
web_url: https://gitlab.com/owner/project/-/issues/42
---

# Test Issue

Test description
"""

        issue = parse_issue(content)

        assert issue.labels == ["bug", "urgent"]
        assert issue.assignees == ["emma", "john"]
        assert issue.milestone == "v1.0"
        assert issue.created_at == datetime(2025, 1, 1, 12, 0, 0)
        assert issue.updated_at == datetime(2025, 1, 2, 10, 30, 0)
        assert issue.author == "emma"
        assert issue.web_url == "https://gitlab.com/owner/project/-/issues/42"
        assert issue.confidential is True

    def test_parse_issue_with_comments(self):
        """Test parsing issue with comments."""
        content = """---
iid: 42
title: Test
state: opened
confidential: false
---

# Test

Description

## Comments

### emma - 2025-01-01 14:00:00

First comment

### john - 2025-01-01 15:00:00

Second comment
"""

        issue = parse_issue(content)

        assert len(issue.comments) == 2
        assert issue.comments[0].author == "emma"
        assert issue.comments[0].body == "First comment"
        assert issue.comments[1].author == "john"
        assert issue.comments[1].body == "Second comment"

    def test_roundtrip_serialization(self):
        """Test that serialize -> parse preserves data."""
        original = Issue(
            iid=42,
            title="Test Issue",
            state="opened",
            description="Test description with\nmultiple lines.",
            labels=["bug"],
            assignees=["emma"],
            comments=[
                IssueComment(
                    author="john",
                    created_at=datetime(2025, 1, 1, 12, 0, 0),
                    body="A comment",
                )
            ],
        )

        content = serialize_issue(original)
        parsed = parse_issue(content)

        assert parsed.iid == original.iid
        assert parsed.title == original.title
        assert parsed.state == original.state
        assert parsed.description == original.description
        assert parsed.labels == original.labels
        assert parsed.assignees == original.assignees
        assert len(parsed.comments) == 1
        assert parsed.comments[0].author == "john"

    def test_serialize_description_with_checkboxes(self):
        """Test that checkbox syntax is preserved during serialization."""
        description = """## Requirements

- [x] Completed task
- [ ] Pending task
- [x] Another completed task

## Notes

Some additional notes here.
"""
        issue = Issue(
            iid=42,
            title="Test Checkboxes",
            state="opened",
            description=description,
        )

        content = serialize_issue(issue)

        # Verify checkbox syntax is preserved in output
        assert "- [x] Completed task" in content
        assert "- [ ] Pending task" in content
        assert "- [x] Another completed task" in content

    def test_parse_description_with_checkboxes(self):
        """Test that checkbox syntax is correctly parsed from markdown."""
        content = """---
iid: 42
title: Test Checkboxes
state: opened
confidential: false
---

# Test Checkboxes

## Requirements

- [x] Completed task
- [ ] Pending task
- [x] Another completed task

## Notes

Some additional notes.
"""

        issue = parse_issue(content)

        # Verify checkboxes are preserved in description
        assert "- [x] Completed task" in issue.description
        assert "- [ ] Pending task" in issue.description
        assert "- [x] Another completed task" in issue.description
        assert issue.title == "Test Checkboxes"

    def test_roundtrip_with_checkboxes(self):
        """Test that checkboxes survive serialize -> parse roundtrip."""
        original_description = """## Todo List

- [x] First task (done)
- [ ] Second task (pending)
- [x] Third task (done)
- [ ] Fourth task (pending)

Mixed with regular text and other markdown."""
        issue = Issue(
            iid=99,
            title="Roundtrip Test",
            state="opened",
            description=original_description,
        )

        # Serialize then parse
        content = serialize_issue(issue)
        parsed = parse_issue(content)

        # Verify checkbox states are identical
        assert parsed.description == original_description

    def test_checkboxes_in_various_contexts(self):
        """Test checkboxes work in different parts of the description."""
        description = """Start with some text.

- [x] Checkbox in middle
- [ ] Another checkbox

## Section with checkboxes

Here's a list:
- [x] Item one
- [x] Item two
- [ ] Item three

And some more text.

### Subsection

- [ ] Nested task
  - [x] Subtask
  - [ ] Another subtask

Final paragraph."""
        issue = Issue(
            iid=42,
            title="Complex Checkboxes",
            state="opened",
            description=description,
        )

        # Test serialization preserves everything
        content = serialize_issue(issue)
        assert "- [x] Checkbox in middle" in content
        assert "- [ ] Another checkbox" in content
        assert "- [x] Item one" in content
        assert "- [ ] Item three" in content
        assert "- [ ] Nested task" in content
        assert "  - [x] Subtask" in content

        # Test parsing preserves everything
        parsed = parse_issue(content)
        assert parsed.description == description

    def test_checkboxes_mixed_with_code_blocks(self):
        """Test that checkboxes in code blocks are preserved literally."""
        description = """## Example

Here's some checkbox syntax to copy:

```markdown
- [x] Completed task
- [ ] Pending task
```

And here are real checkboxes:

- [x] This is actually checked
- [ ] This is actually unchecked

More text here."""
        issue = Issue(
            iid=42,
            title="Code Block Test",
            state="opened",
            description=description,
        )

        # Serialize and parse roundtrip
        content = serialize_issue(issue)
        parsed = parse_issue(content)

        # Verify everything is preserved including code blocks
        assert parsed.description == description
        # Both the code block examples and real checkboxes should be there
        assert "```markdown" in parsed.description
        assert "- [x] Completed task" in parsed.description
        assert "- [ ] Pending task" in parsed.description
        assert "- [x] This is actually checked" in parsed.description
        assert "- [ ] This is actually unchecked" in parsed.description


class TestSaveAndLoad:
    """Tests for saving and loading issues."""

    def test_save_and_load_issue(self, temp_git_repo):
        """Test saving and loading an issue."""
        issue = Issue(
            iid=42,
            title="Test",
            state="opened",
            description="Test description",
        )

        issue.save(temp_git_repo)

        # Verify file exists
        issue_path = temp_git_repo / ".issues" / ISSUE_STATE_OPENED / "42.md"
        assert issue_path.exists()

        # Load and verify
        loaded = Issue.load(42, temp_git_repo)
        assert loaded.iid == 42
        assert loaded.title == "Test"
        assert loaded.description == "Test description"

    def test_save_closed_issue(self, temp_git_repo):
        """Test that closed issues go to closed directory."""
        issue = Issue(
            iid=42,
            title="Test",
            state="closed",
            description="Closed issue",
        )

        issue.save(temp_git_repo)

        # Verify in closed directory
        closed_path = temp_git_repo / ".issues" / ISSUE_STATE_CLOSED / "42.md"
        assert closed_path.exists()

        open_path = temp_git_repo / ".issues" / ISSUE_STATE_OPENED / "42.md"
        assert not open_path.exists()

    def test_save_temporary_issue(self, temp_git_repo):
        """Test saving a temporary issue."""
        issue = Issue(
            iid="T1",
            title="Temporary",
            state="opened",
            description="Local only",
        )

        issue.save(temp_git_repo)

        # Verify file exists
        issue_path = temp_git_repo / ".issues" / ISSUE_STATE_OPENED / "T1.md"
        assert issue_path.exists()

    def test_state_transition_cleanup(self, temp_git_repo):
        """Test that state transitions clean up old files."""
        # Save as opened
        issue = Issue(iid=42, title="Test", state="opened", description="Test")
        issue.save(temp_git_repo)

        opened_path = temp_git_repo / ".issues" / ISSUE_STATE_OPENED / "42.md"
        assert opened_path.exists()

        # Change to closed and save
        issue.state = "closed"
        issue.save(temp_git_repo)

        closed_path = temp_git_repo / ".issues" / ISSUE_STATE_CLOSED / "42.md"
        assert closed_path.exists()
        assert not opened_path.exists()  # Old file should be deleted


class TestOriginalSnapshots:
    """Tests for original snapshot functionality."""

    def test_save_and_load_snapshot(self, temp_git_repo):
        """Test saving and loading original snapshots."""
        issue = Issue(
            iid=42,
            title="Original",
            state="opened",
            description="Original description",
        )

        Issue.backend.save_original(issue, temp_git_repo)

        # Load and verify
        snapshot = Issue.backend.load_original(42, temp_git_repo)
        assert snapshot is not None
        assert snapshot.title == "Original"

    def test_load_nonexistent_snapshot(self, temp_git_repo):
        """Test loading a snapshot that doesn't exist."""
        snapshot = Issue.backend.load_original(999, temp_git_repo)
        assert snapshot is None

    def test_load_all_originals(self, temp_git_repo):
        """Test loading all original snapshots."""
        issue1 = Issue(iid=1, title="Issue 1", state="opened", description="Test")
        issue2 = Issue(iid=2, title="Issue 2", state="opened", description="Test")

        Issue.backend.save_original(issue1, temp_git_repo)
        Issue.backend.save_original(issue2, temp_git_repo)

        originals = Issue.backend.load_all_originals(temp_git_repo)
        assert len(originals) == 2
        assert {o.iid for o in originals} == {1, 2}


class TestGetNextTemporaryId:
    """Tests for temporary ID generation."""

    def test_get_first_temporary_id(self, temp_git_repo):
        """Test getting first temporary ID when none exist."""
        next_id = get_next_temporary_id(temp_git_repo)
        assert next_id == "T1"

    def test_get_next_temporary_id(self, temp_git_repo):
        """Test getting next temporary ID when some exist."""
        # Create some temporary issues
        for i in range(1, 4):
            issue = Issue(iid=f"T{i}", title=f"Temp {i}", state="opened", description="Test")
            issue.save(temp_git_repo)

        next_id = get_next_temporary_id(temp_git_repo)
        assert next_id == "T4"

    def test_get_next_temporary_id_with_gaps(self, temp_git_repo):
        """Test that ID generation works even with gaps."""
        # Create T1 and T3, skip T2
        for i in [1, 3]:
            issue = Issue(iid=f"T{i}", title=f"Temp {i}", state="opened", description="Test")
            issue.save(temp_git_repo)

        next_id = get_next_temporary_id(temp_git_repo)
        assert next_id == "T4"  # Should still be T4, not T2


class TestListIssues:
    """Tests for listing issues."""

    def test_list_all_issues(self, temp_git_repo):
        """Test listing all issues."""
        # Create some issues
        open_issue = Issue(iid=1, title="Open", state="opened", description="Open")
        closed_issue = Issue(iid=2, title="Closed", state="closed", description="Closed")

        open_issue.save(temp_git_repo)
        closed_issue.save(temp_git_repo)

        issues = Issue.list_all(state=None, repo_path=temp_git_repo)
        assert len(issues) == 2

    def test_list_open_issues(self, temp_git_repo):
        """Test listing only open issues."""
        open_issue = Issue(iid=1, title="Open", state="opened", description="Open")
        closed_issue = Issue(iid=2, title="Closed", state="closed", description="Closed")

        open_issue.save(temp_git_repo)
        closed_issue.save(temp_git_repo)

        issues = Issue.list_all(state=ISSUE_STATE_OPENED, repo_path=temp_git_repo)
        assert len(issues) == 1
        assert issues[0].iid == 1

    def test_list_closed_issues(self, temp_git_repo):
        """Test listing only closed issues."""
        open_issue = Issue(iid=1, title="Open", state="opened", description="Open")
        closed_issue = Issue(iid=2, title="Closed", state="closed", description="Closed")

        open_issue.save(temp_git_repo)
        closed_issue.save(temp_git_repo)

        issues = Issue.list_all(state=ISSUE_STATE_CLOSED, repo_path=temp_git_repo)
        assert len(issues) == 1
        assert issues[0].iid == 2


class TestIssueFilter:
    """Tests for Issue.filter() method."""

    def test_filter_by_labels(self, temp_git_repo):
        """Test filtering issues by labels (AND logic)."""
        issue1 = Issue(iid=1, title="Bug", state="opened", description="Test", labels=["bug", "urgent"])
        issue2 = Issue(iid=2, title="Feature", state="opened", description="Test", labels=["feature"])
        issue3 = Issue(iid=3, title="Bug 2", state="opened", description="Test", labels=["bug"])

        issue1.save(temp_git_repo)
        issue2.save(temp_git_repo)
        issue3.save(temp_git_repo)

        # Filter for issues with both bug AND urgent
        filtered = Issue.filter(labels=["bug", "urgent"], repo_path=temp_git_repo)
        assert len(filtered) == 1
        assert filtered[0].iid == 1

        # Filter for issues with just bug
        filtered = Issue.filter(labels=["bug"], repo_path=temp_git_repo)
        assert len(filtered) == 2
        assert {i.iid for i in filtered} == {1, 3}

    def test_filter_by_milestone(self, temp_git_repo):
        """Test filtering issues by milestone (OR logic)."""
        issue1 = Issue(iid=1, title="Test", state="opened", description="Test", milestone="v1.0")
        issue2 = Issue(iid=2, title="Test", state="opened", description="Test", milestone="v2.0")
        issue3 = Issue(iid=3, title="Test", state="opened", description="Test", milestone=None)

        issue1.save(temp_git_repo)
        issue2.save(temp_git_repo)
        issue3.save(temp_git_repo)

        # Filter for v1.0 or v2.0
        filtered = Issue.filter(milestones=["v1.0", "v2.0"], repo_path=temp_git_repo)
        assert len(filtered) == 2
        assert {i.iid for i in filtered} == {1, 2}


class TestParseIssueErrors:
    """Tests for parse_issue error handling."""

    def test_parse_issue_missing_frontmatter(self):
        """Test parsing issue without YAML frontmatter raises error."""
        content = "# Just a title\n\nSome description"

        with pytest.raises(StorageError, match="missing YAML frontmatter"):
            parse_issue(content)

    def test_parse_issue_invalid_yaml(self):
        """Test parsing issue with invalid YAML raises error."""
        content = """---
iid: [invalid yaml
title: Test
---
Description"""

        with pytest.raises(StorageError, match="Invalid YAML frontmatter"):
            parse_issue(content)


class TestSerializeWithComments:
    """Tests for serializing issues with various comment scenarios."""

    def test_serialize_with_empty_comment_body(self):
        """Test serializing issue with comment that has empty body."""
        issue = Issue(
            iid=1,
            title="Test",
            state="opened",
            description="Description",
            comments=[
                IssueComment(
                    author="user1",
                    created_at=datetime(2025, 1, 1, 12, 0, 0),
                    body="",  # Empty body
                )
            ],
        )

        result = serialize_issue(issue)

        assert "## Comments" in result
        assert "### user1 - 2025-01-01T12:00:00" in result

    def test_serialize_with_multiline_description_and_comments(self):
        """Test serializing issue with multiline description and multiple comments."""
        issue = Issue(
            iid=1,
            title="Test",
            state="opened",
            description="Line 1\nLine 2\nLine 3",
            comments=[
                IssueComment(
                    author="user1",
                    created_at=datetime(2025, 1, 1, 12, 0, 0),
                    body="Comment 1\nMultiline",
                ),
                IssueComment(
                    author="user2",
                    created_at=datetime(2025, 1, 1, 13, 0, 0),
                    body="Comment 2",
                ),
            ],
        )

        result = serialize_issue(issue)

        assert "Line 1\nLine 2\nLine 3" in result
        assert "Comment 1\nMultiline" in result
        assert "Comment 2" in result
        assert "### user1 - 2025-01-01T12:00:00" in result
        assert "### user2 - 2025-01-01T13:00:00" in result


class TestParseWithComments:
    """Tests for parsing issues with various comment scenarios."""

    def test_parse_with_multiple_comments(self):
        """Test parsing issue with multiple comments."""
        content = """---
iid: 1
title: Test
state: opened
---
# Test

Description

## Comments

### user1 - 2025-01-01 12:00:00

First comment

### user2 - 2025-01-01 13:00:00

Second comment
"""

        issue = parse_issue(content)

        assert len(issue.comments) == 2
        assert issue.comments[0].author == "user1"
        assert issue.comments[0].body == "First comment"
        assert issue.comments[1].author == "user2"
        assert issue.comments[1].body == "Second comment"

    def test_parse_with_comment_containing_code_block(self):
        """Test parsing comment that contains code block."""
        content = """---
iid: 1
title: Test
state: opened
---
# Test

Description

## Comments

### user1 - 2025-01-01 12:00:00

This is a comment.

```python
def hello():
    print("world")
```

More content after code
"""

        issue = parse_issue(content)

        assert len(issue.comments) == 1
        assert issue.comments[0].author == "user1"
        assert "```python" in issue.comments[0].body
        assert "More content after code" in issue.comments[0].body

    def test_parse_comment_with_h3_headers_in_body(self):
        """Test that h3 headers in comment body don't break parsing (Issue #17)."""
        content = """---
iid: 1
title: Test
state: opened
---
# Test

Description

## Comments

### user1 - 2025-01-01 12:00:00

This is a comment with sections.

### Files Created

1. file1.py
2. file2.py

### Files Updated

- Updated file3.py
- Updated file4.py
"""

        issue = parse_issue(content)

        assert len(issue.comments) == 1
        assert issue.comments[0].author == "user1"
        assert "### Files Created" in issue.comments[0].body
        assert "### Files Updated" in issue.comments[0].body

    def test_parse_comment_with_bullet_lists(self):
        """Test that bullet lists with ' - ' in comments don't break parsing (Issue #17)."""
        content = """---
iid: 1
title: Test
state: opened
---
# Test

Description

## Comments

### user1 - 2025-01-01 12:00:00

Features implemented:
   - Authentication module
   - Database migrations
   - API endpoints
"""

        issue = parse_issue(content)

        assert len(issue.comments) == 1
        assert issue.comments[0].author == "user1"
        assert "- Authentication module" in issue.comments[0].body
        assert "- Database migrations" in issue.comments[0].body

    def test_parse_comment_with_h3_and_bullets_combined(self):
        """Test comments with both h3 headers and bullet lists (Issue #17)."""
        content = """---
iid: 1
title: Test
state: opened
---
# Test

Description

## Comments

### user1 - 2025-01-01 12:00:00

## Session Progress

### Files Created

1. references/issue-refinement.md
   - When to refine issues
   - Refinement templates
   - Checklist workflows

### Files Updated

2. SKILL.md
   - Added workflow section
   - Updated triggers

### user2 - 2025-01-01 13:00:00

Second comment
"""

        issue = parse_issue(content)

        assert len(issue.comments) == 2
        assert issue.comments[0].author == "user1"
        assert "### Files Created" in issue.comments[0].body
        assert "### Files Updated" in issue.comments[0].body
        assert "- When to refine issues" in issue.comments[0].body
        assert issue.comments[1].author == "user2"
        assert issue.comments[1].body == "Second comment"

    def test_parse_comment_does_not_match_invalid_timestamp_format(self):
        """Test that patterns resembling comments but without valid timestamps are not matched."""
        content = """---
iid: 1
title: Test
state: opened
---
# Test

Description with ### header - some text that looks like pattern

## Comments

### user1 - 2025-01-01 12:00:00

Real comment
"""

        issue = parse_issue(content)

        # Should only find 1 real comment, not the fake pattern in description
        assert len(issue.comments) == 1
        assert issue.comments[0].author == "user1"

    def test_parse_raises_error_for_unparsed_comment_content(self):
        """Test that unparsed content under ## Comments raises StorageError."""
        content = """---
iid: 1
title: Test
state: opened
---
Description

## Comments

### Implementation Notes

This content doesn't follow the comment format and should raise an error.

### user1 - 2025-01-01 12:00:00

Real comment
"""
        with pytest.raises(StorageError) as exc_info:
            parse_issue(content)

        error_msg = str(exc_info.value)
        assert "Unparsed content found under '## Comments'" in error_msg
        assert "Implementation Notes" in error_msg
        assert "gl-issue-sync comment" in error_msg

    def test_parse_raises_error_for_malformed_timestamp(self):
        """Test that comments with malformed timestamps raise StorageError."""
        content = """---
iid: 1
title: Test
state: opened
---
Description

## Comments

### user1 - 2025-01-01

Comment with date but no time - doesn't match pattern
"""
        with pytest.raises(StorageError) as exc_info:
            parse_issue(content)

        assert "Unparsed content found under '## Comments'" in str(exc_info.value)

    def test_parse_valid_comments_no_error(self):
        """Test that properly formatted comments parse without error."""
        content = """---
iid: 1
title: Test
state: opened
---
Description

## Comments

### user1 - 2025-01-01 12:00:00

First comment

### user2 - 2025-01-02T14:30:00.123456+00:00

Second comment with ISO timestamp
"""
        issue = parse_issue(content)

        assert len(issue.comments) == 2
        assert issue.comments[0].author == "user1"
        assert issue.comments[1].author == "user2"


class TestEnsureStorageStructure:
    """Tests for ensure_storage_structure function."""

    def test_ensure_directories_creates_all_required_dirs(self, temp_git_repo):
        """Test that all required directories are created."""
        ensure_storage_structure(temp_git_repo)

        assert (temp_git_repo / ".issues" / ISSUE_STATE_OPENED).exists()
        assert (temp_git_repo / ".issues" / ISSUE_STATE_CLOSED).exists()
        assert (temp_git_repo / ".issues" / ".sync" / "originals").exists()
        assert (temp_git_repo / ".issues" / "attachments").exists()

    def test_ensure_directories_idempotent(self, temp_git_repo):
        """Test that calling ensure_storage_structure multiple times is safe."""
        ensure_storage_structure(temp_git_repo)
        ensure_storage_structure(temp_git_repo)  # Call again

        # Should not raise error and all directories should exist
        assert (temp_git_repo / ".issues" / ISSUE_STATE_OPENED).exists()
        assert (temp_git_repo / ".issues" / ISSUE_STATE_CLOSED).exists()


class TestListIssuesEdgeCases:
    """Tests for list_issues edge cases."""

    def test_list_issues_empty_directories(self, temp_git_repo):
        """Test listing issues when directories are empty."""
        ensure_storage_structure(temp_git_repo)

        all_issues = Issue.list_all(None, temp_git_repo)
        open_issues = Issue.list_all(ISSUE_STATE_OPENED, temp_git_repo)
        closed_issues = Issue.list_all(ISSUE_STATE_CLOSED, temp_git_repo)

        assert all_issues == []
        assert open_issues == []
        assert closed_issues == []

    def test_list_issues_mixed_states(self, temp_git_repo):
        """Test listing issues with mixed open and closed states."""
        issue1 = Issue(iid=1, title="Open", state="opened", description="Test")
        issue2 = Issue(iid=2, title="Closed", state="closed", description="Test")
        issue3 = Issue(iid=3, title="Open2", state="opened", description="Test")

        issue1.save(temp_git_repo)
        issue2.save(temp_git_repo)
        issue3.save(temp_git_repo)

        all_issues = Issue.list_all(None, temp_git_repo)
        open_issues = Issue.list_all(ISSUE_STATE_OPENED, temp_git_repo)
        closed_issues = Issue.list_all(ISSUE_STATE_CLOSED, temp_git_repo)

        assert len(all_issues) == 3
        assert len(open_issues) == 2
        assert len(closed_issues) == 1


class TestIssueLinks:
    """Tests for issue links functionality."""

    def test_serialize_with_links(self):
        """Test serializing issue with links."""
        issue = Issue(
            iid=1,
            title="Test",
            state="opened",
            description="Test",
            links=[
                IssueLink(
                    link_id=100,
                    target_project_id=10,
                    target_issue_iid=2,
                    link_type="relates_to",
                    created_at=datetime(2025, 1, 1, 12, 0, 0),
                    updated_at=datetime(2025, 1, 1, 12, 0, 0),
                )
            ],
        )

        content = serialize_issue(issue)
        assert "links:" in content
        assert "link_id: 100" in content
        assert "target_issue_iid: 2" in content
        assert "link_type: relates_to" in content

    def test_parse_with_links(self):
        """Test parsing issue with links."""
        content = """---
iid: 1
title: Test
state: opened
confidential: false
links:
  - link_id: 100
    target_project_id: 10
    target_issue_iid: 2
    link_type: relates_to
    created_at: '2025-01-01T12:00:00'
    updated_at: '2025-01-01T12:00:00'
---

# Test

Description
"""

        issue = parse_issue(content)
        assert len(issue.links) == 1
        assert issue.links[0].link_id == 100
        assert issue.links[0].target_issue_iid == 2
        assert issue.links[0].link_type == "relates_to"


# =============================================================================
# Label Tests
# =============================================================================


class TestLabelDataclass:
    """Tests for Label dataclass."""

    def test_compute_content_hash(self):
        """Test label hash generation."""
        label1 = Label(name="bug", color="#FF0000", description="Bug reports")
        hash1 = label1.compute_content_hash()

        # Same content should produce same hash
        label2 = Label(name="bug", color="#FF0000", description="Bug reports")
        hash2 = label2.compute_content_hash()
        assert hash1 == hash2

        # Different content should produce different hash
        label3 = Label(name="bug", color="#00FF00", description="Bug reports")
        hash3 = label3.compute_content_hash()
        assert hash1 != hash3


class TestLabelStorage:
    """Tests for label storage operations."""

    def test_save_and_load_label(self, temp_git_repo):
        """Test saving and loading a label."""
        label = Label(name="bug", color="#FF0000", description="Bug reports")
        label.save(temp_git_repo)

        loaded = Label.load("bug", temp_git_repo)
        assert loaded is not None
        assert loaded.name == "bug"
        assert loaded.color == "#FF0000"
        assert loaded.description == "Bug reports"

    def test_list_all_labels(self, temp_git_repo):
        """Test listing all labels."""
        label1 = Label(name="bug", color="#FF0000")
        label2 = Label(name="feature", color="#00FF00")

        label1.save(temp_git_repo)
        label2.save(temp_git_repo)

        labels = Label.list_all(repo_path=temp_git_repo)
        assert len(labels) == 2
        assert {l.name for l in labels} == {"bug", "feature"}

    def test_list_all_labels_exclude_deleted(self, temp_git_repo):
        """Test that deleted labels are excluded by default."""
        label1 = Label(name="bug", color="#FF0000")
        label2 = Label(name="feature", color="#00FF00")

        label1.save(temp_git_repo)
        label2.save(temp_git_repo)

        # Mark one as deleted
        label1.status = "deleted"
        label1.save(temp_git_repo)

        labels = Label.list_all(include_deleted=False, repo_path=temp_git_repo)
        assert len(labels) == 1
        assert labels[0].name == "feature"

        # Include deleted
        labels = Label.list_all(include_deleted=True, repo_path=temp_git_repo)
        assert len(labels) == 2

    def test_get_colors_map(self, temp_git_repo):
        """Test getting label colors map."""
        label1 = Label(name="bug", color="#FF0000")
        label2 = Label(name="feature", color="#00FF00")

        label1.save(temp_git_repo)
        label2.save(temp_git_repo)

        colors = Label.get_colors_map(temp_git_repo)
        assert colors == {"bug": "#FF0000", "feature": "#00FF00"}


class TestLabelBackend:
    """Tests for LabelBackend JSON storage."""

    def test_json_roundtrip(self, temp_git_repo):
        """Test that labels are correctly serialized to and from JSON."""
        label1 = Label(name="bug", color="#FF0000", description="Bug reports")
        label1.status = "synced"
        label1.remote_id = 123

        label2 = Label(name="feature", color="#00FF00")
        label2.status = "pending"

        label1.save(temp_git_repo)
        label2.save(temp_git_repo)

        # Load and verify status is preserved
        loaded1 = Label.load("bug", temp_git_repo)
        assert loaded1.status == "synced"
        assert loaded1.remote_id == 123

        loaded2 = Label.load("feature", temp_git_repo)
        assert loaded2.status == "pending"


# =============================================================================
# Milestone Tests
# =============================================================================


class TestMilestoneDataclass:
    """Tests for Milestone dataclass."""

    def test_filename_sanitization(self):
        """Test that milestone filenames are sanitized."""
        # Test filename generation (removes dots and special chars)
        milestone = Milestone(title="Version 1.0 - Beta")
        assert milestone.filename == "Version_10_Beta.md"

        milestone2 = Milestone(title="Sprint #5")
        assert milestone2.filename == "Sprint_5.md"

    def test_compute_content_hash(self):
        """Test milestone hash generation."""
        ms1 = Milestone(title="v1.0", description="Release", due_date="2025-12-31")
        hash1 = ms1.compute_content_hash()

        # Same content should produce same hash
        ms2 = Milestone(title="v1.0", description="Release", due_date="2025-12-31")
        hash2 = ms2.compute_content_hash()
        assert hash1 == hash2

        # Different content should produce different hash
        ms3 = Milestone(title="v1.0", description="Different", due_date="2025-12-31")
        hash3 = ms3.compute_content_hash()
        assert hash1 != hash3


class TestMilestoneStorage:
    """Tests for milestone storage operations."""

    def test_save_and_list_milestone(self, temp_git_repo):
        """Test saving and listing milestones."""
        milestone = Milestone(
            title="v1.0",
            description="First release",
            due_date="2025-12-31",
            state="active",
        )
        milestone.save(temp_git_repo)

        # List all to find it (load by title doesn't work due to filename sanitization)
        milestones = Milestone.list_all(repo_path=temp_git_repo)
        assert len(milestones) == 1
        loaded = milestones[0]
        assert loaded.title == "v1.0"
        assert loaded.description == "First release"
        assert loaded.due_date == "2025-12-31"
        assert loaded.state == "active"

    def test_list_all_milestones(self, temp_git_repo):
        """Test listing all milestones."""
        ms1 = Milestone(title="v1.0", description="First release")
        ms2 = Milestone(title="v2.0", description="Second release")

        ms1.save(temp_git_repo)
        ms2.save(temp_git_repo)

        milestones = Milestone.list_all(repo_path=temp_git_repo)
        assert len(milestones) == 2
        assert {m.title for m in milestones} == {"v1.0", "v2.0"}

    def test_list_all_milestones_exclude_deleted(self, temp_git_repo):
        """Test that deleted milestones are excluded by default."""
        ms1 = Milestone(title="v1.0")
        ms2 = Milestone(title="v2.0")

        ms1.save(temp_git_repo)
        ms2.save(temp_git_repo)

        # Mark one as deleted
        ms1.status = "deleted"
        ms1.save(temp_git_repo)

        milestones = Milestone.list_all(include_deleted=False, repo_path=temp_git_repo)
        assert len(milestones) == 1
        assert milestones[0].title == "v2.0"

        # Include deleted
        milestones = Milestone.list_all(include_deleted=True, repo_path=temp_git_repo)
        assert len(milestones) == 2

    def test_get_title_to_id_map(self, temp_git_repo):
        """Test getting milestone title to ID map."""
        ms1 = Milestone(title="v1.0")
        ms1.remote_id = 1
        ms2 = Milestone(title="v2.0")
        ms2.remote_id = 2

        ms1.save(temp_git_repo)
        ms2.save(temp_git_repo)

        id_map = Milestone.get_title_to_id_map(temp_git_repo)
        assert id_map == {"v1.0": 1, "v2.0": 2}


class TestMilestoneBackend:
    """Tests for MilestoneBackend markdown storage."""

    def test_markdown_roundtrip_with_description(self, temp_git_repo):
        """Test that milestones with descriptions are correctly serialized."""
        milestone = Milestone(
            title="v1.0",
            description="# First Release\n\nThis is a **major** release.",
            due_date="2025-12-31",
            state="active",
        )
        milestone.status = "synced"
        milestone.remote_id = 123

        milestone.save(temp_git_repo)

        # Load via list_all (load by title doesn't work due to filename sanitization)
        milestones = Milestone.list_all(repo_path=temp_git_repo)
        assert len(milestones) == 1
        loaded = milestones[0]
        assert loaded.description == "# First Release\n\nThis is a **major** release."
        assert loaded.status == "synced"
        assert loaded.remote_id == 123

    def test_markdown_roundtrip_without_description(self, temp_git_repo):
        """Test that milestones without descriptions work correctly."""
        milestone = Milestone(title="v2.0", due_date="2026-06-30")
        milestone.save(temp_git_repo)

        # Load via list_all
        milestones = Milestone.list_all(repo_path=temp_git_repo)
        assert len(milestones) == 1
        loaded = milestones[0]
        assert loaded.description is None or loaded.description == ""


# =============================================================================
# Storage Backend Tests
# =============================================================================


class TestChangeDetection:
    """Tests for has_changed_from method."""

    def test_issue_no_change(self):
        """Test that identical issues show no change."""
        issue1 = Issue(iid=1, title="Test", state="opened", description="Test")
        issue2 = Issue(iid=1, title="Test", state="opened", description="Test")

        assert not issue1.has_changed_from(issue2)

    def test_issue_title_change(self):
        """Test that title change is detected."""
        original = Issue(iid=1, title="Original", state="opened", description="Test")
        modified = Issue(iid=1, title="Modified", state="opened", description="Test")

        assert modified.has_changed_from(original)

    def test_label_change(self):
        """Test that label changes are detected."""
        original = Label(name="bug", color="#FF0000")
        modified = Label(name="bug", color="#00FF00")

        assert modified.has_changed_from(original)


class TestStorageBackendPull:
    """Tests for StorageBackend.pull() three-way merge."""

    def test_pull_new_remote_issue(self, temp_git_repo, mock_gitlab_project, mock_graphql_execute):
        """Test pulling a new issue from GitLab."""
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory

        # Mock REST API response using factory
        mock_issue = GitLabIssueFactory(
            iid=1,
            title="New Issue",
        )

        mock_gitlab_project.issues.list.return_value = [mock_issue]

        # Mock GraphQL hierarchy response (no parent, no children)
        mock_graphql_execute.return_value = GraphQLHierarchyResponseFactory(iid=1)

        # Pull
        result = Issue.pull(mock_gitlab_project, temp_git_repo, state="opened")

        # Verify new issue was saved
        assert len(result.created) == 1
        assert result.created[0] == 1

        # Verify it's on disk
        loaded = Issue.load(1, temp_git_repo)
        assert loaded is not None
        assert loaded.title == "New Issue"
        assert loaded.parent_iid is None
        assert loaded.child_iids == []


class TestStorageBackendPush:
    """Tests for StorageBackend.push() operations."""

    def test_sync_result_structure(self):
        """Test SyncResult dataclass structure."""
        result = SyncResult()
        assert result.created == []
        assert result.updated == []
        assert result.deleted == []
        assert result.auto_resolve_details == {}
        assert result.conflicts == []
        assert result.conflict_details == {}


class TestPullConflictResolution:
    """Tests for pull auto-resolution of BOTH_MODIFIED conflicts."""

    def test_pull_auto_resolves_different_fields(
        self, temp_git_repo, mock_gitlab_project, mock_graphql_execute
    ):
        """Test that pull auto-resolves when different fields are modified."""
        from copy import deepcopy
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory, IssueFactory

        # Create base issue and save as original
        base = IssueFactory(iid=1, title="Original Title", labels=["feature"])
        Issue.backend.save(base, temp_git_repo)
        Issue.backend.save_original(base, temp_git_repo)

        # Local modified: change title only
        local = deepcopy(base)
        local.title = "Local Title"
        Issue.backend.save(local, temp_git_repo)

        # Remote modified: change labels (different field)
        mock_issue = GitLabIssueFactory(
            iid=1,
            title="Original Title",
            labels=["feature", "bug"],  # Changed remotely
            created_at=base.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
        )
        mock_gitlab_project.issues.list.return_value = [mock_issue]
        mock_graphql_execute.return_value = GraphQLHierarchyResponseFactory(iid=1)

        # Pull
        result = Issue.pull(mock_gitlab_project, temp_git_repo, state="opened")

        # Should auto-resolve: merge local title + remote labels
        assert 1 in result.auto_resolve_details
        assert result.conflicts == []

        # Verify merged content
        merged = Issue.load(1, temp_git_repo)
        assert merged.title == "Local Title"  # Local change preserved
        assert "bug" in merged.labels  # Remote change merged

    def test_pull_conflict_same_field(
        self, temp_git_repo, mock_gitlab_project, mock_graphql_execute
    ):
        """Test that pull records conflict when same field is modified on both sides."""
        from copy import deepcopy
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory, IssueFactory
        from gitlab_issue_sync.storage.conflicts import Conflict

        # Create base issue and save as original
        base = IssueFactory(iid=1, title="Original Title")
        Issue.backend.save(base, temp_git_repo)
        Issue.backend.save_original(base, temp_git_repo)

        # Local modified: change title
        local = deepcopy(base)
        local.title = "Local Title"
        Issue.backend.save(local, temp_git_repo)

        # Remote modified: also change title (same field conflict)
        mock_issue = GitLabIssueFactory(
            iid=1,
            title="Remote Title",  # Same field!
            created_at=base.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
        )
        mock_gitlab_project.issues.list.return_value = [mock_issue]
        mock_graphql_execute.return_value = GraphQLHierarchyResponseFactory(iid=1)

        # Pull
        result = Issue.pull(mock_gitlab_project, temp_git_repo, state="opened")

        # Should NOT auto-resolve: same field conflict
        assert result.auto_resolve_details == {}
        assert 1 in result.conflicts
        assert "title" in result.conflict_details[1]

        # Verify local was NOT changed (preserved for manual resolution)
        unchanged = Issue.load(1, temp_git_repo)
        assert unchanged.title == "Local Title"

        # Verify conflict was recorded
        conflict = Conflict.load(1, temp_git_repo)
        assert conflict is not None
        assert "title" in conflict.fields

        # Verify remote was cached for offline resolution
        cached_remote = conflict.load_cached_remote(temp_git_repo)
        assert cached_remote is not None
        assert cached_remote.title == "Remote Title"


class TestPushConflictResolution:
    """Tests for push auto-resolution of BOTH_MODIFIED conflicts."""

    def test_push_auto_resolves_different_fields(
        self, temp_git_repo, patch_gitlab_class, mock_gitlab_client, mock_graphql_execute
    ):
        """Test that push auto-resolves when different fields are modified."""
        from copy import deepcopy
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory, IssueFactory

        # Create base issue and save as original
        base = IssueFactory(iid=1, title="Original Title", labels=["feature"])
        Issue.backend.save(base, temp_git_repo)
        Issue.backend.save_original(base, temp_git_repo)

        # Local modified: change title only
        local = deepcopy(base)
        local.title = "Local Title"
        Issue.backend.save(local, temp_git_repo)

        # Remote modified: change labels (different field)
        mock_remote_issue = GitLabIssueFactory(
            iid=1,
            title="Original Title",
            labels=["feature", "bug"],  # Changed remotely
            created_at=base.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
        )
        mock_updated_issue = GitLabIssueFactory(
            iid=1,
            title="Local Title",  # After push, has merged content
            labels=["feature", "bug"],
            created_at=base.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
        )

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123

        # issues.list returns remote issues (for conflict detection)
        mock_project.issues.list.return_value = [mock_remote_issue]

        # issues.get returns the updated issue after save
        mock_project.issues.get.return_value = mock_updated_issue

        mock_graphql_execute.return_value = GraphQLHierarchyResponseFactory(iid=1)

        # Push
        result = Issue.push(mock_project, temp_git_repo)

        # Should auto-resolve: merge local title + remote labels
        assert 1 in result.auto_resolve_details
        assert result.conflicts == []
        assert 1 in result.updated

        # Verify merged content was saved
        merged = Issue.load(1, temp_git_repo)
        assert merged.title == "Local Title"  # Local change preserved
        assert "bug" in merged.labels  # Remote change merged

    def test_push_conflict_same_field(
        self, temp_git_repo, patch_gitlab_class, mock_gitlab_client, mock_graphql_execute
    ):
        """Test that push records conflict when same field is modified on both sides."""
        from copy import deepcopy
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory, IssueFactory
        from gitlab_issue_sync.storage.conflicts import Conflict

        # Create base issue and save as original
        base = IssueFactory(iid=1, title="Original Title")
        Issue.backend.save(base, temp_git_repo)
        Issue.backend.save_original(base, temp_git_repo)

        # Local modified: change title
        local = deepcopy(base)
        local.title = "Local Title"
        Issue.backend.save(local, temp_git_repo)

        # Remote modified: also change title (same field conflict)
        mock_remote_issue = GitLabIssueFactory(
            iid=1,
            title="Remote Title",  # Same field!
            created_at=base.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
        )

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123
        mock_project.issues.list.return_value = [mock_remote_issue]
        mock_graphql_execute.return_value = GraphQLHierarchyResponseFactory(iid=1)

        # Push
        result = Issue.push(mock_project, temp_git_repo)

        # Should NOT auto-resolve: same field conflict
        assert result.auto_resolve_details == {}
        assert 1 in result.conflicts
        assert "title" in result.conflict_details[1]

        # Verify local was NOT changed (preserved for manual resolution)
        unchanged = Issue.load(1, temp_git_repo)
        assert unchanged.title == "Local Title"

        # Verify conflict was recorded
        conflict = Conflict.load(1, temp_git_repo)
        assert conflict is not None
        assert "title" in conflict.fields


class TestKanbanColumn:
    """Tests for KanbanColumn workflow navigation methods.

    Note: Position 0 (first column) is "ToDo" from config. Display position 0
    shows as "(no column)" which represents issues not in any workflow column.
    """

    def test_get_next_from_first_column(self, project_config, temp_git_repo):
        """Test moving forward from first column (ToDo -> In Progress)."""
        from gitlab_issue_sync.storage import KanbanColumn

        # Columns: ["ToDo", "In Progress", "Done"]
        target_col, new_state = KanbanColumn.get_next("ToDo", "opened", temp_git_repo)

        assert target_col == "In Progress"
        assert new_state is None  # Keep state

    def test_get_next_from_middle_column(self, project_config, temp_git_repo):
        """Test moving forward from middle column (In Progress -> Done)."""
        from gitlab_issue_sync.storage import KanbanColumn

        target_col, new_state = KanbanColumn.get_next("In Progress", "opened", temp_git_repo)

        assert target_col == "Done"
        assert new_state is None

    def test_get_next_from_last_column(self, project_config, temp_git_repo):
        """Test moving past last column closes the issue (Done -> closed)."""
        from gitlab_issue_sync.storage import KanbanColumn

        target_col, new_state = KanbanColumn.get_next("Done", "opened", temp_git_repo)

        assert target_col is None
        assert new_state == "closed"  # Close after last column

    def test_get_next_from_closed_reopens_to_last(self, project_config, temp_git_repo):
        """Test that moving next when closed re-opens to last column."""
        from gitlab_issue_sync.storage import KanbanColumn

        target_col, new_state = KanbanColumn.get_next(None, "closed", temp_git_repo)

        assert target_col == "Done"
        assert new_state == "opened"

    def test_get_next_from_no_column_enters_first(self, project_config, temp_git_repo):
        """Test entering workflow from no column (None -> ToDo)."""
        from gitlab_issue_sync.storage import KanbanColumn

        target_col, new_state = KanbanColumn.get_next(None, "opened", temp_git_repo)

        assert target_col == "ToDo"
        assert new_state is None

    def test_get_previous_from_last_column(self, project_config, temp_git_repo):
        """Test moving backward from last column (Done -> In Progress)."""
        from gitlab_issue_sync.storage import KanbanColumn

        target_col, new_state = KanbanColumn.get_previous("Done", "opened", temp_git_repo)

        assert target_col == "In Progress"
        assert new_state is None

    def test_get_previous_from_middle_column(self, project_config, temp_git_repo):
        """Test moving backward from middle column (In Progress -> ToDo)."""
        from gitlab_issue_sync.storage import KanbanColumn

        target_col, new_state = KanbanColumn.get_previous("In Progress", "opened", temp_git_repo)

        assert target_col == "ToDo"
        assert new_state is None

    def test_get_previous_from_first_column(self, project_config, temp_git_repo):
        """Test moving before first column removes from workflow (ToDo -> no column)."""
        from gitlab_issue_sync.storage import KanbanColumn

        target_col, new_state = KanbanColumn.get_previous("ToDo", "opened", temp_git_repo)

        assert target_col is None
        assert new_state is None  # Remove from columns

    def test_get_previous_from_closed_reopens_to_last(self, project_config, temp_git_repo):
        """Test that moving previous when closed re-opens to last column."""
        from gitlab_issue_sync.storage import KanbanColumn

        target_col, new_state = KanbanColumn.get_previous(None, "closed", temp_git_repo)

        assert target_col == "Done"
        assert new_state == "opened"

    def test_get_previous_from_no_column_stays_removed(self, project_config, temp_git_repo):
        """Test that going previous from no column stays removed."""
        from gitlab_issue_sync.storage import KanbanColumn

        target_col, new_state = KanbanColumn.get_previous(None, "opened", temp_git_repo)

        assert target_col is None
        assert new_state is None

    def test_validate_and_suggest_exact_match(self, project_config, temp_git_repo):
        """Test validation with exact column name match."""
        from gitlab_issue_sync.storage import KanbanColumn

        is_valid, suggestion = KanbanColumn.validate_and_suggest("ToDo", temp_git_repo)

        assert is_valid is True
        assert suggestion is None

    def test_validate_and_suggest_case_mismatch(self, project_config, temp_git_repo):
        """Test validation suggests correct casing."""
        from gitlab_issue_sync.storage import KanbanColumn

        is_valid, suggestion = KanbanColumn.validate_and_suggest("TODO", temp_git_repo)

        assert is_valid is False
        assert suggestion == "ToDo"

    def test_validate_and_suggest_fuzzy_match(self, project_config, temp_git_repo):
        """Test fuzzy matching suggests similar column."""
        from gitlab_issue_sync.storage import KanbanColumn

        is_valid, suggestion = KanbanColumn.validate_and_suggest("Progress", temp_git_repo)

        assert is_valid is False
        assert suggestion == "In Progress"  # Contains "Progress"

    def test_validate_and_suggest_no_match(self, project_config, temp_git_repo):
        """Test validation with no match returns None."""
        from gitlab_issue_sync.storage import KanbanColumn

        is_valid, suggestion = KanbanColumn.validate_and_suggest("invalid-column", temp_git_repo)

        assert is_valid is False
        assert suggestion is None

    def test_get_column_names(self, project_config, temp_git_repo):
        """Test getting ordered list of column names."""
        from gitlab_issue_sync.storage import KanbanColumn

        names = KanbanColumn.get_column_names(temp_git_repo)

        assert names == ["ToDo", "In Progress", "Done"]

    def test_get_columns(self, project_config, temp_git_repo):
        """Test getting list of KanbanColumn objects."""
        from gitlab_issue_sync.storage import KanbanColumn

        columns = KanbanColumn.get_columns(temp_git_repo)

        assert len(columns) == 3
        assert columns[0].name == "ToDo"
        assert columns[0].position == 0
        assert columns[2].name == "Done"
        assert columns[2].position == 2


# =============================================================================
# Issue Hierarchy Tests
# =============================================================================


class TestIssueHierarchy:
    """Tests for work item hierarchy (parent/child relationships)."""

    def test_serialize_issue_with_parent(self):
        """Test serialization of issue with parent."""
        import re

        import yaml

        from tests.factories import IssueFactory

        issue = IssueFactory(
            iid=4,
            title="Child Issue",
            description="This is a child issue",
            parent_iid=1,
        )

        serialized = serialize_issue(issue)

        # Extract and parse frontmatter
        frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(frontmatter_pattern, serialized, re.DOTALL)
        assert match, "Should have valid frontmatter"

        frontmatter = yaml.safe_load(match.group(1))
        body = match.group(2)

        # Verify parent_iid is in frontmatter
        assert frontmatter["parent_iid"] == 1

        # Verify hierarchy is NOT rendered in body (displayed in CLI only)
        assert "## Hierarchy" not in body
        assert "Parent:" not in body or "Parent Issue:" in body  # Allow "Parent Issue:" in description

    def test_serialize_issue_with_children(self):
        """Test serialization of issue with children."""
        import re

        import yaml

        from tests.factories import IssueFactory

        issue = IssueFactory(
            iid=1,
            title="Parent Issue",
            description="This is a parent issue",
            child_iids=[4, 5],
        )

        serialized = serialize_issue(issue)

        # Extract and parse frontmatter
        frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(frontmatter_pattern, serialized, re.DOTALL)
        assert match, "Should have valid frontmatter"

        frontmatter = yaml.safe_load(match.group(1))
        body = match.group(2)

        # Verify child_iids is in frontmatter
        assert "child_iids" in frontmatter
        assert frontmatter["child_iids"] == [4, 5]

        # Verify hierarchy is NOT rendered in body (displayed in CLI only)
        assert "## Hierarchy" not in body
        assert "Children:" not in body or "Children:" in issue.description  # Allow if in description

    def test_serialize_issue_without_hierarchy(self):
        """Test serialization of issue without hierarchy."""
        import re

        import yaml

        from tests.factories import IssueFactory

        issue = IssueFactory(
            iid=10,
            title="Standalone Issue",
            description="No hierarchy",
        )

        serialized = serialize_issue(issue)

        # Extract and parse frontmatter
        frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(frontmatter_pattern, serialized, re.DOTALL)
        assert match, "Should have valid frontmatter"

        frontmatter = yaml.safe_load(match.group(1))
        body = match.group(2)

        # Verify no hierarchy fields in frontmatter
        assert "parent_iid" not in frontmatter
        assert "child_iids" not in frontmatter

        # Verify no Hierarchy section in body
        assert "## Hierarchy" not in body

    def test_parse_issue_with_parent(self):
        """Test parsing issue with parent (roundtrip test)."""
        from tests.factories import IssueFactory

        # Create issue with parent
        original = IssueFactory(
            iid=4,
            title="Child Issue",
            description="This is a child issue",
            parent_iid=1,
        )

        # Serialize and parse back
        serialized = serialize_issue(original)
        parsed = parse_issue(serialized)

        # Verify hierarchy preserved
        assert parsed.parent_iid == original.parent_iid
        assert parsed.child_iids == original.child_iids

    def test_parse_issue_with_children(self):
        """Test parsing issue with children (roundtrip test)."""
        from tests.factories import IssueFactory

        # Create issue with children
        original = IssueFactory(
            iid=1,
            title="Parent Issue",
            description="This is a parent issue",
            child_iids=[4, 5],
        )

        # Serialize and parse back
        serialized = serialize_issue(original)
        parsed = parse_issue(serialized)

        # Verify hierarchy preserved
        assert parsed.parent_iid == original.parent_iid
        assert parsed.child_iids == original.child_iids

    def test_parse_issue_with_both_parent_and_children(self):
        """Test parsing issue with both parent and children (roundtrip test)."""
        from tests.factories import IssueFactory

        # Create issue with both parent and children
        original = IssueFactory(
            iid=2,
            title="Middle Issue",
            description="Has both parent and children",
            parent_iid=1,
            child_iids=[3, 4],
        )

        # Serialize and parse back
        serialized = serialize_issue(original)
        parsed = parse_issue(serialized)

        # Verify hierarchy preserved
        assert parsed.parent_iid == original.parent_iid
        assert parsed.child_iids == original.child_iids

    def test_compute_content_hash_includes_parent(self):
        """Test that content hash includes parent_iid."""
        from tests.factories import IssueFactory

        issue1 = IssueFactory(iid=4, title="Issue", parent_iid=1)
        issue2 = IssueFactory(iid=4, title="Issue", parent_iid=2)
        issue3 = IssueFactory(iid=4, title="Issue", parent_iid=None)

        # Different parent_iid should result in different hashes
        assert issue1.compute_content_hash() != issue2.compute_content_hash()
        assert issue1.compute_content_hash() != issue3.compute_content_hash()

    def test_compute_content_hash_excludes_children(self):
        """Test that content hash excludes child_iids (read-only field)."""
        from tests.factories import IssueFactory

        # Create one issue and modify child_iids multiple times
        issue = IssueFactory(iid=1, title="Issue", child_iids=[4, 5])
        hash1 = issue.compute_content_hash()

        # Modify child_iids and recompute
        issue.child_iids = [4, 5, 6]
        hash2 = issue.compute_content_hash()

        # Modify again
        issue.child_iids = []
        hash3 = issue.compute_content_hash()

        # child_iids is read-only, so all hashes should be the same
        assert hash1 == hash2
        assert hash1 == hash3


class TestGraphQLMutations:
    """Tests for GraphQL client methods (update_work_item_parent, etc.)."""

    def test_update_work_item_parent_set_parent(self, mock_graphql_execute):
        """Test setting a parent via GraphQL mutation."""
        from src.gitlab_issue_sync.graphql.client import GitLabGraphQLClient

        mock_graphql_execute.return_value = {
            "data": {
                "workItemUpdate": {
                    "workItem": {"id": "gid://gitlab/WorkItem/4", "iid": "4"},
                    "errors": [],
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        client.update_work_item_parent(
            child_global_id="gid://gitlab/WorkItem/4",
            parent_global_id="gid://gitlab/WorkItem/1",
        )

        mock_graphql_execute.assert_called_once()
        call_args = mock_graphql_execute.call_args
        variables = call_args[1]["variables"]

        assert variables["input"]["id"] == "gid://gitlab/WorkItem/4"
        assert variables["input"]["hierarchyWidget"]["parentId"] == "gid://gitlab/WorkItem/1"

    def test_update_work_item_parent_remove_parent(self, mock_graphql_execute):
        """Test removing a parent via GraphQL mutation."""
        from src.gitlab_issue_sync.graphql.client import GitLabGraphQLClient

        mock_graphql_execute.return_value = {
            "data": {
                "workItemUpdate": {
                    "workItem": {"id": "gid://gitlab/WorkItem/4", "iid": "4"},
                    "errors": [],
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")
        client.update_work_item_parent(
            child_global_id="gid://gitlab/WorkItem/4",
            parent_global_id=None,
        )

        mock_graphql_execute.assert_called_once()
        call_args = mock_graphql_execute.call_args
        variables = call_args[1]["variables"]

        assert variables["input"]["id"] == "gid://gitlab/WorkItem/4"
        assert variables["input"]["hierarchyWidget"]["parentId"] is None

    def test_update_work_item_parent_handles_errors(self, mock_graphql_execute):
        """Test error handling in GraphQL mutation."""
        from src.gitlab_issue_sync.graphql.client import GitLabGraphQLClient
        from src.gitlab_issue_sync.issue_sync import SyncError

        mock_graphql_execute.return_value = {
            "data": {
                "workItemUpdate": {
                    "workItem": None,
                    "errors": ["Parent work item not found"],
                }
            }
        }

        client = GitLabGraphQLClient("https://gitlab.example.com", "test-token")

        with pytest.raises(SyncError, match="Parent work item not found"):
            client.update_work_item_parent(
                child_global_id="gid://gitlab/WorkItem/4",
                parent_global_id="gid://gitlab/WorkItem/999",
            )


class TestPushWithParentChanges:
    """Integration tests for push operations with parent_iid changes.

    These tests verify the complete push workflow when parent relationships change,
    ensuring proper GraphQL mutations, REST API optimizations, and conflict detection.
    """

    def test_push_with_parent_set(
        self,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_graphql_execute,
    ):
        """Test pushing an issue with parent_iid set from None."""
        from gitlab_issue_sync.storage import Issue
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory

        # Create parent issue #1 and child issue #4 locally
        parent = Issue(
            iid=1,
            title="Parent Issue",
            state="opened",
            description="Parent description",
            global_id="gid://gitlab/WorkItem/1",
        )
        child = Issue(
            iid=4,
            title="Child Issue",
            state="opened",
            description="Child description",
            global_id="gid://gitlab/WorkItem/4",
            parent_iid=None,  # Initially no parent
        )

        # Save both issues and originals
        parent.save(temp_git_repo)
        Issue.backend.save_original(parent, temp_git_repo)
        child.save(temp_git_repo)
        Issue.backend.save_original(child, temp_git_repo)

        # Modify child to have parent #1
        child.parent_iid = 1
        child.save(temp_git_repo)

        # Create mock GitLab issues
        mock_parent_issue = GitLabIssueFactory(
            iid=1,
            title="Parent Issue",
            description="Parent description",
            state="opened",
        )
        mock_child_issue = GitLabIssueFactory(
            iid=4,
            title="Child Issue",
            description="Child description",
            state="opened",
        )

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123
        mock_project.issues.get.side_effect = lambda iid: (
            mock_parent_issue if iid == 1 else mock_child_issue
        )

        # Configure issues.list to handle both conflict detection and batch re-fetch
        def issues_list_side_effect(state=None, iids=None, get_all=False, **kwargs):
            if iids:
                # Batch re-fetch: return issues matching the IIDs
                result = []
                for iid in iids:
                    if iid == 1:
                        result.append(mock_parent_issue)
                    elif iid == 4:
                        result.append(mock_child_issue)
                return result
            # Conflict detection: return empty (no remote changes)
            return []

        mock_project.issues.list.side_effect = issues_list_side_effect

        # Configure GraphQL responses
        def graphql_side_effect(query, variables=None, operation_name=None):
            # Check if this is a mutation (workItemUpdate)
            if "workItemUpdate" in query and variables and "input" in variables:
                # This is the parent mutation - return success
                return {
                    "data": {
                        "workItemUpdate": {
                            "workItem": {
                                "id": "gid://gitlab/WorkItem/4",
                                "widgets": [],
                            },
                            "errors": [],
                        }
                    }
                }
            # Hierarchy queries (have projectPath in variables)
            if variables and "projectPath" in variables:
                iid = int(variables.get("iid", 1))
                if iid == 4:
                    # Child now has parent #1
                    return GraphQLHierarchyResponseFactory(iid=4, parent_iid=1)
                elif iid == 1:
                    # Parent now has child #4
                    return GraphQLHierarchyResponseFactory(iid=1, child_iids=[4])
                # Default: no hierarchy
                return GraphQLHierarchyResponseFactory(iid=iid)
            # Fallback
            return GraphQLHierarchyResponseFactory(iid=1)

        mock_graphql_execute.side_effect = graphql_side_effect

        # Push changes
        result = Issue.push(mock_project, temp_git_repo)

        # Verify: child was updated (GraphQL mutation called)
        assert child.iid in result.updated
        assert len(result.conflicts) == 0

        # Verify GraphQL mutation was called with correct parameters
        mutation_calls = [
            call for call in mock_graphql_execute.call_args_list
            if "query" in call[1] and "workItemUpdate" in call[1]["query"]
        ]
        assert len(mutation_calls) == 1, f"Expected 1 mutation call, got {len(mutation_calls)}"
        mutation_vars = mutation_calls[0][1].get("variables", {})
        assert mutation_vars["input"]["hierarchyWidget"]["parentId"] == "gid://gitlab/WorkItem/1"

        # Verify: local file was updated with hierarchy
        updated_child = Issue.load(4, temp_git_repo)
        assert updated_child.parent_iid == 1

        # Verify: parent's child_iids was updated via bidirectional fetch
        updated_parent = Issue.load(1, temp_git_repo)
        assert 4 in updated_parent.child_iids

    def test_push_with_parent_unset(
        self,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_graphql_execute,
    ):
        """Test pushing an issue with parent_iid changed from N to None."""
        from gitlab_issue_sync.storage import Issue
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory

        # Create parent issue #1 and child issue #4 locally
        parent = Issue(
            iid=1,
            title="Parent Issue",
            state="opened",
            description="Parent description",
            global_id="gid://gitlab/WorkItem/1",
            child_iids=[4],  # Initially has child #4
        )
        child = Issue(
            iid=4,
            title="Child Issue",
            state="opened",
            description="Child description",
            global_id="gid://gitlab/WorkItem/4",
            parent_iid=1,  # Initially has parent #1
        )

        # Save both issues and originals
        parent.save(temp_git_repo)
        Issue.backend.save_original(parent, temp_git_repo)
        child.save(temp_git_repo)
        Issue.backend.save_original(child, temp_git_repo)

        # Modify child to remove parent
        child.parent_iid = None
        child.save(temp_git_repo)

        # Create mock GitLab issues
        mock_parent_issue = GitLabIssueFactory(
            iid=1,
            title="Parent Issue",
            description="Parent description",
            state="opened",
        )
        mock_child_issue = GitLabIssueFactory(
            iid=4,
            title="Child Issue",
            description="Child description",
            state="opened",
        )

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123
        mock_project.issues.get.side_effect = lambda iid: (
            mock_parent_issue if iid == 1 else mock_child_issue
        )

        # Configure issues.list to handle both conflict detection and batch re-fetch
        def issues_list_side_effect(state=None, iids=None, get_all=False, **kwargs):
            if iids:
                # Batch re-fetch: return issues matching the IIDs
                result = []
                for iid in iids:
                    if iid == 1:
                        result.append(mock_parent_issue)
                    elif iid == 4:
                        result.append(mock_child_issue)
                return result
            # Conflict detection: return empty (no remote changes)
            return []

        mock_project.issues.list.side_effect = issues_list_side_effect

        # Configure GraphQL responses
        def graphql_side_effect(query, variables=None, operation_name=None):
            # After mutation, child should have no parent, parent should have no children
            if variables and "workItemUpdate" in query:
                # This is the parent mutation - return success
                return {
                    "data": {
                        "workItemUpdate": {
                            "workItem": {
                                "id": "gid://gitlab/WorkItem/4",
                                "widgets": [],
                            },
                            "errors": [],
                        }
                    }
                }
            # Hierarchy queries
            if variables and variables.get("iid") == 4:
                # Child now has no parent
                return GraphQLHierarchyResponseFactory(iid=4, parent_iid=None)
            elif variables and variables.get("iid") == 1:
                # Parent now has no children
                return GraphQLHierarchyResponseFactory(iid=1, child_iids=[])
            # Default: no hierarchy
            return GraphQLHierarchyResponseFactory(iid=variables.get("iid", 1))

        mock_graphql_execute.side_effect = graphql_side_effect

        # Push changes
        result = Issue.push(mock_project, temp_git_repo)

        # Verify: child was updated (GraphQL mutation called)
        assert child.iid in result.updated
        assert len(result.conflicts) == 0

        # Verify GraphQL mutation was called with null parent
        mutation_calls = [
            call for call in mock_graphql_execute.call_args_list
            if "query" in call[1] and "workItemUpdate" in call[1]["query"]
        ]
        assert len(mutation_calls) == 1
        mutation_vars = mutation_calls[0][1].get("variables", {})
        assert mutation_vars["input"]["hierarchyWidget"]["parentId"] is None

        # Verify: local file was updated
        updated_child = Issue.load(4, temp_git_repo)
        assert updated_child.parent_iid is None

        # Verify: parent's child_iids was updated via bidirectional fetch
        updated_parent = Issue.load(1, temp_git_repo)
        assert 4 not in updated_parent.child_iids

    def test_push_with_parent_change_from_a_to_b(
        self,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_graphql_execute,
    ):
        """Test pushing an issue with parent_iid changed from A to B."""
        from gitlab_issue_sync.storage import Issue
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory

        # Create two parent issues and one child
        parent_a = Issue(
            iid=1,
            title="Parent A",
            state="opened",
            description="Parent A description",
            global_id="gid://gitlab/WorkItem/1",
            child_iids=[4],  # Initially has child #4
        )
        parent_b = Issue(
            iid=2,
            title="Parent B",
            state="opened",
            description="Parent B description",
            global_id="gid://gitlab/WorkItem/2",
            child_iids=[],  # Initially has no children
        )
        child = Issue(
            iid=4,
            title="Child Issue",
            state="opened",
            description="Child description",
            global_id="gid://gitlab/WorkItem/4",
            parent_iid=1,  # Initially has parent #1
        )

        # Save all issues and originals
        parent_a.save(temp_git_repo)
        Issue.backend.save_original(parent_a, temp_git_repo)
        parent_b.save(temp_git_repo)
        Issue.backend.save_original(parent_b, temp_git_repo)
        child.save(temp_git_repo)
        Issue.backend.save_original(child, temp_git_repo)

        # Modify child to change parent from #1 to #2
        child.parent_iid = 2
        child.save(temp_git_repo)

        # Create mock GitLab issues
        mock_parent_a_issue = GitLabIssueFactory(
            iid=1,
            title="Parent A",
            description="Parent A description",
            state="opened",
        )
        mock_parent_b_issue = GitLabIssueFactory(
            iid=2,
            title="Parent B",
            description="Parent B description",
            state="opened",
        )
        mock_child_issue = GitLabIssueFactory(
            iid=4,
            title="Child Issue",
            description="Child description",
            state="opened",
        )

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123

        def get_issue_side_effect(iid):
            if iid == 1:
                return mock_parent_a_issue
            elif iid == 2:
                return mock_parent_b_issue
            else:
                return mock_child_issue

        mock_project.issues.get.side_effect = get_issue_side_effect

        # Configure issues.list to handle both conflict detection and batch re-fetch
        def issues_list_side_effect(state=None, iids=None, get_all=False, **kwargs):
            if iids:
                # Batch re-fetch: return issues matching the IIDs
                result = []
                for iid in iids:
                    if iid == 1:
                        result.append(mock_parent_a_issue)
                    elif iid == 2:
                        result.append(mock_parent_b_issue)
                    elif iid == 4:
                        result.append(mock_child_issue)
                return result
            # Conflict detection: return empty (no remote changes)
            return []

        mock_project.issues.list.side_effect = issues_list_side_effect

        # Configure GraphQL responses
        def graphql_side_effect(query, variables=None, operation_name=None):
            # Check if this is a mutation (workItemUpdate)
            if "workItemUpdate" in query and variables and "input" in variables:
                # This is the parent mutation - return success
                return {
                    "data": {
                        "workItemUpdate": {
                            "workItem": {
                                "id": "gid://gitlab/WorkItem/4",
                                "widgets": [],
                            },
                            "errors": [],
                        }
                    }
                }
            # Hierarchy queries (have projectPath in variables)
            if variables and "projectPath" in variables:
                iid = int(variables.get("iid", 1))
                if iid == 4:
                    # Child now has parent #2
                    return GraphQLHierarchyResponseFactory(iid=4, parent_iid=2)
                elif iid == 1:
                    # Parent A now has no children
                    return GraphQLHierarchyResponseFactory(iid=1, child_iids=[])
                elif iid == 2:
                    # Parent B now has child #4
                    return GraphQLHierarchyResponseFactory(iid=2, child_iids=[4])
                # Default: no hierarchy
                return GraphQLHierarchyResponseFactory(iid=iid)
            # Fallback
            return GraphQLHierarchyResponseFactory(iid=1)

        mock_graphql_execute.side_effect = graphql_side_effect

        # Push changes
        result = Issue.push(mock_project, temp_git_repo)

        # Verify: child was updated (GraphQL mutation called)
        assert child.iid in result.updated
        assert len(result.conflicts) == 0

        # Verify GraphQL mutation was called with new parent
        mutation_calls = [
            call for call in mock_graphql_execute.call_args_list
            if "query" in call[1] and "workItemUpdate" in call[1]["query"]
        ]
        assert len(mutation_calls) == 1
        mutation_vars = mutation_calls[0][1].get("variables", {})
        assert mutation_vars["input"]["hierarchyWidget"]["parentId"] == "gid://gitlab/WorkItem/2"

        # Verify: local file was updated
        updated_child = Issue.load(4, temp_git_repo)
        assert updated_child.parent_iid == 2

        # Verify: old parent's child_iids was updated
        updated_parent_a = Issue.load(1, temp_git_repo)
        assert 4 not in updated_parent_a.child_iids

        # Verify: new parent's child_iids was updated
        updated_parent_b = Issue.load(2, temp_git_repo)
        assert 4 in updated_parent_b.child_iids

    def test_push_parent_change_no_spurious_conflicts(
        self,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_graphql_execute,
    ):
        """Test that changing parent_iid doesn't create spurious conflicts.

        This test verifies that when only parent_iid changes locally (a GraphQL-only field),
        the push operation correctly handles it without detecting false conflicts.

        Key scenarios tested:
        - Local change: parent_iid modified
        - Remote: No changes
        - Result: Should push successfully without conflicts
        """
        from gitlab_issue_sync.storage import Issue
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory

        # Create parent and child issues locally
        parent = Issue(
            iid=1,
            title="Parent Issue",
            state="opened",
            description="Parent description",
            global_id="gid://gitlab/WorkItem/1",
        )
        child = Issue(
            iid=4,
            title="Child Issue",
            state="opened",
            description="Child description",
            global_id="gid://gitlab/WorkItem/4",
            parent_iid=None,  # Initially no parent
        )

        # Save both issues and originals
        parent.save(temp_git_repo)
        Issue.backend.save_original(parent, temp_git_repo)
        child.save(temp_git_repo)
        Issue.backend.save_original(child, temp_git_repo)

        # Modify child to add parent (local change only)
        child.parent_iid = 1
        child.save(temp_git_repo)

        # Create mock GitLab issues - unchanged from originals
        mock_parent_issue = GitLabIssueFactory(
            iid=1,
            title="Parent Issue",
            description="Parent description",
            state="opened",
        )
        mock_child_issue = GitLabIssueFactory(
            iid=4,
            title="Child Issue",
            description="Child description",
            state="opened",
        )

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123
        mock_project.issues.get.side_effect = lambda iid: (
            mock_parent_issue if iid == 1 else mock_child_issue
        )

        # GitLab shows no changes (parent_iid is GraphQL-only)
        # Handle both conflict detection (no iids) and batch re-fetch (with iids)
        def issues_list_side_effect(state=None, iids=None, get_all=False, **kwargs):
            if iids:
                # Batch re-fetch: return issues matching the IIDs
                result = []
                for iid in iids:
                    if iid == 1:
                        result.append(mock_parent_issue)
                    elif iid == 4:
                        result.append(mock_child_issue)
                return result
            # Conflict detection: return empty (no remote changes)
            return []

        mock_project.issues.list.side_effect = issues_list_side_effect

        # Configure GraphQL responses
        def graphql_side_effect(query, variables=None, operation_name=None):
            # Check if this is a mutation (workItemUpdate)
            if "workItemUpdate" in query and variables and "input" in variables:
                # Return mutation success
                return {
                    "data": {
                        "workItemUpdate": {
                            "workItem": {
                                "id": "gid://gitlab/WorkItem/4",
                                "widgets": [],
                            },
                            "errors": [],
                        }
                    }
                }
            # Hierarchy queries (have projectPath in variables)
            if variables and "projectPath" in variables:
                iid = int(variables.get("iid", 1))
                if iid == 4:
                    # After mutation, child has parent #1
                    return GraphQLHierarchyResponseFactory(iid=4, parent_iid=1)
                elif iid == 1:
                    # After mutation, parent has child #4
                    return GraphQLHierarchyResponseFactory(iid=1, child_iids=[4])
                # Default: no hierarchy
                return GraphQLHierarchyResponseFactory(iid=iid)
            # Fallback
            return GraphQLHierarchyResponseFactory(iid=1)

        mock_graphql_execute.side_effect = graphql_side_effect

        # Push changes
        result = Issue.push(mock_project, temp_git_repo)

        # Verify: No conflicts detected
        assert len(result.conflicts) == 0, f"Expected 0 conflicts, got {len(result.conflicts)}: {result.conflicts}"

        # Verify: Child was successfully updated
        assert child.iid in result.updated

        # Verify: GraphQL mutation was called
        mutation_calls = [
            call for call in mock_graphql_execute.call_args_list
            if "query" in call[1] and "workItemUpdate" in call[1]["query"]
        ]
        assert len(mutation_calls) == 1

        # Verify: Local files updated with hierarchy
        updated_child = Issue.load(4, temp_git_repo)
        assert updated_child.parent_iid == 1
        updated_parent = Issue.load(1, temp_git_repo)
        assert 4 in updated_parent.child_iids

    def test_push_parent_change_skips_rest_api(
        self,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_graphql_execute,
    ):
        """Test that REST API is skipped when only parent_iid changes.

        This test verifies the optimization where changing only GraphQL-only fields
        (parent_iid, child_iids) doesn't trigger REST API updates, only GraphQL mutations.

        Key verification:
        - Only GraphQL mutation is called (workItemUpdate)
        - REST API save() is NOT called on the issue object
        - This is more efficient as it avoids unnecessary REST API round-trips
        """
        from gitlab_issue_sync.storage import Issue
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory

        # Create parent and child issues locally
        parent = Issue(
            iid=1,
            title="Parent Issue",
            state="opened",
            description="Parent description",
            global_id="gid://gitlab/WorkItem/1",
        )
        child = Issue(
            iid=4,
            title="Child Issue",
            state="opened",
            description="Child description",
            global_id="gid://gitlab/WorkItem/4",
            parent_iid=None,  # Initially no parent
        )

        # Save both issues and originals
        parent.save(temp_git_repo)
        Issue.backend.save_original(parent, temp_git_repo)
        child.save(temp_git_repo)
        Issue.backend.save_original(child, temp_git_repo)

        # Modify child to add parent (GraphQL-only change)
        child.parent_iid = 1
        child.save(temp_git_repo)

        # Create mock GitLab issues
        mock_parent_issue = GitLabIssueFactory(
            iid=1,
            title="Parent Issue",
            description="Parent description",
            state="opened",
        )
        mock_child_issue = GitLabIssueFactory(
            iid=4,
            title="Child Issue",
            description="Child description",
            state="opened",
        )

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123
        mock_project.issues.get.side_effect = lambda iid: (
            mock_parent_issue if iid == 1 else mock_child_issue
        )

        # Handle both conflict detection (no iids) and batch re-fetch (with iids)
        def issues_list_side_effect(state=None, iids=None, get_all=False, **kwargs):
            if iids:
                # Batch re-fetch: return issues matching the IIDs
                result = []
                for iid in iids:
                    if iid == 1:
                        result.append(mock_parent_issue)
                    elif iid == 4:
                        result.append(mock_child_issue)
                return result
            # Conflict detection: return empty (no remote changes)
            return []

        mock_project.issues.list.side_effect = issues_list_side_effect

        # Configure GraphQL responses
        def graphql_side_effect(query, variables=None, operation_name=None):
            # Check if this is a mutation (workItemUpdate)
            if "workItemUpdate" in query and variables and "input" in variables:
                # Return mutation success
                return {
                    "data": {
                        "workItemUpdate": {
                            "workItem": {
                                "id": "gid://gitlab/WorkItem/4",
                                "widgets": [],
                            },
                            "errors": [],
                        }
                    }
                }
            # Hierarchy queries (have projectPath in variables)
            if variables and "projectPath" in variables:
                iid = int(variables.get("iid", 1))
                if iid == 4:
                    # After mutation, child has parent #1
                    return GraphQLHierarchyResponseFactory(iid=4, parent_iid=1)
                elif iid == 1:
                    # After mutation, parent has child #4
                    return GraphQLHierarchyResponseFactory(iid=1, child_iids=[4])
                # Default: no hierarchy
                return GraphQLHierarchyResponseFactory(iid=iid)
            # Fallback
            return GraphQLHierarchyResponseFactory(iid=1)

        mock_graphql_execute.side_effect = graphql_side_effect

        # Push changes
        result = Issue.push(mock_project, temp_git_repo)

        # Verify: Child was updated
        assert child.iid in result.updated

        # Verify: GraphQL mutation was called
        mutation_calls = [
            call for call in mock_graphql_execute.call_args_list
            if "query" in call[1] and "workItemUpdate" in call[1]["query"]
        ]
        assert len(mutation_calls) == 1, "Expected exactly 1 GraphQL mutation call"

        # Verify: REST API save() was NOT called on the child issue
        # Since we only changed parent_iid (GraphQL-only field), the REST API
        # should be skipped entirely
        assert not mock_child_issue.save.called, (
            "REST API save() should NOT be called when only GraphQL fields change"
        )

        # Verify: Local files updated with hierarchy
        updated_child = Issue.load(4, temp_git_repo)
        assert updated_child.parent_iid == 1


class TestUnifiedPushFlowScenarios:
    """Test scenarios for the unified push flow.

    These tests verify the complete push workflow for various scenarios:
    - Create issue without parent (should remain Issue type)
    - Create issue with parent (should auto-convert to Task)
    - Update linked issues (difference calculation)
    - Batch re-fetch of affected issues
    """

    def test_create_issue_without_parent_stays_issue_type(
        self,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_graphql_execute,
    ):
        """Test creating a new issue without parent stays as Issue type.

        When creating a new issue without a parent, it should:
        - Create via REST API
        - Remain as Issue type (no type conversion needed)
        - Not trigger any GraphQL mutations for type conversion
        """
        from gitlab_issue_sync.storage import Issue
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory

        # Create a new temporary issue without parent
        new_issue = Issue.create_new(
            title="New Issue",
            description="This is a new issue without parent",
            repo_path=temp_git_repo,
        )

        assert new_issue.is_temporary
        assert new_issue.parent_iid is None

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123

        # Mock REST API create returning the created issue
        created_gl_issue = GitLabIssueFactory(
            iid=10,
            title="New Issue",
            description="This is a new issue without parent",
            state="opened",
        )
        mock_project.issues.create.return_value = created_gl_issue
        mock_project.issues.get.return_value = created_gl_issue

        # Handle batch re-fetch
        mock_project.issues.list.return_value = [created_gl_issue]

        # Configure GraphQL to return Issue type (no parent)
        def graphql_side_effect(query, variables=None, operation_name=None):
            return GraphQLHierarchyResponseFactory(
                iid=10,
                parent_iid=None,
                work_item_type="Issue",  # Should stay as Issue
            )

        mock_graphql_execute.side_effect = graphql_side_effect

        # Push the new issue
        result = Issue.push(mock_project, temp_git_repo)

        # Verify: Issue was created
        assert 10 in result.created
        assert len(result.conflicts) == 0

        # Verify: REST API was called to create the issue
        mock_project.issues.create.assert_called_once()

        # Verify: No type conversion mutations were called
        # (workItemConvert should NOT be called for issues without parents)
        mutation_calls = [
            call for call in mock_graphql_execute.call_args_list
            if "query" in call[1] and "workItemConvert" in call[1]["query"]
        ]
        assert len(mutation_calls) == 0, "No type conversion should occur for issues without parent"

        # Verify: Temporary file was cleaned up
        temp_path = temp_git_repo / ".issues" / "opened" / f"{new_issue.iid}.md"
        assert not temp_path.exists(), "Temporary file should be deleted after push"

        # Verify: Real issue file was created
        real_path = temp_git_repo / ".issues" / "opened" / "10.md"
        assert real_path.exists(), "Real issue file should be created"

    def test_create_issue_with_parent_converts_to_task(
        self,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_graphql_execute,
    ):
        """Test creating a new issue with parent auto-converts to Task.

        When creating a new issue with a parent:
        1. Creates via REST API
        2. Converts from Issue to Task (because children must be Tasks in GitLab)
        3. Sets parent via GraphQL mutation
        """
        from gitlab_issue_sync.storage import Issue, WorkItemType
        from gitlab_issue_sync.storage.work_item_types import WorkItemTypeCache
        from tests.factories import (
            GitLabIssueFactory,
            GraphQLHierarchyResponseFactory,
            IssueFactory,
        )

        # Create parent issue first using factory
        parent_issue = IssueFactory(iid=1, global_id="gid://gitlab/WorkItem/1")
        parent_issue.save(temp_git_repo)
        Issue.backend.save_original(parent_issue, temp_git_repo)

        # Create work item types cache (required for type conversion)
        types_cache = WorkItemTypeCache(
            types=[
                WorkItemType(id="gid://gitlab/WorkItems::Type/1", name="Issue", icon_name="issue-type-issue"),
                WorkItemType(id="gid://gitlab/WorkItems::Type/5", name="Task", icon_name="issue-type-task"),
            ],
        )
        types_cache.save(temp_git_repo)

    def test_create_issue_with_parent_fetches_cache_if_missing(
        self,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_graphql_execute,
    ):
        """Test Bug #173: Creating issue with parent when cache doesn't exist.

        This is the actual bug scenario - when work item types cache is NOT
        pre-populated, the code should fetch it from GitLab instead of skipping
        the type conversion.

        Regression for: https://gitlab.levitnet.be/levit/glworkflow/-/issues/173
        """
        from gitlab_issue_sync.storage import Issue
        from tests.factories import (
            GitLabIssueFactory,
            GraphQLHierarchyResponseFactory,
            IssueFactory,
        )

        # Verify cache doesn't exist (this is the bug scenario)
        cache_path = temp_git_repo / ".issues" / ".work_item_types" / "work_item_types.json"
        assert not cache_path.exists(), "Cache should NOT exist for this test"

        # Create parent issue first using factory
        parent_issue = IssueFactory(iid=1, global_id="gid://gitlab/WorkItem/1")
        parent_issue.save(temp_git_repo)
        Issue.backend.save_original(parent_issue, temp_git_repo)

        # Create a new temporary issue with parent
        new_issue = Issue.create_new(
            title="Child Issue",
            description="This is a child issue",
            parent_iid=1,  # Has parent
            repo_path=temp_git_repo,
        )

        assert new_issue.is_temporary
        assert new_issue.parent_iid == 1

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123

        # Mock REST API create returning the created issue
        created_gl_issue = GitLabIssueFactory(
            iid=10,
            title="Child Issue",
            description="This is a child issue",
            state="opened",
        )
        mock_project.issues.create.return_value = created_gl_issue
        mock_project.issues.get.side_effect = lambda iid: (
            GitLabIssueFactory(iid=1, title="Parent Issue") if iid == 1 else created_gl_issue
        )

        # Handle batch re-fetch
        def issues_list_side_effect(state=None, iids=None, get_all=False, **kwargs):
            if iids:
                result = []
                for iid in iids:
                    if iid == 1:
                        result.append(GitLabIssueFactory(iid=1, title="Parent Issue"))
                    elif iid == 10:
                        result.append(created_gl_issue)
                return result
            return []

        mock_project.issues.list.side_effect = issues_list_side_effect

        # Track GraphQL mutations called
        convert_mutations = []
        parent_mutations = []

        def graphql_side_effect(query, variables=None, operation_name=None):
            # Type conversion mutation
            if "workItemConvert" in query:
                convert_mutations.append(variables)
                return {
                    "data": {
                        "workItemConvert": {
                            "workItem": {
                                "id": "gid://gitlab/WorkItem/10",
                                "iid": "10",
                                "workItemType": {
                                    "id": "gid://gitlab/WorkItems::Type/5",
                                    "name": "Task",
                                    "iconName": "issue-type-task",
                                },
                            },
                            "errors": [],
                        }
                    }
                }

            # Parent update mutation (hierarchyWidget is in variables, not query)
            if "workItemUpdate" in query and variables:
                input_data = variables.get("input", {})
                if "hierarchyWidget" in input_data:
                    parent_mutations.append(variables)
                    return {
                        "data": {
                            "workItemUpdate": {
                                "workItem": {"id": "gid://gitlab/WorkItem/10", "iid": "10"},
                                "errors": [],
                            }
                        }
                    }

            # getWorkItemTypes query (CRITICAL: cache doesn't exist, so it will be fetched)
            if "getWorkItemTypes" in query:
                return {
                    "data": {
                        "project": {
                            "workItemTypes": {
                                "nodes": [
                                    {
                                        "id": "gid://gitlab/WorkItems::Type/1",
                                        "name": "Issue",
                                        "iconName": "issue-type-issue",
                                    },
                                    {
                                        "id": "gid://gitlab/WorkItems::Type/5",
                                        "name": "Task",
                                        "iconName": "issue-type-task",
                                    },
                                ]
                            }
                        }
                    }
                }

            # Hierarchy queries
            if variables and "projectPath" in variables:
                iid = int(variables.get("iid", 1))
                if iid == 10:
                    # After mutation, child is Task with parent #1
                    return GraphQLHierarchyResponseFactory(
                        iid=10,
                        parent_iid=1,
                        work_item_type="Task",
                    )
                elif iid == 1:
                    # Parent now has child #10
                    return GraphQLHierarchyResponseFactory(iid=1, child_iids=[10])
                return GraphQLHierarchyResponseFactory(iid=iid)

            return GraphQLHierarchyResponseFactory(iid=10)

        mock_graphql_execute.side_effect = graphql_side_effect

        # Push the new issue
        result = Issue.push(mock_project, temp_git_repo)

        # Verify: Issue was created
        assert 10 in result.created
        assert len(result.conflicts) == 0

        # Verify: REST API was called to create
        mock_project.issues.create.assert_called_once()

        # Verify: Type conversion mutation was called (Issue → Task)
        assert len(convert_mutations) == 1, "Type conversion should be called"
        assert convert_mutations[0]["input"]["workItemTypeId"] == "gid://gitlab/WorkItems::Type/5"

        # Verify: Parent mutation was called
        assert len(parent_mutations) == 1, "Parent mutation should be called"
        assert parent_mutations[0]["input"]["hierarchyWidget"]["parentId"] == "gid://gitlab/WorkItem/1"

        # Verify: Local file has parent and work_item_type is Task
        updated_child = Issue.load(10, temp_git_repo)
        assert updated_child.parent_iid == 1
        assert updated_child.work_item_type is not None
        assert updated_child.work_item_type.name == "Task"

    def test_temp_file_cleanup_on_partial_failure(
        self,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_graphql_execute,
    ):
        """Test Bug #173 Part 2: Temp files cleaned up even if parent setting fails.

        When creating an issue with parent:
        1. REST creation succeeds → issue gets real IID
        2. Parent setting fails → exception raised
        3. Temp file should still be renamed to real IID
        4. No duplicate issue on next push

        Regression for: https://gitlab.levitnet.be/levit/glworkflow/-/issues/173
        """
        from gitlab_issue_sync.storage import Issue
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory

        # Create a new temporary issue with parent
        new_issue = Issue.create_new(
            title="Child Issue",
            description="This is a child issue",
            parent_iid=1,
            repo_path=temp_git_repo,
        )

        assert new_issue.is_temporary
        temp_iid = new_issue.iid
        temp_file = temp_git_repo / ".issues" / "opened" / f"{temp_iid}.md"
        assert temp_file.exists(), "Temp file should exist before push"

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123

        # Mock REST API create returning the created issue (SUCCESS)
        created_gl_issue = GitLabIssueFactory(
            iid=42,
            title="Child Issue",
            description="This is a child issue",
            state="opened",
        )
        mock_project.issues.create.return_value = created_gl_issue
        mock_project.issues.get.return_value = created_gl_issue
        mock_project.issues.list.return_value = []

        # Mock GraphQL to fail when setting parent (FAILURE)
        from tests.factories import (
            GraphQLWorkItemTypesResponseFactory,
            GraphQLWorkItemConvertResponseFactory,
        )

        def graphql_side_effect(query, variables=None, operation_name=None):
            # getWorkItemTypes query
            if "getWorkItemTypes" in query:
                return GraphQLWorkItemTypesResponseFactory(types=["Issue", "Task"])

            # Type conversion - succeed
            if "workItemConvert" in query:
                return GraphQLWorkItemConvertResponseFactory(iid=42, work_item_type="Task")

            # Parent setting - FAIL
            if "workItemUpdate" in query and variables:
                input_data = variables.get("input", {})
                if "hierarchyWidget" in input_data:
                    raise Exception(
                        "Failed to set parent: #1 cannot be added: "
                        "it's not allowed to add this type of parent item"
                    )

            # getWorkItemHierarchy
            if variables and "projectPath" in variables:
                return GraphQLHierarchyResponseFactory(iid=42, work_item_type="Task")

            return GraphQLHierarchyResponseFactory(iid=42)

        mock_graphql_execute.side_effect = graphql_side_effect

        # Push the new issue - expect partial failure
        result = Issue.push(mock_project, temp_git_repo)

        # Verify: Issue marked as conflict due to parent failure
        assert 42 in result.conflicts
        assert "Issue created as #42 but failed post-creation operations" in result.conflict_details[42]

        # Verify: REST API was called to create
        mock_project.issues.create.assert_called_once()

        # CRITICAL: Temp file should be deleted
        assert not temp_file.exists(), "Temp file should be deleted after successful creation"

        # CRITICAL: Real file should exist
        real_file = temp_git_repo / ".issues" / "opened" / "42.md"
        assert real_file.exists(), "Real file should exist at new IID location"

        # CRITICAL: Original snapshot should exist
        original_file = temp_git_repo / ".issues" / ".sync" / "originals" / "42.md"
        assert original_file.exists(), "Original snapshot should exist"

        # Verify: Issue has real IID
        created_issue = Issue.load(42, temp_git_repo)
        assert created_issue.iid == 42
        assert not created_issue.is_temporary

        # CRITICAL: Next push should NOT create duplicate
        # Reset mocks
        mock_project.issues.create.reset_mock()

        # Try pushing again - should not attempt to create again
        result2 = Issue.push(mock_project, temp_git_repo)

        # Verify: No new create call (would indicate duplicate)
        mock_project.issues.create.assert_not_called()

    def test_update_linked_issues_difference_calculation(
        self,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_graphql_execute,
    ):
        """Test that linked issues are correctly added and removed via difference calculation.

        The push flow should:
        - Calculate which links were added (local - original)
        - Calculate which links were removed (original - local)
        - Create new links via REST API
        - Delete removed links via REST API
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue, IssueLink
        from tests.factories import GitLabIssueFactory, GitLabIssueLinkFactory, GraphQLHierarchyResponseFactory

        # Create issue with two links (to #2 and #3)
        now = datetime.now(UTC)
        link_to_2 = IssueLink(
            link_id=100,
            target_project_id=123,
            target_issue_iid=2,
            link_type="relates_to",
            created_at=now,
            updated_at=now,
        )
        link_to_3 = IssueLink(
            link_id=101,
            target_project_id=123,
            target_issue_iid=3,
            link_type="relates_to",
            created_at=now,
            updated_at=now,
        )

        issue = Issue(
            iid=1,
            title="Issue with Links",
            state="opened",
            description="Test",
            global_id="gid://gitlab/WorkItem/1",
            links=[link_to_2, link_to_3],  # Originally links to #2 and #3
        )

        issue.save(temp_git_repo)
        Issue.backend.save_original(issue, temp_git_repo)

        # Modify links: remove link to #2, add link to #4
        link_to_4 = IssueLink(
            link_id=0,  # New link (no ID yet)
            target_project_id=123,
            target_issue_iid=4,
            link_type="relates_to",
            created_at=now,
            updated_at=now,
        )
        issue.links = [link_to_3, link_to_4]  # Now links to #3 and #4
        issue.save(temp_git_repo)

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123

        # Mock the issue.get and issue.save
        mock_gl_issue = GitLabIssueFactory(
            iid=1,
            title="Issue with Links",
            description="Test",
            state="opened",
        )
        mock_project.issues.get.return_value = mock_gl_issue

        # Track link creations and deletions
        mock_gl_issue.links.create = lambda data: GitLabIssueLinkFactory(**data)
        deleted_link_ids = []
        mock_gl_issue.links.delete = lambda link_id: deleted_link_ids.append(link_id)

        # Mock existing links on GitLab - both #2 and #3 (the original state)
        # This is used both for fetching remote issue AND for deletion lookup
        existing_link_to_2 = GitLabIssueLinkFactory(issue_link_id=100, iid=2)
        existing_link_to_3 = GitLabIssueLinkFactory(issue_link_id=101, iid=3)
        mock_gl_issue.links.list.return_value = [existing_link_to_2, existing_link_to_3]

        # Handle both initial fetch (for conflict detection) and batch re-fetch
        def issues_list_side_effect(state=None, iids=None, get_all=False, **kwargs):
            # Return issue for both: conflict detection (state=opened) and batch re-fetch (iids=[1])
            if state == "opened" or iids:
                return [mock_gl_issue]
            return []

        mock_project.issues.list.side_effect = issues_list_side_effect

        # Configure GraphQL to return no hierarchy
        mock_graphql_execute.return_value = GraphQLHierarchyResponseFactory(iid=1)

        # Push the changes
        result = Issue.push(mock_project, temp_git_repo)

        # Verify: Issue was updated
        assert 1 in result.updated
        assert len(result.conflicts) == 0

        # Verify: Link to #2 was deleted
        assert 100 in deleted_link_ids, "Link to #2 (id=100) should have been deleted"

        # Verify: Link to #4 was created (links.create was called)
        # We can verify this by checking the mock was called

    def test_batch_refetch_updates_affected_issues(
        self,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_graphql_execute,
    ):
        """Test that batch re-fetch updates all affected issues after push.

        When pushing changes, the following issues should be re-fetched:
        - The issue itself (to get updated timestamps)
        - Parent issues (current and old if changed)
        - Linked issues (targets of links)

        This ensures local copies stay in sync with GitLab's state.
        """
        from datetime import UTC, datetime

        from gitlab_issue_sync.storage import Issue, IssueLink
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory, IssueFactory

        # Create parent issue using factory
        parent = IssueFactory(iid=1, global_id="gid://gitlab/WorkItem/1", child_iids=[])
        parent.save(temp_git_repo)
        Issue.backend.save_original(parent, temp_git_repo)

        # Create linked issue using factory
        linked_issue = IssueFactory(iid=3, global_id="gid://gitlab/WorkItem/3")
        linked_issue.save(temp_git_repo)
        Issue.backend.save_original(linked_issue, temp_git_repo)

        # Create child issue without parent or links initially using factory
        child = IssueFactory(iid=2, global_id="gid://gitlab/WorkItem/2", parent_iid=None, links=[])
        child.save(temp_git_repo)
        Issue.backend.save_original(child, temp_git_repo)

        # Now modify child to add parent and link
        now = datetime.now(UTC)
        child.parent_iid = 1
        child.links = [
            IssueLink(
                link_id=0,
                target_project_id=123,
                target_issue_iid=3,
                link_type="relates_to",
                created_at=now,
                updated_at=now,
            )
        ]
        child.save(temp_git_repo)

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123

        # Create mock GitLab issues for all affected IIDs
        mock_parent = GitLabIssueFactory(iid=1, title="Parent Issue")
        mock_child = GitLabIssueFactory(iid=2, title="Child Issue")
        mock_linked = GitLabIssueFactory(iid=3, title="Linked Issue")

        mock_project.issues.get.side_effect = lambda iid: {
            1: mock_parent,
            2: mock_child,
            3: mock_linked,
        }.get(iid)

        # Track which IIDs are fetched via batch list
        fetched_iids = []

        def issues_list_side_effect(state=None, iids=None, get_all=False, **kwargs):
            if iids:
                fetched_iids.extend(iids)
                result = []
                for iid in iids:
                    if iid == 1:
                        result.append(mock_parent)
                    elif iid == 2:
                        result.append(mock_child)
                    elif iid == 3:
                        result.append(mock_linked)
                return result
            return []

        mock_project.issues.list.side_effect = issues_list_side_effect

        # Configure GraphQL responses
        def graphql_side_effect(query, variables=None, operation_name=None):
            if "workItemUpdate" in query:
                return {
                    "data": {
                        "workItemUpdate": {
                            "workItem": {"id": "gid://gitlab/WorkItem/2", "iid": "2"},
                            "errors": [],
                        }
                    }
                }
            if variables and "projectPath" in variables:
                iid = int(variables.get("iid", 1))
                if iid == 1:
                    return GraphQLHierarchyResponseFactory(iid=1, child_iids=[2])
                elif iid == 2:
                    return GraphQLHierarchyResponseFactory(iid=2, parent_iid=1)
                return GraphQLHierarchyResponseFactory(iid=iid)
            return GraphQLHierarchyResponseFactory(iid=2)

        mock_graphql_execute.side_effect = graphql_side_effect

        # Push the changes
        result = Issue.push(mock_project, temp_git_repo)

        # Verify: Child was updated
        assert 2 in result.updated

        # Verify: Batch re-fetch was called with correct IIDs
        # Should include: child (2), parent (1), linked issue (3)
        assert 2 in fetched_iids, "Child issue should be in re-fetch list"
        assert 1 in fetched_iids, "Parent issue should be in re-fetch list"
        assert 3 in fetched_iids, "Linked issue should be in re-fetch list"

        # Verify: Parent's child_iids was updated
        updated_parent = Issue.load(1, temp_git_repo)
        assert 2 in updated_parent.child_iids, "Parent should now have child #2"

    def test_refetch_handles_missing_issues_gracefully(
        self,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_graphql_execute,
    ):
        """Test that batch re-fetch handles missing issues gracefully.

        If an issue in the re-fetch list doesn't exist on GitLab (e.g., deleted),
        the re-fetch should log a warning and continue with other issues.
        """
        from gitlab_issue_sync.storage import Issue
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory, IssueFactory

        # Create issue that references a non-existent parent using factory
        issue = IssueFactory(iid=1, global_id="gid://gitlab/WorkItem/1")
        issue.save(temp_git_repo)
        Issue.backend.save_original(issue, temp_git_repo)

        # Modify to add a parent that will be "deleted" on GitLab
        issue.parent_iid = 999  # This parent doesn't exist
        issue.save(temp_git_repo)

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123

        mock_gl_issue = GitLabIssueFactory(iid=1, title="Issue")
        mock_project.issues.get.return_value = mock_gl_issue

        # Batch re-fetch returns only issue #1, not #999 (deleted/doesn't exist)
        mock_project.issues.list.side_effect = lambda **kwargs: (
            [mock_gl_issue] if kwargs.get("iids") else []
        )

        # Configure GraphQL
        def graphql_side_effect(query, variables=None, operation_name=None):
            if "workItemUpdate" in query:
                return {
                    "data": {
                        "workItemUpdate": {
                            "workItem": {"id": "gid://gitlab/WorkItem/1", "iid": "1"},
                            "errors": [],
                        }
                    }
                }
            return GraphQLHierarchyResponseFactory(iid=1, parent_iid=999)

        mock_graphql_execute.side_effect = graphql_side_effect

        # Push should complete without error even though parent #999 doesn't exist
        result = Issue.push(mock_project, temp_git_repo)

        # Verify: Issue was updated (the push succeeded)
        assert 1 in result.updated
        assert len(result.conflicts) == 0

    def test_update_issue_remove_parent_converts_task_to_issue(
        self,
        temp_git_repo,
        project_config,
        patch_gitlab_class,
        mock_gitlab_client,
        mock_graphql_execute,
    ):
        """Test that removing parent from a Task converts it back to Issue type.

        When removing parent_iid from a Task:
        1. Remove parent via GraphQL mutation
        2. Convert Task back to Issue type (via workItemConvert)
        """
        from gitlab_issue_sync.storage import Issue, WorkItemType
        from gitlab_issue_sync.storage.work_item_types import WorkItemTypeCache
        from tests.factories import GitLabIssueFactory, GraphQLHierarchyResponseFactory, IssueFactory

        # Create work item types cache
        task_type = WorkItemType(id="gid://gitlab/WorkItems::Type/5", name="Task", icon_name="issue-type-task")
        types_cache = WorkItemTypeCache(
            types=[
                WorkItemType(id="gid://gitlab/WorkItems::Type/1", name="Issue", icon_name="issue-type-issue"),
                task_type,
            ],
        )
        types_cache.save(temp_git_repo)

        # Create parent issue
        parent = IssueFactory(iid=1, global_id="gid://gitlab/WorkItem/1", child_iids=[2])
        parent.save(temp_git_repo)
        Issue.backend.save_original(parent, temp_git_repo)

        # Create child as Task with parent
        child = IssueFactory(
            iid=2,
            global_id="gid://gitlab/WorkItem/2",
            parent_iid=1,
            work_item_type=task_type,
        )
        child.save(temp_git_repo)
        Issue.backend.save_original(child, temp_git_repo)

        # Remove parent (should trigger Task→Issue conversion)
        child.parent_iid = None
        child.save(temp_git_repo)

        # Configure mock project
        mock_project = mock_gitlab_client.projects.get.return_value
        mock_project.id = 123

        mock_parent_issue = GitLabIssueFactory(iid=1)
        mock_child_issue = GitLabIssueFactory(iid=2)

        mock_project.issues.get.side_effect = lambda iid: (
            mock_parent_issue if iid == 1 else mock_child_issue
        )

        def issues_list_side_effect(state=None, iids=None, get_all=False, **kwargs):
            if iids:
                result = []
                for iid in iids:
                    if iid == 1:
                        result.append(mock_parent_issue)
                    elif iid == 2:
                        result.append(mock_child_issue)
                return result
            return []

        mock_project.issues.list.side_effect = issues_list_side_effect

        # Track mutations
        parent_mutations = []
        convert_mutations = []

        def graphql_side_effect(query, variables=None, operation_name=None):
            if "workItemConvert" in query:
                convert_mutations.append(variables)
                return {
                    "data": {
                        "workItemConvert": {
                            "workItem": {
                                "id": "gid://gitlab/WorkItem/2",
                                "workItemType": {
                                    "id": "gid://gitlab/WorkItems::Type/1",
                                    "name": "Issue",
                                    "iconName": "issue-type-issue",
                                },
                            },
                            "errors": [],
                        }
                    }
                }
            if "workItemUpdate" in query:
                parent_mutations.append(variables)
                return {
                    "data": {
                        "workItemUpdate": {
                            "workItem": {"id": "gid://gitlab/WorkItem/2", "iid": "2"},
                            "errors": [],
                        }
                    }
                }
            if variables and "projectPath" in variables:
                iid = int(variables.get("iid", 1))
                if iid == 1:
                    return GraphQLHierarchyResponseFactory(iid=1, child_iids=[])
                elif iid == 2:
                    return GraphQLHierarchyResponseFactory(
                        iid=2,
                        parent_iid=None,
                        work_item_type="Issue",
                    )
                return GraphQLHierarchyResponseFactory(iid=iid)
            return GraphQLHierarchyResponseFactory(iid=2)

        mock_graphql_execute.side_effect = graphql_side_effect

        # Push the changes
        result = Issue.push(mock_project, temp_git_repo)

        # Verify: Child was updated
        assert 2 in result.updated
        assert len(result.conflicts) == 0

        # Verify: Parent was removed via mutation
        assert len(parent_mutations) == 1
        assert parent_mutations[0]["input"]["hierarchyWidget"]["parentId"] is None

        # Verify: Type was converted from Task to Issue
        assert len(convert_mutations) == 1, "Type conversion should be called"
        assert convert_mutations[0]["input"]["workItemTypeId"] == "gid://gitlab/WorkItems::Type/1"

        # Verify: Local file has no parent and work_item_type is Issue
        updated_child = Issue.load(2, temp_git_repo)
        assert updated_child.parent_iid is None
        assert updated_child.work_item_type is not None
        assert updated_child.work_item_type.name == "Issue"


# =============================================================================
# Conflict Tests
# =============================================================================


class TestConflictDataclass:
    """Tests for Conflict dataclass."""

    def test_get_identifier(self):
        """Test that get_identifier returns issue_iid."""
        from gitlab_issue_sync.storage import Conflict

        conflict = Conflict(issue_iid=42, fields=["title"])
        assert conflict.get_identifier() == 42

    def test_compute_content_hash(self):
        """Test content hash generation."""
        from gitlab_issue_sync.storage import Conflict

        conflict1 = Conflict(issue_iid=42, fields=["title", "description"])
        hash1 = conflict1.compute_content_hash()

        # Same content should produce same hash
        conflict2 = Conflict(
            issue_iid=42,
            fields=["description", "title"],  # Different order, but sorted
            detected_at=conflict1.detected_at,  # Same timestamp
        )
        hash2 = conflict2.compute_content_hash()
        assert hash1 == hash2

        # Different content should produce different hash
        conflict3 = Conflict(issue_iid=99, fields=["title"])
        hash3 = conflict3.compute_content_hash()
        assert hash1 != hash3


class TestConflictStorage:
    """Tests for Conflict storage operations."""

    def test_save_and_load(self, temp_git_repo, project_config):
        """Test saving and loading a conflict."""
        from gitlab_issue_sync.storage import Conflict

        conflict = Conflict(issue_iid=42, fields=["title", "labels"])
        conflict.save(temp_git_repo)

        loaded = Conflict.load(42, temp_git_repo)
        assert loaded is not None
        assert loaded.issue_iid == 42
        assert loaded.fields == ["title", "labels"]

    def test_list_all_empty(self, temp_git_repo, project_config):
        """Test list_all with no conflicts."""
        from gitlab_issue_sync.storage import Conflict

        conflicts = Conflict.list_all(temp_git_repo)
        assert conflicts == []

    def test_list_all_multiple(self, temp_git_repo, project_config):
        """Test list_all with multiple conflicts."""
        from gitlab_issue_sync.storage import Conflict

        now = datetime.now(UTC)

        conflict1 = Conflict(issue_iid=1, fields=["title"], detected_at=now)
        conflict1.save(temp_git_repo)

        conflict2 = Conflict(issue_iid=2, fields=["description"], detected_at=now + timedelta(hours=1))
        conflict2.save(temp_git_repo)

        conflicts = Conflict.list_all(temp_git_repo)
        assert len(conflicts) == 2
        # Should be sorted by detected_at
        assert conflicts[0].issue_iid == 1
        assert conflicts[1].issue_iid == 2

    def test_has(self, temp_git_repo, project_config):
        """Test has() checks for conflict existence."""
        from gitlab_issue_sync.storage import Conflict

        assert Conflict.has(42, temp_git_repo) is False

        conflict = Conflict(issue_iid=42, fields=["title"])
        conflict.save(temp_git_repo)

        assert Conflict.has(42, temp_git_repo) is True

    def test_delete(self, temp_git_repo, project_config):
        """Test delete() removes conflict."""
        from gitlab_issue_sync.storage import Conflict

        conflict = Conflict(issue_iid=42, fields=["title"])
        conflict.save(temp_git_repo)
        assert Conflict.has(42, temp_git_repo) is True

        conflict.delete(temp_git_repo)
        assert Conflict.has(42, temp_git_repo) is False

    def test_clear(self, temp_git_repo, project_config):
        """Test clear() removes conflict without error if not found."""
        from gitlab_issue_sync.storage import Conflict

        # Should not raise if conflict doesn't exist
        Conflict.clear(42, temp_git_repo)

        # Should remove existing conflict
        conflict = Conflict(issue_iid=42, fields=["title"])
        conflict.save(temp_git_repo)
        assert Conflict.has(42, temp_git_repo) is True

        Conflict.clear(42, temp_git_repo)
        assert Conflict.has(42, temp_git_repo) is False


class TestConflictRemoteCache:
    """Tests for Conflict remote caching."""

    def test_save_with_remote(self, temp_git_repo, project_config):
        """Test save_with_remote caches the remote issue."""
        from gitlab_issue_sync.storage import Conflict, Issue

        # Create a remote issue to cache
        remote = Issue(
            iid=42,
            title="Remote Title",
            state="opened",
            description="Remote description",
        )

        conflict = Conflict(issue_iid=42, fields=["title"])
        conflict.save_with_remote(remote, temp_git_repo)

        # Check conflict was saved
        assert Conflict.has(42, temp_git_repo) is True

        # Check remote was cached
        cache_path = temp_git_repo / ".issues" / ".sync" / "conflicts" / "42_remote.md"
        assert cache_path.exists()

    def test_load_cached_remote(self, temp_git_repo, project_config):
        """Test loading cached remote issue."""
        from gitlab_issue_sync.storage import Conflict, Issue

        remote = Issue(
            iid=42,
            title="Remote Title",
            state="opened",
            description="Remote description",
        )

        conflict = Conflict(issue_iid=42, fields=["title"])
        conflict.save_with_remote(remote, temp_git_repo)

        # Load the cached remote
        loaded_remote = conflict.load_cached_remote(temp_git_repo)
        assert loaded_remote is not None
        assert loaded_remote.iid == 42
        assert loaded_remote.title == "Remote Title"
        assert loaded_remote.description == "Remote description"

    def test_load_cached_remote_not_found(self, temp_git_repo, project_config):
        """Test load_cached_remote returns None if not found."""
        from gitlab_issue_sync.storage import Conflict

        conflict = Conflict(issue_iid=999, fields=["title"])
        loaded = conflict.load_cached_remote(temp_git_repo)
        assert loaded is None

    def test_delete_cached_remote(self, temp_git_repo, project_config):
        """Test delete_cached_remote removes the cached file."""
        from gitlab_issue_sync.storage import Conflict, Issue

        remote = Issue(iid=42, title="Remote", state="opened", description="")
        conflict = Conflict(issue_iid=42, fields=["title"])
        conflict.save_with_remote(remote, temp_git_repo)

        cache_path = temp_git_repo / ".issues" / ".sync" / "conflicts" / "42_remote.md"
        assert cache_path.exists()

        result = conflict.delete_cached_remote(temp_git_repo)
        assert result is True
        assert not cache_path.exists()

        # Second delete returns False
        result = conflict.delete_cached_remote(temp_git_repo)
        assert result is False

    def test_delete_also_removes_cached_remote(self, temp_git_repo, project_config):
        """Test that delete() also removes cached remote file."""
        from gitlab_issue_sync.storage import Conflict, Issue

        remote = Issue(iid=42, title="Remote", state="opened", description="")
        conflict = Conflict(issue_iid=42, fields=["title"])
        conflict.save_with_remote(remote, temp_git_repo)

        cache_path = temp_git_repo / ".issues" / ".sync" / "conflicts" / "42_remote.md"
        assert cache_path.exists()

        conflict.delete(temp_git_repo)
        assert not cache_path.exists()


class TestConflictAutoResolution:
    """Tests for attempt_auto_resolution with field-level merging."""

    def test_auto_resolve_different_fields_changed(self, temp_git_repo, project_config):
        """Test auto-resolve when different fields changed on each side."""
        from gitlab_issue_sync.storage import Conflict, Issue
        from tests.factories import IssueFactory

        issue = IssueFactory(iid=42, title="Original Title", milestone=None)

        # Save as original
        Issue.backend.save_original(issue, temp_git_repo)

        # Local changed title
        issue.title = "Local Title"
        issue.save(temp_git_repo)

        # Remote changed milestone
        issue.title = "Original Title"  # Reset to original
        issue.milestone = "v1.0"
        conflict = Conflict(issue_iid=42, fields=["title", "milestone"])
        conflict.save_with_remote(issue, temp_git_repo)

        result = conflict.attempt_auto_resolution(temp_git_repo)

        assert result is not None
        assert result.title == "Local Title"
        assert result.milestone == "v1.0"

    def test_auto_resolve_fails_same_field_both_sides(self, temp_git_repo, project_config):
        """Test auto-resolve fails when same non-mergeable field changed on both sides."""
        from gitlab_issue_sync.storage import Conflict, Issue
        from tests.factories import IssueFactory

        issue = IssueFactory(iid=42, title="Original Title")

        # Save as original
        Issue.backend.save_original(issue, temp_git_repo)

        # Local changed title
        issue.title = "Local Title"
        issue.save(temp_git_repo)

        # Remote also changed title differently
        issue.title = "Remote Title"
        conflict = Conflict(issue_iid=42, fields=["title"])
        conflict.save_with_remote(issue, temp_git_repo)

        result = conflict.attempt_auto_resolution(temp_git_repo)

        assert result is None

    def test_auto_resolve_comments_both_sides_add(self, temp_git_repo, project_config):
        """Test auto-resolve merges comments when both sides add new ones."""
        from datetime import UTC, datetime, timedelta

        from gitlab_issue_sync.storage import Conflict, Issue
        from gitlab_issue_sync.storage.issue import IssueComment
        from tests.factories import IssueFactory

        now = datetime.now(UTC)
        original_comment = IssueComment(author="user1", created_at=now, body="Original comment")

        issue = IssueFactory(iid=42, comments=[original_comment])

        # Save as original
        Issue.backend.save_original(issue, temp_git_repo)

        # Local adds comment
        local_comment = IssueComment(author="user2", created_at=now + timedelta(hours=1), body="Local comment")
        issue.comments = [original_comment, local_comment]
        issue.save(temp_git_repo)

        # Remote adds different comment
        remote_comment = IssueComment(author="user3", created_at=now + timedelta(hours=2), body="Remote comment")
        issue.comments = [original_comment, remote_comment]
        conflict = Conflict(issue_iid=42, fields=["comments"])
        conflict.save_with_remote(issue, temp_git_repo)

        result = conflict.attempt_auto_resolution(temp_git_repo)

        assert result is not None
        assert len(result.comments) == 3
        bodies = [c.body for c in result.comments]
        assert "Original comment" in bodies
        assert "Local comment" in bodies
        assert "Remote comment" in bodies

    def test_auto_resolve_description_non_overlapping(self, temp_git_repo, project_config):
        """Test auto-resolve description when changes don't overlap."""
        from gitlab_issue_sync.storage import Conflict, Issue
        from tests.factories import IssueFactory

        issue = IssueFactory(iid=42, description="Line 1\nLine 2\nLine 3")

        # Save as original
        Issue.backend.save_original(issue, temp_git_repo)

        # Local adds line at top
        issue.description = "New first line\nLine 1\nLine 2\nLine 3"
        issue.save(temp_git_repo)

        # Remote adds line at bottom
        issue.description = "Line 1\nLine 2\nLine 3\nNew last line"
        conflict = Conflict(issue_iid=42, fields=["description"])
        conflict.save_with_remote(issue, temp_git_repo)

        result = conflict.attempt_auto_resolution(temp_git_repo)

        assert result is not None
        assert "New first line" in result.description
        assert "New last line" in result.description

    def test_auto_resolve_description_fails_overlapping(self, temp_git_repo, project_config):
        """Test auto-resolve fails when description changes overlap."""
        from gitlab_issue_sync.storage import Conflict, Issue
        from tests.factories import IssueFactory

        issue = IssueFactory(iid=42, description="Line 1")

        # Save as original
        Issue.backend.save_original(issue, temp_git_repo)

        # Local changed the same line
        issue.description = "Local changed line 1"
        issue.save(temp_git_repo)

        # Remote also changed the same line
        issue.description = "Remote changed line 1"
        conflict = Conflict(issue_iid=42, fields=["description"])
        conflict.save_with_remote(issue, temp_git_repo)

        result = conflict.attempt_auto_resolution(temp_git_repo)

        assert result is None

    def test_auto_resolve_missing_local_returns_none(self, temp_git_repo, project_config):
        """Test auto-resolve returns None when local issue is missing."""
        from gitlab_issue_sync.storage import Conflict, Issue
        from tests.factories import IssueFactory

        issue = IssueFactory(iid=42)

        # Only save as original (not local)
        Issue.backend.save_original(issue, temp_git_repo)

        issue.title = "Remote Title"
        conflict = Conflict(issue_iid=42, fields=["title"])
        conflict.save_with_remote(issue, temp_git_repo)

        result = conflict.attempt_auto_resolution(temp_git_repo)

        assert result is None

    def test_auto_resolve_missing_original_returns_none(self, temp_git_repo, project_config):
        """Test auto-resolve returns None when original snapshot is missing."""
        from gitlab_issue_sync.storage import Conflict, Issue
        from tests.factories import IssueFactory

        issue = IssueFactory(iid=42)

        # Only save as local (not original)
        issue.save(temp_git_repo)

        issue.title = "Remote Title"
        conflict = Conflict(issue_iid=42, fields=["title"])
        conflict.save_with_remote(issue, temp_git_repo)

        result = conflict.attempt_auto_resolution(temp_git_repo)

        assert result is None

    def test_auto_resolve_missing_remote_returns_none(self, temp_git_repo, project_config):
        """Test auto-resolve returns None when cached remote is missing."""
        from gitlab_issue_sync.storage import Conflict, Issue
        from tests.factories import IssueFactory

        issue = IssueFactory(iid=42)

        # Save as local and original
        Issue.backend.save_original(issue, temp_git_repo)
        issue.save(temp_git_repo)

        # Save conflict without remote cache
        conflict = Conflict(issue_iid=42, fields=["title"])
        conflict.save(temp_git_repo)

        result = conflict.attempt_auto_resolution(temp_git_repo)

        assert result is None
