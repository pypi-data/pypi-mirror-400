"""
XuguDB MCP Server - Main Entry Point

A Model Context Protocol server for XuguDB (虚谷数据库)
with Chat2SQL support and full DDL/DML operations.

FIXED VERSION: Uses single call_tool dispatcher instead of multiple decorators.
"""
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource
from pydantic import AnyUrl

from .config.settings import get_settings
from .db.connection import get_connection_manager, close_connection
from .db import operations
from .mcp_resources import schema_resources
from .utils.logging import get_mcp_logger
from .utils.errors import QueryExecutionError

# Import tool modules for MCP tool implementations
import xugu_mcp.mcp_tools.schema_tools as schema_tools
import xugu_mcp.mcp_tools.dml_tools as dml_tools
import xugu_mcp.mcp_tools.ddl_tools as ddl_tools
import xugu_mcp.mcp_tools.chat2sql_tools as chat2sql_tools
import xugu_mcp.mcp_tools.chat2sql_lightweight_tools as chat2sql_light_tools
import xugu_mcp.mcp_tools.audit_tools as audit_tools
import xugu_mcp.mcp_tools.admin_tools as admin_tools

# Initialize logger
mcp_logger = get_mcp_logger()
logger = mcp_logger.get_logger(__name__)

# Get settings
settings = get_settings()

# Create MCP server instance
server = Server(
    name=settings.mcp_server.name,
    version=settings.mcp_server.version,
)


# =============================================================================
# Tool Handler Functions (without @server.call_tool decorators)
# =============================================================================

async def execute_query_handler(arguments: dict) -> list[TextContent]:
    """Execute a SELECT query and return results."""
    try:
        sql = arguments["sql"]
        params = arguments.get("params", None)
        limit = arguments.get("limit", None)
        max_rows = limit or settings.security.result_set_max_rows
        result = operations.execute_query(sql, tuple(params) if params else None, max_rows)

        output = {
            "success": True,
            "columns": result.columns,
            "rows": result.rows,
            "row_count": result.row_count,
            "execution_time": result.execution_time,
        }

        return [TextContent(type="text", text=str(output))]

    except QueryExecutionError as e:
        logger.error(f"Query execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {e.message}")]

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")]


