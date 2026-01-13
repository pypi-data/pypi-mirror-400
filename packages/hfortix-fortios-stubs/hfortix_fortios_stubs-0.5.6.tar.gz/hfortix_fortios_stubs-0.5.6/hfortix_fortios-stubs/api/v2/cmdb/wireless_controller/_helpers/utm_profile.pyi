from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_UTM_LOG: Literal[{"description": "Enable UTM logging", "help": "Enable UTM logging.", "label": "Enable", "name": "enable"}, {"description": "Disable UTM logging", "help": "Disable UTM logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_SCAN_BOTNET_CONNECTIONS: Literal[{"description": "Do not scan connections to botnet servers", "help": "Do not scan connections to botnet servers.", "label": "Disable", "name": "disable"}, {"description": "Log connections to botnet servers", "help": "Log connections to botnet servers.", "label": "Monitor", "name": "monitor"}, {"description": "Block connections to botnet servers", "help": "Block connections to botnet servers.", "label": "Block", "name": "block"}]

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
    "VALID_BODY_UTM_LOG",
    "VALID_BODY_SCAN_BOTNET_CONNECTIONS",
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