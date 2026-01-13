"""
Tests for DatabaseCreation class.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestDatabaseCreation:
    """Test cases for DatabaseCreation methods."""

    @pytest.fixture
    def creation(self, mock_connection):
        """Create DatabaseCreation instance with mock connection."""
        from django_firebird.creation import DatabaseCreation

        return DatabaseCreation(mock_connection)

    # =========================================================================
    # _quote_name tests
    # =========================================================================

    def test_quote_name(self, creation):
        """Test _quote_name delegates to ops.quote_name."""
        creation.connection.ops.quote_name = MagicMock(return_value='"test"')

        result = creation._quote_name("test")

        assert result == '"test"'
        creation.connection.ops.quote_name.assert_called_once_with("test")

    # =========================================================================
    # _get_test_db_params tests
    # =========================================================================

    def test_get_test_db_params_defaults(self, creation):
        """Test default test database parameters."""
        creation.connection.settings_dict = {
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": None,
            "PORT": None,
            "OPTIONS": {},
            "TEST": {},
        }

        params = creation._get_test_db_params()

        assert params["user"] == "SYSDBA"
        assert params["password"] == "masterkey"
        assert params["page_size"] == 8192
        assert params["charset"] == "UTF8"

    def test_get_test_db_params_custom(self, creation):
        """Test custom test database parameters."""
        creation.connection.settings_dict = {
            "USER": "custom_user",
            "PASSWORD": "custom_pass",
            "HOST": "localhost",
            "PORT": "3050",
            "OPTIONS": {"charset": "WIN1252"},
            "TEST": {"PAGE_SIZE": 16384},
        }

        params = creation._get_test_db_params()

        assert params["user"] == "custom_user"
        assert params["password"] == "custom_pass"
        assert params["host"] == "localhost"
        assert params["port"] == "3050"
        assert params["page_size"] == 16384
        assert params["charset"] == "WIN1252"

    # =========================================================================
    # _get_test_db_name tests
    # =========================================================================

    def test_get_test_db_name_from_test_settings(self, creation):
        """Test getting test database name from TEST settings."""
        creation.connection.settings_dict = {
            "NAME": "/path/to/prod.fdb",
            "TEST": {"NAME": "/tmp/custom_test.fdb"},
        }

        result = creation._get_test_db_name()

        assert result == "/tmp/custom_test.fdb"

    def test_get_test_db_name_generated(self, creation):
        """Test generating test database name from production name."""
        creation.connection.settings_dict = {
            "NAME": "/path/to/mydb.fdb",
            "TEST": {},
        }

        result = creation._get_test_db_name()

        assert result == "/tmp/test_mydb.fdb"

    def test_get_test_db_name_no_extension(self, creation):
        """Test generating test database name without .fdb extension."""
        creation.connection.settings_dict = {
            "NAME": "/path/to/mydb",
            "TEST": {},
        }

        result = creation._get_test_db_name()

        assert result == "/tmp/test_mydb.fdb"

    # =========================================================================
    # _create_test_db tests
    # =========================================================================

    def test_create_test_db_keepdb(self, creation):
        """Test _create_test_db with keepdb=True."""
        creation.connection.settings_dict = {
            "NAME": "/path/to/prod.fdb",
            "TEST": {"NAME": "/tmp/test.fdb"},
        }

        with patch.object(creation, "_get_test_db_params"):
            result = creation._create_test_db(
                verbosity=0, autoclobber=False, keepdb=True
            )

        assert result == "/tmp/test.fdb"

    @patch("os.path.exists")
    @patch("os.remove")
    def test_create_test_db_existing_autoclobber(
        self, mock_remove, mock_exists, creation
    ):
        """Test _create_test_db removes existing database with autoclobber."""
        mock_exists.return_value = True
        creation.connection.settings_dict = {
            "NAME": "/path/to/prod.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": None,
            "PORT": None,
            "OPTIONS": {},
            "TEST": {"NAME": "/tmp/test.fdb"},
        }

        with patch.object(creation, "_create_database"):
            creation._create_test_db(verbosity=0, autoclobber=True, keepdb=False)

        mock_remove.assert_called_once_with("/tmp/test.fdb")

    @patch("os.path.exists")
    def test_create_test_db_new_database(self, mock_exists, creation):
        """Test _create_test_db creates new database."""
        mock_exists.return_value = False
        creation.connection.settings_dict = {
            "NAME": "/path/to/prod.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": None,
            "PORT": None,
            "OPTIONS": {},
            "TEST": {"NAME": "/tmp/test.fdb"},
        }

        with patch.object(creation, "_create_database") as mock_create:
            creation._create_test_db(verbosity=0, autoclobber=False, keepdb=False)

        mock_create.assert_called_once()

    # =========================================================================
    # _create_database tests
    # =========================================================================

    def test_create_database_local(self, creation):
        """Test creating local database."""
        with patch("firebird.driver.create_database") as mock_create:
            creation._create_database(
                "/tmp/test.fdb",
                {
                    "user": "SYSDBA",
                    "password": "masterkey",
                    "page_size": 8192,
                },
            )

        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["database"] == "/tmp/test.fdb"
        assert call_kwargs["user"] == "SYSDBA"
        assert call_kwargs["password"] == "masterkey"
        assert call_kwargs["page_size"] == 8192

    def test_create_database_remote_with_host(self, creation):
        """Test creating remote database with host."""
        with patch("firebird.driver.create_database") as mock_create:
            creation._create_database(
                "/tmp/test.fdb",
                {
                    "host": "server",
                    "user": "SYSDBA",
                    "password": "masterkey",
                    "page_size": 8192,
                },
            )

        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["database"] == "server:/tmp/test.fdb"

    def test_create_database_remote_with_host_and_port(self, creation):
        """Test creating remote database with host and port."""
        with patch("firebird.driver.create_database") as mock_create:
            creation._create_database(
                "/tmp/test.fdb",
                {
                    "host": "server",
                    "port": "3050",
                    "user": "SYSDBA",
                    "password": "masterkey",
                    "page_size": 8192,
                },
            )

        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["database"] == "server/3050:/tmp/test.fdb"

    # =========================================================================
    # _destroy_test_db tests
    # =========================================================================

    @patch("os.path.exists")
    @patch("os.remove")
    def test_destroy_test_db(self, mock_remove, mock_exists, creation):
        """Test _destroy_test_db removes database file."""
        mock_exists.return_value = True
        creation.connection.close = MagicMock()

        creation._destroy_test_db("/tmp/test.fdb", verbosity=0)

        creation.connection.close.assert_called_once()
        mock_remove.assert_called_once_with("/tmp/test.fdb")

    @patch("os.path.exists")
    @patch("os.remove")
    def test_destroy_test_db_not_exists(self, mock_remove, mock_exists, creation):
        """Test _destroy_test_db when database doesn't exist."""
        mock_exists.return_value = False
        creation.connection.close = MagicMock()

        creation._destroy_test_db("/tmp/test.fdb", verbosity=0)

        creation.connection.close.assert_called_once()
        mock_remove.assert_not_called()

    # =========================================================================
    # _clone_test_db tests
    # =========================================================================

    def test_clone_test_db_not_supported(self, creation):
        """Test _clone_test_db raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            creation._clone_test_db(suffix="1", verbosity=0)

        assert "not supported for Firebird" in str(exc_info.value)
