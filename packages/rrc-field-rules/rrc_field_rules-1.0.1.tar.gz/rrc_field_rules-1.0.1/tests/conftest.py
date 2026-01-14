"""Pytest fixtures for RRC Field Rules tests."""

from datetime import datetime
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
    """Sample og_field data for testing.
    
    Note: Oracle returns datetime objects for DATE columns, even when
    there's a time component. This fixture includes datetime values
    to ensure our models properly handle this.
    """
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
            "modified_dt": datetime(2025, 12, 19, 1, 26, 51),  # Oracle datetime
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
            "modified_dt": None,  # Also test None case
        },
    ]


@pytest.fixture
def sample_field_info_data() -> list[dict[str, Any]]:
    """Sample og_field_info data for testing.
    
    Oracle returns datetime objects for DATE columns. This fixture
    includes datetime values with non-zero time components to ensure
    our models properly handle this.
    """
    return [
        {
            "oil_or_gas_code": "O",
            "field_info_id": 1001,
            "field_id": 1,
            "salt_dome_flag": "N",
            "derived_rule_type_code": "SW",
            "rescind_dt": None,
            "offshore_code": "L",
            "dont_permit_flag": "N",
            "schedule_remarks": None,
            "comments": "Test field info record",
            "noa_manual_rev_rule": None,
            "discovery_dt": datetime(1990, 5, 15, 0, 0, 0),
            "county_code": "001",
            "modified_by": "SYSTEM",
            "modified_dt": datetime(2025, 11, 20, 14, 30, 45),  # Oracle datetime with time
        },
        {
            "oil_or_gas_code": "G",
            "field_info_id": 1002,
            "field_id": 2,
            "salt_dome_flag": "Y",
            "derived_rule_type_code": "SP",
            "rescind_dt": datetime(2020, 1, 15, 9, 0, 0),  # Rescind with time component
            "offshore_code": "B",
            "dont_permit_flag": "N",
            "schedule_remarks": "Y",
            "comments": None,
            "noa_manual_rev_rule": "Special horizontal drilling rules apply",
            "discovery_dt": datetime(1985, 8, 22, 12, 0, 0),
            "county_code": "003",
            "modified_by": "ANALYST2",
            "modified_dt": datetime(2025, 12, 1, 8, 15, 30),
        },
    ]


@pytest.fixture
def sample_field_rule_data() -> list[dict[str, Any]]:
    """Sample og_field_rule data for testing.
    
    Oracle returns datetime objects for DATE columns. This fixture
    includes datetime values with non-zero time components to ensure
    our models properly handle this.
    """
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
            "effective_dt": datetime(2024, 1, 1, 0, 0, 0),
            "modified_by": "RULEADMIN",
            "modified_dt": datetime(2025, 6, 15, 16, 45, 22),  # Oracle datetime with time
        },
        {
            "oil_or_gas_code": "G",
            "field_id": 2,
            "field_rule_id": 102,
            "rule_type_code": "O",
            "minimum_lease_distance": 330,
            "minimum_well_distance": 660,
            "minimum_acres_per_unit": 20.00,
            "tolerance_acres": 2.50,
            "diagonal_type_code": "WC",
            "maximum_diagonal_length": 1500.0,
            "effective_dt": datetime(2023, 7, 1, 8, 30, 0),
            "modified_by": None,
            "modified_dt": None,  # Also test None case
        },
    ]
