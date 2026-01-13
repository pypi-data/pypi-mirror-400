"""
Security Module for XuguDB MCP Server.

Provides audit logging, rate limiting, access control, and query hooks.
"""
from .audit import AuditLogger, AuditEvent, OperationType, OperationStatus, get_audit_logger
from .rate_limiter import RateLimiter, RateLimitResult, get_rate_limiter
from .access_control import (
    AccessController,
    Permission,
    Role,
    TableAccess,
    Roles,
    get_access_controller,
)
from .hooks import (
    HookManager,
    QueryContext,
    QueryResult,
    QueryHook,
    get_hook_manager,
)

__all__ = [
    # Audit
    "AuditLogger",
    "AuditEvent",
    "OperationType",
    "OperationStatus",
    "get_audit_logger",
    # Rate Limiting
    "RateLimiter",
    "RateLimitResult",
    "get_rate_limiter",
    # Access Control
    "AccessController",
    "Permission",
    "Role",
    "TableAccess",
    "Roles",
    "get_access_controller",
    # Hooks
    "HookManager",
    "QueryContext",
    "QueryResult",
    "QueryHook",
    "get_hook_manager",
]
