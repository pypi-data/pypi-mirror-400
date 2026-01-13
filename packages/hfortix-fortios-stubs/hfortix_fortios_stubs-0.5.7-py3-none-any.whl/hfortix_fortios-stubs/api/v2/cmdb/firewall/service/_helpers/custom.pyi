from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_PROXY: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_PROTOCOL: Literal[{"description": "TCP, UDP, UDP-Lite and SCTP", "help": "TCP, UDP, UDP-Lite and SCTP.", "label": "Tcp/Udp/Udp Lite/Sctp", "name": "TCP/UDP/UDP-Lite/SCTP"}, {"description": "ICMP", "help": "ICMP.", "label": "Icmp", "name": "ICMP"}, {"description": "ICMP6", "help": "ICMP6.", "label": "Icmp6", "name": "ICMP6"}, {"description": "IP", "help": "IP.", "label": "Ip", "name": "IP"}, {"description": "HTTP - for web proxy", "help": "HTTP - for web proxy.", "label": "Http", "name": "HTTP"}, {"description": "FTP - for web proxy", "help": "FTP - for web proxy.", "label": "Ftp", "name": "FTP"}, {"description": "Connect - for web proxy", "help": "Connect - for web proxy.", "label": "Connect", "name": "CONNECT"}, {"description": "Socks TCP - for web proxy", "help": "Socks TCP - for web proxy.", "label": "Socks Tcp", "name": "SOCKS-TCP"}, {"description": "Socks UDP - for web proxy", "help": "Socks UDP - for web proxy.", "label": "Socks Udp", "name": "SOCKS-UDP"}, {"description": "All - for web proxy", "help": "All - for web proxy.", "label": "All", "name": "ALL"}]
VALID_BODY_HELPER: Literal[{"description": "Automatically select helper based on protocol and port", "help": "Automatically select helper based on protocol and port.", "label": "Auto", "name": "auto"}, {"description": "Disable helper", "help": "Disable helper.", "label": "Disable", "name": "disable"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "TFTP", "help": "TFTP.", "label": "Tftp", "name": "tftp"}, {"description": "RAS", "help": "RAS.", "label": "Ras", "name": "ras"}, {"description": "H323", "help": "H323.", "label": "H323", "name": "h323"}, {"description": "TNS", "help": "TNS.", "label": "Tns", "name": "tns"}, {"description": "MMS", "help": "MMS.", "label": "Mms", "name": "mms"}, {"description": "SIP", "help": "SIP.", "label": "Sip", "name": "sip"}, {"description": "PPTP", "help": "PPTP.", "label": "Pptp", "name": "pptp"}, {"description": "RTSP", "help": "RTSP.", "label": "Rtsp", "name": "rtsp"}, {"description": "DNS UDP", "help": "DNS UDP.", "label": "Dns Udp", "name": "dns-udp"}, {"description": "DNS TCP", "help": "DNS TCP.", "label": "Dns Tcp", "name": "dns-tcp"}, {"description": "PMAP", "help": "PMAP.", "label": "Pmap", "name": "pmap"}, {"description": "RSH", "help": "RSH.", "label": "Rsh", "name": "rsh"}, {"description": "DCERPC", "help": "DCERPC.", "label": "Dcerpc", "name": "dcerpc"}, {"description": "MGCP", "help": "MGCP.", "label": "Mgcp", "name": "mgcp"}]
VALID_BODY_CHECK_RESET_RANGE: Literal[{"description": "Disable RST range check", "help": "Disable RST range check.", "label": "Disable", "name": "disable"}, {"description": "Check RST range strictly", "help": "Check RST range strictly.", "label": "Strict", "name": "strict"}, {"description": "Using system default setting", "help": "Using system default setting.", "label": "Default", "name": "default"}]
VALID_BODY_APP_SERVICE_TYPE: Literal[{"description": "Disable application type", "help": "Disable application type.", "label": "Disable", "name": "disable"}, {"description": "Application ID", "help": "Application ID.", "label": "App Id", "name": "app-id"}, {"description": "Applicatin category", "help": "Applicatin category.", "label": "App Category", "name": "app-category"}]
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
    "VALID_BODY_PROXY",
    "VALID_BODY_PROTOCOL",
    "VALID_BODY_HELPER",
    "VALID_BODY_CHECK_RESET_RANGE",
    "VALID_BODY_APP_SERVICE_TYPE",
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