"""
Tests for DatabaseSchemaEditor class.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestDatabaseSchemaEditor:
    """Test cases for DatabaseSchemaEditor methods."""

    @pytest.fixture
    def schema_editor(self, mock_connection):
        """Create DatabaseSchemaEditor instance with mock connection."""
        from django_firebird.schema import DatabaseSchemaEditor

        return DatabaseSchemaEditor(mock_connection)

    # =========================================================================
    # SQL template tests
    # =========================================================================

    def test_sql_create_index_template(self, schema_editor):
        """Test CREATE INDEX template includes condition placeholder."""
        assert "%(columns)s" in schema_editor.sql_create_index
        assert "%(condition)s" in schema_editor.sql_create_index

    def test_sql_create_unique_index_template(self, schema_editor):
        """Test CREATE UNIQUE INDEX template includes condition placeholder."""
        assert "%(columns)s" in schema_editor.sql_create_unique_index
        assert "%(condition)s" in schema_editor.sql_create_unique_index

    def test_sql_create_expression_index_template(self, schema_editor):
        """Test expression index uses COMPUTED BY syntax."""
        assert "COMPUTED BY" in schema_editor.sql_create_expression_index
        assert "%(expressions)s" in schema_editor.sql_create_expression_index
        assert "%(condition)s" in schema_editor.sql_create_expression_index

    def test_sql_create_unique_expression_index_template(self, schema_editor):
        """Test unique expression index uses COMPUTED BY syntax."""
        assert "COMPUTED BY" in schema_editor.sql_create_unique_expression_index
        assert "UNIQUE" in schema_editor.sql_create_unique_expression_index
        assert "%(expressions)s" in schema_editor.sql_create_unique_expression_index

    def test_sql_rename_column_template(self, schema_editor):
        """Test Firebird's column rename syntax (ALTER ... TO)."""
        assert "ALTER COLUMN" in schema_editor.sql_rename_column
        assert "TO" in schema_editor.sql_rename_column

    def test_sql_delete_index_template(self, schema_editor):
        """Test DROP INDEX template."""
        assert schema_editor.sql_delete_index == "DROP INDEX %(name)s"

    # =========================================================================
    # quote_value tests
    # =========================================================================

    def test_quote_value_string(self, schema_editor):
        """Test quoting string values."""
        assert schema_editor.quote_value("test") == "'test'"

    def test_quote_value_string_with_quotes(self, schema_editor):
        """Test quoting string with embedded single quotes."""
        assert schema_editor.quote_value("it's") == "'it''s'"

    def test_quote_value_boolean_true(self, schema_editor):
        """Test quoting boolean True."""
        assert schema_editor.quote_value(True) == "1"

    def test_quote_value_boolean_false(self, schema_editor):
        """Test quoting boolean False."""
        assert schema_editor.quote_value(False) == "0"

    def test_quote_value_none(self, schema_editor):
        """Test quoting None."""
        assert schema_editor.quote_value(None) == "NULL"

    def test_quote_value_integer(self, schema_editor):
        """Test quoting integer."""
        assert schema_editor.quote_value(42) == "42"

    def test_quote_value_float(self, schema_editor):
        """Test quoting float."""
        assert schema_editor.quote_value(3.14) == "3.14"

    # =========================================================================
    # Sequence and trigger SQL tests
    # =========================================================================

    def test_create_sequence_sql(self, schema_editor):
        """Test sequence creation SQL."""
        # Mock the ops methods
        schema_editor.connection.ops._get_generator_name = MagicMock(
            return_value="GEN_MY_TABLE_ID"
        )

        sql = schema_editor._create_sequence_sql("my_table", "id")
        assert "CREATE SEQUENCE" in sql

    def test_delete_sequence_sql(self, schema_editor):
        """Test sequence deletion SQL."""
        schema_editor.connection.ops._get_generator_name = MagicMock(
            return_value="GEN_MY_TABLE_ID"
        )

        sql = schema_editor._delete_sequence_sql("my_table", "id")
        assert "DROP SEQUENCE" in sql

    def test_create_trigger_sql(self, schema_editor):
        """Test auto-increment trigger creation SQL."""
        schema_editor.connection.ops._get_generator_name = MagicMock(
            return_value="GEN_MY_TABLE_ID"
        )
        schema_editor.connection.ops._get_trigger_name = MagicMock(
            return_value="TRG_MY_TABLE_ID"
        )

        sql = schema_editor._create_trigger_sql("my_table", "id")
        assert "CREATE TRIGGER" in sql
        assert "BEFORE INSERT" in sql
        assert "NEXT VALUE FOR" in sql
        assert "IS NULL" in sql

    def test_delete_trigger_sql(self, schema_editor):
        """Test trigger deletion SQL."""
        schema_editor.connection.ops._get_trigger_name = MagicMock(
            return_value="TRG_MY_TABLE_ID"
        )

        sql = schema_editor._delete_trigger_sql("my_table", "id")
        assert "DROP TRIGGER" in sql

    # =========================================================================
    # _alter_column_type_sql tests
    # =========================================================================

    def test_alter_column_type_sql(self, schema_editor):
        """Test ALTER COLUMN TYPE SQL generation."""
        mock_model = MagicMock()
        mock_model._meta.db_table = "test_table"

        old_field = MagicMock()
        new_field = MagicMock()
        new_field.column = "my_column"

        sql, params = schema_editor._alter_column_type_sql(
            mock_model, old_field, new_field, "VARCHAR(100)"
        )

        assert "ALTER TABLE" in sql
        assert "ALTER COLUMN" in sql
        assert "TYPE" in sql
        assert "VARCHAR(100)" in sql
        assert params == []

    # =========================================================================
    # _alter_column_null_sql tests
    # =========================================================================

    def test_alter_column_null_sql_set_nullable(self, schema_editor):
        """Test making column nullable."""
        mock_model = MagicMock()
        mock_model._meta.db_table = "test_table"

        old_field = MagicMock()
        new_field = MagicMock()
        new_field.column = "my_column"
        new_field.null = True

        sql, params = schema_editor._alter_column_null_sql(
            mock_model, old_field, new_field
        )

        assert "DROP NOT NULL" in sql
        assert params == []

    def test_alter_column_null_sql_set_not_nullable(self, schema_editor):
        """Test making column not nullable."""
        mock_model = MagicMock()
        mock_model._meta.db_table = "test_table"

        old_field = MagicMock()
        new_field = MagicMock()
        new_field.column = "my_column"
        new_field.null = False

        sql, params = schema_editor._alter_column_null_sql(
            mock_model, old_field, new_field
        )

        assert "SET NOT NULL" in sql
        assert params == []

    # =========================================================================
    # _alter_column_default_sql tests
    # =========================================================================

    def test_alter_column_default_sql_drop(self, schema_editor):
        """Test dropping column default."""
        mock_model = MagicMock()
        mock_model._meta.db_table = "test_table"

        old_field = MagicMock()
        new_field = MagicMock()
        new_field.column = "my_column"

        sql, params = schema_editor._alter_column_default_sql(
            mock_model, old_field, new_field, drop=True
        )

        assert "DROP DEFAULT" in sql
        assert params == []

    def test_alter_column_default_sql_set(self, schema_editor):
        """Test setting column default."""
        mock_model = MagicMock()
        mock_model._meta.db_table = "test_table"

        old_field = MagicMock()
        new_field = MagicMock()
        new_field.column = "my_column"

        with patch.object(
            schema_editor, "effective_default", return_value="default_value"
        ):
            sql, params = schema_editor._alter_column_default_sql(
                mock_model, old_field, new_field, drop=False
            )

        assert "SET DEFAULT" in sql
        assert "'default_value'" in sql
        assert params == []

    # =========================================================================
    # _field_should_be_altered tests
    # =========================================================================

    def test_field_should_be_altered_auto_field(self, schema_editor):
        """Test that AutoField changes are ignored."""
        old_field = MagicMock()
        old_field.get_internal_type.return_value = "AutoField"
        new_field = MagicMock()

        result = schema_editor._field_should_be_altered(old_field, new_field)

        assert result is False

    def test_field_should_be_altered_big_auto_field(self, schema_editor):
        """Test that BigAutoField changes are ignored."""
        old_field = MagicMock()
        old_field.get_internal_type.return_value = "BigAutoField"
        new_field = MagicMock()

        result = schema_editor._field_should_be_altered(old_field, new_field)

        assert result is False

    def test_field_should_be_altered_small_auto_field(self, schema_editor):
        """Test that SmallAutoField changes are ignored."""
        old_field = MagicMock()
        old_field.get_internal_type.return_value = "SmallAutoField"
        new_field = MagicMock()

        result = schema_editor._field_should_be_altered(old_field, new_field)

        assert result is False
