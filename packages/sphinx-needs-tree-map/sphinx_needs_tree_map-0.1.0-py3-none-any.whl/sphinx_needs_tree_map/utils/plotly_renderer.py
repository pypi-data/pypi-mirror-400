"""Plotly.js treemap rendering utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from jinja2 import Environment, FileSystemLoader

if TYPE_CHECKING:
    from sphinx_needs_tree_map.utils.hierarchy import TreeNode


# Template directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


class PlotlyTreemapRenderer:
    """Renders a TreeNode hierarchy as a Plotly.js treemap.

    Generates HTML/JavaScript code that creates an interactive treemap
    visualization using Plotly.js.

    Args:
        tree: Root TreeNode of the hierarchy to render.
        treemap_id: Unique HTML ID for this treemap instance.
        color_by: How to determine node colors (type | status).
        color_map: Dictionary mapping values to colors.
        show_values: Whether to show values in labels.
        interactive: Whether to enable interactive features.
        height: CSS height value (e.g., '600px').
        width: CSS width value (e.g., '100%').
        title: Optional title for the treemap.
        plotly_cdn: CDN URL for Plotly.js.
    """

    def __init__(
        self,
        tree: TreeNode,
        treemap_id: str,
        color_by: str = "type",
        color_map: dict[str, str] | None = None,
        show_values: bool = True,
        interactive: bool = True,
        height: str = "600px",
        width: str = "100%",
        title: str = "",
        plotly_cdn: str = "https://cdn.plot.ly/plotly-2.35.2.min.js",
    ) -> None:
        self.tree = tree
        self.treemap_id = treemap_id
        self.color_by = color_by
        self.color_map = color_map or {}
        self.show_values = show_values
        self.interactive = interactive
        self.height = height
        self.width = width
        self.title = title
        self.plotly_cdn = plotly_cdn

        # Jinja2 environment
        self._env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=True,
        )

    def render(self) -> str:
        """Render the treemap to HTML.

        Returns:
            HTML string containing the treemap visualization.
        """
        # Flatten tree to Plotly data format
        plotly_data = self._build_plotly_data()

        # Render template
        template = self._env.get_template("treemap.html.jinja2")
        return template.render(
            treemap_id=self.treemap_id,
            plotly_data=json.dumps(plotly_data),
            plotly_layout=json.dumps(self._build_layout()),
            plotly_config=json.dumps(self._build_config()),
            plotly_cdn=self.plotly_cdn,
            height=self.height,
            width=self.width,
            title=self.title,
        )

    def _build_plotly_data(self) -> dict[str, Any]:
        """Build Plotly treemap data structure from tree.

        Plotly treemaps require parallel arrays:
        - ids: Unique identifier for each node
        - labels: Display text for each node
        - parents: Parent ID for each node (empty for root)
        - values: Numeric value for sizing
        - marker.colors: Color for each node

        Returns:
            Dictionary with Plotly treemap data.
        """
        ids: list[str] = []
        labels: list[str] = []
        parents: list[str] = []
        values: list[int] = []
        colors: list[str] = []
        custom_data: list[dict[str, Any]] = []

        # Traverse tree and build arrays
        for node in self.tree.iter_all():
            ids.append(node.id)

            # Build label with optional value
            if self.show_values and node.value > 0:
                label = f"{node.label} ({node.value})"
            else:
                label = node.label
            labels.append(label)

            parents.append(node.parent_id)
            values.append(node.value)
            colors.append(self._get_node_color(node))
            custom_data.append(
                {
                    "node_type": node.node_type,
                    "need_type": node.need_type,
                    "status": node.status,
                    "metadata": node.metadata,
                }
            )

        return {
            "type": "treemap",
            "ids": ids,
            "labels": labels,
            "parents": parents,
            "values": values,
            "branchvalues": "total",
            "textinfo": "label",
            "hovertemplate": "<b>%{label}</b><extra></extra>",
            "marker": {
                "colors": colors,
                "line": {"width": 1, "color": "white"},
            },
            "pathbar": {"visible": True},
            "customdata": custom_data,
        }

    def _build_layout(self) -> dict[str, Any]:
        """Build Plotly layout configuration.

        Returns:
            Dictionary with Plotly layout settings.
        """
        layout: dict[str, Any] = {
            "margin": {"t": 30, "l": 10, "r": 10, "b": 10},
            "paper_bgcolor": "rgba(0,0,0,0)",
        }

        if self.title:
            layout["title"] = {
                "text": self.title,
                "font": {"size": 16},
            }

        return layout

    def _build_config(self) -> dict[str, Any]:
        """Build Plotly config object.

        Returns:
            Dictionary with Plotly config settings.
        """
        return {
            "responsive": True,
            "displayModeBar": self.interactive,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        }

    def _get_node_color(self, node: TreeNode) -> str:
        """Determine the color for a node.

        Args:
            node: The TreeNode to get color for.

        Returns:
            CSS color string.
        """
        # Root and structural nodes get neutral colors
        if node.node_type in ("root", "document", "section"):
            return self._get_structural_color(node.node_type)

        # Color by type or status
        if self.color_by == "status" and node.status:
            return self.color_map.get(
                node.status,
                self.color_map.get("default", "#ECEFF1"),
            )
        elif node.need_type:
            return self.color_map.get(
                node.need_type,
                self.color_map.get("default", "#ECEFF1"),
            )

        return self.color_map.get("default", "#ECEFF1")

    def _get_structural_color(self, node_type: str) -> str:
        """Get color for structural nodes (root, document, section).

        Args:
            node_type: Type of structural node.

        Returns:
            CSS color string.
        """
        structural_colors = {
            "root": "#FAFAFA",
            "document": "#F5F5F5",
            "section": "#EEEEEE",
            "type_group": "#E0E0E0",
            "status_group": "#E8E8E8",
        }
        return structural_colors.get(node_type, "#ECEFF1")
