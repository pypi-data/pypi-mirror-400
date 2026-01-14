"""Tests for metadata handlers."""

import pytest

from gitlab_issue_sync.metadata_manager import (
    MetadataChange,
    ParentHandler,
)
from tests.factories import IssueFactory


class TestParentHandler:
    """Test ParentHandler for work item hierarchy."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ParentHandler()

    def test_metadata_name(self):
        """Test metadata name property."""
        assert self.handler.metadata_name == "parent"

    def test_metadata_key(self):
        """Test metadata key property."""
        assert self.handler.metadata_key == "parent_iid"

    def test_get_values_with_parent(self):
        """Test getting parent when set."""
        issue = IssueFactory(parent_iid=42)
        values = self.handler.get_values(issue)
        assert values == [42]

    def test_get_values_without_parent(self):
        """Test getting parent when not set."""
        issue = IssueFactory(parent_iid=None)
        values = self.handler.get_values(issue)
        assert values == []

    def test_set_values_new_parent(self):
        """Test setting parent when none exists."""
        issue = IssueFactory(iid=10, parent_iid=None)
        change = self.handler.set_values(issue, [42])

        assert issue.parent_iid == 42
        assert change.added == [42]
        assert change.removed == []
        assert change.unchanged == []

    def test_set_values_replace_parent(self):
        """Test replacing existing parent."""
        issue = IssueFactory(iid=10, parent_iid=42)
        change = self.handler.set_values(issue, [99])

        assert issue.parent_iid == 99
        assert change.added == [99]
        assert change.removed == [42]
        assert change.unchanged == []

    def test_set_values_same_parent(self):
        """Test setting same parent (no change)."""
        issue = IssueFactory(iid=10, parent_iid=42)
        change = self.handler.set_values(issue, [42])

        assert issue.parent_iid == 42
        assert change.added == []
        assert change.removed == []
        assert change.unchanged == [42]

    def test_set_values_self_reference_error(self):
        """Test that issue cannot be its own parent."""
        issue = IssueFactory(iid=10, parent_iid=None)

        with pytest.raises(ValueError, match="cannot be its own parent"):
            self.handler.set_values(issue, [10])

    def test_unset_values_with_parent(self):
        """Test unsetting parent when one exists."""
        issue = IssueFactory(iid=10, parent_iid=42)
        change = self.handler.unset_values(issue)

        assert issue.parent_iid is None
        assert change.added == []
        assert change.removed == [42]
        assert change.unchanged == []

    def test_unset_values_without_parent(self):
        """Test unsetting parent when none exists."""
        issue = IssueFactory(iid=10, parent_iid=None)
        change = self.handler.unset_values(issue)

        assert issue.parent_iid is None
        assert change.added == []
        assert change.removed == []
        assert change.unchanged == []

    def test_add_values_not_supported(self):
        """Test that add operation is not supported."""
        issue = IssueFactory(iid=10)

        with pytest.raises(ValueError, match="does not support 'add' operation"):
            self.handler.add_values(issue, [42])

    def test_remove_values_not_supported(self):
        """Test that remove operation is not supported."""
        issue = IssueFactory(iid=10)

        with pytest.raises(ValueError, match="does not support 'remove' operation"):
            self.handler.remove_values(issue, [42])

    def test_format_value(self):
        """Test formatting parent IID for display."""
        assert self.handler.format_value(42) == "#42"
        assert self.handler.format_value(1) == "#1"
        assert self.handler.format_value(999) == "#999"

    def test_validate_values_valid(self):
        """Test validation with valid parent IID."""
        # Should not raise
        self.handler.validate_values([42])
        self.handler.validate_values([1])
        self.handler.validate_values([999])

    def test_validate_values_not_integer(self):
        """Test validation fails for non-integer values."""
        with pytest.raises(ValueError, match="must be an integer"):
            self.handler.validate_values(["not an int"])

        with pytest.raises(ValueError, match="must be an integer"):
            self.handler.validate_values([42.5])

    def test_validate_values_multiple_values(self):
        """Test validation fails for multiple values."""
        with pytest.raises(ValueError, match="requires exactly one parent IID"):
            self.handler.validate_values([42, 99])

    def test_validate_values_empty_list(self):
        """Test validation fails for empty list."""
        with pytest.raises(ValueError, match="requires exactly one parent IID"):
            self.handler.validate_values([])

    def test_validate_values_non_positive(self):
        """Test validation fails for non-positive IIDs."""
        with pytest.raises(ValueError, match="must be a positive integer"):
            self.handler.validate_values([0])

        with pytest.raises(ValueError, match="must be a positive integer"):
            self.handler.validate_values([-1])
