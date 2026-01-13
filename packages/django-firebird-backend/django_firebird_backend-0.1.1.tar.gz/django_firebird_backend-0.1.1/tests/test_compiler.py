"""
Tests for SQL compiler classes.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestSQLCompiler:
    """Test cases for SQLCompiler class."""

    @pytest.fixture
    def mock_query(self):
        """Create a mock query object."""
        query = MagicMock()
        query.alias_refcount = {}
        query.high_mark = None
        query.low_mark = 0
        return query

    @pytest.fixture
    def compiler(self, mock_connection, mock_query):
        """Create a SQLCompiler instance."""
        from django_firebird.compiler import SQLCompiler

        compiler = SQLCompiler(mock_query, mock_connection, using="default")
        return compiler

    def test_as_sql_no_limits(self, compiler, mock_query):
        """Test SQL generation without limits."""
        mock_query.high_mark = None
        mock_query.low_mark = 0

        with patch.object(
            compiler.__class__.__bases__[0],
            "as_sql",
            return_value=("SELECT * FROM test", []),
        ):
            sql, params = compiler.as_sql(with_limits=True)

        # No limits, so SQL should be unchanged
        assert sql == "SELECT * FROM test"

    def test_as_sql_with_limit_only(self, compiler, mock_query):
        """Test SQL generation with FIRST (limit) only."""
        mock_query.high_mark = 10
        mock_query.low_mark = 0
        compiler.connection.ops.limit_offset_sql = MagicMock(return_value="FIRST 10 ")

        with patch.object(
            compiler.__class__.__bases__[0],
            "as_sql",
            return_value=("SELECT * FROM test", []),
        ):
            sql, params = compiler.as_sql(with_limits=True)

        assert "SELECT" in sql
        assert "FIRST 10" in sql
        assert "FROM test" in sql

    def test_as_sql_with_offset_only(self, compiler, mock_query):
        """Test SQL generation with SKIP (offset) only."""
        mock_query.high_mark = None
        mock_query.low_mark = 5
        compiler.connection.ops.limit_offset_sql = MagicMock(return_value="SKIP 5 ")

        with patch.object(
            compiler.__class__.__bases__[0],
            "as_sql",
            return_value=("SELECT * FROM test", []),
        ):
            sql, params = compiler.as_sql(with_limits=True)

        assert "SELECT" in sql
        assert "SKIP 5" in sql
        assert "FROM test" in sql

    def test_as_sql_with_limit_and_offset(self, compiler, mock_query):
        """Test SQL generation with both FIRST and SKIP."""
        mock_query.high_mark = 15
        mock_query.low_mark = 5
        compiler.connection.ops.limit_offset_sql = MagicMock(
            return_value="FIRST 10 SKIP 5 "
        )

        with patch.object(
            compiler.__class__.__bases__[0],
            "as_sql",
            return_value=("SELECT * FROM test", []),
        ):
            sql, params = compiler.as_sql(with_limits=True)

        assert "SELECT" in sql
        assert "FIRST 10" in sql
        assert "SKIP 5" in sql
        assert "FROM test" in sql

    def test_as_sql_with_distinct(self, compiler, mock_query):
        """Test FIRST/SKIP placement after SELECT DISTINCT."""
        mock_query.high_mark = 10
        mock_query.low_mark = 0
        compiler.connection.ops.limit_offset_sql = MagicMock(return_value="FIRST 10 ")

        with patch.object(
            compiler.__class__.__bases__[0],
            "as_sql",
            return_value=("SELECT DISTINCT * FROM test", []),
        ):
            sql, params = compiler.as_sql(with_limits=True)

        assert sql.startswith("SELECT DISTINCT")
        assert "FIRST 10" in sql
        assert "FROM test" in sql

    def test_as_sql_preserves_params(self, compiler, mock_query):
        """Test that parameters are preserved."""
        mock_query.high_mark = 10
        mock_query.low_mark = 0
        compiler.connection.ops.limit_offset_sql = MagicMock(return_value="FIRST 10 ")

        with patch.object(
            compiler.__class__.__bases__[0],
            "as_sql",
            return_value=("SELECT * FROM test WHERE id = ?", [42]),
        ):
            sql, params = compiler.as_sql(with_limits=True)

        assert params == [42]

    def test_as_sql_without_limits_flag(self, compiler, mock_query):
        """Test SQL generation when with_limits=False."""
        mock_query.high_mark = 10
        mock_query.low_mark = 5

        with patch.object(
            compiler.__class__.__bases__[0],
            "as_sql",
            return_value=("SELECT * FROM test", []),
        ):
            sql, params = compiler.as_sql(with_limits=False)

        # with_limits=False should not add FIRST/SKIP
        assert "FIRST" not in sql
        assert "SKIP" not in sql

    def test_alias_refcount_restored(self, compiler, mock_query):
        """Test that alias_refcount is restored after exception."""
        mock_query.alias_refcount = {"original": 1}

        with patch.object(
            compiler.__class__.__bases__[0],
            "as_sql",
            side_effect=Exception("Test error"),
        ):
            with pytest.raises(Exception):
                compiler.as_sql()

        # alias_refcount should be restored
        assert mock_query.alias_refcount == {"original": 1}


class TestSQLInsertCompiler:
    """Test cases for SQLInsertCompiler class."""

    @pytest.fixture
    def mock_query(self):
        """Create a mock query object."""
        query = MagicMock()
        return query

    @pytest.fixture
    def insert_compiler(self, mock_connection, mock_query):
        """Create a SQLInsertCompiler instance."""
        from django_firebird.compiler import SQLInsertCompiler

        compiler = SQLInsertCompiler(mock_query, mock_connection, using="default")
        return compiler

    def test_as_sql_without_returning(self, insert_compiler):
        """Test INSERT without RETURNING clause."""
        insert_compiler.returning_fields = []

        with patch.object(
            insert_compiler.__class__.__bases__[0],
            "as_sql",
            return_value=[("INSERT INTO test VALUES (?)", [1])],
        ):
            result = insert_compiler.as_sql()

        assert result == [("INSERT INTO test VALUES (?)", [1])]

    def test_as_sql_with_returning(self, insert_compiler):
        """Test INSERT with RETURNING clause."""
        # Mock returning_fields
        field = MagicMock()
        field.column = "id"
        insert_compiler.returning_fields = [field]
        insert_compiler.connection.features.can_return_columns_from_insert = True
        insert_compiler.connection.ops.quote_name = lambda x: f'"{x}"'

        with patch.object(
            insert_compiler.__class__.__bases__[0],
            "as_sql",
            return_value=[("INSERT INTO test VALUES (?)", [1])],
        ):
            result = insert_compiler.as_sql()

        assert len(result) == 1
        sql, params = result[0]
        assert "RETURNING" in sql
        assert '"id"' in sql

    def test_as_sql_returning_multiple_fields(self, insert_compiler):
        """Test INSERT with multiple RETURNING fields."""
        field1 = MagicMock()
        field1.column = "id"
        field2 = MagicMock()
        field2.column = "created_at"
        insert_compiler.returning_fields = [field1, field2]
        insert_compiler.connection.features.can_return_columns_from_insert = True
        insert_compiler.connection.ops.quote_name = lambda x: f'"{x}"'

        with patch.object(
            insert_compiler.__class__.__bases__[0],
            "as_sql",
            return_value=[("INSERT INTO test VALUES (?)", [1])],
        ):
            result = insert_compiler.as_sql()

        sql, params = result[0]
        assert '"id"' in sql
        assert '"created_at"' in sql

    def test_as_sql_returning_not_duplicated(self, insert_compiler):
        """Test that RETURNING is not added if already present."""
        field = MagicMock()
        field.column = "id"
        insert_compiler.returning_fields = [field]
        insert_compiler.connection.features.can_return_columns_from_insert = True
        insert_compiler.connection.ops.quote_name = lambda x: f'"{x}"'

        with patch.object(
            insert_compiler.__class__.__bases__[0],
            "as_sql",
            return_value=[("INSERT INTO test VALUES (?) RETURNING id", [1])],
        ):
            result = insert_compiler.as_sql()

        sql, params = result[0]
        # Should only have one RETURNING
        assert sql.upper().count("RETURNING") == 1

    def test_as_sql_bulk_insert(self, insert_compiler):
        """Test bulk INSERT with RETURNING."""
        field = MagicMock()
        field.column = "id"
        insert_compiler.returning_fields = [field]
        insert_compiler.connection.features.can_return_columns_from_insert = True
        insert_compiler.connection.ops.quote_name = lambda x: f'"{x}"'

        with patch.object(
            insert_compiler.__class__.__bases__[0],
            "as_sql",
            return_value=[
                ("INSERT INTO test VALUES (?)", [1]),
                ("INSERT INTO test VALUES (?)", [2]),
            ],
        ):
            result = insert_compiler.as_sql()

        assert len(result) == 2
        for sql, _params in result:
            assert "RETURNING" in sql


class TestSQLDeleteCompiler:
    """Test cases for SQLDeleteCompiler class."""

    def test_inherits_from_base(self):
        """Test that SQLDeleteCompiler inherits from base class."""
        from django.db.models.sql import compiler

        from django_firebird.compiler import SQLDeleteCompiler

        assert issubclass(SQLDeleteCompiler, compiler.SQLDeleteCompiler)


class TestSQLUpdateCompiler:
    """Test cases for SQLUpdateCompiler class."""

    def test_inherits_from_base(self):
        """Test that SQLUpdateCompiler inherits from base class."""
        from django.db.models.sql import compiler

        from django_firebird.compiler import SQLUpdateCompiler

        assert issubclass(SQLUpdateCompiler, compiler.SQLUpdateCompiler)


class TestSQLAggregateCompiler:
    """Test cases for SQLAggregateCompiler class."""

    def test_inherits_from_base(self):
        """Test that SQLAggregateCompiler inherits from base class."""
        from django.db.models.sql import compiler

        from django_firebird.compiler import SQLAggregateCompiler

        assert issubclass(SQLAggregateCompiler, compiler.SQLAggregateCompiler)
