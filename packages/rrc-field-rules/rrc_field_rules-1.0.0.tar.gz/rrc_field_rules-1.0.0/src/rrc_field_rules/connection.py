"""Oracle database connection management."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import oracledb

from rrc_field_rules.config import ParserConfig
from rrc_field_rules.exceptions import ConnectionError, HealthCheckError


class OracleConnection:
    """Manages Oracle database connections.

    Provides connection pooling, health checks, and context manager support
    for safe connection handling.

    Example:
        config = ParserConfig(password="secret")
        conn_manager = OracleConnection(config)

        # Check health
        if conn_manager.check_health():
            print("Database is healthy")

        # Use connection
        with conn_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM og_field")
    """

    def __init__(self, config: ParserConfig) -> None:
        """Initialize connection manager.

        Args:
            config: Parser configuration with database credentials.
        """
        self._config = config
        self._pool: oracledb.ConnectionPool | None = None

    def _create_pool(self) -> oracledb.ConnectionPool:
        """Create connection pool lazily."""
        if self._pool is None:
            try:
                self._pool = oracledb.create_pool(
                    user=self._config.user,
                    password=self._config.password.get_secret_value(),
                    dsn=self._config.dsn,
                    min=1,
                    max=5,
                    increment=1,
                )
            except oracledb.Error as e:
                raise ConnectionError(f"Failed to create connection pool: {e}") from e
        return self._pool

    @contextmanager
    def get_connection(self) -> Generator[oracledb.Connection, None, None]:
        """Get a connection from the pool.

        Yields:
            Active Oracle connection.

        Raises:
            ConnectionError: If connection cannot be established.
        """
        pool = self._create_pool()
        conn: oracledb.Connection | None = None
        try:
            conn = pool.acquire()
            yield conn
        except oracledb.Error as e:
            raise ConnectionError(f"Failed to acquire connection: {e}") from e
        finally:
            if conn is not None:
                pool.release(conn)

    def check_health(self) -> bool:
        """Verify database connectivity.

        Returns:
            True if database is accessible and responding.

        Raises:
            HealthCheckError: If health check fails.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM DUAL")
                result = cursor.fetchone()
                cursor.close()
                return result is not None and result[0] == 1
        except ConnectionError as e:
            raise HealthCheckError(f"Health check failed: {e}") from e
        except oracledb.Error as e:
            raise HealthCheckError(f"Health check query failed: {e}") from e

    def execute_query(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a query and return results as list of dicts.

        Args:
            query: SQL query to execute.
            params: Optional query parameters.

        Returns:
            List of dictionaries, one per row.

        Raises:
            ConnectionError: If connection fails.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Get column names from cursor description
            columns = [col[0].lower() for col in cursor.description]

            # Convert rows to dicts
            rows = cursor.fetchall()
            cursor.close()

            return [dict(zip(columns, row, strict=False)) for row in rows]

    def get_table_count(self, table_name: str) -> int:
        """Get row count for a table.

        Args:
            table_name: Name of the table.

        Returns:
            Number of rows in the table.
        """
        query = f"SELECT COUNT(*) FROM {table_name}"  # noqa: S608 - table name validated upstream
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return int(result[0]) if result else 0

    def close(self) -> None:
        """Close the connection pool."""
        if self._pool is not None:
            self._pool.close()
            self._pool = None
