"""
Firebird database features for Django.

Defines what features are supported by the Firebird database.
Based on official Firebird 5 documentation and PostgreSQL backend patterns.
"""

from django.db import InterfaceError
from django.db.backends.base.features import BaseDatabaseFeatures
from django.utils.functional import cached_property


class DatabaseFeatures(BaseDatabaseFeatures):
    # =========================================================================
    # Version requirements
    # =========================================================================
    minimum_database_version = (2, 5)

    # =========================================================================
    # Transaction support
    # =========================================================================
    supports_transactions = True
    atomic_transactions = True
    uses_savepoints = True
    can_release_savepoints = True
    # DDL in Firebird is auto-committed (cannot be rolled back)
    can_rollback_ddl = False

    # =========================================================================
    # SELECT FOR UPDATE support
    # Firebird uses WITH LOCK syntax instead of FOR UPDATE
    # =========================================================================
    has_select_for_update = True
    has_select_for_update_nowait = True  # WITH LOCK (implicit nowait behavior)
    has_select_for_update_of = False  # Firebird doesn't support OF clause
    has_select_for_no_key_update = False  # PostgreSQL specific

    @cached_property
    def has_select_for_update_skip_locked(self):
        """SKIP LOCKED available in Firebird 5.0+"""
        return self.connection.firebird_version >= (5, 0)

    # =========================================================================
    # RETURNING clause support
    # =========================================================================
    can_return_columns_from_insert = True
    can_return_rows_from_bulk_insert = False  # Only single row RETURNING

    @cached_property
    def can_return_rows_from_update(self):
        """UPDATE ... RETURNING supported in Firebird 2.1+"""
        return self.connection.firebird_version >= (2, 1)

    # =========================================================================
    # Constraints and indexes
    # =========================================================================
    supports_foreign_keys = True
    can_introspect_foreign_keys = True
    can_create_inline_fk = True
    indexes_foreign_keys = True

    # Constraint checking
    can_defer_constraint_checks = False  # Firebird checks immediately
    supports_deferrable_unique_constraints = False

    # Index features
    supports_partial_indexes = True  # CREATE INDEX ... WHERE (Firebird 2.0+)
    supports_functions_in_partial_indexes = True
    supports_expression_indexes = True  # COMPUTED BY in index
    supports_covering_indexes = False  # Firebird doesn't have INCLUDE clause
    can_rename_index = False  # No ALTER INDEX ... RENAME in Firebird
    supports_index_column_ordering = True  # ASC/DESC in indexes

    # CHECK constraints
    supports_column_check_constraints = True
    supports_table_check_constraints = True
    can_introspect_check_constraints = True

    # =========================================================================
    # Field types
    # =========================================================================
    has_real_datatype = True  # FLOAT is REAL in Firebird
    has_native_uuid_field = False  # No native UUID, use CHAR(36) or BINARY(16)
    has_native_duration_field = False  # No INTERVAL type
    supports_temporal_subtraction = False  # Uses DATEDIFF(), not - operator
    supports_unlimited_charfield = False  # VARCHAR requires length in Firebird

    @cached_property
    def has_native_boolean_field(self):
        """Native BOOLEAN type in Firebird 3.0+"""
        return self.connection.firebird_version >= (3, 0)

    # =========================================================================
    # JSON support - Firebird does NOT have native JSON
    # =========================================================================
    supports_json_field = False
    can_introspect_json_field = False
    has_native_json_field = False
    has_json_operators = False
    supports_json_field_contains = False
    has_json_object_function = False

    # =========================================================================
    # Timezone support
    # =========================================================================
    @cached_property
    def supports_timezones(self):
        """TIME/TIMESTAMP WITH TIME ZONE in Firebird 4.0+"""
        return self.connection.firebird_version >= (4, 0)

    @cached_property
    def has_zoneinfo_database(self):
        """Firebird 4.0+ has built-in timezone database (ICU)"""
        return self.connection.firebird_version >= (4, 0)

    # =========================================================================
    # Generated/Computed columns
    # =========================================================================
    @cached_property
    def supports_stored_generated_columns(self):
        """COMPUTED BY columns (stored) - available since Firebird 1.0"""
        return True

    supports_virtual_generated_columns = False  # Firebird only has stored

    # =========================================================================
    # NULL handling
    # =========================================================================
    nulls_order_largest = False  # Firebird: NULLs sort first by default
    order_by_nulls_first = True  # Firebird default
    supports_order_by_nulls_modifier = True  # NULLS FIRST/LAST supported
    implied_column_null = True  # Columns are nullable by default
    supports_nullable_unique_constraints = True
    supports_partially_nullable_unique_constraints = True
    supports_nulls_distinct_unique_constraints = False  # No NULLS DISTINCT syntax

    # =========================================================================
    # String/LIKE features
    # =========================================================================
    has_case_insensitive_like = False  # LIKE is case-sensitive
    supports_regex_backreferencing = False  # SIMILAR TO has limitations
    supports_collation_on_charfield = True
    supports_collation_on_textfield = True  # BLOB SUB_TYPE TEXT

    # =========================================================================
    # Aggregate and Window functions
    # =========================================================================
    @cached_property
    def supports_over_clause(self):
        """Window functions in Firebird 3.0+"""
        return self.connection.firebird_version >= (3, 0)

    @cached_property
    def supports_frame_range_fixed_distance(self):
        """ROWS/RANGE with bounds in Firebird 3.0+"""
        return self.connection.firebird_version >= (3, 0)

    supports_frame_exclusion = False  # EXCLUDE clause not supported
    # Firebird 3+ supports value expressions in window frames (not just UNBOUNDED)
    only_supports_unbounded_with_preceding_and_following = False

    @cached_property
    def supports_aggregate_filter_clause(self):
        """FILTER (WHERE ...) in aggregates - Firebird 3.0+"""
        return self.connection.firebird_version >= (3, 0)

    supports_aggregate_order_by_clause = False  # No ORDER BY in aggregates
    supports_any_value = False  # No SQL 2023 ANY_VALUE function

    # =========================================================================
    # Combinatorial (UNION, INTERSECT, EXCEPT)
    # =========================================================================
    supports_select_union = True
    supports_select_intersection = True  # INTERSECT
    supports_select_difference = True  # EXCEPT
    supports_slicing_ordering_in_compound = False  # No LIMIT in compound
    supports_parentheses_in_compound = True
    requires_compound_order_by_subquery = True

    # =========================================================================
    # Subqueries
    # =========================================================================
    supports_subqueries_in_group_by = True
    allow_sliced_subqueries_with_in = True
    delete_can_self_reference_subquery = True

    # =========================================================================
    # UPSERT / Conflict handling
    # Firebird has UPDATE OR INSERT and MERGE, but not ON CONFLICT syntax
    # =========================================================================
    supports_ignore_conflicts = False  # No INSERT ... ON CONFLICT DO NOTHING
    supports_update_conflicts = False  # No ON CONFLICT DO UPDATE
    supports_update_conflicts_with_target = False

    # =========================================================================
    # Table features
    # =========================================================================
    supports_tablespaces = False  # Firebird doesn't have tablespaces
    supports_sequence_reset = True  # ALTER SEQUENCE ... RESTART
    can_introspect_default = False  # Complex due to generators/triggers
    can_introspect_materialized_views = False  # No materialized views
    can_distinct_on_fields = False  # No DISTINCT ON

    # =========================================================================
    # Comments
    # =========================================================================
    supports_comments = True  # COMMENT ON supported
    supports_comments_inline = False  # Not in ADD COLUMN

    # =========================================================================
    # Schema operations
    # =========================================================================
    supports_combined_alters = False  # One ALTER per statement
    connection_persists_old_columns = False
    schema_editor_uses_clientside_param_binding = False
    requires_casted_case_in_updates = False

    # =========================================================================
    # Misc features
    # =========================================================================
    allows_group_by_selected_pks = False
    allows_group_by_lob = False  # Cannot GROUP BY BLOB
    greatest_least_ignores_nulls = False  # Returns NULL if any arg is NULL
    can_clone_databases = False  # No built-in clone
    truncates_names = True  # Firebird truncates long identifiers

    # Parameters
    supports_paramstyle_pyformat = False  # Firebird uses ? placeholders
    requires_literal_defaults = True  # No parameterized defaults
    supports_expression_defaults = False  # Limited default expressions

    # Error handling
    closed_cursor_error_class = InterfaceError

    # =========================================================================
    # EXPLAIN support
    # =========================================================================
    supported_explain_formats = {"TEXT"}  # SET EXPLAIN ON gives text plan

    # =========================================================================
    # Test configuration (for Django test suite)
    # =========================================================================
    # SQL for INSERT with DEFAULT VALUES
    insert_test_table_with_defaults = "INSERT INTO {} DEFAULT VALUES"

    # SQL template for current UTC timestamp
    test_now_utc_template = "CURRENT_TIMESTAMP"

    # Collation names for tests
    test_collations = {
        "ci": None,  # Case-insensitive - Firebird uses collation per charset
        "cs": None,  # Case-sensitive
        "non_default": "UNICODE",  # Non-default collation
        "swedish_ci": None,  # Swedish case-insensitive
        "virtual": None,  # For virtual columns
    }

    # =========================================================================
    # Test procedures (for Django test suite)
    # =========================================================================
    create_test_procedure_without_params_sql = """
        CREATE PROCEDURE test_procedure
        AS
        DECLARE VARIABLE V_I INTEGER;
        BEGIN
            V_I = 1;
        END
    """
    create_test_procedure_with_int_param_sql = """
        CREATE PROCEDURE test_procedure (P_I INTEGER)
        AS
        DECLARE VARIABLE V_I INTEGER;
        BEGIN
            V_I = P_I;
        END
    """

    # =========================================================================
    # Introspected field types mapping
    # =========================================================================
    @cached_property
    def introspected_field_types(self):
        types = {
            **super().introspected_field_types,
            "PositiveBigIntegerField": "BigIntegerField",
            "PositiveIntegerField": "IntegerField",
            "PositiveSmallIntegerField": "SmallIntegerField",
        }
        if not self.has_native_boolean_field:
            types["BooleanField"] = "SmallIntegerField"
        return types

    # =========================================================================
    # Version detection helpers
    # =========================================================================
    @cached_property
    def is_firebird_3(self):
        return self.connection.firebird_version >= (3, 0)

    @cached_property
    def is_firebird_4(self):
        return self.connection.firebird_version >= (4, 0)

    @cached_property
    def is_firebird_5(self):
        return self.connection.firebird_version >= (5, 0)

    # =========================================================================
    # Test skips - tests that don't apply to Firebird
    # =========================================================================
    @cached_property
    def django_test_skips(self):
        skips = {
            "Firebird does not support covering indexes": {
                "indexes.tests.CoveringIndexTests",
            },
            "Firebird does not support DISTINCT ON": {
                "distinct_on_fields.tests",
            },
            "Firebird does not support JSON field": {
                "model_fields.test_jsonfield",
            },
            "Firebird does not have native UUID field": {
                "model_fields.test_uuid.TestQuerying.test_exact",
            },
            "Firebird uses WITH LOCK instead of FOR UPDATE OF": {
                "select_for_update.tests.SelectForUpdateTests."
                "test_for_update_of_argument",
            },
        }

        if not self.is_firebird_3:
            skips["Firebird < 3.0 does not support window functions"] = {
                "expressions_window.tests",
            }
            skips["Firebird < 3.0 does not support FILTER clause"] = {
                "aggregation.tests.AggregateTestCase.test_filter_argument",
            }

        if not self.is_firebird_4:
            skips["Firebird < 4.0 does not support timezones"] = {
                "timezones.tests",
            }

        if not self.is_firebird_5:
            skips["Firebird < 5.0 does not support SKIP LOCKED"] = {
                "select_for_update.tests.SelectForUpdateTests."
                "test_for_update_skip_locked",
            }

        return skips

    @cached_property
    def django_test_expected_failures(self):
        """Tests expected to fail on Firebird."""
        return set()
