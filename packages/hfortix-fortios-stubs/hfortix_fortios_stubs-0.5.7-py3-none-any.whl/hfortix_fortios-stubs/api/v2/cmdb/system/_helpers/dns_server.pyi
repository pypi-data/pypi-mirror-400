from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_MODE: Literal[{"description": "Shadow DNS database and forward", "help": "Shadow DNS database and forward.", "label": "Recursive", "name": "recursive"}, {"description": "Public DNS database only", "help": "Public DNS database only.", "label": "Non Recursive", "name": "non-recursive"}, {"description": "Forward only", "help": "Forward only.", "label": "Forward Only", "name": "forward-only"}, {"description": "Recursive resolver mode", "help": "Recursive resolver mode.", "label": "Resolver", "name": "resolver"}]
VALID_BODY_DOH: Literal[{"description": "Enable DNS over HTTPS", "help": "Enable DNS over HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS over HTTPS", "help": "Disable DNS over HTTPS.", "label": "Disable", "name": "disable"}]
VALID_BODY_DOH3: Literal[{"description": "Enable DNS over HTTP3/QUIC", "help": "Enable DNS over HTTP3/QUIC.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS over HTTP3/QUIC", "help": "Disable DNS over HTTP3/QUIC.", "label": "Disable", "name": "disable"}]
VALID_BODY_DOQ: Literal[{"description": "Enable DNS over QUIC", "help": "Enable DNS over QUIC.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS over QUIC", "help": "Disable DNS over QUIC.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_MODE",
    "VALID_BODY_DOH",
    "VALID_BODY_DOH3",
    "VALID_BODY_DOQ",
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