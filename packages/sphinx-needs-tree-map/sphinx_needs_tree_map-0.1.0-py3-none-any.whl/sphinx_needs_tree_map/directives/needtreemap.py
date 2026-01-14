"""NeedTreeMap directive implementation."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

if TYPE_CHECKING:
    from docutils.nodes import Node
    from sphinx.application import Sphinx


class NeedTreeMapNode(nodes.General, nodes.Element):
    """Custom docutils node for needtreemap directive.

    This node stores the directive options and is processed later
    in the doctree-resolved event when all needs data is available.
    """

    pass


class NeedTreeMapDirective(SphinxDirective):
    """Directive to create an interactive treemap visualization of needs.

    Usage::

        .. needtreemap::
           :filter: type == 'req' or type == 'spec'
           :root: document
           :depth: 3
           :size_by: count
           :color_by: type
           :show_values:
           :interactive:
           :height: 600px
           :width: 100%
    """

    has_content: ClassVar[bool] = False
    required_arguments: ClassVar[int] = 0
    optional_arguments: ClassVar[int] = 0
    final_argument_whitespace: ClassVar[bool] = True

    option_spec: ClassVar[dict[str, Any]] = {
        # Filtering
        "filter": directives.unchanged,
        "types": directives.unchanged,  # Comma-separated list
        "status": directives.unchanged,  # Comma-separated list
        "tags": directives.unchanged,  # Comma-separated list
        # Hierarchy options
        "root": directives.unchanged,  # document | section | <need_id>
        "hierarchy": directives.unchanged,  # document | links | type
        "depth": directives.positive_int,
        # Visualization options
        "size_by": directives.unchanged,  # count | links | content_length
        "color_by": directives.unchanged,  # type | status | coverage
        "show_values": directives.flag,
        "interactive": directives.flag,
        # Layout options
        "height": directives.unchanged,
        "width": directives.unchanged,
        "title": directives.unchanged,
    }

    def run(self) -> list[Node]:
        """Execute the directive and return a placeholder node.

        The actual treemap generation happens in the doctree-resolved event
        when all needs have been collected.

        Returns:
            List containing a single NeedTreeMapNode.
        """
        # Generate unique ID for this treemap instance
        treemap_id = f"needtreemap-{uuid.uuid4().hex[:8]}"

        # Create the placeholder node with all options
        node = NeedTreeMapNode()
        node["treemap_id"] = treemap_id
        node["docname"] = self.env.docname
        node["lineno"] = self.lineno

        # Store all directive options
        node["options"] = {
            "filter": self.options.get("filter"),
            "types": self._parse_list_option("types"),
            "status": self._parse_list_option("status"),
            "tags": self._parse_list_option("tags"),
            "root": self.options.get("root", "document"),
            "hierarchy": self.options.get("hierarchy", "document"),
            "depth": self.options.get("depth", 3),
            "size_by": self.options.get("size_by", "count"),
            "color_by": self.options.get("color_by", "type"),
            "show_values": "show_values" in self.options,
            "interactive": "interactive" not in self.options
            or self.options.get("interactive") is None,
            "height": self.options.get("height", self.config.needtreemap_default_height),
            "width": self.options.get("width", self.config.needtreemap_default_width),
            "title": self.options.get("title", ""),
        }

        return [node]

    def _parse_list_option(self, option_name: str) -> list[str] | None:
        """Parse a comma-separated option into a list.

        Args:
            option_name: Name of the option to parse.

        Returns:
            List of stripped strings, or None if option not present.
        """
        value = self.options.get(option_name)
        if value is None:
            return None
        return [item.strip() for item in value.split(",") if item.strip()]


def process_needtreemap_nodes(
    app: Sphinx,
    doctree: nodes.document,
    _docname: str,
) -> None:
    """Process all NeedTreeMapNode instances in the doctree.

    This event handler is called during the doctree-resolved phase,
    when all needs have been collected and are available for processing.

    Args:
        app: The Sphinx application instance.
        doctree: The document tree being processed.
        _docname: Name of the document being processed (unused).
    """
    from sphinx_needs.data import SphinxNeedsData

    from sphinx_needs_tree_map.utils.filters import filter_needs
    from sphinx_needs_tree_map.utils.hierarchy import HierarchyBuilder
    from sphinx_needs_tree_map.utils.plotly_renderer import PlotlyTreemapRenderer

    # Skip if not HTML builder
    if app.builder.format != "html":
        for node in doctree.findall(NeedTreeMapNode):
            node.replace_self([])
        return

    # Get all needs data
    needs_data = SphinxNeedsData(app.env)
    all_needs = needs_data.get_needs_view()

    # Process each needtreemap node
    for node in doctree.findall(NeedTreeMapNode):
        options = node["options"]
        treemap_id = node["treemap_id"]

        try:
            # Step 1: Filter needs based on directive options
            filtered_needs = filter_needs(
                needs=all_needs,
                _app=app,
                filter_string=options["filter"],
                types=options["types"],
                status=options["status"],
                tags=options["tags"],
            )

            # Step 2: Build hierarchy tree
            builder = HierarchyBuilder(
                needs=filtered_needs,
                hierarchy_mode=options["hierarchy"],
                root=options["root"],
                max_depth=options["depth"],
                size_by=options["size_by"],
            )
            tree = builder.build()

            # Step 3: Render to Plotly HTML
            renderer = PlotlyTreemapRenderer(
                tree=tree,
                treemap_id=treemap_id,
                color_by=options["color_by"],
                color_map=_get_color_map(app.config, options["color_by"]),
                show_values=options["show_values"],
                interactive=options["interactive"],
                height=options["height"],
                width=options["width"],
                title=options["title"],
                plotly_cdn=app.config.needtreemap_plotly_cdn,
            )
            html_content = renderer.render()

            # Store HTML in node for visitor
            node["html_content"] = html_content

        except Exception as e:
            # Log error and replace with error message
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to generate treemap: {e}")
            error_node = nodes.error()
            error_node += nodes.paragraph(text=f"Error generating treemap: {e}")
            node.replace_self([error_node])


def _get_color_map(config: Any, color_by: str) -> dict[str, str]:
    """Get the appropriate color map based on color_by option.

    Args:
        config: Sphinx config object.
        color_by: The color_by option value.

    Returns:
        Dictionary mapping values to colors.
    """
    if color_by == "status":
        result: dict[str, str] = config.needtreemap_status_colors
        return result
    result = config.needtreemap_colors
    return result
