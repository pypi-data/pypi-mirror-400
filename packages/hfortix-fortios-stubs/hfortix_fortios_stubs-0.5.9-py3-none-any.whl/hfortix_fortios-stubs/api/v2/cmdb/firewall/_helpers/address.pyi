from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"description": "Standard IPv4 address with subnet mask", "help": "Standard IPv4 address with subnet mask.", "label": "Ipmask", "name": "ipmask"}, {"description": "Range of IPv4 addresses between two specified addresses (inclusive)", "help": "Range of IPv4 addresses between two specified addresses (inclusive).", "label": "Iprange", "name": "iprange"}, {"description": "Fully Qualified Domain Name address", "help": "Fully Qualified Domain Name address.", "label": "Fqdn", "name": "fqdn"}, {"description": "IP addresses from a specified country", "help": "IP addresses from a specified country.", "label": "Geography", "name": "geography"}, {"description": "Standard IPv4 using a wildcard subnet mask", "help": "Standard IPv4 using a wildcard subnet mask.", "label": "Wildcard", "name": "wildcard"}, {"description": "Dynamic address object", "help": "Dynamic address object.", "label": "Dynamic", "name": "dynamic"}, {"description": "IP and subnet of interface", "help": "IP and subnet of interface.", "label": "Interface Subnet", "name": "interface-subnet"}, {"description": "Range of MAC addresses", "help": "Range of MAC addresses.", "label": "Mac", "name": "mac"}, {"description": "route-tag addresses", "help": "route-tag addresses.", "label": "Route Tag", "name": "route-tag"}]
VALID_BODY_SUB_TYPE: Literal[{"description": "SDN address", "help": "SDN address.", "label": "Sdn", "name": "sdn"}, {"description": "ClearPass SPT (System Posture Token) address", "help": "ClearPass SPT (System Posture Token) address.", "label": "Clearpass Spt", "name": "clearpass-spt"}, {"description": "FSSO address", "help": "FSSO address.", "label": "Fsso", "name": "fsso"}, {"description": "RSSO address", "help": "RSSO address.", "label": "Rsso", "name": "rsso"}, {"description": "FortiClient EMS tag", "help": "FortiClient EMS tag.", "label": "Ems Tag", "name": "ems-tag"}, {"description": "FortiVoice tag", "help": "FortiVoice tag.", "label": "Fortivoice Tag", "name": "fortivoice-tag"}, {"description": "FortiNAC tag", "help": "FortiNAC tag.", "label": "Fortinac Tag", "name": "fortinac-tag"}, {"description": "Switch Controller NAC policy tag", "help": "Switch Controller NAC policy tag.", "label": "Swc Tag", "name": "swc-tag"}, {"description": "Device address", "help": "Device address.", "label": "Device Identification", "name": "device-identification"}, {"description": "External resource", "help": "External resource.", "label": "External Resource", "name": "external-resource"}, {"description": "Tag from EOL product", "help": "Tag from EOL product.", "label": "Obsolete", "name": "obsolete"}]
VALID_BODY_CLEARPASS_SPT: Literal[{"description": "UNKNOWN", "help": "UNKNOWN.", "label": "Unknown", "name": "unknown"}, {"description": "HEALTHY", "help": "HEALTHY.", "label": "Healthy", "name": "healthy"}, {"description": "QUARANTINE", "help": "QUARANTINE.", "label": "Quarantine", "name": "quarantine"}, {"description": "CHECKUP", "help": "CHECKUP.", "label": "Checkup", "name": "checkup"}, {"description": "TRANSIENT", "help": "TRANSIENT.", "label": "Transient", "name": "transient"}, {"description": "INFECTED", "help": "INFECTED.", "label": "Infected", "name": "infected"}]
VALID_BODY_OBJ_TYPE: Literal[{"description": "IP address", "help": "IP address.", "label": "Ip", "name": "ip"}, {"description": "MAC address", "help": "MAC address", "label": "Mac", "name": "mac"}]
VALID_BODY_SDN_ADDR_TYPE: Literal[{"description": "Collect private addresses only", "help": "Collect private addresses only.", "label": "Private", "name": "private"}, {"description": "Collect public addresses only", "help": "Collect public addresses only.", "label": "Public", "name": "public"}, {"description": "Collect both public and private addresses", "help": "Collect both public and private addresses.", "label": "All", "name": "all"}]
VALID_BODY_NODE_IP_ONLY: Literal[{"description": "Enable collection of node addresses only in Kubernetes", "help": "Enable collection of node addresses only in Kubernetes.", "label": "Enable", "name": "enable"}, {"description": "Disable collection of node addresses only in Kubernetes", "help": "Disable collection of node addresses only in Kubernetes.", "label": "Disable", "name": "disable"}]
VALID_BODY_ALLOW_ROUTING: Literal[{"description": "Enable use of this address in routing configurations", "help": "Enable use of this address in routing configurations.", "label": "Enable", "name": "enable"}, {"description": "Disable use of this address in routing configurations", "help": "Disable use of this address in routing configurations.", "label": "Disable", "name": "disable"}]
VALID_BODY_PASSIVE_FQDN_LEARNING: Literal[{"description": "Disable passive learning of FQDNs", "help": "Disable passive learning of FQDNs.", "label": "Disable", "name": "disable"}, {"description": "Enable passive learning of FQDNs", "help": "Enable passive learning of FQDNs.", "label": "Enable", "name": "enable"}]
VALID_BODY_FABRIC_OBJECT: Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_SUB_TYPE",
    "VALID_BODY_CLEARPASS_SPT",
    "VALID_BODY_OBJ_TYPE",
    "VALID_BODY_SDN_ADDR_TYPE",
    "VALID_BODY_NODE_IP_ONLY",
    "VALID_BODY_ALLOW_ROUTING",
    "VALID_BODY_PASSIVE_FQDN_LEARNING",
    "VALID_BODY_FABRIC_OBJECT",
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