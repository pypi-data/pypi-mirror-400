"""
Tests for Firebird database features.
"""

from unittest.mock import MagicMock

import pytest


class TestDatabaseFeatures:
    """Test cases for DatabaseFeatures."""

    @pytest.fixture
    def features_25(self):
        """Features instance for Firebird 2.5."""
        from django_firebird.features import DatabaseFeatures

        mock_connection = MagicMock()
        mock_connection.firebird_version = (2, 5)
        return DatabaseFeatures(mock_connection)

    @pytest.fixture
    def features_30(self):
        """Features instance for Firebird 3.0."""
        from django_firebird.features import DatabaseFeatures

        mock_connection = MagicMock()
        mock_connection.firebird_version = (3, 0)
        return DatabaseFeatures(mock_connection)

    @pytest.fixture
    def features_40(self):
        """Features instance for Firebird 4.0."""
        from django_firebird.features import DatabaseFeatures

        mock_connection = MagicMock()
        mock_connection.firebird_version = (4, 0)
        return DatabaseFeatures(mock_connection)

    @pytest.fixture
    def features_50(self):
        """Features instance for Firebird 5.0."""
        from django_firebird.features import DatabaseFeatures

        mock_connection = MagicMock()
        mock_connection.firebird_version = (5, 0)
        return DatabaseFeatures(mock_connection)

    # =========================================================================
    # Basic features (all versions)
    # =========================================================================

    def test_supports_transactions(self, features_25):
        """All Firebird versions support transactions."""
        assert features_25.supports_transactions is True

    def test_supports_savepoints(self, features_25):
        """All Firebird versions support savepoints."""
        assert features_25.uses_savepoints is True
        assert features_25.can_release_savepoints is True

    def test_cannot_rollback_ddl(self, features_25):
        """DDL is auto-committed in Firebird."""
        assert features_25.can_rollback_ddl is False

    def test_supports_foreign_keys(self, features_25):
        """All Firebird versions support foreign keys."""
        assert features_25.supports_foreign_keys is True
        assert features_25.can_introspect_foreign_keys is True

    # =========================================================================
    # SELECT FOR UPDATE features
    # =========================================================================

    def test_has_select_for_update(self, features_25):
        """Firebird supports SELECT ... WITH LOCK."""
        assert features_25.has_select_for_update is True

    def test_has_select_for_update_nowait(self, features_25):
        """Firebird WITH LOCK has implicit nowait behavior."""
        assert features_25.has_select_for_update_nowait is True

    def test_no_select_for_update_of(self, features_25):
        """Firebird doesn't support FOR UPDATE OF clause."""
        assert features_25.has_select_for_update_of is False

    def test_skip_locked_firebird_25(self, features_25):
        """Firebird 2.5 does not support SKIP LOCKED."""
        assert features_25.has_select_for_update_skip_locked is False

    def test_skip_locked_firebird_50(self, features_50):
        """Firebird 5.0 supports SKIP LOCKED."""
        assert features_50.has_select_for_update_skip_locked is True

    # =========================================================================
    # RETURNING clause
    # =========================================================================

    def test_can_return_from_insert(self, features_25):
        """All Firebird versions support RETURNING from INSERT."""
        assert features_25.can_return_columns_from_insert is True

    def test_cannot_return_bulk_insert(self, features_25):
        """Firebird only supports single-row RETURNING."""
        assert features_25.can_return_rows_from_bulk_insert is False

    def test_can_return_from_update(self, features_25):
        """Firebird 2.1+ supports UPDATE ... RETURNING."""
        assert features_25.can_return_rows_from_update is True

    # =========================================================================
    # Index features
    # =========================================================================

    def test_supports_partial_indexes(self, features_25):
        """Firebird supports partial indexes (WHERE clause)."""
        assert features_25.supports_partial_indexes is True
        assert features_25.supports_functions_in_partial_indexes is True

    def test_supports_expression_indexes(self, features_25):
        """Firebird supports expression indexes (COMPUTED BY)."""
        assert features_25.supports_expression_indexes is True

    def test_no_covering_indexes(self, features_50):
        """Firebird doesn't support covering indexes (INCLUDE)."""
        assert features_50.supports_covering_indexes is False

    def test_cannot_rename_index(self, features_25):
        """Firebird doesn't support ALTER INDEX ... RENAME."""
        assert features_25.can_rename_index is False

    # =========================================================================
    # Boolean field (version dependent)
    # =========================================================================

    def test_no_native_boolean_firebird_25(self, features_25):
        """Firebird 2.5 has no native BOOLEAN type."""
        assert features_25.has_native_boolean_field is False

    def test_native_boolean_firebird_30(self, features_30):
        """Firebird 3.0 has native BOOLEAN type."""
        assert features_30.has_native_boolean_field is True

    # =========================================================================
    # JSON support (none)
    # =========================================================================

    def test_no_json_support(self, features_50):
        """Firebird does not have JSON support."""
        assert features_50.supports_json_field is False
        assert features_50.has_native_json_field is False
        assert features_50.has_json_operators is False
        assert features_50.can_introspect_json_field is False

    # =========================================================================
    # Timezone support (version dependent)
    # =========================================================================

    def test_no_timezone_firebird_30(self, features_30):
        """Firebird 3.0 does not support timezones."""
        assert features_30.supports_timezones is False
        assert features_30.has_zoneinfo_database is False

    def test_timezone_firebird_40(self, features_40):
        """Firebird 4.0 supports TIME/TIMESTAMP WITH TIME ZONE."""
        assert features_40.supports_timezones is True
        assert features_40.has_zoneinfo_database is True

    # =========================================================================
    # Generated columns
    # =========================================================================

    def test_supports_stored_generated_columns(self, features_25):
        """Firebird supports COMPUTED BY columns."""
        assert features_25.supports_stored_generated_columns is True

    def test_no_virtual_generated_columns(self, features_50):
        """Firebird doesn't have virtual generated columns."""
        assert features_50.supports_virtual_generated_columns is False

    # =========================================================================
    # Window functions (version dependent)
    # =========================================================================

    def test_no_window_functions_firebird_25(self, features_25):
        """Firebird 2.5 does not support window functions."""
        assert features_25.supports_over_clause is False
        assert features_25.supports_aggregate_filter_clause is False

    def test_window_functions_firebird_30(self, features_30):
        """Firebird 3.0 supports window functions."""
        assert features_30.supports_over_clause is True
        assert features_30.supports_frame_range_fixed_distance is True
        assert features_30.supports_aggregate_filter_clause is True

    def test_no_frame_exclusion(self, features_50):
        """Firebird doesn't support EXCLUDE clause in frames."""
        assert features_50.supports_frame_exclusion is False

    # =========================================================================
    # NULL handling
    # =========================================================================

    def test_nulls_order(self, features_25):
        """Firebird sorts NULLs first by default."""
        assert features_25.nulls_order_largest is False
        assert features_25.order_by_nulls_first is True

    def test_supports_nulls_modifier(self, features_25):
        """Firebird supports NULLS FIRST/LAST."""
        assert features_25.supports_order_by_nulls_modifier is True

    def test_implied_column_null(self, features_25):
        """Columns are nullable by default in Firebird."""
        assert features_25.implied_column_null is True

    # =========================================================================
    # Unsupported features
    # =========================================================================

    def test_no_tablespaces(self, features_25):
        """Firebird doesn't have tablespaces."""
        assert features_25.supports_tablespaces is False

    def test_no_distinct_on(self, features_25):
        """Firebird doesn't support DISTINCT ON."""
        assert features_25.can_distinct_on_fields is False

    def test_no_clone_databases(self, features_25):
        """Firebird doesn't have built-in database cloning."""
        assert features_25.can_clone_databases is False

    def test_no_defer_constraints(self, features_25):
        """Firebird checks constraints immediately."""
        assert features_25.can_defer_constraint_checks is False
        assert features_25.supports_deferrable_unique_constraints is False

    # =========================================================================
    # UPSERT features
    # =========================================================================

    def test_no_on_conflict_syntax(self, features_50):
        """Firebird uses UPDATE OR INSERT, not ON CONFLICT."""
        assert features_50.supports_ignore_conflicts is False
        assert features_50.supports_update_conflicts is False

    # =========================================================================
    # Version detection helpers
    # =========================================================================

    def test_is_firebird_3(self, features_25, features_30):
        """Test is_firebird_3 property."""
        assert features_25.is_firebird_3 is False
        assert features_30.is_firebird_3 is True

    def test_is_firebird_4(self, features_30, features_40):
        """Test is_firebird_4 property."""
        assert features_30.is_firebird_4 is False
        assert features_40.is_firebird_4 is True

    def test_is_firebird_5(self, features_40, features_50):
        """Test is_firebird_5 property."""
        assert features_40.is_firebird_5 is False
        assert features_50.is_firebird_5 is True

    # =========================================================================
    # Introspected field types
    # =========================================================================

    def test_introspected_field_types_firebird_25(self, features_25):
        """Firebird 2.5 maps BooleanField to SmallIntegerField."""
        types = features_25.introspected_field_types
        assert types["BooleanField"] == "SmallIntegerField"
        assert types["PositiveIntegerField"] == "IntegerField"

    def test_introspected_field_types_firebird_30(self, features_30):
        """Firebird 3.0 has native BooleanField."""
        types = features_30.introspected_field_types
        assert (
            "BooleanField" not in types or types.get("BooleanField") == "BooleanField"
        )

    # =========================================================================
    # Test skips
    # =========================================================================

    def test_django_test_skips_base(self, features_50):
        """Basic test skips are present."""
        skips = features_50.django_test_skips
        assert "Firebird does not support covering indexes" in skips
        assert "Firebird does not support DISTINCT ON" in skips
        assert "Firebird does not support JSON field" in skips

    def test_django_test_skips_version_dependent(self, features_25):
        """Version-dependent test skips for Firebird 2.5."""
        skips = features_25.django_test_skips
        assert "Firebird < 3.0 does not support window functions" in skips
        assert "Firebird < 4.0 does not support timezones" in skips
        assert "Firebird < 5.0 does not support SKIP LOCKED" in skips

    def test_no_extra_skips_firebird_50(self, features_50):
        """Firebird 5.0 doesn't have version-dependent skips."""
        skips = features_50.django_test_skips
        assert "Firebird < 3.0 does not support window functions" not in skips
        assert "Firebird < 4.0 does not support timezones" not in skips
        assert "Firebird < 5.0 does not support SKIP LOCKED" not in skips

    # =========================================================================
    # Test procedures
    # =========================================================================

    def test_create_test_procedure_sql(self, features_25):
        """Test procedure SQL is defined."""
        assert features_25.create_test_procedure_without_params_sql is not None
        assert (
            "CREATE PROCEDURE test_procedure"
            in features_25.create_test_procedure_without_params_sql
        )
        assert features_25.create_test_procedure_with_int_param_sql is not None
        assert "P_I INTEGER" in features_25.create_test_procedure_with_int_param_sql

    # =========================================================================
    # Misc features
    # =========================================================================

    def test_truncates_names(self, features_25):
        """Firebird truncates long identifiers."""
        assert features_25.truncates_names is True

    def test_no_pyformat_paramstyle(self, features_25):
        """Firebird uses ? placeholders, not %(name)s."""
        assert features_25.supports_paramstyle_pyformat is False

    def test_supports_comments(self, features_25):
        """Firebird supports COMMENT ON."""
        assert features_25.supports_comments is True
        assert features_25.supports_comments_inline is False

    def test_explain_formats(self, features_25):
        """Firebird supports TEXT explain format."""
        assert "TEXT" in features_25.supported_explain_formats

    # =========================================================================
    # Additional PostgreSQL-compatible flags
    # =========================================================================

    def test_insert_test_table_with_defaults(self, features_25):
        """Firebird supports INSERT ... DEFAULT VALUES."""
        assert features_25.insert_test_table_with_defaults is not None
        assert "DEFAULT VALUES" in features_25.insert_test_table_with_defaults

    def test_only_supports_unbounded(self, features_25):
        """Firebird 3+ supports value expressions in window frames."""
        assert features_25.only_supports_unbounded_with_preceding_and_following is False

    def test_requires_casted_case_in_updates(self, features_25):
        """Firebird doesn't require CASE casting in UPDATEs."""
        assert features_25.requires_casted_case_in_updates is False

    def test_schema_editor_clientside_binding(self, features_25):
        """Firebird doesn't use client-side param binding in schema editor."""
        assert features_25.schema_editor_uses_clientside_param_binding is False

    def test_supports_any_value(self, features_25):
        """Firebird doesn't support SQL 2023 ANY_VALUE."""
        assert features_25.supports_any_value is False

    def test_supports_nulls_distinct_unique(self, features_25):
        """Firebird doesn't support NULLS DISTINCT in unique constraints."""
        assert features_25.supports_nulls_distinct_unique_constraints is False

    def test_supports_temporal_subtraction(self, features_25):
        """Firebird uses DATEDIFF(), not - operator for temporal subtraction."""
        assert features_25.supports_temporal_subtraction is False

    def test_supports_unlimited_charfield(self, features_25):
        """Firebird requires VARCHAR length."""
        assert features_25.supports_unlimited_charfield is False

    def test_test_collations(self, features_25):
        """Test collations dict is defined."""
        assert features_25.test_collations is not None
        assert isinstance(features_25.test_collations, dict)
        assert "non_default" in features_25.test_collations

    def test_test_now_utc_template(self, features_25):
        """UTC timestamp template is defined."""
        assert features_25.test_now_utc_template is not None
        assert "TIMESTAMP" in features_25.test_now_utc_template
