"""
XuguDB connection manager with pooling and transaction support.
"""
import time
from typing import Optional, Generator
from contextlib import contextmanager

import xgcondb

from ..config.settings import get_settings
from ..utils.errors import ConnectionError, QueryExecutionError
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Type alias for xgcondb.Connection (not directly available as module attribute)
# Use string literal "xgcondb.Connection" for type annotations to avoid
# runtime import issues and type checker errors.


class XuguConnectionManager:
    """Manage XuguDB database connections with transaction support."""

    def __init__(self):
        self._connection: "xgcondb.Connection" | None = None
        self._cursor: "xgcondb.Cursor" | None = None
        self._in_transaction = False
        self._settings = get_settings()

    @property
    def _conn(self) -> "xgcondb.Connection":
        """Get the connection, raising an error if not connected."""
        if self._connection is None:
            raise ConnectionError("Not connected to database")
        return self._connection

    def connect(self) -> "xgcondb.Connection":
        """Establish database connection.

        Returns:
            Connection object

        Raises:
            ConnectionError: If connection fails
        """
        if self._connection is not None:
            logger.debug("Using existing connection")
            return self._connection

        config = self._settings.xugu
        logger.info(
            f"Connecting to XuguDB: {config.host}:{config.port}/{config.database}"
        )

        try:
            self._connection = xgcondb.connect(
                host=config.host,
                port=config.port,
                database=config.database,
                user=config.user,
                password=config.password,
                charset=config.charset,
                usessl=config.usessl,
            )
            logger.info("Successfully connected to XuguDB")
            return self._connection

        except Exception as e:
            logger.error(f"Failed to connect to XuguDB: {e}")
            raise ConnectionError(f"Database connection failed: {e}") from e

    def disconnect(self):
        """Close database connection."""
        if self._cursor is not None:
            try:
                self._cursor.close()
                logger.debug("Cursor closed")
            except Exception as e:
                logger.warning(f"Error closing cursor: {e}")
            self._cursor = None

        if self._connection is not None:
            try:
                self._connection.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
            self._connection = None

        self._in_transaction = False

    @contextmanager
    def get_cursor(self) -> Generator["xgcondb.Cursor", None, None]:
        """Get database cursor with automatic cleanup.

        Yields:
            Database cursor

        Example:
            >>> with conn_manager.get_cursor() as cur:
            ...     cur.execute("SELECT * FROM users")
            ...     results = cur.fetchall()
        """
        if self._connection is None:
            self.connect()

        cursor = self._conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        """Execute operations within a transaction.

        Yields:
            None

        Raises:
            ConnectionError: If transaction fails

        Example:
            >>> with conn_manager.transaction():
            ...     cur.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
            ...     cur.execute("UPDATE stats SET count = count + 1")
        """
        if self._connection is None:
            self.connect()

        if self._in_transaction:
            # Already in transaction, just yield
            yield
            return

        self._in_transaction = True
        try:
            self._conn.begin()
            logger.debug("Transaction started")
            yield
            self._conn.commit()
            logger.debug("Transaction committed")
        except Exception as e:
            try:
                self._conn.rollback()
                logger.debug("Transaction rolled back")
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {rollback_error}")
            raise QueryExecutionError(f"Transaction failed: {e}") from e
        finally:
            self._in_transaction = False

    def execute(
        self,
        sql: str,
        params: Optional[tuple | list | dict] = None,
        auto_commit: bool = False,
    ) -> "xgcondb.Cursor":
        """Execute a SQL statement.

        Args:
            sql: SQL statement to execute
            params: Optional parameters for parameterized query
            auto_commit: Whether to commit after execution

        Returns:
            Cursor object (注意：游标需要在使用后手动关闭)

        Raises:
            QueryExecutionError: If execution fails
        """
        if self._connection is None:
            self.connect()

        start_time = time.time()
        logger.debug(f"Executing SQL: {sql[:100]}...")

        try:
            # 创建游标但不使用 context manager，让调用者负责关闭
            cursor = self._conn.cursor()

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            if auto_commit and not self._in_transaction:
                self._conn.commit()

            elapsed = time.time() - start_time
            logger.debug(f"Query executed in {elapsed:.3f}s")

            return cursor

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise QueryExecutionError(
                f"Query execution failed: {e}", sql=sql, details={"params": params}
            ) from e

    def execute_many(
        self,
        sql: str,
        params_list: list[tuple] | list[dict],
        auto_commit: bool = False,
    ) -> "xgcondb.Cursor":
        """Execute a SQL statement multiple times with different parameters.

        Args:
            sql: SQL statement to execute
            params_list: List of parameter tuples/dicts
            auto_commit: Whether to commit after execution

        Returns:
            Cursor object

        Raises:
            QueryExecutionError: If execution fails
        """
        if self._connection is None:
            self.connect()

        start_time = time.time()
        logger.debug(f"Executing batch SQL ({len(params_list)} rows): {sql[:100]}...")

        try:
            with self.get_cursor() as cursor:
                cursor.executemany(sql, params_list)

                if auto_commit and not self._in_transaction:
                    self._conn.commit()

                elapsed = time.time() - start_time
                logger.debug(f"Batch query executed in {elapsed:.3f}s")

                return cursor

        except Exception as e:
            logger.error(f"Batch query execution failed: {e}")
            raise QueryExecutionError(
                f"Batch query execution failed: {e}",
                sql=sql,
                details={"row_count": len(params_list)},
            ) from e

    def fetch_all(
        self,
        sql: str,
        params: Optional[tuple | list | dict] = None,
        max_rows: Optional[int] = None,
    ) -> list[tuple]:
        """Execute query and fetch all results.

        Args:
            sql: SELECT query
            params: Optional parameters
            max_rows: Maximum rows to return

        Returns:
            List of result rows

        Raises:
            QueryExecutionError: If query fails
        """
        cursor = self.execute(sql, params)
        results = cursor.fetchall()

        if max_rows and len(results) > max_rows:
            logger.warning(f"Result set truncated to {max_rows} rows")
            results = results[:max_rows]

        return results

    def fetch_one(
        self,
        sql: str,
        params: Optional[tuple | list | dict] = None,
    ) -> Optional[tuple]:
        """Execute query and fetch one result.

        Args:
            sql: SELECT query
            params: Optional parameters

        Returns:
            One result row or None

        Raises:
            QueryExecutionError: If query fails
        """
        cursor = self.execute(sql, params)
        return cursor.fetchone()

    @property
    def is_connected(self) -> bool:
        """Check if connection is active.

        Returns:
            True if connected, False otherwise
        """
        if self._connection is None:
            return False

        try:
            return self._conn.ping(reconnect=False)
        except Exception:
            return False

    def ping(self, reconnect: bool = True) -> bool:
        """Check connection health and optionally reconnect.

        Args:
            reconnect: Whether to automatically reconnect

        Returns:
            True if connection is alive (or reconnected), False otherwise
        """
        if self._connection is None:
            if reconnect:
                self.connect()
                return True
            return False

        try:
            alive = self._conn.ping(reconnect=reconnect)
            if not alive and reconnect:
                logger.warning("Connection lost, attempting to reconnect...")
                self._connection = None
                self.connect()
                return True
            return alive
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            if reconnect:
                self._connection = None
                try:
                    self.connect()
                    return True
                except Exception:
                    pass
            return False

    def select_db(self, database: str):
        """Switch to a different database.

        Args:
            database: Database name

        Raises:
            ConnectionError: If operation fails
        """
        if self._connection is None:
            self.connect()

        try:
            self._conn.select_db(database)
            logger.info(f"Switched to database: {database}")
        except Exception as e:
            logger.error(f"Failed to switch database: {e}")
            raise ConnectionError(f"Failed to switch database: {e}") from e


# Global connection manager instance
_connection_manager: Optional[XuguConnectionManager] = None


def get_connection_manager() -> XuguConnectionManager:
    """Get global connection manager instance (singleton).

    Returns:
        Connection manager instance
    """
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = XuguConnectionManager()
    return _connection_manager


def close_connection():
    """Close the global connection."""
    global _connection_manager
    if _connection_manager is not None:
        _connection_manager.disconnect()
        _connection_manager = None
