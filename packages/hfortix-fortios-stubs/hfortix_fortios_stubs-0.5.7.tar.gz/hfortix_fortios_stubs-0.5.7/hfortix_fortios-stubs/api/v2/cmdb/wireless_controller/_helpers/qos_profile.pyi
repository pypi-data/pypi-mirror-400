from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_BURST: Literal[{"description": "Enable client rate burst", "help": "Enable client rate burst.", "label": "Enable", "name": "enable"}, {"description": "Disable client rate burst", "help": "Disable client rate burst.", "label": "Disable", "name": "disable"}]
VALID_BODY_WMM: Literal[{"description": "Enable WiFi multi-media (WMM) control", "help": "Enable WiFi multi-media (WMM) control.", "label": "Enable", "name": "enable"}, {"description": "Disable WiFi multi-media (WMM) control", "help": "Disable WiFi multi-media (WMM) control.", "label": "Disable", "name": "disable"}]
VALID_BODY_WMM_UAPSD: Literal[{"description": "Enable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode", "help": "Enable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode", "help": "Disable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode.", "label": "Disable", "name": "disable"}]
VALID_BODY_CALL_ADMISSION_CONTROL: Literal[{"description": "Enable WMM call admission control", "help": "Enable WMM call admission control.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM call admission control", "help": "Disable WMM call admission control.", "label": "Disable", "name": "disable"}]
VALID_BODY_BANDWIDTH_ADMISSION_CONTROL: Literal[{"description": "Enable WMM bandwidth admission control", "help": "Enable WMM bandwidth admission control.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM bandwidth admission control", "help": "Disable WMM bandwidth admission control.", "label": "Disable", "name": "disable"}]
VALID_BODY_DSCP_WMM_MAPPING: Literal[{"description": "Enable Differentiated Services Code Point (DSCP) mapping", "help": "Enable Differentiated Services Code Point (DSCP) mapping.", "label": "Enable", "name": "enable"}, {"description": "Disable Differentiated Services Code Point (DSCP) mapping", "help": "Disable Differentiated Services Code Point (DSCP) mapping.", "label": "Disable", "name": "disable"}]
VALID_BODY_WMM_DSCP_MARKING: Literal[{"description": "Enable WMM Differentiated Services Code Point (DSCP) marking", "help": "Enable WMM Differentiated Services Code Point (DSCP) marking.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM Differentiated Services Code Point (DSCP) marking", "help": "Disable WMM Differentiated Services Code Point (DSCP) marking.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_BURST",
    "VALID_BODY_WMM",
    "VALID_BODY_WMM_UAPSD",
    "VALID_BODY_CALL_ADMISSION_CONTROL",
    "VALID_BODY_BANDWIDTH_ADMISSION_CONTROL",
    "VALID_BODY_DSCP_WMM_MAPPING",
    "VALID_BODY_WMM_DSCP_MARKING",
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