from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_CONNECT_PROTOCOL: Literal[{"description": "Connect using RPC-over-TCP", "help": "Connect using RPC-over-TCP. Use for MS Exchange 2010 and earlier versions. Supported in MS Exchange 2013.", "label": "Rpc Over Tcp", "name": "rpc-over-tcp"}, {"description": "Connect using RPC-over-HTTP", "help": "Connect using RPC-over-HTTP. Use for MS Exchange 2016 and later versions. Supported in MS Exchange 2013.", "label": "Rpc Over Http", "name": "rpc-over-http"}, {"description": "Connect using RPC-over-HTTPS", "help": "Connect using RPC-over-HTTPS. Use for MS Exchange 2016 and later versions. Supported in MS Exchange 2013.", "label": "Rpc Over Https", "name": "rpc-over-https"}]
VALID_BODY_VALIDATE_SERVER_CERTIFICATE: Literal[{"description": "Disable validation of server certificate", "help": "Disable validation of server certificate.", "label": "Disable", "name": "disable"}, {"description": "Enable validation of server certificate", "help": "Enable validation of server certificate.", "label": "Enable", "name": "enable"}]
VALID_BODY_AUTH_TYPE: Literal[{"description": "Negotiate authentication", "help": "Negotiate authentication.", "label": "Spnego", "name": "spnego"}, {"description": "NTLM authentication", "help": "NTLM authentication.", "label": "Ntlm", "name": "ntlm"}, {"description": "Kerberos authentication", "help": "Kerberos authentication.", "label": "Kerberos", "name": "kerberos"}]
VALID_BODY_AUTH_LEVEL: Literal[{"description": "RPC authentication level \u0027connect\u0027", "help": "RPC authentication level \u0027connect\u0027.", "label": "Connect", "name": "connect"}, {"description": "RPC authentication level \u0027call\u0027", "help": "RPC authentication level \u0027call\u0027.", "label": "Call", "name": "call"}, {"description": "RPC authentication level \u0027packet\u0027", "help": "RPC authentication level \u0027packet\u0027.", "label": "Packet", "name": "packet"}, {"description": "RPC authentication level \u0027integrity\u0027", "help": "RPC authentication level \u0027integrity\u0027.", "label": "Integrity", "name": "integrity"}, {"description": "RPC authentication level \u0027privacy\u0027", "help": "RPC authentication level \u0027privacy\u0027.", "label": "Privacy", "name": "privacy"}]
VALID_BODY_HTTP_AUTH_TYPE: Literal[{"description": "Basic HTTP authentication", "help": "Basic HTTP authentication.", "label": "Basic", "name": "basic"}, {"description": "NTLM HTTP authentication", "help": "NTLM HTTP authentication.", "label": "Ntlm", "name": "ntlm"}]
VALID_BODY_SSL_MIN_PROTO_VERSION: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]
VALID_BODY_AUTO_DISCOVER_KDC: Literal[{"description": "Enable automatic discovery of KDC IP addresses", "help": "Enable automatic discovery of KDC IP addresses.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic discovery of KDC IP addresses", "help": "Disable automatic discovery of KDC IP addresses.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_CONNECT_PROTOCOL",
    "VALID_BODY_VALIDATE_SERVER_CERTIFICATE",
    "VALID_BODY_AUTH_TYPE",
    "VALID_BODY_AUTH_LEVEL",
    "VALID_BODY_HTTP_AUTH_TYPE",
    "VALID_BODY_SSL_MIN_PROTO_VERSION",
    "VALID_BODY_AUTO_DISCOVER_KDC",
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