"""Pydantic models for Texas RRC Field Rules tables.

These models represent the Oracle database tables containing field rules data
from the Texas Railroad Commission Oil & Gas Division.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OgField(BaseModel):
    """Oil & Gas Field master record.

    Contains core field information including field number, name, classification,
    and various operational flags.
    """

    field_number: str = Field(
        ...,
        max_length=8,
        description="8-digit field number. First 5 digits unique, last 3 are reservoir number.",
    )
    field_name: str = Field(
        ...,
        max_length=50,
        description="Field name (operator choice + formation + depth, e.g., 'Johnson Frio 4700').",
    )
    field_id: int = Field(..., description="System-generated unique key.")
    field_class_code: Literal["G", "O", "B", "g", "o", "b"] = Field(
        ..., description="Field class: G=gas, O=oil, B=both (associated)."
    )
    field_h2s_flag: Literal["Y", "N", "E", "y", "n", "e"] = Field(
        ..., description="H2S presence: Y=present, N=not present, E=exempt from filing."
    )
    field_manual_rev_flag: Literal["Y", "N", "y", "n"] = Field(
        ..., description="Complex rules requiring manual intervention."
    )
    wildcat_flag: Literal["Y", "N", "y", "n"] = Field(
        ..., description="No known zone of production for this field."
    )
    district_id: int = Field(..., description="System key for district relation.")
    district_code: str | None = Field(
        None, max_length=2, description="RRC district code (01-10, 6e, 7b, 7c, 8a, 8b)."
    )
    associated_field_id: int | None = Field(
        None, description="Related oil field ID when gas field has different number."
    )
    modified_by: str | None = Field(None, max_length=30, description="Last modifier ID.")
    modified_dt: date | None = Field(None, description="Last modification date.")

    model_config = ConfigDict(from_attributes=True)


class OgFieldInfo(BaseModel):
    """Field information record with additional details.

    Contains discovery dates, county information, offshore codes, and remarks.
    """

    oil_or_gas_code: Literal["G", "O", "B", "g", "o", "b"] = Field(
        ..., description="Classification: G=gas, O=oil, B=both."
    )
    field_info_id: int = Field(..., description="System-generated unique key.")
    field_id: int = Field(..., description="Foreign key to og_field.")
    salt_dome_flag: Literal["Y", "N", "y", "n"] = Field(
        ..., description="Salt dome classification (statewide spacing rule exemption)."
    )
    derived_rule_type_code: str | None = Field(
        None,
        max_length=2,
        description="Rule type: CR=county rules, MC=McCulloch, SP=special, SW=statewide.",
    )
    rescind_dt: date | None = Field(
        None, description="Date field rules rescinded (reverted to statewide)."
    )
    offshore_code: str | None = Field(
        None,
        max_length=2,
        description="Geographic surface: L=land, B=bays, SO=state offshore, etc.",
    )
    dont_permit_flag: Literal["Y", "N", "y", "n"] = Field(
        ..., description="No wells permitted (field consolidated)."
    )
    schedule_remarks: str | None = Field(
        None, max_length=66, description="Proration analyst remarks (Y=show on terminal)."
    )
    comments: str | None = Field(
        None, max_length=66, description="Free-form analyst comments."
    )
    noa_manual_rev_rule: str | None = Field(
        None,
        max_length=2000,
        description="Horizontal/vertical drilling spacing & depth remarks.",
    )
    discovery_dt: date | None = Field(
        None, description="Discovery date of first well (CCYYMMDD format)."
    )
    county_code: str | None = Field(
        None, max_length=3, description="County code (odd=onshore, even=offshore)."
    )
    modified_by: str | None = Field(None, max_length=30, description="Last modifier ID.")
    modified_dt: date | None = Field(None, description="Last modification date.")

    model_config = ConfigDict(from_attributes=True)


class OgFieldRule(BaseModel):
    """Field-specific spacing and acreage rules.

    Contains well spacing requirements, lease distances, and proration unit sizes.
    """

    oil_or_gas_code: Literal["G", "O", "B", "g", "o", "b"] = Field(
        ..., description="Classification: G=gas, O=oil, B=both."
    )
    field_id: int = Field(..., description="Foreign key to og_field.")
    field_rule_id: int = Field(..., description="System-generated unique key.")
    rule_type_code: Literal["B", "O", "b", "o"] = Field(
        ..., description="Rule type: B=base, O=optional."
    )
    minimum_lease_distance: int = Field(
        ..., description="Minimum distance from lease line (feet)."
    )
    minimum_well_distance: int = Field(
        ..., description="Minimum distance between wells (feet)."
    )
    minimum_acres_per_unit: float = Field(
        ..., description="Minimum acres dedicated to each well."
    )
    tolerance_acres: float = Field(
        ..., description="Remaining acreage tolerance after full unit allocation."
    )
    diagonal_type_code: str | None = Field(
        None, max_length=2, description="Diagonal measurement: CC=corner-to-corner, WC=well-to-corner."
    )
    maximum_diagonal_length: float | None = Field(
        None, description="Maximum diagonal measurement (feet)."
    )
    effective_dt: date | None = Field(None, description="Rule effective date.")
    modified_by: str | None = Field(None, max_length=30, description="Last modifier ID.")
    modified_dt: date | None = Field(None, description="Last modification date.")

    model_config = ConfigDict(from_attributes=True)


class OgStdFieldRule(BaseModel):
    """Statewide standard field rules.

    Contains default spacing rules based on depth ranges (county rules, statewide rules).
    """

    std_field_rule_code: str = Field(
        ..., max_length=2, description="Rule code: CR=county, MC=McCulloch, SW=statewide."
    )
    std_field_rule_id: str = Field(
        ..., max_length=4, description="Relative table ID (e.g., CR1, CR2, SW1, SW2)."
    )
    min_depth: int = Field(..., description="Top of production zone (feet).")
    max_depth: int = Field(..., description="Bottom of production zone (feet).")
    min_lease_distance: int = Field(
        ..., description="Minimum distance from lease line (feet)."
    )
    min_well_distance: int = Field(
        ..., description="Minimum distance between wells (feet)."
    )
    min_acres_per_unit: float = Field(
        ..., description="Minimum acres per proration unit."
    )

    model_config = ConfigDict(from_attributes=True)


# Type alias for all model types
FieldRulesModel = OgField | OgFieldInfo | OgFieldRule | OgStdFieldRule

# Table name to model mapping
TABLE_MODELS: dict[str, type[FieldRulesModel]] = {
    "og_field": OgField,
    "og_field_info": OgFieldInfo,
    "og_field_rule": OgFieldRule,
    "og_std_field_rule": OgStdFieldRule,
}

# List of available tables
AVAILABLE_TABLES: list[str] = list(TABLE_MODELS.keys())
