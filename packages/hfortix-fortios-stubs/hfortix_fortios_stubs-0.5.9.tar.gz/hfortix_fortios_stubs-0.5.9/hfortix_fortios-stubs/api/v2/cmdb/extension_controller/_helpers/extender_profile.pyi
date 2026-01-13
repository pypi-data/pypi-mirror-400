from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_MODEL: Literal[{"description": "FEX-201E model", "help": "FEX-201E model.", "label": "Fx201E", "name": "FX201E"}, {"description": "FEX-211E model", "help": "FEX-211E model.", "label": "Fx211E", "name": "FX211E"}, {"description": "FEX-200F model", "help": "FEX-200F model.", "label": "Fx200F", "name": "FX200F"}, {"description": "FEX-101F-AM model", "help": "FEX-101F-AM model.", "label": "Fxa11F", "name": "FXA11F"}, {"description": "FEX-101F-EA model", "help": "FEX-101F-EA model.", "label": "Fxe11F", "name": "FXE11F"}, {"description": "FEX-201F-AM model", "help": "FEX-201F-AM model.", "label": "Fxa21F", "name": "FXA21F"}, {"description": "FEX-201F-EA model", "help": "FEX-201F-EA model.", "label": "Fxe21F", "name": "FXE21F"}, {"description": "FEX-202F-AM model", "help": "FEX-202F-AM model.", "label": "Fxa22F", "name": "FXA22F"}, {"description": "FEX-202F-EA model", "help": "FEX-202F-EA model.", "label": "Fxe22F", "name": "FXE22F"}, {"description": "FEX-212F model", "help": "FEX-212F model.", "label": "Fx212F", "name": "FX212F"}, {"description": "FEX-311F model", "help": "FEX-311F model.", "label": "Fx311F", "name": "FX311F"}, {"description": "FEX-312F model", "help": "FEX-312F model.", "label": "Fx312F", "name": "FX312F"}, {"description": "FEX-511F model", "help": "FEX-511F model.", "label": "Fx511F", "name": "FX511F"}, {"description": "FER-511G model", "help": "FER-511G model.", "label": "Fxr51G", "name": "FXR51G"}, {"description": "FEX-511G model", "help": "FEX-511G model.", "label": "Fxn51G", "name": "FXN51G"}, {"description": "FEX-511G-Wifi model", "help": "FEX-511G-Wifi model.", "label": "Fxw51G", "name": "FXW51G"}, {"description": "FEV-211F model", "help": "FEV-211F model.", "label": "Fvg21F", "name": "FVG21F"}, {"description": "FEV-211F-AM model", "help": "FEV-211F-AM model.", "label": "Fva21F", "name": "FVA21F"}, {"description": "FEV-212F model", "help": "FEV-212F model.", "label": "Fvg22F", "name": "FVG22F"}, {"description": "FEV-212F-AM model", "help": "FEV-212F-AM model.", "label": "Fva22F", "name": "FVA22F"}, {"description": "FX40D-AMEU model", "help": "FX40D-AMEU model.", "label": "Fx04Da", "name": "FX04DA"}, {"description": "FG-CONNECTOR model", "help": "FG-CONNECTOR model.", "label": "Fg", "name": "FG"}, {"description": "FBS-10FW model", "help": "FBS-10FW model.", "label": "Bs10Fw", "name": "BS10FW"}, {"description": "FBS-20GW model", "help": "FBS-20GW model.", "label": "Bs20Gw", "name": "BS20GW"}, {"description": "FBS-20G model", "help": "FBS-20G model.", "label": "Bs20Gn", "name": "BS20GN"}, {"description": "FEV-511G model", "help": "FEV-511G model.", "label": "Fvg51G", "name": "FVG51G"}, {"description": "FEX-101G model", "help": "FEX-101G model.", "label": "Fxe11G", "name": "FXE11G"}, {"description": "FEX-211G model", "help": "FEX-211G model.", "label": "Fx211G", "name": "FX211G"}]
VALID_BODY_EXTENSION: Literal[{"description": "WAN extension", "help": "WAN extension.", "label": "Wan Extension", "name": "wan-extension"}, {"description": "LAN extension", "help": "LAN extension.", "label": "Lan Extension", "name": "lan-extension"}]
VALID_BODY_ALLOWACCESS: Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}]
VALID_BODY_LOGIN_PASSWORD_CHANGE: Literal[{"description": "Change the managed extender\u0027s administrator password", "help": "Change the managed extender\u0027s administrator password. Use the login-password option to set the password.", "label": "Yes", "name": "yes"}, {"description": "Keep the managed extender\u0027s administrator password set to the factory default", "help": "Keep the managed extender\u0027s administrator password set to the factory default.", "label": "Default", "name": "default"}, {"description": "Do not change the managed extender\u0027s administrator password", "help": "Do not change the managed extender\u0027s administrator password.", "label": "No", "name": "no"}]
VALID_BODY_ENFORCE_BANDWIDTH: Literal[{"description": "Enable to enforce bandwidth limit on LAN extension interface", "help": "Enable to enforce bandwidth limit on LAN extension interface.", "label": "Enable", "name": "enable"}, {"description": "Disable to enforce bandwidth limit on LAN extension interface", "help": "Disable to enforce bandwidth limit on LAN extension interface.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_MODEL",
    "VALID_BODY_EXTENSION",
    "VALID_BODY_ALLOWACCESS",
    "VALID_BODY_LOGIN_PASSWORD_CHANGE",
    "VALID_BODY_ENFORCE_BANDWIDTH",
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