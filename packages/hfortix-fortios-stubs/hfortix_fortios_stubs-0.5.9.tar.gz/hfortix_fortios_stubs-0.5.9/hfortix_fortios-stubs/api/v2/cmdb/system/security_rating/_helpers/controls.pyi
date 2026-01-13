from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_DISPLAY_REPORT: Literal[{"description": "Enable displaying the Security Rating control in the default report", "help": "Enable displaying the Security Rating control in the default report.", "label": "Enable", "name": "enable"}, {"description": "Disable displaying the Security Rating control in the default report", "help": "Disable displaying the Security Rating control in the default report.", "label": "Disable", "name": "disable"}]
VALID_BODY_DISPLAY_INSIGHT: Literal[{"description": "Enable displaying the Security Rating control as an insight across the GUI", "help": "Enable displaying the Security Rating control as an insight across the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable displaying the Security Rating control as an insight across the GUI", "help": "Disable displaying the Security Rating control as an insight across the GUI.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_DISPLAY_REPORT",
    "VALID_BODY_DISPLAY_INSIGHT",
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