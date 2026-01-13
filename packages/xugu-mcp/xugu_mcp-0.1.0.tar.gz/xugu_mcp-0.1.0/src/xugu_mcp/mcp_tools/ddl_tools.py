"""
DDL (Data Definition Language) tools for XuguDB MCP Server.

Provides tools for CREATE, ALTER, DROP operations on databases, tables, indexes, and views.
"""
from typing import Any
from dataclasses import dataclass

from ..db import operations
from ..utils.logging import get_logger
from ..utils.helpers import sanitize_table_name

logger = get_logger(__name__)


@dataclass
class DDLResult:
    """Result of a DDL operation."""

    success: bool
    message: str
    object_name: str | None = None
    object_type: str | None = None
    error: str | None = None


async def create_database(
    database_name: str,
    if_not_exists: bool = True,
) -> DDLResult:
    """Create a new database.

    Args:
        database_name: Name of the database to create
        if_not_exists: Add IF NOT EXISTS clause

    Returns:
        DDLResult with operation status
    """
    try:
        # Validate database name
        database_name = database_name.strip().upper()
        if not database_name:
            return DDLResult(
                success=False,
                message="Database name cannot be empty",
                error="Invalid database name"
            )

        # Build CREATE DATABASE statement
        if_exists = "IF NOT EXISTS " if if_not_exists else ""
        sql = f"CREATE DATABASE {if_exists}{database_name}"

        operations.execute_non_query(sql)

        logger.info(f"Database '{database_name}' created successfully")

        return DDLResult(
            success=True,
            message=f"Database '{database_name}' created successfully",
            object_name=database_name,
            object_type="database",
        )

    except Exception as e:
        logger.error(f"Failed to create database '{database_name}': {e}")
        return DDLResult(
            success=False,
            message=f"Failed to create database '{database_name}'",
            object_name=database_name,
            object_type="database",
            error=str(e),
        )


async def drop_database(
    database_name: str,
    if_exists: bool = True,
    cascade: bool = False,
) -> DDLResult:
    """Drop a database.

    Args:
        database_name: Name of the database to drop
        if_exists: Add IF EXISTS clause
        cascade: Drop all objects in the database

    Returns:
        DDLResult with operation status
    """
    try:
        # Validate database name
        database_name = database_name.strip().upper()
        if not database_name:
            return DDLResult(
                success=False,
                message="Database name cannot be empty",
                error="Invalid database name"
            )

        # Build DROP DATABASE statement
        if_exists_clause = "IF EXISTS " if if_exists else ""
        cascade_clause = " CASCADE" if cascade else ""
        sql = f"DROP DATABASE {if_exists_clause}{database_name}{cascade_clause}"

        operations.execute_non_query(sql)

        logger.info(f"Database '{database_name}' dropped successfully")

        return DDLResult(
            success=True,
            message=f"Database '{database_name}' dropped successfully",
            object_name=database_name,
            object_type="database",
        )

    except Exception as e:
        logger.error(f"Failed to drop database '{database_name}': {e}")
        return DDLResult(
            success=False,
            message=f"Failed to drop database '{database_name}'",
            object_name=database_name,
            object_type="database",
            error=str(e),
        )


async def create_schema(
    schema_name: str,
    if_not_exists: bool = True,
) -> DDLResult:
    """Create a new schema.

    Args:
        schema_name: Name of the schema to create
        if_not_exists: Check if schema exists before creating (XuguDB doesn't support IF NOT EXISTS)

    Returns:
        DDLResult with operation status
    """
    try:
        # Validate schema name
        schema_name = schema_name.strip().upper()
        if not schema_name:
            return DDLResult(
                success=False,
                message="Schema name cannot be empty",
                error="Invalid schema name"
            )

        # Check if schema exists (XuguDB doesn't support IF NOT EXISTS)
        if if_not_exists:
            try:
                check_sql = f"SELECT 1 FROM ALL_USERS WHERE USER_NAME = '{schema_name}'"
                result = operations.execute_query(check_sql)
                if result.rows and len(result.rows) > 0:
                    return DDLResult(
                        success=True,
                        message=f"Schema '{schema_name}' already exists",
                        object_name=schema_name,
                        object_type="schema",
                    )
            except Exception:
                # If check fails, continue with CREATE
                pass

        # Build CREATE SCHEMA statement (without IF NOT EXISTS)
        sql = f"CREATE SCHEMA {schema_name}"

        operations.execute_non_query(sql)

        logger.info(f"Schema '{schema_name}' created successfully")

        return DDLResult(
            success=True,
            message=f"Schema '{schema_name}' created successfully",
            object_name=schema_name,
            object_type="schema",
        )

    except Exception as e:
        logger.error(f"Failed to create schema '{schema_name}': {e}")
        return DDLResult(
            success=False,
            message=f"Failed to create schema '{schema_name}'",
            object_name=schema_name,
            object_type="schema",
            error=str(e),
        )


