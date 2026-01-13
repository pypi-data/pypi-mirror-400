"""
Admin and Management MCP tools for XuguDB MCP Server.

Health checks, metrics collection, and system management.
"""
import time
import psutil
from typing import Any
from datetime import datetime

from ..db.connection import get_connection_manager
from ..db import operations
from ..config.settings import get_settings
from ..security import get_audit_logger, get_rate_limiter
from ..utils.logging import get_logger
from ..chat2sql import Chat2SQLEngine

# Global Chat2SQL engine instance
_chat2sql_engine: Chat2SQLEngine | None = None


def get_engine() -> Chat2SQLEngine:
    """Get or create the Chat2SQL engine instance.

    Returns:
        Chat2SQLEngine instance
    """
    global _chat2sql_engine
    if _chat2sql_engine is None:
        _chat2sql_engine = Chat2SQLEngine()
    return _chat2sql_engine

logger = get_logger(__name__)


async def health_check(
    detailed: bool = False,
) -> dict[str, Any]:
    """Perform health check on the MCP server.

    Args:
        detailed: Include detailed component status

    Returns:
        Health check results
    """
    try:
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {},
        }

        # Check database connection
        try:
            conn_mgr = get_connection_manager()
            db_connected = conn_mgr.ping()
            health["components"]["database"] = {
                "status": "healthy" if db_connected else "unhealthy",
                "connected": db_connected,
            }
            if detailed:
                health["components"]["database"]["details"] = {
                    "host": get_settings().xugu.host,
                    "port": get_settings().xugu.port,
                    "database": get_settings().xugu.database,
                    "pool_min_size": get_settings().xugu.pool_min_size,
                    "pool_max_size": get_settings().xugu.pool_max_size,
                }
        except Exception as e:
            health["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health["status"] = "degraded"

        # Check LLM provider
        try:
            llm_config = get_settings().llm
            has_api_key = bool(llm_config.api_key)
            health["components"]["llm"] = {
                "status": "healthy" if has_api_key else "warning",
                "provider": llm_config.provider,
                "model": llm_config.model,
                "configured": has_api_key,
            }
            if not has_api_key:
                health["status"] = "degraded"
        except Exception as e:
            health["components"]["llm"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health["status"] = "degraded"

        # Check Chat2SQL engine
        try:
            chat2sql_engine = get_engine()
            schema_info = chat2sql_engine.get_schema_info()
            health["components"]["chat2sql"] = {
                "status": "healthy",
                "schema_cached": schema_info.get("table_count", 0) > 0,
            }
        except Exception as e:
            health["components"]["chat2sql"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health["status"] = "degraded"

        # Check audit log
        try:
            get_audit_logger()
            health["components"]["audit_log"] = {
                "status": "healthy",
                "enabled": get_settings().security.enable_audit_log,
            }
        except Exception as e:
            health["components"]["audit_log"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health["status"] = "degraded"

        # Check rate limiter
        try:
            get_rate_limiter()
            health["components"]["rate_limiter"] = {
                "status": "healthy",
                "enabled": get_settings().security.rate_limit_enabled,
            }
        except Exception as e:
            health["components"]["rate_limiter"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health["status"] = "degraded"

        # System metrics (if detailed)
        if detailed:
            try:
                health["components"]["system"] = {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent,
                }
            except Exception:
                pass

        return {
            "success": True,
            "health": health,
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def get_server_metrics() -> dict[str, Any]:
    """Get comprehensive server metrics.

    Returns:
        Server metrics dictionary
    """
    try:
        settings = get_settings()
        conn_mgr = get_connection_manager()
        rate_limiter = get_rate_limiter()
        audit_logger = get_audit_logger()

        # Get audit statistics
        audit_stats = await audit_logger.get_statistics(hours=1)

        # Get rate limiter statistics
        rate_stats = rate_limiter.get_statistics()

        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Database connection pool status
        pool_status = "unknown"
        try:
            if conn_mgr.ping():
                pool_status = "connected"
        except Exception:
            pool_status = "disconnected"

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "percent": memory.percent,
                    "available_gb": memory.available / (1024**3),
                    "total_gb": memory.total / (1024**3),
                },
                "disk": {
                    "percent": disk.percent,
                    "free_gb": disk.free / (1024**3),
                    "total_gb": disk.total / (1024**3),
                },
            },
            "database": {
                "pool_status": pool_status,
                "host": settings.xugu.host,
                "port": settings.xugu.port,
                "database": settings.xugu.database,
            },
            "audit": {
                "last_hour": audit_stats,
            },
            "rate_limiter": {
                "enabled": settings.security.rate_limit_enabled,
                "statistics": rate_stats,
            },
            "chat2sql": {
                "schema_cache_ttl": settings.chat2sql.schema_cache_ttl,
                "enable_validation": settings.chat2sql.enable_validation,
            },
        }

    except Exception as e:
        logger.error(f"Get server metrics failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def get_connections() -> dict[str, Any]:
    """Get database connection information.

    Returns:
        Connection information
    """
    try:
        conn_mgr = get_connection_manager()

        return {
            "success": True,
            "pool_min_size": get_settings().xugu.pool_min_size,
            "pool_max_size": get_settings().xugu.pool_max_size,
            "pool_max_overflow": get_settings().xugu.pool_max_overflow,
            "pool_timeout": get_settings().xugu.pool_timeout,
            "connected": conn_mgr.ping(),
        }

    except Exception as e:
        logger.error(f"Get connections failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def test_query(
    sql: str | None = None,
) -> dict[str, Any]:
    """Test database connectivity with a test query.

    Args:
        sql: Optional custom SQL query to test (default: SELECT 1)

    Returns:
        Test query results
    """
    try:
        test_sql = sql or "SELECT 1 as test_value"
        start_time = time.time()

        result = operations.execute_query(test_sql)
        execution_time = (time.time() - start_time) * 1000

        return {
            "success": True,
            "sql": test_sql,
            "execution_time_ms": execution_time,
            "rows_returned": result.row_count if result.rows else 0,
            "columns": result.columns if result.columns else [],
        }

    except Exception as e:
        logger.error(f"Test query failed: {e}")
        return {
            "success": False,
            "sql": sql or "SELECT 1",
            "error": str(e),
        }


async def get_server_info() -> dict[str, Any]:
    """Get server information and configuration.

    Returns:
        Server information
    """
    try:
        settings = get_settings()

        # Get database info
        try:
            db_info = operations.get_database_info()
        except Exception as e:
            db_info = {"error": str(e)}

        return {
            "success": True,
            "server": {
                "name": settings.mcp_server.name,
                "version": settings.mcp_server.version,
                "log_level": settings.mcp_server.log_level,
            },
            "database": db_info,
            "llm": {
                "provider": settings.llm.provider,
                "model": settings.llm.model,
                "api_key_configured": bool(settings.llm.api_key),
            },
            "chat2sql": {
                "enabled": True,
                "schema_cache_enabled": settings.chat2sql.enable_schema_cache,
                "validation_enabled": settings.chat2sql.enable_validation,
            },
            "security": {
                "audit_log_enabled": settings.security.enable_audit_log,
                "rate_limit_enabled": settings.security.rate_limit_enabled,
                "max_query_time": settings.security.max_query_execution_time,
            },
        }

    except Exception as e:
        logger.error(f"Get server info failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def reload_config() -> dict[str, Any]:
    """Reload configuration (placeholder for future implementation).

    Returns:
        Reload result
    """
    # In a full implementation, this would reload settings from file/env
    return {
        "success": True,
        "message": "Configuration reload not yet implemented. Restart server to apply config changes.",
    }


async def get_query_history(
    limit: int = 50,
    operation_type: str | None = None,
) -> dict[str, Any]:
    """Get recent query history from audit log.

    Args:
        limit: Maximum number of entries
        operation_type: Filter by operation type

    Returns:
        Query history
    """
    try:
        from ..mcp_tools.audit_tools import get_audit_log
        from ..security import OperationType

        if operation_type:
            try:
                OperationType[operation_type.upper()]
            except KeyError:
                return {
                    "success": False,
                    "error": f"Invalid operation type: {operation_type}",
                }

        result = await get_audit_log(limit, operation_type)

        if result.get("success"):
            return {
                "success": True,
                "query_history": result.get("events", []),
                "count": result.get("count", 0),
            }
        else:
            return result

    except Exception as e:
        logger.error(f"Get query history failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def clear_all_caches() -> dict[str, Any]:
    """Clear all server caches.

    Returns:
        Clear cache results
    """
    try:
        chat2sql_engine = get_engine()
        chat2sql_engine.clear_schema_cache()

        return {
            "success": True,
            "message": "All caches cleared successfully",
            "caches_cleared": ["schema_cache"],
        }

    except Exception as e:
        logger.error(f"Clear caches failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def diagnose_connection(detailed: bool = False) -> dict[str, Any]:
    """Diagnose database connection issues.

    Args:
        detailed: Include detailed component status and system metrics

    Returns:
        Diagnostic information
    """
    try:
        settings = get_settings()
        diagnostics = {
            "success": True,
            "checks": [],
        }

        # Check configuration
        config_ok = bool(
            settings.xugu.host
            and settings.xugu.port
            and settings.xugu.database
            and settings.xugu.user
        )
        diagnostics["checks"].append({
            "name": "configuration",
            "status": "pass" if config_ok else "fail",
            "details": {
                "host": settings.xugu.host,
                "port": settings.xugu.port,
                "database": settings.xugu.database,
                "user": settings.xugu.user,
                "password_set": bool(settings.xugu.password),
            },
        })

        # Try to connect
        try:
            conn_mgr = get_connection_manager()
            connected = conn_mgr.ping()
            diagnostics["checks"].append({
                "name": "connection",
                "status": "pass" if connected else "fail",
                "details": {
                    "connected": connected,
                },
            })
        except Exception as e:
            diagnostics["checks"].append({
                "name": "connection",
                "status": "fail",
                "error": str(e),
            })

        # Test query
        try:
            result = await test_query()
            diagnostics["checks"].append({
                "name": "test_query",
                "status": "pass" if result.get("success") else "fail",
                "details": {
                    "execution_time_ms": result.get("execution_time_ms"),
                },
            })
        except Exception as e:
            diagnostics["checks"].append({
                "name": "test_query",
                "status": "fail",
                "error": str(e),
            })

        # Overall status
        all_pass = all(check.get("status") == "pass" for check in diagnostics["checks"])
        diagnostics["overall_status"] = "healthy" if all_pass else "unhealthy"

        return diagnostics

    except Exception as e:
        logger.error(f"Diagnose connection failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }
