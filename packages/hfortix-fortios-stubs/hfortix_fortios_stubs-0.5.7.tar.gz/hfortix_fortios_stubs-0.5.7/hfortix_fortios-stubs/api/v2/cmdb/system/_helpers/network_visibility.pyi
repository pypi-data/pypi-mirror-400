from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_DESTINATION_VISIBILITY: Literal[{"description": "Disable logging of destination visibility", "help": "Disable logging of destination visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of destination visibility", "help": "Enable logging of destination visibility.", "label": "Enable", "name": "enable"}]
VALID_BODY_SOURCE_LOCATION: Literal[{"description": "Disable logging of source geographical location visibility", "help": "Disable logging of source geographical location visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of source geographical location visibility", "help": "Enable logging of source geographical location visibility.", "label": "Enable", "name": "enable"}]
VALID_BODY_DESTINATION_HOSTNAME_VISIBILITY: Literal[{"description": "Disable logging of destination hostname visibility", "help": "Disable logging of destination hostname visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of destination hostname visibility", "help": "Enable logging of destination hostname visibility.", "label": "Enable", "name": "enable"}]
VALID_BODY_DESTINATION_LOCATION: Literal[{"description": "Disable logging of destination geographical location visibility", "help": "Disable logging of destination geographical location visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of destination geographical location visibility", "help": "Enable logging of destination geographical location visibility.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_DESTINATION_VISIBILITY",
    "VALID_BODY_SOURCE_LOCATION",
    "VALID_BODY_DESTINATION_HOSTNAME_VISIBILITY",
    "VALID_BODY_DESTINATION_LOCATION",
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