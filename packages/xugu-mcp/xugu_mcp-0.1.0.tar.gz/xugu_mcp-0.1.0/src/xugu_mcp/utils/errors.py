"""
Custom error classes for XuguDB MCP Server.
"""
from typing import Optional, Any


class XuguMCPError(Exception):
    """Base exception for XuguDB MCP Server."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(XuguMCPError):
    """Raised when configuration is invalid or missing."""

    pass


class ConnectionError(XuguMCPError):
    """Raised when database connection fails."""

    pass


class QueryExecutionError(XuguMCPError):
    """Raised when query execution fails."""

    def __init__(
        self,
        message: str,
        sql: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.sql = sql


class ValidationError(XuguMCPError):
    """Raised when input validation fails."""

    pass


class SQLInjectionWarning(XuguMCPError):
    """Raised when potential SQL injection is detected."""

    pass


class SQLError(QueryExecutionError):
    """Raised when SQL syntax or execution error occurs."""

    pass


class SecurityError(XuguMCPError):
    """Raised when a security violation is detected."""

    pass


class RateLimitError(XuguMCPError):
    """Raised when rate limit is exceeded."""

    pass


class TimeoutError(XuguMCPError):
    """Raised when operation timeout occurs."""

    pass


class LLMError(XuguMCPError):
    """Raised when LLM provider fails."""

    pass


class Chat2SQLError(XuguMCPError):
    """Raised when Chat2SQL conversion fails."""

    pass


class SchemaError(XuguMCPError):
    """Raised when schema operation fails."""

    pass
