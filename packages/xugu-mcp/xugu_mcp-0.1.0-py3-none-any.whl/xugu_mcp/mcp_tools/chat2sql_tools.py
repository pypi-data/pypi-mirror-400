"""
Chat2SQL MCP tools for natural language to SQL conversion.
"""
from typing import Any

from ..chat2sql import Chat2SQLEngine
from ..db import operations
from ..utils.logging import get_logger
from ..config.settings import get_settings

logger = get_logger(__name__)

# Global Chat2SQL engine instance
_engine: Chat2SQLEngine | None = None


def check_llm_configured() -> dict[str, Any] | None:
    """Check if LLM is configured.

    Returns None if configured, error dict if not.
    """
    if not get_settings().llm.is_configured():
        return {
            "success": False,
            "error": "LLM is not configured. Please set LLM_API_KEY for cloud providers (claude, openai, zai, zhipu) or use local/ollama provider.",
            "hint": "Local providers (local, ollama) do not require API key.",
        }
    return None


def get_engine() -> Chat2SQLEngine:
    """Get or create the Chat2SQL engine instance.

    Returns:
        Chat2SQLEngine instance
    """
    global _engine
    if _engine is None:
        _engine = Chat2SQLEngine()
    return _engine


async def natural_language_query(
    question: str,
    execute: bool = False,
    limit: int | None = None,
) -> dict[str, Any]:
    """Convert natural language question to SQL and optionally execute it.

    Args:
        question: Natural language question
        execute: Whether to execute the generated SQL
        limit: Optional limit for result rows

    Returns:
        Dictionary with SQL query and optional execution results
    """
    try:
        # Check if LLM is configured
        if error := check_llm_configured():
            return error

        engine = get_engine()

        # Convert to SQL
        result = await engine.natural_language_to_sql(question)

        if not result.is_valid:
            return {
                "success": False,
                "question": question,
                "sql": result.sql,
                "error": result.error or "SQL validation failed",
                "validation_issues": [
                    {
                        "severity": issue.severity.value,
                        "code": issue.code,
                        "message": issue.message,
                    }
                    for issue in (result.validation_result.issues if result.validation_result else [])
                ],
            }

        response = {
            "success": True,
            "question": question,
            "sql": result.sql,
            "is_valid": result.is_valid,
        }

        # Optionally execute the query
        if execute and result.sql.upper().strip().startswith("SELECT"):
            try:
                if limit:
                    sql_with_limit = f"{result.sql} LIMIT {int(limit)}"
                else:
                    sql_with_limit = result.sql

                query_result = operations.execute_query(sql_with_limit)

                response["execution_result"] = {
                    "rows": query_result.rows,
                    "columns": query_result.columns,
                    "row_count": len(query_result.rows) if query_result.rows else 0,
                }

            except Exception as e:
                response["execution_error"] = str(e)

        return response

    except Exception as e:
        logger.error(f"Natural language query failed: {e}")
        return {
            "success": False,
            "question": question,
            "error": str(e),
        }


async def explain_sql(
    sql: str,
) -> dict[str, Any]:
    """Explain a SQL query in natural language.

    Args:
        sql: SQL query to explain

    Returns:
        Dictionary with explanation
    """
    try:
        # Check if LLM is configured
        if error := check_llm_configured():
            return error

        engine = get_engine()
        explanation = await engine.explain_sql(sql)

        return {
            "success": True,
            "sql": sql,
            "explanation": explanation,
        }

    except Exception as e:
        logger.error(f"SQL explanation failed: {e}")
        return {
            "success": False,
            "sql": sql,
            "error": str(e),
        }


async def suggest_query(
    question: str,
) -> dict[str, Any]:
    """Suggest a SQL query for a natural language question.

    Args:
        question: Natural language question

    Returns:
        Dictionary with suggested SQL
    """
    try:
        # Check if LLM is configured
        if error := check_llm_configured():
            return error

        engine = get_engine()
        sql = await engine.suggest_query(question)

        return {
            "success": True,
            "question": question,
            "suggested_sql": sql,
        }

    except Exception as e:
        logger.error(f"Query suggestion failed: {e}")
        return {
            "success": False,
            "question": question,
            "error": str(e),
        }


