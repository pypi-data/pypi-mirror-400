"""Tests for filter utilities."""

from __future__ import annotations

from unittest.mock import MagicMock

from sphinx_needs_tree_map.utils.filters import filter_needs


class TestFilterNeeds:
    """Tests for filter_needs function."""

    def test_filter_by_type(self, sample_needs):
        """Test filtering by need type."""
        app = MagicMock()
        result = filter_needs(
            sample_needs,
            app,
            types=["req"],
        )

        assert len(result) == 2
        assert all(n["type"] == "req" for n in result.values())

    def test_filter_by_status(self, sample_needs):
        """Test filtering by status."""
        app = MagicMock()
        result = filter_needs(
            sample_needs,
            app,
            status=["open"],
        )

        assert len(result) == 3
        assert all(n["status"] == "open" for n in result.values())

    def test_filter_by_multiple_types(self, sample_needs):
        """Test filtering by multiple types."""
        app = MagicMock()
        result = filter_needs(
            sample_needs,
            app,
            types=["req", "spec"],
        )

        assert len(result) == 5  # All needs

    def test_filter_by_filter_string(self, sample_needs):
        """Test filtering by filter expression."""
        app = MagicMock()
        result = filter_needs(
            sample_needs,
            app,
            filter_string="type == 'req'",
        )

        assert len(result) == 2
        assert all(n["type"] == "req" for n in result.values())

    def test_filter_by_complex_filter_string(self, sample_needs):
        """Test filtering by complex filter expression."""
        app = MagicMock()
        result = filter_needs(
            sample_needs,
            app,
            filter_string="type == 'spec' and status == 'open'",
        )

        assert len(result) == 2
        assert all(n["type"] == "spec" and n["status"] == "open" for n in result.values())

    def test_filter_no_criteria_returns_all(self, sample_needs):
        """Test that no filter criteria returns all needs."""
        app = MagicMock()
        result = filter_needs(
            sample_needs,
            app,
        )

        assert len(result) == len(sample_needs)

    def test_filter_combined_criteria(self, sample_needs):
        """Test filtering with combined type and status."""
        app = MagicMock()
        result = filter_needs(
            sample_needs,
            app,
            types=["req"],
            status=["implemented"],
        )

        assert len(result) == 1
        assert "REQ-002" in result

    def test_filter_empty_result(self, sample_needs):
        """Test filtering that returns no results."""
        app = MagicMock()
        result = filter_needs(
            sample_needs,
            app,
            types=["nonexistent"],
        )

        assert len(result) == 0

    def test_filter_handles_dict_needs(self, sample_needs):
        """Test that filter handles dict-based needs."""
        app = MagicMock()
        result = filter_needs(
            sample_needs,  # Already a dict
            app,
            types=["req"],
        )

        assert isinstance(result, dict)
        assert len(result) == 2
