"""
Tests for Firebird database backend base module.
"""

from unittest.mock import MagicMock

import pytest


class TestCursorWrapper:
    """Test cases for CursorWrapper."""

    def setup_method(self):
        """Set up test fixtures."""
        from django_firebird.base import CursorWrapper

        self.mock_cursor = MagicMock()
        self.wrapper = CursorWrapper(self.mock_cursor)

    def test_execute_converts_placeholders(self):
        """Test that %s placeholders are converted to ?."""
        sql = "SELECT * FROM users WHERE id = %s AND name = %s"
        params = [1, "test"]

        self.wrapper.execute(sql, params)

        self.mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM users WHERE id = ? AND name = ?", [1, "test"]
        )

    def test_execute_without_params(self):
        """Test execute without parameters."""
        sql = "SELECT * FROM users"

        self.wrapper.execute(sql)

        self.mock_cursor.execute.assert_called_once_with(sql, [])

    def test_execute_with_none_params(self):
        """Test execute with None params."""
        sql = "SELECT * FROM users"

        self.wrapper.execute(sql, None)

        self.mock_cursor.execute.assert_called_once_with(sql, [])

    def test_executemany_converts_placeholders(self):
        """Test that executemany converts placeholders."""
        sql = "INSERT INTO users (id, name) VALUES (%s, %s)"
        params = [[1, "a"], [2, "b"]]

        self.wrapper.executemany(sql, params)

        self.mock_cursor.executemany.assert_called_once_with(
            "INSERT INTO users (id, name) VALUES (?, ?)", params
        )

    def test_callproc_with_params(self):
        """Test calling stored procedure with parameters."""
        self.wrapper.callproc("MY_PROCEDURE", [1, "test"])

        self.mock_cursor.execute.assert_called_once_with(
            'EXECUTE PROCEDURE "MY_PROCEDURE"(?, ?)', [1, "test"]
        )

    def test_callproc_without_params(self):
        """Test calling stored procedure without parameters."""
        self.wrapper.callproc("MY_PROCEDURE")

        self.mock_cursor.execute.assert_called_once_with(
            'EXECUTE PROCEDURE "MY_PROCEDURE"'
        )

    def test_callproc_with_empty_params(self):
        """Test calling stored procedure with empty params list."""
        self.wrapper.callproc("MY_PROCEDURE", [])

        self.mock_cursor.execute.assert_called_once_with(
            'EXECUTE PROCEDURE "MY_PROCEDURE"'
        )

    def test_callproc_escapes_quotes(self):
        """Test that callproc escapes double quotes to prevent SQL injection."""
        self.wrapper.callproc('evil"; DROP TABLE users; --')

        # The double quote should be escaped by doubling it
        self.mock_cursor.execute.assert_called_once_with(
            'EXECUTE PROCEDURE "evil""; DROP TABLE users; --"'
        )

    def test_delegate_fetchone(self):
        """Test that fetchone is delegated to underlying cursor."""
        self.mock_cursor.fetchone.return_value = (1, "test")

        result = self.wrapper.fetchone()

        assert result == (1, "test")
        self.mock_cursor.fetchone.assert_called_once()

    def test_delegate_fetchall(self):
        """Test that fetchall is delegated to underlying cursor."""
        self.mock_cursor.fetchall.return_value = [(1, "a"), (2, "b")]

        result = self.wrapper.fetchall()

        assert result == [(1, "a"), (2, "b")]
        self.mock_cursor.fetchall.assert_called_once()

    def test_delegate_description(self):
        """Test that description is delegated."""
        self.mock_cursor.description = [("id", int), ("name", str)]

        assert self.wrapper.description == [("id", int), ("name", str)]

    def test_iterator(self):
        """Test cursor iterator protocol."""
        self.mock_cursor.__iter__ = MagicMock(return_value=iter([(1,), (2,)]))

        result = list(self.wrapper)

        assert result == [(1,), (2,)]

    def test_context_manager(self):
        """Test cursor context manager protocol."""
        with self.wrapper as cursor:
            assert cursor is self.wrapper

        self.mock_cursor.close.assert_called_once()


