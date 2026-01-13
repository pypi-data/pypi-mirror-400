from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable this DHCPv6 server configuration", "help": "Enable this DHCPv6 server configuration.", "label": "Disable", "name": "disable"}, {"description": "Disable this DHCPv6 server configuration", "help": "Disable this DHCPv6 server configuration.", "label": "Enable", "name": "enable"}]
VALID_BODY_RAPID_COMMIT: Literal[{"description": "Do not allow rapid commit", "help": "Do not allow rapid commit.", "label": "Disable", "name": "disable"}, {"description": "Allow rapid commit", "help": "Allow rapid commit.", "label": "Enable", "name": "enable"}]
VALID_BODY_DNS_SERVICE: Literal[{"description": "Delegated DNS settings", "help": "Delegated DNS settings.", "label": "Delegated", "name": "delegated"}, {"description": "Clients are assigned the FortiGate\u0027s configured DNS servers", "help": "Clients are assigned the FortiGate\u0027s configured DNS servers.", "label": "Default", "name": "default"}, {"description": "Specify up to 3 DNS servers in the DHCPv6 server configuration", "help": "Specify up to 3 DNS servers in the DHCPv6 server configuration.", "label": "Specify", "name": "specify"}]
VALID_BODY_DNS_SEARCH_LIST: Literal[{"description": "Delegated the DNS search list", "help": "Delegated the DNS search list.", "label": "Delegated", "name": "delegated"}, {"description": "Specify the DNS search list", "help": "Specify the DNS search list.", "label": "Specify", "name": "specify"}]
VALID_BODY_DELEGATED_PREFIX_ROUTE: Literal[{"description": "Disable automatically adding of routing for delegated prefix", "help": "Disable automatically adding of routing for delegated prefix.", "label": "Disable", "name": "disable"}, {"description": "Enable automatically adding of routing for delegated prefix", "help": "Enable automatically adding of routing for delegated prefix.", "label": "Enable", "name": "enable"}]
VALID_BODY_IP_MODE: Literal[{"description": "Use range defined by start IP/end IP to assign client IP", "help": "Use range defined by start IP/end IP to assign client IP.", "label": "Range", "name": "range"}, {"description": "Use delegated prefix method to assign client IP", "help": "Use delegated prefix method to assign client IP.", "label": "Delegated", "name": "delegated"}]
VALID_BODY_PREFIX_MODE: Literal[{"description": "Use delegated prefix from a DHCPv6 client", "help": "Use delegated prefix from a DHCPv6 client.", "label": "Dhcp6", "name": "dhcp6"}, {"description": "Use prefix from RA", "help": "Use prefix from RA.", "label": "Ra", "name": "ra"}]

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
    "VALID_BODY_RAPID_COMMIT",
    "VALID_BODY_DNS_SERVICE",
    "VALID_BODY_DNS_SEARCH_LIST",
    "VALID_BODY_DELEGATED_PREFIX_ROUTE",
    "VALID_BODY_IP_MODE",
    "VALID_BODY_PREFIX_MODE",
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