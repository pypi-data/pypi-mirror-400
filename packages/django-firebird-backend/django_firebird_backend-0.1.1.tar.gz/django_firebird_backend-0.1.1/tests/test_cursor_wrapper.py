"""
Tests for CursorWrapper class.
"""

from unittest.mock import MagicMock

import pytest


class TestCursorWrapper:
    """Test cases for CursorWrapper placeholder conversion."""

    @pytest.fixture
    def cursor_wrapper(self):
        """Create CursorWrapper with mock cursor."""
        from django_firebird.base import CursorWrapper

        mock_cursor = MagicMock()
        return CursorWrapper(mock_cursor), mock_cursor

    def test_execute_no_params(self, cursor_wrapper):
        """Test execute without parameters."""
        wrapper, mock = cursor_wrapper

        wrapper.execute("SELECT * FROM table")

        mock.execute.assert_called_once_with("SELECT * FROM table", [])

    def test_execute_single_param(self, cursor_wrapper):
        """Test execute with single parameter converts %s to ?."""
        wrapper, mock = cursor_wrapper

        wrapper.execute("SELECT * FROM table WHERE id = %s", [1])

        mock.execute.assert_called_once_with("SELECT * FROM table WHERE id = ?", [1])

    def test_execute_multiple_params(self, cursor_wrapper):
        """Test execute with multiple parameters."""
        wrapper, mock = cursor_wrapper

        wrapper.execute("SELECT * FROM table WHERE id = %s AND name = %s", [1, "test"])

        mock.execute.assert_called_once_with(
            "SELECT * FROM table WHERE id = ? AND name = ?", [1, "test"]
        )

    def test_execute_no_conversion_without_params(self, cursor_wrapper):
        """Test that SQL is not modified when params is None."""
        wrapper, mock = cursor_wrapper

        # SQL with %s but no params - should not convert
        wrapper.execute("SELECT '%s' FROM table")

        mock.execute.assert_called_once_with("SELECT '%s' FROM table", [])

    def test_execute_preserves_percent_in_like(self, cursor_wrapper):
        """Test that % in LIKE patterns is preserved when params exist."""
        wrapper, mock = cursor_wrapper

        wrapper.execute("SELECT * FROM table WHERE name LIKE %s", ["%test%"])

        # The %s should become ?, but the LIKE pattern in params stays
        mock.execute.assert_called_once_with(
            "SELECT * FROM table WHERE name LIKE ?", ["%test%"]
        )

    def test_execute_complex_query(self, cursor_wrapper):
        """Test complex query with multiple placeholders."""
        wrapper, mock = cursor_wrapper

        sql = """
            SELECT t1.id, t2.name
            FROM table1 t1
            JOIN table2 t2 ON t1.fk = t2.id
            WHERE t1.status = %s
            AND t2.created > %s
            AND t1.value BETWEEN %s AND %s
            ORDER BY t1.id
        """
        params = ["active", "2024-01-01", 100, 500]

        wrapper.execute(sql, params)

        expected_sql = sql.replace("%s", "?")
        mock.execute.assert_called_once_with(expected_sql, params)

    def test_executemany(self, cursor_wrapper):
        """Test executemany converts placeholders."""
        wrapper, mock = cursor_wrapper

        wrapper.executemany(
            "INSERT INTO table (a, b) VALUES (%s, %s)", [(1, "a"), (2, "b"), (3, "c")]
        )

        mock.executemany.assert_called_once_with(
            "INSERT INTO table (a, b) VALUES (?, ?)", [(1, "a"), (2, "b"), (3, "c")]
        )

    def test_fetchone_delegation(self, cursor_wrapper):
        """Test fetchone is delegated to underlying cursor."""
        wrapper, mock = cursor_wrapper
        mock.fetchone.return_value = (1, "test")

        result = wrapper.fetchone()

        assert result == (1, "test")
        mock.fetchone.assert_called_once()

    def test_fetchall_delegation(self, cursor_wrapper):
        """Test fetchall is delegated to underlying cursor."""
        wrapper, mock = cursor_wrapper
        mock.fetchall.return_value = [(1, "a"), (2, "b")]

        result = wrapper.fetchall()

        assert result == [(1, "a"), (2, "b")]
        mock.fetchall.assert_called_once()

    def test_fetchmany_delegation(self, cursor_wrapper):
        """Test fetchmany is delegated to underlying cursor."""
        wrapper, mock = cursor_wrapper
        mock.fetchmany.return_value = [(1, "a")]

        result = wrapper.fetchmany(1)

        assert result == [(1, "a")]
        mock.fetchmany.assert_called_once_with(1)

    def test_close_delegation(self, cursor_wrapper):
        """Test close is delegated to underlying cursor."""
        wrapper, mock = cursor_wrapper

        wrapper.close()

        mock.close.assert_called_once()

    def test_description_delegation(self, cursor_wrapper):
        """Test description property is delegated."""
        wrapper, mock = cursor_wrapper
        mock.description = [("col1", int), ("col2", str)]

        assert wrapper.description == [("col1", int), ("col2", str)]

    def test_rowcount_delegation(self, cursor_wrapper):
        """Test rowcount property is delegated."""
        wrapper, mock = cursor_wrapper
        mock.rowcount = 5

        assert wrapper.rowcount == 5

    def test_iteration(self, cursor_wrapper):
        """Test cursor iteration."""
        wrapper, mock = cursor_wrapper
        mock.__iter__ = MagicMock(return_value=iter([(1,), (2,), (3,)]))

        results = list(wrapper)

        assert results == [(1,), (2,), (3,)]

    def test_context_manager(self, cursor_wrapper):
        """Test cursor as context manager."""
        wrapper, mock = cursor_wrapper

        with wrapper as ctx:
            assert ctx is wrapper

        mock.close.assert_called_once()

    def test_empty_params_list(self, cursor_wrapper):
        """Test execute with empty params list."""
        wrapper, mock = cursor_wrapper

        wrapper.execute("SELECT * FROM table", [])

        mock.execute.assert_called_once_with("SELECT * FROM table", [])

    def test_none_in_params(self, cursor_wrapper):
        """Test execute with None value in params."""
        wrapper, mock = cursor_wrapper

        wrapper.execute("INSERT INTO table (a, b) VALUES (%s, %s)", [1, None])

        mock.execute.assert_called_once_with(
            "INSERT INTO table (a, b) VALUES (?, ?)", [1, None]
        )
