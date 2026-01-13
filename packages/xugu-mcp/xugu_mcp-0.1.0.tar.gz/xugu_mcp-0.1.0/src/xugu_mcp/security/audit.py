"""
Audit logging for XuguDB MCP Server.

Comprehensive logging of all database operations for security and compliance.
"""
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any
from dataclasses import dataclass, asdict
from enum import Enum

from ..config.settings import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class OperationType(Enum):
    """Types of database operations."""

    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    ALTER = "ALTER"
    DROP = "DROP"
    TRUNCATE = "TRUNCATE"
    EXECUTE = "EXECUTE"
    CHAT2SQL = "CHAT2SQL"
    VALIDATE = "VALIDATE"
    EXPLAIN = "EXPLAIN"
    OTHER = "OTHER"


class OperationStatus(Enum):
    """Status of operation execution."""

    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"
    BLOCKED = "blocked"


@dataclass
class AuditEvent:
    """An audit event for logging."""

    timestamp: str
    operation_type: str
    operation_status: str
    sql: str | None = None
    sql_anonymized: str | None = None
    table_name: str | None = None
    rows_affected: int = 0
    execution_time_ms: float = 0
    error_message: str | None = None
    user: str | None = None
    client_ip: str | None = None
    extra: dict | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class AuditLogger:
    """Audit logger for database operations."""

    def __init__(
        self,
        log_path: str | None = None,
        enable_console: bool = True,
        buffer_size: int = 100,
        flush_interval: int = 5,
    ):
        """Initialize audit logger.

        Args:
            log_path: Path to audit log file
            enable_console: Also log to console
            buffer_size: Buffer size before flushing
            flush_interval: Flush interval in seconds
        """
        self.settings = get_settings()
        self.log_path = log_path or self.settings.security.audit_log_path
        self.enable_console = enable_console
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval

        self._buffer: list[AuditEvent] = []
        self._lock = asyncio.Lock()
        self._flush_task: asyncio.Task | None = None
        self._shutdown = False

        # Create log directory if needed
        if self.log_path:
            Path(self.log_path).parent.mkdir(parents=True, exist_ok=True)

        # Start background flush task
        if self.settings.security.enable_audit_log:
            self._start_flush_task()

    async def log(
        self,
        operation_type: OperationType,
        operation_status: OperationStatus,
        sql: str | None = None,
        table_name: str | None = None,
        rows_affected: int = 0,
        execution_time_ms: float = 0,
        error_message: str | None = None,
        extra: dict | None = None,
    ) -> AuditEvent:
        """Log an audit event.

        Args:
            operation_type: Type of operation
            operation_status: Status of operation
            sql: SQL query executed
            table_name: Table affected
            rows_affected: Number of rows affected
            execution_time_ms: Execution time in milliseconds
            error_message: Error message if failed
            extra: Extra metadata

        Returns:
            AuditEvent that was logged
        """
        if not self.settings.security.enable_audit_log:
            return AuditEvent(
                timestamp=datetime.now().isoformat(),
                operation_type=operation_type.value,
                operation_status=operation_status.value,
            )

        # Anonymize SQL for logging
        sql_anonymized = None
        if sql:
            sql_anonymized = self._anonymize_sql(sql)

        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            operation_type=operation_type.value,
            operation_status=operation_status.value,
            sql=sql,
            sql_anonymized=sql_anonymized,
            table_name=table_name,
            rows_affected=rows_affected,
            execution_time_ms=execution_time_ms,
            error_message=error_message,
            extra=extra,
        )

        async with self._lock:
            self._buffer.append(event)

            # Flush if buffer is full
            if len(self._buffer) >= self.buffer_size:
                await self._flush_buffer()

        return event

    async def log_query(
        self,
        sql: str,
        execution_time_ms: float = 0,
        row_count: int = 0,
        error: str | None = None,
    ) -> AuditEvent:
        """Log a query execution.

        Args:
            sql: SQL query executed
            execution_time_ms: Execution time in milliseconds
            row_count: Number of rows returned/affected
            error: Error message if failed

        Returns:
            AuditEvent that was logged
        """
        operation_type = self._detect_operation_type(sql)
        operation_status = OperationStatus.SUCCESS if not error else OperationStatus.ERROR

        # Extract table name
        table_name = self._extract_table_name(sql)

        return await self.log(
            operation_type=operation_type,
            operation_status=operation_status,
            sql=sql,
            table_name=table_name,
            rows_affected=row_count,
            execution_time_ms=execution_time_ms,
            error_message=error,
        )

    async def log_chat2sql(
        self,
        question: str,
        sql: str,
        execution_time_ms: float = 0,
        is_valid: bool = True,
        error: str | None = None,
    ) -> AuditEvent:
        """Log a Chat2SQL operation.

        Args:
            question: Natural language question
            sql: Generated SQL query
            execution_time_ms: Execution time in milliseconds
            is_valid: Whether the SQL is valid
            error: Error message if failed

        Returns:
            AuditEvent that was logged
        """
        return await self.log(
            operation_type=OperationType.CHAT2SQL,
            operation_status=OperationStatus.SUCCESS if is_valid and not error else OperationStatus.ERROR,
            sql=sql,
            execution_time_ms=execution_time_ms,
            error_message=error,
            extra={"question": question},
        )

    async def log_blocked_operation(
        self,
        sql: str,
        reason: str,
    ) -> AuditEvent:
        """Log a blocked operation.

        Args:
            sql: SQL query that was blocked
            reason: Reason for blocking

        Returns:
            AuditEvent that was logged
        """
        return await self.log(
            operation_type=self._detect_operation_type(sql),
            operation_status=OperationStatus.BLOCKED,
            sql=sql,
            error_message=f"Blocked: {reason}",
        )

    async def _flush_buffer(self):
        """Flush buffer to disk."""
        if not self._buffer:
            return

        events_to_write = self._buffer.copy()
        self._buffer.clear()

        try:
            if self.log_path:
                async with asyncio.Lock():
                    with open(self.log_path, "a", encoding="utf-8") as f:
                        for event in events_to_write:
                            f.write(event.to_json() + "\n")

            if self.enable_console:
                for event in events_to_write:
                    logger.info(f"[AUDIT] {event.to_json()}")

        except Exception as e:
            logger.error(f"Failed to flush audit log: {e}")
            # Put events back in buffer
            self._buffer.extend(events_to_write)

    def _start_flush_task(self):
        """Start background flush task."""
        async def flush_loop():
            while not self._shutdown:
                await asyncio.sleep(self.flush_interval)
                if self._buffer:
                    await self._flush_buffer()

        self._flush_task = asyncio.create_task(flush_loop())

    async def shutdown(self):
        """Shutdown audit logger and flush remaining events."""
        self._shutdown = True

        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        # Final flush
        await self._flush_buffer()

    def _detect_operation_type(self, sql: str) -> OperationType:
        """Detect operation type from SQL.

        Args:
            sql: SQL query

        Returns:
            Operation type
        """
        if not sql:
            return OperationType.OTHER

        sql_upper = sql.strip().upper()

        if sql_upper.startswith("SELECT"):
            return OperationType.SELECT
        elif sql_upper.startswith("INSERT"):
            return OperationType.INSERT
        elif sql_upper.startswith("UPDATE"):
            return OperationType.UPDATE
        elif sql_upper.startswith("DELETE"):
            return OperationType.DELETE
        elif sql_upper.startswith("CREATE"):
            return OperationType.CREATE
        elif sql_upper.startswith("ALTER"):
            return OperationType.ALTER
        elif sql_upper.startswith("DROP"):
            return OperationType.DROP
        elif sql_upper.startswith("TRUNCATE"):
            return OperationType.TRUNCATE
        elif sql_upper.startswith("EXPLAIN"):
            return OperationType.EXPLAIN
        else:
            return OperationType.OTHER

    def _extract_table_name(self, sql: str) -> str | None:
        """Extract table name from SQL.

        Args:
            sql: SQL query

        Returns:
            Table name or None
        """
        import re

        sql_upper = sql.upper()

        # Try FROM clause
        from_match = re.search(r"FROM\s+(\w+)", sql_upper)
        if from_match:
            return from_match.group(1)

        # Try INTO clause
        into_match = re.search(r"INTO\s+(\w+)", sql_upper)
        if into_match:
            return into_match.group(1)

        # Try UPDATE clause
        update_match = re.search(r"UPDATE\s+(\w+)", sql_upper)
        if update_match:
            return update_match.group(1)

        # Try TABLE clause
        table_match = re.search(r"TABLE\s+(\w+)", sql_upper)
        if table_match:
            return table_match.group(1)

        return None

    def _anonymize_sql(self, sql: str) -> str:
        """Anonymize SQL query for logging.

        Args:
            sql: SQL query

        Returns:
            Anonymized SQL
        """
        import re

        # Replace string literals
        anonymized = re.sub(r"'[^']*'", "'?'", sql)

        # Replace numbers
        anonymized = re.sub(r"\b\d+\b", "?", anonymized)

        return anonymized

    async def get_recent_events(
        self,
        limit: int = 100,
        operation_type: OperationType | None = None,
    ) -> list[AuditEvent]:
        """Get recent audit events from log file.

        Args:
            limit: Maximum number of events to return
            operation_type: Filter by operation type

        Returns:
            List of recent audit events
        """
        if not self.log_path or not Path(self.log_path).exists():
            return []

        events = []
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event_data = json.loads(line.strip())
                        event = AuditEvent(**event_data)

                        if operation_type is None or event.operation_type == operation_type.value:
                            events.append(event)

                        if len(events) >= limit:
                            break
                    except (json.JSONDecodeError, TypeError):
                        continue

        except Exception as e:
            logger.error(f"Failed to read audit log: {e}")

        return events[-limit:][::-1]  # Return in reverse chronological order

    async def get_statistics(
        self,
        hours: int = 24,
    ) -> dict[str, Any]:
        """Get audit statistics for recent period.

        Args:
            hours: Number of hours to look back

        Returns:
            Statistics dictionary
        """
        events = await self.get_recent_events(limit=10000)

        # Filter by time
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()

        recent_events = [
            e for e in events
            if e.timestamp >= cutoff_str
        ]

        # Calculate statistics
        stats = {
            "total_operations": len(recent_events),
            "successful_operations": 0,
            "failed_operations": 0,
            "blocked_operations": 0,
            "by_type": {},
            "avg_execution_time_ms": 0,
            "total_rows_affected": 0,
        }

        total_time = 0
        time_count = 0

        for event in recent_events:
            # Count by status
            if event.operation_status == OperationStatus.SUCCESS.value:
                stats["successful_operations"] += 1
            elif event.operation_status == OperationStatus.ERROR.value:
                stats["failed_operations"] += 1
            elif event.operation_status == OperationStatus.BLOCKED.value:
                stats["blocked_operations"] += 1

            # Count by type
            stats["by_type"][event.operation_type] = stats["by_type"].get(event.operation_type, 0) + 1

            # Execution time
            if event.execution_time_ms > 0:
                total_time += event.execution_time_ms
                time_count += 1

            # Rows affected
            stats["total_rows_affected"] += event.rows_affected

        # Average execution time
        if time_count > 0:
            stats["avg_execution_time_ms"] = total_time / time_count

        return stats


# Global audit logger instance
_audit_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance.

    Returns:
        AuditLogger instance
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


async def close_audit_logger():
    """Close global audit logger."""
    global _audit_logger
    if _audit_logger:
        await _audit_logger.shutdown()
        _audit_logger = None
