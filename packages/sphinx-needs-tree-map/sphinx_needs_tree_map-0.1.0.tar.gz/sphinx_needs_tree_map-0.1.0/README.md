# sphinx-needs-tree-map

StrictDoc-style tree map visualizations for sphinx-needs documentation.

## Overview

`sphinx-needs-tree-map` is a Sphinx extension that provides interactive treemap visualizations for your sphinx-needs documentation. It allows you to visualize requirements, specifications, and other need types in a hierarchical treemap using Plotly.js.

## Installation

```bash
pip install sphinx-needs-tree-map
```

Or with uv:

```bash
uv add sphinx-needs-tree-map
```

## Quick Start

Add the extension to your `conf.py`:

```python
extensions = [
    "sphinx_needs",
    "sphinx_needs_tree_map",
]
```

Then use the `needtreemap` directive in your documentation:

```rst
.. needtreemap::
   :hierarchy: document
   :depth: 3
   :show_values:
```

## Directive Options

The `needtreemap` directive supports the following options:

### Filtering

- `:filter:` - sphinx-needs filter expression (e.g., `type == 'req'`)
- `:types:` - Comma-separated list of need types to include
- `:status:` - Comma-separated list of statuses to include
- `:tags:` - Comma-separated list of tags to include

### Hierarchy

- `:hierarchy:` - Hierarchy mode: `document` (default), `links`, or `type`
- `:root:` - Root node: `document`, `section`, or a specific need ID
- `:depth:` - Maximum hierarchy depth (default: 3)

### Visualization

- `:size_by:` - Size metric: `count` (default), `links`, or `content_length`
- `:color_by:` - Color scheme: `type` (default) or `status`
- `:show_values:` - Show counts in labels
- `:interactive:` - Enable interactive features (default: enabled)

### Layout

- `:height:` - CSS height (default: `600px`)
- `:width:` - CSS width (default: `100%`)
- `:title:` - Optional title for the treemap

## Configuration

Add these to your `conf.py` to customize the extension:

```python
# Plotly.js CDN URL
needtreemap_plotly_cdn = "https://cdn.plot.ly/plotly-2.35.2.min.js"

# Default dimensions
needtreemap_default_height = "600px"
needtreemap_default_width = "100%"

# Colors for need types
needtreemap_colors = {
    "req": "#E3F2FD",
    "spec": "#FFF3E0",
    "impl": "#E8F5E9",
    "test": "#FCE4EC",
    "default": "#ECEFF1",
}

# Colors for statuses
needtreemap_status_colors = {
    "open": "#FFCDD2",
    "in progress": "#FFF9C4",
    "implemented": "#C8E6C9",
    "verified": "#B2DFDB",
    "default": "#ECEFF1",
}
```

## Examples

### Document-based hierarchy

```rst
.. needtreemap::
   :hierarchy: document
   :depth: 3
   :show_values:
```

### Filter by type

```rst
.. needtreemap::
   :filter: type == 'req' or type == 'spec'
   :color_by: type
```

### Status-based coloring

```rst
.. needtreemap::
   :types: req,spec
   :color_by: status
   :show_values:
```

### Link-based hierarchy

```rst
.. needtreemap::
   :hierarchy: links
   :depth: 4
   :title: Requirements Traceability
```

## Example Project

See the [example/](example/) directory for a complete example Sphinx project demonstrating all features of the extension. The example project is a fictional "Task Management System" with:

- 45+ needs (requirements, specifications, test cases, user stories)
- Multiple documents organized hierarchically
- Traceability links between needs
- Examples of all three hierarchy modes
- Various filtering and visualization options

To build the example:

```bash
cd example
uv sync
make html
# Open _build/html/index.html
```

## Requirements

- Python >= 3.9
- Sphinx >= 5.0
- sphinx-needs >= 2.0

## License

MIT License
