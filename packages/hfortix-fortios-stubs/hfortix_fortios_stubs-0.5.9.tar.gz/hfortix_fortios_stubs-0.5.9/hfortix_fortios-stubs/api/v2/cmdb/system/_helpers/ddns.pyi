from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_DDNS_SERVER: Literal[{"help": "members.dyndns.org and dnsalias.com", "label": "Dyndns.Org", "name": "dyndns.org"}, {"help": "www.dyns.net", "label": "Dyns.Net", "name": "dyns.net"}, {"help": "rh.tzo.com", "label": "Tzo.Com", "name": "tzo.com"}, {"help": "Peanut Hull", "label": "Vavic.Com", "name": "vavic.com"}, {"help": "dipdnsserver.dipdns.com", "label": "Dipdns.Net", "name": "dipdns.net"}, {"help": "ip.todayisp.com", "label": "Now.Net.Cn", "name": "now.net.cn"}, {"help": "members.dhs.org", "label": "Dhs.Org", "name": "dhs.org"}, {"help": "members.easydns.com", "label": "Easydns.Com", "name": "easydns.com"}, {"help": "Generic DDNS based on RFC2136.", "label": "Genericddns", "name": "genericDDNS"}, {"description": "FortiGuard DDNS service", "help": "FortiGuard DDNS service.", "label": "Fortiguardddns", "name": "FortiGuardDDNS"}, {"help": "dynupdate.no-ip.com", "label": "Noip.Com", "name": "noip.com"}]
VALID_BODY_ADDR_TYPE: Literal[{"description": "Use IPv4 address of the interface", "help": "Use IPv4 address of the interface.", "label": "Ipv4", "name": "ipv4"}, {"description": "Use IPv6 address of the interface", "help": "Use IPv6 address of the interface.", "label": "Ipv6", "name": "ipv6"}]
VALID_BODY_SERVER_TYPE: Literal[{"description": "Use IPv4 addressing", "help": "Use IPv4 addressing.", "label": "Ipv4", "name": "ipv4"}, {"description": "Use IPv6 addressing", "help": "Use IPv6 addressing.", "label": "Ipv6", "name": "ipv6"}]
VALID_BODY_DDNS_AUTH: Literal[{"description": "Disable DDNS authentication", "help": "Disable DDNS authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable TSIG authentication based on RFC2845", "help": "Enable TSIG authentication based on RFC2845.", "label": "Tsig", "name": "tsig"}]
VALID_BODY_USE_PUBLIC_IP: Literal[{"description": "Disable use of public IP address", "help": "Disable use of public IP address.", "label": "Disable", "name": "disable"}, {"description": "Enable use of public IP address", "help": "Enable use of public IP address.", "label": "Enable", "name": "enable"}]
VALID_BODY_CLEAR_TEXT: Literal[{"description": "Disable use of clear text connections", "help": "Disable use of clear text connections.", "label": "Disable", "name": "disable"}, {"description": "Enable use of clear text connections", "help": "Enable use of clear text connections.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_DDNS_SERVER",
    "VALID_BODY_ADDR_TYPE",
    "VALID_BODY_SERVER_TYPE",
    "VALID_BODY_DDNS_AUTH",
    "VALID_BODY_USE_PUBLIC_IP",
    "VALID_BODY_CLEAR_TEXT",
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