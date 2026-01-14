"""Tests for Plotly treemap renderer."""

from __future__ import annotations

from sphinx_needs_tree_map.utils.plotly_renderer import PlotlyTreemapRenderer


class TestPlotlyTreemapRenderer:
    """Tests for PlotlyTreemapRenderer."""

    def test_render_returns_html(self, simple_tree):
        """Test that render returns valid HTML string."""
        renderer = PlotlyTreemapRenderer(
            tree=simple_tree,
            treemap_id="test-treemap",
        )
        html = renderer.render()

        assert isinstance(html, str)
        assert "test-treemap" in html
        assert "<div" in html
        assert "<script>" in html

    def test_render_includes_plotly_cdn(self, simple_tree):
        """Test that render includes Plotly CDN."""
        cdn_url = "https://example.com/plotly.js"
        renderer = PlotlyTreemapRenderer(
            tree=simple_tree,
            treemap_id="test",
            plotly_cdn=cdn_url,
        )
        html = renderer.render()

        assert cdn_url in html

    def test_render_includes_title(self, simple_tree):
        """Test that title is included when specified."""
        renderer = PlotlyTreemapRenderer(
            tree=simple_tree,
            treemap_id="test",
            title="Test Treemap",
        )
        html = renderer.render()

        assert "Test Treemap" in html

    def test_build_plotly_data_structure(self, simple_tree):
        """Test that Plotly data has correct structure."""
        renderer = PlotlyTreemapRenderer(
            tree=simple_tree,
            treemap_id="test",
        )
        data = renderer._build_plotly_data()

        assert data["type"] == "treemap"
        assert "ids" in data
        assert "labels" in data
        assert "parents" in data
        assert "values" in data
        assert len(data["ids"]) == 3  # root + 2 children

    def test_show_values_in_labels(self, simple_tree):
        """Test that values appear in labels when show_values=True."""
        renderer = PlotlyTreemapRenderer(
            tree=simple_tree,
            treemap_id="test",
            show_values=True,
        )
        data = renderer._build_plotly_data()

        # Labels should contain values in parentheses
        assert any("(5)" in label or "(8)" in label for label in data["labels"])
        assert any("(3)" in label for label in data["labels"])

    def test_hide_values_in_labels(self, simple_tree):
        """Test that values are hidden when show_values=False."""
        renderer = PlotlyTreemapRenderer(
            tree=simple_tree,
            treemap_id="test",
            show_values=False,
        )
        data = renderer._build_plotly_data()

        # Labels should not contain parentheses with numbers
        assert not any("(" in label for label in data["labels"])

    def test_color_by_type(self, simple_tree):
        """Test coloring by need type."""
        color_map = {"req": "#FF0000", "spec": "#00FF00", "default": "#CCCCCC"}
        renderer = PlotlyTreemapRenderer(
            tree=simple_tree,
            treemap_id="test",
            color_by="type",
            color_map=color_map,
        )
        data = renderer._build_plotly_data()

        colors = data["marker"]["colors"]
        assert "#FF0000" in colors  # req color
        assert "#00FF00" in colors  # spec color

    def test_parents_array_correct(self, simple_tree):
        """Test that parents array correctly reflects tree structure."""
        renderer = PlotlyTreemapRenderer(
            tree=simple_tree,
            treemap_id="test",
        )
        data = renderer._build_plotly_data()

        # Root has empty parent
        root_idx = data["ids"].index("root")
        assert data["parents"][root_idx] == ""

        # Children have root as parent
        child1_idx = data["ids"].index("child1")
        assert data["parents"][child1_idx] == "root"

    def test_build_layout(self, simple_tree):
        """Test layout configuration."""
        renderer = PlotlyTreemapRenderer(
            tree=simple_tree,
            treemap_id="test",
            title="My Title",
        )
        layout = renderer._build_layout()

        assert "margin" in layout
        assert layout["title"]["text"] == "My Title"

    def test_build_config(self, simple_tree):
        """Test config object."""
        renderer = PlotlyTreemapRenderer(
            tree=simple_tree,
            treemap_id="test",
            interactive=True,
        )
        config = renderer._build_config()

        assert config["responsive"] is True
        assert config["displayModeBar"] is True
        assert config["displaylogo"] is False
