from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_COUNT: Literal[{"description": "Enable packet count on the NAC device", "help": "Enable packet count on the NAC device.", "label": "Disable", "name": "disable"}, {"description": "Disable packet count on the NAC device", "help": "Disable packet count on the NAC device.", "label": "Enable", "name": "enable"}]
VALID_BODY_BOUNCE_PORT_LINK: Literal[{"description": "Disable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied", "help": "Disable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied.", "label": "Disable", "name": "disable"}, {"description": "Enable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied", "help": "Enable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied.", "label": "Enable", "name": "enable"}]
VALID_BODY_POE_RESET: Literal[{"description": "Disable POE reset of a switch port where this mac-policy is applied", "help": "Disable POE reset of a switch port where this mac-policy is applied.", "label": "Disable", "name": "disable"}, {"description": "Enable POE reset of a switch port where this mac-policy is applied", "help": "Enable POE reset of a switch port where this mac-policy is applied.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_COUNT",
    "VALID_BODY_BOUNCE_PORT_LINK",
    "VALID_BODY_POE_RESET",
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