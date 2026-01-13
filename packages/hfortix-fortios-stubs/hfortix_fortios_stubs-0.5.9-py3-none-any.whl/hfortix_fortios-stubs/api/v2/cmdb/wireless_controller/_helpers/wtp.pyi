from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_ADMIN: Literal[{"description": "FortiGate wireless controller discovers the WTP, AP, or FortiAP though discovery or join request messages", "help": "FortiGate wireless controller discovers the WTP, AP, or FortiAP though discovery or join request messages.", "label": "Discovered", "name": "discovered"}, {"description": "FortiGate wireless controller is configured to not provide service to this WTP", "help": "FortiGate wireless controller is configured to not provide service to this WTP.", "label": "Disable", "name": "disable"}, {"description": "FortiGate wireless controller is configured to provide service to this WTP", "help": "FortiGate wireless controller is configured to provide service to this WTP.", "label": "Enable", "name": "enable"}]
VALID_BODY_FIRMWARE_PROVISION_LATEST: Literal[{"description": "Do not automatically provision the latest available firmware", "help": "Do not automatically provision the latest available firmware.", "label": "Disable", "name": "disable"}, {"description": "Automatically attempt a one-time upgrade to the latest available firmware version", "help": "Automatically attempt a one-time upgrade to the latest available firmware version.", "label": "Once", "name": "once"}]
VALID_BODY_OVERRIDE_LED_STATE: Literal[{"description": "Override the WTP profile LED state", "help": "Override the WTP profile LED state.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile LED state", "help": "Use the WTP profile LED state.", "label": "Disable", "name": "disable"}]
VALID_BODY_LED_STATE: Literal[{"description": "Allow the LEDs on this FortiAP to light", "help": "Allow the LEDs on this FortiAP to light.", "label": "Enable", "name": "enable"}, {"description": "Keep the LEDs on this FortiAP off", "help": "Keep the LEDs on this FortiAP off.", "label": "Disable", "name": "disable"}]
VALID_BODY_OVERRIDE_WAN_PORT_MODE: Literal[{"description": "Override the WTP profile wan-port-mode", "help": "Override the WTP profile wan-port-mode.", "label": "Enable", "name": "enable"}, {"description": "Use the wan-port-mode in the WTP profile", "help": "Use the wan-port-mode in the WTP profile.", "label": "Disable", "name": "disable"}]
VALID_BODY_WAN_PORT_MODE: Literal[{"description": "Use the FortiAP WAN port as a LAN port", "help": "Use the FortiAP WAN port as a LAN port.", "label": "Wan Lan", "name": "wan-lan"}, {"description": "Do not use the WAN port as a LAN port", "help": "Do not use the WAN port as a LAN port.", "label": "Wan Only", "name": "wan-only"}]
VALID_BODY_OVERRIDE_IP_FRAGMENT: Literal[{"description": "Override the WTP profile IP fragment prevention setting", "help": "Override the WTP profile IP fragment prevention setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile IP fragment prevention setting", "help": "Use the WTP profile IP fragment prevention setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_IP_FRAGMENT_PREVENTING: Literal[{"description": "TCP maximum segment size adjustment", "help": "TCP maximum segment size adjustment.", "label": "Tcp Mss Adjust", "name": "tcp-mss-adjust"}, {"description": "Drop packet and send ICMP Destination Unreachable", "help": "Drop packet and send ICMP Destination Unreachable", "label": "Icmp Unreachable", "name": "icmp-unreachable"}]
VALID_BODY_OVERRIDE_SPLIT_TUNNEL: Literal[{"description": "Override the WTP profile split tunneling setting", "help": "Override the WTP profile split tunneling setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile split tunneling setting", "help": "Use the WTP profile split tunneling setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_SPLIT_TUNNELING_ACL_PATH: Literal[{"description": "Split tunneling ACL list traffic will be tunnel", "help": "Split tunneling ACL list traffic will be tunnel.", "label": "Tunnel", "name": "tunnel"}, {"description": "Split tunneling ACL list traffic will be local NATed", "help": "Split tunneling ACL list traffic will be local NATed.", "label": "Local", "name": "local"}]
VALID_BODY_SPLIT_TUNNELING_ACL_LOCAL_AP_SUBNET: Literal[{"description": "Enable automatically adding local subnetwork of FortiAP to split-tunneling ACL", "help": "Enable automatically adding local subnetwork of FortiAP to split-tunneling ACL.", "label": "Enable", "name": "enable"}, {"description": "Disable automatically adding local subnetwork of FortiAP to split-tunneling ACL", "help": "Disable automatically adding local subnetwork of FortiAP to split-tunneling ACL.", "label": "Disable", "name": "disable"}]
VALID_BODY_OVERRIDE_LAN: Literal[{"description": "Override the WTP profile LAN port setting", "help": "Override the WTP profile LAN port setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile LAN port setting", "help": "Use the WTP profile LAN port setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_OVERRIDE_ALLOWACCESS: Literal[{"description": "Override the WTP profile management access configuration", "help": "Override the WTP profile management access configuration.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile management access configuration", "help": "Use the WTP profile management access configuration.", "label": "Disable", "name": "disable"}]
VALID_BODY_ALLOWACCESS: Literal[{"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}]
VALID_BODY_OVERRIDE_LOGIN_PASSWD_CHANGE: Literal[{"description": "Override the WTP profile login-password (administrator password) setting", "help": "Override the WTP profile login-password (administrator password) setting.", "label": "Enable", "name": "enable"}, {"description": "Use the the WTP profile login-password (administrator password) setting", "help": "Use the the WTP profile login-password (administrator password) setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOGIN_PASSWD_CHANGE: Literal[{"description": "Change the managed WTP, FortiAP or AP\u0027s administrator password", "help": "Change the managed WTP, FortiAP or AP\u0027s administrator password. Use the login-password option to set the password.", "label": "Yes", "name": "yes"}, {"description": "Keep the managed WTP, FortiAP or AP\u0027s administrator password set to the factory default", "help": "Keep the managed WTP, FortiAP or AP\u0027s administrator password set to the factory default.", "label": "Default", "name": "default"}, {"description": "Do not change the managed WTP, FortiAP or AP\u0027s administrator password", "help": "Do not change the managed WTP, FortiAP or AP\u0027s administrator password.", "label": "No", "name": "no"}]
VALID_BODY_OVERRIDE_DEFAULT_MESH_ROOT: Literal[{"description": "Override the WTP profile default mesh root SSID setting", "help": "Override the WTP profile default mesh root SSID setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile default mesh root SSID setting", "help": "Use the WTP profile default mesh root SSID setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_DEFAULT_MESH_ROOT: Literal[{"description": "Enable default mesh root SSID if it is not included by radio\u0027s SSID configuration", "help": "Enable default mesh root SSID if it is not included by radio\u0027s SSID configuration.", "label": "Enable", "name": "enable"}, {"description": "Do not enable default mesh root SSID if it is not included by radio\u0027s SSID configuration", "help": "Do not enable default mesh root SSID if it is not included by radio\u0027s SSID configuration.", "label": "Disable", "name": "disable"}]
VALID_BODY_IMAGE_DOWNLOAD: Literal[{"description": "Enable WTP image download at join time", "help": "Enable WTP image download at join time.", "label": "Enable", "name": "enable"}, {"description": "Disable WTP image download at join time", "help": "Disable WTP image download at join time.", "label": "Disable", "name": "disable"}]
VALID_BODY_MESH_BRIDGE_ENABLE: Literal[{"description": "Use mesh Ethernet bridge local setting on the WTP", "help": "Use mesh Ethernet bridge local setting on the WTP.", "label": "Default", "name": "default"}, {"description": "Turn on mesh Ethernet bridge on the WTP", "help": "Turn on mesh Ethernet bridge on the WTP.", "label": "Enable", "name": "enable"}, {"description": "Turn off mesh Ethernet bridge on the WTP", "help": "Turn off mesh Ethernet bridge on the WTP.", "label": "Disable", "name": "disable"}]
VALID_BODY_PURDUE_LEVEL: Literal[{"description": "Level 1 - Basic Control    1", "help": "Level 1 - Basic Control", "label": "1", "name": "1"}, {"help": "Level 1.5", "label": "1.5", "name": "1.5"}, {"help": "Level 2 - Area Supervisory Control", "label": "2", "name": "2"}, {"help": "Level 2.5", "label": "2.5", "name": "2.5"}, {"help": "Level 3 - Operations \u0026 Control", "label": "3", "name": "3"}, {"help": "Level 3.5", "label": "3.5", "name": "3.5"}, {"help": "Level 4 - Business Planning \u0026 Logistics", "label": "4", "name": "4"}, {"description": "Level 5", "help": "Level 5 - Enterprise Network", "label": "5", "name": "5"}, {"help": "Level 5.5", "label": "5.5", "name": "5.5"}]

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
    "VALID_BODY_ADMIN",
    "VALID_BODY_FIRMWARE_PROVISION_LATEST",
    "VALID_BODY_OVERRIDE_LED_STATE",
    "VALID_BODY_LED_STATE",
    "VALID_BODY_OVERRIDE_WAN_PORT_MODE",
    "VALID_BODY_WAN_PORT_MODE",
    "VALID_BODY_OVERRIDE_IP_FRAGMENT",
    "VALID_BODY_IP_FRAGMENT_PREVENTING",
    "VALID_BODY_OVERRIDE_SPLIT_TUNNEL",
    "VALID_BODY_SPLIT_TUNNELING_ACL_PATH",
    "VALID_BODY_SPLIT_TUNNELING_ACL_LOCAL_AP_SUBNET",
    "VALID_BODY_OVERRIDE_LAN",
    "VALID_BODY_OVERRIDE_ALLOWACCESS",
    "VALID_BODY_ALLOWACCESS",
    "VALID_BODY_OVERRIDE_LOGIN_PASSWD_CHANGE",
    "VALID_BODY_LOGIN_PASSWD_CHANGE",
    "VALID_BODY_OVERRIDE_DEFAULT_MESH_ROOT",
    "VALID_BODY_DEFAULT_MESH_ROOT",
    "VALID_BODY_IMAGE_DOWNLOAD",
    "VALID_BODY_MESH_BRIDGE_ENABLE",
    "VALID_BODY_PURDUE_LEVEL",
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