from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"description": "Static NAT", "help": "Static NAT.", "label": "Static Nat", "name": "static-nat"}, {"description": "Load balance", "help": "Load balance.", "label": "Load Balance", "name": "load-balance"}, {"description": "Server load balance", "help": "Server load balance.", "label": "Server Load Balance", "name": "server-load-balance"}, {"description": "DNS translation", "help": "DNS translation.", "label": "Dns Translation", "name": "dns-translation"}, {"description": "Fully qualified domain name", "help": "Fully qualified domain name.", "label": "Fqdn", "name": "fqdn"}, {"description": "Access proxy", "help": "Access proxy.", "label": "Access Proxy", "name": "access-proxy"}]
VALID_BODY_SERVER_TYPE: Literal[{"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"help": "SSL.", "label": "Ssl", "name": "ssl"}, {"description": "TCP", "help": "TCP.", "label": "Tcp", "name": "tcp"}, {"description": "UDP", "help": "UDP.", "label": "Udp", "name": "udp"}, {"description": "IP", "help": "IP.", "label": "Ip", "name": "ip"}]
VALID_BODY_LDB_METHOD: Literal[{"description": "Distribute to server based on source IP", "help": "Distribute to server based on source IP.", "label": "Static", "name": "static"}, {"description": "Distribute to server based round robin order", "help": "Distribute to server based round robin order.", "label": "Round Robin", "name": "round-robin"}, {"description": "Distribute to server based on weight", "help": "Distribute to server based on weight.", "label": "Weighted", "name": "weighted"}, {"description": "Distribute to server with lowest session count", "help": "Distribute to server with lowest session count.", "label": "Least Session", "name": "least-session"}, {"description": "Distribute to server with lowest Round-Trip-Time", "help": "Distribute to server with lowest Round-Trip-Time.", "label": "Least Rtt", "name": "least-rtt"}, {"description": "Distribute to the first server that is alive", "help": "Distribute to the first server that is alive.", "label": "First Alive", "name": "first-alive"}, {"description": "Distribute to server based on host field in HTTP header", "help": "Distribute to server based on host field in HTTP header.", "label": "Http Host", "name": "http-host"}]
VALID_BODY_SRC_VIP_FILTER: Literal[{"description": "Match any destination for the reverse SNAT rule", "help": "Match any destination for the reverse SNAT rule.", "label": "Disable", "name": "disable"}, {"description": "Match only destinations in \u0027src-filter\u0027 for the reverse SNAT rule", "help": "Match only destinations in \u0027src-filter\u0027 for the reverse SNAT rule.", "label": "Enable", "name": "enable"}]
VALID_BODY_H2_SUPPORT: Literal[{"description": "Enable HTTP2 support", "help": "Enable HTTP2 support.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP2 support", "help": "Disable HTTP2 support.", "label": "Disable", "name": "disable"}]
VALID_BODY_H3_SUPPORT: Literal[{"description": "Enable HTTP3/QUIC support", "help": "Enable HTTP3/QUIC support.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP3/QUIC support", "help": "Disable HTTP3/QUIC support.", "label": "Disable", "name": "disable"}]
VALID_BODY_NAT44: Literal[{"description": "Disable NAT44", "help": "Disable NAT44.", "label": "Disable", "name": "disable"}, {"description": "Enable NAT44", "help": "Enable NAT44.", "label": "Enable", "name": "enable"}]
VALID_BODY_NAT46: Literal[{"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}, {"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}]
VALID_BODY_ADD_NAT46_ROUTE: Literal[{"description": "Disable adding NAT46 route", "help": "Disable adding NAT46 route.", "label": "Disable", "name": "disable"}, {"description": "Enable adding NAT46 route", "help": "Enable adding NAT46 route.", "label": "Enable", "name": "enable"}]
VALID_BODY_ARP_REPLY: Literal[{"description": "Disable ARP reply", "help": "Disable ARP reply.", "label": "Disable", "name": "disable"}, {"description": "Enable ARP reply", "help": "Enable ARP reply.", "label": "Enable", "name": "enable"}]
VALID_BODY_HTTP_REDIRECT: Literal[{"description": "Enable redirection of HTTP to HTTPS", "help": "Enable redirection of HTTP to HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable redirection of HTTP to HTTPS", "help": "Disable redirection of HTTP to HTTPS.", "label": "Disable", "name": "disable"}]
VALID_BODY_PERSISTENCE: Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "HTTP cookie", "help": "HTTP cookie.", "label": "Http Cookie", "name": "http-cookie"}, {"description": "SSL session ID", "help": "SSL session ID.", "label": "Ssl Session Id", "name": "ssl-session-id"}]
VALID_BODY_NAT_SOURCE_VIP: Literal[{"description": "Force only the source NAT mapped IP to the external IP for traffic egressing the external interface of the VIP", "help": "Force only the source NAT mapped IP to the external IP for traffic egressing the external interface of the VIP.", "label": "Disable", "name": "disable"}, {"description": "Force the source NAT mapped IP to the external IP for all traffic", "help": "Force the source NAT mapped IP to the external IP for all traffic.", "label": "Enable", "name": "enable"}]
VALID_BODY_PORTFORWARD: Literal[{"description": "Disable port forward", "help": "Disable port forward.", "label": "Disable", "name": "disable"}, {"description": "Enable port forward", "help": "Enable port forward.", "label": "Enable", "name": "enable"}]
VALID_BODY_STATUS: Literal[{"description": "Disable the VIP", "help": "Disable the VIP.", "label": "Disable", "name": "disable"}, {"description": "Enable the VIP", "help": "Enable the VIP.", "label": "Enable", "name": "enable"}]
VALID_BODY_PROTOCOL: Literal[{"description": "TCP", "help": "TCP.", "label": "Tcp", "name": "tcp"}, {"description": "UDP", "help": "UDP.", "label": "Udp", "name": "udp"}, {"description": "SCTP", "help": "SCTP.", "label": "Sctp", "name": "sctp"}, {"description": "ICMP", "help": "ICMP.", "label": "Icmp", "name": "icmp"}]
VALID_BODY_PORTMAPPING_TYPE: Literal[{"description": "One to one", "help": "One to one.", "label": "1 To 1", "name": "1-to-1"}, {"description": "Many to many", "help": "Many to many.", "label": "M To N", "name": "m-to-n"}]
VALID_BODY_EMPTY_CERT_ACTION: Literal[{"description": "Accept the SSL handshake if the client certificate is empty", "help": "Accept the SSL handshake if the client certificate is empty.", "label": "Accept", "name": "accept"}, {"description": "Block the SSL handshake if the client certificate is empty", "help": "Block the SSL handshake if the client certificate is empty.", "label": "Block", "name": "block"}, {"description": "Accept the SSL handshake only if the end-point is unmanageable", "help": "Accept the SSL handshake only if the end-point is unmanageable.", "label": "Accept Unmanageable", "name": "accept-unmanageable"}]
VALID_BODY_USER_AGENT_DETECT: Literal[{"description": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Disable", "name": "disable"}, {"description": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Enable", "name": "enable"}]
VALID_BODY_CLIENT_CERT: Literal[{"description": "Disable client certificate request", "help": "Disable client certificate request.", "label": "Disable", "name": "disable"}, {"description": "Enable client certificate request", "help": "Enable client certificate request.", "label": "Enable", "name": "enable"}]
VALID_BODY_HTTP_COOKIE_DOMAIN_FROM_HOST: Literal[{"description": "Disable use of HTTP cookie domain from host field in HTTP (use http-cooke-domain setting)", "help": "Disable use of HTTP cookie domain from host field in HTTP (use http-cooke-domain setting).", "label": "Disable", "name": "disable"}, {"description": "Enable use of HTTP cookie domain from host field in HTTP", "help": "Enable use of HTTP cookie domain from host field in HTTP.", "label": "Enable", "name": "enable"}]
VALID_BODY_HTTP_COOKIE_SHARE: Literal[{"description": "Only allow HTTP cookie to match this virtual server", "help": "Only allow HTTP cookie to match this virtual server.", "label": "Disable", "name": "disable"}, {"description": "Allow HTTP cookie to match any virtual server with same IP", "help": "Allow HTTP cookie to match any virtual server with same IP.", "label": "Same Ip", "name": "same-ip"}]
VALID_BODY_HTTPS_COOKIE_SECURE: Literal[{"description": "Do not mark cookie as secure, allow sharing between an HTTP and HTTPS connection", "help": "Do not mark cookie as secure, allow sharing between an HTTP and HTTPS connection.", "label": "Disable", "name": "disable"}, {"description": "Mark inserted cookie as secure, cookie can only be used for HTTPS a connection", "help": "Mark inserted cookie as secure, cookie can only be used for HTTPS a connection.", "label": "Enable", "name": "enable"}]
VALID_BODY_HTTP_MULTIPLEX: Literal[{"description": "Enable HTTP session multiplexing", "help": "Enable HTTP session multiplexing.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP session multiplexing", "help": "Disable HTTP session multiplexing.", "label": "Disable", "name": "disable"}]
VALID_BODY_HTTP_IP_HEADER: Literal[{"description": "Enable adding HTTP header", "help": "Enable adding HTTP header.", "label": "Enable", "name": "enable"}, {"description": "Disable adding HTTP header", "help": "Disable adding HTTP header.", "label": "Disable", "name": "disable"}]
VALID_BODY_OUTLOOK_WEB_ACCESS: Literal[{"description": "Disable Outlook Web Access support", "help": "Disable Outlook Web Access support.", "label": "Disable", "name": "disable"}, {"description": "Enable Outlook Web Access support", "help": "Enable Outlook Web Access support.", "label": "Enable", "name": "enable"}]
VALID_BODY_WEBLOGIC_SERVER: Literal[{"description": "Do not add HTTP header indicating SSL offload for WebLogic server", "help": "Do not add HTTP header indicating SSL offload for WebLogic server.", "label": "Disable", "name": "disable"}, {"description": "Add HTTP header indicating SSL offload for WebLogic server", "help": "Add HTTP header indicating SSL offload for WebLogic server.", "label": "Enable", "name": "enable"}]
VALID_BODY_WEBSPHERE_SERVER: Literal[{"description": "Do not add HTTP header indicating SSL offload for WebSphere server", "help": "Do not add HTTP header indicating SSL offload for WebSphere server.", "label": "Disable", "name": "disable"}, {"description": "Add HTTP header indicating SSL offload for WebSphere server", "help": "Add HTTP header indicating SSL offload for WebSphere server.", "label": "Enable", "name": "enable"}]
VALID_BODY_SSL_MODE: Literal[{"description": "Client to FortiGate SSL", "help": "Client to FortiGate SSL.", "label": "Half", "name": "half"}, {"description": "Client to FortiGate and FortiGate to Server SSL", "help": "Client to FortiGate and FortiGate to Server SSL.", "label": "Full", "name": "full"}]
VALID_BODY_SSL_DH_BITS: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}, {"description": "3072-bit Diffie-Hellman prime", "help": "3072-bit Diffie-Hellman prime.", "label": "3072", "name": "3072"}, {"description": "4096-bit Diffie-Hellman prime", "help": "4096-bit Diffie-Hellman prime.", "label": "4096", "name": "4096"}]
VALID_BODY_SSL_ALGORITHM: Literal[{"description": "High encryption", "help": "High encryption. Allow only AES and ChaCha.", "label": "High", "name": "high"}, {"description": "Medium encryption", "help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}, {"description": "Custom encryption", "help": "Custom encryption. Use config ssl-cipher-suites to select the cipher suites that are allowed.", "label": "Custom", "name": "custom"}]
VALID_BODY_SSL_SERVER_ALGORITHM: Literal[{"description": "High encryption", "help": "High encryption. Allow only AES and ChaCha.", "label": "High", "name": "high"}, {"description": "Medium encryption", "help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}, {"description": "Custom encryption", "help": "Custom encryption. Use ssl-server-cipher-suites to select the cipher suites that are allowed.", "label": "Custom", "name": "custom"}, {"description": "Use the same encryption algorithms for both client and server sessions", "help": "Use the same encryption algorithms for both client and server sessions.", "label": "Client", "name": "client"}]
VALID_BODY_SSL_PFS: Literal[{"description": "Allow only Diffie-Hellman cipher-suites, so PFS is applied", "help": "Allow only Diffie-Hellman cipher-suites, so PFS is applied.", "label": "Require", "name": "require"}, {"description": "Allow only non-Diffie-Hellman cipher-suites, so PFS is not applied", "help": "Allow only non-Diffie-Hellman cipher-suites, so PFS is not applied.", "label": "Deny", "name": "deny"}, {"description": "Allow use of any cipher suite so PFS may or may not be used depending on the cipher suite selected", "help": "Allow use of any cipher suite so PFS may or may not be used depending on the cipher suite selected.", "label": "Allow", "name": "allow"}]
VALID_BODY_SSL_MIN_VERSION: Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}]
VALID_BODY_SSL_MAX_VERSION: Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}]
VALID_BODY_SSL_SERVER_MIN_VERSION: Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}, {"description": "Use same value as client configuration", "help": "Use same value as client configuration.", "label": "Client", "name": "client"}]
VALID_BODY_SSL_SERVER_MAX_VERSION: Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}, {"description": "Use same value as client configuration", "help": "Use same value as client configuration.", "label": "Client", "name": "client"}]
VALID_BODY_SSL_ACCEPT_FFDHE_GROUPS: Literal[{"description": "Accept FFDHE groups", "help": "Accept FFDHE groups.", "label": "Enable", "name": "enable"}, {"description": "Do not accept FFDHE groups", "help": "Do not accept FFDHE groups.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSL_SEND_EMPTY_FRAGS: Literal[{"description": "Send empty fragments", "help": "Send empty fragments.", "label": "Enable", "name": "enable"}, {"description": "Do not send empty fragments", "help": "Do not send empty fragments.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSL_CLIENT_FALLBACK: Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Enable", "help": "Enable.", "label": "Enable", "name": "enable"}]
VALID_BODY_SSL_CLIENT_RENEGOTIATION: Literal[{"description": "Allow a SSL client to renegotiate", "help": "Allow a SSL client to renegotiate.", "label": "Allow", "name": "allow"}, {"description": "Abort any client initiated SSL re-negotiation attempt", "help": "Abort any client initiated SSL re-negotiation attempt.", "label": "Deny", "name": "deny"}, {"description": "Abort any client initiated SSL re-negotiation attempt that does not use RFC 5746 Secure Renegotiation", "help": "Abort any client initiated SSL re-negotiation attempt that does not use RFC 5746 Secure Renegotiation.", "label": "Secure", "name": "secure"}]
VALID_BODY_SSL_CLIENT_SESSION_STATE_TYPE: Literal[{"description": "Do not keep session states", "help": "Do not keep session states.", "label": "Disable", "name": "disable"}, {"description": "Expire session states after this many minutes", "help": "Expire session states after this many minutes.", "label": "Time", "name": "time"}, {"description": "Expire session states when this maximum is reached", "help": "Expire session states when this maximum is reached.", "label": "Count", "name": "count"}, {"description": "Expire session states based on time or count, whichever occurs first", "help": "Expire session states based on time or count, whichever occurs first.", "label": "Both", "name": "both"}]
VALID_BODY_SSL_SERVER_RENEGOTIATION: Literal[{"description": "Enable secure renegotiation", "help": "Enable secure renegotiation.", "label": "Enable", "name": "enable"}, {"description": "Disable secure renegotiation", "help": "Disable secure renegotiation.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSL_SERVER_SESSION_STATE_TYPE: Literal[{"description": "Do not keep session states", "help": "Do not keep session states.", "label": "Disable", "name": "disable"}, {"description": "Expire session states after this many minutes", "help": "Expire session states after this many minutes.", "label": "Time", "name": "time"}, {"description": "Expire session states when this maximum is reached", "help": "Expire session states when this maximum is reached.", "label": "Count", "name": "count"}, {"description": "Expire session states based on time or count, whichever occurs first", "help": "Expire session states based on time or count, whichever occurs first.", "label": "Both", "name": "both"}]
VALID_BODY_SSL_HTTP_LOCATION_CONVERSION: Literal[{"description": "Enable HTTP location conversion", "help": "Enable HTTP location conversion.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP location conversion", "help": "Disable HTTP location conversion.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSL_HTTP_MATCH_HOST: Literal[{"description": "Match HTTP host in response header", "help": "Match HTTP host in response header.", "label": "Enable", "name": "enable"}, {"description": "Do not match HTTP host", "help": "Do not match HTTP host.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSL_HPKP: Literal[{"description": "Do not add a HPKP header to each HTTP response", "help": "Do not add a HPKP header to each HTTP response.", "label": "Disable", "name": "disable"}, {"description": "Add a HPKP header to each a HTTP response", "help": "Add a HPKP header to each a HTTP response.", "label": "Enable", "name": "enable"}, {"description": "Add a HPKP Report-Only header to each HTTP response", "help": "Add a HPKP Report-Only header to each HTTP response.", "label": "Report Only", "name": "report-only"}]
VALID_BODY_SSL_HPKP_INCLUDE_SUBDOMAINS: Literal[{"description": "HPKP header does not apply to subdomains", "help": "HPKP header does not apply to subdomains.", "label": "Disable", "name": "disable"}, {"description": "HPKP header applies to subdomains", "help": "HPKP header applies to subdomains.", "label": "Enable", "name": "enable"}]
VALID_BODY_SSL_HSTS: Literal[{"description": "Do not add a HSTS header to each a HTTP response", "help": "Do not add a HSTS header to each a HTTP response.", "label": "Disable", "name": "disable"}, {"description": "Add a HSTS header to each HTTP response", "help": "Add a HSTS header to each HTTP response.", "label": "Enable", "name": "enable"}]
VALID_BODY_SSL_HSTS_INCLUDE_SUBDOMAINS: Literal[{"description": "HSTS header does not apply to subdomains", "help": "HSTS header does not apply to subdomains.", "label": "Disable", "name": "disable"}, {"description": "HSTS header applies to subdomains", "help": "HSTS header applies to subdomains.", "label": "Enable", "name": "enable"}]
VALID_BODY_ONE_CLICK_GSLB_SERVER: Literal[{"description": "Disable integration with FortiGSLB", "help": "Disable integration with FortiGSLB.", "label": "Disable", "name": "disable"}, {"description": "Enable integration with FortiGSLB", "help": "Enable integration with FortiGSLB.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_SERVER_TYPE",
    "VALID_BODY_LDB_METHOD",
    "VALID_BODY_SRC_VIP_FILTER",
    "VALID_BODY_H2_SUPPORT",
    "VALID_BODY_H3_SUPPORT",
    "VALID_BODY_NAT44",
    "VALID_BODY_NAT46",
    "VALID_BODY_ADD_NAT46_ROUTE",
    "VALID_BODY_ARP_REPLY",
    "VALID_BODY_HTTP_REDIRECT",
    "VALID_BODY_PERSISTENCE",
    "VALID_BODY_NAT_SOURCE_VIP",
    "VALID_BODY_PORTFORWARD",
    "VALID_BODY_STATUS",
    "VALID_BODY_PROTOCOL",
    "VALID_BODY_PORTMAPPING_TYPE",
    "VALID_BODY_EMPTY_CERT_ACTION",
    "VALID_BODY_USER_AGENT_DETECT",
    "VALID_BODY_CLIENT_CERT",
    "VALID_BODY_HTTP_COOKIE_DOMAIN_FROM_HOST",
    "VALID_BODY_HTTP_COOKIE_SHARE",
    "VALID_BODY_HTTPS_COOKIE_SECURE",
    "VALID_BODY_HTTP_MULTIPLEX",
    "VALID_BODY_HTTP_IP_HEADER",
    "VALID_BODY_OUTLOOK_WEB_ACCESS",
    "VALID_BODY_WEBLOGIC_SERVER",
    "VALID_BODY_WEBSPHERE_SERVER",
    "VALID_BODY_SSL_MODE",
    "VALID_BODY_SSL_DH_BITS",
    "VALID_BODY_SSL_ALGORITHM",
    "VALID_BODY_SSL_SERVER_ALGORITHM",
    "VALID_BODY_SSL_PFS",
    "VALID_BODY_SSL_MIN_VERSION",
    "VALID_BODY_SSL_MAX_VERSION",
    "VALID_BODY_SSL_SERVER_MIN_VERSION",
    "VALID_BODY_SSL_SERVER_MAX_VERSION",
    "VALID_BODY_SSL_ACCEPT_FFDHE_GROUPS",
    "VALID_BODY_SSL_SEND_EMPTY_FRAGS",
    "VALID_BODY_SSL_CLIENT_FALLBACK",
    "VALID_BODY_SSL_CLIENT_RENEGOTIATION",
    "VALID_BODY_SSL_CLIENT_SESSION_STATE_TYPE",
    "VALID_BODY_SSL_SERVER_RENEGOTIATION",
    "VALID_BODY_SSL_SERVER_SESSION_STATE_TYPE",
    "VALID_BODY_SSL_HTTP_LOCATION_CONVERSION",
    "VALID_BODY_SSL_HTTP_MATCH_HOST",
    "VALID_BODY_SSL_HPKP",
    "VALID_BODY_SSL_HPKP_INCLUDE_SUBDOMAINS",
    "VALID_BODY_SSL_HSTS",
    "VALID_BODY_SSL_HSTS_INCLUDE_SUBDOMAINS",
    "VALID_BODY_ONE_CLICK_GSLB_SERVER",
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