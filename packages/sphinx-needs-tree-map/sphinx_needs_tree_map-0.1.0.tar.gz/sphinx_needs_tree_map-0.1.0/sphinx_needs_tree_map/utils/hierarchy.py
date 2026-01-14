"""Hierarchy building utilities for treemap generation."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class TreeNode:
    """A node in the treemap hierarchy tree.

    Attributes:
        id: Unique identifier for this node.
        label: Display label for the node.
        parent_id: ID of parent node (empty string for root).
        value: Numeric value for sizing (e.g., count of needs).
        node_type: Type of node (root, document, section, need).
        need_type: For need nodes, the sphinx-needs type (req, spec, etc.).
        status: For need nodes, the status value.
        metadata: Additional metadata for the node.
        children: List of child nodes.
    """

    id: str
    label: str
    parent_id: str = ""
    value: int = 1
    node_type: str = "node"  # root | document | section | need
    need_type: str | None = None
    status: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    children: list[TreeNode] = field(default_factory=list)

    def add_child(self, child: TreeNode) -> None:
        """Add a child node and set its parent."""
        child.parent_id = self.id
        self.children.append(child)

    def iter_all(self) -> Iterator[TreeNode]:
        """Iterate over this node and all descendants."""
        yield self
        for child in self.children:
            yield from child.iter_all()

    def compute_values(self) -> int:
        """Recursively compute values from leaf nodes up.

        For branch nodes, value = sum of children values.
        For leaf nodes, value remains as set.

        Returns:
            The computed value for this node.
        """
        if self.children:
            self.value = sum(child.compute_values() for child in self.children)
        return self.value


HierarchyMode = Literal["document", "links", "type"]
SizeByMode = Literal["count", "links", "content_length"]


class HierarchyBuilder:
    """Builds a tree hierarchy from sphinx-needs data.

    Supports multiple hierarchy strategies:
    - document: Group by document name, then sections
    - links: Build tree from parent-child link relationships
    - type: Group by need type, then by status

    Args:
        needs: The filtered needs to build hierarchy from.
        hierarchy_mode: The hierarchy strategy to use.
        root: Root node identifier (document | section | need_id).
        max_depth: Maximum hierarchy depth.
        size_by: How to calculate node sizes.
    """

    def __init__(
        self,
        needs: dict[str, Any] | Any,
        hierarchy_mode: str = "document",
        root: str = "document",
        max_depth: int = 3,
        size_by: str = "count",
    ) -> None:
        self.needs = needs
        self.hierarchy_mode = hierarchy_mode
        self.root = root
        self.max_depth = max_depth
        self.size_by = size_by

    def build(self) -> TreeNode:
        """Build the hierarchy tree.

        Returns:
            Root TreeNode of the hierarchy.
        """
        if self.hierarchy_mode == "document":
            return self._build_document_hierarchy()
        elif self.hierarchy_mode == "links":
            return self._build_links_hierarchy()
        elif self.hierarchy_mode == "type":
            return self._build_type_hierarchy()
        else:
            raise ValueError(f"Unknown hierarchy mode: {self.hierarchy_mode}")

    def _build_document_hierarchy(self) -> TreeNode:
        """Build hierarchy based on document structure.

        Structure:
            Root
            +-- Document 1
            |   +-- Section A
            |   |   +-- Need 1
            |   |   +-- Need 2
            |   +-- Section B
            |       +-- Need 3
            +-- Document 2
                +-- ...

        Returns:
            Root TreeNode with document/section hierarchy.
        """
        # Create root node
        root = TreeNode(
            id="__root__",
            label="Documentation",
            node_type="root",
        )

        # Group needs by document
        docs: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for _need_id, need in self._iter_needs():
            need_dict = self._need_to_dict(need)
            docname = need_dict.get("docname", "unknown")
            docs[docname].append(need_dict)

        # Build document nodes
        for docname in sorted(docs.keys()):
            doc_needs = docs[docname]
            doc_node = TreeNode(
                id=f"doc:{docname}",
                label=self._format_doc_label(docname),
                node_type="document",
            )

            if self.max_depth > 1:
                # Group by sections within document
                section_nodes = self._build_section_hierarchy(doc_needs, depth=2)
                for section_node in section_nodes:
                    doc_node.add_child(section_node)
            else:
                # Add needs directly to document
                for need in doc_needs:
                    need_node = self._create_need_node(need)
                    doc_node.add_child(need_node)

            root.add_child(doc_node)

        # Compute values bottom-up
        root.compute_values()

        return root

    def _build_section_hierarchy(
        self,
        needs: list[dict[str, Any]],
        depth: int,
    ) -> list[TreeNode]:
        """Build section hierarchy for needs within a document.

        Args:
            needs: List of needs in this document.
            depth: Current depth level.

        Returns:
            List of section TreeNodes.
        """
        # Group needs by their first section
        sections: dict[str, list[dict[str, Any]]] = defaultdict(list)
        no_section: list[dict[str, Any]] = []

        for need in needs:
            need_sections = need.get("sections", [])
            if need_sections:
                # Use the first section as the grouping key
                first_section = need_sections[0] if need_sections else ""
                sections[first_section].append(need)
            else:
                no_section.append(need)

        result: list[TreeNode] = []

        # Create section nodes
        for section_name in sorted(sections.keys()):
            section_needs = sections[section_name]
            section_node = TreeNode(
                id=f"section:{section_name}:{id(section_needs)}",
                label=section_name or "(No Section)",
                node_type="section",
            )

            if depth < self.max_depth:
                # Recursively build deeper sections
                # Remove the first section from each need for next level
                deeper_needs = []
                for need in section_needs:
                    deeper_need = dict(need)
                    deeper_need["sections"] = need.get("sections", [])[1:]
                    deeper_needs.append(deeper_need)

                # Check if there are deeper sections
                has_deeper = any(n.get("sections") for n in deeper_needs)
                if has_deeper:
                    children = self._build_section_hierarchy(deeper_needs, depth + 1)
                    for child in children:
                        section_node.add_child(child)
                else:
                    # Add needs directly
                    for need in section_needs:
                        need_node = self._create_need_node(need)
                        section_node.add_child(need_node)
            else:
                # Max depth reached, add needs directly
                for need in section_needs:
                    need_node = self._create_need_node(need)
                    section_node.add_child(need_node)

            result.append(section_node)

        # Add needs without sections
        for need in no_section:
            need_node = self._create_need_node(need)
            result.append(need_node)

        return result

    def _build_links_hierarchy(self) -> TreeNode:
        """Build hierarchy based on link relationships.

        Uses the 'links' and 'links_back' attributes to build
        a parent-child tree. Needs without incoming links are
        considered root-level items.

        Returns:
            Root TreeNode with link-based hierarchy.
        """
        root = TreeNode(
            id="__root__",
            label="Requirements",
            node_type="root",
        )

        # Build index of all needs
        needs_dict: dict[str, dict[str, Any]] = {}
        for need_id, need in self._iter_needs():
            needs_dict[need_id] = self._need_to_dict(need)

        # Find root needs (no incoming links from within our set)
        root_need_ids: set[str] = set()
        for need_id, need in needs_dict.items():
            links_back = need.get("links_back", [])
            # Check if any incoming link is from within our filtered set
            has_parent_in_set = any(link_id in needs_dict for link_id in links_back)
            if not has_parent_in_set:
                root_need_ids.add(need_id)

        # Build tree recursively from root needs
        visited: set[str] = set()

        def build_subtree(need_id: str, depth: int) -> TreeNode | None:
            if need_id in visited or depth > self.max_depth:
                return None
            if need_id not in needs_dict:
                return None

            visited.add(need_id)
            need = needs_dict[need_id]
            node = self._create_need_node(need)

            # Add children (needs that link back to this one)
            for child_id, child_need in needs_dict.items():
                if need_id in child_need.get("links_back", []):
                    child_node = build_subtree(child_id, depth + 1)
                    if child_node:
                        node.add_child(child_node)

            return node

        # Build from root needs
        for root_id in sorted(root_need_ids):
            subtree = build_subtree(root_id, 1)
            if subtree:
                root.add_child(subtree)

        root.compute_values()
        return root

    def _build_type_hierarchy(self) -> TreeNode:
        """Build hierarchy based on need types and status.

        Structure:
            Root
            +-- Requirements
            |   +-- Open
            |   |   +-- Need 1
            |   +-- Implemented
            |       +-- Need 2
            +-- Specifications
                +-- ...

        Returns:
            Root TreeNode with type/status hierarchy.
        """
        root = TreeNode(
            id="__root__",
            label="All Needs",
            node_type="root",
        )

        # Group by type, then by status
        by_type: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))

        for _need_id, need in self._iter_needs():
            need_dict = self._need_to_dict(need)
            need_type = need_dict.get("type", "unknown")
            status = need_dict.get("status", "none") or "none"
            by_type[need_type][status].append(need_dict)

        # Build type nodes
        for type_name in sorted(by_type.keys()):
            type_data = by_type[type_name]
            type_node = TreeNode(
                id=f"type:{type_name}",
                label=type_name.title(),
                node_type="type_group",
                need_type=type_name,
            )

            if self.max_depth > 1:
                # Add status sub-groups
                for status in sorted(type_data.keys()):
                    status_needs = type_data[status]
                    status_node = TreeNode(
                        id=f"status:{type_name}:{status}",
                        label=status.title() if status else "(No Status)",
                        node_type="status_group",
                        status=status,
                    )

                    if self.max_depth > 2:
                        for need in status_needs:
                            need_node = self._create_need_node(need)
                            status_node.add_child(need_node)
                    else:
                        status_node.value = len(status_needs)

                    type_node.add_child(status_node)
            else:
                # Just count all needs of this type
                type_node.value = sum(len(needs) for needs in type_data.values())

            root.add_child(type_node)

        root.compute_values()
        return root

    def _create_need_node(self, need: dict[str, Any]) -> TreeNode:
        """Create a TreeNode for a single need.

        Args:
            need: The need dictionary.

        Returns:
            TreeNode representing the need.
        """
        need_id = need.get("id", "unknown")
        title = need.get("title", need_id)

        # Calculate value based on size_by option
        value = self._calculate_value(need)

        return TreeNode(
            id=f"need:{need_id}",
            label=title,
            value=value,
            node_type="need",
            need_type=need.get("type"),
            status=need.get("status"),
            metadata={
                "need_id": need_id,
                "docname": need.get("docname"),
                "lineno": need.get("lineno"),
            },
        )

    def _calculate_value(self, need: dict[str, Any]) -> int:
        """Calculate the value for a need based on size_by option.

        Args:
            need: The need dictionary.

        Returns:
            Calculated value (minimum 1).
        """
        if self.size_by == "count":
            return 1
        elif self.size_by == "links":
            links = need.get("links", [])
            links_back = need.get("links_back", [])
            return max(1, len(links) + len(links_back))
        elif self.size_by == "content_length":
            content = need.get("content", "")
            return max(1, len(content) // 100)  # Per 100 chars
        else:
            return 1

    def _iter_needs(self) -> Iterator[tuple[str, Any]]:
        """Iterate over needs, handling both dict and NeedsView."""
        if hasattr(self.needs, "items"):
            yield from self.needs.items()
        else:
            for need in self.needs:
                if isinstance(need, dict) or hasattr(need, "get"):
                    yield need.get("id", ""), need
                else:
                    yield str(need), need

    def _need_to_dict(self, need: Any) -> dict[str, Any]:
        """Convert a need object to a dictionary."""
        if isinstance(need, dict):
            return need
        # Handle NeedsView objects that may have attribute access
        return dict(need) if hasattr(need, "__iter__") else {"id": str(need)}

    def _format_doc_label(self, docname: str) -> str:
        """Format a document name for display.

        Args:
            docname: The sphinx docname (e.g., 'requirements/system').

        Returns:
            Formatted display label.
        """
        # Take the last part of the path and titleize
        parts = docname.split("/")
        label = parts[-1] if parts else docname
        return label.replace("_", " ").replace("-", " ").title()
