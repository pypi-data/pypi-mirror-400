from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Add FortiSwitch logs to FortiGate event log", "help": "Add FortiSwitch logs to FortiGate event log.", "label": "Enable", "name": "enable"}, {"description": "Do not add  FortiSwitch logs to FortiGate event log", "help": "Do not add  FortiSwitch logs to FortiGate event log.", "label": "Disable", "name": "disable"}]
VALID_BODY_SEVERITY: Literal[{"description": "Emergency level", "help": "Emergency level.", "label": "Emergency", "name": "emergency"}, {"description": "Alert level", "help": "Alert level.", "label": "Alert", "name": "alert"}, {"description": "Critical level", "help": "Critical level.", "label": "Critical", "name": "critical"}, {"description": "Error level", "help": "Error level.", "label": "Error", "name": "error"}, {"description": "Warning level", "help": "Warning level.", "label": "Warning", "name": "warning"}, {"description": "Notification level", "help": "Notification level.", "label": "Notification", "name": "notification"}, {"description": "Information level", "help": "Information level.", "label": "Information", "name": "information"}, {"description": "Debug level", "help": "Debug level.", "label": "Debug", "name": "debug"}]

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
    "VALID_BODY_STATUS",
    "VALID_BODY_SEVERITY",
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