async def drop_schema(
    schema_name: str,
    if_exists: bool = True,
    cascade: bool = False,
) -> DDLResult:
    """Drop a schema.

    Args:
        schema_name: Name of the schema to drop
        if_exists: Check if schema exists before dropping (XuguDB doesn't support IF EXISTS)
        cascade: Drop all objects in the schema

    Returns:
        DDLResult with operation status
    """
    try:
        # Validate schema name
        schema_name = schema_name.strip().upper()
        if not schema_name:
            return DDLResult(
                success=False,
                message="Schema name cannot be empty",
                error="Invalid schema name"
            )

        # Check if schema exists (XuguDB doesn't support IF EXISTS)
        if if_exists:
            try:
                check_sql = f"SELECT 1 FROM ALL_USERS WHERE USER_NAME = '{schema_name}'"
                result = operations.execute_query(check_sql)
                if not result.rows or len(result.rows) == 0:
                    return DDLResult(
                        success=True,
                        message=f"Schema '{schema_name}' does not exist",
                        object_name=schema_name,
                        object_type="schema",
                    )
            except Exception:
                # If check fails, continue with DROP
                pass

        # Build DROP SCHEMA statement (without IF EXISTS)
        cascade_clause = " CASCADE" if cascade else ""
        sql = f"DROP SCHEMA {schema_name}{cascade_clause}"

        operations.execute_non_query(sql)

        logger.info(f"Schema '{schema_name}' dropped successfully")

        return DDLResult(
            success=True,
            message=f"Schema '{schema_name}' dropped successfully",
            object_name=schema_name,
            object_type="schema",
        )

    except Exception as e:
        logger.error(f"Failed to drop schema '{schema_name}': {e}")
        return DDLResult(
            success=False,
            message=f"Failed to drop schema '{schema_name}'",
            object_name=schema_name,
            object_type="schema",
            error=str(e),
        )


async def create_table(
    table_name: str,
    columns: dict[str, str],
    primary_key: list[str] | str | None = None,
    constraints: list[dict] | None = None,
    if_not_exists: bool = True,
) -> DDLResult:
    """Create a new table.

    Args:
        table_name: Name of the table to create
        columns: Dictionary mapping column names to data types
                  Format: {"column_name": "DATA_TYPE", ...}
        primary_key: Optional primary key column(s)
        constraints: Optional list of constraint definitions
        if_not_exists: Add IF NOT EXISTS clause

    Returns:
        DDLResult with operation status
    """
    try:
        # Validate table name
        table_name = sanitize_table_name(table_name)

        # Build column definitions
        col_defs = []
        for col_name, col_type in columns.items():
            col_defs.append(f"{col_name} {col_type}")

        # Add primary key constraint
        if primary_key:
            if isinstance(primary_key, str):
                primary_key = [primary_key]
            pk_cols = ", ".join(primary_key)
            col_defs.append(f"PRIMARY KEY ({pk_cols})")

        # Add additional constraints
        if constraints:
            for constraint in constraints:
                if constraint.get("type") == "foreign_key":
                    fk_cols = constraint["columns"]
                    ref_table = constraint["ref_table"]
                    ref_cols = constraint["ref_columns"]
                    col_defs.append(
                        f"FOREIGN KEY ({fk_cols}) REFERENCES {ref_table}({ref_cols})"
                    )
                elif constraint.get("type") == "unique":
                    unique_cols = constraint["columns"]
                    col_defs.append(f"UNIQUE ({unique_cols})")
                elif constraint.get("type") == "check":
                    check_expr = constraint["expression"]
                    col_defs.append(f"CHECK ({check_expr})")

        # Build CREATE TABLE statement
        col_def_str = ",\n    ".join(col_defs)
        if_not_exists_clause = "IF NOT EXISTS " if if_not_exists else ""
        sql = f"CREATE TABLE {if_not_exists_clause}{table_name} (\n    {col_def_str}\n)"

        # Execute
        operations.execute_non_query(sql)

        return DDLResult(
            success=True,
            message=f"Table '{table_name}' created successfully",
            object_name=table_name,
            object_type="TABLE",
        )

    except Exception as e:
        logger.error(f"Create table failed: {e}")
        return DDLResult(
            success=False,
            message=f"Failed to create table '{table_name}'",
            object_name=table_name,
            object_type="TABLE",
            error=str(e),
        )


