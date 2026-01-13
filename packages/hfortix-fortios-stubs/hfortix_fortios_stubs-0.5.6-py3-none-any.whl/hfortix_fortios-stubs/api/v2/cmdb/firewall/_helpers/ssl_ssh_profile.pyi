from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_ALLOWLIST: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_BLOCK_BLOCKLISTED_CERTIFICATES: Literal[{"description": "Disable FortiGuard certificate blocklist", "help": "Disable FortiGuard certificate blocklist.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiGuard certificate blocklist", "help": "Enable FortiGuard certificate blocklist.", "label": "Enable", "name": "enable"}]
VALID_BODY_SERVER_CERT_MODE: Literal[{"description": "Multiple clients connecting to multiple servers", "help": "Multiple clients connecting to multiple servers.", "label": "Re Sign", "name": "re-sign"}, {"description": "Protect an SSL server", "help": "Protect an SSL server.", "label": "Replace", "name": "replace"}]
VALID_BODY_USE_SSL_SERVER: Literal[{"description": "Don\u0027t use SSL server configuration", "help": "Don\u0027t use SSL server configuration.", "label": "Disable", "name": "disable"}, {"description": "Use SSL server configuration", "help": "Use SSL server configuration.", "label": "Enable", "name": "enable"}]
VALID_BODY_SSL_EXEMPTION_IP_RATING: Literal[{"description": "Enable IP based URL rating", "help": "Enable IP based URL rating.", "label": "Enable", "name": "enable"}, {"description": "Disable IP based URL rating", "help": "Disable IP based URL rating.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSL_EXEMPTION_LOG: Literal[{"description": "Disable logging of SSL exemptions", "help": "Disable logging of SSL exemptions.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of SSL exemptions", "help": "Enable logging of SSL exemptions.", "label": "Enable", "name": "enable"}]
VALID_BODY_SSL_ANOMALY_LOG: Literal[{"description": "Disable logging of SSL anomalies", "help": "Disable logging of SSL anomalies.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of SSL anomalies", "help": "Enable logging of SSL anomalies.", "label": "Enable", "name": "enable"}]
VALID_BODY_SSL_NEGOTIATION_LOG: Literal[{"description": "Disable logging of SSL negotiation events", "help": "Disable logging of SSL negotiation events.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of SSL negotiation events", "help": "Enable logging of SSL negotiation events.", "label": "Enable", "name": "enable"}]
VALID_BODY_SSL_SERVER_CERT_LOG: Literal[{"description": "Disable logging of server certificate information", "help": "Disable logging of server certificate information.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of server certificate information", "help": "Enable logging of server certificate information.", "label": "Enable", "name": "enable"}]
VALID_BODY_SSL_HANDSHAKE_LOG: Literal[{"description": "Disable logging of TLS handshakes", "help": "Disable logging of TLS handshakes.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of TLS handshakes", "help": "Enable logging of TLS handshakes.", "label": "Enable", "name": "enable"}]
VALID_BODY_RPC_OVER_HTTPS: Literal[{"description": "Enable inspection of RPC over HTTPS", "help": "Enable inspection of RPC over HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable inspection of RPC over HTTPS", "help": "Disable inspection of RPC over HTTPS.", "label": "Disable", "name": "disable"}]
VALID_BODY_MAPI_OVER_HTTPS: Literal[{"description": "Enable inspection of MAPI over HTTPS", "help": "Enable inspection of MAPI over HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable inspection of MAPI over HTTPS", "help": "Disable inspection of MAPI over HTTPS.", "label": "Disable", "name": "disable"}]
VALID_BODY_SUPPORTED_ALPN: Literal[{"description": "Enable all ALPN including HTTP1", "help": "Enable all ALPN including HTTP1.1 except HTTP2 and SPDY.", "label": "Http1 1", "name": "http1-1"}, {"description": "Enable all ALPN including HTTP2 except HTTP1", "help": "Enable all ALPN including HTTP2 except HTTP1.1 and SPDY.", "label": "Http2", "name": "http2"}, {"description": "Allow all ALPN extensions except SPDY", "help": "Allow all ALPN extensions except SPDY.", "label": "All", "name": "all"}, {"description": "Do not use ALPN", "help": "Do not use ALPN.", "label": "None", "name": "none"}]

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
    "VALID_BODY_ALLOWLIST",
    "VALID_BODY_BLOCK_BLOCKLISTED_CERTIFICATES",
    "VALID_BODY_SERVER_CERT_MODE",
    "VALID_BODY_USE_SSL_SERVER",
    "VALID_BODY_SSL_EXEMPTION_IP_RATING",
    "VALID_BODY_SSL_EXEMPTION_LOG",
    "VALID_BODY_SSL_ANOMALY_LOG",
    "VALID_BODY_SSL_NEGOTIATION_LOG",
    "VALID_BODY_SSL_SERVER_CERT_LOG",
    "VALID_BODY_SSL_HANDSHAKE_LOG",
    "VALID_BODY_RPC_OVER_HTTPS",
    "VALID_BODY_MAPI_OVER_HTTPS",
    "VALID_BODY_SUPPORTED_ALPN",
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