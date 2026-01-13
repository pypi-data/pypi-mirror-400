from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_YOUTUBE: Literal[{"description": "Enable YouTube source", "help": "Enable YouTube source.", "label": "Enable", "name": "enable"}, {"description": "Disable YouTube source", "help": "Disable YouTube source.", "label": "Disable", "name": "disable"}]
VALID_BODY_VIMEO: Literal[{"description": "Enable Vimeo source", "help": "Enable Vimeo source.", "label": "Enable", "name": "enable"}, {"description": "Disable Vimeo source", "help": "Disable Vimeo source.", "label": "Disable", "name": "disable"}]
VALID_BODY_DAILYMOTION: Literal[{"description": "Enable Dailymotion source", "help": "Enable Dailymotion source.", "label": "Enable", "name": "enable"}, {"description": "Disable Dailymotion source", "help": "Disable Dailymotion source.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_YOUTUBE",
    "VALID_BODY_VIMEO",
    "VALID_BODY_DAILYMOTION",
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