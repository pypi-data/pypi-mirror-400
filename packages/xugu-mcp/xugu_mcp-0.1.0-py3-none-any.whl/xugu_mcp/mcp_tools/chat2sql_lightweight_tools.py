"""
Lightweight Chat2SQL MCP tools - No internal LLM required.

These tools provide schema context and SQL validation only.
The client-side LLM (e.g., Claude in Claude Desktop) generates the SQL.

Mode: lightweight (no LLM_API_KEY required)
"""
from typing import Any

from ..chat2sql import Chat2SQLEngine
from ..chat2sql.sql_validator import SQLValidator
from ..db import operations
from ..utils.logging import get_logger
from ..config.settings import get_settings

logger = get_logger(__name__)

# Global Chat2SQL engine instance (used for schema and validation only)
_engine: Chat2SQLEngine | None = None
_validator: SQLValidator | None = None


def get_engine() -> Chat2SQLEngine:
    """Get or create the Chat2SQL engine instance (for schema only)."""
    global _engine
    if _engine is None:
        # Create engine without LLM provider
        from ..llm.base import BaseLLMProvider

        class NoOpLLMProvider(BaseLLMProvider):
            """No-op LLM provider for lightweight mode."""

            def __init__(self):
                self.provider_name = "noop"

            async def generate(self, messages, **kwargs):
                # This should never be called in lightweight mode
                from ..llm import LLMResponse
                return LLMResponse(
                    content="",
                    error="Lightweight mode does not support internal LLM calls. Use client-side LLM instead.",
                    model="noop",
                    usage={},
                )

            async def generate_stream(self, messages, **kwargs):
                # This should never be called in lightweight mode
                yield ""
                raise NotImplementedError("Lightweight mode does not support streaming")

            def validate_config(self) -> bool:
                # NoOp provider is always valid
                return True

        _engine = Chat2SQLEngine(llm_provider=NoOpLLMProvider())
    return _engine


def get_validator() -> SQLValidator:
    """Get or create the SQL validator instance."""
    global _validator
    if _validator is None:
        settings = get_settings()
        _validator = SQLValidator()
    return _validator


async def get_schema_for_llm(
    question: str,
    max_tables: int = 5,
) -> dict[str, Any]:
    """Get schema context formatted for LLM prompt (lightweight mode).

    This tool returns database schema information that the client-side LLM
    can use to generate SQL queries. No internal LLM call is made.

    Args:
        question: Natural language question (used to find relevant tables)
        max_tables: Maximum number of tables to include

    Returns:
        Dictionary with formatted schema context for LLM
    """
    try:
        engine = get_engine()
        settings = get_settings()

        # Get schema context
        context = await engine.schema_manager.get_schema_context(question, max_tables)

        # Format for LLM consumption
        formatted = {
            "database": settings.xugu.database,
            "relevant_tables": [],
            "all_tables": [],
            "relationships": [],
        }

        # Add relevant tables with columns
        if "relevant_tables" in context:
            for table in context["relevant_tables"]:
                # table is from TableSchema.to_dict() which has:
                # - table_name, columns, primary_keys, foreign_keys, indexes, row_count, sample_data
                # columns are list of dicts with keys: name, type, nullable, default, comment

                formatted["relevant_tables"].append({
                    "name": table.get("table_name", ""),
                    "columns": [
                        {
                            "name": col.get("name", ""),
                            "type": col.get("type", ""),
                            "nullable": col.get("nullable", True),
                            "primary_key": col.get("name") in table.get("primary_keys", []),
                            "default": col.get("default", ""),
                        }
                        for col in table.get("columns", [])
                    ],
                    "row_count": table.get("row_count", 0),
                })

        # Add all tables list
        if "all_tables" in context:
            formatted["all_tables"] = context["all_tables"]

        # Add relationships
        if "relationships" in context:
            formatted["relationships"] = context["relationships"]

        return {
            "success": True,
            "mode": "lightweight",
            "question": question,
            "schema": formatted,
            "instructions": {
                "use_this_schema_to": "Generate a SQL query for the user's question",
                "database_type": "XuguDB (similar to Oracle/PostgreSQL)",
                "sql_dialect": "Standard SQL with XuguDB extensions",
                "tips": [
                    "Use table names and columns from the schema above",
                    "Join tables using relationships if needed",
                    "Add LIMIT clause to limit result rows",
                    "Use proper data types from column definitions",
                ]
            }
        }

    except Exception as e:
        logger.error(f"Get schema for LLM failed: {e}")
        return {
            "success": False,
            "mode": "lightweight",
            "question": question,
            "error": str(e),
        }


