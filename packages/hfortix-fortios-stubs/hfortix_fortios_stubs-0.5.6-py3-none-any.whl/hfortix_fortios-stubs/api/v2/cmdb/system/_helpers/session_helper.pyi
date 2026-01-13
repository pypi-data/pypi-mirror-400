from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_NAME: Literal[{"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "TFTP", "help": "TFTP.", "label": "Tftp", "name": "tftp"}, {"description": "RAS", "help": "RAS.", "label": "Ras", "name": "ras"}, {"description": "H323", "help": "H323.", "label": "H323", "name": "h323"}, {"description": "TNS", "help": "TNS.", "label": "Tns", "name": "tns"}, {"description": "MMS", "help": "MMS.", "label": "Mms", "name": "mms"}, {"description": "SIP", "help": "SIP.", "label": "Sip", "name": "sip"}, {"description": "PPTP", "help": "PPTP.", "label": "Pptp", "name": "pptp"}, {"description": "RTSP", "help": "RTSP.", "label": "Rtsp", "name": "rtsp"}, {"description": "DNS UDP", "help": "DNS UDP.", "label": "Dns Udp", "name": "dns-udp"}, {"description": "DNS TCP", "help": "DNS TCP.", "label": "Dns Tcp", "name": "dns-tcp"}, {"description": "PMAP", "help": "PMAP.", "label": "Pmap", "name": "pmap"}, {"description": "RSH", "help": "RSH.", "label": "Rsh", "name": "rsh"}, {"description": "DCERPC", "help": "DCERPC.", "label": "Dcerpc", "name": "dcerpc"}, {"description": "MGCP", "help": "MGCP.", "label": "Mgcp", "name": "mgcp"}]

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
    "VALID_BODY_NAME",
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