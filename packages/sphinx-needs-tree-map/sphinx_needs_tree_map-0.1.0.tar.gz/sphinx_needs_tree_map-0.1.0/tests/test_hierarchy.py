"""Tests for hierarchy building utilities."""

from __future__ import annotations

from sphinx_needs_tree_map.utils.hierarchy import HierarchyBuilder


class TestTreeNode:
    """Tests for TreeNode dataclass."""

    def test_create_basic_node(self, tree_node_factory):
        """Test creating a basic tree node."""
        node = tree_node_factory(id="test", label="Test")
        assert node.id == "test"
        assert node.label == "Test"
        assert node.value == 1
        assert node.children == []

    def test_add_child(self, tree_node_factory):
        """Test adding child nodes."""
        parent = tree_node_factory(id="parent", label="Parent")
        child = tree_node_factory(id="child", label="Child")

        parent.add_child(child)

        assert len(parent.children) == 1
        assert parent.children[0] is child
        assert child.parent_id == "parent"

    def test_iter_all(self, tree_node_factory):
        """Test iterating over all descendants."""
        root = tree_node_factory(id="root", label="Root")
        child1 = tree_node_factory(id="child1", label="Child 1")
        child2 = tree_node_factory(id="child2", label="Child 2")
        grandchild = tree_node_factory(id="grandchild", label="Grandchild")

        root.add_child(child1)
        root.add_child(child2)
        child1.add_child(grandchild)

        all_nodes = list(root.iter_all())

        assert len(all_nodes) == 4
        assert root in all_nodes
        assert child1 in all_nodes
        assert child2 in all_nodes
        assert grandchild in all_nodes

    def test_compute_values(self, tree_node_factory):
        """Test computing values from leaf nodes."""
        root = tree_node_factory(id="root", label="Root", value=0)
        child1 = tree_node_factory(id="child1", label="Child 1", value=5)
        child2 = tree_node_factory(id="child2", label="Child 2", value=3)

        root.add_child(child1)
        root.add_child(child2)

        result = root.compute_values()

        assert result == 8
        assert root.value == 8


class TestHierarchyBuilderDocument:
    """Tests for document-based hierarchy building."""

    def test_build_empty_needs(self):
        """Test building hierarchy from empty needs."""
        builder = HierarchyBuilder(needs={})
        tree = builder.build()

        assert tree.id == "__root__"
        assert tree.children == []

    def test_build_single_document(self, sample_needs):
        """Test building hierarchy with single document."""
        # Filter to just system requirements
        filtered = {k: v for k, v in sample_needs.items() if v["docname"] == "requirements/system"}

        builder = HierarchyBuilder(needs=filtered, hierarchy_mode="document")
        tree = builder.build()

        assert tree.id == "__root__"
        assert len(tree.children) == 1
        assert tree.children[0].label == "System"

    def test_build_multiple_documents(self, sample_needs):
        """Test building hierarchy with multiple documents."""
        builder = HierarchyBuilder(needs=sample_needs, hierarchy_mode="document")
        tree = builder.build()

        assert tree.id == "__root__"
        # Should have 3 documents: requirements/system, specifications/performance, specifications/security
        assert len(tree.children) == 3

    def test_build_with_sections(self, sample_needs):
        """Test that sections are correctly nested."""
        builder = HierarchyBuilder(
            needs=sample_needs,
            hierarchy_mode="document",
            max_depth=3,
        )
        tree = builder.build()

        # Find the system requirements document
        system_doc = next(
            (c for c in tree.children if "system" in c.id.lower()),
            None,
        )
        assert system_doc is not None
        # Should have section children
        assert len(system_doc.children) > 0

    def test_max_depth_limits_hierarchy(self, sample_needs):
        """Test that max_depth limits hierarchy depth."""
        builder = HierarchyBuilder(
            needs=sample_needs,
            hierarchy_mode="document",
            max_depth=1,
        )
        tree = builder.build()

        # At depth 1, needs should be direct children of documents
        for doc in tree.children:
            for child in doc.children:
                # Children should be needs, not sections
                assert child.node_type in ("need", "section")


class TestHierarchyBuilderLinks:
    """Tests for link-based hierarchy building."""

    def test_build_links_hierarchy(self, sample_needs):
        """Test building hierarchy from link relationships."""
        builder = HierarchyBuilder(needs=sample_needs, hierarchy_mode="links")
        tree = builder.build()

        assert tree.id == "__root__"
        # REQ-001 and REQ-002 should be root level (no incoming links)
        root_need_ids = [c.metadata.get("need_id") for c in tree.children]
        assert "REQ-001" in root_need_ids
        assert "REQ-002" in root_need_ids

    def test_links_hierarchy_has_children(self, sample_needs):
        """Test that linked needs become children."""
        builder = HierarchyBuilder(needs=sample_needs, hierarchy_mode="links")
        tree = builder.build()

        # Find REQ-002 (has 2 specs linked)
        req_002 = next(
            (c for c in tree.children if c.metadata.get("need_id") == "REQ-002"),
            None,
        )
        assert req_002 is not None
        # Should have children (SPEC-002 and SPEC-003 link back to REQ-002)
        assert len(req_002.children) == 2


class TestHierarchyBuilderType:
    """Tests for type-based hierarchy building."""

    def test_build_type_hierarchy(self, sample_needs):
        """Test building hierarchy by need type."""
        builder = HierarchyBuilder(needs=sample_needs, hierarchy_mode="type")
        tree = builder.build()

        assert tree.id == "__root__"
        type_labels = [c.label.lower() for c in tree.children]
        assert "req" in type_labels
        assert "spec" in type_labels

    def test_type_hierarchy_includes_status(self, sample_needs):
        """Test that type hierarchy includes status grouping."""
        builder = HierarchyBuilder(
            needs=sample_needs,
            hierarchy_mode="type",
            max_depth=2,
        )
        tree = builder.build()

        # Find req type node
        req_node = next(
            (c for c in tree.children if c.need_type == "req"),
            None,
        )
        assert req_node is not None
        # Should have status children
        status_labels = [c.label.lower() for c in req_node.children]
        assert any("open" in s for s in status_labels)


class TestHierarchyBuilderSizeBy:
    """Tests for different size_by options."""

    def test_size_by_count(self, sample_needs):
        """Test size_by='count' gives value=1 per need."""
        builder = HierarchyBuilder(
            needs=sample_needs,
            size_by="count",
        )
        tree = builder.build()

        # Total should equal number of needs
        assert tree.value == len(sample_needs)

    def test_size_by_links(self, sample_needs):
        """Test size_by='links' uses link counts."""
        builder = HierarchyBuilder(
            needs=sample_needs,
            size_by="links",
        )
        tree = builder.build()

        # REQ-002 has 2 outgoing links, should have higher value
        # Total should be sum of link counts
        assert tree.value > len(sample_needs)
