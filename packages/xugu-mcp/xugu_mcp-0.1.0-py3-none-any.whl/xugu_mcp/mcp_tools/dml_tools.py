"""
DML (Data Manipulation Language) tools for XuguDB MCP Server.

Provides tools for INSERT, UPDATE, DELETE, and UPSERT operations.
"""
from typing import Any
from dataclasses import dataclass

from ..db import operations
from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class DMLResult:
    """Result of a DML operation."""

    success: bool
    rows_affected: int
    message: str
    error: str | None = None


async def insert_rows(
    table_name: str,
    rows: list[dict[str, Any]] | dict[str, Any],
) -> DMLResult:
    """Insert single or multiple rows into a table.

    Args:
        table_name: Name of the table
        rows: Dictionary or list of dictionaries with column-value pairs

    Returns:
        DMLResult with operation status
    """
    try:
        # Normalize to list
        if isinstance(rows, dict):
            rows = [rows]

        if not rows:
            return DMLResult(
                success=False,
                rows_affected=0,
                message="No rows to insert",
            )

        # Get column names from first row
        columns = list(rows[0].keys())
        if not columns:
            return DMLResult(
                success=False,
                rows_affected=0,
                message="No columns specified",
            )

        # Build INSERT statement with parameter placeholders
        placeholders = ", ".join(["?"] * len(columns))
        columns_str = ", ".join(columns)
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

        # Prepare parameters
        params_list = [tuple(row.get(col) for col in columns) for row in rows]

        # Execute
        row_count = operations.execute_batch(sql, params_list)

        return DMLResult(
            success=True,
            rows_affected=row_count,
            message=f"Inserted {row_count} row(s) into {table_name}",
        )

    except Exception as e:
        logger.error(f"Insert rows failed: {e}")
        return DMLResult(
            success=False,
            rows_affected=0,
            message="Insert failed",
            error=str(e),
        )


async def update_rows(
    table_name: str,
    updates: dict[str, Any],
    where: str | None = None,
    where_params: list | tuple | None = None,
) -> DMLResult:
    """Update rows matching the WHERE condition.

    Args:
        table_name: Name of the table
        updates: Dictionary of column-value pairs to update
        where: Optional WHERE clause (without WHERE keyword)
        where_params: Optional parameters for WHERE clause

    Returns:
        DMLResult with operation status
    """
    try:
        if not updates:
            return DMLResult(
                success=False,
                rows_affected=0,
                message="No columns specified for update",
            )

        # Build SET clause
        set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
        sql = f"UPDATE {table_name} SET {set_clause}"

        # Add WHERE clause if provided
        params = list(updates.values())
        if where:
            sql += f" WHERE {where}"
            if where_params:
                if isinstance(where_params, (list, tuple)):
                    params.extend(where_params)
                else:
                    params.append(where_params)

        # Execute
        row_count = operations.execute_non_query(sql, tuple(params) if params else None)

        return DMLResult(
            success=True,
            rows_affected=row_count,
            message=f"Updated {row_count} row(s) in {table_name}",
        )

    except Exception as e:
        logger.error(f"Update rows failed: {e}")
        return DMLResult(
            success=False,
            rows_affected=0,
            message="Update failed",
            error=str(e),
        )


async def delete_rows(
    table_name: str,
    where: str | None = None,
    where_params: list | tuple | None = None,
) -> DMLResult:
    """Delete rows matching the WHERE condition.

    Args:
        table_name: Name of the table
        where: WHERE clause (without WHERE keyword)
        where_params: Optional parameters for WHERE clause

    Returns:
        DMLResult with operation status

    Warning:
        If no WHERE clause is provided, ALL rows will be deleted!
    """
    try:
        sql = f"DELETE FROM {table_name}"

        params = None
        if where:
            sql += f" WHERE {where}"
            if where_params:
                params = tuple(where_params) if isinstance(where_params, (list, tuple)) else (where_params,)

        # Safety warning for DELETE without WHERE
        if not where:
            logger.warning(f"DELETE without WHERE clause on {table_name} - this will delete all rows!")

        # Execute
        row_count = operations.execute_non_query(sql, params)

        return DMLResult(
            success=True,
            rows_affected=row_count,
            message=f"Deleted {row_count} row(s) from {table_name}",
        )

    except Exception as e:
        logger.error(f"Delete rows failed: {e}")
        return DMLResult(
            success=False,
            rows_affected=0,
            message="Delete failed",
            error=str(e),
        )


