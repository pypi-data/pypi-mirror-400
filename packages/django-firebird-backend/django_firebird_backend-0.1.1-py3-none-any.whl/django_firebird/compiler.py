"""
Firebird SQL compiler for Django.

Handles SQL generation for SELECT, INSERT, UPDATE, DELETE.
"""

from django.db.models.sql import compiler


class SQLCompiler(compiler.SQLCompiler):
    """Firebird SQL compiler for SELECT queries."""

    def as_sql(self, with_limits=True, with_col_aliases=False):
        """
        Generate SQL for SELECT statement.

        Firebird uses FIRST/SKIP instead of LIMIT/OFFSET.
        The FIRST/SKIP must come right after SELECT.
        """
        refcounts_before = self.query.alias_refcount.copy()
        try:
            result, params = super().as_sql(
                with_limits=False, with_col_aliases=with_col_aliases
            )

            # Add FIRST/SKIP for limiting
            if with_limits and (
                self.query.high_mark is not None or self.query.low_mark
            ):
                limit_sql = self.connection.ops.limit_offset_sql(
                    self.query.low_mark, self.query.high_mark
                )
                if limit_sql:
                    # Insert FIRST/SKIP after SELECT keyword
                    if result.upper().startswith("SELECT DISTINCT"):
                        result = "SELECT DISTINCT " + limit_sql + result[15:]
                    elif result.upper().startswith("SELECT"):
                        result = "SELECT " + limit_sql + result[6:]

            return result, params
        finally:
            self.query.alias_refcount = refcounts_before


class SQLInsertCompiler(compiler.SQLInsertCompiler):
    """Firebird SQL compiler for INSERT queries."""

    def as_sql(self):
        """
        Generate SQL for INSERT statement with RETURNING clause.
        """
        result = super().as_sql()

        # If we have a pk and RETURNING is supported, add it
        if (
            self.returning_fields
            and self.connection.features.can_return_columns_from_insert
        ):
            # Result is a list of (sql, params) tuples
            new_result = []
            for sql, params in result:
                returning_columns = ", ".join(
                    self.connection.ops.quote_name(field.column)
                    for field in self.returning_fields
                )
                # Only add RETURNING if not already present
                if "RETURNING" not in sql.upper():
                    sql = f"{sql} RETURNING {returning_columns}"
                new_result.append((sql, params))
            return new_result

        return result


class SQLDeleteCompiler(compiler.SQLDeleteCompiler):
    """Firebird SQL compiler for DELETE queries."""

    pass


class SQLUpdateCompiler(compiler.SQLUpdateCompiler):
    """Firebird SQL compiler for UPDATE queries."""

    pass


class SQLAggregateCompiler(compiler.SQLAggregateCompiler):
    """Firebird SQL compiler for aggregate queries."""

    pass