async def validate_sql_only(
    sql: str,
) -> dict[str, Any]:
    """Validate SQL query without LLM explanation (lightweight mode).

    This tool performs security and syntax validation on the provided SQL.
    No internal LLM call is made.

    Args:
        sql: SQL query to validate

    Returns:
        Dictionary with validation results
    """
    try:
        settings = get_settings()
        validator = get_validator()

        # Perform validation
        result = validator.validate(
            sql,
            allow_ddl=settings.chat2sql.allow_ddl,
        )

        return {
            "success": True,
            "mode": "lightweight",
            "sql": sql,
            "is_valid": result.is_valid,
            "has_warnings": result.has_warnings(),
            "issues": [
                {
                    "severity": issue.severity.value,
                    "code": issue.code,
                    "message": issue.message,
                    "line": issue.line,
                    "column": issue.column,
                    "suggestion": issue.suggestion,
                }
                for issue in result.issues
            ],
            "normalized_sql": result.normalized_sql,
            "blocked_operations": [
                op for op in ["DROP DATABASE", "ALTER SYSTEM"]
                if op in sql.upper()
            ] if not result.is_valid else [],
        }

    except Exception as e:
        logger.error(f"SQL validation failed: {e}")
        return {
            "success": False,
            "mode": "lightweight",
            "sql": sql,
            "error": str(e),
        }


async def execute_validated_sql(
    sql: str,
    limit: int | None = None,
) -> dict[str, Any]:
    """Execute SQL query with validation (lightweight mode).

    This tool validates and executes the SQL query.
    No internal LLM call is made.

    Args:
        sql: SQL query to execute
        limit: Optional limit for result rows

    Returns:
        Dictionary with execution results
    """
    try:
        settings = get_settings()

        # First validate
        validator = get_validator()
        validation_result = validator.validate(
            sql,
            allow_ddl=settings.chat2sql.allow_ddl,
        )

        if not validation_result.is_valid:
            return {
                "success": False,
                "mode": "lightweight",
                "sql": sql,
                "error": "SQL validation failed",
                "validation_issues": [
                    {
                        "severity": issue.severity.value,
                        "code": issue.code,
                        "message": issue.message,
                    }
                    for issue in validation_result.issues
                ],
            }

        # Add limit if specified and query is SELECT
        final_sql = sql
        if limit and sql.strip().upper().startswith("SELECT"):
            # Check if LIMIT already exists
            if "LIMIT" not in sql.upper():
                final_sql = f"{sql.rstrip(';')} LIMIT {int(limit)}"

        # Execute query (only for SELECT)
        if final_sql.strip().upper().startswith("SELECT"):
            query_result = operations.execute_query(final_sql)

            return {
                "success": True,
                "mode": "lightweight",
                "sql": final_sql,
                "execution_result": {
                    "rows": query_result.rows,
                    "columns": query_result.columns,
                    "row_count": query_result.row_count,
                    "execution_time": query_result.execution_time,
                },
            }
        else:
            return {
                "success": False,
                "mode": "lightweight",
                "sql": sql,
                "error": "Only SELECT queries can be executed in lightweight mode. For DML/DDL, use the dedicated DML/DDl tools.",
            }

    except Exception as e:
        logger.error(f"Execute validated SQL failed: {e}")
        return {
            "success": False,
            "mode": "lightweight",
            "sql": sql,
            "error": str(e),
        }


