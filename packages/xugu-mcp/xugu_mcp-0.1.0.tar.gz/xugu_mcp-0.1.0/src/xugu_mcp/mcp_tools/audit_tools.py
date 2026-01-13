"""
Audit and Security MCP tools for XuguDB MCP Server.
"""
from typing import Any

from ..security import (
    get_audit_logger,
    get_rate_limiter,
    get_access_controller,
    OperationType,
    OperationStatus,
)
from ..utils.logging import get_logger

logger = get_logger(__name__)


async def get_audit_log(
    limit: int = 100,
    operation_type: str | None = None,
) -> dict[str, Any]:
    """Get recent audit log entries.

    Args:
        limit: Maximum number of entries to return
        operation_type: Filter by operation type (SELECT, INSERT, etc.)

    Returns:
        Dictionary with audit log entries
    """
    try:
        audit_logger = get_audit_logger()

        op_type = None
        if operation_type:
            try:
                op_type = OperationType[operation_type.upper()]
            except KeyError:
                return {
                    "success": False,
                    "error": f"Invalid operation type: {operation_type}",
                }

        events = await audit_logger.get_recent_events(limit, op_type)

        return {
            "success": True,
            "count": len(events),
            "events": [event.to_dict() for event in events],
        }

    except Exception as e:
        logger.error(f"Get audit log failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def get_audit_statistics(
    hours: int = 24,
) -> dict[str, Any]:
    """Get audit statistics for recent period.

    Args:
        hours: Number of hours to look back

    Returns:
        Dictionary with audit statistics
    """
    try:
        audit_logger = get_audit_logger()
        stats = await audit_logger.get_statistics(hours)

        return {
            "success": True,
            "period_hours": hours,
            "statistics": stats,
        }

    except Exception as e:
        logger.error(f"Get audit statistics failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def get_rate_limit_stats() -> dict[str, Any]:
    """Get rate limiter statistics.

    Returns:
        Dictionary with rate limiter statistics
    """
    try:
        rate_limiter = get_rate_limiter()
        stats = rate_limiter.get_statistics()

        return {
            "success": True,
            "statistics": stats,
        }

    except Exception as e:
        logger.error(f"Get rate limit stats failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def reset_rate_limit_stats() -> dict[str, Any]:
    """Reset rate limiter statistics.

    Returns:
        Dictionary with operation result
    """
    try:
        rate_limiter = get_rate_limiter()
        rate_limiter.reset_statistics()

        return {
            "success": True,
            "message": "Rate limiter statistics reset successfully",
        }

    except Exception as e:
        logger.error(f"Reset rate limit stats failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def clear_client_rate_limit(
    client_id: str,
) -> dict[str, Any]:
    """Clear rate limit for a specific client.

    Args:
        client_id: Client identifier to clear

    Returns:
        Dictionary with operation result
    """
    try:
        rate_limiter = get_rate_limiter()
        rate_limiter.clear_client(client_id)

        return {
            "success": True,
            "message": f"Rate limit cleared for client: {client_id}",
        }

    except Exception as e:
        logger.error(f"Clear client rate limit failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def list_roles() -> dict[str, Any]:
    """List all available roles.

    Returns:
        Dictionary with available roles
    """
    try:
        access_controller = get_access_controller()
        roles = access_controller.list_roles()

        role_details = []
        for role_name in roles:
            role = access_controller.get_role(role_name)
            if role:
                role_details.append({
                    "name": role.name,
                    "permissions": [p.value for p in role.permissions],
                    "description": role.description,
                    "table_access_count": len(role.table_access),
                })

        return {
            "success": True,
            "roles": role_details,
        }

    except Exception as e:
        logger.error(f"List roles failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def get_role_details(
    role_name: str,
) -> dict[str, Any]:
    """Get details of a specific role.

    Args:
        role_name: Name of the role

    Returns:
        Dictionary with role details
    """
    try:
        access_controller = get_access_controller()
        role = access_controller.get_role(role_name)

        if not role:
            return {
                "success": False,
                "error": f"Role not found: {role_name}",
            }

        table_access_details = []
        for ta in role.table_access:
            table_access_details.append({
                "table_pattern": ta.table_pattern,
                "permissions": [p.value for p in ta.permissions],
                "allowed_columns": list(ta.allowed_columns) if ta.allowed_columns else None,
                "denied_columns": list(ta.denied_columns) if ta.denied_columns else None,
                "where_filter": ta.where_filter,
            })

        return {
            "success": True,
            "role": {
                "name": role.name,
                "permissions": [p.value for p in role.permissions],
                "description": role.description,
                "table_access": table_access_details,
            },
        }

    except Exception as e:
        logger.error(f"Get role details failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def check_permission(
    role_name: str,
    operation: str,
    table_name: str | None = None,
) -> dict[str, Any]:
    """Check if a role has permission for an operation.

    Args:
        role_name: Name of the role
        operation: SQL operation (SELECT, INSERT, etc.)
        table_name: Optional table name

    Returns:
        Dictionary with check result
    """
    try:
        access_controller = get_access_controller()
        allowed = access_controller.check_permission(role_name, operation, table_name)

        return {
            "success": True,
            "allowed": allowed,
            "role": role_name,
            "operation": operation,
            "table_name": table_name,
        }

    except Exception as e:
        logger.error(f"Check permission failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def clear_schema_cache_audit() -> dict[str, Any]:
    """Clear the schema cache (audit action).

    Returns:
        Dictionary with operation result
    """
    try:
        # This would call the Chat2SQL schema manager's clear_cache method
        # For now, just log the action
        audit_logger = get_audit_logger()
        await audit_logger.log(
            operation_type=OperationType.OTHER,
            operation_status=OperationStatus.SUCCESS,
            extra={"action": "clear_schema_cache"},
        )

        return {
            "success": True,
            "message": "Schema cache clear action logged",
        }

    except Exception as e:
        logger.error(f"Clear schema cache audit failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def get_security_status() -> dict[str, Any]:
    """Get overall security status.

    Returns:
        Dictionary with security status information
    """
    try:
        from ..config.settings import get_settings

        settings = get_settings()
        rate_limiter = get_rate_limiter()
        audit_logger = get_audit_logger()

        # Get rate limiter stats
        rate_stats = rate_limiter.get_statistics()

        # Get audit stats
        audit_stats = await audit_logger.get_statistics(hours=24)

        # Get role list
        access_controller = get_access_controller()
        roles = access_controller.list_roles()

        return {
            "success": True,
            "security": {
                "rate_limiting": {
                    "enabled": settings.security.rate_limit_enabled,
                    "max_queries_per_minute": settings.security.rate_limit_max_queries,
                    "statistics": rate_stats,
                },
                "audit_logging": {
                    "enabled": settings.security.enable_audit_log,
                    "log_path": settings.security.audit_log_path,
                    "statistics_24h": audit_stats,
                },
                "access_control": {
                    "allowed_operations": settings.security.allowed_operations,
                    "blocked_patterns": settings.security.blocked_patterns,
                    "available_roles": roles,
                },
            },
        }

    except Exception as e:
        logger.error(f"Get security status failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }
