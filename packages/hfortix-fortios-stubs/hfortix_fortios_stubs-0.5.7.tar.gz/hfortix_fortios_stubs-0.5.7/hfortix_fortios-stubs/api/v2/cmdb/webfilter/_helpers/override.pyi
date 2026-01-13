from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable override rule", "help": "Enable override rule.", "label": "Enable", "name": "enable"}, {"description": "Disable override rule", "help": "Disable override rule.", "label": "Disable", "name": "disable"}]
VALID_BODY_SCOPE: Literal[{"description": "Override the specified user", "help": "Override the specified user.", "label": "User", "name": "user"}, {"description": "Override the specified user group", "help": "Override the specified user group.", "label": "User Group", "name": "user-group"}, {"description": "Override the specified IP address", "help": "Override the specified IP address.", "label": "Ip", "name": "ip"}, {"description": "Override the specified IPv6 address", "help": "Override the specified IPv6 address.", "label": "Ip6", "name": "ip6"}]

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
    "VALID_BODY_SCOPE",
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