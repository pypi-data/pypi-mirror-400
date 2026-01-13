from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_ADVERTISING: Literal[{"description": "iBeacon advertising", "help": "iBeacon advertising.", "label": "Ibeacon", "name": "ibeacon"}, {"description": "Eddystone UID advertising", "help": "Eddystone UID advertising.", "label": "Eddystone Uid", "name": "eddystone-uid"}, {"description": "Eddystone URL advertising", "help": "Eddystone URL advertising.", "label": "Eddystone Url", "name": "eddystone-url"}]
VALID_BODY_TXPOWER: Literal[{"description": "Transmit power level 0 (-21 dBm)    1:Transmit power level 1 (-18 dBm)    2:Transmit power level 2 (-15 dBm)    3:Transmit power level 3 (-12 dBm)    4:Transmit power level 4 (-9 dBm)    5:Transmit power level 5 (-6 dBm)    6:Transmit power level 6 (-3 dBm)    7:Transmit power level 7 (0 dBm)    8:Transmit power level 8 (1 dBm)    9:Transmit power level 9 (2 dBm)    10:Transmit power level 10 (3 dBm)    11:Transmit power level 11 (4 dBm)    12:Transmit power level 12 (5 dBm)    13:Transmit power level 13 (8 dBm)    14:Transmit power level 14 (11 dBm)    15:Transmit power level 15 (14 dBm)    16:Transmit power level 16 (17 dBm)    17:Transmit power level 17 (20 dBm)", "help": "Transmit power level 0 (-21 dBm)", "label": "0", "name": "0"}, {"help": "Transmit power level 1 (-18 dBm)", "label": "1", "name": "1"}, {"help": "Transmit power level 2 (-15 dBm)", "label": "2", "name": "2"}, {"help": "Transmit power level 3 (-12 dBm)", "label": "3", "name": "3"}, {"help": "Transmit power level 4 (-9 dBm)", "label": "4", "name": "4"}, {"help": "Transmit power level 5 (-6 dBm)", "label": "5", "name": "5"}, {"help": "Transmit power level 6 (-3 dBm)", "label": "6", "name": "6"}, {"help": "Transmit power level 7 (0 dBm)", "label": "7", "name": "7"}, {"help": "Transmit power level 8 (1 dBm)", "label": "8", "name": "8"}, {"help": "Transmit power level 9 (2 dBm)", "label": "9", "name": "9"}, {"help": "Transmit power level 10 (3 dBm)", "label": "10", "name": "10"}, {"help": "Transmit power level 11 (4 dBm)", "label": "11", "name": "11"}, {"help": "Transmit power level 12 (5 dBm)", "label": "12", "name": "12"}, {"help": "Transmit power level 13 (8 dBm)", "label": "13", "name": "13"}, {"help": "Transmit power level 14 (11 dBm)", "label": "14", "name": "14"}, {"help": "Transmit power level 15 (14 dBm)", "label": "15", "name": "15"}, {"help": "Transmit power level 16 (17 dBm)", "label": "16", "name": "16"}, {"help": "Transmit power level 17 (20 dBm)", "label": "17", "name": "17"}]
VALID_BODY_BLE_SCANNING: Literal[{"description": "Enable BLE scanning", "help": "Enable BLE scanning.", "label": "Enable", "name": "enable"}, {"description": "Disable BLE scanning", "help": "Disable BLE scanning.", "label": "Disable", "name": "disable"}]
VALID_BODY_SCAN_TYPE: Literal[{"description": "Active BLE scanning", "help": "Active BLE scanning.", "label": "Active", "name": "active"}, {"description": "Passive BLE scanning", "help": "Passive BLE scanning.", "label": "Passive", "name": "passive"}]

# Metadata dictionaries
FIELD_TYPES: dict[str, str]
FIELD_DESCRIPTIONS: dict[str, str]
FIELD_CONSTRAINTS: dict[str, dict[str, Any]]
NESTED_SCHEMAS: dict[str, dict[str, Any]]
FIELDS_WITH_DEFAULTS: dict[str, Any]

# Helper functions
def get_field_type(field_name: str) -> str | None: ...
def get_field_description(field_name: str) -> str | None: ...
def get_field_default(field_name: str) -> Any: ...
def get_field_constraints(field_name: str) -> dict[str, Any]: ...
def get_nested_schema(field_name: str) -> dict[str, Any] | None: ...
def get_field_metadata(field_name: str) -> dict[str, Any]: ...
def validate_field_value(field_name: str, value: Any) -> bool: ...
def get_all_fields() -> list[str]: ...
def get_required_fields() -> list[str]: ...
def get_schema_info() -> dict[str, Any]: ...


__all__ = [
    "VALID_BODY_ADVERTISING",
    "VALID_BODY_TXPOWER",
    "VALID_BODY_BLE_SCANNING",
    "VALID_BODY_SCAN_TYPE",
    "FIELD_TYPES",
    "FIELD_DESCRIPTIONS",
    "FIELD_CONSTRAINTS",
    "NESTED_SCHEMAS",
    "FIELDS_WITH_DEFAULTS",
    "get_field_type",
    "get_field_description",
    "get_field_default",
    "get_field_constraints",
    "get_nested_schema",
    "get_field_metadata",
    "validate_field_value",
    "get_all_fields",
    "get_required_fields",
    "get_schema_info",
]