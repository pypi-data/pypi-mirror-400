from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"help": "IP addresses in the IP pool can be shared by clients.", "label": "Overload", "name": "overload"}, {"description": "One to one mapping", "help": "One to one mapping.", "label": "One To One", "name": "one-to-one"}, {"description": "Fixed port range", "help": "Fixed port range.", "label": "Fixed Port Range", "name": "fixed-port-range"}, {"description": "Port block allocation", "help": "Port block allocation.", "label": "Port Block Allocation", "name": "port-block-allocation"}]
VALID_BODY_PERMIT_ANY_HOST: Literal[{"description": "Disable full cone NAT", "help": "Disable full cone NAT.", "label": "Disable", "name": "disable"}, {"description": "Enable full cone NAT", "help": "Enable full cone NAT.", "label": "Enable", "name": "enable"}]
VALID_BODY_ARP_REPLY: Literal[{"description": "Disable ARP reply", "help": "Disable ARP reply.", "label": "Disable", "name": "disable"}, {"description": "Enable ARP reply", "help": "Enable ARP reply.", "label": "Enable", "name": "enable"}]
VALID_BODY_NAT64: Literal[{"description": "Disable DNAT64", "help": "Disable DNAT64.", "label": "Disable", "name": "disable"}, {"description": "Enable DNAT64", "help": "Enable DNAT64.", "label": "Enable", "name": "enable"}]
VALID_BODY_ADD_NAT64_ROUTE: Literal[{"description": "Disable adding NAT64 route", "help": "Disable adding NAT64 route.", "label": "Disable", "name": "disable"}, {"description": "Enable adding NAT64 route", "help": "Enable adding NAT64 route.", "label": "Enable", "name": "enable"}]
VALID_BODY_PRIVILEGED_PORT_USE_PBA: Literal[{"description": "Select new nat port for privileged source ports from priviliged range 512-1023", "help": "Select new nat port for privileged source ports from priviliged range 512-1023.", "label": "Disable", "name": "disable"}, {"description": "Select new nat port for privileged source ports from client\u0027s port block", "help": "Select new nat port for privileged source ports from client\u0027s port block", "label": "Enable", "name": "enable"}]
VALID_BODY_SUBNET_BROADCAST_IN_IPPOOL: Literal[{"description": "Do not include the subnetwork address and broadcast IP address in the NAT64 IP pool", "help": "Do not include the subnetwork address and broadcast IP address in the NAT64 IP pool.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_PERMIT_ANY_HOST",
    "VALID_BODY_ARP_REPLY",
    "VALID_BODY_NAT64",
    "VALID_BODY_ADD_NAT64_ROUTE",
    "VALID_BODY_PRIVILEGED_PORT_USE_PBA",
    "VALID_BODY_SUBNET_BROADCAST_IN_IPPOOL",
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