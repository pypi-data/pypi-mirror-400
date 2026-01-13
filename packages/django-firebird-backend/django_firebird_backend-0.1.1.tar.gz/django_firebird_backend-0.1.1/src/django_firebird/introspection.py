"""
Firebird database introspection for Django.

Used by inspectdb command to read existing database schema.
"""

from collections import namedtuple

from django.db.backends.base.introspection import BaseDatabaseIntrospection, TableInfo
from django.db.backends.base.introspection import FieldInfo as BaseFieldInfo

# Extended FieldInfo with Firebird-specific attributes
# Django 5.0+ BaseFieldInfo already has: name, type_code, display_size, internal_size,
# precision, scale, null_ok, default, collation
# We add 'comment' and 'subtype' for Firebird (subtype differentiates BLOB text vs binary)
FieldInfo = namedtuple(
    "FieldInfo",
    BaseFieldInfo._fields + ("comment", "subtype"),
)


class DatabaseIntrospection(BaseDatabaseIntrospection):
    """Firebird database introspection class."""

    # Map Firebird type codes to Django field types
    # Based on RDB$FIELD_TYPE values
    data_types_reverse = {
        7: "SmallIntegerField",  # SMALLINT
        8: "IntegerField",  # INTEGER
        10: "FloatField",  # FLOAT
        12: "DateField",  # DATE
        13: "TimeField",  # TIME
        14: "CharField",  # CHAR
        16: "BigIntegerField",  # BIGINT
        23: "BooleanField",  # BOOLEAN (Firebird 3.0+)
        27: "FloatField",  # DOUBLE PRECISION
        35: "DateTimeField",  # TIMESTAMP
        37: "CharField",  # VARCHAR
        261: "TextField",  # BLOB
    }

    # BLOB subtypes
    BLOB_SUBTYPE_TEXT = 1
    BLOB_SUBTYPE_BINARY = 0

    def get_field_type(self, data_type, description):
        """Return Django field type for Firebird data type."""
        field_type = super().get_field_type(data_type, description)

        # Handle BLOB subtypes
        if data_type == 261 and description.subtype is not None:
            if description.subtype == self.BLOB_SUBTYPE_TEXT:
                return "TextField"
            else:
                return "BinaryField"

        return field_type

    def get_table_list(self, cursor):
        """Return list of tables and views in the database."""
        cursor.execute("""
            SELECT
                TRIM(RDB$RELATION_NAME),
                CASE
                    WHEN RDB$VIEW_SOURCE IS NOT NULL THEN 'v'
                    ELSE 't'
                END
            FROM RDB$RELATIONS
            WHERE RDB$SYSTEM_FLAG = 0
            ORDER BY RDB$RELATION_NAME
        """)
        return [TableInfo(row[0], row[1]) for row in cursor.fetchall()]

    def get_table_description(self, cursor, table_name):
        """Return description of columns in a table."""
        cursor.execute(
            """
            SELECT
                TRIM(rf.RDB$FIELD_NAME),
                f.RDB$FIELD_TYPE,
                f.RDB$FIELD_LENGTH,
                f.RDB$FIELD_PRECISION,
                f.RDB$FIELD_SCALE,
                CASE WHEN rf.RDB$NULL_FLAG = 1 THEN 0 ELSE 1 END,
                rf.RDB$DEFAULT_SOURCE,
                f.RDB$CHARACTER_LENGTH,
                f.RDB$FIELD_SUB_TYPE,
                TRIM(rf.RDB$DESCRIPTION),
                TRIM(rf.RDB$FIELD_SOURCE),
                TRIM(cs.RDB$CHARACTER_SET_NAME)
            FROM RDB$RELATION_FIELDS rf
            JOIN RDB$FIELDS f ON rf.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
            LEFT JOIN RDB$CHARACTER_SETS cs ON f.RDB$CHARACTER_SET_ID = cs.RDB$CHARACTER_SET_ID
            WHERE rf.RDB$RELATION_NAME = ?
            ORDER BY rf.RDB$FIELD_POSITION
        """,
            [table_name.upper()],
        )

        fields = []
        for row in cursor.fetchall():
            name = row[0]
            type_code = row[1]
            length = row[2]
            precision = row[3]
            scale = row[4]
            null_ok = bool(row[5])
            default = row[6]
            char_length = row[7]
            subtype = row[8]
            comment = row[9]
            # row[10] is field_source (domain name), reserved for future use
            collation = row[11]

            # Use character length for string fields
            if type_code in (14, 37):  # CHAR, VARCHAR
                display_size = char_length or length
            else:
                display_size = length

            fields.append(
                FieldInfo(
                    name=name,
                    type_code=type_code,
                    display_size=display_size,
                    internal_size=length,
                    precision=precision,
                    scale=abs(scale) if scale else None,
                    null_ok=null_ok,
                    default=default,
                    collation=collation,
                    comment=comment,
                    subtype=subtype,
                )
            )

        return fields

    def get_primary_key_column(self, cursor, table_name):
        """Return the name of the primary key column."""
        cursor.execute(
            """
            SELECT TRIM(s.RDB$FIELD_NAME)
            FROM RDB$RELATION_CONSTRAINTS rc
            JOIN RDB$INDEX_SEGMENTS s ON rc.RDB$INDEX_NAME = s.RDB$INDEX_NAME
            WHERE rc.RDB$RELATION_NAME = ?
            AND rc.RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
        """,
            [table_name.upper()],
        )

        row = cursor.fetchone()
        return row[0] if row else None

    def get_constraints(self, cursor, table_name):
        """Return dict of constraints for a table."""
        constraints = {}

        # Primary keys
        cursor.execute(
            """
            SELECT
                TRIM(rc.RDB$CONSTRAINT_NAME),
                TRIM(s.RDB$FIELD_NAME),
                TRIM(rc.RDB$INDEX_NAME),
                i.RDB$INDEX_TYPE
            FROM RDB$RELATION_CONSTRAINTS rc
            JOIN RDB$INDEX_SEGMENTS s ON rc.RDB$INDEX_NAME = s.RDB$INDEX_NAME
            JOIN RDB$INDICES i ON rc.RDB$INDEX_NAME = i.RDB$INDEX_NAME
            WHERE rc.RDB$RELATION_NAME = ?
            AND rc.RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
            ORDER BY s.RDB$FIELD_POSITION
        """,
            [table_name.upper()],
        )

        for row in cursor.fetchall():
            constraint_name = row[0]
            column = row[1]
            # index_name = row[2]
            index_type = row[3]  # 0 = ASC, 1 = DESC

            if constraint_name not in constraints:
                constraints[constraint_name] = {
                    "columns": [],
                    "orders": [],
                    "primary_key": True,
                    "unique": True,
                    "foreign_key": None,
                    "check": False,
                    "index": True,
                    "type": "idx",  # Firebird uses B-tree indexes
                }
            constraints[constraint_name]["columns"].append(column)
            constraints[constraint_name]["orders"].append(
                "DESC" if index_type else "ASC"
            )

        # Unique constraints
        cursor.execute(
            """
            SELECT
                TRIM(rc.RDB$CONSTRAINT_NAME),
                TRIM(s.RDB$FIELD_NAME),
                i.RDB$INDEX_TYPE
            FROM RDB$RELATION_CONSTRAINTS rc
            JOIN RDB$INDEX_SEGMENTS s ON rc.RDB$INDEX_NAME = s.RDB$INDEX_NAME
            JOIN RDB$INDICES i ON rc.RDB$INDEX_NAME = i.RDB$INDEX_NAME
            WHERE rc.RDB$RELATION_NAME = ?
            AND rc.RDB$CONSTRAINT_TYPE = 'UNIQUE'
            ORDER BY rc.RDB$CONSTRAINT_NAME, s.RDB$FIELD_POSITION
        """,
            [table_name.upper()],
        )

        for row in cursor.fetchall():
            constraint_name = row[0]
            column = row[1]
            index_type = row[2]

            if constraint_name not in constraints:
                constraints[constraint_name] = {
                    "columns": [],
                    "orders": [],
                    "primary_key": False,
                    "unique": True,
                    "foreign_key": None,
                    "check": False,
                    "index": True,
                    "type": "idx",
                }
            constraints[constraint_name]["columns"].append(column)
            constraints[constraint_name]["orders"].append(
                "DESC" if index_type else "ASC"
            )

        # Foreign keys
        cursor.execute(
            """
            SELECT
                TRIM(rc.RDB$CONSTRAINT_NAME),
                TRIM(s.RDB$FIELD_NAME),
                TRIM(ref_rc.RDB$RELATION_NAME),
                TRIM(ref_s.RDB$FIELD_NAME),
                i.RDB$INDEX_TYPE
            FROM RDB$RELATION_CONSTRAINTS rc
            JOIN RDB$INDEX_SEGMENTS s ON rc.RDB$INDEX_NAME = s.RDB$INDEX_NAME
            JOIN RDB$INDICES i ON rc.RDB$INDEX_NAME = i.RDB$INDEX_NAME
            JOIN RDB$REF_CONSTRAINTS ref ON rc.RDB$CONSTRAINT_NAME = ref.RDB$CONSTRAINT_NAME
            JOIN RDB$RELATION_CONSTRAINTS ref_rc ON ref.RDB$CONST_NAME_UQ = ref_rc.RDB$CONSTRAINT_NAME
            JOIN RDB$INDEX_SEGMENTS ref_s ON ref_rc.RDB$INDEX_NAME = ref_s.RDB$INDEX_NAME
                AND ref_s.RDB$FIELD_POSITION = s.RDB$FIELD_POSITION
            WHERE rc.RDB$RELATION_NAME = ?
            AND rc.RDB$CONSTRAINT_TYPE = 'FOREIGN KEY'
            ORDER BY s.RDB$FIELD_POSITION
        """,
            [table_name.upper()],
        )

        for row in cursor.fetchall():
            constraint_name = row[0]
            column = row[1]
            ref_table = row[2]
            ref_column = row[3]
            index_type = row[4]

            if constraint_name not in constraints:
                constraints[constraint_name] = {
                    "columns": [],
                    "orders": [],
                    "primary_key": False,
                    "unique": False,
                    "foreign_key": (ref_table, ref_column),
                    "check": False,
                    "index": True,
                    "type": "idx",
                }
            constraints[constraint_name]["columns"].append(column)
            constraints[constraint_name]["orders"].append(
                "DESC" if index_type else "ASC"
            )

        # Check constraints
        cursor.execute(
            """
            SELECT
                TRIM(rc.RDB$CONSTRAINT_NAME),
                TRIM(t.RDB$TRIGGER_SOURCE)
            FROM RDB$RELATION_CONSTRAINTS rc
            JOIN RDB$CHECK_CONSTRAINTS cc ON rc.RDB$CONSTRAINT_NAME = cc.RDB$CONSTRAINT_NAME
            JOIN RDB$TRIGGERS t ON cc.RDB$TRIGGER_NAME = t.RDB$TRIGGER_NAME
            WHERE rc.RDB$RELATION_NAME = ?
            AND rc.RDB$CONSTRAINT_TYPE = 'CHECK'
        """,
            [table_name.upper()],
        )

        for row in cursor.fetchall():
            constraint_name = row[0]
            constraints[constraint_name] = {
                "columns": [],
                "orders": [],
                "primary_key": False,
                "unique": False,
                "foreign_key": None,
                "check": True,
                "index": False,
                "type": "",
            }

        # Indexes (non-constraint)
        cursor.execute(
            """
            SELECT
                TRIM(i.RDB$INDEX_NAME),
                TRIM(s.RDB$FIELD_NAME),
                i.RDB$UNIQUE_FLAG,
                i.RDB$INDEX_TYPE
            FROM RDB$INDICES i
            JOIN RDB$INDEX_SEGMENTS s ON i.RDB$INDEX_NAME = s.RDB$INDEX_NAME
            WHERE i.RDB$RELATION_NAME = ?
            AND i.RDB$SYSTEM_FLAG = 0
            AND NOT EXISTS (
                SELECT 1 FROM RDB$RELATION_CONSTRAINTS rc
                WHERE rc.RDB$INDEX_NAME = i.RDB$INDEX_NAME
            )
            ORDER BY i.RDB$INDEX_NAME, s.RDB$FIELD_POSITION
        """,
            [table_name.upper()],
        )

        for row in cursor.fetchall():
            index_name = row[0]
            column = row[1]
            unique = bool(row[2])
            index_type = row[3]

            if index_name not in constraints:
                constraints[index_name] = {
                    "columns": [],
                    "orders": [],
                    "primary_key": False,
                    "unique": unique,
                    "foreign_key": None,
                    "check": False,
                    "index": True,
                    "type": "idx",
                }
            constraints[index_name]["columns"].append(column)
            constraints[index_name]["orders"].append("DESC" if index_type else "ASC")

        return constraints

    def get_relations(self, cursor, table_name):
        """
        Return dict mapping column names to (referenced_table, referenced_column).
        Used by inspectdb to generate ForeignKey fields.
        """
        cursor.execute(
            """
            SELECT
                TRIM(s.RDB$FIELD_NAME),
                TRIM(ref_rc.RDB$RELATION_NAME),
                TRIM(ref_s.RDB$FIELD_NAME)
            FROM RDB$RELATION_CONSTRAINTS rc
            JOIN RDB$INDEX_SEGMENTS s ON rc.RDB$INDEX_NAME = s.RDB$INDEX_NAME
            JOIN RDB$REF_CONSTRAINTS ref ON rc.RDB$CONSTRAINT_NAME = ref.RDB$CONSTRAINT_NAME
            JOIN RDB$RELATION_CONSTRAINTS ref_rc ON ref.RDB$CONST_NAME_UQ = ref_rc.RDB$CONSTRAINT_NAME
            JOIN RDB$INDEX_SEGMENTS ref_s ON ref_rc.RDB$INDEX_NAME = ref_s.RDB$INDEX_NAME
                AND ref_s.RDB$FIELD_POSITION = s.RDB$FIELD_POSITION
            WHERE rc.RDB$RELATION_NAME = ?
            AND rc.RDB$CONSTRAINT_TYPE = 'FOREIGN KEY'
        """,
            [table_name.upper()],
        )

        relations = {}
        for row in cursor.fetchall():
            column = row[0]
            ref_table = row[1]
            ref_column = row[2]
            relations[column] = (ref_table, ref_column)

        return relations

    def get_sequences(self, cursor, table_name, table_fields=()):
        """Return list of sequences for table's auto-increment fields."""
        sequences = []
        for field in table_fields:
            if field.primary_key:
                seq_name = self.connection.ops._get_generator_name(
                    table_name, field.column
                )
                sequences.append(
                    {"name": seq_name, "table": table_name, "column": field.column}
                )
        return sequences