async def upsert_rows(
    table_name: str,
    rows: list[dict[str, Any]] | dict[str, Any],
    constraint: str | None = None,
) -> DMLResult:
    """Insert or update rows (UPSERT operation).

    For XuguDB, this uses MERGE or INSERT...ON DUPLICATE KEY UPDATE pattern.

    Args:
        table_name: Name of the table
        rows: Dictionary or list of dictionaries with column-value pairs
        constraint: Optional constraint name for conflict resolution

    Returns:
        DMLResult with operation status
    """
    try:
        # Normalize to list
        if isinstance(rows, dict):
            rows = [rows]

        if not rows:
            return DMLResult(
                success=False,
                rows_affected=0,
                message="No rows to upsert",
            )

        # Get column names from first row
        columns = list(rows[0].keys())
        if not columns:
            return DMLResult(
                success=False,
                rows_affected=0,
                message="No columns specified",
            )

        # Try insert first, then update if conflict
        inserted = 0
        updated = 0
        errors = []

        for row in rows:
            try:
                placeholders = ", ".join(["?"] * len(columns))
                columns_str = ", ".join(columns)
                sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                params = tuple(row.get(col) for col in columns)

                count = operations.execute_non_query(sql, params)
                inserted += count

            except Exception as e:
                # If insert fails (duplicate key), try update
                error_str = str(e).lower()
                if "duplicate" in error_str or "unique" in error_str or "primary" in error_str:
                    try:
                        # Build UPDATE clause
                        set_clause = ", ".join([f"{col} = ?" for col in columns])

                        # Build WHERE clause for primary key columns
                        # Note: This is a simplified approach - you may need to adjust
                        where_conditions = [f"{col} = ?" for col in columns]
                        sql = f"UPDATE {table_name} SET {set_clause} WHERE {' AND '.join(where_conditions)}"
                        params = tuple(row.get(col) for col in columns) * 2  # For SET and WHERE

                        count = operations.execute_non_query(sql, params)
                        updated += count

                    except Exception as update_error:
                        errors.append(str(update_error))
                else:
                    errors.append(str(e))

        total_affected = inserted + updated

        return DMLResult(
            success=len(errors) == 0 or total_affected > 0,
            rows_affected=total_affected,
            message=f"Upserted into {table_name}: {inserted} inserted, {updated} updated",
            error="; ".join(errors) if errors else None,
        )

    except Exception as e:
        logger.error(f"Upsert rows failed: {e}")
        return DMLResult(
            success=False,
            rows_affected=0,
            message="Upsert failed",
            error=str(e),
        )


async def truncate_table(
    table_name: str,
) -> DMLResult:
    """Truncate a table (fast delete all rows).

    Args:
        table_name: Name of the table

    Returns:
        DMLResult with operation status
    """
    try:
        sql = f"TRUNCATE TABLE {table_name}"
        operations.execute_non_query(sql)

        return DMLResult(
            success=True,
            rows_affected=0,  # TRUNCATE doesn't return row count
            message=f"Truncated table {table_name}",
        )

    except Exception as e:
        logger.error(f"Truncate table failed: {e}")
        return DMLResult(
            success=False,
            rows_affected=0,
            message="Truncate failed",
            error=str(e),
        )


async def bulk_import(
    table_name: str,
    data: list[dict[str, Any]],
    batch_size: int = 1000,
) -> DMLResult:
    """Bulk import data into a table in batches.

    Args:
        table_name: Name of the table
        data: List of dictionaries with column-value pairs
        batch_size: Number of rows per batch

    Returns:
        DMLResult with operation status
    """
    try:
        if not data:
            return DMLResult(
                success=False,
                rows_affected=0,
                message="No data to import",
            )

        total_rows = len(data)
        total_imported = 0
        batches = (total_rows + batch_size - 1) // batch_size

        for i in range(batches):
            start_idx = i * batch_size
            end_idx = min(start_idx + batch_size, total_rows)
            batch = data[start_idx:end_idx]

            result = await insert_rows(table_name, batch)
            if result.success:
                total_imported += result.rows_affected
            else:
                return DMLResult(
                    success=False,
                    rows_affected=total_imported,
                    message=f"Bulk import failed at batch {i+1}/{batches}",
                    error=result.error,
                )

        return DMLResult(
            success=True,
            rows_affected=total_imported,
            message=f"Bulk imported {total_imported}/{total_rows} rows into {table_name} in {batches} batch(es)",
        )

    except Exception as e:
        logger.error(f"Bulk import failed: {e}")
        return DMLResult(
            success=False,
            rows_affected=0,
            message="Bulk import failed",
            error=str(e),
        )
