"""Custom exceptions for the RRC Field Rules Parser."""


class RRCParserError(Exception):
    """Base exception for all RRC Parser errors."""

    pass


class ConnectionError(RRCParserError):
    """Raised when database connection fails."""

    def __init__(self, message: str = "Failed to connect to Oracle database") -> None:
        self.message = message
        super().__init__(self.message)


class HealthCheckError(RRCParserError):
    """Raised when health check fails."""

    def __init__(self, message: str = "Database health check failed") -> None:
        self.message = message
        super().__init__(self.message)


class QueryError(RRCParserError):
    """Raised when a database query fails."""

    def __init__(
        self, message: str = "Query execution failed", query: str | None = None
    ) -> None:
        self.message = message
        self.query = query
        super().__init__(self.message)


class TableNotFoundError(RRCParserError):
    """Raised when a requested table does not exist."""

    def __init__(self, table_name: str) -> None:
        self.table_name = table_name
        self.message = f"Table '{table_name}' not found in database"
        super().__init__(self.message)
