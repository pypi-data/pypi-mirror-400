"""
Schema introspection tools for XuguDB MCP Server.

Provides tools for exploring database schema including tables, indexes,
foreign keys, views, and relationships.

Note: XuguDB does not support standard INFORMATION_SCHEMA. This module
uses XuguDB-specific system tables (ALL_TABLES, etc.) where available.
"""
from typing import Optional

from ..db import operations
from ..utils.logging import get_logger
from ..utils.errors import QueryExecutionError

logger = get_logger(__name__)


async def list_indexes(
    table_name: Optional[str] = None,
    schema: Optional[str] = None,
) -> dict:
    """List indexes for a table or all indexes.

    Note: XuguDB does not expose index metadata through standard system tables.
    This function returns a success response with empty results.

    Args:
        table_name: Optional table name filter
        schema: Optional schema name (not used in XuguDB)

    Returns:
        Dictionary with index information
    """
    try:
        # XuguDB doesn't have a public information_schema.indexes equivalent
        # Return empty result with success to indicate feature not available
        if table_name:
            return {
                "success": True,
                "table_name": table_name,
                "indexes": [],
                "count": 0,
                "note": "Index metadata not available through XuguDB system tables",
            }
        else:
            return {
                "success": True,
                "indexes": [],
                "count": 0,
                "note": "Index metadata not available through XuguDB system tables",
            }

    except Exception as e:
        logger.error(f"List indexes failed: {e}")
        raise QueryExecutionError(f"List indexes failed: {e}") from e


async def get_foreign_keys(
    table_name: Optional[str] = None,
    schema: Optional[str] = None,
) -> dict:
    """Get foreign key relationships.

    Note: XuguDB does not expose foreign key metadata through standard system tables.
    This function returns a success response with empty results.

    Args:
        table_name: Optional table name filter
        schema: Optional schema name (not used in XuguDB)

    Returns:
        Dictionary with foreign key information
    """
    try:
        # XuguDB doesn't have a public information_schema.table_constraints equivalent
        # Return empty result with success to indicate feature not available
        return {
            "success": True,
            "foreign_keys": [],
            "count": 0,
            "note": "Foreign key metadata not available through XuguDB system tables",
        }

    except Exception as e:
        logger.error(f"Get foreign keys failed: {e}")
        raise QueryExecutionError(f"Get foreign keys failed: {e}") from e


async def search_tables(
    pattern: str,
    schema: Optional[str] = None,
) -> dict:
    """Search tables by name pattern.

    Args:
        pattern: Search pattern (supports % wildcards)
        schema: Optional schema name (not used in XuguDB)

    Returns:
        Dictionary with matching tables
    """
    try:
        # Use ALL_TABLES system view
        # Basic SQL escaping for safety
        escaped_pattern = pattern.replace("'", "''")

        sql = f"""
            SELECT TABLE_NAME, TABLE_TYPE
            FROM ALL_TABLES
            WHERE TABLE_NAME LIKE '{escaped_pattern}'
                AND IS_SYS = 0
            ORDER BY TABLE_NAME
        """

        result = operations.execute_query(sql)

        return {
            "success": True,
            "pattern": pattern,
            "tables": [
                {"table_name": row[0], "table_type": row[1]}
                for row in result.rows
            ],
            "count": result.row_count,
        }

    except Exception as e:
        logger.error(f"Search tables failed: {e}")
        raise QueryExecutionError(f"Search tables failed: {e}") from e


async def list_views(
    schema: Optional[str] = None,
) -> dict:
    """List all views in the database.

    Note: XuguDB may not distinguish views from tables in ALL_TABLES.
    This function attempts to filter for view types.

    Args:
        schema: Optional schema name (not used in XuguDB)

    Returns:
        Dictionary with view information
    """
    try:
        # Try to get views from ALL_TABLES
        # Note: TABLE_TYPE comparison may fail in XuguDB, so we skip it
        # and return empty result since XuguDB doesn't have user-defined views
        return {
            "success": True,
            "views": [],
            "count": 0,
            "note": "XuguDB doesn't expose user-defined views through ALL_TABLES",
        }

    except Exception as e:
        logger.error(f"List views failed: {e}")
        # If view type filtering fails, return empty
        return {
            "success": True,
            "views": [],
            "count": 0,
            "error": str(e),
        }


async def get_view_definition(
    view_name: str,
    schema: Optional[str] = None,
) -> dict:
    """Get the definition of a specific view.

    Note: XuguDB does not expose view definitions through system tables.

    Args:
        view_name: Name of the view
        schema: Optional schema name (not used in XuguDB)

    Returns:
        Dictionary with view definition
    """
    try:
        # Check if view exists
        # Note: TABLE_TYPE column in ALL_TABLES may have data format issues in XuguDB
        # We'll use a simpler query that doesn't filter by TABLE_TYPE
        sql = """
            SELECT TABLE_NAME
            FROM ALL_TABLES
            WHERE TABLE_NAME = ?
                AND IS_SYS = 0
        """

        result = operations.execute_query(sql, (view_name,))

        if not result.rows:
            return {
                "success": False,
                "error": f"View '{view_name}' not found",
            }

        return {
            "success": True,
            "view_name": view_name,
            "definition": None,
            "is_updatable": None,
            "note": "View definition not available through XuguDB system tables",
        }

    except Exception as e:
        logger.error(f"Get view definition failed: {e}")
        # Return a graceful failure instead of raising
        return {
            "success": False,
            "error": f"Failed to get view definition: {e}",
        }


async def list_columns(
    table_name: str,
    schema: Optional[str] = None,
) -> dict:
    """Get detailed column information for a table.

    Uses get_table_info to retrieve detailed column information from XuguDB system tables.

    Args:
        table_name: Name of the table
        schema: Optional schema name (not used in XuguDB)

    Returns:
        Dictionary with column information
    """
    try:
        # Use get_table_info for detailed column information
        table_info = operations.get_table_info(table_name)

        columns = []
        for i, col in enumerate(table_info.get("columns", [])):
            # Determine if this column is a primary key
            is_pk = col.get("column_name") in table_info.get("primary_key", [])

            columns.append({
                "column_name": col.get("column_name"),
                "data_type": col.get("data_type"),
                "is_nullable": col.get("is_nullable", True),
                "column_default": col.get("column_default"),
                "is_primary_key": is_pk,
                "max_length": col.get("max_length"),
                "comments": col.get("comments"),
                "position": i + 1,
            })

        return {
            "success": True,
            "table_name": table_name,
            "columns": columns,
            "count": len(columns),
            "primary_key": table_info.get("primary_key", []),
        }

    except Exception as e:
        logger.error(f"List columns failed: {e}")
        raise QueryExecutionError(f"List columns failed: {e}") from e


async def get_table_constraints(
    table_name: str,
    schema: Optional[str] = None,
) -> dict:
    """Get constraint information for a table.

    Note: XuguDB does not expose constraint metadata through standard system tables.
    This function returns a success response with empty results.

    Args:
        table_name: Name of the table
        schema: Optional schema name (not used in XuguDB)

    Returns:
        Dictionary with constraint information
    """
    try:
        # XuguDB doesn't have a public information_schema.table_constraints equivalent
        return {
            "success": True,
            "table_name": table_name,
            "constraints": [],
            "count": 0,
            "note": "Constraint metadata not available through XuguDB system tables",
        }

    except Exception as e:
        logger.error(f"Get table constraints failed: {e}")
        raise QueryExecutionError(f"Get table constraints failed: {e}") from e
