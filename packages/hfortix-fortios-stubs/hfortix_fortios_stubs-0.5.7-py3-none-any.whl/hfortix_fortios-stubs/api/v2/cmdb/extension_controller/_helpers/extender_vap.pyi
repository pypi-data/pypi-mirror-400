from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"description": "Local VAP", "help": "Local VAP.", "label": "Local Vap", "name": "local-vap"}, {"description": "Lan Extension VAP", "help": "Lan Extension VAP.", "label": "Lan Ext Vap", "name": "lan-ext-vap"}]
VALID_BODY_BROADCAST_SSID: Literal[{"description": "Disable broadcast SSID", "help": "Disable broadcast SSID.", "label": "Disable", "name": "disable"}, {"description": "Enable broadcast SSID", "help": "Enable broadcast SSID.", "label": "Enable", "name": "enable"}]
VALID_BODY_SECURITY: Literal[{"description": "Wi-Fi security OPEN    WPA2-Personal:Wi-Fi security WPA2 Personal    WPA-WPA2-Personal:Wi-Fi security WPA-WPA2 Personal    WPA3-SAE:Wi-Fi security WPA3 SAE    WPA3-SAE-Transition:Wi-Fi security WPA3 SAE Transition    WPA2-Enterprise:Wi-Fi security WPA2 Enterprise    WPA3-Enterprise-only:Wi-Fi security WPA3 Enterprise only    WPA3-Enterprise-transition:Wi-Fi security WPA3 Enterprise Transition    WPA3-Enterprise-192-bit:Wi-Fi security WPA3 Enterprise 192-bit", "help": "Wi-Fi security OPEN", "label": "Open", "name": "OPEN"}, {"help": "Wi-Fi security WPA2 Personal", "label": "Wpa2 Personal", "name": "WPA2-Personal"}, {"help": "Wi-Fi security WPA-WPA2 Personal", "label": "Wpa Wpa2 Personal", "name": "WPA-WPA2-Personal"}, {"help": "Wi-Fi security WPA3 SAE", "label": "Wpa3 Sae", "name": "WPA3-SAE"}, {"help": "Wi-Fi security WPA3 SAE Transition", "label": "Wpa3 Sae Transition", "name": "WPA3-SAE-Transition"}, {"help": "Wi-Fi security WPA2 Enterprise", "label": "Wpa2 Enterprise", "name": "WPA2-Enterprise"}, {"help": "Wi-Fi security WPA3 Enterprise only", "label": "Wpa3 Enterprise Only", "name": "WPA3-Enterprise-only"}, {"help": "Wi-Fi security WPA3 Enterprise Transition", "label": "Wpa3 Enterprise Transition", "name": "WPA3-Enterprise-transition"}, {"help": "Wi-Fi security WPA3 Enterprise 192-bit", "label": "Wpa3 Enterprise 192 Bit", "name": "WPA3-Enterprise-192-bit"}]
VALID_BODY_PMF: Literal[{"description": "Disable PMF (Protected Management Frames)", "help": "Disable PMF (Protected Management Frames).", "label": "Disabled", "name": "disabled"}, {"description": "Set PMF (Protected Management Frames) optional", "help": "Set PMF (Protected Management Frames) optional.", "label": "Optional", "name": "optional"}, {"description": "Require PMF (Protected Management Frames)", "help": "Require PMF (Protected Management Frames).", "label": "Required", "name": "required"}]
VALID_BODY_TARGET_WAKE_TIME: Literal[{"description": "Disable target wake time", "help": "Disable target wake time.", "label": "Disable", "name": "disable"}, {"description": "Enable target wake time", "help": "Enable target wake time.", "label": "Enable", "name": "enable"}]
VALID_BODY_BSS_COLOR_PARTIAL: Literal[{"description": "Disable bss color partial", "help": "Disable bss color partial.", "label": "Disable", "name": "disable"}, {"description": "Enable bss color partial", "help": "Enable bss color partial.", "label": "Enable", "name": "enable"}]
VALID_BODY_MU_MIMO: Literal[{"description": "Disable multi-user MIMO", "help": "Disable multi-user MIMO.", "label": "Disable", "name": "disable"}, {"description": "Enable multi-user MIMO", "help": "Enable multi-user MIMO.", "label": "Enable", "name": "enable"}]
VALID_BODY_ALLOWACCESS: Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}]

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
    "VALID_BODY_BROADCAST_SSID",
    "VALID_BODY_SECURITY",
    "VALID_BODY_PMF",
    "VALID_BODY_TARGET_WAKE_TIME",
    "VALID_BODY_BSS_COLOR_PARTIAL",
    "VALID_BODY_MU_MIMO",
    "VALID_BODY_ALLOWACCESS",
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