"""
Query execution hooks for XuguDB MCP Server.

Pre and post execution hooks for query interception and modification.
"""
import time
from typing import Callable, Any, List
from dataclasses import dataclass
from contextlib import asynccontextmanager

from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class QueryContext:
    """Context for query execution hooks."""

    sql: str
    params: tuple | None = None
    user: str | None = None
    client_ip: str | None = None
    operation_type: str | None = None
    table_name: str | None = None
    extra: dict | None = None


@dataclass
class QueryResult:
    """Result of query execution."""

    success: bool
    rows: int = 0
    execution_time_ms: float = 0
    error: str | None = None
    result: Any = None


class QueryHook:
    """Base class for query hooks."""

    async def pre_execute(
        self,
        context: QueryContext,
    ) -> tuple[bool, str | None]:
        """Called before query execution.

        Args:
            context: Query execution context

        Returns:
            Tuple of (should_continue, error_message)
            - should_continue: False to block execution
            - error_message: Error message if blocking
        """
        return True, None

    async def post_execute(
        self,
        context: QueryContext,
        result: QueryResult,
    ):
        """Called after query execution.

        Args:
            context: Query execution context
            result: Query execution result
        """
        pass

    async def on_error(
        self,
        context: QueryContext,
        error: Exception,
    ):
        """Called on query execution error.

        Args:
            context: Query execution context
            error: Exception that occurred
        """
        pass


class AuditLogHook(QueryHook):
    """Hook that logs all queries to audit log."""

    def __init__(self):
        """Initialize audit log hook."""
        # Import here to avoid circular dependency
        from .audit import get_audit_logger
        self.audit_logger = get_audit_logger()

    async def post_execute(
        self,
        context: QueryContext,
        result: QueryResult,
    ):
        """Log query execution to audit log."""
        await self.audit_logger.log_query(
            sql=context.sql,
            execution_time_ms=result.execution_time_ms,
            row_count=result.rows,
            error=result.error,
        )

    async def on_error(
        self,
        context: QueryContext,
        error: Exception,
    ):
        """Log query error to audit log."""
        await self.audit_logger.log_query(
            sql=context.sql,
            error=str(error),
        )


class RateLimitHook(QueryHook):
    """Hook that enforces rate limits."""

    def __init__(self):
        """Initialize rate limit hook."""
        from .rate_limiter import get_rate_limiter
        self.rate_limiter = get_rate_limiter()

    async def pre_execute(
        self,
        context: QueryContext,
    ) -> tuple[bool, str | None]:
        """Check rate limit before execution."""
        result = await self.rate_limiter.check_rate_limit(
            client_id=context.client_ip,
        )

        if not result.allowed:
            retry_after = int(result.retry_after) if result.retry_after else 60
            return False, f"Rate limit exceeded. Retry after {retry_after} seconds."

        return True, None


class AccessControlHook(QueryHook):
    """Hook that enforces access control."""

    def __init__(self):
        """Initialize access control hook."""
        from .access_control import get_access_controller
        self.access_controller = get_access_controller()

    async def pre_execute(
        self,
        context: QueryContext,
    ) -> tuple[bool, str | None]:
        """Check access control before execution."""
        allowed, reason = self.access_controller.check_sql(
            role_name=context.user,  # Use user field as role
            sql=context.sql,
        )

        if not allowed:
            return False, reason or "Access denied"

        # Apply any SQL filters
        context.sql = self.access_controller.filter_sql(
            role_name=context.user,
            sql=context.sql,
        )

        return True, None


class ExecutionTimeHook(QueryHook):
    """Hook that tracks execution time and logs slow queries."""

    def __init__(self, slow_threshold_ms: float = 1000):
        """Initialize execution time hook.

        Args:
            slow_threshold_ms: Threshold for logging slow queries
        """
        self.slow_threshold_ms = slow_threshold_ms
        self._start_time: float | None = None

    async def pre_execute(
        self,
        context: QueryContext,
    ) -> tuple[bool, str | None]:
        """Record start time."""
        self._start_time = time.time()
        return True, None

    async def post_execute(
        self,
        context: QueryContext,
        result: QueryResult,
    ):
        """Check execution time and log slow queries."""
        if self._start_time and result.execution_time_ms > self.slow_threshold_ms:
            logger.warning(
                f"Slow query detected: {result.execution_time_ms:.2f}ms - "
                f"{context.sql[:100]}..."
            )


