"""
Custom inspectdb command for Firebird with topological ordering.

This command generates Django models from an existing Firebird database,
ordering them by their foreign key dependencies so that referenced models
come before the models that reference them.
"""

from collections import defaultdict, deque

from django.core.management.commands.inspectdb import Command as InspectDBCommand


class Command(InspectDBCommand):
    help = (
        "Introspects the Firebird database and outputs Django model classes "
        "ordered by their foreign key dependencies."
    )

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--no-order",
            action="store_true",
            dest="no_order",
            help="Disable topological ordering (use alphabetical order like default inspectdb)",
        )

    def handle(self, **options):
        # If --no-order is specified, use default behavior
        if options.get("no_order"):
            return super().handle(**options)

        # Otherwise, use our custom ordered inspection
        return self.handle_ordered(**options)

    def handle_ordered(self, **options):
        """Handle inspection with topological ordering."""
        from django.db import connections

        connection = connections[options["database"]]

        # Get all tables and their dependencies
        with connection.cursor() as cursor:
            # Get table list
            table_info = connection.introspection.get_table_list(cursor)

            # Filter by specified tables if provided
            if options["table"]:
                table_names = set(options["table"])
            else:
                table_names = {t.name for t in table_info if t.type == "t"}

            # Build dependency graph
            dependencies = self.build_dependency_graph(cursor, connection, table_names)

            # Topological sort
            ordered_tables, cyclic_tables = self.topological_sort(
                table_names, dependencies
            )

        # Store ordered tables for use in handle_inspection
        self._ordered_tables = ordered_tables
        self._cyclic_tables = cyclic_tables

        # Call parent's handle with our custom table filter
        options["table"] = ordered_tables + cyclic_tables

        # Generate output
        output = []
        for line in self.handle_inspection(options):
            output.append(line)

        # Add comment about cyclic dependencies if any
        if cyclic_tables:
            output.insert(
                7,  # After the initial comments
                "# NOTE: The following tables have circular dependencies and were added at the end:",
            )
            output.insert(8, f"#   {', '.join(cyclic_tables)}")
            output.insert(9, "")

        return "\n".join(output)

    def build_dependency_graph(self, cursor, connection, table_names):
        """
        Build a graph of table dependencies based on foreign keys.

        Returns a dict: {table_name: set of tables it depends on}
        """
        dependencies = defaultdict(set)
        introspection = connection.introspection

        for table_name in table_names:
            try:
                relations = introspection.get_relations(cursor, table_name)
                for _column, (ref_table, _ref_column) in relations.items():
                    # Only add dependency if referenced table is in our set
                    if ref_table in table_names and ref_table != table_name:
                        dependencies[table_name].add(ref_table)
            except Exception:
                # If we can't get relations, assume no dependencies
                pass

        return dependencies

    def topological_sort(self, table_names, dependencies):
        """
        Perform topological sort using Kahn's algorithm.

        Returns:
            (ordered_tables, cyclic_tables): Tuple of ordered list and list of
            tables involved in cycles.
        """
        # Calculate in-degree for each table
        in_degree = {table: 0 for table in table_names}
        reverse_deps = defaultdict(set)  # Tables that depend on each table

        for table, deps in dependencies.items():
            in_degree[table] = len(deps)
            for dep in deps:
                reverse_deps[dep].add(table)

        # Start with tables that have no dependencies (in-degree = 0)
        queue = deque(
            sorted(table for table, degree in in_degree.items() if degree == 0)
        )

        ordered = []

        while queue:
            # Get next table with no remaining dependencies
            table = queue.popleft()
            ordered.append(table)

            # Reduce in-degree for tables that depend on this one
            for dependent in sorted(reverse_deps[table]):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Tables not in ordered list have circular dependencies
        cyclic = sorted(table for table in table_names if table not in ordered)

        return ordered, cyclic

    def get_meta(
        self,
        table_name,
        constraints,
        column_to_field_name,
        is_view,
        is_partition,
        comment,
    ):
        """Override to add ordering info in meta."""
        meta = super().get_meta(
            table_name,
            constraints,
            column_to_field_name,
            is_view,
            is_partition,
            comment,
        )

        # Add comment if table has circular dependencies
        if hasattr(self, "_cyclic_tables") and table_name in self._cyclic_tables:
            meta = list(meta)
            meta.insert(0, "    # WARNING: This table has circular FK dependencies")

        return meta
