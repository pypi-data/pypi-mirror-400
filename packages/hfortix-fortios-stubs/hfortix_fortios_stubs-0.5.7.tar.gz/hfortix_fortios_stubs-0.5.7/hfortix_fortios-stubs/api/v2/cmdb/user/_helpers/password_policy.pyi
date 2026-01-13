from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_EXPIRE_STATUS: Literal[{"description": "Passwords expire after expire-day days", "help": "Passwords expire after expire-day days.", "label": "Enable", "name": "enable"}, {"description": "Passwords do not expire", "help": "Passwords do not expire.", "label": "Disable", "name": "disable"}]
VALID_BODY_EXPIRED_PASSWORD_RENEWAL: Literal[{"description": "Enable renewal of a password that already is expired", "help": "Enable renewal of a password that already is expired.", "label": "Enable", "name": "enable"}, {"description": "Disable renewal of a password that already is expired", "help": "Disable renewal of a password that already is expired.", "label": "Disable", "name": "disable"}]
VALID_BODY_REUSE_PASSWORD: Literal[{"description": "Users are allowed to reuse the same password up to a limit", "help": "Users are allowed to reuse the same password up to a limit.", "label": "Enable", "name": "enable"}, {"description": "Users must create a new password", "help": "Users must create a new password.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_EXPIRE_STATUS",
    "VALID_BODY_EXPIRED_PASSWORD_RENEWAL",
    "VALID_BODY_REUSE_PASSWORD",
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