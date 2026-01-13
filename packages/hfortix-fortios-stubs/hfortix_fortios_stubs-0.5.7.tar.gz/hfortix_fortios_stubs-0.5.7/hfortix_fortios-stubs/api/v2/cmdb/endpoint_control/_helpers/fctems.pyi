from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable EMS configuration and operation", "help": "Enable EMS configuration and operation.", "label": "Enable", "name": "enable"}, {"description": "Disable EMS configuration and operation", "help": "Disable EMS configuration and operation.", "label": "Disable", "name": "disable"}]
VALID_BODY_DIRTY_REASON: Literal[{"description": "FortiClient EMS entry not dirty", "help": "FortiClient EMS entry not dirty.", "label": "None", "name": "none"}, {"description": "FortiClient EMS entry dirty because EMS SN is mismatched with configured SN", "help": "FortiClient EMS entry dirty because EMS SN is mismatched with configured SN.", "label": "Mismatched Ems Sn", "name": "mismatched-ems-sn"}]
VALID_BODY_FORTINETONE_CLOUD_AUTHENTICATION: Literal[{"description": "Enable authentication of FortiClient EMS Cloud through FortiCloud account", "help": "Enable authentication of FortiClient EMS Cloud through FortiCloud account.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication of FortiClient EMS Cloud through FortiCloud account", "help": "Disable authentication of FortiClient EMS Cloud through FortiCloud account.", "label": "Disable", "name": "disable"}]
VALID_BODY_PULL_SYSINFO: Literal[{"description": "Enable pulling FortiClient user SysInfo from EMS", "help": "Enable pulling FortiClient user SysInfo from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling FortiClient user SysInfo from EMS", "help": "Disable pulling FortiClient user SysInfo from EMS.", "label": "Disable", "name": "disable"}]
VALID_BODY_PULL_VULNERABILITIES: Literal[{"description": "Enable pulling client vulnerabilities from EMS", "help": "Enable pulling client vulnerabilities from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling client vulnerabilities from EMS", "help": "Disable pulling client vulnerabilities from EMS.", "label": "Disable", "name": "disable"}]
VALID_BODY_PULL_TAGS: Literal[{"description": "Enable pulling FortiClient user tags from EMS", "help": "Enable pulling FortiClient user tags from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling FortiClient user tags from EMS", "help": "Disable pulling FortiClient user tags from EMS.", "label": "Disable", "name": "disable"}]
VALID_BODY_PULL_MALWARE_HASH: Literal[{"description": "Enable pulling FortiClient malware hash from EMS", "help": "Enable pulling FortiClient malware hash from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling FortiClient malware hash from EMS", "help": "Disable pulling FortiClient malware hash from EMS.", "label": "Disable", "name": "disable"}]
VALID_BODY_CAPABILITIES: Literal[{"description": "Allow this FortiGate unit to load the authentication page provided by EMS to authenticate itself with EMS", "help": "Allow this FortiGate unit to load the authentication page provided by EMS to authenticate itself with EMS.", "label": "Fabric Auth", "name": "fabric-auth"}, {"description": "Allow silent approval of non-root or FortiGate HA clusters on EMS in the Security Fabric", "help": "Allow silent approval of non-root or FortiGate HA clusters on EMS in the Security Fabric.", "label": "Silent Approval", "name": "silent-approval"}, {"description": "Enable/disable websockets for this FortiGate unit", "help": "Enable/disable websockets for this FortiGate unit. Override behavior using websocket-override.", "label": "Websocket", "name": "websocket"}, {"description": "Allow this FortiGate unit to request malware hash notifications over websocket", "help": "Allow this FortiGate unit to request malware hash notifications over websocket.", "label": "Websocket Malware", "name": "websocket-malware"}, {"description": "Enable/disable syncing deep inspection certificates with EMS", "help": "Enable/disable syncing deep inspection certificates with EMS.", "label": "Push Ca Certs", "name": "push-ca-certs"}, {"description": "Can recieve tag information from New Common Tags API from EMS", "help": "Can recieve tag information from New Common Tags API from EMS.", "label": "Common Tags Api", "name": "common-tags-api"}, {"description": "Allow this FortiGate to retrieve Tenant-ID from EMS", "help": "Allow this FortiGate to retrieve Tenant-ID from EMS.", "label": "Tenant Id", "name": "tenant-id"}, {"description": "Allow this FortiGate to retrieve avatars from EMS by fingerprint", "help": "Allow this FortiGate to retrieve avatars from EMS by fingerprint.", "label": "Client Avatars", "name": "client-avatars"}, {"description": "Allow this FortiGate to create a vdom connector to EMS", "help": "Allow this FortiGate to create a vdom connector to EMS.", "label": "Single Vdom Connector", "name": "single-vdom-connector"}, {"description": "Allow this FortiGate to send additional info to EMS", "help": "Allow this FortiGate to send additional info to EMS.", "label": "Fgt Sysinfo Api", "name": "fgt-sysinfo-api"}, {"description": "Allow this FortiGate to send vdom\u0027s ZTNA server information to EMS", "help": "Allow this FortiGate to send vdom\u0027s ZTNA server information to EMS.", "label": "Ztna Server Info", "name": "ztna-server-info"}, {"description": "Allow this FortiGate to send used tags information to EMS", "help": "Allow this FortiGate to send used tags information to EMS.", "label": "Used Tags", "name": "used-tags"}]
VALID_BODY_SEND_TAGS_TO_ALL_VDOMS: Literal[{"help": "Enable sending tags to all vdoms.", "label": "Enable", "name": "enable"}, {"description": "Disable sending tags to all vdoms", "help": "Disable sending tags to all vdoms.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEBSOCKET_OVERRIDE: Literal[{"description": "Do not override the WebSocket connection", "help": "Do not override the WebSocket connection. Connect to WebSocket of this EMS server if it is capable (default).", "label": "Enable", "name": "enable"}, {"description": "Override the WebSocket connection", "help": "Override the WebSocket connection. Do not connect to WebSocket even if EMS is capable of a WebSocket connection.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]
VALID_BODY_TRUST_CA_CN: Literal[{"description": "Trust EMS certificate CA \u0026 CN to automatically renew certificate", "help": "Trust EMS certificate CA \u0026 CN to automatically renew certificate.", "label": "Enable", "name": "enable"}, {"description": "Do not trust EMS certificate CA \u0026 CN to automatically renew certificate", "help": "Do not trust EMS certificate CA \u0026 CN to automatically renew certificate.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_DIRTY_REASON",
    "VALID_BODY_FORTINETONE_CLOUD_AUTHENTICATION",
    "VALID_BODY_PULL_SYSINFO",
    "VALID_BODY_PULL_VULNERABILITIES",
    "VALID_BODY_PULL_TAGS",
    "VALID_BODY_PULL_MALWARE_HASH",
    "VALID_BODY_CAPABILITIES",
    "VALID_BODY_SEND_TAGS_TO_ALL_VDOMS",
    "VALID_BODY_WEBSOCKET_OVERRIDE",
    "VALID_BODY_INTERFACE_SELECT_METHOD",
    "VALID_BODY_TRUST_CA_CN",
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