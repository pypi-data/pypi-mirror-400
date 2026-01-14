"""
sphinx-needs-tree-map: StrictDoc-style tree map visualizations for sphinx-needs.

This extension provides the `needtreemap` directive to create interactive
Plotly.js treemap visualizations of sphinx-needs documentation.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import docutils.nodes

from sphinx_needs_tree_map.directives.needtreemap import (
    NeedTreeMapDirective,
    NeedTreeMapNode,
    process_needtreemap_nodes,
)

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.config import Config

__version__ = "0.1.0"
__all__ = ["__version__", "setup"]

# Path to static files
STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"


def builder_inited(app: Sphinx) -> None:
    """Called when builder is initialized.

    Adds static files directory to Sphinx's static paths.
    """
    # Add our static directory
    if hasattr(app.config, "html_static_path"):
        app.config.html_static_path.append(str(STATIC_DIR))


def config_inited(app: Sphinx, config: Config) -> None:
    """Called when config is initialized.

    Sets up default configuration values.
    """
    # Ensure sphinx-needs is loaded first
    if "sphinx_needs" not in config.extensions:
        app.setup_extension("sphinx_needs")


def setup(app: Sphinx) -> dict[str, Any]:
    """Set up the sphinx-needs-tree-map extension.

    Args:
        app: The Sphinx application instance.

    Returns:
        Extension metadata dictionary.
    """
    # Configuration values
    app.add_config_value(
        "needtreemap_plotly_cdn",
        "https://cdn.plot.ly/plotly-2.35.2.min.js",
        "html",
    )
    app.add_config_value(
        "needtreemap_default_height",
        "600px",
        "html",
    )
    app.add_config_value(
        "needtreemap_default_width",
        "100%",
        "html",
    )
    app.add_config_value(
        "needtreemap_colors",
        {
            "req": "#E3F2FD",
            "spec": "#FFF3E0",
            "impl": "#E8F5E9",
            "test": "#FCE4EC",
            "story": "#F3E5F5",
            "default": "#ECEFF1",
        },
        "html",
    )
    app.add_config_value(
        "needtreemap_status_colors",
        {
            "open": "#FFCDD2",
            "in progress": "#FFF9C4",
            "implemented": "#C8E6C9",
            "verified": "#B2DFDB",
            "default": "#ECEFF1",
        },
        "html",
    )

    # Register the directive
    app.add_directive("needtreemap", NeedTreeMapDirective)

    # Register the custom docutils node
    app.add_node(
        NeedTreeMapNode,
        html=(visit_needtreemap_node, depart_needtreemap_node),
        latex=(skip_needtreemap_node, None),
        text=(skip_needtreemap_node, None),
    )

    # Connect event handlers
    app.connect("config-inited", config_inited)
    app.connect("builder-inited", builder_inited)
    app.connect("doctree-resolved", process_needtreemap_nodes)

    # Add CSS file
    app.add_css_file("needtreemap.css")

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def visit_needtreemap_node(self: Any, node: NeedTreeMapNode) -> None:
    """HTML visitor for NeedTreeMapNode - renders the treemap HTML."""
    self.body.append(node.get("html_content", ""))


def depart_needtreemap_node(self: Any, node: NeedTreeMapNode) -> None:
    """HTML departure handler for NeedTreeMapNode."""
    pass


def skip_needtreemap_node(_self: Any, _node: NeedTreeMapNode) -> None:
    """Skip rendering for non-HTML builders."""
    raise docutils.nodes.SkipNode
