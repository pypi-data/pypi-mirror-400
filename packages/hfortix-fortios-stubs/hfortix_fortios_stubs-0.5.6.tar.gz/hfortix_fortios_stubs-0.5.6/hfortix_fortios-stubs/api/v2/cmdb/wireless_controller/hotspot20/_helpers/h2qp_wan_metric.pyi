from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_LINK_STATUS: Literal[{"description": "Link up", "help": "Link up.", "label": "Up", "name": "up"}, {"description": "Link down", "help": "Link down.", "label": "Down", "name": "down"}, {"description": "Link in test state", "help": "Link in test state.", "label": "In Test", "name": "in-test"}]
VALID_BODY_SYMMETRIC_WAN_LINK: Literal[{"description": "Symmetric WAN link (uplink and downlink speeds are the same)", "help": "Symmetric WAN link (uplink and downlink speeds are the same).", "label": "Symmetric", "name": "symmetric"}, {"description": "Asymmetric WAN link (uplink and downlink speeds are not the same)", "help": "Asymmetric WAN link (uplink and downlink speeds are not the same).", "label": "Asymmetric", "name": "asymmetric"}]
VALID_BODY_LINK_AT_CAPACITY: Literal[{"description": "Link at capacity (not allow additional mobile devices to associate)", "help": "Link at capacity (not allow additional mobile devices to associate).", "label": "Enable", "name": "enable"}, {"description": "Link not at capacity (allow additional mobile devices to associate)", "help": "Link not at capacity (allow additional mobile devices to associate).", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_LINK_STATUS",
    "VALID_BODY_SYMMETRIC_WAN_LINK",
    "VALID_BODY_LINK_AT_CAPACITY",
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