async def list_tables_handler(arguments: dict) -> list[TextContent]:
    """List all tables in the database."""
    try:
        schema = arguments.get("schema", None)
        include_system = arguments.get("include_system", False)
        tables = operations.list_tables(schema or settings.xugu.database, include_system)

        output = {
            "success": True,
            "tables": tables,
            "count": len(tables),
        }

        return [TextContent(type="text", text=str(output))]

    except Exception as e:
        logger.error(f"List tables failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def get_database_info_handler(arguments: dict) -> list[TextContent]:
    """Get database version and information."""
    try:
        info = operations.get_database_info()

        output = {
            "success": True,
            "info": info,
        }

        return [TextContent(type="text", text=str(output))]

    except Exception as e:
        logger.error(f"Get database info failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


# =============================================================================
# Unified Tool Dispatcher
# =============================================================================

# Map of tool names to their handler functions
TOOL_HANDLERS: dict[str, callable] = {
    # Query Execution Tools
    "execute_query": execute_query_handler,
    "explain_query": lambda args: _explain_query_handler(args),
    "execute_batch": lambda args: _execute_batch_handler(args),

    # Schema Introspection Tools
    "list_tables": list_tables_handler,
    "describe_table": lambda args: _describe_table_handler(args),
    "get_table_stats": lambda args: _get_table_stats_handler(args),
    "list_indexes": lambda args: _list_indexes_handler(args),
    "get_foreign_keys": lambda args: _get_foreign_keys_handler(args),
    "search_tables": lambda args: _search_tables_handler(args),
    "list_views": lambda args: _list_views_handler(args),
    "list_columns": lambda args: _list_columns_handler(args),

    # DML Operation Tools
    "insert_rows": lambda args: _insert_rows_handler(args),
    "update_rows": lambda args: _update_rows_handler(args),
    "delete_rows": lambda args: _delete_rows_handler(args),
    "upsert_rows": lambda args: _upsert_rows_handler(args),
    "truncate_table": lambda args: _truncate_table_handler(args),
    "bulk_import": lambda args: _bulk_import_handler(args),

    # DDL Operation Tools
    "create_database": lambda args: _create_database_handler(args),
    "drop_database": lambda args: _drop_database_handler(args),
    "create_schema": lambda args: _create_schema_handler(args),
    "drop_schema": lambda args: _drop_schema_handler(args),
    "create_table": lambda args: _create_table_handler(args),
    "drop_table": lambda args: _drop_table_handler(args),
    "alter_table": lambda args: _alter_table_handler(args),
    "create_index": lambda args: _create_index_handler(args),
    "drop_index": lambda args: _drop_index_handler(args),
    "create_view": lambda args: _create_view_handler(args),
    "drop_view": lambda args: _drop_view_handler(args),
    "backup_table": lambda args: _backup_table_handler(args),

    # Database Info Tools
    "get_database_info": get_database_info_handler,

    # Chat2SQL Tools
    "natural_language_query": lambda args: _natural_language_query_handler(args),
    "explain_sql": lambda args: _explain_sql_handler(args),
    "suggest_query": lambda args: _suggest_query_handler(args),
    "validate_sql": lambda args: _validate_sql_handler(args),
    "optimize_query": lambda args: _optimize_query_handler(args),
    "fix_sql": lambda args: _fix_sql_handler(args),
    "get_schema_context": lambda args: _get_schema_context_handler(args),
    "clear_schema_cache": lambda args: _clear_schema_cache_handler(args),
    "get_schema_info": lambda args: _get_schema_info_tool_handler(args),

    # Chat2SQL Lightweight Tools (no internal LLM required)
    "get_schema_for_llm": lambda args: _get_schema_for_llm_handler(args),
    "validate_sql_only": lambda args: _validate_sql_only_handler(args),
    "execute_validated_sql": lambda args: _execute_validated_sql_handler(args),
    "get_table_schema_for_llm": lambda args: _get_table_schema_for_llm_handler(args),
    "suggest_sql_from_schema": lambda args: _suggest_sql_from_schema_handler(args),
    "get_lightweight_mode_info": lambda args: _get_lightweight_mode_info_handler(args),

    # Security & Audit Tools
    "get_audit_log": lambda args: _get_audit_log_handler(args),
    "get_audit_statistics": lambda args: _get_audit_statistics_handler(args),
    "get_rate_limit_stats": lambda args: _get_rate_limit_stats_handler(args),
    "list_roles": lambda args: _list_roles_handler(args),
    "get_role_details": lambda args: _get_role_details_handler(args),
    "check_permission": lambda args: _check_permission_handler(args),
    "get_security_status": lambda args: _get_security_status_handler(args),

    # Admin & Management Tools
    "health_check": lambda args: _health_check_handler(args),
    "get_server_metrics": lambda args: _get_server_metrics_handler(args),
    "get_connections": lambda args: _get_connections_handler(args),
    "test_query": lambda args: _test_query_handler(args),
    "get_server_info": lambda args: _get_server_info_handler(args),
    "reload_config": lambda args: _reload_config_handler(args),
    "get_query_history": lambda args: _get_query_history_handler(args),
    "clear_all_caches": lambda args: _clear_all_caches_handler(args),
    "diagnose_connection": lambda args: _diagnose_connection_handler(args),
}


# Additional handler implementations (wrapped for consistency)
async def _explain_query_handler(arguments: dict) -> list[TextContent]:
    """Get query execution plan."""
    try:
        sql = arguments["sql"]
        analyze = arguments.get("analyze", False)
        explain_sql = f"EXPLAIN {'ANALYZE' if analyze else ''} {sql}"
        result = operations.execute_query(explain_sql)

        output = {
            "success": True,
            "plan": [row[0] if row else "" for row in result.rows],
        }

        return [TextContent(type="text", text=str(output))]

    except Exception as e:
        logger.error(f"Explain failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _execute_batch_handler(arguments: dict) -> list[TextContent]:
    """Execute multiple queries in batch."""
    results = []
    conn_mgr = get_connection_manager()

    try:
        queries = arguments["queries"]
        with conn_mgr.transaction():
            for i, sql in enumerate(queries):
                try:
                    result = operations.execute_query(sql)
                    results.append({
                        "index": i,
                        "success": True,
                        "row_count": result.row_count,
                    })
                except Exception as e:
                    results.append({
                        "index": i,
                        "success": False,
                        "error": str(e),
                    })

        return [TextContent(type="text", text=str(results))]

    except Exception as e:
        logger.error(f"Batch execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _describe_table_handler(arguments: dict) -> list[TextContent]:
    """Get detailed table structure."""
    try:
        table_name = arguments["table_name"]
        table_info = operations.get_table_info(table_name)

        output = {
            "success": True,
            "table": table_info,
        }

        return [TextContent(type="text", text=str(output))]

    except Exception as e:
        logger.error(f"Describe table failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_table_stats_handler(arguments: dict) -> list[TextContent]:
    """Get table statistics."""
    try:
        table_name = arguments["table_name"]
        count_result = operations.execute_query(f"SELECT COUNT(*) FROM {table_name}")
        row_count = count_result.rows[0][0] if count_result.rows else 0

        output = {
            "success": True,
            "table_name": table_name,
            "row_count": row_count,
        }

        return [TextContent(type="text", text=str(output))]

    except Exception as e:
        logger.error(f"Get table stats failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _list_indexes_handler(arguments: dict) -> list[TextContent]:
    """List indexes for a table or all indexes."""
    try:
        table_name = arguments.get("table_name", None)
        schema = arguments.get("schema", None)
        result = await schema_tools.list_indexes(table_name, schema)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"List indexes failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_foreign_keys_handler(arguments: dict) -> list[TextContent]:
    """Get foreign key relationships."""
    try:
        table_name = arguments.get("table_name", None)
        schema = arguments.get("schema", None)
        result = await schema_tools.get_foreign_keys(table_name, schema)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get foreign keys failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _search_tables_handler(arguments: dict) -> list[TextContent]:
    """Search tables by name pattern."""
    try:
        pattern = arguments["pattern"]
        schema = arguments.get("schema", None)
        result = await schema_tools.search_tables(pattern, schema)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Search tables failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _list_views_handler(arguments: dict) -> list[TextContent]:
    """List all views in the database."""
    try:
        schema = arguments.get("schema", None)
        result = await schema_tools.list_views(schema)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"List views failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _list_columns_handler(arguments: dict) -> list[TextContent]:
    """Get detailed column information for a table."""
    try:
        table_name = arguments["table_name"]
        schema = arguments.get("schema", None)
        result = await schema_tools.list_columns(table_name, schema)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"List columns failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


# DML Handlers
async def _insert_rows_handler(arguments: dict) -> list[TextContent]:
    """Insert single or multiple rows into a table."""
    try:
        table_name = arguments["table_name"]
        rows = arguments["rows"]
        result = await dml_tools.insert_rows(table_name, rows)
        output = {
            "success": result.success,
            "rows_affected": result.rows_affected,
            "message": result.message,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Insert rows failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _update_rows_handler(arguments: dict) -> list[TextContent]:
    """Update rows matching the WHERE condition."""
    try:
        table_name = arguments["table_name"]
        updates = arguments["updates"]
        where = arguments.get("where", None)
        where_params = arguments.get("where_params", None)
        result = await dml_tools.update_rows(table_name, updates, where, where_params)
        output = {
            "success": result.success,
            "rows_affected": result.rows_affected,
            "message": result.message,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Update rows failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _delete_rows_handler(arguments: dict) -> list[TextContent]:
    """Delete rows matching the WHERE condition."""
    try:
        table_name = arguments["table_name"]
        where = arguments.get("where", None)
        where_params = arguments.get("where_params", None)
        result = await dml_tools.delete_rows(table_name, where, where_params)
        output = {
            "success": result.success,
            "rows_affected": result.rows_affected,
            "message": result.message,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Delete rows failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _upsert_rows_handler(arguments: dict) -> list[TextContent]:
    """Insert or update rows (UPSERT operation)."""
    try:
        table_name = arguments["table_name"]
        rows = arguments["rows"]
        constraint = arguments.get("constraint", None)
        result = await dml_tools.upsert_rows(table_name, rows, constraint)
        output = {
            "success": result.success,
            "rows_affected": result.rows_affected,
            "message": result.message,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Upsert rows failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _truncate_table_handler(arguments: dict) -> list[TextContent]:
    """Truncate a table (fast delete all rows)."""
    try:
        table_name = arguments["table_name"]
        result = await dml_tools.truncate_table(table_name)
        output = {
            "success": result.success,
            "rows_affected": result.rows_affected,
            "message": result.message,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Truncate table failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _bulk_import_handler(arguments: dict) -> list[TextContent]:
    """Bulk import data into a table in batches."""
    try:
        table_name = arguments["table_name"]
        data = arguments["data"]
        batch_size = arguments.get("batch_size", 1000)
        result = await dml_tools.bulk_import(table_name, data, batch_size)
        output = {
            "success": result.success,
            "rows_affected": result.rows_affected,
            "message": result.message,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Bulk import failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


# DDL Handlers
async def _create_database_handler(arguments: dict) -> list[TextContent]:
    """Create a new database."""
    try:
        database_name = arguments["database_name"]
        if_not_exists = arguments.get("if_not_exists", True)
        result = await ddl_tools.create_database(database_name, if_not_exists)
        output = {
            "success": result.success,
            "message": result.message,
            "database_name": result.object_name,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Create database failed: {e}")
        return [TextContent(type="text", text=str({"success": False, "error": str(e)}))]


async def _drop_database_handler(arguments: dict) -> list[TextContent]:
    """Drop a database."""
    try:
        database_name = arguments["database_name"]
        if_exists = arguments.get("if_exists", True)
        cascade = arguments.get("cascade", False)
        result = await ddl_tools.drop_database(database_name, if_exists, cascade)
        output = {
            "success": result.success,
            "message": result.message,
            "database_name": result.object_name,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Drop database failed: {e}")
        return [TextContent(type="text", text=str({"success": False, "error": str(e)}))]


async def _create_schema_handler(arguments: dict) -> list[TextContent]:
    """Create a new schema."""
    try:
        schema_name = arguments["schema_name"]
        if_not_exists = arguments.get("if_not_exists", True)
        result = await ddl_tools.create_schema(schema_name, if_not_exists)
        output = {
            "success": result.success,
            "message": result.message,
            "schema_name": result.object_name,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Create schema failed: {e}")
        return [TextContent(type="text", text=str({"success": False, "error": str(e)}))]


async def _drop_schema_handler(arguments: dict) -> list[TextContent]:
    """Drop a schema."""
    try:
        schema_name = arguments["schema_name"]
        if_exists = arguments.get("if_exists", True)
        cascade = arguments.get("cascade", False)
        result = await ddl_tools.drop_schema(schema_name, if_exists, cascade)
        output = {
            "success": result.success,
            "message": result.message,
            "schema_name": result.object_name,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Drop schema failed: {e}")
        return [TextContent(type="text", text=str({"success": False, "error": str(e)}))]


async def _create_table_handler(arguments: dict) -> list[TextContent]:
    """Create a new table."""
    try:
        table_name = arguments["table_name"]
        columns = arguments["columns"]
        primary_key = arguments.get("primary_key", None)
        constraints = arguments.get("constraints", None)
        if_not_exists = arguments.get("if_not_exists", True)
        result = await ddl_tools.create_table(table_name, columns, primary_key, constraints, if_not_exists)
        output = {
            "success": result.success,
            "message": result.message,
            "object_name": result.object_name,
            "object_type": result.object_type,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Create table failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _drop_table_handler(arguments: dict) -> list[TextContent]:
    """Drop a table."""
    try:
        table_name = arguments["table_name"]
        cascade = arguments.get("cascade", False)
        if_exists = arguments.get("if_exists", True)
        result = await ddl_tools.drop_table(table_name, cascade, if_exists)
        output = {
            "success": result.success,
            "message": result.message,
            "object_name": result.object_name,
            "object_type": result.object_type,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Drop table failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _alter_table_handler(arguments: dict) -> list[TextContent]:
    """Alter table structure."""
    try:
        table_name = arguments["table_name"]
        action = arguments["action"]
        alterations = arguments.get("alterations", None)
        result = await ddl_tools.alter_table(table_name, action, alterations)
        output = {
            "success": result.success,
            "message": result.message,
            "object_name": result.object_name,
            "object_type": result.object_type,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Alter table failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _create_index_handler(arguments: dict) -> list[TextContent]:
    """Create an index on a table."""
    try:
        index_name = arguments["index_name"]
        table_name = arguments["table_name"]
        columns = arguments["columns"]
        unique = arguments.get("unique", False)
        if_not_exists = arguments.get("if_not_exists", True)
        result = await ddl_tools.create_index(index_name, table_name, columns, unique, if_not_exists)
        output = {
            "success": result.success,
            "message": result.message,
            "object_name": result.object_name,
            "object_type": result.object_type,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Create index failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _drop_index_handler(arguments: dict) -> list[TextContent]:
    """Drop an index."""
    try:
        index_name = arguments["index_name"]
        table_name = arguments.get("table_name", None)
        if_exists = arguments.get("if_exists", True)
        result = await ddl_tools.drop_index(index_name, table_name, if_exists)
        output = {
            "success": result.success,
            "message": result.message,
            "object_name": result.object_name,
            "object_type": result.object_type,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Drop index failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _create_view_handler(arguments: dict) -> list[TextContent]:
    """Create a view."""
    try:
        view_name = arguments["view_name"]
        select_statement = arguments["select_statement"]
        columns = arguments.get("columns", None)
        if_not_exists = arguments.get("if_not_exists", True)
        result = await ddl_tools.create_view(view_name, select_statement, columns, if_not_exists)
        output = {
            "success": result.success,
            "message": result.message,
            "object_name": result.object_name,
            "object_type": result.object_type,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Create view failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _drop_view_handler(arguments: dict) -> list[TextContent]:
    """Drop a view."""
    try:
        view_name = arguments["view_name"]
        cascade = arguments.get("cascade", False)
        if_exists = arguments.get("if_exists", True)
        result = await ddl_tools.drop_view(view_name, cascade, if_exists)
        output = {
            "success": result.success,
            "message": result.message,
            "object_name": result.object_name,
            "object_type": result.object_type,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Drop view failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _backup_table_handler(arguments: dict) -> list[TextContent]:
    """Create a backup of a table."""
    try:
        table_name = arguments["table_name"]
        backup_name = arguments.get("backup_name", None)
        result = await ddl_tools.backup_table(table_name, backup_name)
        output = {
            "success": result.success,
            "message": result.message,
            "object_name": result.object_name,
            "object_type": result.object_type,
            "error": result.error,
        }
        return [TextContent(type="text", text=str(output))]
    except Exception as e:
        logger.error(f"Backup table failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


# Chat2SQL Handlers
async def _natural_language_query_handler(arguments: dict) -> list[TextContent]:
    """Convert natural language question to SQL and optionally execute it."""
    try:
        question = arguments["question"]
        execute = arguments.get("execute", False)
        limit = arguments.get("limit", None)
        result = await chat2sql_tools.natural_language_query(question, execute, limit)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Natural language query failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _explain_sql_handler(arguments: dict) -> list[TextContent]:
    """Explain a SQL query in natural language."""
    try:
        sql = arguments["sql"]
        result = await chat2sql_tools.explain_sql(sql)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"SQL explanation failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _suggest_query_handler(arguments: dict) -> list[TextContent]:
    """Suggest a SQL query for a natural language question."""
    try:
        question = arguments["question"]
        result = await chat2sql_tools.suggest_query(question)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Query suggestion failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _validate_sql_handler(arguments: dict) -> list[TextContent]:
    """Validate a SQL query."""
    try:
        sql = arguments["sql"]
        result = await chat2sql_tools.validate_sql(sql)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"SQL validation failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _optimize_query_handler(arguments: dict) -> list[TextContent]:
    """Get optimization suggestions for a SQL query."""
    try:
        sql = arguments["sql"]
        result = await chat2sql_tools.optimize_query(sql)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Query optimization failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _fix_sql_handler(arguments: dict) -> list[TextContent]:
    """Fix a SQL query based on error message."""
    try:
        sql = arguments["sql"]
        error_message = arguments["error_message"]
        result = await chat2sql_tools.fix_sql(sql, error_message)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"SQL fix failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_schema_context_handler(arguments: dict) -> list[TextContent]:
    """Get relevant schema context for a query."""
    try:
        query = arguments["query"]
        max_tables = arguments.get("max_tables", 5)
        result = await chat2sql_tools.get_schema_context(query, max_tables)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get schema context failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _clear_schema_cache_handler(arguments: dict) -> list[TextContent]:
    """Clear the schema cache."""
    try:
        result = await chat2sql_tools.clear_schema_cache()
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Clear schema cache failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_schema_info_tool_handler(arguments: dict) -> list[TextContent]:
    """Get schema cache information."""
    try:
        result = await chat2sql_tools.get_schema_info()
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get schema info failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


# =============================================================================
# Chat2SQL Lightweight Handlers (no internal LLM required)
# =============================================================================

async def _get_schema_for_llm_handler(arguments: dict) -> list[TextContent]:
    """Get schema context formatted for LLM prompt (lightweight mode)."""
    try:
        question = arguments["question"]
        max_tables = arguments.get("max_tables", 5)
        result = await chat2sql_light_tools.get_schema_for_llm(question, max_tables)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get schema for LLM failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _validate_sql_only_handler(arguments: dict) -> list[TextContent]:
    """Validate SQL query without LLM explanation (lightweight mode)."""
    try:
        sql = arguments["sql"]
        result = await chat2sql_light_tools.validate_sql_only(sql)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Validate SQL only failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _execute_validated_sql_handler(arguments: dict) -> list[TextContent]:
    """Execute SQL query with validation (lightweight mode)."""
    try:
        sql = arguments["sql"]
        limit = arguments.get("limit", None)
        result = await chat2sql_light_tools.execute_validated_sql(sql, limit)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Execute validated SQL failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_table_schema_for_llm_handler(arguments: dict) -> list[TextContent]:
    """Get detailed table schema for LLM (lightweight mode)."""
    try:
        table_name = arguments["table_name"]
        result = await chat2sql_light_tools.get_table_schema_for_llm(table_name)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get table schema for LLM failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _suggest_sql_from_schema_handler(arguments: dict) -> list[TextContent]:
    """Suggest improvements for user-provided SQL (lightweight mode)."""
    try:
        question = arguments["question"]
        sql = arguments["sql"]
        result = await chat2sql_light_tools.suggest_sql_from_schema(question, sql)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Suggest SQL from schema failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_lightweight_mode_info_handler(arguments: dict) -> list[TextContent]:
    """Get information about lightweight mode."""
    try:
        result = chat2sql_light_tools.get_lightweight_mode_info()
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get lightweight mode info failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


# =============================================================================
# Security & Audit Handlers
# =============================================================================
async def _get_audit_log_handler(arguments: dict) -> list[TextContent]:
    """Get recent audit log entries."""
    try:
        limit = arguments.get("limit", 100)
        operation_type = arguments.get("operation_type", None)
        result = await audit_tools.get_audit_log(limit, operation_type)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get audit log failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_audit_statistics_handler(arguments: dict) -> list[TextContent]:
    """Get audit statistics for recent period."""
    try:
        hours = arguments.get("hours", 24)
        result = await audit_tools.get_audit_statistics(hours)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get audit statistics failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_rate_limit_stats_handler(arguments: dict) -> list[TextContent]:
    """Get rate limiter statistics."""
    try:
        result = await audit_tools.get_rate_limit_stats()
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get rate limit stats failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _list_roles_handler(arguments: dict) -> list[TextContent]:
    """List all available roles."""
    try:
        result = await audit_tools.list_roles()
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"List roles failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_role_details_handler(arguments: dict) -> list[TextContent]:
    """Get details of a specific role."""
    try:
        role_name = arguments["role_name"]
        result = await audit_tools.get_role_details(role_name)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get role details failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _check_permission_handler(arguments: dict) -> list[TextContent]:
    """Check if a role has permission for an operation."""
    try:
        role_name = arguments["role_name"]
        operation = arguments["operation"]
        table_name = arguments.get("table_name", None)
        result = await audit_tools.check_permission(role_name, operation, table_name)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Check permission failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_security_status_handler(arguments: dict) -> list[TextContent]:
    """Get overall security status."""
    try:
        result = await audit_tools.get_security_status()
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get security status failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


# Admin & Management Handlers
async def _health_check_handler(arguments: dict) -> list[TextContent]:
    """Perform health check on the MCP server."""
    try:
        detailed = arguments.get("detailed", False)
        result = await admin_tools.health_check(detailed)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_server_metrics_handler(arguments: dict) -> list[TextContent]:
    """Get comprehensive server metrics."""
    try:
        result = await admin_tools.get_server_metrics()
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get server metrics failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_connections_handler(arguments: dict) -> list[TextContent]:
    """Get database connection information."""
    try:
        result = await admin_tools.get_connections()
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get connections failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _test_query_handler(arguments: dict) -> list[TextContent]:
    """Test database connectivity with a test query."""
    try:
        sql = arguments.get("sql", None)
        result = await admin_tools.test_query(sql)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Test query failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_server_info_handler(arguments: dict) -> list[TextContent]:
    """Get server information and configuration."""
    try:
        result = await admin_tools.get_server_info()
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get server info failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _reload_config_handler(arguments: dict) -> list[TextContent]:
    """Reload configuration."""
    try:
        result = await admin_tools.reload_config()
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Reload config failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _get_query_history_handler(arguments: dict) -> list[TextContent]:
    """Get recent query history from audit log."""
    try:
        limit = arguments.get("limit", 50)
        operation_type = arguments.get("operation_type", None)
        result = await admin_tools.get_query_history(limit, operation_type)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Get query history failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _clear_all_caches_handler(arguments: dict) -> list[TextContent]:
    """Clear all server caches."""
    try:
        result = await admin_tools.clear_all_caches()
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Clear caches failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def _diagnose_connection_handler(arguments: dict) -> list[TextContent]:
    """Diagnose database connection issues."""
    try:
        detailed = arguments.get("detailed", False)
        result = await admin_tools.diagnose_connection(detailed=detailed)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Diagnose connection failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


# =============================================================================
# SINGLE UNIFIED CALL_TOOL HANDLER
# =============================================================================

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Unified handler for all tool calls.

    This is the ONLY handler registered with @server.call_tool().
    It dispatches to the appropriate tool handler based on the tool name.
    """
    if name not in TOOL_HANDLERS:
        logger.error(f"Unknown tool: {name}")
        return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

    try:
        handler = TOOL_HANDLERS[name]
        return await handler(arguments)
    except Exception as e:
        logger.error(f"Tool {name} execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# =============================================================================
# MCP Resources
# =============================================================================

@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available MCP resources."""
    return [
        Resource(uri=AnyUrl("schema://database/tables"), name="database/tables", description="List all tables in the database"),
        Resource(uri=AnyUrl("schema://database/info"), name="database/info", description="Get database information"),
        Resource(uri=AnyUrl("schema://database/relationships"), name="database/relationships", description="Get table relationships"),
        Resource(uri=AnyUrl("schema://database/indexes"), name="database/indexes", description="List all indexes"),
        Resource(uri=AnyUrl("schema://database/views"), name="database/views", description="List all views"),
        Resource(uri=AnyUrl("meta://database/info"), name="meta/database/info", description="Get database metadata"),
        Resource(uri=AnyUrl("meta://database/stats"), name="meta/database/stats", description="Get database statistics"),
    ]


@server.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read an MCP resource."""
    try:
        uri_str = str(uri)

        if uri_str == "schema://database/tables":
            return await schema_resources.get_tables_resource(settings.xugu.database, False)
        elif uri_str == "schema://database/info":
            return await schema_resources.get_database_info_resource()
        elif uri_str == "schema://database/relationships":
            return await schema_resources.get_relationships_resource()
        elif uri_str == "schema://database/indexes":
            return await schema_resources.get_indexes_resource()
        elif uri_str == "schema://database/views":
            return await schema_resources.get_views_resource()
        elif uri_str == "meta://database/info":
            return await schema_resources.get_database_info_resource()
        elif uri_str == "meta://database/stats":
            return await schema_resources.get_database_stats_resource()
        elif uri_str.startswith("schema://database/table/"):
            table_name = uri_str.replace("schema://database/table/", "")
            return await schema_resources.get_table_resource(table_name)
        else:
            return f"Unknown resource: {uri_str}"

    except Exception as e:
        logger.error(f"Read resource failed: {e}")
        return f"Error: {e}"


# =============================================================================
# Tool Listing
# =============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="execute_query",
            description="Execute a SELECT query and return results",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL SELECT statement"},
                    "params": {"type": "array", "description": "Query parameters"},
                    "limit": {"type": "integer", "description": "Maximum rows to return"},
                },
                "required": ["sql"],
            },
        ),
        Tool(
            name="list_tables",
            description="List all tables in the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema": {"type": "string", "description": "Schema filter"},
                    "include_system": {"type": "boolean", "description": "Include system tables"},
                },
            },
        ),
        Tool(
            name="get_database_info",
            description="Get database version and information",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="health_check",
            description="Perform health check on the MCP server",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {"type": "boolean", "description": "Include detailed component status"},
                },
            },
        ),
        Tool(
            name="diagnose_connection",
            description="Diagnose database connection issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {"type": "boolean", "description": "Include detailed component status"},
                },
            },
        ),
        # Chat2SQL Lightweight Tools (no LLM_API_KEY required)
        Tool(
            name="get_schema_for_llm",
            description="Get database schema context for LLM to generate SQL (lightweight mode)",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Natural language question"},
                    "max_tables": {"type": "integer", "description": "Maximum tables to include", "default": 5},
                },
                "required": ["question"],
            },
        ),
        Tool(
            name="validate_sql_only",
            description="Validate SQL query without LLM explanation (lightweight mode)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL query to validate"},
                },
                "required": ["sql"],
            },
        ),
        Tool(
            name="execute_validated_sql",
            description="Execute validated SQL query (lightweight mode)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL query to execute"},
                    "limit": {"type": "integer", "description": "Maximum rows to return"},
                },
                "required": ["sql"],
            },
        ),
        Tool(
            name="get_table_schema_for_llm",
            description="Get detailed table schema for LLM (lightweight mode)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "Table name"},
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="suggest_sql_from_schema",
            description="Validate and suggest improvements for user-provided SQL (lightweight mode)",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Original natural language question"},
                    "sql": {"type": "string", "description": "User-provided SQL query"},
                },
                "required": ["question", "sql"],
            },
        ),
        Tool(
            name="get_lightweight_mode_info",
            description="Get information about lightweight Chat2SQL mode",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    """Main entry point for the MCP server."""
    logger.info(f"Starting {settings.mcp_server.name} v{settings.mcp_server.version}")
    logger.info(f"XuguDB connection: {settings.xugu.host}:{settings.xugu.port}/{settings.xugu.database}")

    # Test database connection
    try:
        conn_mgr = get_connection_manager()
        if conn_mgr.ping():
            logger.info("Successfully connected to XuguDB")
        else:
            logger.warning("Database connection test failed")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.warning("Server will start but database operations may fail")

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def cli_main():
    """CLI entry point."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    finally:
        close_connection()
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    cli_main()
