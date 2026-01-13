"""
Tests for topological sorting in inspectdb_firebird command.
"""

from collections import defaultdict
from unittest.mock import MagicMock

from django_firebird.management.commands.inspectdb_firebird import Command


class TestTopologicalSort:
    """Test cases for the topological sort algorithm."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = Command()

    def test_empty_tables(self):
        """Test with no tables."""
        ordered, cyclic = self.command.topological_sort(set(), {})
        assert ordered == []
        assert cyclic == []

    def test_single_table_no_deps(self):
        """Test with single table without dependencies."""
        tables = {"A"}
        deps = {}

        ordered, cyclic = self.command.topological_sort(tables, deps)

        assert ordered == ["A"]
        assert cyclic == []

    def test_linear_chain(self, mock_introspection_data):
        """Test dependency chain: COMPANY -> CUSTOMER -> ORDER, etc."""
        tables = set(mock_introspection_data["tables"])
        relations = mock_introspection_data["relations"]

        # Build dependencies (which tables each table depends on)
        deps = defaultdict(set)
        for table, rels in relations.items():
            for _col, (ref_table, _ref_col) in rels.items():
                if ref_table in tables and ref_table != table:
                    deps[table].add(ref_table)

        ordered, cyclic = self.command.topological_sort(tables, deps)

        assert cyclic == []
        # COMPANY must come before CUSTOMER
        assert ordered.index("COMPANY") < ordered.index("CUSTOMER")
        # CUSTOMER must come before ORDER
        assert ordered.index("CUSTOMER") < ordered.index("ORDER")
        # ORDER must come before ORDER_ITEM
        assert ordered.index("ORDER") < ordered.index("ORDER_ITEM")
        # PRODUCT must come before ORDER_ITEM
        assert ordered.index("PRODUCT") < ordered.index("ORDER_ITEM")

    def test_diamond_dependency(self, mock_complex_data):
        """
        Test diamond-shaped dependency:
        A -> B, A -> C, B -> D, C -> D, D -> E
        """
        tables = set(mock_complex_data["tables"])
        relations = mock_complex_data["relations"]

        deps = defaultdict(set)
        for table, rels in relations.items():
            for _col, (ref_table, _ref_col) in rels.items():
                if ref_table in tables and ref_table != table:
                    deps[table].add(ref_table)

        ordered, cyclic = self.command.topological_sort(tables, deps)

        assert cyclic == []
        # A must come first (no dependencies)
        assert ordered[0] == "A"
        # B and C must come after A
        assert ordered.index("A") < ordered.index("B")
        assert ordered.index("A") < ordered.index("C")
        # D must come after both B and C
        assert ordered.index("B") < ordered.index("D")
        assert ordered.index("C") < ordered.index("D")
        # E must come last
        assert ordered[-1] == "E"

    def test_circular_dependency(self, mock_cyclic_data):
        """Test detection of circular dependencies: A -> B -> C -> A."""
        tables = set(mock_cyclic_data["tables"])
        relations = mock_cyclic_data["relations"]

        deps = defaultdict(set)
        for table, rels in relations.items():
            for _col, (ref_table, _ref_col) in rels.items():
                if ref_table in tables and ref_table != table:
                    deps[table].add(ref_table)

        ordered, cyclic = self.command.topological_sort(tables, deps)

        # A, B, C are in a cycle, D depends on A
        # All should be in cyclic since none can be resolved
        assert set(cyclic) == {"A", "B", "C", "D"}
        assert ordered == []

    def test_partial_cycle(self):
        """Test partial cycle where some tables can be resolved."""
        tables = {"A", "B", "C", "D", "E"}
        # A has no deps, B->C->B (cycle), D->A, E->D
        deps = {
            "A": set(),
            "B": {"C"},
            "C": {"B"},
            "D": {"A"},
            "E": {"D"},
        }

        ordered, cyclic = self.command.topological_sort(tables, deps)

        # A, D, E should be ordered (A->D->E chain)
        assert "A" in ordered
        assert "D" in ordered
        assert "E" in ordered
        assert ordered.index("A") < ordered.index("D")
        assert ordered.index("D") < ordered.index("E")

        # B and C are in a cycle
        assert set(cyclic) == {"B", "C"}

    def test_self_referential(self, mock_self_referential_data):
        """Test self-referential FK (table references itself)."""
        tables = set(mock_self_referential_data["tables"])
        relations = mock_self_referential_data["relations"]

        deps = defaultdict(set)
        for table, rels in relations.items():
            for _col, (ref_table, _ref_col) in rels.items():
                # Self-references should be ignored
                if ref_table in tables and ref_table != table:
                    deps[table].add(ref_table)

        ordered, cyclic = self.command.topological_sort(tables, deps)

        assert cyclic == []
        # CATEGORY has no external deps (self-ref ignored)
        # ITEM depends on CATEGORY
        assert ordered.index("CATEGORY") < ordered.index("ITEM")

    def test_multiple_independent_chains(self):
        """Test multiple independent dependency chains."""
        tables = {"A1", "B1", "C1", "A2", "B2"}
        # Chain 1: A1 -> B1 -> C1
        # Chain 2: A2 -> B2
        deps = {
            "A1": set(),
            "B1": {"A1"},
            "C1": {"B1"},
            "A2": set(),
            "B2": {"A2"},
        }

        ordered, cyclic = self.command.topological_sort(tables, deps)

        assert cyclic == []
        # Chain 1 order
        assert ordered.index("A1") < ordered.index("B1")
        assert ordered.index("B1") < ordered.index("C1")
        # Chain 2 order
        assert ordered.index("A2") < ordered.index("B2")

    def test_alphabetical_order_for_same_level(self):
        """Test that tables at same dependency level are sorted alphabetically."""
        tables = {"Z", "A", "M", "B"}
        deps = {}  # No dependencies

        ordered, cyclic = self.command.topological_sort(tables, deps)

        assert cyclic == []
        # Should be alphabetically sorted
        assert ordered == ["A", "B", "M", "Z"]

    def test_preserves_order_within_levels(self):
        """Test that alphabetical order is preserved within each level."""
        tables = {"Z_CHILD", "A_CHILD", "PARENT"}
        deps = {
            "PARENT": set(),
            "Z_CHILD": {"PARENT"},
            "A_CHILD": {"PARENT"},
        }

        ordered, cyclic = self.command.topological_sort(tables, deps)

        assert cyclic == []
        assert ordered[0] == "PARENT"
        # Children should be alphabetically sorted
        assert ordered[1] == "A_CHILD"
        assert ordered[2] == "Z_CHILD"


class TestBuildDependencyGraph:
    """Test cases for building the dependency graph."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = Command()

    def test_build_graph_filters_external_tables(self):
        """Test that dependencies on tables outside the set are ignored."""
        mock_cursor = MagicMock()
        mock_connection = MagicMock()

        # CUSTOMER depends on COMPANY, but COMPANY is not in our table set
        def mock_get_relations(cursor, table_name):
            if table_name == "CUSTOMER":
                return {"COMPANY_ID": ("COMPANY", "ID")}
            return {}

        mock_connection.introspection.get_relations = mock_get_relations

        tables = {"CUSTOMER"}  # Only CUSTOMER, not COMPANY
        deps = self.command.build_dependency_graph(mock_cursor, mock_connection, tables)

        # CUSTOMER should have no dependencies since COMPANY is not in our set
        assert deps["CUSTOMER"] == set()

    def test_build_graph_includes_internal_deps(self):
        """Test that dependencies within the set are included."""
        mock_cursor = MagicMock()
        mock_connection = MagicMock()

        def mock_get_relations(cursor, table_name):
            if table_name == "CUSTOMER":
                return {"COMPANY_ID": ("COMPANY", "ID")}
            return {}

        mock_connection.introspection.get_relations = mock_get_relations

        tables = {"CUSTOMER", "COMPANY"}  # Both tables
        deps = self.command.build_dependency_graph(mock_cursor, mock_connection, tables)

        assert deps["CUSTOMER"] == {"COMPANY"}
        assert deps["COMPANY"] == set()

    def test_build_graph_handles_errors(self):
        """Test that errors during introspection are handled gracefully."""
        mock_cursor = MagicMock()
        mock_connection = MagicMock()

        def mock_get_relations(cursor, table_name):
            raise Exception("Database error")

        mock_connection.introspection.get_relations = mock_get_relations

        tables = {"CUSTOMER"}
        # Should not raise, just return empty deps
        deps = self.command.build_dependency_graph(mock_cursor, mock_connection, tables)

        assert deps["CUSTOMER"] == set()
