"""
Access control for XuguDB MCP Server.

Role-based access control for SQL operations and table access.
"""
import re
from typing import Set, List, Dict
from dataclasses import dataclass
from enum import Enum

from ..config.settings import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class Permission(Enum):
    """Permission types."""

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
    ADMIN = "ADMIN"


@dataclass
class TableAccess:
    """Table access rules."""

    table_pattern: str  # Supports wildcards like "users_*"
    permissions: Set[Permission]
    # Optional column-level restrictions
    allowed_columns: Set[str] | None = None
    denied_columns: Set[str] | None = None
    # WHERE clause restrictions (e.g., "department_id = 5")
    where_filter: str | None = None


@dataclass
class Role:
    """Role definition with permissions."""

    name: str
    permissions: Set[Permission]
    table_access: List[TableAccess]
    description: str | None = None


# Predefined roles
class Roles:
    """Predefined role definitions."""

    @staticmethod
    def read_only() -> Role:
        """Read-only role - can only SELECT."""
        return Role(
            name="read_only",
            permissions={Permission.SELECT},
            table_access=[
                TableAccess(
                    table_pattern="*",
                    permissions={Permission.SELECT},
                ),
            ],
            description="Read-only access to all tables",
        )

    @staticmethod
    def data_analyst() -> Role:
        """Data analyst role - can SELECT and use Chat2SQL."""
        return Role(
            name="data_analyst",
            permissions={Permission.SELECT, Permission.CHAT2SQL, Permission.EXECUTE},
            table_access=[
                TableAccess(
                    table_pattern="*",
                    permissions={Permission.SELECT},
                ),
            ],
            description="Data analyst with read access and Chat2SQL",
        )

    @staticmethod
    def data_editor() -> Role:
        """Data editor role - can SELECT, INSERT, UPDATE, DELETE."""
        return Role(
            name="data_editor",
            permissions={
                Permission.SELECT,
                Permission.INSERT,
                Permission.UPDATE,
                Permission.DELETE,
            },
            table_access=[
                TableAccess(
                    table_pattern="*",
                    permissions={
                        Permission.SELECT,
                        Permission.INSERT,
                        Permission.UPDATE,
                        Permission.DELETE,
                    },
                ),
            ],
            description="Data editor with full DML access",
        )

    @staticmethod
    def developer() -> Role:
        """Developer role - full DML + limited DDL."""
        return Role(
            name="developer",
            permissions={
                Permission.SELECT,
                Permission.INSERT,
                Permission.UPDATE,
                Permission.DELETE,
                Permission.CREATE,
                Permission.ALTER,
                Permission.TRUNCATE,
                Permission.CHAT2SQL,
            },
            table_access=[
                TableAccess(
                    table_pattern="dev_*",
                    permissions={
                        Permission.SELECT,
                        Permission.INSERT,
                        Permission.UPDATE,
                        Permission.DELETE,
                        Permission.CREATE,
                        Permission.ALTER,
                        Permission.DROP,
                        Permission.TRUNCATE,
                    },
                ),
                TableAccess(
                    table_pattern="*",
                    permissions={
                        Permission.SELECT,
                        Permission.INSERT,
                        Permission.UPDATE,
                    },
                ),
            ],
            description="Developer with DDL access to dev tables",
        )

    @staticmethod
    def admin() -> Role:
        """Admin role - full access."""
        return Role(
            name="admin",
            permissions={p for p in Permission},
            table_access=[
                TableAccess(
                    table_pattern="*",
                    permissions={p for p in Permission},
                ),
            ],
            description="Full administrative access",
        )


