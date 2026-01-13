"""
Tests for DatabaseClient class.
"""

import signal
from unittest.mock import patch

import pytest


class TestDatabaseClient:
    """Test cases for DatabaseClient class."""

    @pytest.fixture
    def client(self, mock_connection):
        """Create DatabaseClient instance."""
        from django_firebird.client import DatabaseClient

        return DatabaseClient(mock_connection)

    # =========================================================================
    # executable_name tests
    # =========================================================================

    def test_executable_name(self):
        """Test default executable name is isql-fb."""
        from django_firebird.client import DatabaseClient

        assert DatabaseClient.executable_name == "isql-fb"

    # =========================================================================
    # settings_to_cmd_args_env tests
    # =========================================================================

    def test_settings_to_cmd_args_env_local(self):
        """Test command args for local database."""
        from django_firebird.client import DatabaseClient

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": None,
            "PORT": None,
            "OPTIONS": {},
        }

        args, env = DatabaseClient.settings_to_cmd_args_env(settings, [])

        assert args[0] == "isql-fb"
        assert "/path/to/database.fdb" in args
        assert "-user" in args
        assert "SYSDBA" in args
        assert "-password" in args
        assert "masterkey" in args
        assert "-charset" in args
        assert "UTF8" in args
        assert env is None

    def test_settings_to_cmd_args_env_remote_host(self):
        """Test command args for remote database with host."""
        from django_firebird.client import DatabaseClient

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": "server",
            "PORT": None,
            "OPTIONS": {},
        }

        args, env = DatabaseClient.settings_to_cmd_args_env(settings, [])

        assert "server:/path/to/database.fdb" in args

    def test_settings_to_cmd_args_env_remote_host_port(self):
        """Test command args for remote database with host and port."""
        from django_firebird.client import DatabaseClient

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": "server",
            "PORT": "3050",
            "OPTIONS": {},
        }

        args, env = DatabaseClient.settings_to_cmd_args_env(settings, [])

        assert "server/3050:/path/to/database.fdb" in args

    def test_settings_to_cmd_args_env_custom_charset(self):
        """Test command args with custom charset."""
        from django_firebird.client import DatabaseClient

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": None,
            "PORT": None,
            "OPTIONS": {"charset": "WIN1252"},
        }

        args, env = DatabaseClient.settings_to_cmd_args_env(settings, [])

        charset_idx = args.index("-charset")
        assert args[charset_idx + 1] == "WIN1252"

    def test_settings_to_cmd_args_env_no_user(self):
        """Test command args without user."""
        from django_firebird.client import DatabaseClient

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": None,
            "PASSWORD": None,
            "HOST": None,
            "PORT": None,
            "OPTIONS": {},
        }

        args, env = DatabaseClient.settings_to_cmd_args_env(settings, [])

        assert "-user" not in args
        assert "-password" not in args

    def test_settings_to_cmd_args_env_extra_parameters(self):
        """Test command args with extra parameters."""
        from django_firebird.client import DatabaseClient

        settings = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": None,
            "PORT": None,
            "OPTIONS": {},
        }

        args, env = DatabaseClient.settings_to_cmd_args_env(settings, ["-echo"])

        assert "-echo" in args

    # =========================================================================
    # runshell tests
    # =========================================================================

    @patch("subprocess.run")
    def test_runshell(self, mock_run, client):
        """Test runshell calls subprocess.run."""
        client.connection.settings_dict = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": None,
            "PORT": None,
            "OPTIONS": {},
        }

        client.runshell([])

        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[1]["check"] is True

    @patch("subprocess.run")
    def test_runshell_with_parameters(self, mock_run, client):
        """Test runshell passes parameters."""
        client.connection.settings_dict = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": None,
            "PORT": None,
            "OPTIONS": {},
        }

        client.runshell(["-echo", "-bail"])

        call_args = mock_run.call_args[0][0]
        assert "-echo" in call_args
        assert "-bail" in call_args

    @patch("subprocess.run")
    @patch("signal.getsignal")
    @patch("signal.signal")
    def test_runshell_sigint_handling(
        self, mock_signal, mock_getsignal, mock_run, client
    ):
        """Test runshell handles SIGINT properly."""
        mock_getsignal.return_value = signal.SIG_DFL
        client.connection.settings_dict = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": None,
            "PORT": None,
            "OPTIONS": {},
        }

        client.runshell([])

        # Should ignore SIGINT before running
        assert mock_signal.call_count >= 2
        # First call should ignore SIGINT
        first_call = mock_signal.call_args_list[0]
        assert first_call[0][0] == signal.SIGINT
        assert first_call[0][1] == signal.SIG_IGN
        # Last call should restore original handler
        last_call = mock_signal.call_args_list[-1]
        assert last_call[0][0] == signal.SIGINT

    @patch("subprocess.run")
    @patch("signal.getsignal")
    @patch("signal.signal")
    def test_runshell_restores_sigint_on_exception(
        self, mock_signal, mock_getsignal, mock_run, client
    ):
        """Test runshell restores SIGINT handler even on exception."""
        mock_getsignal.return_value = signal.SIG_DFL
        mock_run.side_effect = Exception("Test error")
        client.connection.settings_dict = {
            "NAME": "/path/to/database.fdb",
            "USER": "SYSDBA",
            "PASSWORD": "masterkey",
            "HOST": None,
            "PORT": None,
            "OPTIONS": {},
        }

        with pytest.raises(Exception):
            client.runshell([])

        # Signal should still be restored
        last_call = mock_signal.call_args_list[-1]
        assert last_call[0][0] == signal.SIGINT
