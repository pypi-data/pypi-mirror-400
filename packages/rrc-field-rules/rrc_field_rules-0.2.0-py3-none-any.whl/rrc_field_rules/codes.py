"""Code-to-text mappings for RRC field rules data.

This module provides human-readable expansions for coded values
in the RRC database tables.
"""

# Field classification codes
FIELD_CLASS_CODE: dict[str, str] = {
    "G": "Gas",
    "g": "Gas",
    "O": "Oil",
    "o": "Oil",
    "B": "Both (Oil and Gas)",
    "b": "Both (Oil and Gas)",
}

# Oil or Gas classification
OIL_OR_GAS_CODE: dict[str, str] = {
    "G": "Gas",
    "g": "Gas",
    "O": "Oil",
    "o": "Oil",
    "B": "Both",
    "b": "Both",
}

# H2S (Hydrogen Sulfide) presence flag
H2S_FLAG: dict[str, str] = {
    "Y": "Yes - H2S Present",
    "y": "Yes - H2S Present",
    "N": "No - H2S Not Present",
    "n": "No - H2S Not Present",
    "E": "Exempt from Filing",
    "e": "Exempt from Filing",
}

# Yes/No flags (generic)
YES_NO_FLAG: dict[str, str] = {
    "Y": "Yes",
    "y": "Yes",
    "N": "No",
    "n": "No",
}

# Rule type code (base vs optional)
RULE_TYPE_CODE: dict[str, str] = {
    "B": "Base",
    "b": "Base",
    "O": "Optional",
    "o": "Optional",
}

# Diagonal measurement type
DIAGONAL_TYPE_CODE: dict[str, str] = {
    "CC": "Corner-to-Corner",
    "cc": "Corner-to-Corner",
    "WC": "Well-to-Corner",
    "wc": "Well-to-Corner",
}

# Derived rule type code
DERIVED_RULE_TYPE_CODE: dict[str, str] = {
    "CR": "County Rules",
    "cr": "County Rules",
    "MC": "McCulloch County",
    "mc": "McCulloch County",
    "SP": "Special",
    "sp": "Special",
    "SW": "Statewide",
    "sw": "Statewide",
}

# Standard field rule code
STD_FIELD_RULE_CODE: dict[str, str] = {
    "CR": "County Rules",
    "cr": "County Rules",
    "MC": "McCulloch County",
    "mc": "McCulloch County",
    "SW": "Statewide",
    "sw": "Statewide",
}

# Offshore code - geographic surface classification
OFFSHORE_CODE: dict[str, str] = {
    "L": "Land",
    "l": "Land",
    "B": "Bays-Estuaries",
    "b": "Bays-Estuaries",
    "SO": "State Offshore",
    "so": "State Offshore",
    "LB": "Land and Bays-Estuaries",
    "lb": "Land and Bays-Estuaries",
    "BO": "Bays-Estuaries and Offshore",
    "bo": "Bays-Estuaries and Offshore",
    "AL": "All (Land, Bays, Offshore)",
    "al": "All (Land, Bays, Offshore)",
    "SF": "State-Federal",
    "sf": "State-Federal",
}

# District code mapping (table value -> display value)
DISTRICT_CODE: dict[str, str] = {
    "01": "District 01",
    "02": "District 02",
    "03": "District 03",
    "04": "District 04",
    "05": "District 05",
    "06": "District 06",
    "07": "District 6E",
    "6E": "District 6E",
    "6e": "District 6E",
    "08": "District 7B",
    "7B": "District 7B",
    "7b": "District 7B",
    "09": "District 7C",
    "7C": "District 7C",
    "7c": "District 7C",
    "10": "District 08",
    "11": "District 8A",
    "8A": "District 8A",
    "8a": "District 8A",
    "12": "District 8B",
    "8B": "District 8B",
    "8b": "District 8B",
    "13": "District 09",
    "14": "District 10",
}

# Field name to mapping dictionary
FIELD_MAPPINGS: dict[str, dict[str, str]] = {
    "field_class_code": FIELD_CLASS_CODE,
    "oil_or_gas_code": OIL_OR_GAS_CODE,
    "field_h2s_flag": H2S_FLAG,
    "field_manual_rev_flag": YES_NO_FLAG,
    "wildcat_flag": YES_NO_FLAG,
    "salt_dome_flag": YES_NO_FLAG,
    "dont_permit_flag": YES_NO_FLAG,
    "schedule_remarks": YES_NO_FLAG,  # Y=show remarks on terminal, N=don't show
    "rule_type_code": RULE_TYPE_CODE,
    "diagonal_type_code": DIAGONAL_TYPE_CODE,
    "derived_rule_type_code": DERIVED_RULE_TYPE_CODE,
    "std_field_rule_code": STD_FIELD_RULE_CODE,
    "offshore_code": OFFSHORE_CODE,
    "district_code": DISTRICT_CODE,
}


def expand_code(field_name: str, value: str | None) -> str | None:
    """Expand a coded value to its human-readable text.

    Args:
        field_name: The name of the field (e.g., 'field_class_code').
        value: The coded value (e.g., 'O').

    Returns:
        Human-readable text (e.g., 'Oil'), or the original value if no mapping exists.
    """
    if value is None:
        return None

    mapping = FIELD_MAPPINGS.get(field_name)
    if mapping is None:
        return value

    return mapping.get(value, value)


def expand_record(record: dict[str, object]) -> dict[str, object]:
    """Expand all coded values in a record to human-readable text.

    Args:
        record: Dictionary representing a database row.

    Returns:
        New dictionary with expanded values.
    """
    result: dict[str, object] = {}
    for key, value in record.items():
        if key in FIELD_MAPPINGS and isinstance(value, str):
            result[key] = expand_code(key, value)
        else:
            result[key] = value
    return result
