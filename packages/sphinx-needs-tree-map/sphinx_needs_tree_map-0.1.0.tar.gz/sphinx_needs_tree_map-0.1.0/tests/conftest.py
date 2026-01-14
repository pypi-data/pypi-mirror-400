"""Pytest fixtures for sphinx-needs-tree-map tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from sphinx_needs_tree_map.utils.hierarchy import TreeNode

# Path to test roots
ROOTS_DIR = Path(__file__).parent / "roots"


@pytest.fixture
def sample_needs() -> dict[str, dict[str, Any]]:
    """Sample needs data for unit tests."""
    return {
        "REQ-001": {
            "id": "REQ-001",
            "title": "System shall be fast",
            "type": "req",
            "status": "open",
            "docname": "requirements/system",
            "sections": ["System Requirements", "Performance"],
            "links": ["SPEC-001"],
            "links_back": [],
            "content": "The system shall respond within 100ms.",
            "is_need": True,
            "is_part": False,
        },
        "REQ-002": {
            "id": "REQ-002",
            "title": "System shall be secure",
            "type": "req",
            "status": "implemented",
            "docname": "requirements/system",
            "sections": ["System Requirements", "Security"],
            "links": ["SPEC-002", "SPEC-003"],
            "links_back": [],
            "content": "The system shall use encryption.",
            "is_need": True,
            "is_part": False,
        },
        "SPEC-001": {
            "id": "SPEC-001",
            "title": "Performance specification",
            "type": "spec",
            "status": "open",
            "docname": "specifications/performance",
            "sections": ["Specifications"],
            "links": [],
            "links_back": ["REQ-001"],
            "content": "Response time < 100ms.",
            "is_need": True,
            "is_part": False,
        },
        "SPEC-002": {
            "id": "SPEC-002",
            "title": "Encryption specification",
            "type": "spec",
            "status": "implemented",
            "docname": "specifications/security",
            "sections": ["Specifications", "Crypto"],
            "links": [],
            "links_back": ["REQ-002"],
            "content": "Use AES-256.",
            "is_need": True,
            "is_part": False,
        },
        "SPEC-003": {
            "id": "SPEC-003",
            "title": "Authentication specification",
            "type": "spec",
            "status": "open",
            "docname": "specifications/security",
            "sections": ["Specifications", "Auth"],
            "links": [],
            "links_back": ["REQ-002"],
            "content": "Use OAuth 2.0.",
            "is_need": True,
            "is_part": False,
        },
    }


@pytest.fixture
def tree_node_factory():
    """Factory for creating TreeNode instances."""

    def _factory(**kwargs) -> TreeNode:
        defaults = {
            "id": "test-node",
            "label": "Test Node",
            "value": 1,
        }
        defaults.update(kwargs)
        return TreeNode(**defaults)

    return _factory


@pytest.fixture
def simple_tree(tree_node_factory):
    """Create a simple tree for testing."""
    root = tree_node_factory(id="root", label="Root", node_type="root")
    child1 = tree_node_factory(
        id="child1", label="Child 1", value=5, node_type="need", need_type="req"
    )
    child2 = tree_node_factory(
        id="child2", label="Child 2", value=3, node_type="need", need_type="spec"
    )
    root.add_child(child1)
    root.add_child(child2)
    root.compute_values()
    return root
