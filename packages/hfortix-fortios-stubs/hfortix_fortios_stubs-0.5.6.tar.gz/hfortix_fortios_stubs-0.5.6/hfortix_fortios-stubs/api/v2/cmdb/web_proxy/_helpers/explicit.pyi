from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable the explicit web proxy", "help": "Enable the explicit web proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the explicit web proxy", "help": "Disable the explicit web proxy.", "label": "Disable", "name": "disable"}]
VALID_BODY_SECURE_WEB_PROXY: Literal[{"description": "Disable secure webproxy", "help": "Disable secure webproxy.", "label": "Disable", "name": "disable"}, {"description": "Enable secure webproxy access", "help": "Enable secure webproxy access.", "label": "Enable", "name": "enable"}, {"description": "Require secure webproxy access", "help": "Require secure webproxy access.", "label": "Secure", "name": "secure"}]
VALID_BODY_FTP_OVER_HTTP: Literal[{"description": "Enable FTP-over-HTTP sessions", "help": "Enable FTP-over-HTTP sessions.", "label": "Enable", "name": "enable"}, {"description": "Disable FTP-over-HTTP sessions", "help": "Disable FTP-over-HTTP sessions.", "label": "Disable", "name": "disable"}]
VALID_BODY_SOCKS: Literal[{"description": "Enable the SOCKS proxy", "help": "Enable the SOCKS proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the SOCKS proxy", "help": "Disable the SOCKS proxy.", "label": "Disable", "name": "disable"}]
VALID_BODY_HTTP_CONNECTION_MODE: Literal[{"description": "Only one server connection exists during the proxy session", "help": "Only one server connection exists during the proxy session.", "label": "Static", "name": "static"}, {"description": "Established connections are held until the proxy session ends", "help": "Established connections are held until the proxy session ends.", "label": "Multiplex", "name": "multiplex"}, {"description": "Established connections are shared with other proxy sessions", "help": "Established connections are shared with other proxy sessions.", "label": "Serverpool", "name": "serverpool"}]
VALID_BODY_CLIENT_CERT: Literal[{"description": "Disable client certificate request", "help": "Disable client certificate request.", "label": "Disable", "name": "disable"}, {"description": "Enable client certificate request", "help": "Enable client certificate request.", "label": "Enable", "name": "enable"}]
VALID_BODY_USER_AGENT_DETECT: Literal[{"description": "Disable to detect unknown device by HTTP user-agent if no client certificate provided", "help": "Disable to detect unknown device by HTTP user-agent if no client certificate provided.", "label": "Disable", "name": "disable"}, {"description": "Enable to detect unknown device by HTTP user-agent if no client certificate provided", "help": "Enable to detect unknown device by HTTP user-agent if no client certificate provided.", "label": "Enable", "name": "enable"}]
VALID_BODY_EMPTY_CERT_ACTION: Literal[{"description": "Accept the SSL handshake if the client certificate is empty", "help": "Accept the SSL handshake if the client certificate is empty.", "label": "Accept", "name": "accept"}, {"description": "Block the SSL handshake if the client certificate is empty", "help": "Block the SSL handshake if the client certificate is empty.", "label": "Block", "name": "block"}, {"description": "Accept the SSL handshake only if the end-point is unmanageable", "help": "Accept the SSL handshake only if the end-point is unmanageable.", "label": "Accept Unmanageable", "name": "accept-unmanageable"}]
VALID_BODY_SSL_DH_BITS: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}]
VALID_BODY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]
VALID_BODY_IPV6_STATUS: Literal[{"description": "Enable allowing an IPv6 web proxy destination", "help": "Enable allowing an IPv6 web proxy destination.", "label": "Enable", "name": "enable"}, {"description": "Disable allowing an IPv6 web proxy destination", "help": "Disable allowing an IPv6 web proxy destination.", "label": "Disable", "name": "disable"}]
VALID_BODY_STRICT_GUEST: Literal[{"description": "Enable strict guest user checking", "help": "Enable strict guest user checking.", "label": "Enable", "name": "enable"}, {"description": "Disable strict guest user checking", "help": "Disable strict guest user checking.", "label": "Disable", "name": "disable"}]
VALID_BODY_PREF_DNS_RESULT: Literal[{"description": "Send the IPv4 request first and then the IPv6 request", "help": "Send the IPv4 request first and then the IPv6 request. Use the DNS response that returns to the FortiGate first.", "label": "Ipv4", "name": "ipv4"}, {"description": "Send the IPv6 request first and then the IPv4 request", "help": "Send the IPv6 request first and then the IPv4 request. Use the DNS response that returns to the FortiGate first.", "label": "Ipv6", "name": "ipv6"}, {"description": "Use the IPv4 DNS response", "help": "Use the IPv4 DNS response. If the IPv6 DNS response arrives first, wait 50ms for the IPv4 response and then use the IPv4 response, otherwise the IPv6.", "label": "Ipv4 Strict", "name": "ipv4-strict"}, {"description": "Use the IPv6 DNS response", "help": "Use the IPv6 DNS response. If the IPv4 DNS response arrives first, wait 50ms for the IPv6 response and then use the IPv6 response, otherwise the IPv4.", "label": "Ipv6 Strict", "name": "ipv6-strict"}]
VALID_BODY_UNKNOWN_HTTP_VERSION: Literal[{"description": "Reject or tear down HTTP sessions that do not use HTTP 0", "help": "Reject or tear down HTTP sessions that do not use HTTP 0.9, 1.0, or 1.1.", "label": "Reject", "name": "reject"}, {"description": "Assume all HTTP sessions comply with HTTP 0", "help": "Assume all HTTP sessions comply with HTTP 0.9, 1.0, or 1.1. If a session uses a different HTTP version, it may not parse correctly and the connection may be lost.", "label": "Best Effort", "name": "best-effort"}]
VALID_BODY_SEC_DEFAULT_ACTION: Literal[{"description": "Accept requests", "help": "Accept requests. All explicit web proxy traffic is accepted whether there is an explicit web proxy policy or not.", "label": "Accept", "name": "accept"}, {"description": "Deny requests unless there is a matching explicit web proxy policy", "help": "Deny requests unless there is a matching explicit web proxy policy.", "label": "Deny", "name": "deny"}]
VALID_BODY_HTTPS_REPLACEMENT_MESSAGE: Literal[{"description": "Display a replacement message for HTTPS requests", "help": "Display a replacement message for HTTPS requests.", "label": "Enable", "name": "enable"}, {"description": "Do not display a replacement message for HTTPS requests", "help": "Do not display a replacement message for HTTPS requests.", "label": "Disable", "name": "disable"}]
VALID_BODY_MESSAGE_UPON_SERVER_ERROR: Literal[{"description": "Display a replacement message when a server error is detected", "help": "Display a replacement message when a server error is detected.", "label": "Enable", "name": "enable"}, {"description": "Do not display a replacement message when a server error is detected", "help": "Do not display a replacement message when a server error is detected.", "label": "Disable", "name": "disable"}]
VALID_BODY_PAC_FILE_SERVER_STATUS: Literal[{"description": "Enable Proxy Auto-Configuration (PAC)", "help": "Enable Proxy Auto-Configuration (PAC).", "label": "Enable", "name": "enable"}, {"description": "Disable Proxy Auto-Configuration (PAC)", "help": "Disable Proxy Auto-Configuration (PAC).", "label": "Disable", "name": "disable"}]
VALID_BODY_PAC_FILE_THROUGH_HTTPS: Literal[{"description": "Enable to get Proxy Auto-Configuration (PAC) through HTTPS", "help": "Enable to get Proxy Auto-Configuration (PAC) through HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable to get Proxy Auto-Configuration (PAC) through HTTPS", "help": "Disable to get Proxy Auto-Configuration (PAC) through HTTPS.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSL_ALGORITHM: Literal[{"description": "High encrption", "help": "High encrption. Allow only AES and ChaCha.", "label": "High", "name": "high"}, {"description": "Medium encryption", "help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}]
VALID_BODY_TRACE_AUTH_NO_RSP: Literal[{"description": "Enable logging timed-out authentication requests", "help": "Enable logging timed-out authentication requests.", "label": "Enable", "name": "enable"}, {"description": "Disable logging timed-out authentication requests", "help": "Disable logging timed-out authentication requests.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_SECURE_WEB_PROXY",
    "VALID_BODY_FTP_OVER_HTTP",
    "VALID_BODY_SOCKS",
    "VALID_BODY_HTTP_CONNECTION_MODE",
    "VALID_BODY_CLIENT_CERT",
    "VALID_BODY_USER_AGENT_DETECT",
    "VALID_BODY_EMPTY_CERT_ACTION",
    "VALID_BODY_SSL_DH_BITS",
    "VALID_BODY_INTERFACE_SELECT_METHOD",
    "VALID_BODY_IPV6_STATUS",
    "VALID_BODY_STRICT_GUEST",
    "VALID_BODY_PREF_DNS_RESULT",
    "VALID_BODY_UNKNOWN_HTTP_VERSION",
    "VALID_BODY_SEC_DEFAULT_ACTION",
    "VALID_BODY_HTTPS_REPLACEMENT_MESSAGE",
    "VALID_BODY_MESSAGE_UPON_SERVER_ERROR",
    "VALID_BODY_PAC_FILE_SERVER_STATUS",
    "VALID_BODY_PAC_FILE_THROUGH_HTTPS",
    "VALID_BODY_SSL_ALGORITHM",
    "VALID_BODY_TRACE_AUTH_NO_RSP",
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