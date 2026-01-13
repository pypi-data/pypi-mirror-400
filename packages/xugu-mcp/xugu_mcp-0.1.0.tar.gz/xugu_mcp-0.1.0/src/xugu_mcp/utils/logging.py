"""
Logging configuration for XuguDB MCP Server.
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from loguru import logger as loguru_logger

from ..config.settings import get_settings


class MCPLogger:
    """MCP Server logger with configurable output."""

    def __init__(self, name: str = "xugu-mcp"):
        self.name = name
        self._setup()

    def _setup(self):
        """Set up logging configuration."""
        settings = get_settings()
        log_level = settings.mcp_server.log_level

        # Remove default handler
        loguru_logger.remove()

        # Add stderr handler with color and formatting
        loguru_logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True,
        )

        # Add file handler for audit log if enabled
        if settings.security.enable_audit_log:
            log_path = Path(settings.security.audit_log_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            loguru_logger.add(
                log_path,
                level="INFO",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                rotation="1 day",
                retention="30 days",
                compression="zip",
            )

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get a standard logging.Logger instance."""
        logger_name = f"{self.name}.{name}" if name else self.name
        return logging.getLogger(logger_name)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        loguru_logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        loguru_logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        loguru_logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        loguru_logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        loguru_logger.critical(message, **kwargs)


# Global logger instance
_mcp_logger: Optional[MCPLogger] = None


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get logger instance.

    Args:
        name: Optional logger name suffix

    Returns:
        Logger instance
    """
    global _mcp_logger
    if _mcp_logger is None:
        _mcp_logger = MCPLogger()
    return _mcp_logger.get_logger(name)


def get_mcp_logger() -> MCPLogger:
    """Get the MCP logger instance.

    Returns:
        MCPLogger instance
    """
    global _mcp_logger
    if _mcp_logger is None:
        _mcp_logger = MCPLogger()
    return _mcp_logger
