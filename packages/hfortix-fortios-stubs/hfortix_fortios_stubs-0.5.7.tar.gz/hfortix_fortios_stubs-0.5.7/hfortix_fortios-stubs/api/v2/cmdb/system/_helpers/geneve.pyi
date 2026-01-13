from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"description": "Internal packet includes Ethernet header", "help": "Internal packet includes Ethernet header.", "label": "Ethernet", "name": "ethernet"}, {"description": "Internal packet does not include Ethernet header", "help": "Internal packet does not include Ethernet header.", "label": "Ppp", "name": "ppp"}]
VALID_BODY_IP_VERSION: Literal[{"description": "Use IPv4 unicast addressing over the GENEVE", "help": "Use IPv4 unicast addressing over the GENEVE.", "label": "Ipv4 Unicast", "name": "ipv4-unicast"}, {"description": "Use IPv6 unicast addressing over the GENEVE", "help": "Use IPv6 unicast addressing over the GENEVE.", "label": "Ipv6 Unicast", "name": "ipv6-unicast"}]

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
    "VALID_BODY_TYPE",
    "VALID_BODY_IP_VERSION",
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