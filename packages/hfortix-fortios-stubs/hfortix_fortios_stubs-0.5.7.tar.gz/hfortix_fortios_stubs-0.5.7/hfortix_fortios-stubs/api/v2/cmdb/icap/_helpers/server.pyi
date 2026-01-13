from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_ADDR_TYPE: Literal[{"description": "Use an IPv4 address for the remote ICAP server", "help": "Use an IPv4 address for the remote ICAP server.", "label": "Ip4", "name": "ip4"}, {"description": "Use an IPv6 address for the remote ICAP server", "help": "Use an IPv6 address for the remote ICAP server.", "label": "Ip6", "name": "ip6"}, {"description": "Use the FQDN for the forwarding proxy server", "help": "Use the FQDN for the forwarding proxy server.", "label": "Fqdn", "name": "fqdn"}]
VALID_BODY_SECURE: Literal[{"description": "Disable connection to secure ICAP server", "help": "Disable connection to secure ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable connection to secure ICAP server", "help": "Enable connection to secure ICAP server.", "label": "Enable", "name": "enable"}]
VALID_BODY_HEALTHCHECK: Literal[{"description": "Disable health checking", "help": "Disable health checking.", "label": "Disable", "name": "disable"}, {"description": "Enable health checking", "help": "Enable health checking.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_ADDR_TYPE",
    "VALID_BODY_SECURE",
    "VALID_BODY_HEALTHCHECK",
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