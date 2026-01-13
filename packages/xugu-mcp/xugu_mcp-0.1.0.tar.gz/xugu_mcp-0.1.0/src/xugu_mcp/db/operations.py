"""
Database operation wrappers for XuguDB.
"""
from typing import Any, Optional
from dataclasses import dataclass

import xgcondb

from .connection import get_connection_manager
from ..utils.errors import QueryExecutionError
from ..utils.logging import get_logger

logger = get_logger(__name__)


def _get_xugu_version() -> str:
    """Get XuguDB driver version.

    Returns:
        Version string or "unknown" if not available
    """
    try:
        # Try to get version from module attribute
        if hasattr(xgcondb, "version"):
            v = xgcondb.version
            if callable(v):
                return str(v())
            return str(v)
        # Check server_version attribute
        if hasattr(xgcondb, "server_version"):
            return str(xgcondb.server_version)
    except Exception:
        pass
    return "unknown"


@dataclass
class QueryResult:
    """Result of a query execution."""

    columns: list[str]
    rows: list[tuple]
    row_count: int
    execution_time: float

    def to_dict_list(self) -> list[dict[str, Any]]:
        """Convert rows to list of dictionaries.

        Returns:
            List of row dictionaries
        """
        return [dict(zip(self.columns, row)) for row in self.rows]


def execute_query(
    sql: str,
    params: Optional[tuple | list | dict] = None,
    max_rows: Optional[int] = None,
) -> QueryResult:
    """Execute a SELECT query.

    Args:
        sql: SQL SELECT statement
        params: Optional query parameters
        max_rows: Maximum rows to return

    Returns:
        QueryResult with columns, rows, and metadata

    Raises:
        QueryExecutionError: If query fails
    """
    import time

    conn_mgr = get_connection_manager()
    start_time = time.time()

    try:
        cursor = conn_mgr.execute(sql, params)

        try:
            # Get column names from cursor description
            columns = []
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]

            # Fetch results
            rows = cursor.fetchall()

            # Apply max_rows limit
            if max_rows and len(rows) > max_rows:
                logger.warning(f"Result set truncated to {max_rows} rows")
                rows = rows[:max_rows]

            execution_time = time.time() - start_time

            return QueryResult(
                columns=columns,
                rows=rows,
                row_count=len(rows),
                execution_time=execution_time,
            )
        finally:
            # 确保游标被关闭
            cursor.close()

    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise QueryExecutionError(
            f"Query execution failed: {e}", sql=sql, details={"params": params}
        ) from e


def execute_non_query(
    sql: str,
    params: Optional[tuple | list | dict] = None,
) -> int:
    """Execute a non-SELECT statement (INSERT, UPDATE, DELETE, DDL).

    Args:
        sql: SQL statement
        params: Optional statement parameters

    Returns:
        Number of affected rows

    Raises:
        QueryExecutionError: If execution fails
    """
    conn_mgr = get_connection_manager()

    try:
        cursor = conn_mgr.execute(sql, params)
        try:
            row_count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            logger.info(f"Statement executed, {row_count} rows affected")
            return row_count
        finally:
            cursor.close()

    except Exception as e:
        logger.error(f"Statement execution failed: {e}")
        raise QueryExecutionError(
            f"Statement execution failed: {e}", sql=sql, details={"params": params}
        ) from e


def execute_batch(
    sql: str,
    params_list: list[tuple] | list[dict],
) -> int:
    """Execute a statement multiple times with different parameters.

    Args:
        sql: SQL statement
        params_list: List of parameter tuples/dicts

    Returns:
        Total number of affected rows

    Raises:
        QueryExecutionError: If execution fails
    """
    conn_mgr = get_connection_manager()

    try:
        conn_mgr.execute_many(sql, params_list)
        # Note: xgcondb may not return accurate rowcount for executemany
        return len(params_list)

    except Exception as e:
        logger.error(f"Batch execution failed: {e}")
        raise QueryExecutionError(
            f"Batch execution failed: {e}",
            sql=sql,
            details={"row_count": len(params_list)},
        ) from e


