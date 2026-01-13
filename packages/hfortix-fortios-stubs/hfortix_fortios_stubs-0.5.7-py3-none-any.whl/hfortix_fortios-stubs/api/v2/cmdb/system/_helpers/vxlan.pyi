from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_IP_VERSION: Literal[{"description": "Use IPv4 unicast addressing over the VXLAN", "help": "Use IPv4 unicast addressing over the VXLAN.", "label": "Ipv4 Unicast", "name": "ipv4-unicast"}, {"description": "Use IPv6 unicast addressing over the VXLAN", "help": "Use IPv6 unicast addressing over the VXLAN.", "label": "Ipv6 Unicast", "name": "ipv6-unicast"}, {"description": "Use IPv4 multicast addressing over the VXLAN", "help": "Use IPv4 multicast addressing over the VXLAN.", "label": "Ipv4 Multicast", "name": "ipv4-multicast"}, {"description": "Use IPv6 multicast addressing over the VXLAN", "help": "Use IPv6 multicast addressing over the VXLAN.", "label": "Ipv6 Multicast", "name": "ipv6-multicast"}]
VALID_BODY_LEARN_FROM_TRAFFIC: Literal[{"description": "Enable VXLAN MAC learning from traffic", "help": "Enable VXLAN MAC learning from traffic.", "label": "Enable", "name": "enable"}, {"description": "Disable VXLAN MAC learning from traffic", "help": "Disable VXLAN MAC learning from traffic.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_IP_VERSION",
    "VALID_BODY_LEARN_FROM_TRAFFIC",
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