from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_AUTHORIZED: Literal[{"description": "Controller discovered this FortiExtender", "help": "Controller discovered this FortiExtender.", "label": "Discovered", "name": "discovered"}, {"description": "Controller is configured to not provide service to this FortiExtender", "help": "Controller is configured to not provide service to this FortiExtender.", "label": "Disable", "name": "disable"}, {"description": "Controller is configured to provide service to this FortiExtender", "help": "Controller is configured to provide service to this FortiExtender.", "label": "Enable", "name": "enable"}]
VALID_BODY_EXTENSION_TYPE: Literal[{"description": "FortiExtender WAN extension mode", "help": "FortiExtender WAN extension mode.", "label": "Wan Extension", "name": "wan-extension"}, {"description": "FortiExtender LAN extension mode", "help": "FortiExtender LAN extension mode.", "label": "Lan Extension", "name": "lan-extension"}]
VALID_BODY_OVERRIDE_ALLOWACCESS: Literal[{"description": "Override the extender profile management access configuration", "help": "Override the extender profile management access configuration.", "label": "Enable", "name": "enable"}, {"description": "Use the extender profile management access configuration", "help": "Use the extender profile management access configuration.", "label": "Disable", "name": "disable"}]
VALID_BODY_ALLOWACCESS: Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}]
VALID_BODY_OVERRIDE_LOGIN_PASSWORD_CHANGE: Literal[{"description": "Override the WTP profile login-password (administrator password) setting", "help": "Override the WTP profile login-password (administrator password) setting.", "label": "Enable", "name": "enable"}, {"description": "Use the the WTP profile login-password (administrator password) setting", "help": "Use the the WTP profile login-password (administrator password) setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOGIN_PASSWORD_CHANGE: Literal[{"description": "Change the managed extender\u0027s administrator password", "help": "Change the managed extender\u0027s administrator password. Use the login-password option to set the password.", "label": "Yes", "name": "yes"}, {"description": "Keep the managed extender\u0027s administrator password set to the factory default", "help": "Keep the managed extender\u0027s administrator password set to the factory default.", "label": "Default", "name": "default"}, {"description": "Do not change the managed extender\u0027s administrator password", "help": "Do not change the managed extender\u0027s administrator password.", "label": "No", "name": "no"}]
VALID_BODY_OVERRIDE_ENFORCE_BANDWIDTH: Literal[{"description": "Enable override of FortiExtender profile bandwidth setting", "help": "Enable override of FortiExtender profile bandwidth setting.", "label": "Enable", "name": "enable"}, {"description": "Disable override of FortiExtender profile bandwidth setting", "help": "Disable override of FortiExtender profile bandwidth setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_ENFORCE_BANDWIDTH: Literal[{"description": "Enable to enforce bandwidth limit on LAN extension interface", "help": "Enable to enforce bandwidth limit on LAN extension interface.", "label": "Enable", "name": "enable"}, {"description": "Disable to enforce bandwidth limit on LAN extension interface", "help": "Disable to enforce bandwidth limit on LAN extension interface.", "label": "Disable", "name": "disable"}]
VALID_BODY_FIRMWARE_PROVISION_LATEST: Literal[{"description": "Do not automatically provision the latest available firmware", "help": "Do not automatically provision the latest available firmware.", "label": "Disable", "name": "disable"}, {"description": "Automatically attempt a one-time upgrade to the latest available firmware version", "help": "Automatically attempt a one-time upgrade to the latest available firmware version.", "label": "Once", "name": "once"}]

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
    "VALID_BODY_AUTHORIZED",
    "VALID_BODY_EXTENSION_TYPE",
    "VALID_BODY_OVERRIDE_ALLOWACCESS",
    "VALID_BODY_ALLOWACCESS",
    "VALID_BODY_OVERRIDE_LOGIN_PASSWORD_CHANGE",
    "VALID_BODY_LOGIN_PASSWORD_CHANGE",
    "VALID_BODY_OVERRIDE_ENFORCE_BANDWIDTH",
    "VALID_BODY_ENFORCE_BANDWIDTH",
    "VALID_BODY_FIRMWARE_PROVISION_LATEST",
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