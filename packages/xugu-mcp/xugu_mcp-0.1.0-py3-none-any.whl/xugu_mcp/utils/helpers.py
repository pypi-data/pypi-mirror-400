"""
Helper functions for XuguDB MCP Server.
"""
import re
from typing import Any


def sanitize_table_name(name: str) -> str:
    """Sanitize table name to prevent SQL injection.

    Args:
        name: Table name to sanitize

    Returns:
        Sanitized table name

    Raises:
        ValueError: If table name contains invalid characters
    """
    # Only allow alphanumeric, underscore, and dollar sign
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        raise ValueError(f"Invalid table name: {name}")
    return name


def format_result_row(row: tuple, columns: list[str]) -> dict[str, Any]:
    """Convert result row tuple to dictionary.

    Args:
        row: Result row as tuple
        columns: Column names

    Returns:
        Dictionary mapping column names to values
    """
    return dict(zip(columns, row))


def truncate_string(s: str, max_length: int = 100) -> str:
    """Truncate string to maximum length.

    Args:
        s: String to truncate
        max_length: Maximum length

    Returns:
        Truncated string with ellipsis if needed
    """
    if len(s) <= max_length:
        return s
    return s[: max_length - 3] + "..."


def safe_repr(obj: Any, max_length: int = 200) -> str:
    """Get safe string representation of object.

    Args:
        obj: Object to represent
        max_length: Maximum length of representation

    Returns:
        String representation
    """
    try:
        s = repr(obj)
    except Exception:
        s = "<repr failed>"
    return truncate_string(s, max_length)


def extract_sql_type(python_type: type) -> str:
    """Map Python type to SQL type name.

    Args:
        python_type: Python type

    Returns:
        SQL type name
    """
    type_mapping = {
        int: "INTEGER",
        float: "DOUBLE",
        str: "VARCHAR",
        bool: "BOOLEAN",
        bytes: "BLOB",
    }
    return type_mapping.get(python_type, "VARCHAR")


def parse_connection_string(conn_str: str) -> dict[str, str]:
    """Parse connection string into parameters.

    Args:
        conn_str: Connection string in format "key1=value1;key2=value2"

    Returns:
        Dictionary of connection parameters
    """
    params = {}
    for pair in conn_str.split(";"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[key.strip()] = value.strip()
    return params
