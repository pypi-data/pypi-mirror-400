"""
Firebird database creation for Django.

Handles creating and destroying test databases.
"""

import os

from django.db.backends.base.creation import BaseDatabaseCreation


class DatabaseCreation(BaseDatabaseCreation):
    """Firebird database creation class."""

    def _quote_name(self, name):
        """Quote a database name."""
        return self.connection.ops.quote_name(name)

    def _get_test_db_params(self):
        """Return parameters for test database creation."""
        settings = self.connection.settings_dict
        test_settings = settings.get("TEST", {})

        params = {
            "user": settings.get("USER", "SYSDBA"),
            "password": settings.get("PASSWORD", "masterkey"),
            "host": settings.get("HOST"),
            "port": settings.get("PORT"),
            "page_size": test_settings.get("PAGE_SIZE", 8192),
            "charset": settings.get("OPTIONS", {}).get("charset", "UTF8"),
        }

        return params

    def _get_test_db_name(self):
        """
        Return the name of the test database.
        """
        settings = self.connection.settings_dict
        test_settings = settings.get("TEST", {})

        if test_settings.get("NAME"):
            return test_settings["NAME"]

        # Generate test database name
        db_name = settings.get("NAME", "")
        base_name = os.path.splitext(os.path.basename(db_name))[0]
        return f"/tmp/test_{base_name}.fdb"

    def _create_test_db(self, verbosity, autoclobber, keepdb=False):
        """
        Create a test database.
        """
        test_db_name = self._get_test_db_name()
        params = self._get_test_db_params()

        if keepdb:
            return test_db_name

        # Remove existing database if exists
        if os.path.exists(test_db_name):
            if autoclobber:
                os.remove(test_db_name)
            else:
                confirm = input(
                    f"Database {test_db_name} already exists. "
                    "Type 'yes' to delete and recreate it: "
                )
                if confirm != "yes":
                    raise Exception("Database creation cancelled.")
                os.remove(test_db_name)

        # Create the database
        self._create_database(test_db_name, params)

        return test_db_name

    def _create_database(self, db_name, params):
        """Create a new Firebird database."""
        from firebird.driver import create_database

        dsn = db_name
        if params.get("host"):
            if params.get("port"):
                dsn = f"{params['host']}/{params['port']}:{db_name}"
            else:
                dsn = f"{params['host']}:{db_name}"

        create_database(
            database=dsn,
            user=params.get("user", "SYSDBA"),
            password=params.get("password", "masterkey"),
            page_size=params.get("page_size", 8192),
        )

    def _destroy_test_db(self, test_db_name, verbosity):
        """
        Destroy the test database.
        """
        # Close all connections
        self.connection.close()

        # Remove the database file
        if os.path.exists(test_db_name):
            os.remove(test_db_name)

    def _clone_test_db(self, suffix, verbosity, keepdb=False):
        """
        Clone the test database for parallel testing.
        Not supported for Firebird.
        """
        raise NotImplementedError("Cloning databases is not supported for Firebird.")
