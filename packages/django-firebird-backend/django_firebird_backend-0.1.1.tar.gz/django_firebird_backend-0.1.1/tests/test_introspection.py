"""
Tests for DatabaseIntrospection class.
"""

from unittest.mock import MagicMock

import pytest


class TestDatabaseIntrospection:
    """Test cases for DatabaseIntrospection methods."""

    @pytest.fixture
    def introspection(self, mock_connection):
        """Create DatabaseIntrospection instance with mock connection."""
        from django_firebird.introspection import DatabaseIntrospection

        return DatabaseIntrospection(mock_connection)

    # =========================================================================
    # Data types reverse mapping tests
    # =========================================================================

    def test_data_types_reverse_smallint(self, introspection):
        """Test SMALLINT maps to SmallIntegerField."""
        assert introspection.data_types_reverse[7] == "SmallIntegerField"

    def test_data_types_reverse_integer(self, introspection):
        """Test INTEGER maps to IntegerField."""
        assert introspection.data_types_reverse[8] == "IntegerField"

    def test_data_types_reverse_bigint(self, introspection):
        """Test BIGINT maps to BigIntegerField."""
        assert introspection.data_types_reverse[16] == "BigIntegerField"

    def test_data_types_reverse_float(self, introspection):
        """Test FLOAT maps to FloatField."""
        assert introspection.data_types_reverse[10] == "FloatField"

    def test_data_types_reverse_double(self, introspection):
        """Test DOUBLE PRECISION maps to FloatField."""
        assert introspection.data_types_reverse[27] == "FloatField"

    def test_data_types_reverse_date(self, introspection):
        """Test DATE maps to DateField."""
        assert introspection.data_types_reverse[12] == "DateField"

    def test_data_types_reverse_time(self, introspection):
        """Test TIME maps to TimeField."""
        assert introspection.data_types_reverse[13] == "TimeField"

    def test_data_types_reverse_timestamp(self, introspection):
        """Test TIMESTAMP maps to DateTimeField."""
        assert introspection.data_types_reverse[35] == "DateTimeField"

    def test_data_types_reverse_char(self, introspection):
        """Test CHAR maps to CharField."""
        assert introspection.data_types_reverse[14] == "CharField"

    def test_data_types_reverse_varchar(self, introspection):
        """Test VARCHAR maps to CharField."""
        assert introspection.data_types_reverse[37] == "CharField"

    def test_data_types_reverse_blob(self, introspection):
        """Test BLOB maps to TextField."""
        assert introspection.data_types_reverse[261] == "TextField"

    def test_data_types_reverse_boolean(self, introspection):
        """Test BOOLEAN maps to BooleanField (Firebird 3.0+)."""
        assert introspection.data_types_reverse[23] == "BooleanField"

    # =========================================================================
    # get_field_type tests
    # =========================================================================

    def test_get_field_type_basic(self, introspection):
        """Test basic field type lookup."""
        description = MagicMock()
        result = introspection.get_field_type(8, description)  # INTEGER
        assert result == "IntegerField"

    def test_get_field_type_blob_text(self, introspection):
        """Test BLOB with text subtype."""
        description = MagicMock()
        description.subtype = 1  # Text subtype

        result = introspection.get_field_type(261, description)
        assert result == "TextField"

    def test_get_field_type_blob_binary(self, introspection):
        """Test BLOB with binary subtype."""
        description = MagicMock()
        description.subtype = 0  # Binary subtype

        result = introspection.get_field_type(261, description)
        assert result == "BinaryField"

    # =========================================================================
    # get_table_list tests
    # =========================================================================

    def test_get_table_list_tables_only(self, introspection):
        """Test getting list of tables."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("TABLE1", "t"),
            ("TABLE2", "t"),
        ]

        result = introspection.get_table_list(mock_cursor)

        assert len(result) == 2
        assert result[0].name == "TABLE1"
        assert result[0].type == "t"
        assert result[1].name == "TABLE2"

    def test_get_table_list_with_views(self, introspection):
        """Test getting list with views."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("TABLE1", "t"),
            ("VIEW1", "v"),
        ]

        result = introspection.get_table_list(mock_cursor)

        assert len(result) == 2
        assert result[0].type == "t"
        assert result[1].type == "v"

    def test_get_table_list_empty(self, introspection):
        """Test empty table list."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        result = introspection.get_table_list(mock_cursor)

        assert result == []

    # =========================================================================
    # get_table_description tests
    # =========================================================================

    def test_get_table_description_basic(self, introspection):
        """Test basic table description."""
        mock_cursor = MagicMock()
        # name, type, length, precision, scale, nullable, default, char_len, subtype, comment, field_source, collation
        mock_cursor.fetchall.return_value = [
            ("ID", 8, 4, None, None, 0, None, None, None, None, "RDB$1", None),
            (
                "NAME",
                37,
                100,
                None,
                None,
                1,
                None,
                100,
                None,
                "Customer name",
                "RDB$2",
                "UTF8",
            ),
        ]

        result = introspection.get_table_description(mock_cursor, "TEST")

        assert len(result) == 2
        assert result[0].name == "ID"
        assert result[0].type_code == 8
        assert result[0].null_ok is False
        assert result[1].name == "NAME"
        assert result[1].null_ok is True
        assert result[1].comment == "Customer name"
        assert result[1].collation == "UTF8"

    def test_get_table_description_varchar_length(self, introspection):
        """Test VARCHAR uses character length."""
        mock_cursor = MagicMock()
        # name, type, length, precision, scale, nullable, default, char_len, subtype, comment, field_source, collation
        mock_cursor.fetchall.return_value = [
            ("FIELD", 37, 400, None, None, 1, None, 100, None, None, "RDB$1", None),
        ]

        result = introspection.get_table_description(mock_cursor, "TEST")

        assert result[0].display_size == 100  # Should use char_length, not byte length

    def test_get_table_description_uppercase_table(self, introspection):
        """Test table name is uppercased in query."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        introspection.get_table_description(mock_cursor, "lowercase_table")

        # Verify the table name was uppercased in the query
        call_args = mock_cursor.execute.call_args
        assert "LOWERCASE_TABLE" in call_args[0][1]

    # =========================================================================
    # get_primary_key_column tests
    # =========================================================================

    def test_get_primary_key_column_found(self, introspection):
        """Test finding primary key column."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("ID",)

        result = introspection.get_primary_key_column(mock_cursor, "TEST")

        assert result == "ID"

    def test_get_primary_key_column_not_found(self, introspection):
        """Test when no primary key exists."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None

        result = introspection.get_primary_key_column(mock_cursor, "TEST")

        assert result is None

    # =========================================================================
    # get_relations tests
    # =========================================================================

    def test_get_relations_single_column_fk(self, introspection):
        """Test single-column foreign key."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("COMPANY_ID", "COMPANY", "ID"),
        ]

        result = introspection.get_relations(mock_cursor, "CUSTOMER")

        assert "COMPANY_ID" in result
        assert result["COMPANY_ID"] == ("COMPANY", "ID")

    def test_get_relations_multiple_fks(self, introspection):
        """Test multiple foreign keys."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("COMPANY_ID", "COMPANY", "ID"),
            ("CUSTOMER_ID", "CUSTOMER", "ID"),
            ("PRODUCT_ID", "PRODUCT", "ID"),
        ]

        result = introspection.get_relations(mock_cursor, "ORDER")

        assert len(result) == 3
        assert result["COMPANY_ID"] == ("COMPANY", "ID")
        assert result["CUSTOMER_ID"] == ("CUSTOMER", "ID")
        assert result["PRODUCT_ID"] == ("PRODUCT", "ID")

    def test_get_relations_no_fks(self, introspection):
        """Test table with no foreign keys."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        result = introspection.get_relations(mock_cursor, "COMPANY")

        assert result == {}

    def test_get_relations_composite_fk(self, introspection):
        """Test composite foreign key (multiple columns)."""
        mock_cursor = MagicMock()
        # Composite FK: (ORDER_ID, PRODUCT_ID) -> ORDER_ITEM(ORDER_ID, PRODUCT_ID)
        mock_cursor.fetchall.return_value = [
            ("ORDER_ID", "ORDER", "ID"),
            ("LINE_NUMBER", "ORDER", "LINE_NUMBER"),
        ]

        result = introspection.get_relations(mock_cursor, "ORDER_DETAIL")

        # Each column gets its own mapping
        assert result["ORDER_ID"] == ("ORDER", "ID")
        assert result["LINE_NUMBER"] == ("ORDER", "LINE_NUMBER")

    # =========================================================================
    # get_constraints tests
    # =========================================================================

    def test_get_constraints_primary_key(self, introspection):
        """Test primary key constraint detection."""
        mock_cursor = MagicMock()

        def mock_execute(sql, params=None):
            if "PRIMARY KEY" in sql and "SELECT" in sql:
                # constraint_name, field_name, index_name, index_type
                mock_cursor.fetchall.return_value = [
                    ("PK_TEST", "ID", "PK_TEST_IDX", 0),  # 0 = ASC
                ]
            else:
                mock_cursor.fetchall.return_value = []

        mock_cursor.execute.side_effect = mock_execute

        result = introspection.get_constraints(mock_cursor, "TEST")

        assert "PK_TEST" in result
        assert result["PK_TEST"]["primary_key"] is True
        assert result["PK_TEST"]["unique"] is True
        assert "ID" in result["PK_TEST"]["columns"]
        assert result["PK_TEST"]["orders"] == ["ASC"]

    def test_get_constraints_unique(self, introspection):
        """Test unique constraint detection."""
        mock_cursor = MagicMock()

        def mock_execute(sql, params=None):
            if "PRIMARY KEY" in sql:
                mock_cursor.fetchall.return_value = []
            elif "UNIQUE" in sql and "RDB$CONSTRAINT_TYPE" in sql:
                # constraint_name, field_name, index_type
                mock_cursor.fetchall.return_value = [
                    ("UQ_EMAIL", "EMAIL", 0),  # 0 = ASC
                ]
            else:
                mock_cursor.fetchall.return_value = []

        mock_cursor.execute.side_effect = mock_execute

        result = introspection.get_constraints(mock_cursor, "TEST")

        assert "UQ_EMAIL" in result
        assert result["UQ_EMAIL"]["unique"] is True
        assert result["UQ_EMAIL"]["primary_key"] is False

    def test_get_constraints_foreign_key(self, introspection):
        """Test foreign key constraint detection."""
        mock_cursor = MagicMock()

        def mock_execute(sql, params=None):
            if "FOREIGN KEY" in sql:
                # constraint_name, field_name, ref_table, ref_field, index_type
                mock_cursor.fetchall.return_value = [
                    ("FK_CUSTOMER_COMPANY", "COMPANY_ID", "COMPANY", "ID", 0),
                ]
            else:
                mock_cursor.fetchall.return_value = []

        mock_cursor.execute.side_effect = mock_execute

        result = introspection.get_constraints(mock_cursor, "CUSTOMER")

        assert "FK_CUSTOMER_COMPANY" in result
        assert result["FK_CUSTOMER_COMPANY"]["foreign_key"] == ("COMPANY", "ID")
        assert result["FK_CUSTOMER_COMPANY"]["primary_key"] is False