async def validate_sql(
    sql: str,
) -> dict[str, Any]:
    """Validate a SQL query.

    Args:
        sql: SQL query to validate

    Returns:
        Dictionary with validation results
    """
    try:
        engine = get_engine()
        validation_result = await engine.validate_sql(sql)

        return {
            "success": True,
            "sql": sql,
            "is_valid": validation_result.is_valid,
            "has_warnings": validation_result.has_warnings(),
            "issues": [
                {
                    "severity": issue.severity.value,
                    "code": issue.code,
                    "message": issue.message,
                    "line": issue.line,
                    "column": issue.column,
                    "suggestion": issue.suggestion,
                }
                for issue in validation_result.issues
            ],
            "normalized_sql": validation_result.normalized_sql,
        }

    except Exception as e:
        logger.error(f"SQL validation failed: {e}")
        return {
            "success": False,
            "sql": sql,
            "error": str(e),
        }


async def optimize_query(
    sql: str,
) -> dict[str, Any]:
    """Get optimization suggestions for a SQL query.

    Args:
        sql: SQL query to optimize

    Returns:
        Dictionary with optimization suggestions
    """
    try:
        # Check if LLM is configured
        if error := check_llm_configured():
            return error

        engine = get_engine()
        optimization_result = await engine.optimize_sql(sql)

        return {
            "success": True,
            "sql": sql,
            "suggestions": optimization_result.suggestions,
            "optimized_sql": optimization_result.optimized_sql,
            "explanation": optimization_result.explanation,
        }

    except Exception as e:
        logger.error(f"Query optimization failed: {e}")
        return {
            "success": False,
            "sql": sql,
            "error": str(e),
        }


async def fix_sql(
    sql: str,
    error_message: str,
) -> dict[str, Any]:
    """Fix a SQL query based on error message.

    Args:
        sql: SQL query with error
        error_message: Error message from database

    Returns:
        Dictionary with fixed SQL
    """
    try:
        # Check if LLM is configured
        if error := check_llm_configured():
            return error
        engine = get_engine()
        fixed_sql = await engine.fix_sql(sql, error_message)

        # Validate the fixed SQL
        validation_result = await engine.validate_sql(fixed_sql)

        return {
            "success": True,
            "original_sql": sql,
            "error_message": error_message,
            "fixed_sql": fixed_sql,
            "is_valid": validation_result.is_valid,
        }

    except Exception as e:
        logger.error(f"SQL fix failed: {e}")
        return {
            "success": False,
            "original_sql": sql,
            "error": str(e),
        }


async def get_schema_context(
    query: str,
    max_tables: int = 5,
) -> dict[str, Any]:
    """Get relevant schema context for a query.

    Args:
        query: Natural language query or SQL query
        max_tables: Maximum number of tables to include

    Returns:
        Dictionary with schema context
    """
    try:
        engine = get_engine()
        context = await engine.schema_manager.get_schema_context(query, max_tables)

        return {
            "success": True,
            "query": query,
            "context": context,
        }

    except Exception as e:
        logger.error(f"Get schema context failed: {e}")
        return {
            "success": False,
            "query": query,
            "error": str(e),
        }


async def clear_schema_cache() -> dict[str, Any]:
    """Clear the schema cache.

    Returns:
        Dictionary with operation result
    """
    try:
        engine = get_engine()
        engine.clear_schema_cache()

        return {
            "success": True,
            "message": "Schema cache cleared successfully",
        }

    except Exception as e:
        logger.error(f"Clear schema cache failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def get_schema_info() -> dict[str, Any]:
    """Get schema cache information.

    Returns:
        Dictionary with schema cache info
    """
    try:
        engine = get_engine()
        info = engine.get_schema_info()

        return {
            "success": True,
            "schema_info": info,
        }

    except Exception as e:
        logger.error(f"Get schema info failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }
