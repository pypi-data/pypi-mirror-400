from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TTL_MODE: Literal[{"description": "Reinitialize TTL", "help": "Reinitialize TTL.", "label": "Reinit", "name": "reinit"}, {"description": "Decrease TTL", "help": "Decrease TTL.", "label": "Decrease", "name": "decrease"}, {"description": "Retain TTL", "help": "Retain TTL.", "label": "Retain", "name": "retain"}]
VALID_BODY_MODE: Literal[{"description": "Disable probe", "help": "Disable probe.", "label": "None", "name": "none"}, {"description": "HTTP probe", "help": "HTTP probe.", "label": "Http Probe", "name": "http-probe"}, {"description": "Two way active measurement protocol", "help": "Two way active measurement protocol.", "label": "Twamp", "name": "twamp"}]
VALID_BODY_SECURITY_MODE: Literal[{"description": "Unauthenticated mode", "help": "Unauthenticated mode.", "label": "None", "name": "none"}, {"description": "Authenticated mode", "help": "Authenticated mode.", "label": "Authentication", "name": "authentication"}]

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
    "VALID_BODY_TTL_MODE",
    "VALID_BODY_MODE",
    "VALID_BODY_SECURITY_MODE",
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