async def get_table_schema_for_llm(
    table_name: str,
) -> dict[str, Any]:
    """Get detailed table schema for LLM (lightweight mode).

    Args:
        table_name: Name of the table

    Returns:
        Dictionary with table schema formatted for LLM
    """
    try:
        engine = get_engine()

        # Get table schema
        table_schema = await engine.schema_manager.get_table_schema(table_name)

        # Get row count
        try:
            count_result = operations.execute_query(f"SELECT COUNT(*) FROM {table_name}")
            row_count = count_result.rows[0][0] if count_result.rows else 0
        except Exception:
            row_count = None

        # table_schema.columns is a list of dicts
        return {
            "success": True,
            "mode": "lightweight",
            "table": {
                "name": table_schema.table_name,
                "columns": [
                    {
                        "name": col.get("name"),
                        "type": col.get("type"),
                        "nullable": col.get("nullable", True),
                        "primary_key": col.get("name") in table_schema.primary_keys,
                        "default": col.get("default"),
                    }
                    for col in table_schema.columns
                ],
                "primary_key": table_schema.primary_keys,
                "row_count": row_count,
            },
            "sample_query": f"SELECT * FROM {table_name} LIMIT 10;",
        }

    except Exception as e:
        logger.error(f"Get table schema for LLM failed: {e}")
        return {
            "success": False,
            "mode": "lightweight",
            "table_name": table_name,
            "error": str(e),
        }


async def suggest_sql_from_schema(
    question: str,
    sql: str,
) -> dict[str, Any]:
    """Suggest improvements for user-provided SQL (lightweight mode).

    This tool validates the SQL and provides suggestions without LLM.

    Args:
        question: Original natural language question
        sql: User-provided SQL query

    Returns:
        Dictionary with validation results and suggestions
    """
    try:
        # Validate the SQL
        validate_result = await validate_sql_only(sql)

        if not validate_result.get("success"):
            return validate_result

        # Get schema context for reference
        schema_result = await get_schema_for_llm(question, max_tables=5)

        return {
            "success": True,
            "mode": "lightweight",
            "question": question,
            "sql": sql,
            "validation": validate_result,
            "schema_available": schema_result.get("success", False),
            "next_steps": [
                "Review the validation issues above",
                "Use the schema information to refine your query",
                "Call execute_validated_sql to run the query",
            ],
        }

    except Exception as e:
        logger.error(f"Suggest SQL from schema failed: {e}")
        return {
            "success": False,
            "mode": "lightweight",
            "question": question,
            "sql": sql,
            "error": str(e),
        }


def get_lightweight_mode_info() -> dict[str, Any]:
    """Get information about lightweight mode.

    Returns:
        Dictionary with lightweight mode information
    """
    settings = get_settings()

    return {
        "mode": "lightweight",
        "description": "Lightweight Chat2SQL mode - No internal LLM required",
        "how_it_works": {
            "step1": "Client asks a question in natural language",
            "step2": "MCP provides schema context via get_schema_for_llm()",
            "step3": "Client LLM generates SQL using the schema",
            "step4": "MCP validates SQL via validate_sql_only()",
            "step5": "MCP executes SQL via execute_validated_sql()",
        },
        "tools_available": [
            "get_schema_for_llm - Get database schema for SQL generation",
            "validate_sql_only - Validate SQL security and syntax",
            "execute_validated_sql - Execute validated SELECT queries",
            "get_table_schema_for_llm - Get detailed table schema",
            "suggest_sql_from_schema - Validate and improve user SQL",
        ],
        "advantages": [
            "No LLM_API_KEY required",
            "Uses existing client LLM (Claude, GPT, etc.)",
            "Lower latency (no extra API call)",
            "Better context awareness (LLM sees conversation history)",
        ],
        "configuration": {
            "CHAT2SQL_MODE": "lightweight",
            "LLM_API_KEY": "Not required",
        },
        "example_workflow": {
            "1_user_asks": '"Show me all students in Computer Science"',
            "2_mcp_call": "get_schema_for_llm(question='...')",
            "3_llm_generates": "SELECT * FROM STUDENTS WHERE CLASS_NAME = 'Computer Science'",
            "4_mcp_validates": "validate_sql_only(sql='...')",
            "5_mpc_executes": "execute_validated_sql(sql='...')",
        },
    }
