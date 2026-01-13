"""
MCP resource implementations for XuguDB schema and metadata.
"""
import json
from typing import Optional

from ..config.settings import get_settings
from ..db import operations
from ..utils.logging import get_logger

# Import schema tools functions
import xugu_mcp.mcp_tools.schema_tools as schema_tools

logger = get_logger(__name__)


async def get_tables_resource(
    schema: Optional[str] = None,
    include_system: bool = False,
) -> str:
    """Get tables catalog as resource.

    Args:
        schema: Schema filter
        include_system: Include system tables

    Returns:
        JSON string of tables catalog
    """
    try:
        tables = operations.list_tables(schema or "SYSTEM", include_system)
        return json.dumps({
            "schema": schema or "SYSTEM",
            "include_system": include_system,
            "tables": tables,
            "count": len(tables),
        }, indent=2)
    except Exception as e:
        logger.error(f"Get tables resource failed: {e}")
        return json.dumps({"error": str(e)})


async def get_table_resource(table_name: str, schema: Optional[str] = None) -> str:
    """Get detailed table schema as resource.

    Args:
        table_name: Table name
        schema: Schema name

    Returns:
        JSON string of table schema
    """
    try:
        table_info = operations.get_table_info(table_name)
        return json.dumps(table_info, indent=2, default=str)
    except Exception as e:
        logger.error(f"Get table resource failed: {e}")
        return json.dumps({"error": str(e)})


async def get_relationships_resource(
    table_name: Optional[str] = None,
    schema: Optional[str] = None,
) -> str:
    """Get foreign key relationships as resource.

    Args:
        table_name: Optional table name filter
        schema: Schema name

    Returns:
        JSON string of relationships
    """
    try:
        result = await schema_tools.get_foreign_keys(table_name, schema)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Get relationships resource failed: {e}")
        return json.dumps({"error": str(e)})


async def get_indexes_resource(
    table_name: Optional[str] = None,
    schema: Optional[str] = None,
) -> str:
    """Get indexes as resource.

    Args:
        table_name: Optional table name filter
        schema: Schema name

    Returns:
        JSON string of indexes
    """
    try:
        result = await schema_tools.list_indexes(table_name, schema)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Get indexes resource failed: {e}")
        return json.dumps({"error": str(e)})


async def get_views_resource(schema: Optional[str] = None) -> str:
    """Get views as resource.

    Args:
        schema: Schema name

    Returns:
        JSON string of views
    """
    try:
        result = await schema_tools.list_views(schema)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Get views resource failed: {e}")
        return json.dumps({"error": str(e)})


async def get_database_info_resource() -> str:
    """Get database information as resource.

    Returns:
        JSON string of database info
    """
    try:
        info = operations.get_database_info()
        return json.dumps(info, indent=2, default=str)
    except Exception as e:
        logger.error(f"Get database info resource failed: {e}")
        return json.dumps({"error": str(e)})


async def get_database_stats_resource() -> str:
    """Get database statistics as resource.

    Returns:
        JSON string of database stats
    """
    try:
        settings = get_settings()
        tables = operations.list_tables(settings.xugu.database, False)

        # Get stats for each table
        stats = {"database": settings.xugu.database, "tables": []}
        for table in tables[:50]:  # Limit to first 50 tables
            try:
                count_result = operations.execute_query(
                    f"SELECT COUNT(*) FROM {table['table_name']}"
                )
                row_count = count_result.rows[0][0] if count_result.rows else 0
                stats["tables"].append({
                    "table_name": table["table_name"],
                    "row_count": row_count,
                })
            except Exception:
                pass

        return json.dumps(stats, indent=2, default=str)
    except Exception as e:
        logger.error(f"Get database stats resource failed: {e}")
        return json.dumps({"error": str(e)})
