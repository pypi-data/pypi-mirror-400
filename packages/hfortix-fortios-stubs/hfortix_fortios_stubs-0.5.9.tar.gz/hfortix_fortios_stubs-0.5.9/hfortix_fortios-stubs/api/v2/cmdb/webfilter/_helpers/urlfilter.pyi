from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_ONE_ARM_IPS_URLFILTER: Literal[{"description": "Enable DNS resolver for one-arm IPS URL filter operation", "help": "Enable DNS resolver for one-arm IPS URL filter operation.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS resolver for one-arm IPS URL filter operation", "help": "Disable DNS resolver for one-arm IPS URL filter operation.", "label": "Disable", "name": "disable"}]
VALID_BODY_IP_ADDR_BLOCK: Literal[{"description": "Enable blocking URLs when the hostname appears as an IP address", "help": "Enable blocking URLs when the hostname appears as an IP address.", "label": "Enable", "name": "enable"}, {"description": "Disable blocking URLs when the hostname appears as an IP address", "help": "Disable blocking URLs when the hostname appears as an IP address.", "label": "Disable", "name": "disable"}]
VALID_BODY_IP4_MAPPED_IP6: Literal[{"description": "Enable matching IPv4 mapped IPv6 URLs", "help": "Enable matching IPv4 mapped IPv6 URLs.", "label": "Enable", "name": "enable"}, {"description": "Disable matching IPv4 mapped IPv6 URLs", "help": "Disable matching IPv4 mapped IPv6 URLs.", "label": "Disable", "name": "disable"}]
VALID_BODY_INCLUDE_SUBDOMAINS: Literal[{"description": "Enable matching subdomains", "help": "Enable matching subdomains. Applies only to simple type.", "label": "Enable", "name": "enable"}, {"description": "Disable matching subdomains", "help": "Disable matching subdomains. Applies only to simple type.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_ONE_ARM_IPS_URLFILTER",
    "VALID_BODY_IP_ADDR_BLOCK",
    "VALID_BODY_IP4_MAPPED_IP6",
    "VALID_BODY_INCLUDE_SUBDOMAINS",
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