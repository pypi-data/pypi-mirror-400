from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable Status of the entry", "help": "Enable Status of the entry.", "label": "Enable", "name": "enable"}, {"description": "Disable Status of the entry", "help": "Disable Status of the entry.", "label": "Disable", "name": "disable"}]
VALID_BODY_CONNECTION_MODE: Literal[{"description": "Connect the different destinations sequentially", "help": "Connect the different destinations sequentially.", "label": "Sequentially", "name": "sequentially"}, {"description": "Connect the different destinations simultaneously", "help": "Connect the different destinations simultaneously.", "label": "Simultaneously", "name": "simultaneously"}]
VALID_BODY_PROTOCOL: Literal[{"description": "Connect IPv4 destinations first", "help": "Connect IPv4 destinations first.", "label": "Ipv4 First", "name": "IPv4-first"}, {"description": "Connect IPv6 destinations first", "help": "Connect IPv6 destinations first.", "label": "Ipv6 First", "name": "IPv6-first"}, {"description": "Connect IPv4 destinations only", "help": "Connect IPv4 destinations only.", "label": "Ipv4 Only", "name": "IPv4-only"}, {"description": "Connect IPv6 destinations only", "help": "Connect IPv6 destinations only.", "label": "Ipv6 Only", "name": "IPv6-only"}]

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
    "VALID_BODY_CONNECTION_MODE",
    "VALID_BODY_PROTOCOL",
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