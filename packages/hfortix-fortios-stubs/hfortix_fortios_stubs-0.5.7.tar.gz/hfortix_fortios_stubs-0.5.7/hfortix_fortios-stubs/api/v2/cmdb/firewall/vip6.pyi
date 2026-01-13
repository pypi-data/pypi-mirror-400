from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class Vip6Payload(TypedDict, total=False):
    """
    Type hints for firewall/vip6 payload fields.
    
    Configure virtual IP for IPv6.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.vpn.certificate.ca.CaEndpoint` (via: ssl-hpkp-backup, ssl-hpkp-primary)
        - :class:`~.vpn.certificate.local.LocalEndpoint` (via: ssl-hpkp-backup, ssl-hpkp-primary)

    **Usage:**
        payload: Vip6Payload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Virtual ip6 name.
    id: NotRequired[int]  # Custom defined ID.
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    comment: NotRequired[str]  # Comment.
    type: NotRequired[Literal[{"description": "Static NAT", "help": "Static NAT.", "label": "Static Nat", "name": "static-nat"}, {"description": "Server load balance", "help": "Server load balance.", "label": "Server Load Balance", "name": "server-load-balance"}, {"description": "Access proxy", "help": "Access proxy.", "label": "Access Proxy", "name": "access-proxy"}]]  # Configure a static NAT server load balance VIP or access pro
    src_filter: NotRequired[list[dict[str, Any]]]  # Source IP6 filter (x:x:x:x:x:x:x:x/x). Separate addresses wi
    src_vip_filter: NotRequired[Literal[{"description": "Match any destination for the reverse SNAT rule", "help": "Match any destination for the reverse SNAT rule.", "label": "Disable", "name": "disable"}, {"description": "Match only destinations in \u0027src-filter\u0027 for the reverse SNAT rule", "help": "Match only destinations in \u0027src-filter\u0027 for the reverse SNAT rule.", "label": "Enable", "name": "enable"}]]  # Enable/disable use of 'src-filter' to match destinations for
    extip: str  # IPv6 address or address range on the external interface that
    mappedip: str  # Mapped IPv6 address range in the format startIP-endIP.
    nat_source_vip: NotRequired[Literal[{"description": "Disable nat-source-vip", "help": "Disable nat-source-vip.", "label": "Disable", "name": "disable"}, {"description": "Perform SNAT on traffic from mappedip to the extip for all egress interfaces", "help": "Perform SNAT on traffic from mappedip to the extip for all egress interfaces.", "label": "Enable", "name": "enable"}]]  # Enable to perform SNAT on traffic from mappedip to the extip
    ndp_reply: NotRequired[Literal[{"description": "Disable this FortiGate unit\u0027s ability to respond to NDP requests for this virtual IP address", "help": "Disable this FortiGate unit\u0027s ability to respond to NDP requests for this virtual IP address.", "label": "Disable", "name": "disable"}, {"description": "Enable this FortiGate unit\u0027s ability to respond to NDP requests for this virtual IP address", "help": "Enable this FortiGate unit\u0027s ability to respond to NDP requests for this virtual IP address.", "label": "Enable", "name": "enable"}]]  # Enable/disable this FortiGate unit's ability to respond to N
    portforward: NotRequired[Literal[{"description": "Disable port forward", "help": "Disable port forward.", "label": "Disable", "name": "disable"}, {"description": "Enable/disable port forwarding", "help": "Enable/disable port forwarding.", "label": "Enable", "name": "enable"}]]  # Enable port forwarding.
    protocol: NotRequired[Literal[{"description": "TCP", "help": "TCP.", "label": "Tcp", "name": "tcp"}, {"description": "UDP", "help": "UDP.", "label": "Udp", "name": "udp"}, {"description": "SCTP", "help": "SCTP.", "label": "Sctp", "name": "sctp"}]]  # Protocol to use when forwarding packets.
    extport: str  # Incoming port number range that you want to map to a port nu
    mappedport: NotRequired[str]  # Port number range on the destination network to which the ex
    color: NotRequired[int]  # Color of icon on the GUI.
    ldb_method: NotRequired[Literal[{"description": "Distribute sessions based on source IP", "help": "Distribute sessions based on source IP.", "label": "Static", "name": "static"}, {"description": "Distribute sessions based round robin order", "help": "Distribute sessions based round robin order.", "label": "Round Robin", "name": "round-robin"}, {"description": "Distribute sessions based on weight", "help": "Distribute sessions based on weight.", "label": "Weighted", "name": "weighted"}, {"description": "Sends new sessions to the server with the lowest session count", "help": "Sends new sessions to the server with the lowest session count.", "label": "Least Session", "name": "least-session"}, {"description": "Distribute new sessions to the server with lowest Round-Trip-Time", "help": "Distribute new sessions to the server with lowest Round-Trip-Time.", "label": "Least Rtt", "name": "least-rtt"}, {"description": "Distribute sessions to the first server that is alive", "help": "Distribute sessions to the first server that is alive.", "label": "First Alive", "name": "first-alive"}, {"description": "Distribute sessions to servers based on host field in HTTP header", "help": "Distribute sessions to servers based on host field in HTTP header.", "label": "Http Host", "name": "http-host"}]]  # Method used to distribute sessions to real servers.
    server_type: Literal[{"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"help": "SSL.", "label": "Ssl", "name": "ssl"}, {"description": "TCP", "help": "TCP.", "label": "Tcp", "name": "tcp"}, {"description": "UDP", "help": "UDP.", "label": "Udp", "name": "udp"}, {"description": "IP", "help": "IP.", "label": "Ip", "name": "ip"}]  # Protocol to be load balanced by the virtual server (also cal
    http_redirect: NotRequired[Literal[{"description": "Enable redirection of HTTP to HTTPS", "help": "Enable redirection of HTTP to HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable redirection of HTTP to HTTPS", "help": "Disable redirection of HTTP to HTTPS.", "label": "Disable", "name": "disable"}]]  # Enable/disable redirection of HTTP to HTTPS.
    persistence: NotRequired[Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "HTTP cookie", "help": "HTTP cookie.", "label": "Http Cookie", "name": "http-cookie"}, {"description": "SSL session ID", "help": "SSL session ID.", "label": "Ssl Session Id", "name": "ssl-session-id"}]]  # Configure how to make sure that clients connect to the same 
    h2_support: Literal[{"description": "Enable HTTP2 support", "help": "Enable HTTP2 support.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP2 support", "help": "Disable HTTP2 support.", "label": "Disable", "name": "disable"}]  # Enable/disable HTTP2 support (default = enable).
    h3_support: NotRequired[Literal[{"description": "Enable HTTP3/QUIC support", "help": "Enable HTTP3/QUIC support.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP3/QUIC support", "help": "Disable HTTP3/QUIC support.", "label": "Disable", "name": "disable"}]]  # Enable/disable HTTP3/QUIC support (default = disable).
    quic: NotRequired[str]  # QUIC setting.
    nat66: NotRequired[Literal[{"description": "Disable DNAT66", "help": "Disable DNAT66.", "label": "Disable", "name": "disable"}, {"description": "Enable DNAT66", "help": "Enable DNAT66.", "label": "Enable", "name": "enable"}]]  # Enable/disable DNAT66.
    nat64: NotRequired[Literal[{"description": "Disable DNAT64", "help": "Disable DNAT64.", "label": "Disable", "name": "disable"}, {"description": "Enable DNAT64", "help": "Enable DNAT64.", "label": "Enable", "name": "enable"}]]  # Enable/disable DNAT64.
    add_nat64_route: NotRequired[Literal[{"description": "Disable adding NAT64 route", "help": "Disable adding NAT64 route.", "label": "Disable", "name": "disable"}, {"description": "Enable adding NAT64 route", "help": "Enable adding NAT64 route.", "label": "Enable", "name": "enable"}]]  # Enable/disable adding NAT64 route.
    empty_cert_action: NotRequired[Literal[{"description": "Accept the SSL handshake if the client certificate is empty", "help": "Accept the SSL handshake if the client certificate is empty.", "label": "Accept", "name": "accept"}, {"description": "Block the SSL handshake if the client certificate is empty", "help": "Block the SSL handshake if the client certificate is empty.", "label": "Block", "name": "block"}, {"description": "Accept the SSL handshake only if the end-point is unmanageable", "help": "Accept the SSL handshake only if the end-point is unmanageable.", "label": "Accept Unmanageable", "name": "accept-unmanageable"}]]  # Action for an empty client certificate.
    user_agent_detect: NotRequired[Literal[{"description": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Disable", "name": "disable"}, {"description": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Enable", "name": "enable"}]]  # Enable/disable detecting device type by HTTP user-agent if n
    client_cert: NotRequired[Literal[{"description": "Disable client certificate request", "help": "Disable client certificate request.", "label": "Disable", "name": "disable"}, {"description": "Enable client certificate request", "help": "Enable client certificate request.", "label": "Enable", "name": "enable"}]]  # Enable/disable requesting client certificate.
    realservers: NotRequired[list[dict[str, Any]]]  # Select the real servers that this server load balancing VIP 
    http_cookie_domain_from_host: NotRequired[Literal[{"description": "Disable use of HTTP cookie domain from host field in HTTP (use http-cooke-domain setting)", "help": "Disable use of HTTP cookie domain from host field in HTTP (use http-cooke-domain setting).", "label": "Disable", "name": "disable"}, {"description": "Enable use of HTTP cookie domain from host field in HTTP", "help": "Enable use of HTTP cookie domain from host field in HTTP.", "label": "Enable", "name": "enable"}]]  # Enable/disable use of HTTP cookie domain from host field in 
    http_cookie_domain: NotRequired[str]  # Domain that HTTP cookie persistence should apply to.
    http_cookie_path: NotRequired[str]  # Limit HTTP cookie persistence to the specified path.
    http_cookie_generation: NotRequired[int]  # Generation of HTTP cookie to be accepted. Changing invalidat
    http_cookie_age: NotRequired[int]  # Time in minutes that client web browsers should keep a cooki
    http_cookie_share: NotRequired[Literal[{"description": "Only allow HTTP cookie to match this virtual server", "help": "Only allow HTTP cookie to match this virtual server.", "label": "Disable", "name": "disable"}, {"description": "Allow HTTP cookie to match any virtual server with same IP", "help": "Allow HTTP cookie to match any virtual server with same IP.", "label": "Same Ip", "name": "same-ip"}]]  # Control sharing of cookies across virtual servers. Use of sa
    https_cookie_secure: NotRequired[Literal[{"description": "Do not mark cookie as secure, allow sharing between an HTTP and HTTPS connection", "help": "Do not mark cookie as secure, allow sharing between an HTTP and HTTPS connection.", "label": "Disable", "name": "disable"}, {"description": "Mark inserted cookie as secure, cookie can only be used for HTTPS a connection", "help": "Mark inserted cookie as secure, cookie can only be used for HTTPS a connection.", "label": "Enable", "name": "enable"}]]  # Enable/disable verification that inserted HTTPS cookies are 
    http_multiplex: NotRequired[Literal[{"description": "Enable HTTP session multiplexing", "help": "Enable HTTP session multiplexing.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP session multiplexing", "help": "Disable HTTP session multiplexing.", "label": "Disable", "name": "disable"}]]  # Enable/disable HTTP multiplexing.
    http_ip_header: NotRequired[Literal[{"description": "Enable adding HTTP header", "help": "Enable adding HTTP header.", "label": "Enable", "name": "enable"}, {"description": "Disable adding HTTP header", "help": "Disable adding HTTP header.", "label": "Disable", "name": "disable"}]]  # For HTTP multiplexing, enable to add the original client IP 
    http_ip_header_name: NotRequired[str]  # For HTTP multiplexing, enter a custom HTTPS header name. The
    outlook_web_access: NotRequired[Literal[{"description": "Disable Outlook Web Access support", "help": "Disable Outlook Web Access support.", "label": "Disable", "name": "disable"}, {"description": "Enable Outlook Web Access support", "help": "Enable Outlook Web Access support.", "label": "Enable", "name": "enable"}]]  # Enable to add the Front-End-Https header for Microsoft Outlo
    weblogic_server: NotRequired[Literal[{"description": "Do not add HTTP header indicating SSL offload for WebLogic server", "help": "Do not add HTTP header indicating SSL offload for WebLogic server.", "label": "Disable", "name": "disable"}, {"description": "Add HTTP header indicating SSL offload for WebLogic server", "help": "Add HTTP header indicating SSL offload for WebLogic server.", "label": "Enable", "name": "enable"}]]  # Enable to add an HTTP header to indicate SSL offloading for 
    websphere_server: NotRequired[Literal[{"description": "Do not add HTTP header indicating SSL offload for WebSphere server", "help": "Do not add HTTP header indicating SSL offload for WebSphere server.", "label": "Disable", "name": "disable"}, {"description": "Add HTTP header indicating SSL offload for WebSphere server", "help": "Add HTTP header indicating SSL offload for WebSphere server.", "label": "Enable", "name": "enable"}]]  # Enable to add an HTTP header to indicate SSL offloading for 
    ssl_mode: NotRequired[Literal[{"description": "Client to FortiGate SSL", "help": "Client to FortiGate SSL.", "label": "Half", "name": "half"}, {"description": "Client to FortiGate and FortiGate to Server SSL", "help": "Client to FortiGate and FortiGate to Server SSL.", "label": "Full", "name": "full"}]]  # Apply SSL offloading between the client and the FortiGate (h
    ssl_certificate: list[dict[str, Any]]  # Name of the certificate to use for SSL handshake.
    ssl_dh_bits: NotRequired[Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}, {"description": "3072-bit Diffie-Hellman prime", "help": "3072-bit Diffie-Hellman prime.", "label": "3072", "name": "3072"}, {"description": "4096-bit Diffie-Hellman prime", "help": "4096-bit Diffie-Hellman prime.", "label": "4096", "name": "4096"}]]  # Number of bits to use in the Diffie-Hellman exchange for RSA
    ssl_algorithm: NotRequired[Literal[{"description": "Use AES", "help": "Use AES.", "label": "High", "name": "high"}, {"description": "Use AES, 3DES, or RC4", "help": "Use AES, 3DES, or RC4.", "label": "Medium", "name": "medium"}, {"description": "Use AES, 3DES, RC4, or DES", "help": "Use AES, 3DES, RC4, or DES.", "label": "Low", "name": "low"}, {"description": "Use config ssl-cipher-suites to select the cipher suites that are allowed", "help": "Use config ssl-cipher-suites to select the cipher suites that are allowed.", "label": "Custom", "name": "custom"}]]  # Permitted encryption algorithms for SSL sessions according t
    ssl_cipher_suites: NotRequired[list[dict[str, Any]]]  # SSL/TLS cipher suites acceptable from a client, ordered by p
    ssl_server_renegotiation: NotRequired[Literal[{"description": "Enable secure renegotiation", "help": "Enable secure renegotiation.", "label": "Enable", "name": "enable"}, {"description": "Disable secure renegotiation", "help": "Disable secure renegotiation.", "label": "Disable", "name": "disable"}]]  # Enable/disable secure renegotiation to comply with RFC 5746.
    ssl_server_algorithm: NotRequired[Literal[{"description": "Use AES", "help": "Use AES.", "label": "High", "name": "high"}, {"description": "Use AES, 3DES, or RC4", "help": "Use AES, 3DES, or RC4.", "label": "Medium", "name": "medium"}, {"description": "Use AES, 3DES, RC4, or DES", "help": "Use AES, 3DES, RC4, or DES.", "label": "Low", "name": "low"}, {"description": "Use config ssl-server-cipher-suites to select the cipher suites that are allowed", "help": "Use config ssl-server-cipher-suites to select the cipher suites that are allowed.", "label": "Custom", "name": "custom"}, {"description": "Use the same encryption algorithms for client and server sessions", "help": "Use the same encryption algorithms for client and server sessions.", "label": "Client", "name": "client"}]]  # Permitted encryption algorithms for the server side of SSL f
    ssl_server_cipher_suites: NotRequired[list[dict[str, Any]]]  # SSL/TLS cipher suites to offer to a server, ordered by prior
    ssl_pfs: NotRequired[Literal[{"description": "Allow only Diffie-Hellman cipher-suites, so PFS is applied", "help": "Allow only Diffie-Hellman cipher-suites, so PFS is applied.", "label": "Require", "name": "require"}, {"description": "Allow only non-Diffie-Hellman cipher-suites, so PFS is not applied", "help": "Allow only non-Diffie-Hellman cipher-suites, so PFS is not applied.", "label": "Deny", "name": "deny"}, {"description": "Allow use of any cipher suite so PFS may or may not be used depending on the cipher suite selected", "help": "Allow use of any cipher suite so PFS may or may not be used depending on the cipher suite selected.", "label": "Allow", "name": "allow"}]]  # Select the cipher suites that can be used for SSL perfect fo
    ssl_min_version: NotRequired[Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}]]  # Lowest SSL/TLS version acceptable from a client.
    ssl_max_version: NotRequired[Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}]]  # Highest SSL/TLS version acceptable from a client.
    ssl_server_min_version: NotRequired[Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}, {"description": "Use same value as client configuration", "help": "Use same value as client configuration.", "label": "Client", "name": "client"}]]  # Lowest SSL/TLS version acceptable from a server. Use the cli
    ssl_server_max_version: NotRequired[Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}, {"description": "Use same value as client configuration", "help": "Use same value as client configuration.", "label": "Client", "name": "client"}]]  # Highest SSL/TLS version acceptable from a server. Use the cl
    ssl_accept_ffdhe_groups: NotRequired[Literal[{"description": "Accept FFDHE groups", "help": "Accept FFDHE groups.", "label": "Enable", "name": "enable"}, {"description": "Do not accept FFDHE groups", "help": "Do not accept FFDHE groups.", "label": "Disable", "name": "disable"}]]  # Enable/disable FFDHE cipher suite for SSL key exchange.
    ssl_send_empty_frags: NotRequired[Literal[{"description": "Send empty fragments", "help": "Send empty fragments.", "label": "Enable", "name": "enable"}, {"description": "Do not send empty fragments", "help": "Do not send empty fragments.", "label": "Disable", "name": "disable"}]]  # Enable/disable sending empty fragments to avoid CBC IV attac
    ssl_client_fallback: NotRequired[Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Enable", "help": "Enable.", "label": "Enable", "name": "enable"}]]  # Enable/disable support for preventing Downgrade Attacks on c
    ssl_client_renegotiation: NotRequired[Literal[{"description": "Allow a SSL client to renegotiate", "help": "Allow a SSL client to renegotiate.", "label": "Allow", "name": "allow"}, {"description": "Abort any SSL connection that attempts to renegotiate", "help": "Abort any SSL connection that attempts to renegotiate.", "label": "Deny", "name": "deny"}, {"description": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication", "help": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication.", "label": "Secure", "name": "secure"}]]  # Allow, deny, or require secure renegotiation of client sessi
    ssl_client_session_state_type: NotRequired[Literal[{"description": "Do not keep session states", "help": "Do not keep session states.", "label": "Disable", "name": "disable"}, {"description": "Expire session states after this many minutes", "help": "Expire session states after this many minutes.", "label": "Time", "name": "time"}, {"description": "Expire session states when this maximum is reached", "help": "Expire session states when this maximum is reached.", "label": "Count", "name": "count"}, {"description": "Expire session states based on time or count, whichever occurs first", "help": "Expire session states based on time or count, whichever occurs first.", "label": "Both", "name": "both"}]]  # How to expire SSL sessions for the segment of the SSL connec
    ssl_client_session_state_timeout: NotRequired[int]  # Number of minutes to keep client to FortiGate SSL session st
    ssl_client_session_state_max: NotRequired[int]  # Maximum number of client to FortiGate SSL session states to 
    ssl_client_rekey_count: NotRequired[int]  # Maximum length of data in MB before triggering a client reke
    ssl_server_session_state_type: NotRequired[Literal[{"description": "Do not keep session states", "help": "Do not keep session states.", "label": "Disable", "name": "disable"}, {"description": "Expire session states after this many minutes", "help": "Expire session states after this many minutes.", "label": "Time", "name": "time"}, {"description": "Expire session states when this maximum is reached", "help": "Expire session states when this maximum is reached.", "label": "Count", "name": "count"}, {"description": "Expire session states based on time or count, whichever occurs first", "help": "Expire session states based on time or count, whichever occurs first.", "label": "Both", "name": "both"}]]  # How to expire SSL sessions for the segment of the SSL connec
    ssl_server_session_state_timeout: NotRequired[int]  # Number of minutes to keep FortiGate to Server SSL session st
    ssl_server_session_state_max: NotRequired[int]  # Maximum number of FortiGate to Server SSL session states to 
    ssl_http_location_conversion: NotRequired[Literal[{"description": "Enable HTTP location conversion", "help": "Enable HTTP location conversion.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP location conversion", "help": "Disable HTTP location conversion.", "label": "Disable", "name": "disable"}]]  # Enable to replace HTTP with HTTPS in the reply's Location HT
    ssl_http_match_host: NotRequired[Literal[{"description": "Match HTTP host in response header", "help": "Match HTTP host in response header.", "label": "Enable", "name": "enable"}, {"description": "Do not match HTTP host", "help": "Do not match HTTP host.", "label": "Disable", "name": "disable"}]]  # Enable/disable HTTP host matching for location conversion.
    ssl_hpkp: NotRequired[Literal[{"description": "Do not add a HPKP header to each HTTP response", "help": "Do not add a HPKP header to each HTTP response.", "label": "Disable", "name": "disable"}, {"description": "Add a HPKP header to each a HTTP response", "help": "Add a HPKP header to each a HTTP response.", "label": "Enable", "name": "enable"}, {"description": "Add a HPKP Report-Only header to each HTTP response", "help": "Add a HPKP Report-Only header to each HTTP response.", "label": "Report Only", "name": "report-only"}]]  # Enable/disable including HPKP header in response.
    ssl_hpkp_primary: NotRequired[str]  # Certificate to generate primary HPKP pin from.
    ssl_hpkp_backup: NotRequired[str]  # Certificate to generate backup HPKP pin from.
    ssl_hpkp_age: NotRequired[int]  # Number of minutes the web browser should keep HPKP.
    ssl_hpkp_report_uri: NotRequired[str]  # URL to report HPKP violations to.
    ssl_hpkp_include_subdomains: NotRequired[Literal[{"description": "HPKP header does not apply to subdomains", "help": "HPKP header does not apply to subdomains.", "label": "Disable", "name": "disable"}, {"description": "HPKP header applies to subdomains", "help": "HPKP header applies to subdomains.", "label": "Enable", "name": "enable"}]]  # Indicate that HPKP header applies to all subdomains.
    ssl_hsts: NotRequired[Literal[{"description": "Do not add a HSTS header to each a HTTP response", "help": "Do not add a HSTS header to each a HTTP response.", "label": "Disable", "name": "disable"}, {"description": "Add a HSTS header to each HTTP response", "help": "Add a HSTS header to each HTTP response.", "label": "Enable", "name": "enable"}]]  # Enable/disable including HSTS header in response.
    ssl_hsts_age: NotRequired[int]  # Number of seconds the client should honor the HSTS setting.
    ssl_hsts_include_subdomains: NotRequired[Literal[{"description": "HSTS header does not apply to subdomains", "help": "HSTS header does not apply to subdomains.", "label": "Disable", "name": "disable"}, {"description": "HSTS header applies to subdomains", "help": "HSTS header applies to subdomains.", "label": "Enable", "name": "enable"}]]  # Indicate that HSTS header applies to all subdomains.
    monitor: NotRequired[list[dict[str, Any]]]  # Name of the health check monitor to use when polling to dete
    max_embryonic_connections: NotRequired[int]  # Maximum number of incomplete connections.
    embedded_ipv4_address: NotRequired[Literal[{"description": "Disable use of the lower 32 bits of the external IPv6 address as mapped IPv4 address", "help": "Disable use of the lower 32 bits of the external IPv6 address as mapped IPv4 address.", "label": "Disable", "name": "disable"}, {"description": "Enable use of the lower 32 bits of the external IPv6 address as mapped IPv4 address", "help": "Enable use of the lower 32 bits of the external IPv6 address as mapped IPv4 address.", "label": "Enable", "name": "enable"}]]  # Enable/disable use of the lower 32 bits of the external IPv6
    ipv4_mappedip: NotRequired[str]  # Range of mapped IP addresses. Specify the start IP address f
    ipv4_mappedport: NotRequired[str]  # IPv4 port number range on the destination network to which t


class Vip6:
    """
    Configure virtual IP for IPv6.
    
    Path: firewall/vip6
    Category: cmdb
    Primary Key: name
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: Literal[False] = ...,
        response_mode: Literal["object"] = ...,
        **kwargs: Any,
    ) -> list[FortiObject]: ...
    
    @overload
    def get(
        self,
        name: str,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: Literal[False] = ...,
        response_mode: Literal["object"] = ...,
        **kwargs: Any,
    ) -> FortiObject: ...
    
    @overload
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: Literal[True] = ...,
        response_mode: Literal["object"] = ...,
        **kwargs: Any,
    ) -> dict[str, Any]: ...
    
    # Default overload for dict mode
    @overload
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        response_mode: Literal["dict"] | None = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], list[dict[str, Any]]]: ...
    
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        response_mode: str | None = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], list[dict[str, Any]], FortiObject, list[FortiObject]]: ...
    
    def get_schema(
        self,
        vdom: str | None = ...,
        format: str = ...,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def post(
        self,
        payload_dict: Vip6Payload | None = ...,
        name: str | None = ...,
        id: int | None = ...,
        uuid: str | None = ...,
        comment: str | None = ...,
        type: Literal[{"description": "Static NAT", "help": "Static NAT.", "label": "Static Nat", "name": "static-nat"}, {"description": "Server load balance", "help": "Server load balance.", "label": "Server Load Balance", "name": "server-load-balance"}, {"description": "Access proxy", "help": "Access proxy.", "label": "Access Proxy", "name": "access-proxy"}] | None = ...,
        src_filter: list[dict[str, Any]] | None = ...,
        src_vip_filter: Literal[{"description": "Match any destination for the reverse SNAT rule", "help": "Match any destination for the reverse SNAT rule.", "label": "Disable", "name": "disable"}, {"description": "Match only destinations in \u0027src-filter\u0027 for the reverse SNAT rule", "help": "Match only destinations in \u0027src-filter\u0027 for the reverse SNAT rule.", "label": "Enable", "name": "enable"}] | None = ...,
        extip: str | None = ...,
        mappedip: str | None = ...,
        nat_source_vip: Literal[{"description": "Disable nat-source-vip", "help": "Disable nat-source-vip.", "label": "Disable", "name": "disable"}, {"description": "Perform SNAT on traffic from mappedip to the extip for all egress interfaces", "help": "Perform SNAT on traffic from mappedip to the extip for all egress interfaces.", "label": "Enable", "name": "enable"}] | None = ...,
        ndp_reply: Literal[{"description": "Disable this FortiGate unit\u0027s ability to respond to NDP requests for this virtual IP address", "help": "Disable this FortiGate unit\u0027s ability to respond to NDP requests for this virtual IP address.", "label": "Disable", "name": "disable"}, {"description": "Enable this FortiGate unit\u0027s ability to respond to NDP requests for this virtual IP address", "help": "Enable this FortiGate unit\u0027s ability to respond to NDP requests for this virtual IP address.", "label": "Enable", "name": "enable"}] | None = ...,
        portforward: Literal[{"description": "Disable port forward", "help": "Disable port forward.", "label": "Disable", "name": "disable"}, {"description": "Enable/disable port forwarding", "help": "Enable/disable port forwarding.", "label": "Enable", "name": "enable"}] | None = ...,
        protocol: Literal[{"description": "TCP", "help": "TCP.", "label": "Tcp", "name": "tcp"}, {"description": "UDP", "help": "UDP.", "label": "Udp", "name": "udp"}, {"description": "SCTP", "help": "SCTP.", "label": "Sctp", "name": "sctp"}] | None = ...,
        extport: str | None = ...,
        mappedport: str | None = ...,
        color: int | None = ...,
        ldb_method: Literal[{"description": "Distribute sessions based on source IP", "help": "Distribute sessions based on source IP.", "label": "Static", "name": "static"}, {"description": "Distribute sessions based round robin order", "help": "Distribute sessions based round robin order.", "label": "Round Robin", "name": "round-robin"}, {"description": "Distribute sessions based on weight", "help": "Distribute sessions based on weight.", "label": "Weighted", "name": "weighted"}, {"description": "Sends new sessions to the server with the lowest session count", "help": "Sends new sessions to the server with the lowest session count.", "label": "Least Session", "name": "least-session"}, {"description": "Distribute new sessions to the server with lowest Round-Trip-Time", "help": "Distribute new sessions to the server with lowest Round-Trip-Time.", "label": "Least Rtt", "name": "least-rtt"}, {"description": "Distribute sessions to the first server that is alive", "help": "Distribute sessions to the first server that is alive.", "label": "First Alive", "name": "first-alive"}, {"description": "Distribute sessions to servers based on host field in HTTP header", "help": "Distribute sessions to servers based on host field in HTTP header.", "label": "Http Host", "name": "http-host"}] | None = ...,
        server_type: Literal[{"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"help": "SSL.", "label": "Ssl", "name": "ssl"}, {"description": "TCP", "help": "TCP.", "label": "Tcp", "name": "tcp"}, {"description": "UDP", "help": "UDP.", "label": "Udp", "name": "udp"}, {"description": "IP", "help": "IP.", "label": "Ip", "name": "ip"}] | None = ...,
        http_redirect: Literal[{"description": "Enable redirection of HTTP to HTTPS", "help": "Enable redirection of HTTP to HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable redirection of HTTP to HTTPS", "help": "Disable redirection of HTTP to HTTPS.", "label": "Disable", "name": "disable"}] | None = ...,
        persistence: Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "HTTP cookie", "help": "HTTP cookie.", "label": "Http Cookie", "name": "http-cookie"}, {"description": "SSL session ID", "help": "SSL session ID.", "label": "Ssl Session Id", "name": "ssl-session-id"}] | None = ...,
        h2_support: Literal[{"description": "Enable HTTP2 support", "help": "Enable HTTP2 support.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP2 support", "help": "Disable HTTP2 support.", "label": "Disable", "name": "disable"}] | None = ...,
        h3_support: Literal[{"description": "Enable HTTP3/QUIC support", "help": "Enable HTTP3/QUIC support.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP3/QUIC support", "help": "Disable HTTP3/QUIC support.", "label": "Disable", "name": "disable"}] | None = ...,
        quic: str | None = ...,
        nat66: Literal[{"description": "Disable DNAT66", "help": "Disable DNAT66.", "label": "Disable", "name": "disable"}, {"description": "Enable DNAT66", "help": "Enable DNAT66.", "label": "Enable", "name": "enable"}] | None = ...,
        nat64: Literal[{"description": "Disable DNAT64", "help": "Disable DNAT64.", "label": "Disable", "name": "disable"}, {"description": "Enable DNAT64", "help": "Enable DNAT64.", "label": "Enable", "name": "enable"}] | None = ...,
        add_nat64_route: Literal[{"description": "Disable adding NAT64 route", "help": "Disable adding NAT64 route.", "label": "Disable", "name": "disable"}, {"description": "Enable adding NAT64 route", "help": "Enable adding NAT64 route.", "label": "Enable", "name": "enable"}] | None = ...,
        empty_cert_action: Literal[{"description": "Accept the SSL handshake if the client certificate is empty", "help": "Accept the SSL handshake if the client certificate is empty.", "label": "Accept", "name": "accept"}, {"description": "Block the SSL handshake if the client certificate is empty", "help": "Block the SSL handshake if the client certificate is empty.", "label": "Block", "name": "block"}, {"description": "Accept the SSL handshake only if the end-point is unmanageable", "help": "Accept the SSL handshake only if the end-point is unmanageable.", "label": "Accept Unmanageable", "name": "accept-unmanageable"}] | None = ...,
        user_agent_detect: Literal[{"description": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Disable", "name": "disable"}, {"description": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Enable", "name": "enable"}] | None = ...,
        client_cert: Literal[{"description": "Disable client certificate request", "help": "Disable client certificate request.", "label": "Disable", "name": "disable"}, {"description": "Enable client certificate request", "help": "Enable client certificate request.", "label": "Enable", "name": "enable"}] | None = ...,
        realservers: list[dict[str, Any]] | None = ...,
        http_cookie_domain_from_host: Literal[{"description": "Disable use of HTTP cookie domain from host field in HTTP (use http-cooke-domain setting)", "help": "Disable use of HTTP cookie domain from host field in HTTP (use http-cooke-domain setting).", "label": "Disable", "name": "disable"}, {"description": "Enable use of HTTP cookie domain from host field in HTTP", "help": "Enable use of HTTP cookie domain from host field in HTTP.", "label": "Enable", "name": "enable"}] | None = ...,
        http_cookie_domain: str | None = ...,
        http_cookie_path: str | None = ...,
        http_cookie_generation: int | None = ...,
        http_cookie_age: int | None = ...,
        http_cookie_share: Literal[{"description": "Only allow HTTP cookie to match this virtual server", "help": "Only allow HTTP cookie to match this virtual server.", "label": "Disable", "name": "disable"}, {"description": "Allow HTTP cookie to match any virtual server with same IP", "help": "Allow HTTP cookie to match any virtual server with same IP.", "label": "Same Ip", "name": "same-ip"}] | None = ...,
        https_cookie_secure: Literal[{"description": "Do not mark cookie as secure, allow sharing between an HTTP and HTTPS connection", "help": "Do not mark cookie as secure, allow sharing between an HTTP and HTTPS connection.", "label": "Disable", "name": "disable"}, {"description": "Mark inserted cookie as secure, cookie can only be used for HTTPS a connection", "help": "Mark inserted cookie as secure, cookie can only be used for HTTPS a connection.", "label": "Enable", "name": "enable"}] | None = ...,
        http_multiplex: Literal[{"description": "Enable HTTP session multiplexing", "help": "Enable HTTP session multiplexing.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP session multiplexing", "help": "Disable HTTP session multiplexing.", "label": "Disable", "name": "disable"}] | None = ...,
        http_ip_header: Literal[{"description": "Enable adding HTTP header", "help": "Enable adding HTTP header.", "label": "Enable", "name": "enable"}, {"description": "Disable adding HTTP header", "help": "Disable adding HTTP header.", "label": "Disable", "name": "disable"}] | None = ...,
        http_ip_header_name: str | None = ...,
        outlook_web_access: Literal[{"description": "Disable Outlook Web Access support", "help": "Disable Outlook Web Access support.", "label": "Disable", "name": "disable"}, {"description": "Enable Outlook Web Access support", "help": "Enable Outlook Web Access support.", "label": "Enable", "name": "enable"}] | None = ...,
        weblogic_server: Literal[{"description": "Do not add HTTP header indicating SSL offload for WebLogic server", "help": "Do not add HTTP header indicating SSL offload for WebLogic server.", "label": "Disable", "name": "disable"}, {"description": "Add HTTP header indicating SSL offload for WebLogic server", "help": "Add HTTP header indicating SSL offload for WebLogic server.", "label": "Enable", "name": "enable"}] | None = ...,
        websphere_server: Literal[{"description": "Do not add HTTP header indicating SSL offload for WebSphere server", "help": "Do not add HTTP header indicating SSL offload for WebSphere server.", "label": "Disable", "name": "disable"}, {"description": "Add HTTP header indicating SSL offload for WebSphere server", "help": "Add HTTP header indicating SSL offload for WebSphere server.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_mode: Literal[{"description": "Client to FortiGate SSL", "help": "Client to FortiGate SSL.", "label": "Half", "name": "half"}, {"description": "Client to FortiGate and FortiGate to Server SSL", "help": "Client to FortiGate and FortiGate to Server SSL.", "label": "Full", "name": "full"}] | None = ...,
        ssl_certificate: list[dict[str, Any]] | None = ...,
        ssl_dh_bits: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}, {"description": "3072-bit Diffie-Hellman prime", "help": "3072-bit Diffie-Hellman prime.", "label": "3072", "name": "3072"}, {"description": "4096-bit Diffie-Hellman prime", "help": "4096-bit Diffie-Hellman prime.", "label": "4096", "name": "4096"}] | None = ...,
        ssl_algorithm: Literal[{"description": "Use AES", "help": "Use AES.", "label": "High", "name": "high"}, {"description": "Use AES, 3DES, or RC4", "help": "Use AES, 3DES, or RC4.", "label": "Medium", "name": "medium"}, {"description": "Use AES, 3DES, RC4, or DES", "help": "Use AES, 3DES, RC4, or DES.", "label": "Low", "name": "low"}, {"description": "Use config ssl-cipher-suites to select the cipher suites that are allowed", "help": "Use config ssl-cipher-suites to select the cipher suites that are allowed.", "label": "Custom", "name": "custom"}] | None = ...,
        ssl_cipher_suites: list[dict[str, Any]] | None = ...,
        ssl_server_renegotiation: Literal[{"description": "Enable secure renegotiation", "help": "Enable secure renegotiation.", "label": "Enable", "name": "enable"}, {"description": "Disable secure renegotiation", "help": "Disable secure renegotiation.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_server_algorithm: Literal[{"description": "Use AES", "help": "Use AES.", "label": "High", "name": "high"}, {"description": "Use AES, 3DES, or RC4", "help": "Use AES, 3DES, or RC4.", "label": "Medium", "name": "medium"}, {"description": "Use AES, 3DES, RC4, or DES", "help": "Use AES, 3DES, RC4, or DES.", "label": "Low", "name": "low"}, {"description": "Use config ssl-server-cipher-suites to select the cipher suites that are allowed", "help": "Use config ssl-server-cipher-suites to select the cipher suites that are allowed.", "label": "Custom", "name": "custom"}, {"description": "Use the same encryption algorithms for client and server sessions", "help": "Use the same encryption algorithms for client and server sessions.", "label": "Client", "name": "client"}] | None = ...,
        ssl_server_cipher_suites: list[dict[str, Any]] | None = ...,
        ssl_pfs: Literal[{"description": "Allow only Diffie-Hellman cipher-suites, so PFS is applied", "help": "Allow only Diffie-Hellman cipher-suites, so PFS is applied.", "label": "Require", "name": "require"}, {"description": "Allow only non-Diffie-Hellman cipher-suites, so PFS is not applied", "help": "Allow only non-Diffie-Hellman cipher-suites, so PFS is not applied.", "label": "Deny", "name": "deny"}, {"description": "Allow use of any cipher suite so PFS may or may not be used depending on the cipher suite selected", "help": "Allow use of any cipher suite so PFS may or may not be used depending on the cipher suite selected.", "label": "Allow", "name": "allow"}] | None = ...,
        ssl_min_version: Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}] | None = ...,
        ssl_max_version: Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}] | None = ...,
        ssl_server_min_version: Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}, {"description": "Use same value as client configuration", "help": "Use same value as client configuration.", "label": "Client", "name": "client"}] | None = ...,
        ssl_server_max_version: Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}, {"description": "Use same value as client configuration", "help": "Use same value as client configuration.", "label": "Client", "name": "client"}] | None = ...,
        ssl_accept_ffdhe_groups: Literal[{"description": "Accept FFDHE groups", "help": "Accept FFDHE groups.", "label": "Enable", "name": "enable"}, {"description": "Do not accept FFDHE groups", "help": "Do not accept FFDHE groups.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_send_empty_frags: Literal[{"description": "Send empty fragments", "help": "Send empty fragments.", "label": "Enable", "name": "enable"}, {"description": "Do not send empty fragments", "help": "Do not send empty fragments.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_client_fallback: Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Enable", "help": "Enable.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_client_renegotiation: Literal[{"description": "Allow a SSL client to renegotiate", "help": "Allow a SSL client to renegotiate.", "label": "Allow", "name": "allow"}, {"description": "Abort any SSL connection that attempts to renegotiate", "help": "Abort any SSL connection that attempts to renegotiate.", "label": "Deny", "name": "deny"}, {"description": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication", "help": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication.", "label": "Secure", "name": "secure"}] | None = ...,
        ssl_client_session_state_type: Literal[{"description": "Do not keep session states", "help": "Do not keep session states.", "label": "Disable", "name": "disable"}, {"description": "Expire session states after this many minutes", "help": "Expire session states after this many minutes.", "label": "Time", "name": "time"}, {"description": "Expire session states when this maximum is reached", "help": "Expire session states when this maximum is reached.", "label": "Count", "name": "count"}, {"description": "Expire session states based on time or count, whichever occurs first", "help": "Expire session states based on time or count, whichever occurs first.", "label": "Both", "name": "both"}] | None = ...,
        ssl_client_session_state_timeout: int | None = ...,
        ssl_client_session_state_max: int | None = ...,
        ssl_client_rekey_count: int | None = ...,
        ssl_server_session_state_type: Literal[{"description": "Do not keep session states", "help": "Do not keep session states.", "label": "Disable", "name": "disable"}, {"description": "Expire session states after this many minutes", "help": "Expire session states after this many minutes.", "label": "Time", "name": "time"}, {"description": "Expire session states when this maximum is reached", "help": "Expire session states when this maximum is reached.", "label": "Count", "name": "count"}, {"description": "Expire session states based on time or count, whichever occurs first", "help": "Expire session states based on time or count, whichever occurs first.", "label": "Both", "name": "both"}] | None = ...,
        ssl_server_session_state_timeout: int | None = ...,
        ssl_server_session_state_max: int | None = ...,
        ssl_http_location_conversion: Literal[{"description": "Enable HTTP location conversion", "help": "Enable HTTP location conversion.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP location conversion", "help": "Disable HTTP location conversion.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_http_match_host: Literal[{"description": "Match HTTP host in response header", "help": "Match HTTP host in response header.", "label": "Enable", "name": "enable"}, {"description": "Do not match HTTP host", "help": "Do not match HTTP host.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_hpkp: Literal[{"description": "Do not add a HPKP header to each HTTP response", "help": "Do not add a HPKP header to each HTTP response.", "label": "Disable", "name": "disable"}, {"description": "Add a HPKP header to each a HTTP response", "help": "Add a HPKP header to each a HTTP response.", "label": "Enable", "name": "enable"}, {"description": "Add a HPKP Report-Only header to each HTTP response", "help": "Add a HPKP Report-Only header to each HTTP response.", "label": "Report Only", "name": "report-only"}] | None = ...,
        ssl_hpkp_primary: str | None = ...,
        ssl_hpkp_backup: str | None = ...,
        ssl_hpkp_age: int | None = ...,
        ssl_hpkp_report_uri: str | None = ...,
        ssl_hpkp_include_subdomains: Literal[{"description": "HPKP header does not apply to subdomains", "help": "HPKP header does not apply to subdomains.", "label": "Disable", "name": "disable"}, {"description": "HPKP header applies to subdomains", "help": "HPKP header applies to subdomains.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_hsts: Literal[{"description": "Do not add a HSTS header to each a HTTP response", "help": "Do not add a HSTS header to each a HTTP response.", "label": "Disable", "name": "disable"}, {"description": "Add a HSTS header to each HTTP response", "help": "Add a HSTS header to each HTTP response.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_hsts_age: int | None = ...,
        ssl_hsts_include_subdomains: Literal[{"description": "HSTS header does not apply to subdomains", "help": "HSTS header does not apply to subdomains.", "label": "Disable", "name": "disable"}, {"description": "HSTS header applies to subdomains", "help": "HSTS header applies to subdomains.", "label": "Enable", "name": "enable"}] | None = ...,
        monitor: list[dict[str, Any]] | None = ...,
        max_embryonic_connections: int | None = ...,
        embedded_ipv4_address: Literal[{"description": "Disable use of the lower 32 bits of the external IPv6 address as mapped IPv4 address", "help": "Disable use of the lower 32 bits of the external IPv6 address as mapped IPv4 address.", "label": "Disable", "name": "disable"}, {"description": "Enable use of the lower 32 bits of the external IPv6 address as mapped IPv4 address", "help": "Enable use of the lower 32 bits of the external IPv6 address as mapped IPv4 address.", "label": "Enable", "name": "enable"}] | None = ...,
        ipv4_mappedip: str | None = ...,
        ipv4_mappedport: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: Vip6Payload | None = ...,
        name: str | None = ...,
        id: int | None = ...,
        uuid: str | None = ...,
        comment: str | None = ...,
        type: Literal[{"description": "Static NAT", "help": "Static NAT.", "label": "Static Nat", "name": "static-nat"}, {"description": "Server load balance", "help": "Server load balance.", "label": "Server Load Balance", "name": "server-load-balance"}, {"description": "Access proxy", "help": "Access proxy.", "label": "Access Proxy", "name": "access-proxy"}] | None = ...,
        src_filter: list[dict[str, Any]] | None = ...,
        src_vip_filter: Literal[{"description": "Match any destination for the reverse SNAT rule", "help": "Match any destination for the reverse SNAT rule.", "label": "Disable", "name": "disable"}, {"description": "Match only destinations in \u0027src-filter\u0027 for the reverse SNAT rule", "help": "Match only destinations in \u0027src-filter\u0027 for the reverse SNAT rule.", "label": "Enable", "name": "enable"}] | None = ...,
        extip: str | None = ...,
        mappedip: str | None = ...,
        nat_source_vip: Literal[{"description": "Disable nat-source-vip", "help": "Disable nat-source-vip.", "label": "Disable", "name": "disable"}, {"description": "Perform SNAT on traffic from mappedip to the extip for all egress interfaces", "help": "Perform SNAT on traffic from mappedip to the extip for all egress interfaces.", "label": "Enable", "name": "enable"}] | None = ...,
        ndp_reply: Literal[{"description": "Disable this FortiGate unit\u0027s ability to respond to NDP requests for this virtual IP address", "help": "Disable this FortiGate unit\u0027s ability to respond to NDP requests for this virtual IP address.", "label": "Disable", "name": "disable"}, {"description": "Enable this FortiGate unit\u0027s ability to respond to NDP requests for this virtual IP address", "help": "Enable this FortiGate unit\u0027s ability to respond to NDP requests for this virtual IP address.", "label": "Enable", "name": "enable"}] | None = ...,
        portforward: Literal[{"description": "Disable port forward", "help": "Disable port forward.", "label": "Disable", "name": "disable"}, {"description": "Enable/disable port forwarding", "help": "Enable/disable port forwarding.", "label": "Enable", "name": "enable"}] | None = ...,
        protocol: Literal[{"description": "TCP", "help": "TCP.", "label": "Tcp", "name": "tcp"}, {"description": "UDP", "help": "UDP.", "label": "Udp", "name": "udp"}, {"description": "SCTP", "help": "SCTP.", "label": "Sctp", "name": "sctp"}] | None = ...,
        extport: str | None = ...,
        mappedport: str | None = ...,
        color: int | None = ...,
        ldb_method: Literal[{"description": "Distribute sessions based on source IP", "help": "Distribute sessions based on source IP.", "label": "Static", "name": "static"}, {"description": "Distribute sessions based round robin order", "help": "Distribute sessions based round robin order.", "label": "Round Robin", "name": "round-robin"}, {"description": "Distribute sessions based on weight", "help": "Distribute sessions based on weight.", "label": "Weighted", "name": "weighted"}, {"description": "Sends new sessions to the server with the lowest session count", "help": "Sends new sessions to the server with the lowest session count.", "label": "Least Session", "name": "least-session"}, {"description": "Distribute new sessions to the server with lowest Round-Trip-Time", "help": "Distribute new sessions to the server with lowest Round-Trip-Time.", "label": "Least Rtt", "name": "least-rtt"}, {"description": "Distribute sessions to the first server that is alive", "help": "Distribute sessions to the first server that is alive.", "label": "First Alive", "name": "first-alive"}, {"description": "Distribute sessions to servers based on host field in HTTP header", "help": "Distribute sessions to servers based on host field in HTTP header.", "label": "Http Host", "name": "http-host"}] | None = ...,
        server_type: Literal[{"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"help": "SSL.", "label": "Ssl", "name": "ssl"}, {"description": "TCP", "help": "TCP.", "label": "Tcp", "name": "tcp"}, {"description": "UDP", "help": "UDP.", "label": "Udp", "name": "udp"}, {"description": "IP", "help": "IP.", "label": "Ip", "name": "ip"}] | None = ...,
        http_redirect: Literal[{"description": "Enable redirection of HTTP to HTTPS", "help": "Enable redirection of HTTP to HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable redirection of HTTP to HTTPS", "help": "Disable redirection of HTTP to HTTPS.", "label": "Disable", "name": "disable"}] | None = ...,
        persistence: Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "HTTP cookie", "help": "HTTP cookie.", "label": "Http Cookie", "name": "http-cookie"}, {"description": "SSL session ID", "help": "SSL session ID.", "label": "Ssl Session Id", "name": "ssl-session-id"}] | None = ...,
        h2_support: Literal[{"description": "Enable HTTP2 support", "help": "Enable HTTP2 support.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP2 support", "help": "Disable HTTP2 support.", "label": "Disable", "name": "disable"}] | None = ...,
        h3_support: Literal[{"description": "Enable HTTP3/QUIC support", "help": "Enable HTTP3/QUIC support.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP3/QUIC support", "help": "Disable HTTP3/QUIC support.", "label": "Disable", "name": "disable"}] | None = ...,
        quic: str | None = ...,
        nat66: Literal[{"description": "Disable DNAT66", "help": "Disable DNAT66.", "label": "Disable", "name": "disable"}, {"description": "Enable DNAT66", "help": "Enable DNAT66.", "label": "Enable", "name": "enable"}] | None = ...,
        nat64: Literal[{"description": "Disable DNAT64", "help": "Disable DNAT64.", "label": "Disable", "name": "disable"}, {"description": "Enable DNAT64", "help": "Enable DNAT64.", "label": "Enable", "name": "enable"}] | None = ...,
        add_nat64_route: Literal[{"description": "Disable adding NAT64 route", "help": "Disable adding NAT64 route.", "label": "Disable", "name": "disable"}, {"description": "Enable adding NAT64 route", "help": "Enable adding NAT64 route.", "label": "Enable", "name": "enable"}] | None = ...,
        empty_cert_action: Literal[{"description": "Accept the SSL handshake if the client certificate is empty", "help": "Accept the SSL handshake if the client certificate is empty.", "label": "Accept", "name": "accept"}, {"description": "Block the SSL handshake if the client certificate is empty", "help": "Block the SSL handshake if the client certificate is empty.", "label": "Block", "name": "block"}, {"description": "Accept the SSL handshake only if the end-point is unmanageable", "help": "Accept the SSL handshake only if the end-point is unmanageable.", "label": "Accept Unmanageable", "name": "accept-unmanageable"}] | None = ...,
        user_agent_detect: Literal[{"description": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Disable", "name": "disable"}, {"description": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Enable", "name": "enable"}] | None = ...,
        client_cert: Literal[{"description": "Disable client certificate request", "help": "Disable client certificate request.", "label": "Disable", "name": "disable"}, {"description": "Enable client certificate request", "help": "Enable client certificate request.", "label": "Enable", "name": "enable"}] | None = ...,
        realservers: list[dict[str, Any]] | None = ...,
        http_cookie_domain_from_host: Literal[{"description": "Disable use of HTTP cookie domain from host field in HTTP (use http-cooke-domain setting)", "help": "Disable use of HTTP cookie domain from host field in HTTP (use http-cooke-domain setting).", "label": "Disable", "name": "disable"}, {"description": "Enable use of HTTP cookie domain from host field in HTTP", "help": "Enable use of HTTP cookie domain from host field in HTTP.", "label": "Enable", "name": "enable"}] | None = ...,
        http_cookie_domain: str | None = ...,
        http_cookie_path: str | None = ...,
        http_cookie_generation: int | None = ...,
        http_cookie_age: int | None = ...,
        http_cookie_share: Literal[{"description": "Only allow HTTP cookie to match this virtual server", "help": "Only allow HTTP cookie to match this virtual server.", "label": "Disable", "name": "disable"}, {"description": "Allow HTTP cookie to match any virtual server with same IP", "help": "Allow HTTP cookie to match any virtual server with same IP.", "label": "Same Ip", "name": "same-ip"}] | None = ...,
        https_cookie_secure: Literal[{"description": "Do not mark cookie as secure, allow sharing between an HTTP and HTTPS connection", "help": "Do not mark cookie as secure, allow sharing between an HTTP and HTTPS connection.", "label": "Disable", "name": "disable"}, {"description": "Mark inserted cookie as secure, cookie can only be used for HTTPS a connection", "help": "Mark inserted cookie as secure, cookie can only be used for HTTPS a connection.", "label": "Enable", "name": "enable"}] | None = ...,
        http_multiplex: Literal[{"description": "Enable HTTP session multiplexing", "help": "Enable HTTP session multiplexing.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP session multiplexing", "help": "Disable HTTP session multiplexing.", "label": "Disable", "name": "disable"}] | None = ...,
        http_ip_header: Literal[{"description": "Enable adding HTTP header", "help": "Enable adding HTTP header.", "label": "Enable", "name": "enable"}, {"description": "Disable adding HTTP header", "help": "Disable adding HTTP header.", "label": "Disable", "name": "disable"}] | None = ...,
        http_ip_header_name: str | None = ...,
        outlook_web_access: Literal[{"description": "Disable Outlook Web Access support", "help": "Disable Outlook Web Access support.", "label": "Disable", "name": "disable"}, {"description": "Enable Outlook Web Access support", "help": "Enable Outlook Web Access support.", "label": "Enable", "name": "enable"}] | None = ...,
        weblogic_server: Literal[{"description": "Do not add HTTP header indicating SSL offload for WebLogic server", "help": "Do not add HTTP header indicating SSL offload for WebLogic server.", "label": "Disable", "name": "disable"}, {"description": "Add HTTP header indicating SSL offload for WebLogic server", "help": "Add HTTP header indicating SSL offload for WebLogic server.", "label": "Enable", "name": "enable"}] | None = ...,
        websphere_server: Literal[{"description": "Do not add HTTP header indicating SSL offload for WebSphere server", "help": "Do not add HTTP header indicating SSL offload for WebSphere server.", "label": "Disable", "name": "disable"}, {"description": "Add HTTP header indicating SSL offload for WebSphere server", "help": "Add HTTP header indicating SSL offload for WebSphere server.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_mode: Literal[{"description": "Client to FortiGate SSL", "help": "Client to FortiGate SSL.", "label": "Half", "name": "half"}, {"description": "Client to FortiGate and FortiGate to Server SSL", "help": "Client to FortiGate and FortiGate to Server SSL.", "label": "Full", "name": "full"}] | None = ...,
        ssl_certificate: list[dict[str, Any]] | None = ...,
        ssl_dh_bits: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}, {"description": "3072-bit Diffie-Hellman prime", "help": "3072-bit Diffie-Hellman prime.", "label": "3072", "name": "3072"}, {"description": "4096-bit Diffie-Hellman prime", "help": "4096-bit Diffie-Hellman prime.", "label": "4096", "name": "4096"}] | None = ...,
        ssl_algorithm: Literal[{"description": "Use AES", "help": "Use AES.", "label": "High", "name": "high"}, {"description": "Use AES, 3DES, or RC4", "help": "Use AES, 3DES, or RC4.", "label": "Medium", "name": "medium"}, {"description": "Use AES, 3DES, RC4, or DES", "help": "Use AES, 3DES, RC4, or DES.", "label": "Low", "name": "low"}, {"description": "Use config ssl-cipher-suites to select the cipher suites that are allowed", "help": "Use config ssl-cipher-suites to select the cipher suites that are allowed.", "label": "Custom", "name": "custom"}] | None = ...,
        ssl_cipher_suites: list[dict[str, Any]] | None = ...,
        ssl_server_renegotiation: Literal[{"description": "Enable secure renegotiation", "help": "Enable secure renegotiation.", "label": "Enable", "name": "enable"}, {"description": "Disable secure renegotiation", "help": "Disable secure renegotiation.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_server_algorithm: Literal[{"description": "Use AES", "help": "Use AES.", "label": "High", "name": "high"}, {"description": "Use AES, 3DES, or RC4", "help": "Use AES, 3DES, or RC4.", "label": "Medium", "name": "medium"}, {"description": "Use AES, 3DES, RC4, or DES", "help": "Use AES, 3DES, RC4, or DES.", "label": "Low", "name": "low"}, {"description": "Use config ssl-server-cipher-suites to select the cipher suites that are allowed", "help": "Use config ssl-server-cipher-suites to select the cipher suites that are allowed.", "label": "Custom", "name": "custom"}, {"description": "Use the same encryption algorithms for client and server sessions", "help": "Use the same encryption algorithms for client and server sessions.", "label": "Client", "name": "client"}] | None = ...,
        ssl_server_cipher_suites: list[dict[str, Any]] | None = ...,
        ssl_pfs: Literal[{"description": "Allow only Diffie-Hellman cipher-suites, so PFS is applied", "help": "Allow only Diffie-Hellman cipher-suites, so PFS is applied.", "label": "Require", "name": "require"}, {"description": "Allow only non-Diffie-Hellman cipher-suites, so PFS is not applied", "help": "Allow only non-Diffie-Hellman cipher-suites, so PFS is not applied.", "label": "Deny", "name": "deny"}, {"description": "Allow use of any cipher suite so PFS may or may not be used depending on the cipher suite selected", "help": "Allow use of any cipher suite so PFS may or may not be used depending on the cipher suite selected.", "label": "Allow", "name": "allow"}] | None = ...,
        ssl_min_version: Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}] | None = ...,
        ssl_max_version: Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}] | None = ...,
        ssl_server_min_version: Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}, {"description": "Use same value as client configuration", "help": "Use same value as client configuration.", "label": "Client", "name": "client"}] | None = ...,
        ssl_server_max_version: Literal[{"help": "SSL 3.0.", "label": "Ssl 3.0", "name": "ssl-3.0"}, {"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}, {"description": "Use same value as client configuration", "help": "Use same value as client configuration.", "label": "Client", "name": "client"}] | None = ...,
        ssl_accept_ffdhe_groups: Literal[{"description": "Accept FFDHE groups", "help": "Accept FFDHE groups.", "label": "Enable", "name": "enable"}, {"description": "Do not accept FFDHE groups", "help": "Do not accept FFDHE groups.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_send_empty_frags: Literal[{"description": "Send empty fragments", "help": "Send empty fragments.", "label": "Enable", "name": "enable"}, {"description": "Do not send empty fragments", "help": "Do not send empty fragments.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_client_fallback: Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Enable", "help": "Enable.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_client_renegotiation: Literal[{"description": "Allow a SSL client to renegotiate", "help": "Allow a SSL client to renegotiate.", "label": "Allow", "name": "allow"}, {"description": "Abort any SSL connection that attempts to renegotiate", "help": "Abort any SSL connection that attempts to renegotiate.", "label": "Deny", "name": "deny"}, {"description": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication", "help": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication.", "label": "Secure", "name": "secure"}] | None = ...,
        ssl_client_session_state_type: Literal[{"description": "Do not keep session states", "help": "Do not keep session states.", "label": "Disable", "name": "disable"}, {"description": "Expire session states after this many minutes", "help": "Expire session states after this many minutes.", "label": "Time", "name": "time"}, {"description": "Expire session states when this maximum is reached", "help": "Expire session states when this maximum is reached.", "label": "Count", "name": "count"}, {"description": "Expire session states based on time or count, whichever occurs first", "help": "Expire session states based on time or count, whichever occurs first.", "label": "Both", "name": "both"}] | None = ...,
        ssl_client_session_state_timeout: int | None = ...,
        ssl_client_session_state_max: int | None = ...,
        ssl_client_rekey_count: int | None = ...,
        ssl_server_session_state_type: Literal[{"description": "Do not keep session states", "help": "Do not keep session states.", "label": "Disable", "name": "disable"}, {"description": "Expire session states after this many minutes", "help": "Expire session states after this many minutes.", "label": "Time", "name": "time"}, {"description": "Expire session states when this maximum is reached", "help": "Expire session states when this maximum is reached.", "label": "Count", "name": "count"}, {"description": "Expire session states based on time or count, whichever occurs first", "help": "Expire session states based on time or count, whichever occurs first.", "label": "Both", "name": "both"}] | None = ...,
        ssl_server_session_state_timeout: int | None = ...,
        ssl_server_session_state_max: int | None = ...,
        ssl_http_location_conversion: Literal[{"description": "Enable HTTP location conversion", "help": "Enable HTTP location conversion.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP location conversion", "help": "Disable HTTP location conversion.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_http_match_host: Literal[{"description": "Match HTTP host in response header", "help": "Match HTTP host in response header.", "label": "Enable", "name": "enable"}, {"description": "Do not match HTTP host", "help": "Do not match HTTP host.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_hpkp: Literal[{"description": "Do not add a HPKP header to each HTTP response", "help": "Do not add a HPKP header to each HTTP response.", "label": "Disable", "name": "disable"}, {"description": "Add a HPKP header to each a HTTP response", "help": "Add a HPKP header to each a HTTP response.", "label": "Enable", "name": "enable"}, {"description": "Add a HPKP Report-Only header to each HTTP response", "help": "Add a HPKP Report-Only header to each HTTP response.", "label": "Report Only", "name": "report-only"}] | None = ...,
        ssl_hpkp_primary: str | None = ...,
        ssl_hpkp_backup: str | None = ...,
        ssl_hpkp_age: int | None = ...,
        ssl_hpkp_report_uri: str | None = ...,
        ssl_hpkp_include_subdomains: Literal[{"description": "HPKP header does not apply to subdomains", "help": "HPKP header does not apply to subdomains.", "label": "Disable", "name": "disable"}, {"description": "HPKP header applies to subdomains", "help": "HPKP header applies to subdomains.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_hsts: Literal[{"description": "Do not add a HSTS header to each a HTTP response", "help": "Do not add a HSTS header to each a HTTP response.", "label": "Disable", "name": "disable"}, {"description": "Add a HSTS header to each HTTP response", "help": "Add a HSTS header to each HTTP response.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_hsts_age: int | None = ...,
        ssl_hsts_include_subdomains: Literal[{"description": "HSTS header does not apply to subdomains", "help": "HSTS header does not apply to subdomains.", "label": "Disable", "name": "disable"}, {"description": "HSTS header applies to subdomains", "help": "HSTS header applies to subdomains.", "label": "Enable", "name": "enable"}] | None = ...,
        monitor: list[dict[str, Any]] | None = ...,
        max_embryonic_connections: int | None = ...,
        embedded_ipv4_address: Literal[{"description": "Disable use of the lower 32 bits of the external IPv6 address as mapped IPv4 address", "help": "Disable use of the lower 32 bits of the external IPv6 address as mapped IPv4 address.", "label": "Disable", "name": "disable"}, {"description": "Enable use of the lower 32 bits of the external IPv6 address as mapped IPv4 address", "help": "Enable use of the lower 32 bits of the external IPv6 address as mapped IPv4 address.", "label": "Enable", "name": "enable"}] | None = ...,
        ipv4_mappedip: str | None = ...,
        ipv4_mappedport: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        name: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        name: str,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: Vip6Payload | None = ...,
        vdom: str | bool | None = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    # Helper methods
    @staticmethod
    def help(field_name: str | None = ...) -> str: ...
    
    @staticmethod
    def fields(detailed: bool = ...) -> Union[list[str], list[dict[str, Any]]]: ...
    
    @staticmethod
    def field_info(field_name: str) -> dict[str, Any]: ...
    
    @staticmethod
    def validate_field(name: str, value: Any) -> bool: ...
    
    @staticmethod
    def required_fields() -> list[str]: ...
    
    @staticmethod
    def defaults() -> dict[str, Any]: ...
    
    @staticmethod
    def schema() -> dict[str, Any]: ...


__all__ = [
    "Vip6",
    "Vip6Payload",
]