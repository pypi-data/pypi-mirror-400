"""
SQL Validator for Chat2SQL engine.

Validates SQL queries for syntax, security, and safety.
"""
import re
from typing import List
from dataclasses import dataclass
from enum import Enum

from ..config.settings import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """A validation issue found in SQL."""

    severity: ValidationSeverity
    code: str
    message: str
    line: int | None = None
    column: int | None = None
    suggestion: str | None = None


@dataclass
class ValidationResult:
    """Result of SQL validation."""

    is_valid: bool
    issues: List[ValidationIssue]
    normalized_sql: str | None = None

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return any(
            issue.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)
            for issue in self.issues
        )

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return any(
            issue.severity == ValidationSeverity.WARNING
            for issue in self.issues
        )

    def get_critical_issues(self) -> List[ValidationIssue]:
        """Get critical issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.CRITICAL]

    def get_error_issues(self) -> List[ValidationIssue]:
        """Get error issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    def get_warning_issues(self) -> List[ValidationIssue]:
        """Get warning issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]


class SQLValidator:
    """Validator for SQL queries."""

    # Dangerous SQL patterns
    DANGEROUS_PATTERNS = [
        (r"DROP\s+DATABASE", "DROP DATABASE is extremely dangerous"),
        (r"DROP\s+SCHEMA", "DROP SCHEMA is extremely dangerous"),
        (r"TRUNCATE\s+.*\s+CASCADE", "TRUNCATE CASCADE is dangerous"),
        (r"DELETE\s+FROM\s+\w+\s*$", "DELETE without WHERE clause will delete all rows"),
        (r"UPDATE\s+\w+\s+SET\s+\w+\s*=.*\s*$", "UPDATE without WHERE clause will update all rows"),
        (r"ALTER\s+SYSTEM", "ALTER SYSTEM changes database configuration"),
        (r"GRANT\s+ALL\s+PRIVILEGES", "GRANT ALL PRIVILEGES is dangerous"),
        (r"EXEC\s*\(", "EXEC() allows arbitrary command execution"),
        (r"EVAL\s*\(", "EVAL() allows arbitrary code execution"),
        (r";\s*DROP", "Multiple statements with DROP"),
        (r";\s*DELETE", "Multiple statements with DELETE"),
        (r";\s*UPDATE", "Multiple statements with UPDATE"),
    ]

    # SQL injection patterns
    INJECTION_PATTERNS = [
        (r"\'\s*OR\s*", "Potential SQL injection with OR"),
        (r"\'\s*AND\s*", "Potential SQL injection with AND"),
        (r"\'\s*;\s*", "Potential SQL injection with statement separator"),
        (r"\'\s*--", "Potential SQL injection with comment"),
        (r"\'\s*#", "Potential SQL injection with comment"),
        (r"\$\{[^}]*\}", "Potential injection with variable substitution"),
        (r"UNION\s+SELECT", "Potential SQL injection with UNION SELECT"),
    ]

    # Regex patterns for SQL syntax elements
    SQL_PATTERNS = {
        "select": r"^\s*SELECT\s+",
        "insert": r"^\s*INSERT\s+INTO\s+",
        "update": r"^\s*UPDATE\s+\w+\s+SET\s+",
        "delete": r"^\s*DELETE\s+FROM\s+",
        "create": r"^\s*CREATE\s+(TABLE|INDEX|VIEW|DATABASE|SCHEMA)\s+",
        "alter": r"^\s*ALTER\s+(TABLE|INDEX|VIEW|DATABASE)\s+",
        "drop": r"^\s*DROP\s+(TABLE|INDEX|VIEW|DATABASE|SCHEMA)\s+",
        "truncate": r"^\s*TRUNCATE\s+TABLE\s+",
    }

    def __init__(self):
        """Initialize SQL validator."""
        self.settings = get_settings()
        self.allowed_operations = self.settings.security.allowed_operations
        self.blocked_patterns = self.settings.security.blocked_patterns

    def validate(self, sql: str, allow_ddl: bool = True) -> ValidationResult:
        """Validate SQL query.

        Args:
            sql: SQL query to validate
            allow_ddl: Whether to allow DDL operations

        Returns:
            ValidationResult with issues found
        """
        issues = []
        normalized = self._normalize_sql(sql)

        # Check for dangerous patterns
        issues.extend(self._check_dangerous_patterns(normalized))

        # Check for injection patterns
        issues.extend(self._check_injection_patterns(normalized))

        # Check operation type
        operation = self._detect_operation(normalized)
        if operation and not self._is_operation_allowed(operation, allow_ddl):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="OPERATION_NOT_ALLOWED",
                message=f"Operation '{operation}' is not allowed",
                suggestion=f"Allowed operations: {', '.join(self.allowed_operations)}",
            ))

        # Check custom blocked patterns
        issues.extend(self._check_blocked_patterns(normalized))

        # Syntax validation (basic)
        issues.extend(self._check_syntax(normalized))

        # Check for common mistakes
        issues.extend(self._check_common_mistakes(normalized))

        is_valid = not any(
            issue.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)
            for issue in issues
        )

        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            normalized_sql=normalized,
        )

    def _normalize_sql(self, sql: str) -> str:
        """Normalize SQL for validation.

        Args:
            sql: Raw SQL

        Returns:
            Normalized SQL
        """
        # Remove extra whitespace
        sql = re.sub(r"\s+", " ", sql)
        # Trim
        sql = sql.strip()
        return sql

    def _check_dangerous_patterns(self, sql: str) -> List[ValidationIssue]:
        """Check for dangerous SQL patterns.

        Args:
            sql: SQL to check

        Returns:
            List of validation issues
        """
        issues = []
        sql_upper = sql.upper()

        for pattern, message in self.DANGEROUS_PATTERNS:
            if re.search(pattern, sql_upper, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    code="DANGEROUS_PATTERN",
                    message=message,
                    suggestion="Review this query carefully before execution",
                ))

        return issues

    def _check_injection_patterns(self, sql: str) -> List[ValidationIssue]:
        """Check for SQL injection patterns.

        Args:
            sql: SQL to check

        Returns:
            List of validation issues
        """
        issues = []

        for pattern, message in self.INJECTION_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="POTENTIAL_INJECTION",
                    message=message,
                    suggestion="Use parameterized queries instead",
                ))

        return issues

    def _check_blocked_patterns(self, sql: str) -> List[ValidationIssue]:
        """Check custom blocked patterns.

        Args:
            sql: SQL to check

        Returns:
            List of validation issues
        """
        issues = []
        sql_upper = sql.upper()

        for pattern in self.blocked_patterns:
            if pattern.upper() in sql_upper:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="BLOCKED_PATTERN",
                    message=f"Pattern '{pattern}' is blocked",
                ))

        return issues

    def _check_syntax(self, sql: str) -> List[ValidationIssue]:
        """Check basic SQL syntax.

        Args:
            sql: SQL to check

        Returns:
            List of validation issues
        """
        issues = []

        # Check for balanced parentheses
        open_count = sql.count("(")
        close_count = sql.count(")")
        if open_count != close_count:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="UNBALANCED_PARENTHESES",
                message=f"Unbalanced parentheses: {open_count} open, {close_count} close",
            ))

        # Check for quoted strings
        single_quotes = sql.count("'")
        if single_quotes % 2 != 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="UNCLOSED_QUOTE",
                message="Odd number of single quotes - possible unclosed string",
            ))

        # Check for statement separators in multi-statement queries
        if sql.count(";") > 1:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="MULTIPLE_STATEMENTS",
                message="Multiple statements detected - ensure this is intentional",
            ))

        return issues

    def _check_common_mistakes(self, sql: str) -> List[ValidationIssue]:
        """Check for common SQL mistakes.

        Args:
            sql: SQL to check

        Returns:
            List of validation issues
        """
        issues = []

        # Check for SELECT *
        if re.search(r"SELECT\s+\*\s+FROM", sql, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                code="SELECT_STAR",
                message="SELECT * retrieves all columns",
                suggestion="Specify only the columns you need for better performance",
            ))

        # Check for missing WHERE clause in DELETE
        if re.match(r"DELETE\s+FROM\s+\w+\s*$", sql, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                code="DELETE_WITHOUT_WHERE",
                message="DELETE without WHERE clause will delete all rows",
                suggestion="Add a WHERE clause to limit the scope",
            ))

        # Check for missing WHERE clause in UPDATE
        if re.match(r"UPDATE\s+\w+\s+SET\s+[\w\s,=]+\s*$", sql, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                code="UPDATE_WITHOUT_WHERE",
                message="UPDATE without WHERE clause will update all rows",
                suggestion="Add a WHERE clause to limit the scope",
            ))

        return issues

    def _detect_operation(self, sql: str) -> str | None:
        """Detect the type of SQL operation.

        Args:
            sql: SQL to analyze

        Returns:
            Operation type (SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, TRUNCATE)
        """
        sql_upper = sql.strip().upper()

        for operation, pattern in self.SQL_PATTERNS.items():
            if re.match(pattern, sql_upper, re.IGNORECASE):
                return operation.upper()

        return None

    def _is_operation_allowed(self, operation: str, allow_ddl: bool) -> bool:
        """Check if an operation is allowed.

        Args:
            operation: Operation type
            allow_ddl: Whether DDL is allowed

        Returns:
            True if operation is allowed
        """
        # DDL operations
        ddl_operations = {"CREATE", "ALTER", "DROP", "TRUNCATE"}

        if operation in ddl_operations and not allow_ddl:
            return False

        if operation not in self.allowed_operations:
            return False

        return True

    def explain_query(self, sql: str) -> str:
        """Explain what a SQL query does in natural language.

        Args:
            sql: SQL query to explain

        Returns:
            Natural language explanation
        """
        operation = self._detect_operation(sql)
        if not operation:
            return "Unable to determine the operation type"

        explanations = {
            "SELECT": "This query retrieves data from the database",
            "INSERT": "This query adds new data to the database",
            "UPDATE": "This query modifies existing data in the database",
            "DELETE": "This query removes data from the database",
            "CREATE": "This query creates a new database object (table, index, view, etc.)",
            "ALTER": "This query modifies the structure of a database object",
            "DROP": "This query deletes a database object",
            "TRUNCATE": "This query removes all data from a table quickly",
        }

        return explanations.get(operation, f"This is a {operation} operation")

    def suggest_optimizations(self, sql: str) -> List[str]:
        """Suggest optimizations for a SQL query.

        Args:
            sql: SQL query to analyze

        Returns:
            List of optimization suggestions
        """
        suggestions = []
        sql_upper = sql.upper()

        # Suggest specific columns instead of *
        if "SELECT *" in sql_upper or "SELECT\t*" in sql_upper:
            suggestions.append("Consider specifying only the columns you need instead of SELECT *")

        # Check for JOIN without ON
        if re.search(r"JOIN\s+\w+\s+(?!ON)", sql_upper):
            suggestions.append("JOIN without ON clause - this may result in a Cartesian product")

        # Check for ORDER BY without LIMIT
        if "ORDER BY" in sql_upper and "LIMIT" not in sql_upper:
            suggestions.append("Consider adding LIMIT to ORDER BY queries for large result sets")

        # Check for subqueries
        if re.search(r"\([^)]*SELECT[^)]*\)", sql_upper):
            suggestions.append("Subquery detected - consider using JOIN for better performance")

        # Check for LIKE with leading wildcard
        if re.search(r"LIKE\s+'[%_]", sql_upper):
            suggestions.append("LIKE with leading wildcard prevents index usage")

        # Check for functions in WHERE clause
        if re.search(r"WHERE\s+.*\([^)]*\)\s*[=<>]", sql_upper):
            suggestions.append("Function in WHERE clause may prevent index usage")

        return suggestions
