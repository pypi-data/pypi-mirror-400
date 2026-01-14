"""Sphinx configuration for test-basic."""

extensions = [
    "sphinx_needs",
    "sphinx_needs_tree_map",
]

# Sphinx-needs configuration
needs_types = [
    {
        "directive": "req",
        "title": "Requirement",
        "prefix": "REQ-",
        "color": "#BFD8D2",
        "style": "node",
    },
    {
        "directive": "spec",
        "title": "Specification",
        "prefix": "SPEC-",
        "color": "#DCB8CB",
        "style": "node",
    },
]

needs_id_regex = r"^[A-Z]+-[0-9]+"

# sphinx-needs-tree-map configuration
needtreemap_colors = {
    "req": "#E3F2FD",
    "spec": "#FFF3E0",
    "default": "#ECEFF1",
}