class AccessController:
    """Access control for SQL operations."""

    def __init__(self):
        """Initialize access controller."""
        self.settings = get_settings()
        self._roles: Dict[str, Role] = {}

        # Register predefined roles
        for role in [Roles.read_only(), Roles.data_analyst(), Roles.data_editor(), Roles.developer(), Roles.admin()]:
            self._roles[role.name] = role

        # Default role (if no role assigned)
        self._default_role = Roles.data_analyst()

    def add_role(self, role: Role):
        """Add a custom role.

        Args:
            role: Role to add
        """
        self._roles[role.name] = role

    def get_role(self, role_name: str) -> Role | None:
        """Get a role by name.

        Args:
            role_name: Name of the role

        Returns:
            Role or None if not found
        """
        return self._roles.get(role_name)

    def list_roles(self) -> List[str]:
        """List all available roles.

        Returns:
            List of role names
        """
        return list(self._roles.keys())

    def check_permission(
        self,
        role_name: str | None,
        operation: str,
        table_name: str | None = None,
    ) -> bool:
        """Check if a role has permission for an operation.

        Args:
            role_name: Name of the role (None for default)
            operation: SQL operation (SELECT, INSERT, etc.)
            table_name: Optional table name

        Returns:
            True if permission granted
        """
        # Get role
        role = self._get_role(role_name)

        # Check if operation is allowed globally
        if operation not in self.settings.security.allowed_operations:
            logger.warning(f"Operation '{operation}' not in allowed operations")
            return False

        # Check role permissions
        try:
            permission = Permission[operation.upper()]
        except KeyError:
            # Unknown operation - deny
            return False

        if permission not in role.permissions:
            return False

        # Check table-level access if table specified
        if table_name:
            return self._check_table_access(role, table_name, permission)

        return True

    def check_sql(
        self,
        role_name: str | None,
        sql: str,
    ) -> tuple[bool, str | None]:
        """Check if SQL is allowed for a role.

        Args:
            role_name: Name of the role
            sql: SQL query to check

        Returns:
            Tuple of (allowed, reason)
        """
        # Get role
        role = self._get_role(role_name)

        # Detect operation type
        operation = self._detect_operation(sql)
        if not operation:
            return True, None  # Unknown operation - allow

        # Check permission
        if not self.check_permission(role_name, operation):
            return False, f"Role '{role.name}' does not have '{operation}' permission"

        # Check table access
        table_name = self._extract_table_name(sql)
        if table_name:
            table_access = self._get_table_access(role, table_name)
            if not table_access:
                return False, f"Role '{role.name}' does not have access to table '{table_name}'"

            # Check if operation is allowed on this table
            try:
                permission = Permission[operation]
            except KeyError:
                return True, None

            if permission not in table_access.permissions:
                return False, f"Role '{role.name}' cannot {operation} on table '{table_name}'"

        return True, None

    def filter_sql(
        self,
        role_name: str | None,
        sql: str,
    ) -> str:
        """Apply access control filters to SQL.

        Args:
            role_name: Name of the role
            sql: SQL query to filter

        Returns:
            Filtered SQL query
        """
        role = self._get_role(role_name)

        # For SELECT queries, add WHERE filters if needed
        if sql.strip().upper().startswith("SELECT"):
            table_name = self._extract_table_name(sql)
            if table_name:
                table_access = self._get_table_access(role, table_name)
                if table_access and table_access.where_filter:
                    # Add WHERE clause if not present
                    sql_upper = sql.upper()
                    if " WHERE " not in sql_upper:
                        # Insert WHERE before ORDER BY, GROUP BY, LIMIT, etc.
                        for keyword in ["ORDER BY", "GROUP BY", "LIMIT", "HAVING"]:
                            if f" {keyword} " in sql_upper:
                                idx = sql_upper.find(f" {keyword} ")
                                return sql[:idx] + f" WHERE {table_access.where_filter} " + sql[idx:]
                        # Append at end
                        return f"{sql} WHERE {table_access.where_filter}"

        return sql

    def _get_role(self, role_name: str | None) -> Role:
        """Get role, falling back to default.

        Args:
            role_name: Name of the role

        Returns:
            Role instance
        """
        if role_name and role_name in self._roles:
            return self._roles[role_name]
        return self._default_role

    def _check_table_access(
        self,
        role: Role,
        table_name: str,
        permission: Permission,
    ) -> bool:
        """Check if role has access to table.

        Args:
            role: Role to check
            table_name: Table name
            permission: Permission required

        Returns:
            True if access granted
        """
        table_access = self._get_table_access(role, table_name)
        if not table_access:
            return False

        return permission in table_access.permissions

    def _get_table_access(
        self,
        role: Role,
        table_name: str,
    ) -> TableAccess | None:
        """Get table access rule for a table.

        Args:
            role: Role to check
            table_name: Table name

        Returns:
            TableAccess or None
        """
        # Check exact match first
        for access in role.table_access:
            if access.table_pattern == table_name:
                return access

        # Check wildcard patterns
        for access in role.table_access:
            if self._match_pattern(access.table_pattern, table_name):
                return access

        return None

    def _match_pattern(self, pattern: str, table_name: str) -> bool:
        """Match table name against pattern.

        Args:
            pattern: Pattern with wildcards
            table_name: Table name to match

        Returns:
            True if pattern matches
        """
        # Convert wildcard pattern to regex
        regex = pattern.replace("*", ".*").replace("?", ".")
        regex = f"^{regex}$"
        return re.match(regex, table_name, re.IGNORECASE) is not None

    def _detect_operation(self, sql: str) -> str | None:
        """Detect SQL operation type.

        Args:
            sql: SQL query

        Returns:
            Operation type or None
        """
        sql_upper = sql.strip().upper()

        for op in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "TRUNCATE"]:
            if sql_upper.startswith(op):
                return op

        return None

    def _extract_table_name(self, sql: str) -> str | None:
        """Extract table name from SQL.

        Args:
            sql: SQL query

        Returns:
            Table name or None
        """
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


# Global access controller instance
_access_controller: AccessController | None = None


def get_access_controller() -> AccessController:
    """Get global access controller instance.

    Returns:
        AccessController instance
    """
    global _access_controller
    if _access_controller is None:
        _access_controller = AccessController()
    return _access_controller


def reset_access_controller():
    """Reset global access controller (useful for testing)."""
    global _access_controller
    _access_controller = None
