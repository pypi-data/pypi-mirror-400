from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable this policy", "help": "Enable this policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy", "help": "Disable this policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_TYPE: Literal[{"description": "Perform IPv4 source NAT", "help": "Perform IPv4 source NAT.", "label": "Ipv4", "name": "ipv4"}, {"description": "Perform IPv6 source NAT", "help": "Perform IPv6 source NAT.", "label": "Ipv6", "name": "ipv6"}]
VALID_BODY_NAT: Literal[{"description": "Disable source NAT", "help": "Disable source NAT.", "label": "Disable", "name": "disable"}, {"description": "Enable source NAT", "help": "Enable source NAT.", "label": "Enable", "name": "enable"}]
VALID_BODY_NAT46: Literal[{"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}]
VALID_BODY_NAT64: Literal[{"description": "Enable NAT64", "help": "Enable NAT64.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT64", "help": "Disable NAT64.", "label": "Disable", "name": "disable"}]
VALID_BODY_PORT_PRESERVE: Literal[{"description": "Use the original source port if it has not been used", "help": "Use the original source port if it has not been used.", "label": "Enable", "name": "enable"}, {"description": "Source NAT always changes the source port", "help": "Source NAT always changes the source port.", "label": "Disable", "name": "disable"}]
VALID_BODY_PORT_RANDOM: Literal[{"description": "Enable random source port selection for source NAT", "help": "Enable random source port selection for source NAT.", "label": "Enable", "name": "enable"}, {"description": "Disable random source port selection for source NAT", "help": "Disable random source port selection for source NAT.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_TYPE",
    "VALID_BODY_NAT",
    "VALID_BODY_NAT46",
    "VALID_BODY_NAT64",
    "VALID_BODY_PORT_PRESERVE",
    "VALID_BODY_PORT_RANDOM",
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