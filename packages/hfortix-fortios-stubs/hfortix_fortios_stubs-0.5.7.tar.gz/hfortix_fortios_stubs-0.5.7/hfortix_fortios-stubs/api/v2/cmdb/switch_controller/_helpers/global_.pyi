from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_HTTPS_IMAGE_PUSH: Literal[{"description": "Enable image push to FortiSwitch using HTTPS", "help": "Enable image push to FortiSwitch using HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable image push to FortiSwitch using HTTPS", "help": "Disable image push to FortiSwitch using HTTPS.", "label": "Disable", "name": "disable"}]
VALID_BODY_VLAN_ALL_MODE: Literal[{"description": "Include all possible VLANs (1-4093)", "help": "Include all possible VLANs (1-4093).", "label": "All", "name": "all"}, {"description": "Include user defined VLANs", "help": "Include user defined VLANs.", "label": "Defined", "name": "defined"}]
VALID_BODY_VLAN_OPTIMIZATION: Literal[{"description": "Enable VLAN optimization (only VLANs necessary on or along path between destinations) on FortiSwitch units for auto-generated trunks", "help": "Enable VLAN optimization (only VLANs necessary on or along path between destinations) on FortiSwitch units for auto-generated trunks.", "label": "Prune", "name": "prune"}, {"description": "Enable VLAN optimization (only VLANs created on Fortilink interface) on FortiSwitch units for auto-generated trunks", "help": "Enable VLAN optimization (only VLANs created on Fortilink interface) on FortiSwitch units for auto-generated trunks.", "label": "Configured", "name": "configured"}, {"description": "Disable VLAN optimization on FortiSwitch units for auto-generated trunks", "help": "Disable VLAN optimization on FortiSwitch units for auto-generated trunks.", "label": "None", "name": "none"}]
VALID_BODY_VLAN_IDENTITY: Literal[{"description": "Configure the VLAN description to that of the FortiOS interface description if available; otherwise use the interface name", "help": "Configure the VLAN description to that of the FortiOS interface description if available; otherwise use the interface name.", "label": "Description", "name": "description"}, {"description": "Configure the VLAN description to that of the FortiOS interface name", "help": "Configure the VLAN description to that of the FortiOS interface name.", "label": "Name", "name": "name"}]
VALID_BODY_DHCP_SERVER_ACCESS_LIST: Literal[{"description": "Enable DHCP server access list", "help": "Enable DHCP server access list.", "label": "Enable", "name": "enable"}, {"description": "Disable DHCP server access list", "help": "Disable DHCP server access list.", "label": "Disable", "name": "disable"}]
VALID_BODY_DHCP_OPTION82_FORMAT: Literal[{"description": "Allow user to choose values for circuit-id and remote-id", "help": "Allow user to choose values for circuit-id and remote-id.\n\t  Format:  cid= [hostname,interface,mode,vlan,description] rid=[hostname,xx:xx:xx:xx:xx:xx,ip]\n", "label": "Ascii", "name": "ascii"}, {"help": "Generate predefine fixed format for circuit-id and remote.\n\tFormat: cid=hostname-[\u003cvlan:16\u003e\u003cmod:8\u003e\u003cport:8\u003e].32bit, rid= [mac(0..6)].48bit\n", "label": "Legacy", "name": "legacy"}]
VALID_BODY_DHCP_OPTION82_CIRCUIT_ID: Literal[{"description": "Interface name", "help": "Interface name.", "label": "Intfname", "name": "intfname"}, {"description": "VLAN name", "help": "VLAN name.", "label": "Vlan", "name": "vlan"}, {"description": "Hostname", "help": "Hostname.", "label": "Hostname", "name": "hostname"}, {"description": "Mode", "help": "Mode.", "label": "Mode", "name": "mode"}, {"description": "Description", "help": "Description.", "label": "Description", "name": "description"}]
VALID_BODY_DHCP_OPTION82_REMOTE_ID: Literal[{"description": "MAC address", "help": "MAC address.", "label": "Mac", "name": "mac"}, {"description": "Hostname", "help": "Hostname.", "label": "Hostname", "name": "hostname"}, {"description": "IP address", "help": "IP address.", "label": "Ip", "name": "ip"}]
VALID_BODY_DHCP_SNOOP_CLIENT_REQ: Literal[{"description": "Broadcast packets on trusted ports in the VLAN", "help": "Broadcast packets on trusted ports in the VLAN.", "label": "Drop Untrusted", "name": "drop-untrusted"}, {"description": "Broadcast packets on all ports in the VLAN", "help": "Broadcast packets on all ports in the VLAN.", "label": "Forward Untrusted", "name": "forward-untrusted"}]
VALID_BODY_LOG_MAC_LIMIT_VIOLATIONS: Literal[{"description": "Enable Learn Limit Violation", "help": "Enable Learn Limit Violation.", "label": "Enable", "name": "enable"}, {"description": "Disable Learn Limit Violation", "help": "Disable Learn Limit Violation.", "label": "Disable", "name": "disable"}]
VALID_BODY_SN_DNS_RESOLUTION: Literal[{"description": "Enable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name", "help": "Enable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name", "help": "Disable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name.", "label": "Disable", "name": "disable"}]
VALID_BODY_MAC_EVENT_LOGGING: Literal[{"description": "Enable MAC address event logging", "help": "Enable MAC address event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable MAC address event logging", "help": "Disable MAC address event logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_BOUNCE_QUARANTINED_LINK: Literal[{"description": "Disable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last", "help": "Disable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last.", "label": "Disable", "name": "disable"}, {"description": "Enable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last", "help": "Enable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last.", "label": "Enable", "name": "enable"}]
VALID_BODY_QUARANTINE_MODE: Literal[{"description": "Quarantined device traffic is sent to FortiGate on a separate quarantine VLAN", "help": "Quarantined device traffic is sent to FortiGate on a separate quarantine VLAN.", "label": "By Vlan", "name": "by-vlan"}, {"description": "Quarantined device traffic is redirected only to the FortiGate on the received VLAN", "help": "Quarantined device traffic is redirected only to the FortiGate on the received VLAN.", "label": "By Redirect", "name": "by-redirect"}]
VALID_BODY_UPDATE_USER_DEVICE: Literal[{"description": "Update MAC address from switch-controller mac-cache", "help": "Update MAC address from switch-controller mac-cache.", "label": "Mac Cache", "name": "mac-cache"}, {"description": "Update from FortiSwitch LLDP neighbor database", "help": "Update from FortiSwitch LLDP neighbor database.", "label": "Lldp", "name": "lldp"}, {"description": "Update from FortiSwitch DHCP snooping client and server databases", "help": "Update from FortiSwitch DHCP snooping client and server databases.", "label": "Dhcp Snooping", "name": "dhcp-snooping"}, {"description": "Update from FortiSwitch Network-monitor Layer 2 tracking database", "help": "Update from FortiSwitch Network-monitor Layer 2 tracking database.", "label": "L2 Db", "name": "l2-db"}, {"description": "Update from FortiSwitch Network-monitor Layer 3 tracking database", "help": "Update from FortiSwitch Network-monitor Layer 3 tracking database.", "label": "L3 Db", "name": "l3-db"}]
VALID_BODY_FIPS_ENFORCE: Literal[{"description": "Disable enforcement of FIPS on managed FortiSwitch devices", "help": "Disable enforcement of FIPS on managed FortiSwitch devices.", "label": "Disable", "name": "disable"}, {"description": "Enable enforcement of FIPS on managed FortiSwitch devices", "help": "Enable enforcement of FIPS on managed FortiSwitch devices.", "label": "Enable", "name": "enable"}]
VALID_BODY_FIRMWARE_PROVISION_ON_AUTHORIZATION: Literal[{"description": "Enable firmware provision on authorization", "help": "Enable firmware provision on authorization.", "label": "Enable", "name": "enable"}, {"description": "Disable firmware provision on authorization", "help": "Disable firmware provision on authorization.", "label": "Disable", "name": "disable"}]
VALID_BODY_SWITCH_ON_DEAUTH: Literal[{"description": "No-operation on the managed FortiSwitch on deauthorization", "help": "No-operation on the managed FortiSwitch on deauthorization.", "label": "No Op", "name": "no-op"}, {"description": "Factory-reset the managed FortiSwitch on deauthorization", "help": "Factory-reset the managed FortiSwitch on deauthorization.", "label": "Factory Reset", "name": "factory-reset"}]

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
    "VALID_BODY_HTTPS_IMAGE_PUSH",
    "VALID_BODY_VLAN_ALL_MODE",
    "VALID_BODY_VLAN_OPTIMIZATION",
    "VALID_BODY_VLAN_IDENTITY",
    "VALID_BODY_DHCP_SERVER_ACCESS_LIST",
    "VALID_BODY_DHCP_OPTION82_FORMAT",
    "VALID_BODY_DHCP_OPTION82_CIRCUIT_ID",
    "VALID_BODY_DHCP_OPTION82_REMOTE_ID",
    "VALID_BODY_DHCP_SNOOP_CLIENT_REQ",
    "VALID_BODY_LOG_MAC_LIMIT_VIOLATIONS",
    "VALID_BODY_SN_DNS_RESOLUTION",
    "VALID_BODY_MAC_EVENT_LOGGING",
    "VALID_BODY_BOUNCE_QUARANTINED_LINK",
    "VALID_BODY_QUARANTINE_MODE",
    "VALID_BODY_UPDATE_USER_DEVICE",
    "VALID_BODY_FIPS_ENFORCE",
    "VALID_BODY_FIRMWARE_PROVISION_ON_AUTHORIZATION",
    "VALID_BODY_SWITCH_ON_DEAUTH",
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