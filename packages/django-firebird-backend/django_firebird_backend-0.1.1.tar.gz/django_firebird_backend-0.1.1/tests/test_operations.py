"""
Tests for DatabaseOperations class.
"""

import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest


class TestDatabaseOperations:
    """Test cases for DatabaseOperations methods."""

    @pytest.fixture
    def operations(self, mock_connection):
        """Create DatabaseOperations instance with mock connection."""
        from django_firebird.operations import DatabaseOperations

        ops = DatabaseOperations(mock_connection)
        return ops

    # =========================================================================
    # Limit/Offset SQL tests
    # =========================================================================

    def test_limit_offset_sql_limit_only(self, operations):
        """Test FIRST without SKIP."""
        sql = operations.limit_offset_sql(0, 10)
        assert sql == "FIRST 10"

    def test_limit_offset_sql_offset_only(self, operations):
        """Test SKIP without FIRST."""
        sql = operations.limit_offset_sql(5, None)
        assert sql == "SKIP 5"

    def test_limit_offset_sql_both(self, operations):
        """Test FIRST and SKIP together."""
        sql = operations.limit_offset_sql(10, 20)
        assert sql == "FIRST 10 SKIP 10"

    def test_limit_offset_sql_zero_offset(self, operations):
        """Test with zero offset (should not include SKIP)."""
        sql = operations.limit_offset_sql(0, 5)
        assert sql == "FIRST 5"
        assert "SKIP" not in sql

    def test_limit_offset_sql_none_values(self, operations):
        """Test with None values."""
        sql = operations.limit_offset_sql(None, None)
        assert sql == ""

    def test_limit_offset_sql_pagination(self, operations):
        """Test typical pagination scenario: page 3, 10 items per page."""
        # Page 3 = skip 20 items, get 10
        sql = operations.limit_offset_sql(20, 30)
        assert sql == "FIRST 10 SKIP 20"

    # =========================================================================
    # Quote name tests
    # =========================================================================

    def test_quote_name_simple(self, operations):
        """Test quoting simple identifier."""
        assert operations.quote_name("table") == '"table"'

    def test_quote_name_already_quoted(self, operations):
        """Test that already quoted names are not double-quoted."""
        assert operations.quote_name('"table"') == '"table"'

    def test_quote_name_with_spaces(self, operations):
        """Test quoting identifier with spaces."""
        assert operations.quote_name("my table") == '"my table"'

    def test_quote_name_reserved_word(self, operations):
        """Test quoting reserved word."""
        assert operations.quote_name("SELECT") == '"SELECT"'

    def test_quote_name_escapes_internal_quotes(self, operations):
        """Test that internal double quotes are escaped to prevent SQL injection."""
        # This prevents: SELECT * FROM "evil"; DROP TABLE users; --"
        result = operations.quote_name('evil"; DROP TABLE users; --')
        assert result == '"evil""; DROP TABLE users; --"'

    def test_quote_name_double_escape(self, operations):
        """Test escaping already present double quotes."""
        result = operations.quote_name('table"name')
        assert result == '"table""name"'

    # =========================================================================
    # Date/Time adaptation tests
    # =========================================================================

    def test_adapt_datefield_value_none(self, operations):
        """Test adapting None date value."""
        result = operations.adapt_datefield_value(None)
        assert result is None

    def test_adapt_datefield_value(self, operations):
        """Test adapting date value."""
        date = datetime.date(2024, 6, 15)
        result = operations.adapt_datefield_value(date)
        assert result == "2024-06-15"

    def test_adapt_datetimefield_value_none(self, operations):
        """Test adapting None datetime value."""
        result = operations.adapt_datetimefield_value(None)
        assert result is None

    def test_adapt_datetimefield_value_no_microseconds(self, operations):
        """Test adapting datetime without microseconds."""
        dt = datetime.datetime(2024, 6, 15, 10, 30, 45)
        result = operations.adapt_datetimefield_value(dt)
        assert result == "2024-06-15 10:30:45"

    def test_adapt_datetimefield_value_with_microseconds(self, operations):
        """Test adapting datetime with microseconds (truncated to ms)."""
        dt = datetime.datetime(2024, 6, 15, 10, 30, 45, 123456)
        result = operations.adapt_datetimefield_value(dt)
        # Should truncate to 3 digits (milliseconds)
        assert result == "2024-06-15 10:30:45.123"

    def test_adapt_datetimefield_value_with_small_microseconds(self, operations):
        """Test adapting datetime with small microsecond value."""
        dt = datetime.datetime(2024, 6, 15, 10, 30, 45, 5000)
        result = operations.adapt_datetimefield_value(dt)
        assert result == "2024-06-15 10:30:45.005"

    def test_adapt_datetimefield_value_999_milliseconds(self, operations):
        """Test adapting datetime at end of second (999ms)."""
        dt = datetime.datetime(2024, 12, 31, 23, 59, 59, 999000)
        result = operations.adapt_datetimefield_value(dt)
        assert result == "2024-12-31 23:59:59.999"

    def test_adapt_timefield_value_none(self, operations):
        """Test adapting None time value."""
        result = operations.adapt_timefield_value(None)
        assert result is None

    def test_adapt_timefield_value(self, operations):
        """Test adapting time value."""
        t = datetime.time(10, 30, 45)
        result = operations.adapt_timefield_value(t)
        assert result == "10:30:45"

    # =========================================================================
    # Year lookup bounds tests
    # =========================================================================

    def test_year_lookup_bounds_no_tz(self, operations):
        """Test year lookup bounds without timezone."""
        first, second = operations.year_lookup_bounds_for_datetime_field(2024)

        assert first == "2024-01-01 00:00:00"
        assert second == "2024-12-31 23:59:59.999"

    def test_year_lookup_bounds_different_years(self, operations):
        """Test year lookup bounds for different years."""
        first_2020, second_2020 = operations.year_lookup_bounds_for_datetime_field(2020)
        first_2025, second_2025 = operations.year_lookup_bounds_for_datetime_field(2025)

        assert "2020-01-01" in first_2020
        assert "2020-12-31" in second_2020
        assert "2025-01-01" in first_2025
        assert "2025-12-31" in second_2025

    # =========================================================================
    # Max name length tests
    # =========================================================================

    def test_max_name_length_firebird_25(self, mock_connection):
        """Test max name length for Firebird 2.5."""
        from django_firebird.operations import DatabaseOperations

        mock_connection.firebird_version = (2, 5)
        ops = DatabaseOperations(mock_connection)

        assert ops.max_name_length() == 31

    def test_max_name_length_firebird_30(self, mock_connection):
        """Test max name length for Firebird 3.0."""
        from django_firebird.operations import DatabaseOperations

        mock_connection.firebird_version = (3, 0)
        ops = DatabaseOperations(mock_connection)

        assert ops.max_name_length() == 31

    def test_max_name_length_firebird_40(self, mock_connection):
        """Test max name length for Firebird 4.0+."""
        from django_firebird.operations import DatabaseOperations

        mock_connection.firebird_version = (4, 0)
        ops = DatabaseOperations(mock_connection)

        assert ops.max_name_length() == 63

    def test_max_name_length_firebird_50(self, mock_connection):
        """Test max name length for Firebird 5.0."""
        from django_firebird.operations import DatabaseOperations

        mock_connection.firebird_version = (5, 0)
        ops = DatabaseOperations(mock_connection)

        assert ops.max_name_length() == 63

    # =========================================================================
    # Other value adaptation tests
    # =========================================================================

    def test_adapt_decimalfield_value_none(self, operations):
        """Test adapting None decimal value."""
        result = operations.adapt_decimalfield_value(None)
        assert result is None

    def test_adapt_decimalfield_value(self, operations):
        """Test adapting decimal value."""
        value = Decimal("123.45")
        result = operations.adapt_decimalfield_value(value)
        assert result == "123.45"

    def test_adapt_ipaddressfield_value_none(self, operations):
        """Test adapting None IP address."""
        result = operations.adapt_ipaddressfield_value(None)
        assert result is None

    def test_adapt_ipaddressfield_value(self, operations):
        """Test adapting IP address."""
        result = operations.adapt_ipaddressfield_value("192.168.1.1")
        assert result == "192.168.1.1"

    # =========================================================================
    # Sequence/Generator tests
    # =========================================================================

    def test_get_generator_name(self, mock_connection):
        """Test generator name generation."""
        from django_firebird.operations import DatabaseOperations

        # Use a real connection mock that provides truncate_name
        mock_connection.firebird_version = (2, 5)
        ops = DatabaseOperations(mock_connection)

        # Mock truncate_name since it's from base class
        ops.truncate_name = lambda name, length: name[:length]

        name = ops._get_generator_name("my_table", "id")
        assert "MY_TABLE" in name or "my_table" in name.lower()

    def test_get_trigger_name(self, mock_connection):
        """Test trigger name generation."""
        from django_firebird.operations import DatabaseOperations

        mock_connection.firebird_version = (2, 5)
        ops = DatabaseOperations(mock_connection)

        # Mock truncate_name since it's from base class
        ops.truncate_name = lambda name, length: name[:length]

        name = ops._get_trigger_name("my_table", "id")
        assert "MY_TABLE" in name or "my_table" in name.lower()

    # =========================================================================
    # SQL generation tests
    # =========================================================================

    def test_no_limit_value(self, operations):
        """Test no limit value returns None."""
        assert operations.no_limit_value() is None

    def test_pk_default_value(self, operations):
        """Test primary key default value."""
        assert operations.pk_default_value() == "NULL"

    def test_for_update_sql_default(self, operations):
        """Test FOR UPDATE clause generation - Firebird uses WITH LOCK."""
        sql = operations.for_update_sql()
        assert sql == "WITH LOCK"

    def test_for_update_sql_nowait(self, operations):
        """Test WITH LOCK (nowait has same behavior in Firebird)."""
        sql = operations.for_update_sql(nowait=True)
        assert sql == "WITH LOCK"

    def test_for_update_sql_skip_locked_fb25(self, operations):
        """Test that SKIP LOCKED is not added for Firebird < 5.0."""
        # Default fixture uses FB 2.5
        sql = operations.for_update_sql(skip_locked=True)
        assert sql == "WITH LOCK"  # No SKIP LOCKED for FB < 5.0

    def test_for_update_sql_skip_locked_fb50(self):
        """Test SKIP LOCKED is added for Firebird 5.0+."""
        from django_firebird.operations import DatabaseOperations

        mock_connection = MagicMock()
        mock_connection.firebird_version = (5, 0)
        operations = DatabaseOperations(mock_connection)

        sql = operations.for_update_sql(skip_locked=True)
        assert sql == "WITH LOCK SKIP LOCKED"

    # =========================================================================
    # Additional methods tests
    # =========================================================================

    def test_explain_query_prefix(self, operations):
        """Test EXPLAIN prefix - Firebird handles this differently."""
        assert operations.explain_query_prefix() == ""

    def test_last_executed_query_no_params(self, operations):
        """Test last executed query without parameters."""
        sql = "SELECT * FROM users"
        result = operations.last_executed_query(None, sql, None)
        assert result == sql

    def test_last_executed_query_with_params(self, operations):
        """Test last executed query with parameters."""
        sql = "SELECT * FROM users WHERE id = ? AND name = ?"
        params = [1, "test"]
        result = operations.last_executed_query(None, sql, params)
        assert "1" in result
        assert "'test'" in result

    def test_prep_for_iexact_query(self, operations):
        """Test prep_for_iexact_query returns value unchanged."""
        assert operations.prep_for_iexact_query("Test") == "Test"

    def test_set_time_zone_sql_fb25(self, operations):
        """Test set_time_zone_sql returns empty for Firebird < 4.0."""
        assert operations.set_time_zone_sql() == ""

    def test_set_time_zone_sql_fb40(self):
        """Test set_time_zone_sql returns SQL for Firebird 4.0+."""
        from django_firebird.operations import DatabaseOperations

        mock_connection = MagicMock()
        mock_connection.firebird_version = (4, 0)
        operations = DatabaseOperations(mock_connection)

        assert "SET TIME ZONE" in operations.set_time_zone_sql()

    def test_lookup_cast_regular(self, operations):
        """Test lookup_cast for regular lookups."""
        assert operations.lookup_cast("exact") == "%s"

    def test_lookup_cast_case_insensitive(self, operations):
        """Test lookup_cast for case-insensitive lookups."""
        assert operations.lookup_cast("iexact") == "UPPER(%s)"
        assert operations.lookup_cast("icontains") == "UPPER(%s)"

    def test_prepare_sql_script(self, operations):
        """Test SQL script splitting."""
        script = "SELECT 1; SELECT 2; SELECT 3"
        result = operations.prepare_sql_script(script)
        assert len(result) == 3
        assert "SELECT 1" in result

    def test_prepare_sql_script_empty_statements(self, operations):
        """Test SQL script splitting ignores empty statements."""
        script = "SELECT 1;; SELECT 2;  "
        result = operations.prepare_sql_script(script)
        assert len(result) == 2

    def test_subtract_temporals_date(self, operations):
        """Test temporal subtraction for dates."""
        sql, params = operations.subtract_temporals("DateField", "lhs", "rhs")
        assert "DATEDIFF" in sql
        assert "DAY" in sql

    def test_subtract_temporals_datetime(self, operations):
        """Test temporal subtraction for datetimes."""
        sql, params = operations.subtract_temporals("DateTimeField", "lhs", "rhs")
        assert "DATEDIFF" in sql
        assert "MILLISECOND" in sql

    def test_subtract_temporals_time(self, operations):
        """Test temporal subtraction for times."""
        sql, params = operations.subtract_temporals("TimeField", "lhs", "rhs")
        assert "EXTRACT" in sql

    def test_combine_expression_power(self, operations):
        """Test combine_expression for power operator."""
        result = operations.combine_expression("^", ["a", "b"])
        assert result == "POWER(a, b)"

    def test_regex_lookup_regex(self, operations):
        """Test regex lookup SQL."""
        result = operations.regex_lookup("regex")
        assert "SIMILAR TO" in result

    def test_regex_lookup_iregex(self, operations):
        """Test case-insensitive regex lookup SQL."""
        result = operations.regex_lookup("iregex")
        assert "SIMILAR TO" in result
        assert "UPPER" in result

    def test_regex_lookup_unknown(self, operations):
        """Test unknown regex lookup raises error."""
        import pytest

        with pytest.raises(NotImplementedError):
            operations.regex_lookup("unknown")