async def drop_table(
    table_name: str,
    cascade: bool = False,
    if_exists: bool = True,
) -> DDLResult:
    """Drop a table.

    Args:
        table_name: Name of the table to drop
        cascade: Drop dependent objects (CASCADE)
        if_exists: Add IF EXISTS clause

    Returns:
        DDLResult with operation status
    """
    try:
        table_name = sanitize_table_name(table_name)

        if_exists_clause = "IF EXISTS " if if_exists else ""
        cascade_clause = " CASCADE" if cascade else ""
        sql = f"DROP TABLE {if_exists_clause}{table_name}{cascade_clause}"

        operations.execute_non_query(sql)

        return DDLResult(
            success=True,
            message=f"Table '{table_name}' dropped successfully",
            object_name=table_name,
            object_type="TABLE",
        )

    except Exception as e:
        logger.error(f"Drop table failed: {e}")
        return DDLResult(
            success=False,
            message=f"Failed to drop table '{table_name}'",
            object_name=table_name,
            object_type="TABLE",
            error=str(e),
        )


async def alter_table(
    table_name: str,
    action: str,
    alterations: dict[str, Any] | None = None,
) -> DDLResult:
    """Alter table structure.

    Args:
        table_name: Name of the table to alter
        action: Type of alteration (ADD_COLUMN, DROP_COLUMN, ALTER_COLUMN,
                RENAME_COLUMN, ADD_CONSTRAINT, DROP_CONSTRAINT, RENAME)
        alterations: Dictionary of alteration parameters

    Returns:
        DDLResult with operation status
    """
    try:
        table_name = sanitize_table_name(table_name)

        # Ensure alterations is not None
        if alterations is None:
            alterations = {}

        if action == "ADD_COLUMN":
            # Add a new column
            col_name = alterations.get("column_name")
            col_type = alterations.get("data_type")
            nullable = alterations.get("nullable", True)
            default = alterations.get("default")

            col_def = f"{col_name} {col_type}"
            if not nullable:
                col_def += " NOT NULL"
            if default is not None:
                col_def += f" DEFAULT {default}"

            sql = f"ALTER TABLE {table_name} ADD COLUMN {col_def}"

        elif action == "DROP_COLUMN":
            col_name = alterations.get("column_name")
            sql = f"ALTER TABLE {table_name} DROP COLUMN {col_name}"

        elif action == "ALTER_COLUMN":
            col_name = alterations.get("column_name")
            new_type = alterations.get("data_type")
            nullable = alterations.get("nullable")
            default = alterations.get("default")

            # XuguDB doesn't support ALTER COLUMN with TYPE clause
            # It uses MODIFY COLUMN syntax instead (similar to MySQL)
            if new_type:
                # Build MODIFY clause for XuguDB
                mod_clause = f"{col_name} {new_type}"
                if nullable is not None:
                    mod_clause += "" if nullable else " NOT NULL"
                if default is not None:
                    mod_clause += f" DEFAULT {default}"
                sql = f"ALTER TABLE {table_name} MODIFY COLUMN {mod_clause}"
            else:
                # For nullable/default changes only (not supported in XuguDB)
                modifications = []
                if nullable is not None:
                    # XuguDB doesn't support SET/DROP NOT NULL syntax
                    modifications.append("SET NOT NULL" if not nullable else "DROP NOT NULL")
                if default is not None:
                    modifications.append(f"SET DEFAULT {default}")

                if modifications:
                    mod_str = ", ".join(modifications)
                    sql = f"ALTER TABLE {table_name} ALTER COLUMN {col_name} {mod_str}"
                else:
                    return DDLResult(
                        success=False,
                        message="ALTER_COLUMN requires at least one of: data_type, nullable, default",
                        object_name=table_name,
                        object_type="TABLE",
                        error="No valid modification specified",
                    )

        elif action == "RENAME_COLUMN":
            old_name = alterations.get("old_column_name")
            new_name = alterations.get("new_column_name")
            sql = f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name}"

        elif action == "RENAME":
            new_table_name = alterations.get("new_table_name")
            if new_table_name is None:
                return DDLResult(
                    success=False,
                    message="RENAME action requires 'new_table_name' parameter",
                    object_name=table_name,
                    object_type="TABLE",
                    error="Missing required parameter: new_table_name",
                )
            new_table_name = sanitize_table_name(new_table_name)
            sql = f"ALTER TABLE {table_name} RENAME TO {new_table_name}"
            table_name = new_table_name  # Update for result message

        elif action == "ADD_CONSTRAINT":
            constraint_def = alterations.get("constraint_definition")
            sql = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_def}"

        elif action == "DROP_CONSTRAINT":
            constraint_name = alterations.get("constraint_name")
            sql = f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name}"

        else:
            return DDLResult(
                success=False,
                message=f"Unknown ALTER action: {action}",
                object_name=table_name,
                object_type="TABLE",
                error=f"Action '{action}' is not supported",
            )

        # Execute
        operations.execute_non_query(sql)

        return DDLResult(
            success=True,
            message=f"Table '{table_name}' altered successfully ({action})",
            object_name=table_name,
            object_type="TABLE",
        )

    except Exception as e:
        logger.error(f"Alter table failed: {e}")
        return DDLResult(
            success=False,
            message=f"Failed to alter table '{table_name}'",
            object_name=table_name,
            object_type="TABLE",
            error=str(e),
        )


