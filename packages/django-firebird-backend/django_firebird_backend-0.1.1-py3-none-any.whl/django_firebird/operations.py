"""
Firebird database operations for Django.

Contains SQL generation methods specific to Firebird.
"""

import datetime
import uuid

from django.conf import settings
from django.db.backends.base.operations import BaseDatabaseOperations
from django.utils import timezone


class DatabaseOperations(BaseDatabaseOperations):
    compiler_module = "django_firebird.compiler"

    # Integer field ranges for Firebird
    integer_field_ranges = {
        "SmallIntegerField": (-32768, 32767),
        "IntegerField": (-2147483648, 2147483647),
        "BigIntegerField": (-9223372036854775808, 9223372036854775807),
        "PositiveBigIntegerField": (0, 9223372036854775807),
        "PositiveSmallIntegerField": (0, 32767),
        "PositiveIntegerField": (0, 2147483647),
    }

    # =========================================================================
    # Naming and quoting
    # =========================================================================

    def max_name_length(self):
        """
        Return max identifier length.
        Firebird 2.5-3.0: 31 characters
        Firebird 4.0+: 63 characters
        """
        if self.connection.firebird_version >= (4, 0):
            return 63
        return 31

    def quote_name(self, name):
        """
        Quote an identifier using double quotes.

        Escapes internal double quotes by doubling them (SQL standard).
        """
        if name.startswith('"') and name.endswith('"'):
            return name
        # Escape internal double quotes by doubling them
        name = name.replace('"', '""')
        return f'"{name}"'

    # =========================================================================
    # Limit/Offset - Firebird uses FIRST/SKIP or ROWS
    # =========================================================================

    def limit_offset_sql(self, low_mark, high_mark):
        """
        Return LIMIT/OFFSET SQL.
        Firebird uses FIRST n SKIP m syntax (placed after SELECT).
        """
        fetch, offset = self._get_limit_offset_params(low_mark, high_mark)
        return " ".join(
            sql
            for sql in (
                f"FIRST {fetch}" if fetch else None,
                f"SKIP {offset}" if offset else None,
            )
            if sql
        )

    def _get_limit_offset_params(self, low_mark, high_mark):
        """Calculate FIRST and SKIP parameters."""
        offset = low_mark or 0
        if high_mark is not None:
            fetch = high_mark - offset
        else:
            fetch = None
        return fetch, offset

    # =========================================================================
    # Date/Time operations
    # =========================================================================

    def date_extract_sql(self, lookup_type, sql, params):
        """Extract date part using EXTRACT function."""
        return f"EXTRACT({lookup_type.upper()} FROM {sql})", params

    def date_trunc_sql(self, lookup_type, sql, params):
        """Truncate date to specified precision."""
        if lookup_type == "year":
            return f"CAST(EXTRACT(YEAR FROM {sql}) || '-01-01' AS DATE)", params
        elif lookup_type == "month":
            return (
                f"CAST(EXTRACT(YEAR FROM {sql}) || '-' || "
                f"LPAD(EXTRACT(MONTH FROM {sql}), 2, '0') || '-01' AS DATE)",
                params,
            )
        elif lookup_type == "day":
            return f"CAST({sql} AS DATE)", params
        elif lookup_type == "quarter":
            return (
                f"CAST(EXTRACT(YEAR FROM {sql}) || '-' || "
                f"LPAD(((EXTRACT(MONTH FROM {sql}) - 1) / 3) * 3 + 1, 2, '0') || '-01' AS DATE)",
                params,
            )
        elif lookup_type == "week":
            # Truncate to Monday of the week
            return (
                f"DATEADD(DAY, -EXTRACT(WEEKDAY FROM {sql}), CAST({sql} AS DATE))",
                params,
            )
        return sql, params

    def datetime_cast_date_sql(self, sql, params):
        """Cast datetime to date."""
        return f"CAST({sql} AS DATE)", params

    def datetime_cast_time_sql(self, sql, params):
        """Cast datetime to time."""
        return f"CAST({sql} AS TIME)", params

    def datetime_extract_sql(self, lookup_type, sql, params):
        """Extract datetime part."""
        return self.date_extract_sql(lookup_type, sql, params)

    def datetime_trunc_sql(self, lookup_type, sql, params, tzname):
        """Truncate datetime to specified precision."""
        return self.date_trunc_sql(lookup_type, sql, params)

    def time_trunc_sql(self, lookup_type, sql, params):
        """Truncate time to specified precision."""
        if lookup_type == "hour":
            return f"CAST(EXTRACT(HOUR FROM {sql}) || ':00:00' AS TIME)", params
        elif lookup_type == "minute":
            return (
                f"CAST(EXTRACT(HOUR FROM {sql}) || ':' || "
                f"LPAD(EXTRACT(MINUTE FROM {sql}), 2, '0') || ':00' AS TIME)",
                params,
            )
        elif lookup_type == "second":
            return (
                f"CAST(EXTRACT(HOUR FROM {sql}) || ':' || "
                f"LPAD(EXTRACT(MINUTE FROM {sql}), 2, '0') || ':' || "
                f"LPAD(CAST(EXTRACT(SECOND FROM {sql}) AS INTEGER), 2, '0') AS TIME)",
                params,
            )
        return sql, params

    # =========================================================================
    # Value adapters - Python to SQL
    # =========================================================================

    def adapt_datefield_value(self, value):
        """Convert Python date to database format."""
        if value is None:
            return None
        return str(value)

    def adapt_datetimefield_value(self, value):
        """Convert Python datetime to database format."""
        if value is None:
            return None
        if timezone.is_aware(value):
            if settings.USE_TZ:
                # Use Python's datetime.timezone.utc for compatibility
                value = timezone.make_naive(value, datetime.UTC)
        # Firebird 2.5 only supports milliseconds (4 digits), not microseconds (6 digits)
        # Format: YYYY-MM-DD HH:MM:SS.mmm
        if value.microsecond:
            # Truncate to milliseconds (first 3 digits of microseconds)
            ms = value.microsecond // 1000
            return value.strftime("%Y-%m-%d %H:%M:%S") + f".{ms:03d}"
        return value.strftime("%Y-%m-%d %H:%M:%S")

    def adapt_timefield_value(self, value):
        """Convert Python time to database format."""
        if value is None:
            return None
        return str(value)

    def adapt_decimalfield_value(self, value, max_digits=None, decimal_places=None):
        """Convert Decimal to database format."""
        if value is None:
            return None
        return str(value)

    def adapt_ipaddressfield_value(self, value):
        """Convert IP address to database format."""
        if value is None:
            return None
        return str(value)

    # =========================================================================
    # Sequence/Generator operations
    # =========================================================================

    def autoinc_sql(self, table, column):
        """
        Return SQL to create auto-increment trigger.
        Firebird uses generators (sequences) + triggers.
        """
        generator_name = self._get_generator_name(table, column)
        trigger_name = self._get_trigger_name(table, column)

        return (
            # Create generator
            f"CREATE SEQUENCE {self.quote_name(generator_name)}",
            # Create trigger
            f"""CREATE TRIGGER {self.quote_name(trigger_name)}
                FOR {self.quote_name(table)}
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.{self.quote_name(column)} IS NULL) THEN
                        NEW.{self.quote_name(column)} = NEXT VALUE FOR {self.quote_name(generator_name)};
                END""",
        )

    def _get_generator_name(self, table, column):
        """Generate name for sequence/generator."""
        name = f"{table}_{column}_seq"
        return self.truncate_name(name, self.max_name_length())

    def _get_trigger_name(self, table, column):
        """Generate name for auto-increment trigger."""
        name = f"{table}_{column}_trg"
        return self.truncate_name(name, self.max_name_length())

    def sequence_reset_by_name_sql(self, style, sequences):
        """Return SQL to reset sequences."""
        sql = []
        for sequence_info in sequences:
            seq_name = sequence_info["name"]
            sql.append(f"ALTER SEQUENCE {self.quote_name(seq_name)} RESTART WITH 0")
        return sql

    def sequence_reset_sql(self, style, model_list):
        """Return SQL to reset sequences for models."""
        output = []
        for model in model_list:
            for field in model._meta.local_fields:
                if field.primary_key and field.get_internal_type() in (
                    "AutoField",
                    "BigAutoField",
                    "SmallAutoField",
                ):
                    table = model._meta.db_table
                    column = field.column
                    generator_name = self._get_generator_name(table, column)

                    # Get max value
                    output.append(
                        f"EXECUTE BLOCK AS "
                        f"DECLARE max_val INTEGER; "
                        f"BEGIN "
                        f"SELECT COALESCE(MAX({self.quote_name(column)}), 0) "
                        f"FROM {self.quote_name(table)} INTO :max_val; "
                        f"EXECUTE STATEMENT 'ALTER SEQUENCE {self.quote_name(generator_name)} "
                        f"RESTART WITH ' || :max_val; "
                        f"END"
                    )
        return output

    def last_insert_id(self, cursor, table_name, pk_name):
        """
        Get the last inserted ID.
        This should be called after INSERT ... RETURNING.
        """
        # With RETURNING clause, the ID is returned by the INSERT
        # This method is called as fallback
        generator_name = self._get_generator_name(table_name, pk_name)
        cursor.execute(
            f"SELECT GEN_ID({self.quote_name(generator_name)}, 0) FROM RDB$DATABASE"
        )
        return cursor.fetchone()[0]

    # =========================================================================
    # SQL generation helpers
    # =========================================================================

    def no_limit_value(self):
        """Return value indicating no limit."""
        return None

    def pk_default_value(self):
        """Return SQL for default PK value."""
        return "NULL"

    def return_insert_columns(self, fields):
        """
        Generate RETURNING clause for INSERT.
        """
        if not fields:
            return "", ()

        columns = ", ".join(self.quote_name(field.column) for field in fields)
        return f"RETURNING {columns}", ()

    def bulk_insert_sql(self, fields, placeholder_rows):
        """Generate bulk INSERT SQL."""
        # Firebird doesn't support multi-row INSERT VALUES
        # Each row must be a separate INSERT
        return " UNION ALL ".join(
            "SELECT {} FROM RDB$DATABASE".format(", ".join(row))
            for row in placeholder_rows
        )

    def sql_flush(self, style, tables, *, reset_sequences=False, allow_cascade=False):
        """Return SQL to flush tables."""
        if not tables:
            return []

        sql = []
        for table in tables:
            sql.append(f"DELETE FROM {self.quote_name(table)}")

        if reset_sequences:
            sql.extend(self.sequence_reset_sql(style, []))

        return sql

    def for_update_sql(self, nowait=False, skip_locked=False, of=(), no_key=False):
        """
        Generate FOR UPDATE clause.

        Firebird uses WITH LOCK instead of FOR UPDATE.
        SKIP LOCKED is available in Firebird 5.0+.
        """
        sql = "WITH LOCK"
        if skip_locked and self.connection.firebird_version >= (5, 0):
            sql += " SKIP LOCKED"
        return sql

    def distinct_sql(self, fields, params):
        """Generate DISTINCT clause."""
        if fields:
            # Firebird doesn't support DISTINCT ON
            raise NotImplementedError("Firebird does not support DISTINCT ON fields.")
        return ["DISTINCT"], []

    def year_lookup_bounds_for_datetime_field(self, value, iso_year=False):
        """
        Return datetime bounds for year lookup.
        Firebird 2.5 only supports 3-digit milliseconds, not 6-digit microseconds.
        """
        first = datetime.datetime(value, 1, 1)
        # Use 999 milliseconds = 999000 microseconds, will be truncated to .999 in adapt
        second = datetime.datetime(value, 12, 31, 23, 59, 59, 999000)
        if settings.USE_TZ:
            tz = datetime.UTC
            first = timezone.make_aware(first, tz)
            second = timezone.make_aware(second, tz)
        first = self.adapt_datetimefield_value(first)
        second = self.adapt_datetimefield_value(second)
        return (first, second)

    # =========================================================================
    # Type conversions
    # =========================================================================

    def convert_booleanfield_value(self, value, expression, connection):
        """Convert database boolean to Python bool."""
        if value is None:
            return None
        return bool(value)

    def convert_uuidfield_value(self, value, expression, connection):
        """Convert database UUID string to Python UUID."""
        if value is None:
            return None
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value

    def get_db_converters(self, expression):
        """Return list of converters for expression."""
        converters = super().get_db_converters(expression)
        internal_type = expression.output_field.get_internal_type()

        if internal_type == "BooleanField":
            converters.append(self.convert_booleanfield_value)
        elif internal_type == "UUIDField":
            converters.append(self.convert_uuidfield_value)

        return converters

    # =========================================================================
    # Additional methods for Django compatibility
    # =========================================================================

    def explain_query_prefix(self, format=None, **options):
        """
        Return EXPLAIN prefix for query plan.

        Firebird doesn't have EXPLAIN syntax - use SET PLAN ON / PLAN statement.
        Returns empty string as Firebird handles this differently.
        """
        # Firebird shows plan via PLAN keyword or SET PLAN ON
        return ""

    def last_executed_query(self, cursor, sql, params):
        """
        Return the last executed query with parameters substituted.

        Used for debugging.
        """
        if params:
            # Replace ? placeholders with actual values for debugging
            # Firebird uses ? placeholders, not %s
            result = sql
            for param in params:
                result = result.replace("?", repr(param), 1)
            return result
        return sql

    def prep_for_iexact_query(self, x):
        """
        Prepare value for case-insensitive exact match.

        Firebird is case-sensitive by default, so we uppercase both sides.
        """
        return x

    def set_time_zone_sql(self):
        """
        Return SQL to set session timezone.

        Used for Firebird 4.0+ which supports TIME ZONE.
        """
        if self.connection.firebird_version >= (4, 0):
            return "SET TIME ZONE %s"
        return ""

    def lookup_cast(self, lookup_type, internal_type=None):
        """
        Return SQL fragment for CAST in lookups.

        Firebird may need explicit casts for some lookups.
        """
        if lookup_type in ("iexact", "icontains", "istartswith", "iendswith"):
            return "UPPER(%s)"
        return "%s"

    def prepare_sql_script(self, sql):
        """
        Take an SQL script and split it into individual statements.

        Firebird uses ; as statement separator but stored procedures
        use it inside blocks, so we need careful parsing.
        """
        # Simple split for now - complex scripts should use isql
        return [s.strip() for s in sql.split(";") if s.strip()]

    def subtract_temporals(self, internal_type, lhs, rhs):
        """
        Return SQL for subtracting two temporal values.

        Firebird uses DATEDIFF function instead of - operator.
        Returns interval in microseconds.
        """
        if internal_type == "DateField":
            # DATEDIFF returns days for dates
            return f"DATEDIFF(DAY, {rhs}, {lhs}) * 86400000000", []
        elif internal_type == "TimeField":
            # For time, calculate difference in microseconds
            return (
                f"(EXTRACT(HOUR FROM {lhs}) - EXTRACT(HOUR FROM {rhs})) * 3600000000 + "
                f"(EXTRACT(MINUTE FROM {lhs}) - EXTRACT(MINUTE FROM {rhs})) * 60000000 + "
                f"(EXTRACT(SECOND FROM {lhs}) - EXTRACT(SECOND FROM {rhs})) * 1000000",
                [],
            )
        else:
            # DateTimeField - use DATEDIFF with MILLISECOND and convert to microseconds
            return f"DATEDIFF(MILLISECOND, {rhs}, {lhs}) * 1000", []

    def combine_expression(self, connector, sub_expressions):
        """
        Combine expressions with operator.

        Handle special cases for Firebird.
        """
        if connector == "^":
            # Firebird uses POWER function, not ^ operator
            return "POWER({})".format(", ".join(sub_expressions))
        return super().combine_expression(connector, sub_expressions)

    def combine_duration_expression(self, connector, sub_expressions):
        """
        Combine duration expressions.

        Firebird stores durations as BIGINT (microseconds).
        """
        if connector == "+":
            return "({} + {})".format(*tuple(sub_expressions))
        elif connector == "-":
            return "({} - {})".format(*tuple(sub_expressions))
        return super().combine_duration_expression(connector, sub_expressions)

    def format_for_duration_arithmetic(self, sql):
        """
        Format SQL for duration arithmetic.

        Firebird stores durations as BIGINT (microseconds).
        """
        return sql

    def regex_lookup(self, lookup_type):
        """
        Return SQL for regex lookup.

        Firebird uses SIMILAR TO instead of ~ operator.
        """
        if lookup_type == "regex":
            return "%s SIMILAR TO %s"
        elif lookup_type == "iregex":
            return "UPPER(%s) SIMILAR TO UPPER(%s)"
        raise NotImplementedError(f"Unknown regex lookup type: {lookup_type}")
