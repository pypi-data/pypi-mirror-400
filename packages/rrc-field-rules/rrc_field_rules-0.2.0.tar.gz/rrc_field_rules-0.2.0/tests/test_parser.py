"""Tests for parser module."""

from typing import Any

import pytest

from rrc_field_rules.models import OgField, OgFieldRule


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
