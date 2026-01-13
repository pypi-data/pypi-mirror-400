from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SCHEDULE: Literal[{"description": "Strict scheduling (queue7: highest priority, queue0: lowest priority)", "help": "Strict scheduling (queue7: highest priority, queue0: lowest priority).", "label": "Strict", "name": "strict"}, {"description": "Round robin scheduling", "help": "Round robin scheduling.", "label": "Round Robin", "name": "round-robin"}, {"description": "Weighted round robin scheduling", "help": "Weighted round robin scheduling.", "label": "Weighted", "name": "weighted"}]
VALID_BODY_RATE_BY: Literal[{"description": "Rate by kbps", "help": "Rate by kbps.", "label": "Kbps", "name": "kbps"}, {"description": "Rate by percent", "help": "Rate by percent.", "label": "Percent", "name": "percent"}]

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
    "VALID_BODY_SCHEDULE",
    "VALID_BODY_RATE_BY",
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