class QuerySizeLimitHook(QueryHook):
    """Hook that limits result set size."""

    def __init__(self, max_rows: int = 10000):
        """Initialize query size limit hook.

        Args:
            max_rows: Maximum rows allowed in result
        """
        self.max_rows = max_rows

    async def pre_execute(
        self,
        context: QueryContext,
    ) -> tuple[bool, str | None]:
        """Add LIMIT clause if not present."""
        if context.operation_type == "SELECT":
            sql_upper = context.sql.upper()
            if "LIMIT" not in sql_upper:
                # Add LIMIT clause
                context.sql = f"{context.sql} LIMIT {self.max_rows}"

        return True, None


class DangerousQueryHook(QueryHook):
    """Hook that blocks dangerous queries."""

    DANGEROUS_PATTERNS = [
        "DROP DATABASE",
        "DROP SCHEMA",
        "TRUNCATE.*CASCADE",
        "DELETE FROM \\w+;$",  # DELETE without WHERE
        "UPDATE \\w+ SET [^;]+;$",  # UPDATE without WHERE
    ]

    async def pre_execute(
        self,
        context: QueryContext,
    ) -> tuple[bool, str | None]:
        """Check for dangerous patterns."""
        import re

        sql_upper = context.sql.upper()

        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, sql_upper):
                return False, f"Dangerous query detected: {pattern}"

        return True, None


class HookManager:
    """Manager for query execution hooks."""

    def __init__(self):
        """Initialize hook manager."""
        self._pre_hooks: List[QueryHook] = []
        self._post_hooks: List[QueryHook] = []
        self._error_hooks: List[QueryHook] = []

    def register_hook(self, hook: QueryHook):
        """Register a query hook.

        Args:
            hook: Hook to register
        """
        self._pre_hooks.append(hook)
        self._post_hooks.append(hook)
        self._error_hooks.append(hook)

    def unregister_hook(self, hook: QueryHook):
        """Unregister a query hook.

        Args:
            hook: Hook to unregister
        """
        if hook in self._pre_hooks:
            self._pre_hooks.remove(hook)
        if hook in self._post_hooks:
            self._post_hooks.remove(hook)
        if hook in self._error_hooks:
            self._error_hooks.remove(hook)

    @asynccontextmanager
    async def execute_with_hooks(
        self,
        sql: str,
        params: tuple | None = None,
        user: str | None = None,
        client_ip: str | None = None,
        executor: Callable | None = None,
    ):
        """Execute query with hooks.

        Args:
            sql: SQL query
            params: Query parameters
            user: User/role name
            client_ip: Client IP address
            executor: Function that executes the query

        Yields:
            Tuple of (context, result)
        """
        # Create context
        context = QueryContext(
            sql=sql,
            params=params,
            user=user,
            client_ip=client_ip,
        )

        result = QueryResult(success=False)

        try:
            # Pre-execution hooks
            for hook in self._pre_hooks:
                should_continue, error = await hook.pre_execute(context)
                if not should_continue:
                    result.error = error or "Blocked by hook"
                    yield context, result
                    return

            # Record start time
            start_time = time.time()

            # Execute query
            if executor:
                query_result = await executor(sql, params)
                result.result = query_result
                result.success = True

                # Try to get row count
                if hasattr(query_result, "row_count"):
                    result.rows = query_result.row_count
                elif hasattr(query_result, "rows") and query_result.rows:
                    result.rows = len(query_result.rows)

            execution_time = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time

            # Post-execution hooks
            for hook in self._post_hooks:
                await hook.post_execute(context, result)

            yield context, result

        except Exception as e:
            result.error = str(e)

            # Error hooks
            for hook in self._error_hooks:
                try:
                    await hook.on_error(context, e)
                except Exception as hook_error:
                    logger.error(f"Error in error hook: {hook_error}")

            yield context, result

    def clear_hooks(self):
        """Clear all hooks."""
        self._pre_hooks.clear()
        self._post_hooks.clear()
        self._error_hooks.clear()

    def get_hook_count(self) -> int:
        """Get number of registered hooks.

        Returns:
            Number of hooks
        """
        return len(self._pre_hooks)


# Global hook manager instance
_hook_manager: HookManager | None = None


def get_hook_manager() -> HookManager:
    """Get global hook manager instance.

    Returns:
        HookManager instance
    """
    global _hook_manager
    if _hook_manager is None:
        _hook_manager = HookManager()
        # Register default hooks
        _hook_manager.register_hook(AuditLogHook())
        _hook_manager.register_hook(ExecutionTimeHook())
    return _hook_manager


def reset_hook_manager():
    """Reset global hook manager (useful for testing)."""
    global _hook_manager
    _hook_manager = None
