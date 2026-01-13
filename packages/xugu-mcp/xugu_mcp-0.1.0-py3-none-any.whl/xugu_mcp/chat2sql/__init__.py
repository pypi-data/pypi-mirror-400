"""
Chat2SQL Module for XuguDB MCP Server.

Provides natural language to SQL conversion capabilities.
"""
from .schema_manager import SchemaManager, TableSchema, DatabaseSchema
from .sql_validator import SQLValidator, ValidationResult, ValidationIssue, ValidationSeverity
from .sql_sanitizer import SQLSanitizer
from .prompt_builder import PromptBuilder, Example
from .engine import Chat2SQLEngine, Chat2SQLResult, SQLOptimizationResult

__all__ = [
    "SchemaManager",
    "TableSchema",
    "DatabaseSchema",
    "SQLValidator",
    "ValidationResult",
    "ValidationIssue",
    "ValidationSeverity",
    "SQLSanitizer",
    "PromptBuilder",
    "Example",
    "Chat2SQLEngine",
    "Chat2SQLResult",
    "SQLOptimizationResult",
]
