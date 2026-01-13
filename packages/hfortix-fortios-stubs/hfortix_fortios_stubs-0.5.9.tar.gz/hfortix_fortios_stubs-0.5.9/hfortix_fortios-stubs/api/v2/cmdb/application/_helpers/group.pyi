from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"description": "Application ID", "help": "Application ID.", "label": "Application", "name": "application"}, {"description": "Application filter", "help": "Application filter.", "label": "Filter", "name": "filter"}]
VALID_BODY_POPULARITY: Literal[{"description": "Popularity level 1", "help": "Popularity level 1.", "label": "1", "name": "1"}, {"description": "Popularity level 2", "help": "Popularity level 2.", "label": "2", "name": "2"}, {"description": "Popularity level 3", "help": "Popularity level 3.", "label": "3", "name": "3"}, {"description": "Popularity level 4", "help": "Popularity level 4.", "label": "4", "name": "4"}, {"description": "Popularity level 5", "help": "Popularity level 5.", "label": "5", "name": "5"}]

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
    "VALID_BODY_TYPE",
    "VALID_BODY_POPULARITY",
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