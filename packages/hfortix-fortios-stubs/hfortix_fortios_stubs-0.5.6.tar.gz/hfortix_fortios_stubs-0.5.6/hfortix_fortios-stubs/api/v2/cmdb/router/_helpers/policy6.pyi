from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_INPUT_DEVICE_NEGATE: Literal[{"description": "Enable negation of input device match", "help": "Enable negation of input device match.", "label": "Enable", "name": "enable"}, {"description": "Disable negation of input device match", "help": "Disable negation of input device match.", "label": "Disable", "name": "disable"}]
VALID_BODY_SRC_NEGATE: Literal[{"description": "Enable source address negation", "help": "Enable source address negation.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negation", "help": "Disable source address negation.", "label": "Disable", "name": "disable"}]
VALID_BODY_DST_NEGATE: Literal[{"description": "Enable destination address negation", "help": "Enable destination address negation.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negation", "help": "Disable destination address negation.", "label": "Disable", "name": "disable"}]
VALID_BODY_ACTION: Literal[{"description": "Do not search policy route table", "help": "Do not search policy route table.", "label": "Deny", "name": "deny"}, {"description": "Use this policy route for forwarding", "help": "Use this policy route for forwarding.", "label": "Permit", "name": "permit"}]
VALID_BODY_STATUS: Literal[{"description": "Enable this policy route", "help": "Enable this policy route.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy route", "help": "Disable this policy route.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_INPUT_DEVICE_NEGATE",
    "VALID_BODY_SRC_NEGATE",
    "VALID_BODY_DST_NEGATE",
    "VALID_BODY_ACTION",
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