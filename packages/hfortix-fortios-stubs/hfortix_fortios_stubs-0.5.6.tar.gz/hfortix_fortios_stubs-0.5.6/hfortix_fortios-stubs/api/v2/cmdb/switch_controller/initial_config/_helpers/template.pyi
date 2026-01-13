from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_ALLOWACCESS: Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "FortiManager access", "help": "FortiManager access.", "label": "Fgfm", "name": "fgfm"}, {"description": "RADIUS accounting access", "help": "RADIUS accounting access.", "label": "Radius Acct", "name": "radius-acct"}, {"description": "Probe access", "help": "Probe access.", "label": "Probe Response", "name": "probe-response"}, {"description": "Security Fabric access", "help": "Security Fabric access.", "label": "Fabric", "name": "fabric"}, {"description": "FTM access", "help": "FTM access.", "label": "Ftm", "name": "ftm"}]
VALID_BODY_AUTO_IP: Literal[{"description": "Enable auto-ip status", "help": "Enable auto-ip status.", "label": "Enable", "name": "enable"}, {"description": "Disable auto-ip status", "help": "Disable auto-ip status.", "label": "Disable", "name": "disable"}]
VALID_BODY_DHCP_SERVER: Literal[{"description": "Enable DHCP server", "help": "Enable DHCP server.", "label": "Enable", "name": "enable"}, {"description": "Disable DHCP server", "help": "Disable DHCP server.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_ALLOWACCESS",
    "VALID_BODY_AUTO_IP",
    "VALID_BODY_DHCP_SERVER",
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