from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_PURDUE_LEVEL: Literal[{"description": "Level 1 - Basic Control    1", "help": "Level 1 - Basic Control", "label": "1", "name": "1"}, {"help": "Level 1.5", "label": "1.5", "name": "1.5"}, {"help": "Level 2 - Area Supervisory Control", "label": "2", "name": "2"}, {"help": "Level 2.5", "label": "2.5", "name": "2.5"}, {"help": "Level 3 - Operations \u0026 Control", "label": "3", "name": "3"}, {"help": "Level 3.5", "label": "3.5", "name": "3.5"}, {"help": "Level 4 - Business Planning \u0026 Logistics", "label": "4", "name": "4"}, {"description": "Level 5", "help": "Level 5 - Enterprise Network", "label": "5", "name": "5"}, {"help": "Level 5.5", "label": "5.5", "name": "5.5"}]
VALID_BODY_FSW_WAN1_ADMIN: Literal[{"description": "Link waiting to be authorized", "help": "Link waiting to be authorized.", "label": "Discovered", "name": "discovered"}, {"description": "Link unauthorized", "help": "Link unauthorized.", "label": "Disable", "name": "disable"}, {"description": "Link authorized", "help": "Link authorized.", "label": "Enable", "name": "enable"}]
VALID_BODY_POE_PRE_STANDARD_DETECTION: Literal[{"description": "Enable PoE pre-standard detection", "help": "Enable PoE pre-standard detection.", "label": "Enable", "name": "enable"}, {"description": "Disable PoE pre-standard detection", "help": "Disable PoE pre-standard detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_DHCP_SERVER_ACCESS_LIST: Literal[{"description": "Use global setting for DHCP snooping server access list", "help": "Use global setting for DHCP snooping server access list.", "label": "Global", "name": "global"}, {"description": "Override global setting and enable DHCP server access list", "help": "Override global setting and enable DHCP server access list.", "label": "Enable", "name": "enable"}, {"description": "Override global setting and disable DHCP server access list", "help": "Override global setting and disable DHCP server access list.", "label": "Disable", "name": "disable"}]
VALID_BODY_MCLAG_IGMP_SNOOPING_AWARE: Literal[{"description": "Enable MCLAG IGMP-snooping awareness", "help": "Enable MCLAG IGMP-snooping awareness.", "label": "Enable", "name": "enable"}, {"description": "Disable MCLAG IGMP-snooping awareness", "help": "Disable MCLAG IGMP-snooping awareness.", "label": "Disable", "name": "disable"}]
VALID_BODY_PTP_STATUS: Literal[{"description": "Disable PTP profile", "help": "Disable PTP profile.", "label": "Disable", "name": "disable"}, {"description": "Enable PTP profile", "help": "Enable PTP profile.", "label": "Enable", "name": "enable"}]
VALID_BODY_RADIUS_NAS_IP_OVERRIDE: Literal[{"description": "Disable radius-nas-ip-override", "help": "Disable radius-nas-ip-override.", "label": "Disable", "name": "disable"}, {"description": "Enable radius-nas-ip-override", "help": "Enable radius-nas-ip-override.", "label": "Enable", "name": "enable"}]
VALID_BODY_ROUTE_OFFLOAD: Literal[{"description": "Disable route offload", "help": "Disable route offload.", "label": "Disable", "name": "disable"}, {"description": "Enable route offload", "help": "Enable route offload.", "label": "Enable", "name": "enable"}]
VALID_BODY_ROUTE_OFFLOAD_MCLAG: Literal[{"description": "Disable route offload MCLAG", "help": "Disable route offload MCLAG.", "label": "Disable", "name": "disable"}, {"description": "Enable route offload MCLAG", "help": "Enable route offload MCLAG.", "label": "Enable", "name": "enable"}]
VALID_BODY_TYPE: Literal[{"description": "Switch is of type virtual", "help": "Switch is of type virtual.", "label": "Virtual", "name": "virtual"}, {"description": "Switch is of type physical", "help": "Switch is of type physical.", "label": "Physical", "name": "physical"}]
VALID_BODY_FIRMWARE_PROVISION: Literal[{"description": "Enable firmware-provision", "help": "Enable firmware-provision.", "label": "Enable", "name": "enable"}, {"description": "Disable firmware-provision", "help": "Disable firmware-provision.", "label": "Disable", "name": "disable"}]
VALID_BODY_FIRMWARE_PROVISION_LATEST: Literal[{"description": "Do not automatically provision the latest available firmware", "help": "Do not automatically provision the latest available firmware.", "label": "Disable", "name": "disable"}, {"description": "Automatically attempt a one-time upgrade to the latest available firmware version", "help": "Automatically attempt a one-time upgrade to the latest available firmware version.", "label": "Once", "name": "once"}]
VALID_BODY_OVERRIDE_SNMP_SYSINFO: Literal[{"description": "Use the global SNMP system information", "help": "Use the global SNMP system information.", "label": "Disable", "name": "disable"}, {"description": "Override the global SNMP system information", "help": "Override the global SNMP system information.", "label": "Enable", "name": "enable"}]
VALID_BODY_OVERRIDE_SNMP_TRAP_THRESHOLD: Literal[{"description": "Override the global SNMP trap threshold values", "help": "Override the global SNMP trap threshold values.", "label": "Enable", "name": "enable"}, {"description": "Use the global SNMP trap threshold values", "help": "Use the global SNMP trap threshold values.", "label": "Disable", "name": "disable"}]
VALID_BODY_OVERRIDE_SNMP_COMMUNITY: Literal[{"description": "Override the global SNMP communities", "help": "Override the global SNMP communities.", "label": "Enable", "name": "enable"}, {"description": "Use the global SNMP communities", "help": "Use the global SNMP communities.", "label": "Disable", "name": "disable"}]
VALID_BODY_OVERRIDE_SNMP_USER: Literal[{"description": "Override the global SNMPv3 users", "help": "Override the global SNMPv3 users.", "label": "Enable", "name": "enable"}, {"description": "Use the global SNMPv3 users", "help": "Use the global SNMPv3 users.", "label": "Disable", "name": "disable"}]
VALID_BODY_QOS_DROP_POLICY: Literal[{"description": "Taildrop policy", "help": "Taildrop policy.", "label": "Taildrop", "name": "taildrop"}, {"description": "Random early detection drop policy", "help": "Random early detection drop policy.", "label": "Random Early Detection", "name": "random-early-detection"}]

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
    "VALID_BODY_PURDUE_LEVEL",
    "VALID_BODY_FSW_WAN1_ADMIN",
    "VALID_BODY_POE_PRE_STANDARD_DETECTION",
    "VALID_BODY_DHCP_SERVER_ACCESS_LIST",
    "VALID_BODY_MCLAG_IGMP_SNOOPING_AWARE",
    "VALID_BODY_PTP_STATUS",
    "VALID_BODY_RADIUS_NAS_IP_OVERRIDE",
    "VALID_BODY_ROUTE_OFFLOAD",
    "VALID_BODY_ROUTE_OFFLOAD_MCLAG",
    "VALID_BODY_TYPE",
    "VALID_BODY_FIRMWARE_PROVISION",
    "VALID_BODY_FIRMWARE_PROVISION_LATEST",
    "VALID_BODY_OVERRIDE_SNMP_SYSINFO",
    "VALID_BODY_OVERRIDE_SNMP_TRAP_THRESHOLD",
    "VALID_BODY_OVERRIDE_SNMP_COMMUNITY",
    "VALID_BODY_OVERRIDE_SNMP_USER",
    "VALID_BODY_QOS_DROP_POLICY",
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