class TestDatabaseWrapper:
    """Test cases for DatabaseWrapper."""

    @pytest.fixture
    def mock_database_wrapper(self):
        """Create a mock DatabaseWrapper instance."""
        from django_firebird.base import DatabaseWrapper

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": "",
            "PORT": "",
            "OPTIONS": {},
        }

        wrapper = DatabaseWrapper(settings)
        wrapper.connection = MagicMock()
        wrapper._firebird_version = (5, 0)
        return wrapper

    # =========================================================================
    # Connection parameters
    # =========================================================================

    def test_get_connection_params_local_database(self):
        """Test connection params for local database."""
        from django_firebird.base import DatabaseWrapper

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": "",
            "PORT": "",
            "OPTIONS": {},
        }

        wrapper = DatabaseWrapper(settings)
        params = wrapper.get_connection_params()

        assert params["database"] == "/path/to/database.fdb"
        assert params["user"] == "SYSDBA"
        assert params["password"] == "masterkey"
        assert params["charset"] == "UTF8"

    def test_get_connection_params_remote_database(self):
        """Test connection params for remote database."""
        from django_firebird.base import DatabaseWrapper

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": "localhost",
            "PORT": "",
            "OPTIONS": {},
        }

        wrapper = DatabaseWrapper(settings)
        params = wrapper.get_connection_params()

        assert params["database"] == "localhost:/path/to/database.fdb"

    def test_get_connection_params_with_port(self):
        """Test connection params with custom port."""
        from django_firebird.base import DatabaseWrapper

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": "localhost",
            "PORT": "3050",
            "OPTIONS": {},
        }

        wrapper = DatabaseWrapper(settings)
        params = wrapper.get_connection_params()

        assert params["database"] == "localhost/3050:/path/to/database.fdb"

    def test_get_connection_params_custom_charset(self):
        """Test connection params with custom charset."""
        from django_firebird.base import DatabaseWrapper

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": "",
            "PORT": "",
            "OPTIONS": {"charset": "ISO8859_1"},
        }

        wrapper = DatabaseWrapper(settings)
        params = wrapper.get_connection_params()

        assert params["charset"] == "ISO8859_1"

    def test_get_connection_params_missing_name(self):
        """Test that missing NAME raises ImproperlyConfigured."""
        from django.core.exceptions import ImproperlyConfigured

        from django_firebird.base import DatabaseWrapper

        settings = {
            "NAME": "",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": "",
            "PORT": "",
            "OPTIONS": {},
        }

        wrapper = DatabaseWrapper(settings)

        with pytest.raises(ImproperlyConfigured):
            wrapper.get_connection_params()

    # =========================================================================
    # Data types
    # =========================================================================

    def test_data_types_boolean_firebird_25(self):
        """Test BooleanField uses smallint in Firebird 2.5."""
        from django_firebird.base import DatabaseWrapper

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": "",
            "PORT": "",
            "OPTIONS": {},
        }

        wrapper = DatabaseWrapper(settings)
        wrapper.connection = MagicMock()
        wrapper._firebird_version = (2, 5)

        # Clear cached property
        if "data_types" in wrapper.__dict__:
            del wrapper.__dict__["data_types"]
        if "features" in wrapper.__dict__:
            del wrapper.__dict__["features"]

        assert wrapper.data_types["BooleanField"] == "smallint"

    def test_data_types_boolean_firebird_30(self):
        """Test BooleanField uses native boolean in Firebird 3.0+."""
        from django_firebird.base import DatabaseWrapper

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": "",
            "PORT": "",
            "OPTIONS": {},
        }

        wrapper = DatabaseWrapper(settings)
        wrapper.connection = MagicMock()
        wrapper._firebird_version = (3, 0)

        # Clear cached property
        if "data_types" in wrapper.__dict__:
            del wrapper.__dict__["data_types"]
        if "features" in wrapper.__dict__:
            del wrapper.__dict__["features"]

        assert wrapper.data_types["BooleanField"] == "boolean"

    # =========================================================================
    # Transaction methods
    # =========================================================================

    def test_commit_with_wrap_database_errors(self, mock_database_wrapper):
        """Test _commit uses wrap_database_errors."""
        mock_database_wrapper._commit()

        mock_database_wrapper.connection.commit.assert_called_once()

    def test_rollback_with_wrap_database_errors(self, mock_database_wrapper):
        """Test _rollback uses wrap_database_errors."""
        mock_database_wrapper._rollback()

        mock_database_wrapper.connection.rollback.assert_called_once()

    def test_close_with_wrap_database_errors(self, mock_database_wrapper):
        """Test _close uses wrap_database_errors."""
        mock_database_wrapper._close()

        mock_database_wrapper.connection.close.assert_called_once()

    def test_commit_no_connection(self):
        """Test _commit does nothing when no connection."""
        from django_firebird.base import DatabaseWrapper

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": "",
            "PORT": "",
            "OPTIONS": {},
        }

        wrapper = DatabaseWrapper(settings)
        wrapper.connection = None

        # Should not raise
        wrapper._commit()

    def test_set_autocommit_commits_pending(self, mock_database_wrapper):
        """Test _set_autocommit commits pending transaction when active."""
        # Set up main_transaction as active
        mock_database_wrapper.connection.main_transaction = MagicMock()
        mock_database_wrapper.connection.main_transaction.is_active.return_value = True

        mock_database_wrapper._set_autocommit(True)

        mock_database_wrapper.connection.commit.assert_called_once()

    def test_set_autocommit_no_commit_when_no_transaction(self, mock_database_wrapper):
        """Test _set_autocommit doesn't commit when no active transaction."""
        # main_transaction is None (no transaction started)
        mock_database_wrapper.connection.main_transaction = None

        mock_database_wrapper._set_autocommit(True)

        mock_database_wrapper.connection.commit.assert_not_called()

    def test_set_autocommit_no_commit_when_inactive(self, mock_database_wrapper):
        """Test _set_autocommit doesn't commit when transaction is inactive."""
        mock_database_wrapper.connection.main_transaction = MagicMock()
        mock_database_wrapper.connection.main_transaction.is_active.return_value = False

        mock_database_wrapper._set_autocommit(True)

        mock_database_wrapper.connection.commit.assert_not_called()

    def test_set_autocommit_false_no_commit(self, mock_database_wrapper):
        """Test _set_autocommit(False) doesn't commit."""
        mock_database_wrapper._set_autocommit(False)

        mock_database_wrapper.connection.commit.assert_not_called()

    # =========================================================================
    # Cursor creation
    # =========================================================================

    def test_create_cursor(self, mock_database_wrapper):
        """Test create_cursor returns CursorWrapper."""
        from django_firebird.base import CursorWrapper

        mock_cursor = MagicMock()
        mock_database_wrapper.connection.cursor.return_value = mock_cursor

        cursor = mock_database_wrapper.create_cursor()

        assert isinstance(cursor, CursorWrapper)

    def test_make_debug_cursor(self, mock_database_wrapper):
        """Test make_debug_cursor returns CursorDebugWrapper."""
        from django.db.backends.utils import CursorDebugWrapper

        mock_cursor = MagicMock()

        debug_cursor = mock_database_wrapper.make_debug_cursor(mock_cursor)

        assert isinstance(debug_cursor, CursorDebugWrapper)

    # =========================================================================
    # Connection usability
    # =========================================================================

    def test_is_usable_true(self, mock_database_wrapper):
        """Test is_usable returns True for working connection."""
        mock_cursor = MagicMock()
        mock_database_wrapper.connection.cursor.return_value = mock_cursor

        assert mock_database_wrapper.is_usable() is True

    def test_is_usable_false_on_error(self, mock_database_wrapper):
        """Test is_usable returns False when query fails."""
        mock_database_wrapper.connection.cursor.side_effect = Exception(
            "Connection lost"
        )

        assert mock_database_wrapper.is_usable() is False

    # =========================================================================
    # Timezone
    # =========================================================================

    def test_ensure_timezone_firebird_40(self):
        """Test ensure_timezone sets timezone in Firebird 4.0+."""
        from django_firebird.base import DatabaseWrapper

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": "",
            "PORT": "",
            "OPTIONS": {},
            "TIME_ZONE": "America/New_York",
        }

        wrapper = DatabaseWrapper(settings)
        wrapper.connection = MagicMock()
        wrapper._firebird_version = (4, 0)

        # Clear cached properties
        if "features" in wrapper.__dict__:
            del wrapper.__dict__["features"]

        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        wrapper.connection.cursor.return_value = mock_cursor

        wrapper.ensure_timezone()

        mock_cursor.execute.assert_called_once_with(
            "SET TIME ZONE ?", ["America/New_York"]
        )

    def test_ensure_timezone_no_tz_setting(self):
        """Test ensure_timezone does nothing without TIME_ZONE setting."""
        from django_firebird.base import DatabaseWrapper

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": "",
            "PORT": "",
            "OPTIONS": {},
        }

        wrapper = DatabaseWrapper(settings)
        wrapper.connection = MagicMock()
        wrapper._firebird_version = (4, 0)

        # Clear cached properties
        if "features" in wrapper.__dict__:
            del wrapper.__dict__["features"]

        wrapper.ensure_timezone()

        wrapper.connection.cursor.assert_not_called()

    # =========================================================================
    # Version detection
    # =========================================================================

    def test_firebird_version_property(self, mock_database_wrapper):
        """Test firebird_version returns version tuple."""
        assert mock_database_wrapper.firebird_version == (5, 0)

    def test_get_database_version(self, mock_database_wrapper):
        """Test get_database_version returns firebird_version."""
        assert mock_database_wrapper.get_database_version() == (5, 0)

    # =========================================================================
    # Operators and patterns
    # =========================================================================

    def test_operators_defined(self):
        """Test SQL operators are defined."""
        from django_firebird.base import DatabaseWrapper

        assert "exact" in DatabaseWrapper.operators
        assert "contains" in DatabaseWrapper.operators
        assert "startswith" in DatabaseWrapper.operators
        assert "regex" in DatabaseWrapper.operators

    def test_pattern_ops_defined(self):
        """Test pattern operations are defined."""
        from django_firebird.base import DatabaseWrapper

        assert "contains" in DatabaseWrapper.pattern_ops
        assert "icontains" in DatabaseWrapper.pattern_ops
        assert "startswith" in DatabaseWrapper.pattern_ops
        assert "endswith" in DatabaseWrapper.pattern_ops

    def test_check_constraints_defined(self):
        """Test check constraints for positive fields."""
        from django_firebird.base import DatabaseWrapper

        assert "PositiveIntegerField" in DatabaseWrapper.data_type_check_constraints
        assert "PositiveBigIntegerField" in DatabaseWrapper.data_type_check_constraints
        assert (
            "PositiveSmallIntegerField" in DatabaseWrapper.data_type_check_constraints
        )
