"""Tests for code expansion module."""

import pytest

from rrc_field_rules.codes import (
    FIELD_CLASS_CODE,
    H2S_FLAG,
    OIL_OR_GAS_CODE,
    YES_NO_FLAG,
    expand_code,
    expand_record,
)


class TestExpandCode:
    """Tests for expand_code function."""

    def test_field_class_code_oil(self) -> None:
        """Test oil field class expansion."""
        assert expand_code("field_class_code", "O") == "Oil"
        assert expand_code("field_class_code", "o") == "Oil"

    def test_field_class_code_gas(self) -> None:
        """Test gas field class expansion."""
        assert expand_code("field_class_code", "G") == "Gas"
        assert expand_code("field_class_code", "g") == "Gas"

    def test_field_class_code_both(self) -> None:
        """Test both field class expansion."""
        assert expand_code("field_class_code", "B") == "Both (Oil and Gas)"
        assert expand_code("field_class_code", "b") == "Both (Oil and Gas)"

    def test_h2s_flag_values(self) -> None:
        """Test H2S flag expansion."""
        assert expand_code("field_h2s_flag", "Y") == "Yes - H2S Present"
        assert expand_code("field_h2s_flag", "N") == "No - H2S Not Present"
        assert expand_code("field_h2s_flag", "E") == "Exempt from Filing"

    def test_yes_no_flags(self) -> None:
        """Test generic Y/N flag expansion."""
        assert expand_code("wildcat_flag", "Y") == "Yes"
        assert expand_code("wildcat_flag", "N") == "No"
        assert expand_code("salt_dome_flag", "Y") == "Yes"
        assert expand_code("dont_permit_flag", "N") == "No"
        assert expand_code("schedule_remarks", "Y") == "Yes"
        assert expand_code("schedule_remarks", "N") == "No"
        assert expand_code("field_manual_rev_flag", "Y") == "Yes"

    def test_rule_type_code(self) -> None:
        """Test rule type code expansion."""
        assert expand_code("rule_type_code", "B") == "Base"
        assert expand_code("rule_type_code", "O") == "Optional"

    def test_derived_rule_type_code(self) -> None:
        """Test derived rule type code expansion."""
        assert expand_code("derived_rule_type_code", "SW") == "Statewide"
        assert expand_code("derived_rule_type_code", "CR") == "County Rules"
        assert expand_code("derived_rule_type_code", "MC") == "McCulloch County"
        assert expand_code("derived_rule_type_code", "SP") == "Special"

    def test_offshore_code(self) -> None:
        """Test offshore code expansion."""
        assert expand_code("offshore_code", "L") == "Land"
        assert expand_code("offshore_code", "B") == "Bays-Estuaries"
        assert expand_code("offshore_code", "SO") == "State Offshore"

    def test_diagonal_type_code(self) -> None:
        """Test diagonal type code expansion."""
        assert expand_code("diagonal_type_code", "CC") == "Corner-to-Corner"
        assert expand_code("diagonal_type_code", "WC") == "Well-to-Corner"

    def test_unknown_field_returns_original(self) -> None:
        """Test that unknown fields return original value."""
        assert expand_code("unknown_field", "X") == "X"

    def test_unknown_value_returns_original(self) -> None:
        """Test that unknown values return original value."""
        assert expand_code("field_class_code", "Z") == "Z"

    def test_none_value_returns_none(self) -> None:
        """Test that None values return None."""
        assert expand_code("field_class_code", None) is None


class TestExpandRecord:
    """Tests for expand_record function."""

    def test_expand_single_field(self) -> None:
        """Test expanding a single coded field."""
        record = {"field_class_code": "O", "field_name": "TEST FIELD"}
        result = expand_record(record)

        assert result["field_class_code"] == "Oil"
        assert result["field_name"] == "TEST FIELD"

    def test_expand_multiple_fields(self) -> None:
        """Test expanding multiple coded fields."""
        record = {
            "field_class_code": "G",
            "field_h2s_flag": "Y",
            "wildcat_flag": "N",
            "field_name": "GAS FIELD",
            "field_id": 12345,
        }
        result = expand_record(record)

        assert result["field_class_code"] == "Gas"
        assert result["field_h2s_flag"] == "Yes - H2S Present"
        assert result["wildcat_flag"] == "No"
        assert result["field_name"] == "GAS FIELD"
        assert result["field_id"] == 12345

    def test_expand_preserves_non_string_values(self) -> None:
        """Test that non-string values are preserved."""
        record = {
            "field_id": 123,
            "minimum_acres": 40.5,
            "modified_dt": None,
        }
        result = expand_record(record)

        assert result["field_id"] == 123
        assert result["minimum_acres"] == 40.5
        assert result["modified_dt"] is None

    def test_expand_og_field_info_record(self) -> None:
        """Test expanding an og_field_info-like record."""
        record = {
            "oil_or_gas_code": "O",
            "salt_dome_flag": "N",
            "dont_permit_flag": "N",
            "offshore_code": "L",
            "derived_rule_type_code": "SW",
        }
        result = expand_record(record)

        assert result["oil_or_gas_code"] == "Oil"
        assert result["salt_dome_flag"] == "No"
        assert result["dont_permit_flag"] == "No"
        assert result["offshore_code"] == "Land"
        assert result["derived_rule_type_code"] == "Statewide"

    def test_expand_og_field_rule_record(self) -> None:
        """Test expanding an og_field_rule-like record."""
        record = {
            "oil_or_gas_code": "G",
            "rule_type_code": "B",
            "diagonal_type_code": "CC",
            "minimum_lease_distance": 467,
        }
        result = expand_record(record)

        assert result["oil_or_gas_code"] == "Gas"
        assert result["rule_type_code"] == "Base"
        assert result["diagonal_type_code"] == "Corner-to-Corner"
        assert result["minimum_lease_distance"] == 467


class TestCodeMappings:
    """Tests for code mapping completeness."""

    def test_field_class_code_covers_all_cases(self) -> None:
        """Ensure FIELD_CLASS_CODE has upper and lowercase variants."""
        assert "G" in FIELD_CLASS_CODE
        assert "g" in FIELD_CLASS_CODE
        assert "O" in FIELD_CLASS_CODE
        assert "o" in FIELD_CLASS_CODE
        assert "B" in FIELD_CLASS_CODE
        assert "b" in FIELD_CLASS_CODE

    def test_h2s_flag_covers_all_cases(self) -> None:
        """Ensure H2S_FLAG has all expected values."""
        assert "Y" in H2S_FLAG
        assert "N" in H2S_FLAG
        assert "E" in H2S_FLAG

    def test_oil_or_gas_matches_field_class(self) -> None:
        """Ensure OIL_OR_GAS_CODE values are consistent."""
        assert OIL_OR_GAS_CODE["O"] == "Oil"
        assert OIL_OR_GAS_CODE["G"] == "Gas"
        assert OIL_OR_GAS_CODE["B"] == "Both"

    def test_yes_no_flag_consistency(self) -> None:
        """Ensure YES_NO_FLAG is consistent."""
        assert YES_NO_FLAG["Y"] == "Yes"
        assert YES_NO_FLAG["N"] == "No"