def get_table_info(table_name: str) -> dict[str, Any]:
    """Get detailed information about a table.

    Args:
        table_name: Table name

    Returns:
        Dictionary with table information

    Raises:
        QueryExecutionError: If query fails
    """
    try:
        # First get column names from querying the table (for cursor description)
        columns_sql = f"SELECT * FROM {table_name} WHERE 1=0"
        columns_result = execute_query(columns_sql)

        # Try to get detailed column info from XuguDB system tables
        columns = []
        try:
            # Query SYS_COLUMNS for detailed column information
            detail_sql = """
                SELECT c.COL_NAME, c.TYPE_NAME, c.NOT_NULL, c.DEF_VAL, c.COMMENTS, c.SCALE
                FROM SYS_TABLES t, SYS_COLUMNS c
                WHERE t.TABLE_ID = c.TABLE_ID
                    AND t.TABLE_NAME = ?
                ORDER BY c.COL_NO
            """
            detail_result = execute_query(detail_sql, (table_name,))

            # Build a map of column details
            col_details = {}
            for row in detail_result.rows:
                col_name = row[0]
                col_details[col_name] = {
                    "column_name": col_name,
                    "data_type": row[1],  # TYPE_NAME
                    "is_nullable": not row[2],  # NOT_NULL -> nullable
                    "column_default": row[3],  # DEF_VAL
                    "comments": row[4],  # COMMENTS
                    "max_length": row[5] if row[5] and row[5] > 0 else None,  # SCALE
                }

            # Merge cursor description with detailed info
            for col_name in columns_result.columns:
                if col_name in col_details:
                    columns.append(col_details[col_name])
                else:
                    # Fallback for columns not in SYS_COLUMNS
                    columns.append({
                        "column_name": col_name,
                        "data_type": "UNKNOWN",
                        "is_nullable": True,
                        "column_default": None,
                        "comments": "",
                        "max_length": None,
                    })
        except Exception as e:
            # Fallback: use cursor description only
            logger.debug(f"Failed to get column details from SYS_COLUMNS: {e}")
            for col_name in columns_result.columns:
                columns.append({
                    "column_name": col_name,
                    "data_type": "UNKNOWN",
                    "is_nullable": True,
                    "column_default": None,
                    "comments": "",
                    "max_length": None,
                })

        # Try to get primary key from XuguDB system tables if available
        primary_keys = []
        try:
            # XuguDB stores index info in SYS_INDEXES with KEYS column containing column names
            # IS_PRIMARY = 1 (or True) indicates primary key
            pk_sql = """
                SELECT i.KEYS
                FROM SYS_INDEXES i, SYS_TABLES t
                WHERE i.TABLE_ID = t.TABLE_ID
                    AND t.TABLE_NAME = ?
                    AND i.IS_PRIMARY = 1
            """
            pk_result = execute_query(pk_sql, (table_name,))
            if pk_result.rows:
                # KEYS column contains quoted column name like '"COLUMN_NAME"'
                # Parse and unquote the column names
                for row in pk_result.rows:
                    keys_str = row[0]  # e.g., '"COL1","COL2"' or '"COL1"'
                    if keys_str:
                        # Remove quotes and split by comma
                        import re
                        # Match quoted strings
                        keys = re.findall(r'"([^"]+)"', keys_str)
                        primary_keys.extend(keys)
        except Exception as e:
            # If system table query fails, leave empty
            logger.debug(f"Failed to get primary key info: {e}")
            pass

        # Foreign keys - not available through XuguDB system tables
        foreign_keys = []

        return {
            "table_name": table_name,
            "columns": columns,
            "primary_key": primary_keys,
            "foreign_keys": foreign_keys,
        }

    except Exception as e:
        logger.error(f"Failed to get table info for {table_name}: {e}")
        raise QueryExecutionError(f"Failed to get table info: {e}") from e


def list_tables(
    schema: Optional[str] = None,
    include_system: bool = False,
) -> list[dict[str, Any]]:
    """List all tables in the database.

    Args:
        schema: Optional schema filter (not used in XuguDB, kept for compatibility)
        include_system: Whether to include system tables

    Returns:
        List of table information dictionaries

    Raises:
        QueryExecutionError: If query fails
    """
    # XuguDB uses ALL_TABLES system view instead of information_schema.tables
    # The schema parameter is not used (XuguDB doesn't support schema filtering)
    # IS_SYS = 0 表示用户表, IS_SYS = 1 表示系统表
    _ = schema  # Mark as intentionally unused
    if include_system:
        sql = """
            SELECT TABLE_NAME, TABLE_TYPE
            FROM ALL_TABLES
            ORDER BY TABLE_NAME
        """
        result = execute_query(sql)
    else:
        sql = """
            SELECT TABLE_NAME, TABLE_TYPE
            FROM ALL_TABLES
            WHERE IS_SYS = 0
            ORDER BY TABLE_NAME
        """
        result = execute_query(sql)

    return [
        {"table_name": row[0], "table_type": row[1]} for row in result.rows
    ]


def get_database_info() -> dict[str, Any]:
    """Get database information.

    Returns:
        Dictionary with database information including:
        - Driver version (xgcondb version)
        - Database instance info (from SHOW DB_INFO)
        - Database version (from SHOW VERSION and SHOW VERSION_NUM)

    Raises:
        QueryExecutionError: If query fails
    """
    conn_mgr = get_connection_manager()

    try:
        # Get driver version (xgcondb version)
        driver_version = _get_xugu_version()

        # Get database version info
        db_version = None
        db_version_num = None
        try:
            result = execute_query("SHOW VERSION")
            if result.rows and len(result.rows) > 0:
                db_version = result.rows[0][0]  # VERSION string
        except Exception as e:
            logger.debug(f"Failed to get VERSION: {e}")

        try:
            result = execute_query("SHOW VERSION_NUM")
            if result.rows and len(result.rows) > 0:
                db_version_num = result.rows[0][0]  # VERSION_NUM integer
        except Exception as e:
            logger.debug(f"Failed to get VERSION_NUM: {e}")

        # Get database instance info using SHOW DB_INFO
        db_info = {}
        try:
            result = execute_query("SHOW DB_INFO")
            if result.rows and len(result.rows) > 0:
                row = result.rows[0]
                # DB_INFO returns: DB_NAME, DB_ID, DB_OWNER, DB_CHARSET, DB_TIMEZ
                db_info = {
                    "db_name": row[0],      # Database name
                    "db_id": row[1],        # Database ID
                    "db_owner": row[2],     # Database owner
                    "db_charset": row[3],   # Database charset
                    "db_timezone": row[4],  # Database timezone
                }
        except Exception as e:
            logger.debug(f"Failed to get DB_INFO: {e}")

        return {
            # Driver/connection info (xgcondb version)
            "driver_version": driver_version,
            "database": conn_mgr._settings.xugu.database,
            "host": conn_mgr._settings.xugu.host,
            "port": conn_mgr._settings.xugu.port,
            "connected": conn_mgr.is_connected,
            # Database version info (from SHOW VERSION/VERSION_NUM)
            "db_version": db_version,
            "db_version_num": db_version_num,
            # Database instance info (from SHOW DB_INFO)
            "db_info": db_info if db_info else None,
        }

    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        raise QueryExecutionError(f"Failed to get database info: {e}") from e
