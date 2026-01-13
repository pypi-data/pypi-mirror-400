from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"help": "Disable status.", "name": "disable"}, {"help": "Enable status.", "name": "enable"}]
VALID_BODY_LOG: Literal[{"description": "Disable logging", "help": "Disable logging.", "label": "Disable", "name": "disable"}, {"description": "Enable logging", "help": "Enable logging.", "label": "Enable", "name": "enable"}]
VALID_BODY_LOG_PACKET: Literal[{"description": "Disable packet logging", "help": "Disable packet logging.", "label": "Disable", "name": "disable"}, {"description": "Enable packet logging", "help": "Enable packet logging.", "label": "Enable", "name": "enable"}]
VALID_BODY_ACTION: Literal[{"description": "Pass or allow matching traffic", "help": "Pass or allow matching traffic.", "label": "Pass", "name": "pass"}, {"description": "Block or drop matching traffic", "help": "Block or drop matching traffic.", "label": "Block", "name": "block"}]

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
    "VALID_BODY_LOG",
    "VALID_BODY_LOG_PACKET",
    "VALID_BODY_ACTION",
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