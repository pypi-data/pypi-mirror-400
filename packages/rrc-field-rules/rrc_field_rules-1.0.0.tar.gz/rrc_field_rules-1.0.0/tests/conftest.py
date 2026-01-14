"""Pytest fixtures for RRC Field Rules tests."""

from typing import Any, Generator
from unittest.mock import MagicMock

import pytest

from rrc_field_rules.config import ParserConfig


@pytest.fixture
def mock_config() -> ParserConfig:
    """Create a test configuration."""
    return ParserConfig(
        host="localhost",
        port=1521,
        service="TESTDB",
        user="test_user",
        password="test_password",
    )


@pytest.fixture
def mock_oracle_connection() -> Generator[MagicMock, None, None]:
    """Mock Oracle connection for unit tests."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    yield mock_conn


@pytest.fixture
def sample_field_data() -> list[dict[str, Any]]:
    """Sample og_field data for testing."""
    return [
        {
            "field_number": "00001001",
            "field_name": "TEST FIELD FORMATION 5000",
            "field_id": 1,
            "field_class_code": "O",
            "field_h2s_flag": "N",
            "field_manual_rev_flag": "N",
            "wildcat_flag": "N",
            "district_id": 1,
            "district_code": "01",
            "associated_field_id": None,
            "modified_by": "SYSTEM",
            "modified_dt": None,
        },
        {
            "field_number": "00002001",
            "field_name": "ANOTHER TEST GAS 7500",
            "field_id": 2,
            "field_class_code": "G",
            "field_h2s_flag": "Y",
            "field_manual_rev_flag": "N",
            "wildcat_flag": "N",
            "district_id": 3,
            "district_code": "03",
            "associated_field_id": None,
            "modified_by": "ANALYST1",
            "modified_dt": None,
        },
    ]


@pytest.fixture
def sample_field_rule_data() -> list[dict[str, Any]]:
    """Sample og_field_rule data for testing."""
    return [
        {
            "oil_or_gas_code": "O",
            "field_id": 1,
            "field_rule_id": 101,
            "rule_type_code": "B",
            "minimum_lease_distance": 467,
            "minimum_well_distance": 1200,
            "minimum_acres_per_unit": 40.00,
            "tolerance_acres": 5.00,
            "diagonal_type_code": "CC",
            "maximum_diagonal_length": None,
            "effective_dt": None,
            "modified_by": None,
            "modified_dt": None,
        },
    ]
