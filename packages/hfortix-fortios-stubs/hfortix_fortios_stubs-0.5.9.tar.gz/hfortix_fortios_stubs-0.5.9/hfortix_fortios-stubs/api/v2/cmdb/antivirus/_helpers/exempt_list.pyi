from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_HASH_TYPE: Literal[{"description": "MD5 hash value (32 characters in length)", "help": "MD5 hash value (32 characters in length).", "label": "Md5", "name": "md5"}, {"description": "SHA1 hash value (40 characters in length)", "help": "SHA1 hash value (40 characters in length).", "label": "Sha1", "name": "sha1"}, {"description": "SHA256 hash value (64 characters in length)", "help": "SHA256 hash value (64 characters in length).", "label": "Sha256", "name": "sha256"}]
VALID_BODY_STATUS: Literal[{"description": "Disable AV exempt-list table entry", "help": "Disable AV exempt-list table entry.", "label": "Disable", "name": "disable"}, {"description": "Enable AV exempt-list table entry", "help": "Enable AV exempt-list table entry.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_HASH_TYPE",
    "VALID_BODY_STATUS",
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