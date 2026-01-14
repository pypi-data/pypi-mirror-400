"""Filter utilities for sphinx-needs data."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def filter_needs(
    needs: dict[str, Any] | Any,
    _app: Sphinx,
    filter_string: str | None = None,
    types: list[str] | None = None,
    status: list[str] | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Filter needs based on various criteria.

    Args:
        needs: All needs (dict or NeedsView).
        _app: Sphinx application instance (unused, kept for API compatibility).
        filter_string: sphinx-needs filter expression.
        types: List of need types to include.
        status: List of statuses to include.
        tags: List of tags to include (any match).

    Returns:
        Filtered needs as a dictionary.
    """
    # Convert to dict if needed
    if hasattr(needs, "items"):
        needs_dict = dict(needs)
    else:
        needs_dict = {}
        for n in needs:
            if isinstance(n, dict) or hasattr(n, "get"):
                needs_dict[n.get("id", "")] = n
            else:
                needs_dict[str(n)] = n

    result: dict[str, Any] = {}

    for need_id, need in needs_dict.items():
        # Convert need to dict if it's not already
        if not isinstance(need, dict):
            need = dict(need) if hasattr(need, "__iter__") else {}

        # Apply type filter
        if types is not None:
            need_type = need.get("type", "")
            if need_type not in types:
                continue

        # Apply status filter
        if status is not None:
            need_status = need.get("status", "")
            if need_status not in status:
                continue

        # Apply tags filter (any match)
        if tags is not None:
            need_tags = need.get("tags", [])
            if not any(tag in need_tags for tag in tags):
                continue

        # Apply filter string using sphinx-needs filter
        if filter_string is not None and not _eval_filter(need, filter_string, needs_dict):
            continue

        result[need_id] = need

    return result


def _eval_filter(
    need: dict[str, Any],
    filter_string: str,
    _all_needs: dict[str, Any],
) -> bool:
    """Evaluate a sphinx-needs filter expression.

    Args:
        need: The need to evaluate.
        filter_string: The filter expression.
        _all_needs: All needs for context (unused, kept for future use).

    Returns:
        True if the need matches the filter.
    """
    try:
        # Create a context with need attributes
        context = {
            "id": need.get("id", ""),
            "title": need.get("title", ""),
            "type": need.get("type", ""),
            "status": need.get("status", ""),
            "tags": need.get("tags", []),
            "links": need.get("links", []),
            "links_back": need.get("links_back", []),
            "docname": need.get("docname", ""),
            "sections": need.get("sections", []),
            "content": need.get("content", ""),
            "is_need": need.get("is_need", True),
            "is_part": need.get("is_part", False),
            # Add all attributes from the need
            **{k: v for k, v in need.items() if k not in ("id", "title", "type")},
        }

        # Add helper functions
        context["search"] = lambda pattern, field: _search_in_field(need, pattern, field)

        # Safely evaluate the filter expression
        return bool(eval(filter_string, {"__builtins__": {}}, context))

    except Exception:
        # If filter evaluation fails, include the need
        return True


def _search_in_field(need: dict[str, Any], pattern: str, field: str) -> bool:
    """Search for a pattern in a need field.

    Args:
        need: The need dictionary.
        pattern: Pattern to search for.
        field: Field name to search in.

    Returns:
        True if pattern found in field.
    """
    import re

    value = need.get(field, "")
    value = " ".join(str(v) for v in value) if isinstance(value, list) else str(value)

    try:
        return bool(re.search(pattern, value, re.IGNORECASE))
    except re.error:
        return pattern.lower() in value.lower()