async def create_index(
    index_name: str,
    table_name: str,
    columns: list[str] | str,
    unique: bool = False,
    if_not_exists: bool = True,
) -> DDLResult:
    """Create an index on a table.

    Args:
        index_name: Name of the index to create
        table_name: Name of the table
        columns: Column(s) to index
        unique: Whether to create a UNIQUE index
        if_not_exists: Add IF NOT EXISTS clause

    Returns:
        DDLResult with operation status
    """
    try:
        table_name = sanitize_table_name(table_name)
        index_name = sanitize_table_name(index_name)

        if isinstance(columns, str):
            columns = [columns]

        index_cols = ", ".join(columns)

        unique_clause = "UNIQUE " if unique else ""
        if_not_exists_clause = "IF NOT EXISTS " if if_not_exists else ""

        sql = f"CREATE {unique_clause}INDEX {if_not_exists_clause}{index_name} ON {table_name} ({index_cols})"

        operations.execute_non_query(sql)

        return DDLResult(
            success=True,
            message=f"Index '{index_name}' created successfully on table '{table_name}'",
            object_name=index_name,
            object_type="INDEX",
        )

    except Exception as e:
        logger.error(f"Create index failed: {e}")
        return DDLResult(
            success=False,
            message=f"Failed to create index '{index_name}'",
            object_name=index_name,
            object_type="INDEX",
            error=str(e),
        )


async def drop_index(
    index_name: str,
    table_name: str | None = None,
    if_exists: bool = True,
) -> DDLResult:
    """Drop an index.

    Args:
        index_name: Name of the index to drop
        table_name: Table name (required for XuguDB)
        if_exists: Add IF EXISTS clause (not supported by XuguDB)

    Returns:
        DDLResult with operation status
    """
    try:
        index_name = sanitize_table_name(index_name)

        # XuguDB uses Oracle-style syntax: DROP INDEX table_name.index_name
        # IF EXISTS is not supported by XuguDB
        if not table_name:
            return DDLResult(
                success=False,
                message=f"Table name is required for DROP INDEX in XuguDB",
                object_name=index_name,
                object_type="INDEX",
                error="Table name is required for DROP INDEX in XuguDB",
            )

        sql = f"DROP INDEX {table_name}.{index_name}"

        operations.execute_non_query(sql)

        return DDLResult(
            success=True,
            message=f"Index '{index_name}' on table '{table_name}' dropped successfully",
            object_name=index_name,
            object_type="INDEX",
        )

    except Exception as e:
        logger.error(f"Drop index failed: {e}")
        return DDLResult(
            success=False,
            message=f"Failed to drop index '{index_name}'",
            object_name=index_name,
            object_type="INDEX",
            error=str(e),
        )


