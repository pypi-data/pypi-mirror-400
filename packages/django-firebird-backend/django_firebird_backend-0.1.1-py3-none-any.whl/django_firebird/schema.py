"""
Firebird database schema editor for Django.

Handles DDL operations like CREATE TABLE, ALTER TABLE, etc.
"""

from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.backends.ddl_references import (
    Expressions,
    IndexName,
    Statement,
    Table,
)
from django.db.models.sql import Query


class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):
    """Firebird-specific schema editor."""

    # SQL templates
    sql_create_table = "CREATE TABLE %(table)s (%(definition)s)"
    sql_delete_table = "DROP TABLE %(table)s"
    sql_rename_table = "/* Firebird does not support RENAME TABLE */"

    sql_create_column = "ALTER TABLE %(table)s ADD %(column)s %(definition)s"
    sql_alter_column = "ALTER TABLE %(table)s ALTER COLUMN %(column)s"
    sql_delete_column = "ALTER TABLE %(table)s DROP %(column)s"
    sql_rename_column = (
        "ALTER TABLE %(table)s ALTER COLUMN %(old_column)s TO %(new_column)s"
    )

    sql_create_fk = (
        "ALTER TABLE %(table)s ADD CONSTRAINT %(name)s "
        "FOREIGN KEY (%(column)s) REFERENCES %(to_table)s (%(to_column)s)"
    )
    sql_delete_fk = "ALTER TABLE %(table)s DROP CONSTRAINT %(name)s"

    sql_create_pk = (
        "ALTER TABLE %(table)s ADD CONSTRAINT %(name)s PRIMARY KEY (%(columns)s)"
    )
    sql_delete_pk = "ALTER TABLE %(table)s DROP CONSTRAINT %(name)s"

    sql_create_unique = (
        "ALTER TABLE %(table)s ADD CONSTRAINT %(name)s UNIQUE (%(columns)s)"
    )
    sql_delete_unique = "ALTER TABLE %(table)s DROP CONSTRAINT %(name)s"

    sql_create_check = "ALTER TABLE %(table)s ADD CONSTRAINT %(name)s CHECK (%(check)s)"
    sql_delete_check = "ALTER TABLE %(table)s DROP CONSTRAINT %(name)s"

    # Index templates - Firebird supports partial indexes with WHERE clause
    sql_create_index = "CREATE INDEX %(name)s ON %(table)s (%(columns)s)%(condition)s"
    sql_create_unique_index = (
        "CREATE UNIQUE INDEX %(name)s ON %(table)s (%(columns)s)%(condition)s"
    )
    # Expression indexes use COMPUTED BY syntax in Firebird
    sql_create_expression_index = (
        "CREATE INDEX %(name)s ON %(table)s COMPUTED BY (%(expressions)s)%(condition)s"
    )
    sql_create_unique_expression_index = "CREATE UNIQUE INDEX %(name)s ON %(table)s COMPUTED BY (%(expressions)s)%(condition)s"
    sql_delete_index = "DROP INDEX %(name)s"

    sql_create_sequence = "CREATE SEQUENCE %(name)s"
    sql_delete_sequence = "DROP SEQUENCE %(name)s"
    sql_alter_sequence = "ALTER SEQUENCE %(name)s RESTART WITH %(value)s"

    def quote_value(self, value):
        """Quote a value for use in DDL SQL."""
        if isinstance(value, str):
            return "'{}'".format(value.replace("'", "''"))
        elif isinstance(value, bool):
            return "1" if value else "0"
        elif value is None:
            return "NULL"
        else:
            return str(value)

    def _create_sequence_sql(self, table, column):
        """Return SQL to create a sequence for auto-increment field."""
        seq_name = self.connection.ops._get_generator_name(table, column)
        return self.sql_create_sequence % {"name": self.quote_name(seq_name)}

    def _create_trigger_sql(self, table, column):
        """Return SQL to create a trigger for auto-increment field."""
        seq_name = self.connection.ops._get_generator_name(table, column)
        trigger_name = self.connection.ops._get_trigger_name(table, column)

        return (
            f"CREATE TRIGGER {self.quote_name(trigger_name)} "
            f"FOR {self.quote_name(table)} "
            f"ACTIVE BEFORE INSERT POSITION 0 "
            f"AS BEGIN "
            f"IF (NEW.{self.quote_name(column)} IS NULL) THEN "
            f"NEW.{self.quote_name(column)} = NEXT VALUE FOR {self.quote_name(seq_name)}; "
            f"END"
        )

    def _delete_sequence_sql(self, table, column):
        """Return SQL to delete a sequence."""
        seq_name = self.connection.ops._get_generator_name(table, column)
        return self.sql_delete_sequence % {"name": self.quote_name(seq_name)}

    def _delete_trigger_sql(self, table, column):
        """Return SQL to delete a trigger."""
        trigger_name = self.connection.ops._get_trigger_name(table, column)
        return f"DROP TRIGGER {self.quote_name(trigger_name)}"

    def create_model(self, model):
        """Create a table for the model."""
        # Create table
        super().create_model(model)

        # Create sequences and triggers for auto-increment fields
        for field in model._meta.local_fields:
            if field.get_internal_type() in (
                "AutoField",
                "BigAutoField",
                "SmallAutoField",
            ):
                self.execute(
                    self._create_sequence_sql(model._meta.db_table, field.column)
                )
                self.execute(
                    self._create_trigger_sql(model._meta.db_table, field.column)
                )

    def delete_model(self, model):
        """Delete a table for the model."""
        # Delete triggers and sequences first
        for field in model._meta.local_fields:
            if field.get_internal_type() in (
                "AutoField",
                "BigAutoField",
                "SmallAutoField",
            ):
                try:
                    self.execute(
                        self._delete_trigger_sql(model._meta.db_table, field.column)
                    )
                except Exception:
                    pass
                try:
                    self.execute(
                        self._delete_sequence_sql(model._meta.db_table, field.column)
                    )
                except Exception:
                    pass

        # Delete table
        super().delete_model(model)

    def add_field(self, model, field):
        """Add a field to a table."""
        super().add_field(model, field)

        # Create sequence/trigger for auto-increment fields
        if field.get_internal_type() in ("AutoField", "BigAutoField", "SmallAutoField"):
            self.execute(self._create_sequence_sql(model._meta.db_table, field.column))
            self.execute(self._create_trigger_sql(model._meta.db_table, field.column))

    def remove_field(self, model, field):
        """Remove a field from a table."""
        # Delete trigger/sequence for auto-increment fields
        if field.get_internal_type() in ("AutoField", "BigAutoField", "SmallAutoField"):
            try:
                self.execute(
                    self._delete_trigger_sql(model._meta.db_table, field.column)
                )
            except Exception:
                pass
            try:
                self.execute(
                    self._delete_sequence_sql(model._meta.db_table, field.column)
                )
            except Exception:
                pass

        super().remove_field(model, field)

    def column_sql(self, model, field, include_default=False):
        """
        Return SQL to define a column.
        Handle BLOB fields specially (no default allowed).
        """
        sql, params = super().column_sql(model, field, include_default=False)

        # BLOB fields cannot have defaults in Firebird
        if field.get_internal_type() in ("TextField", "BinaryField"):
            include_default = False

        # Add default for non-BLOB fields
        if include_default:
            default_value = self.effective_default(field)
            if default_value is not None:
                sql += f" DEFAULT {self.quote_value(default_value)}"

        return sql, params

    def _alter_column_type_sql(self, model, old_field, new_field, new_type):
        """Return SQL to alter a column's type."""
        return (
            (
                self.sql_alter_column
                % {
                    "table": self.quote_name(model._meta.db_table),
                    "column": self.quote_name(new_field.column),
                }
            )
            + " TYPE "
            + new_type,
            [],
        )

    def _alter_column_null_sql(self, model, old_field, new_field):
        """Return SQL to set/unset NULL constraint."""
        if new_field.null:
            return (
                (
                    self.sql_alter_column
                    % {
                        "table": self.quote_name(model._meta.db_table),
                        "column": self.quote_name(new_field.column),
                    }
                )
                + " DROP NOT NULL",
                [],
            )
        else:
            return (
                (
                    self.sql_alter_column
                    % {
                        "table": self.quote_name(model._meta.db_table),
                        "column": self.quote_name(new_field.column),
                    }
                )
                + " SET NOT NULL",
                [],
            )

    def _alter_column_default_sql(self, model, old_field, new_field, drop=False):
        """Return SQL to set/drop column default."""
        if drop:
            return (
                (
                    self.sql_alter_column
                    % {
                        "table": self.quote_name(model._meta.db_table),
                        "column": self.quote_name(new_field.column),
                    }
                )
                + " DROP DEFAULT",
                [],
            )
        else:
            default_value = self.effective_default(new_field)
            return (
                (
                    self.sql_alter_column
                    % {
                        "table": self.quote_name(model._meta.db_table),
                        "column": self.quote_name(new_field.column),
                    }
                )
                + " SET DEFAULT "
                + self.quote_value(default_value),
                [],
            )

    def prepare_default(self, value):
        """Format default value for SQL."""
        return self.quote_value(value)

    def _create_index_sql(
        self,
        model,
        *,
        fields=None,
        name=None,
        suffix="",
        using="",
        db_tablespace=None,
        col_suffixes=(),
        sql=None,
        opclasses=(),
        condition=None,
        include=None,
        expressions=None,
    ):
        """
        Return the SQL statement to create the index.

        Firebird uses COMPUTED BY for expression indexes instead of
        putting expressions in the column list.
        """
        if expressions:
            # Expression index - use COMPUTED BY syntax
            compiler = Query(model, alias_cols=False).get_compiler(
                connection=self.connection,
            )
            table = model._meta.db_table
            columns = [field.column for field in (fields or [])]

            # Determine which SQL template to use
            if sql is None:
                sql = self.sql_create_expression_index

            def create_index_name(*args, **kwargs):
                nonlocal name
                if name is None:
                    name = self._create_index_name(*args, **kwargs)
                return self.quote_name(name)

            return Statement(
                sql,
                table=Table(table, self.quote_name),
                name=IndexName(table, columns, suffix, create_index_name),
                expressions=Expressions(table, expressions, compiler, self.quote_value),
                condition=self._index_condition_sql(condition),
            )

        # Regular column index - use parent implementation
        return super()._create_index_sql(
            model,
            fields=fields,
            name=name,
            suffix=suffix,
            using=using,
            db_tablespace=db_tablespace,
            col_suffixes=col_suffixes,
            sql=sql,
            opclasses=opclasses,
            condition=condition,
            include=include,
            expressions=expressions,
        )

    def _field_should_be_altered(self, old_field, new_field):
        """Check if field needs alteration."""
        # Don't detect changes for auto-increment fields
        if old_field.get_internal_type() in (
            "AutoField",
            "BigAutoField",
            "SmallAutoField",
        ):
            return False
        return super()._field_should_be_altered(old_field, new_field)
