from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Do not use this DHCP server configuration", "help": "Do not use this DHCP server configuration.", "label": "Disable", "name": "disable"}, {"description": "Use this DHCP server configuration", "help": "Use this DHCP server configuration.", "label": "Enable", "name": "enable"}]
VALID_BODY_MAC_ACL_DEFAULT_ACTION: Literal[{"description": "Allow the DHCP server to assign IP settings to clients on the MAC access control list", "help": "Allow the DHCP server to assign IP settings to clients on the MAC access control list.", "label": "Assign", "name": "assign"}, {"description": "Block the DHCP server from assigning IP settings to clients on the MAC access control list", "help": "Block the DHCP server from assigning IP settings to clients on the MAC access control list.", "label": "Block", "name": "block"}]
VALID_BODY_FORTICLIENT_ON_NET_STATUS: Literal[{"description": "Disable FortiClient On-Net Status", "help": "Disable FortiClient On-Net Status.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiClient On-Net Status", "help": "Enable FortiClient On-Net Status.", "label": "Enable", "name": "enable"}]
VALID_BODY_DNS_SERVICE: Literal[{"description": "IP address of the interface the DHCP server is added to becomes the client\u0027s DNS server IP address", "help": "IP address of the interface the DHCP server is added to becomes the client\u0027s DNS server IP address.", "label": "Local", "name": "local"}, {"description": "Clients are assigned the FortiGate\u0027s configured DNS servers", "help": "Clients are assigned the FortiGate\u0027s configured DNS servers.", "label": "Default", "name": "default"}, {"description": "Specify up to 3 DNS servers in the DHCP server configuration", "help": "Specify up to 3 DNS servers in the DHCP server configuration.", "label": "Specify", "name": "specify"}]
VALID_BODY_WIFI_AC_SERVICE: Literal[{"description": "Specify up to 3 WiFi Access Controllers in the DHCP server configuration", "help": "Specify up to 3 WiFi Access Controllers in the DHCP server configuration.", "label": "Specify", "name": "specify"}, {"description": "IP address of the interface the DHCP server is added to becomes the client\u0027s WiFi Access Controller IP address", "help": "IP address of the interface the DHCP server is added to becomes the client\u0027s WiFi Access Controller IP address.", "label": "Local", "name": "local"}]
VALID_BODY_NTP_SERVICE: Literal[{"description": "IP address of the interface the DHCP server is added to becomes the client\u0027s NTP server IP address", "help": "IP address of the interface the DHCP server is added to becomes the client\u0027s NTP server IP address.", "label": "Local", "name": "local"}, {"description": "Clients are assigned the FortiGate\u0027s configured NTP servers", "help": "Clients are assigned the FortiGate\u0027s configured NTP servers.", "label": "Default", "name": "default"}, {"description": "Specify up to 3 NTP servers in the DHCP server configuration", "help": "Specify up to 3 NTP servers in the DHCP server configuration.", "label": "Specify", "name": "specify"}]
VALID_BODY_TIMEZONE_OPTION: Literal[{"description": "Do not set the client\u0027s time zone", "help": "Do not set the client\u0027s time zone.", "label": "Disable", "name": "disable"}, {"description": "Clients are assigned the FortiGate\u0027s configured time zone", "help": "Clients are assigned the FortiGate\u0027s configured time zone.", "label": "Default", "name": "default"}, {"description": "Specify the time zone to be assigned to DHCP clients", "help": "Specify the time zone to be assigned to DHCP clients.", "label": "Specify", "name": "specify"}]
VALID_BODY_SERVER_TYPE: Literal[{"description": "Regular DHCP service", "help": "Regular DHCP service.", "label": "Regular", "name": "regular"}, {"description": "DHCP over IPsec service", "help": "DHCP over IPsec service.", "label": "Ipsec", "name": "ipsec"}]
VALID_BODY_IP_MODE: Literal[{"description": "Use range defined by start-ip/end-ip to assign client IP", "help": "Use range defined by start-ip/end-ip to assign client IP.", "label": "Range", "name": "range"}, {"description": "Use user-group defined method to assign client IP", "help": "Use user-group defined method to assign client IP.", "label": "Usrgrp", "name": "usrgrp"}]
VALID_BODY_AUTO_CONFIGURATION: Literal[{"description": "Disable auto configuration", "help": "Disable auto configuration.", "label": "Disable", "name": "disable"}, {"description": "Enable auto configuration", "help": "Enable auto configuration.", "label": "Enable", "name": "enable"}]
VALID_BODY_DHCP_SETTINGS_FROM_FORTIIPAM: Literal[{"description": "Disable populating of DHCP server settings from FortiIPAM", "help": "Disable populating of DHCP server settings from FortiIPAM.", "label": "Disable", "name": "disable"}, {"description": "Enable populating of DHCP server settings from FortiIPAM", "help": "Enable populating of DHCP server settings from FortiIPAM.", "label": "Enable", "name": "enable"}]
VALID_BODY_AUTO_MANAGED_STATUS: Literal[{"description": "Disable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM", "help": "Disable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM.", "label": "Disable", "name": "disable"}, {"description": "Enable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM", "help": "Enable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM.", "label": "Enable", "name": "enable"}]
VALID_BODY_DDNS_UPDATE: Literal[{"description": "Disable DDNS update for DHCP", "help": "Disable DDNS update for DHCP.", "label": "Disable", "name": "disable"}, {"description": "Enable DDNS update for DHCP", "help": "Enable DDNS update for DHCP.", "label": "Enable", "name": "enable"}]
VALID_BODY_DDNS_UPDATE_OVERRIDE: Literal[{"description": "Disable DDNS update override for DHCP", "help": "Disable DDNS update override for DHCP.", "label": "Disable", "name": "disable"}, {"description": "Enable DDNS update override for DHCP", "help": "Enable DDNS update override for DHCP.", "label": "Enable", "name": "enable"}]
VALID_BODY_DDNS_AUTH: Literal[{"description": "Disable DDNS authentication", "help": "Disable DDNS authentication.", "label": "Disable", "name": "disable"}, {"description": "TSIG based on RFC2845", "help": "TSIG based on RFC2845.", "label": "Tsig", "name": "tsig"}]
VALID_BODY_VCI_MATCH: Literal[{"description": "Disable VCI matching", "help": "Disable VCI matching.", "label": "Disable", "name": "disable"}, {"description": "Enable VCI matching", "help": "Enable VCI matching.", "label": "Enable", "name": "enable"}]
VALID_BODY_SHARED_SUBNET: Literal[{"description": "Disable shared subnet", "help": "Disable shared subnet.", "label": "Disable", "name": "disable"}, {"description": "Enable shared subnet", "help": "Enable shared subnet.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_MAC_ACL_DEFAULT_ACTION",
    "VALID_BODY_FORTICLIENT_ON_NET_STATUS",
    "VALID_BODY_DNS_SERVICE",
    "VALID_BODY_WIFI_AC_SERVICE",
    "VALID_BODY_NTP_SERVICE",
    "VALID_BODY_TIMEZONE_OPTION",
    "VALID_BODY_SERVER_TYPE",
    "VALID_BODY_IP_MODE",
    "VALID_BODY_AUTO_CONFIGURATION",
    "VALID_BODY_DHCP_SETTINGS_FROM_FORTIIPAM",
    "VALID_BODY_AUTO_MANAGED_STATUS",
    "VALID_BODY_DDNS_UPDATE",
    "VALID_BODY_DDNS_UPDATE_OVERRIDE",
    "VALID_BODY_DDNS_AUTH",
    "VALID_BODY_VCI_MATCH",
    "VALID_BODY_SHARED_SUBNET",
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