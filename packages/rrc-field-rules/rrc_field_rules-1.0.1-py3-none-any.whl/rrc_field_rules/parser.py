"""Main parser class for extracting field rules data."""

import json
from pathlib import Path
from typing import Any

from rrc_field_rules.codes import expand_record
from rrc_field_rules.config import ParserConfig
from rrc_field_rules.connection import OracleConnection
from rrc_field_rules.exceptions import QueryError, TableNotFoundError
from rrc_field_rules.models import (
    AVAILABLE_TABLES,
    OgField,
    OgFieldInfo,
    OgFieldRule,
    OgStdFieldRule,
)


class FieldRulesParser:
    """Parser for Texas RRC field rules data.

    Connects to an Oracle database containing RRC field rules and provides
    methods to extract data as Pydantic models or export to JSON.

    Example:
        from rrc_field_rules import FieldRulesParser, ParserConfig

        config = ParserConfig(password="ParserPassword123")
        parser = FieldRulesParser(config)

        # Check connection
        if parser.check_health():
            # Get all fields
            fields = parser.get_fields()
            print(f"Found {len(fields)} fields")

            # Export to JSON
            parser.export_all_to_json(Path("./output.json"))

        # With human-readable code expansion
        config = ParserConfig(password="secret", expand_codes=True)
        parser = FieldRulesParser(config)
        # Now 'O' becomes 'Oil', 'N' becomes 'No', etc.
    """

    def __init__(self, config: ParserConfig) -> None:
        """Initialize parser with configuration.

        Args:
            config: Parser configuration with database credentials.
        """
        self._config = config
        self._connection = OracleConnection(config)

    @property
    def expand_codes(self) -> bool:
        """Whether to expand coded values to human-readable text."""
        return self._config.expand_codes

    def check_health(self) -> bool:
        """Check database connectivity.

        Returns:
            True if database is accessible.

        Raises:
            HealthCheckError: If health check fails.
        """
        return self._connection.check_health()

    def close(self) -> None:
        """Close database connections."""
        self._connection.close()

    def __enter__(self) -> "FieldRulesParser":
        """Context manager entry."""
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit - close connections."""
        self.close()

    # --- Table-specific getters ---

    def get_fields(self, limit: int | None = None) -> list[OgField]:
        """Get all field records.

        Args:
            limit: Optional maximum number of records.

        Returns:
            List of OgField models.
        """
        return self._get_table_data("og_field", OgField, limit)

    def get_field_info(self, limit: int | None = None) -> list[OgFieldInfo]:
        """Get all field info records.

        Args:
            limit: Optional maximum number of records.

        Returns:
            List of OgFieldInfo models.
        """
        return self._get_table_data("og_field_info", OgFieldInfo, limit)

    def get_field_rules(self, limit: int | None = None) -> list[OgFieldRule]:
        """Get all field rule records.

        Args:
            limit: Optional maximum number of records.

        Returns:
            List of OgFieldRule models.
        """
        return self._get_table_data("og_field_rule", OgFieldRule, limit)

    def get_std_field_rules(self, limit: int | None = None) -> list[OgStdFieldRule]:
        """Get all standard field rule records.

        Args:
            limit: Optional maximum number of records.

        Returns:
            List of OgStdFieldRule models.
        """
        return self._get_table_data("og_std_field_rule", OgStdFieldRule, limit)

    # --- Generic table access ---

    def get_table_data(
        self, table_name: str, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Get data from a specific table as dictionaries.

        Args:
            table_name: Name of the table to query.
            limit: Optional maximum number of records.

        Returns:
            List of dictionaries representing table rows.
            If expand_codes is enabled, coded values are expanded to text.

        Raises:
            TableNotFoundError: If table doesn't exist.
            QueryError: If query fails.
        """
        table_lower = table_name.lower()
        if table_lower not in AVAILABLE_TABLES:
            raise TableNotFoundError(table_name)

        query = f"SELECT * FROM {table_lower}"  # noqa: S608 - validated above
        if limit:
            query += f" WHERE ROWNUM <= {limit}"

        try:
            data = self._connection.execute_query(query)

            # Expand codes if enabled
            if self.expand_codes:
                data = [expand_record(row) for row in data]

            return data
        except Exception as e:
            raise QueryError(f"Failed to query {table_name}: {e}", query) from e

    def get_table_count(self, table_name: str) -> int:
        """Get row count for a table.

        Args:
            table_name: Name of the table.

        Returns:
            Number of rows.

        Raises:
            TableNotFoundError: If table doesn't exist.
        """
        table_lower = table_name.lower()
        if table_lower not in AVAILABLE_TABLES:
            raise TableNotFoundError(table_name)

        return self._connection.get_table_count(table_lower)

    def list_tables(self) -> list[str]:
        """List available tables.

        Returns:
            List of table names.
        """
        return AVAILABLE_TABLES.copy()

    # --- Export methods ---

    def export_table_to_json(
        self,
        table_name: str,
        output_path: Path,
        limit: int | None = None,
        indent: int = 2,
    ) -> int:
        """Export a single table to JSON file.

        Args:
            table_name: Name of the table to export.
            output_path: Path to output JSON file.
            limit: Optional maximum number of records.
            indent: JSON indentation level.

        Returns:
            Number of records exported.
        """
        data = self.get_table_data(table_name, limit)

        # Convert dates to ISO format strings
        serialized = self._serialize_for_json(data)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=indent, ensure_ascii=False)

        return len(data)

    def export_all_to_json(
        self,
        output_path: Path,
        limit_per_table: int | None = None,
        indent: int = 2,
    ) -> dict[str, int]:
        """Export all tables to a single JSON file.

        Args:
            output_path: Path to output JSON file.
            limit_per_table: Optional maximum records per table.
            indent: JSON indentation level.

        Returns:
            Dictionary of table names to record counts.
        """
        result: dict[str, Any] = {}
        counts: dict[str, int] = {}

        for table_name in AVAILABLE_TABLES:
            data = self.get_table_data(table_name, limit_per_table)
            result[table_name] = self._serialize_for_json(data)
            counts[table_name] = len(data)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=indent, ensure_ascii=False)

        return counts

    # --- Private helpers ---

    def _get_table_data(
        self, table_name: str, model_class: type, limit: int | None = None
    ) -> list[Any]:
        """Get table data and convert to Pydantic models.

        Note: When expand_codes is enabled, models may fail validation
        because the expanded strings don't match Literal types.
        Use get_table_data() for expanded data instead.

        Args:
            table_name: Name of the table.
            model_class: Pydantic model class to use.
            limit: Optional maximum records.

        Returns:
            List of Pydantic models.
        """
        # For Pydantic models, we need raw data (not expanded)
        # because Literal types expect exact code values
        table_lower = table_name.lower()
        if table_lower not in AVAILABLE_TABLES:
            raise TableNotFoundError(table_name)

        query = f"SELECT * FROM {table_lower}"  # noqa: S608 - validated above
        if limit:
            query += f" WHERE ROWNUM <= {limit}"

        try:
            data = self._connection.execute_query(query)
            return [model_class.model_validate(row) for row in data]
        except Exception as e:
            raise QueryError(f"Failed to query {table_name}: {e}", query) from e

    def _serialize_for_json(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert data to JSON-serializable format.

        Handles date conversion and other non-serializable types.

        Args:
            data: List of dictionaries to serialize.

        Returns:
            JSON-serializable list.
        """
        from datetime import date, datetime

        result = []
        for row in data:
            serialized_row = {}
            for key, value in row.items():
                if isinstance(value, (date, datetime)):
                    serialized_row[key] = value.isoformat()
                else:
                    serialized_row[key] = value
            result.append(serialized_row)
        return result

