"""
Firebird database backend for Django.

Requires firebird-driver >= 1.10.0
"""

from django.core.exceptions import ImproperlyConfigured
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.utils import CursorDebugWrapper
from django.utils.asyncio import async_unsafe
from django.utils.functional import cached_property

try:
    import firebird.driver as Database
    from firebird.driver import connect, driver_config
except ImportError as err:
    raise ImproperlyConfigured(
        "Error loading firebird-driver module. Did you install firebird-driver?"
    ) from err

from .client import DatabaseClient
from .creation import DatabaseCreation
from .features import DatabaseFeatures
from .introspection import DatabaseIntrospection
from .operations import DatabaseOperations
from .schema import DatabaseSchemaEditor


class CursorWrapper:
    """
    Wrapper around firebird-driver cursor to convert Django's %s
    placeholders to Firebird's ? placeholders.
    """

    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, sql, params=None):
        """Execute SQL converting %s to ?"""
        if params is not None:
            # Convert %s placeholders to ?
            sql = sql.replace("%s", "?")
        return self.cursor.execute(sql, params or [])

    def executemany(self, sql, param_list):
        """Execute SQL for multiple parameter sets."""
        sql = sql.replace("%s", "?")
        return self.cursor.executemany(sql, param_list)

    def callproc(self, procname, params=None):
        """
        Call a stored procedure.

        Firebird uses: EXECUTE PROCEDURE procname(params)
        """
        # Validate and quote procedure name to prevent SQL injection
        # Escape internal double quotes by doubling them
        safe_procname = procname.replace('"', '""')
        quoted_name = f'"{safe_procname}"'

        if params:
            placeholders = ", ".join("?" * len(params))
            sql = f"EXECUTE PROCEDURE {quoted_name}({placeholders})"
            return self.cursor.execute(sql, params)
        else:
            sql = f"EXECUTE PROCEDURE {quoted_name}"
            return self.cursor.execute(sql)

    def __getattr__(self, attr):
        """Delegate all other attributes to the underlying cursor."""
        return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = "firebird"
    display_name = "Firebird"

    # Base mapping of Django field types to Firebird column types
    _data_types_base = {
        "AutoField": "integer",
        "BigAutoField": "bigint",
        "BinaryField": "blob",
        "CharField": "varchar(%(max_length)s)",
        "DateField": "date",
        "DateTimeField": "timestamp",
        "DecimalField": "decimal(%(max_digits)s, %(decimal_places)s)",
        "DurationField": "bigint",
        "FileField": "varchar(%(max_length)s)",
        "FilePathField": "varchar(%(max_length)s)",
        "FloatField": "double precision",
        "IntegerField": "integer",
        "BigIntegerField": "bigint",
        "IPAddressField": "varchar(15)",
        "GenericIPAddressField": "varchar(39)",
        "JSONField": "blob sub_type text",
        "PositiveBigIntegerField": "bigint",
        "PositiveIntegerField": "integer",
        "PositiveSmallIntegerField": "smallint",
        "SlugField": "varchar(%(max_length)s)",
        "SmallAutoField": "smallint",
        "SmallIntegerField": "smallint",
        "TextField": "blob sub_type text",
        "TimeField": "time",
        "UUIDField": "char(36)",
    }

    @cached_property
    def data_types(self):
        """
        Return data types mapping.

        BooleanField uses native BOOLEAN in Firebird 3.0+, smallint otherwise.
        """
        types = self._data_types_base.copy()
        # Use _firebird_version directly to avoid circular dependency with features
        has_native_boolean = (
            self._firebird_version is not None and self._firebird_version >= (3, 0)
        )
        if has_native_boolean:
            types["BooleanField"] = "boolean"
        else:
            types["BooleanField"] = "smallint"
        return types

    # Constraints for positive fields
    data_type_check_constraints = {
        "PositiveBigIntegerField": '"%(column)s" >= 0',
        "PositiveIntegerField": '"%(column)s" >= 0',
        "PositiveSmallIntegerField": '"%(column)s" >= 0',
    }

    # No suffix for auto fields - Firebird uses generators/sequences
    data_types_suffix = {}

    # SQL operators for lookups
    operators = {
        "exact": "= %s",
        "iexact": "= UPPER(%s)",
        "contains": "LIKE %s ESCAPE '\\\\'",
        "icontains": "LIKE UPPER(%s) ESCAPE '\\\\'",
        "regex": "SIMILAR TO %s",
        "iregex": "SIMILAR TO %s",  # Firebird regex is case-sensitive
        "gt": "> %s",
        "gte": ">= %s",
        "lt": "< %s",
        "lte": "<= %s",
        "startswith": "LIKE %s ESCAPE '\\\\'",
        "endswith": "LIKE %s ESCAPE '\\\\'",
        "istartswith": "LIKE UPPER(%s) ESCAPE '\\\\'",
        "iendswith": "LIKE UPPER(%s) ESCAPE '\\\\'",
    }

    # Pattern operations for LIKE queries
    pattern_esc = (
        r"REPLACE(REPLACE(REPLACE({}, '\\', '\\\\'), '%%', '\\%%'), '_', '\\_')"
    )
    pattern_ops = {
        "contains": "LIKE '%%' || {} || '%%' ESCAPE '\\\\'",
        "icontains": "LIKE '%%' || UPPER({}) || '%%' ESCAPE '\\\\'",
        "startswith": "LIKE {} || '%%' ESCAPE '\\\\'",
        "istartswith": "LIKE UPPER({}) || '%%' ESCAPE '\\\\'",
        "endswith": "LIKE '%%' || {} ESCAPE '\\\\'",
        "iendswith": "LIKE '%%' || UPPER({}) ESCAPE '\\\\'",
    }

    Database = Database
    SchemaEditorClass = DatabaseSchemaEditor
    client_class = DatabaseClient
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._firebird_version = None

    @cached_property
    def firebird_version(self):
        """Return Firebird version as tuple (major, minor)."""
        if self._firebird_version is None:
            self.ensure_connection()
        return self._firebird_version

    def get_database_version(self):
        """Return database version as tuple for Django's version check."""
        return self.firebird_version

    def get_connection_params(self):
        """Return connection parameters for firebird-driver."""
        settings_dict = self.settings_dict

        if not settings_dict.get("NAME"):
            raise ImproperlyConfigured(
                "settings.DATABASES is improperly configured. "
                "Please supply the NAME value."
            )

        # Build DSN string: host/port:database or host:database or just database
        database = settings_dict["NAME"]
        host = settings_dict.get("HOST")
        port = settings_dict.get("PORT")

        if host:
            if port:
                dsn = f"{host}/{port}:{database}"
            else:
                dsn = f"{host}:{database}"
        else:
            dsn = database

        conn_params = {
            "database": dsn,
            "user": settings_dict.get("USER") or "SYSDBA",
            "password": settings_dict.get("PASSWORD") or "",
        }

        # Add charset from OPTIONS
        options = settings_dict.get("OPTIONS", {})
        conn_params["charset"] = options.get("charset", "UTF8")

        # Configure client library path if specified
        fb_client_library = options.get("fb_client_library")
        if fb_client_library:
            driver_config.fb_client_library.value = fb_client_library

        return conn_params

    @async_unsafe
    def get_new_connection(self, conn_params):
        """Open a new connection to the database."""
        return connect(**conn_params)

    def init_connection_state(self):
        """Initialize connection state after opening."""
        # Get Firebird version
        if self._firebird_version is None:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT RDB$GET_CONTEXT('SYSTEM', 'ENGINE_VERSION') FROM RDB$DATABASE"
            )
            version_str = cursor.fetchone()[0]
            cursor.close()

            if version_str:
                parts = version_str.split(".")
                self._firebird_version = (
                    int(parts[0]),
                    int(parts[1]) if len(parts) > 1 else 0,
                )
            else:
                # Fallback for older Firebird versions
                self._firebird_version = (2, 5)

        # Call parent's version check
        super().init_connection_state()

        # Set timezone for Firebird 4.0+ if USE_TZ is enabled
        from django.conf import settings

        if getattr(settings, "USE_TZ", False):
            self.ensure_timezone()

    @async_unsafe
    def create_cursor(self, name=None):
        """Create a database cursor wrapped to convert %s to ? placeholders."""
        return CursorWrapper(self.connection.cursor())

    def _set_autocommit(self, autocommit):
        """
        Set autocommit mode on the connection.

        Firebird doesn't have a direct autocommit mode like PostgreSQL.
        When switching to autocommit, we commit any pending transaction.
        Django handles the rest by committing after each operation in autocommit mode.
        """
        with self.wrap_database_errors:
            if autocommit and self.connection is not None:
                # Only commit if there's an active transaction
                # main_transaction may be None when connection is first established
                if (
                    hasattr(self.connection, "main_transaction")
                    and self.connection.main_transaction is not None
                    and self.connection.main_transaction.is_active()
                ):
                    try:
                        self.connection.commit()
                    except Database.Error:
                        # Ignore if no transaction is active
                        pass

    def is_usable(self):
        """Test if the database connection is usable."""
        try:
            # Try a simple query
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1 FROM RDB$DATABASE")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False

    def _commit(self):
        """Commit the current transaction."""
        if self.connection is not None:
            with self.wrap_database_errors:
                self.connection.commit()

    def _rollback(self):
        """Roll back the current transaction."""
        if self.connection is not None:
            with self.wrap_database_errors:
                self.connection.rollback()

    def _close(self):
        """Close the database connection."""
        if self.connection is not None:
            with self.wrap_database_errors:
                self.connection.close()

    def make_debug_cursor(self, cursor):
        """Create a cursor that logs all queries for debugging."""
        return CursorDebugWrapper(cursor, self)

    def ensure_timezone(self):
        """
        Set the session timezone for Firebird 4.0+.

        Called from init_connection_state when USE_TZ is True.
        """
        # Use _firebird_version directly to avoid circular dependency with features
        supports_tz = self._firebird_version is not None and self._firebird_version >= (
            4,
            0,
        )
        if supports_tz and self.settings_dict.get("TIME_ZONE"):
            tz = self.settings_dict["TIME_ZONE"]
            with self.connection.cursor() as cursor:
                cursor.execute("SET TIME ZONE ?", [tz])
