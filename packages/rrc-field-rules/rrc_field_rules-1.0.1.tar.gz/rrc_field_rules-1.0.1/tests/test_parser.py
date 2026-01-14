"""Tests for parser module."""

from datetime import datetime
from typing import Any

import pytest

from rrc_field_rules.models import OgField, OgFieldInfo, OgFieldRule


class TestOgFieldModel:
    """Tests for OgField Pydantic model."""

    def test_valid_field_creation(self, sample_field_data: list[dict[str, Any]]) -> None:
        """Test creating OgField from valid data."""
        field = OgField.model_validate(sample_field_data[0])

        assert field.field_number == "00001001"
        assert field.field_name == "TEST FIELD FORMATION 5000"
        assert field.field_id == 1
        assert field.field_class_code == "O"
        assert field.field_h2s_flag == "N"

    def test_field_class_code_validation(self) -> None:
        """Test field_class_code accepts valid values."""
        for code in ["G", "O", "B", "g", "o", "b"]:
            data = {
                "field_number": "00001001",
                "field_name": "TEST",
                "field_id": 1,
                "field_class_code": code,
                "field_h2s_flag": "N",
                "field_manual_rev_flag": "N",
                "wildcat_flag": "N",
                "district_id": 1,
            }
            field = OgField.model_validate(data)
            assert field.field_class_code == code

    def test_datetime_field_with_time_component(
        self, sample_field_data: list[dict[str, Any]]
    ) -> None:
        """Test that datetime fields accept Oracle datetime with time components.
        
        Oracle returns datetime objects for DATE columns, even when there's a
        non-zero time component. This test ensures our models handle this correctly.
        """
        field = OgField.model_validate(sample_field_data[0])
        
        # Verify datetime is preserved with time component
        assert field.modified_dt is not None
        assert isinstance(field.modified_dt, datetime)
        assert field.modified_dt == datetime(2025, 12, 19, 1, 26, 51)
        assert field.modified_dt.hour == 1
        assert field.modified_dt.minute == 26
        assert field.modified_dt.second == 51

    def test_datetime_field_accepts_none(
        self, sample_field_data: list[dict[str, Any]]
    ) -> None:
        """Test that datetime fields accept None values."""
        field = OgField.model_validate(sample_field_data[1])
        assert field.modified_dt is None


class TestOgFieldInfoModel:
    """Tests for OgFieldInfo Pydantic model."""

    def test_valid_field_info_creation(
        self, sample_field_info_data: list[dict[str, Any]]
    ) -> None:
        """Test creating OgFieldInfo from valid data."""
        info = OgFieldInfo.model_validate(sample_field_info_data[0])

        assert info.oil_or_gas_code == "O"
        assert info.field_info_id == 1001
        assert info.field_id == 1
        assert info.salt_dome_flag == "N"
        assert info.derived_rule_type_code == "SW"
        assert info.offshore_code == "L"

    def test_datetime_fields_with_time_components(
        self, sample_field_info_data: list[dict[str, Any]]
    ) -> None:
        """Test that all datetime fields accept Oracle datetime with time components.
        
        OgFieldInfo has multiple datetime fields: rescind_dt, discovery_dt, modified_dt.
        Oracle returns datetime objects with non-zero time components.
        """
        info = OgFieldInfo.model_validate(sample_field_info_data[1])
        
        # Check rescind_dt
        assert info.rescind_dt is not None
        assert isinstance(info.rescind_dt, datetime)
        assert info.rescind_dt == datetime(2020, 1, 15, 9, 0, 0)
        
        # Check discovery_dt
        assert info.discovery_dt is not None
        assert isinstance(info.discovery_dt, datetime)
        assert info.discovery_dt == datetime(1985, 8, 22, 12, 0, 0)
        
        # Check modified_dt
        assert info.modified_dt is not None
        assert isinstance(info.modified_dt, datetime)
        assert info.modified_dt == datetime(2025, 12, 1, 8, 15, 30)


class TestOgFieldRuleModel:
    """Tests for OgFieldRule Pydantic model."""

    def test_valid_rule_creation(
        self, sample_field_rule_data: list[dict[str, Any]]
    ) -> None:
        """Test creating OgFieldRule from valid data."""
        rule = OgFieldRule.model_validate(sample_field_rule_data[0])

        assert rule.oil_or_gas_code == "O"
        assert rule.field_id == 1
        assert rule.rule_type_code == "B"
        assert rule.minimum_lease_distance == 467
        assert rule.minimum_well_distance == 1200
        assert rule.minimum_acres_per_unit == 40.00

    def test_statewide_rule_37_defaults(self) -> None:
        """Test typical Statewide Rule 37 values."""
        data = {
            "oil_or_gas_code": "O",
            "field_id": 1,
            "field_rule_id": 1,
            "rule_type_code": "B",
            "minimum_lease_distance": 467,  # Rule 37 default
            "minimum_well_distance": 1200,  # Rule 37 default
            "minimum_acres_per_unit": 40.00,  # Rule 37 default
            "tolerance_acres": 0.00,
        }
        rule = OgFieldRule.model_validate(data)

        # Verify Rule 37 defaults
        assert rule.minimum_lease_distance == 467
        assert rule.minimum_well_distance == 1200
        assert rule.minimum_acres_per_unit == 40.0

    def test_datetime_fields_with_time_components(
        self, sample_field_rule_data: list[dict[str, Any]]
    ) -> None:
        """Test that datetime fields accept Oracle datetime with time components.
        
        OgFieldRule has effective_dt and modified_dt datetime fields.
        Oracle returns datetime objects with non-zero time components.
        """
        rule = OgFieldRule.model_validate(sample_field_rule_data[0])
        
        # Check effective_dt
        assert rule.effective_dt is not None
        assert isinstance(rule.effective_dt, datetime)
        assert rule.effective_dt == datetime(2024, 1, 1, 0, 0, 0)
        
        # Check modified_dt with time component
        assert rule.modified_dt is not None
        assert isinstance(rule.modified_dt, datetime)
        assert rule.modified_dt == datetime(2025, 6, 15, 16, 45, 22)
        assert rule.modified_dt.hour == 16
        assert rule.modified_dt.minute == 45

    def test_datetime_fields_accept_none(
        self, sample_field_rule_data: list[dict[str, Any]]
    ) -> None:
        """Test that datetime fields accept None values."""
        rule = OgFieldRule.model_validate(sample_field_rule_data[1])
        assert rule.modified_dt is None


class TestModelSerialization:
    """Tests for model JSON serialization."""

    def test_field_to_dict(self, sample_field_data: list[dict[str, Any]]) -> None:
        """Test OgField serialization to dict."""
        field = OgField.model_validate(sample_field_data[0])
        data = field.model_dump()

        assert isinstance(data, dict)
        assert data["field_number"] == "00001001"
        assert data["field_name"] == "TEST FIELD FORMATION 5000"

    def test_field_to_json(self, sample_field_data: list[dict[str, Any]]) -> None:
        """Test OgField serialization to JSON string."""
        field = OgField.model_validate(sample_field_data[0])
        json_str = field.model_dump_json()

        assert isinstance(json_str, str)
        assert "00001001" in json_str
        assert "TEST FIELD FORMATION 5000" in json_str

    def test_datetime_serialization(self, sample_field_data: list[dict[str, Any]]) -> None:
        """Test that datetime fields serialize correctly to JSON."""
        field = OgField.model_validate(sample_field_data[0])
        json_str = field.model_dump_json()
        
        # Datetime should be serialized as ISO format string
        assert "2025-12-19" in json_str
        assert "01:26:51" in json_str

