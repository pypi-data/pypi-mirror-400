from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_DIRECTION: Literal[{"description": "As source in the firewall policy", "help": "As source in the firewall policy.", "label": "Src", "name": "src"}, {"description": "As destination in the firewall policy", "help": "As destination in the firewall policy.", "label": "Dst", "name": "dst"}, {"description": "Both directions in the firewall policy", "help": "Both directions in the firewall policy.", "label": "Both", "name": "both"}]
VALID_BODY_DATABASE: Literal[{"description": "Internet Service Database", "help": "Internet Service Database.", "label": "Isdb", "name": "isdb"}, {"description": "Internet RRR Database", "help": "Internet RRR Database.", "label": "Irdb", "name": "irdb"}]

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
    "VALID_BODY_DIRECTION",
    "VALID_BODY_DATABASE",
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