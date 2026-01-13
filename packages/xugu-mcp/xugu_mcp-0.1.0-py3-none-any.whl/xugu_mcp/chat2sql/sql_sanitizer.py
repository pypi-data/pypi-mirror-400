"""
SQL Sanitizer for Chat2SQL engine.

Sanitizes SQL queries to prevent SQL injection and ensure safety.
"""
import re
from typing import List, Tuple

from ..utils.logging import get_logger

logger = get_logger(__name__)


class SQLSanitizer:
    """Sanitizer for SQL queries."""

    # Characters that need special handling
    SPECIAL_CHARS = ["'", ";", "--", "#", "/*", "*/"]

    # SQL comments patterns
    COMMENT_PATTERNS = [
        (r"--.*$", "", re.MULTILINE),  # Single-line comments
        (r"/\*.*?\*/", "", re.DOTALL),  # Multi-line comments
        (r"#.*$", "", re.MULTILINE),  # MySQL-style comments
    ]

    def __init__(self):
        """Initialize SQL sanitizer."""
        pass

    def sanitize(self, sql: str, remove_comments: bool = True) -> str:
        """Sanitize SQL query.

        Args:
            sql: SQL query to sanitize
            remove_comments: Whether to remove SQL comments

        Returns:
            Sanitized SQL query
        """
        sanitized = sql

        # Remove comments if requested
        if remove_comments:
            sanitized = self._remove_comments(sanitized)

        # Normalize whitespace
        sanitized = self._normalize_whitespace(sanitized)

        # Remove trailing semicolon (will be added by executor if needed)
        sanitized = sanitized.rstrip(";").strip()

        return sanitized

    def _remove_comments(self, sql: str) -> str:
        """Remove SQL comments from query.

        Args:
            sql: SQL query

        Returns:
            SQL without comments
        """
        result = sql
        for pattern, replacement, flags in self.COMMENT_PATTERNS:
            result = re.sub(pattern, replacement, result, flags=flags)
        return result

    def _normalize_whitespace(self, sql: str) -> str:
        """Normalize whitespace in SQL query.

        Args:
            sql: SQL query

        Returns:
            SQL with normalized whitespace
        """
        # Replace multiple spaces with single space
        sql = re.sub(r" +", " ", sql)
        # Replace multiple tabs with single space
        sql = re.sub(r"\t+", " ", sql)
        # Replace multiple newlines with single space
        sql = re.sub(r"\n+", " ", sql)
        # Remove spaces around parentheses
        sql = re.sub(r"\s*\(\s*", "(", sql)
        sql = re.sub(r"\s*\)\s*", ")", sql)
        # Remove spaces around commas
        sql = re.sub(r"\s*,\s*", ", ", sql)
        return sql.strip()

    def escape_string(self, value: str) -> str:
        """Escape a string value for SQL.

        Args:
            value: String value to escape

        Returns:
            Escaped string
        """
        # Escape single quotes by doubling them
        return value.replace("'", "''")

    def escape_identifier(self, identifier: str) -> str:
        """Escape a SQL identifier (table name, column name).

        Args:
            identifier: Identifier to escape

        Returns:
            Escaped identifier
        """
        # Remove any existing quotes
        identifier = identifier.strip('"').strip("`").strip("[]")
        # Quote with double quotes (SQL standard)
        return f'"{identifier}"'

    def extract_parameters(self, sql: str) -> List[str]:
        """Extract potential parameter values from SQL.

        Args:
            sql: SQL query

        Returns:
            List of string literals found in SQL
        """
        # Match single-quoted strings
        pattern = r"'([^']*)'"
        matches = re.findall(pattern, sql)
        return matches

    def anonymize_parameters(self, sql: str) -> Tuple[str, List[str]]:
        """Anonymize parameters in SQL for logging/validation.

        Args:
            sql: SQL query

        Returns:
            Tuple of (anonymized SQL, list of original values)
        """
        values = []
        counter = 0

        def replace_match(match):
            nonlocal counter
            value = match.group(1)
            values.append(value)
            placeholder = f"?param{counter}?"
            counter += 1
            return f"'{placeholder}'"

        anonymized = re.sub(r"'([^']*)'", replace_match, sql)
        return anonymized, values

    def validate_string_literal(self, literal: str) -> bool:
        """Validate a string literal.

        Args:
            literal: String literal to validate

        Returns:
            True if literal is safe
        """
        # Check for unescaped quotes
        if literal.count("'") % 2 != 0:
            return False

        # Check for suspicious patterns
        suspicious = ["'", ";", "--", "/*", "xp_", "sp_"]
        for pattern in suspicious:
            if pattern in literal:
                return False

        return True

    def check_for_multiple_statements(self, sql: str) -> List[str]:
        """Check for multiple statements in SQL.

        Args:
            sql: SQL query

        Returns:
            List of statements found
        """
        # Split on semicolons (outside of quotes)
        statements = []
        current = ""
        in_quote = False

        for char in sql:
            if char == "'" and (not current or current[-1] != "\\"):
                in_quote = not in_quote
            elif char == ";" and not in_quote:
                if current.strip():
                    statements.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            statements.append(current.strip())

        return statements

    def limit_result_set(
        self,
        sql: str,
        default_limit: int = 1000,
        max_limit: int = 10000,
    ) -> Tuple[str, int]:
        """Add LIMIT clause to SELECT queries if not present.

        Args:
            sql: SQL query
            default_limit: Default limit to add
            max_limit: Maximum allowed limit

        Returns:
            Tuple of (modified SQL, limit applied)
        """
        sql_upper = sql.upper()

        # Check if it's a SELECT query
        if not sql_upper.strip().startswith("SELECT"):
            return sql, 0

        # Check if LIMIT already exists
        if re.search(r"\bLIMIT\s+(\d+)", sql_upper, re.IGNORECASE):
            return sql, 0

        # Check if it has FOR UPDATE or similar clauses
        if any(clause in sql_upper for clause in ["FOR UPDATE", "FOR SHARE", "LOCK IN"]):
            return sql, 0

        # Add LIMIT clause
        # Find the end of the query (before ORDER BY, FOR, etc.)
        limit_clause = f" LIMIT {default_limit}"

        # Insert before ORDER BY if present
        order_by_match = re.search(r"\bORDER\s+BY\s+", sql_upper, re.IGNORECASE)
        if order_by_match:
            pos = order_by_match.start()
            return sql[:pos] + limit_clause + " " + sql[pos:], default_limit

        # Append at the end
        return sql + limit_clause, default_limit

    def add_timeout_hint(self, sql: str, timeout_seconds: int = 30) -> str:
        """Add query timeout hint to SQL.

        Note: This is database-specific and may not work for all databases.

        Args:
            sql: SQL query
            timeout_seconds: Timeout in seconds

        Returns:
            SQL with timeout hint
        """
        # This is a placeholder - actual implementation depends on database
        # For example, MySQL uses: SET max_statement_time = N;
        # PostgreSQL uses: SET statement_timeout TO 'Ns';
        return sql

    def get_safe_sql(self, sql: str) -> str:
        """Get a safe version of SQL for logging.

        Args:
            sql: SQL query

        Returns:
            Safe SQL with parameters anonymized
        """
        # Remove comments
        safe = self._remove_comments(sql)
        # Anonymize parameters
        safe, _ = self.anonymize_parameters(safe)
        # Normalize whitespace
        safe = self._normalize_whitespace(safe)
        # Limit length
        if len(safe) > 1000:
            safe = safe[:1000] + "... [truncated]"
        return safe

    def reconstruct_with_params(
        self,
        sql: str,
        params: Tuple | List,
    ) -> str:
        """Reconstruct SQL with parameters for display.

        Args:
            sql: SQL query with ? placeholders
            params: Parameter values

        Returns:
            SQL with parameters substituted
        """
        result = sql
        for i, param in enumerate(params):
            placeholder = "?"
            # Replace first occurrence
            if param is None:
                value = "NULL"
            elif isinstance(param, str):
                value = f"'{self.escape_string(param)}'"
            elif isinstance(param, (int, float)):
                value = str(param)
            else:
                value = f"'{str(param)}'"

            result = result.replace(placeholder, value, 1)

        return result