async def create_view(
    view_name: str,
    select_statement: str,
    columns: list[str] | None = None,
    if_not_exists: bool = True,
) -> DDLResult:
    """Create a view.

    Args:
        view_name: Name of the view to create
        select_statement: SELECT statement for the view
        columns: Optional column names for the view
        if_not_exists: Add IF NOT EXISTS clause

    Returns:
        DDLResult with operation status
    """
    try:
        view_name = sanitize_table_name(view_name)

        # Ensure SELECT statement starts with SELECT
        select_statement = select_statement.strip()
        if not select_statement.upper().startswith("SELECT"):
            return DDLResult(
                success=False,
                message="SELECT statement must start with SELECT",
                object_name=view_name,
                object_type="VIEW",
                error="Invalid SELECT statement",
            )

        col_clause = ""
        if columns:
            col_names = ", ".join(columns)
            col_clause = f" ({col_names})"

        if_not_exists_clause = "IF NOT EXISTS " if if_not_exists else ""
        sql = f"CREATE VIEW {if_not_exists_clause}{view_name}{col_clause} AS {select_statement}"

        operations.execute_non_query(sql)

        return DDLResult(
            success=True,
            message=f"View '{view_name}' created successfully",
            object_name=view_name,
            object_type="VIEW",
        )

    except Exception as e:
        logger.error(f"Create view failed: {e}")
        return DDLResult(
            success=False,
            message=f"Failed to create view '{view_name}'",
            object_name=view_name,
            object_type="VIEW",
            error=str(e),
        )


async def drop_view(
    view_name: str,
    cascade: bool = False,
    if_exists: bool = True,
) -> DDLResult:
    """Drop a view.

    Args:
        view_name: Name of the view to drop
        cascade: Drop dependent objects
        if_exists: Add IF EXISTS clause

    Returns:
        DDLResult with operation status
    """
    try:
        view_name = sanitize_table_name(view_name)

        if_exists_clause = "IF EXISTS " if if_exists else ""
        cascade_clause = " CASCADE" if cascade else ""
        sql = f"DROP VIEW {if_exists_clause}{view_name}{cascade_clause}"

        operations.execute_non_query(sql)

        return DDLResult(
            success=True,
            message=f"View '{view_name}' dropped successfully",
            object_name=view_name,
            object_type="VIEW",
        )

    except Exception as e:
        logger.error(f"Drop view failed: {e}")
        return DDLResult(
            success=False,
            message=f"Failed to drop view '{view_name}'",
            object_name=view_name,
            object_type="VIEW",
            error=str(e),
        )


async def rename_table(
    old_name: str,
    new_name: str,
) -> DDLResult:
    """Rename a table.

    Args:
        old_name: Current table name
        new_name: New table name

    Returns:
        DDLResult with operation status
    """
    return await alter_table(
        old_name,
        "RENAME",
        alterations={"new_table_name": new_name},
    )


async def backup_table(
    table_name: str,
    backup_name: str | None = None,
) -> DDLResult:
    """Create a backup of a table by copying it.

    Args:
        table_name: Name of the table to backup
        backup_name: Optional name for the backup table

    Returns:
        DDLResult with operation status
    """
    try:
        if not backup_name:
            backup_name = f"{table_name}_backup"

        backup_name = sanitize_table_name(backup_name)

        # Create table as select
        sql = f"CREATE TABLE {backup_name} AS SELECT * FROM {table_name}"

        operations.execute_non_query(sql)

        return DDLResult(
            success=True,
            message=f"Table '{table_name}' backed up as '{backup_name}'",
            object_name=backup_name,
            object_type="TABLE",
        )

    except Exception as e:
        logger.error(f"Backup table failed: {e}")
        return DDLResult(
            success=False,
            message=f"Failed to backup table '{table_name}'",
            object_name=table_name,
            object_type="TABLE",
            error=str(e),
        )
