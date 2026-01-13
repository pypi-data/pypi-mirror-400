from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_UNKNOWN_UNICAST: Literal[{"description": "Enable unknown unicast storm control", "help": "Enable unknown unicast storm control.", "label": "Enable", "name": "enable"}, {"description": "Disable unknown unicast storm control", "help": "Disable unknown unicast storm control.", "label": "Disable", "name": "disable"}]
VALID_BODY_UNKNOWN_MULTICAST: Literal[{"description": "Enable unknown multicast storm control", "help": "Enable unknown multicast storm control.", "label": "Enable", "name": "enable"}, {"description": "Disable unknown multicast storm control", "help": "Disable unknown multicast storm control.", "label": "Disable", "name": "disable"}]
VALID_BODY_BROADCAST: Literal[{"description": "Enable broadcast storm control", "help": "Enable broadcast storm control.", "label": "Enable", "name": "enable"}, {"description": "Disable broadcast storm control", "help": "Disable broadcast storm control.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_UNKNOWN_UNICAST",
    "VALID_BODY_UNKNOWN_MULTICAST",
    "VALID_BODY_BROADCAST",
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