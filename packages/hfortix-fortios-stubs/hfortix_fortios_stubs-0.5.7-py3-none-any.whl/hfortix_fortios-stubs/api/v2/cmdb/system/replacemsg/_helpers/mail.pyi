from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_HEADER: Literal[{"description": "No header type", "help": "No header type.", "label": "None", "name": "none"}, {"description": "HTTP    8bit:8 bit", "help": "HTTP", "label": "Http", "name": "http"}, {"help": "8 bit.", "label": "8Bit", "name": "8bit"}]
VALID_BODY_FORMAT: Literal[{"description": "No format type", "help": "No format type.", "label": "None", "name": "none"}, {"description": "Text format", "help": "Text format.", "label": "Text", "name": "text"}, {"description": "HTML format", "help": "HTML format.", "label": "Html", "name": "html"}]

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
    "VALID_BODY_HEADER",
    "VALID_BODY_FORMAT",
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