from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ExplicitPayload(TypedDict, total=False):
    """
    Type hints for web_proxy/explicit payload fields.
    
    Configure explicit Web proxy settings.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: ExplicitPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: NotRequired[Literal[{"description": "Enable the explicit web proxy", "help": "Enable the explicit web proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the explicit web proxy", "help": "Disable the explicit web proxy.", "label": "Disable", "name": "disable"}]]  # Enable/disable the explicit Web proxy for HTTP and HTTPS ses
    secure_web_proxy: NotRequired[Literal[{"description": "Disable secure webproxy", "help": "Disable secure webproxy.", "label": "Disable", "name": "disable"}, {"description": "Enable secure webproxy access", "help": "Enable secure webproxy access.", "label": "Enable", "name": "enable"}, {"description": "Require secure webproxy access", "help": "Require secure webproxy access.", "label": "Secure", "name": "secure"}]]  # Enable/disable/require the secure web proxy for HTTP and HTT
    ftp_over_http: NotRequired[Literal[{"description": "Enable FTP-over-HTTP sessions", "help": "Enable FTP-over-HTTP sessions.", "label": "Enable", "name": "enable"}, {"description": "Disable FTP-over-HTTP sessions", "help": "Disable FTP-over-HTTP sessions.", "label": "Disable", "name": "disable"}]]  # Enable to proxy FTP-over-HTTP sessions sent from a web brows
    socks: NotRequired[Literal[{"description": "Enable the SOCKS proxy", "help": "Enable the SOCKS proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the SOCKS proxy", "help": "Disable the SOCKS proxy.", "label": "Disable", "name": "disable"}]]  # Enable/disable the SOCKS proxy.
    http_incoming_port: NotRequired[str]  # Accept incoming HTTP requests on one or more ports (0 - 6553
    http_connection_mode: NotRequired[Literal[{"description": "Only one server connection exists during the proxy session", "help": "Only one server connection exists during the proxy session.", "label": "Static", "name": "static"}, {"description": "Established connections are held until the proxy session ends", "help": "Established connections are held until the proxy session ends.", "label": "Multiplex", "name": "multiplex"}, {"description": "Established connections are shared with other proxy sessions", "help": "Established connections are shared with other proxy sessions.", "label": "Serverpool", "name": "serverpool"}]]  # HTTP connection mode (default = static).
    https_incoming_port: NotRequired[str]  # Accept incoming HTTPS requests on one or more ports (0 - 655
    secure_web_proxy_cert: NotRequired[list[dict[str, Any]]]  # Name of certificates for secure web proxy.
    client_cert: NotRequired[Literal[{"description": "Disable client certificate request", "help": "Disable client certificate request.", "label": "Disable", "name": "disable"}, {"description": "Enable client certificate request", "help": "Enable client certificate request.", "label": "Enable", "name": "enable"}]]  # Enable/disable to request client certificate.
    user_agent_detect: NotRequired[Literal[{"description": "Disable to detect unknown device by HTTP user-agent if no client certificate provided", "help": "Disable to detect unknown device by HTTP user-agent if no client certificate provided.", "label": "Disable", "name": "disable"}, {"description": "Enable to detect unknown device by HTTP user-agent if no client certificate provided", "help": "Enable to detect unknown device by HTTP user-agent if no client certificate provided.", "label": "Enable", "name": "enable"}]]  # Enable/disable to detect device type by HTTP user-agent if n
    empty_cert_action: NotRequired[Literal[{"description": "Accept the SSL handshake if the client certificate is empty", "help": "Accept the SSL handshake if the client certificate is empty.", "label": "Accept", "name": "accept"}, {"description": "Block the SSL handshake if the client certificate is empty", "help": "Block the SSL handshake if the client certificate is empty.", "label": "Block", "name": "block"}, {"description": "Accept the SSL handshake only if the end-point is unmanageable", "help": "Accept the SSL handshake only if the end-point is unmanageable.", "label": "Accept Unmanageable", "name": "accept-unmanageable"}]]  # Action of an empty client certificate.
    ssl_dh_bits: NotRequired[Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}]]  # Bit-size of Diffie-Hellman (DH) prime used in DHE-RSA negoti
    ftp_incoming_port: NotRequired[str]  # Accept incoming FTP-over-HTTP requests on one or more ports 
    socks_incoming_port: NotRequired[str]  # Accept incoming SOCKS proxy requests on one or more ports (0
    incoming_ip: NotRequired[str]  # Restrict the explicit HTTP proxy to only accept sessions fro
    outgoing_ip: NotRequired[list[dict[str, Any]]]  # Outgoing HTTP requests will have this IP address as their so
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.
    ipv6_status: NotRequired[Literal[{"description": "Enable allowing an IPv6 web proxy destination", "help": "Enable allowing an IPv6 web proxy destination.", "label": "Enable", "name": "enable"}, {"description": "Disable allowing an IPv6 web proxy destination", "help": "Disable allowing an IPv6 web proxy destination.", "label": "Disable", "name": "disable"}]]  # Enable/disable allowing an IPv6 web proxy destination in pol
    incoming_ip6: NotRequired[str]  # Restrict the explicit web proxy to only accept sessions from
    outgoing_ip6: NotRequired[list[dict[str, Any]]]  # Outgoing HTTP requests will leave this IPv6. Multiple interf
    strict_guest: NotRequired[Literal[{"description": "Enable strict guest user checking", "help": "Enable strict guest user checking.", "label": "Enable", "name": "enable"}, {"description": "Disable strict guest user checking", "help": "Disable strict guest user checking.", "label": "Disable", "name": "disable"}]]  # Enable/disable strict guest user checking by the explicit we
    pref_dns_result: NotRequired[Literal[{"description": "Send the IPv4 request first and then the IPv6 request", "help": "Send the IPv4 request first and then the IPv6 request. Use the DNS response that returns to the FortiGate first.", "label": "Ipv4", "name": "ipv4"}, {"description": "Send the IPv6 request first and then the IPv4 request", "help": "Send the IPv6 request first and then the IPv4 request. Use the DNS response that returns to the FortiGate first.", "label": "Ipv6", "name": "ipv6"}, {"description": "Use the IPv4 DNS response", "help": "Use the IPv4 DNS response. If the IPv6 DNS response arrives first, wait 50ms for the IPv4 response and then use the IPv4 response, otherwise the IPv6.", "label": "Ipv4 Strict", "name": "ipv4-strict"}, {"description": "Use the IPv6 DNS response", "help": "Use the IPv6 DNS response. If the IPv4 DNS response arrives first, wait 50ms for the IPv6 response and then use the IPv6 response, otherwise the IPv4.", "label": "Ipv6 Strict", "name": "ipv6-strict"}]]  # Prefer resolving addresses using the configured IPv4 or IPv6
    unknown_http_version: NotRequired[Literal[{"description": "Reject or tear down HTTP sessions that do not use HTTP 0", "help": "Reject or tear down HTTP sessions that do not use HTTP 0.9, 1.0, or 1.1.", "label": "Reject", "name": "reject"}, {"description": "Assume all HTTP sessions comply with HTTP 0", "help": "Assume all HTTP sessions comply with HTTP 0.9, 1.0, or 1.1. If a session uses a different HTTP version, it may not parse correctly and the connection may be lost.", "label": "Best Effort", "name": "best-effort"}]]  # How to handle HTTP sessions that do not comply with HTTP 0.9
    realm: str  # Authentication realm used to identify the explicit web proxy
    sec_default_action: NotRequired[Literal[{"description": "Accept requests", "help": "Accept requests. All explicit web proxy traffic is accepted whether there is an explicit web proxy policy or not.", "label": "Accept", "name": "accept"}, {"description": "Deny requests unless there is a matching explicit web proxy policy", "help": "Deny requests unless there is a matching explicit web proxy policy.", "label": "Deny", "name": "deny"}]]  # Accept or deny explicit web proxy sessions when no web proxy
    https_replacement_message: NotRequired[Literal[{"description": "Display a replacement message for HTTPS requests", "help": "Display a replacement message for HTTPS requests.", "label": "Enable", "name": "enable"}, {"description": "Do not display a replacement message for HTTPS requests", "help": "Do not display a replacement message for HTTPS requests.", "label": "Disable", "name": "disable"}]]  # Enable/disable sending the client a replacement message for 
    message_upon_server_error: NotRequired[Literal[{"description": "Display a replacement message when a server error is detected", "help": "Display a replacement message when a server error is detected.", "label": "Enable", "name": "enable"}, {"description": "Do not display a replacement message when a server error is detected", "help": "Do not display a replacement message when a server error is detected.", "label": "Disable", "name": "disable"}]]  # Enable/disable displaying a replacement message when a serve
    pac_file_server_status: NotRequired[Literal[{"description": "Enable Proxy Auto-Configuration (PAC)", "help": "Enable Proxy Auto-Configuration (PAC).", "label": "Enable", "name": "enable"}, {"description": "Disable Proxy Auto-Configuration (PAC)", "help": "Disable Proxy Auto-Configuration (PAC).", "label": "Disable", "name": "disable"}]]  # Enable/disable Proxy Auto-Configuration (PAC) for users of t
    pac_file_url: NotRequired[str]  # PAC file access URL.
    pac_file_server_port: NotRequired[str]  # Port number that PAC traffic from client web browsers uses t
    pac_file_through_https: NotRequired[Literal[{"description": "Enable to get Proxy Auto-Configuration (PAC) through HTTPS", "help": "Enable to get Proxy Auto-Configuration (PAC) through HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable to get Proxy Auto-Configuration (PAC) through HTTPS", "help": "Disable to get Proxy Auto-Configuration (PAC) through HTTPS.", "label": "Disable", "name": "disable"}]]  # Enable/disable to get Proxy Auto-Configuration (PAC) through
    pac_file_name: str  # Pac file name.
    pac_file_data: NotRequired[str]  # PAC file contents enclosed in quotes (maximum of 256K bytes)
    pac_policy: NotRequired[list[dict[str, Any]]]  # PAC policies.
    ssl_algorithm: NotRequired[Literal[{"description": "High encrption", "help": "High encrption. Allow only AES and ChaCha.", "label": "High", "name": "high"}, {"description": "Medium encryption", "help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}]]  # Relative strength of encryption algorithms accepted in HTTPS
    trace_auth_no_rsp: NotRequired[Literal[{"description": "Enable logging timed-out authentication requests", "help": "Enable logging timed-out authentication requests.", "label": "Enable", "name": "enable"}, {"description": "Disable logging timed-out authentication requests", "help": "Disable logging timed-out authentication requests.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging timed-out authentication requests.


class Explicit:
    """
    Configure explicit Web proxy settings.
    
    Path: web_proxy/explicit
    Category: cmdb
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
        payload_dict: ExplicitPayload | None = ...,
        status: Literal[{"description": "Enable the explicit web proxy", "help": "Enable the explicit web proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the explicit web proxy", "help": "Disable the explicit web proxy.", "label": "Disable", "name": "disable"}] | None = ...,
        secure_web_proxy: Literal[{"description": "Disable secure webproxy", "help": "Disable secure webproxy.", "label": "Disable", "name": "disable"}, {"description": "Enable secure webproxy access", "help": "Enable secure webproxy access.", "label": "Enable", "name": "enable"}, {"description": "Require secure webproxy access", "help": "Require secure webproxy access.", "label": "Secure", "name": "secure"}] | None = ...,
        ftp_over_http: Literal[{"description": "Enable FTP-over-HTTP sessions", "help": "Enable FTP-over-HTTP sessions.", "label": "Enable", "name": "enable"}, {"description": "Disable FTP-over-HTTP sessions", "help": "Disable FTP-over-HTTP sessions.", "label": "Disable", "name": "disable"}] | None = ...,
        socks: Literal[{"description": "Enable the SOCKS proxy", "help": "Enable the SOCKS proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the SOCKS proxy", "help": "Disable the SOCKS proxy.", "label": "Disable", "name": "disable"}] | None = ...,
        http_incoming_port: str | None = ...,
        http_connection_mode: Literal[{"description": "Only one server connection exists during the proxy session", "help": "Only one server connection exists during the proxy session.", "label": "Static", "name": "static"}, {"description": "Established connections are held until the proxy session ends", "help": "Established connections are held until the proxy session ends.", "label": "Multiplex", "name": "multiplex"}, {"description": "Established connections are shared with other proxy sessions", "help": "Established connections are shared with other proxy sessions.", "label": "Serverpool", "name": "serverpool"}] | None = ...,
        https_incoming_port: str | None = ...,
        secure_web_proxy_cert: list[dict[str, Any]] | None = ...,
        client_cert: Literal[{"description": "Disable client certificate request", "help": "Disable client certificate request.", "label": "Disable", "name": "disable"}, {"description": "Enable client certificate request", "help": "Enable client certificate request.", "label": "Enable", "name": "enable"}] | None = ...,
        user_agent_detect: Literal[{"description": "Disable to detect unknown device by HTTP user-agent if no client certificate provided", "help": "Disable to detect unknown device by HTTP user-agent if no client certificate provided.", "label": "Disable", "name": "disable"}, {"description": "Enable to detect unknown device by HTTP user-agent if no client certificate provided", "help": "Enable to detect unknown device by HTTP user-agent if no client certificate provided.", "label": "Enable", "name": "enable"}] | None = ...,
        empty_cert_action: Literal[{"description": "Accept the SSL handshake if the client certificate is empty", "help": "Accept the SSL handshake if the client certificate is empty.", "label": "Accept", "name": "accept"}, {"description": "Block the SSL handshake if the client certificate is empty", "help": "Block the SSL handshake if the client certificate is empty.", "label": "Block", "name": "block"}, {"description": "Accept the SSL handshake only if the end-point is unmanageable", "help": "Accept the SSL handshake only if the end-point is unmanageable.", "label": "Accept Unmanageable", "name": "accept-unmanageable"}] | None = ...,
        ssl_dh_bits: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}] | None = ...,
        ftp_incoming_port: str | None = ...,
        socks_incoming_port: str | None = ...,
        incoming_ip: str | None = ...,
        outgoing_ip: list[dict[str, Any]] | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        ipv6_status: Literal[{"description": "Enable allowing an IPv6 web proxy destination", "help": "Enable allowing an IPv6 web proxy destination.", "label": "Enable", "name": "enable"}, {"description": "Disable allowing an IPv6 web proxy destination", "help": "Disable allowing an IPv6 web proxy destination.", "label": "Disable", "name": "disable"}] | None = ...,
        incoming_ip6: str | None = ...,
        outgoing_ip6: list[dict[str, Any]] | None = ...,
        strict_guest: Literal[{"description": "Enable strict guest user checking", "help": "Enable strict guest user checking.", "label": "Enable", "name": "enable"}, {"description": "Disable strict guest user checking", "help": "Disable strict guest user checking.", "label": "Disable", "name": "disable"}] | None = ...,
        pref_dns_result: Literal[{"description": "Send the IPv4 request first and then the IPv6 request", "help": "Send the IPv4 request first and then the IPv6 request. Use the DNS response that returns to the FortiGate first.", "label": "Ipv4", "name": "ipv4"}, {"description": "Send the IPv6 request first and then the IPv4 request", "help": "Send the IPv6 request first and then the IPv4 request. Use the DNS response that returns to the FortiGate first.", "label": "Ipv6", "name": "ipv6"}, {"description": "Use the IPv4 DNS response", "help": "Use the IPv4 DNS response. If the IPv6 DNS response arrives first, wait 50ms for the IPv4 response and then use the IPv4 response, otherwise the IPv6.", "label": "Ipv4 Strict", "name": "ipv4-strict"}, {"description": "Use the IPv6 DNS response", "help": "Use the IPv6 DNS response. If the IPv4 DNS response arrives first, wait 50ms for the IPv6 response and then use the IPv6 response, otherwise the IPv4.", "label": "Ipv6 Strict", "name": "ipv6-strict"}] | None = ...,
        unknown_http_version: Literal[{"description": "Reject or tear down HTTP sessions that do not use HTTP 0", "help": "Reject or tear down HTTP sessions that do not use HTTP 0.9, 1.0, or 1.1.", "label": "Reject", "name": "reject"}, {"description": "Assume all HTTP sessions comply with HTTP 0", "help": "Assume all HTTP sessions comply with HTTP 0.9, 1.0, or 1.1. If a session uses a different HTTP version, it may not parse correctly and the connection may be lost.", "label": "Best Effort", "name": "best-effort"}] | None = ...,
        realm: str | None = ...,
        sec_default_action: Literal[{"description": "Accept requests", "help": "Accept requests. All explicit web proxy traffic is accepted whether there is an explicit web proxy policy or not.", "label": "Accept", "name": "accept"}, {"description": "Deny requests unless there is a matching explicit web proxy policy", "help": "Deny requests unless there is a matching explicit web proxy policy.", "label": "Deny", "name": "deny"}] | None = ...,
        https_replacement_message: Literal[{"description": "Display a replacement message for HTTPS requests", "help": "Display a replacement message for HTTPS requests.", "label": "Enable", "name": "enable"}, {"description": "Do not display a replacement message for HTTPS requests", "help": "Do not display a replacement message for HTTPS requests.", "label": "Disable", "name": "disable"}] | None = ...,
        message_upon_server_error: Literal[{"description": "Display a replacement message when a server error is detected", "help": "Display a replacement message when a server error is detected.", "label": "Enable", "name": "enable"}, {"description": "Do not display a replacement message when a server error is detected", "help": "Do not display a replacement message when a server error is detected.", "label": "Disable", "name": "disable"}] | None = ...,
        pac_file_server_status: Literal[{"description": "Enable Proxy Auto-Configuration (PAC)", "help": "Enable Proxy Auto-Configuration (PAC).", "label": "Enable", "name": "enable"}, {"description": "Disable Proxy Auto-Configuration (PAC)", "help": "Disable Proxy Auto-Configuration (PAC).", "label": "Disable", "name": "disable"}] | None = ...,
        pac_file_url: str | None = ...,
        pac_file_server_port: str | None = ...,
        pac_file_through_https: Literal[{"description": "Enable to get Proxy Auto-Configuration (PAC) through HTTPS", "help": "Enable to get Proxy Auto-Configuration (PAC) through HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable to get Proxy Auto-Configuration (PAC) through HTTPS", "help": "Disable to get Proxy Auto-Configuration (PAC) through HTTPS.", "label": "Disable", "name": "disable"}] | None = ...,
        pac_file_name: str | None = ...,
        pac_file_data: str | None = ...,
        pac_policy: list[dict[str, Any]] | None = ...,
        ssl_algorithm: Literal[{"description": "High encrption", "help": "High encrption. Allow only AES and ChaCha.", "label": "High", "name": "high"}, {"description": "Medium encryption", "help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}] | None = ...,
        trace_auth_no_rsp: Literal[{"description": "Enable logging timed-out authentication requests", "help": "Enable logging timed-out authentication requests.", "label": "Enable", "name": "enable"}, {"description": "Disable logging timed-out authentication requests", "help": "Disable logging timed-out authentication requests.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ExplicitPayload | None = ...,
        status: Literal[{"description": "Enable the explicit web proxy", "help": "Enable the explicit web proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the explicit web proxy", "help": "Disable the explicit web proxy.", "label": "Disable", "name": "disable"}] | None = ...,
        secure_web_proxy: Literal[{"description": "Disable secure webproxy", "help": "Disable secure webproxy.", "label": "Disable", "name": "disable"}, {"description": "Enable secure webproxy access", "help": "Enable secure webproxy access.", "label": "Enable", "name": "enable"}, {"description": "Require secure webproxy access", "help": "Require secure webproxy access.", "label": "Secure", "name": "secure"}] | None = ...,
        ftp_over_http: Literal[{"description": "Enable FTP-over-HTTP sessions", "help": "Enable FTP-over-HTTP sessions.", "label": "Enable", "name": "enable"}, {"description": "Disable FTP-over-HTTP sessions", "help": "Disable FTP-over-HTTP sessions.", "label": "Disable", "name": "disable"}] | None = ...,
        socks: Literal[{"description": "Enable the SOCKS proxy", "help": "Enable the SOCKS proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the SOCKS proxy", "help": "Disable the SOCKS proxy.", "label": "Disable", "name": "disable"}] | None = ...,
        http_incoming_port: str | None = ...,
        http_connection_mode: Literal[{"description": "Only one server connection exists during the proxy session", "help": "Only one server connection exists during the proxy session.", "label": "Static", "name": "static"}, {"description": "Established connections are held until the proxy session ends", "help": "Established connections are held until the proxy session ends.", "label": "Multiplex", "name": "multiplex"}, {"description": "Established connections are shared with other proxy sessions", "help": "Established connections are shared with other proxy sessions.", "label": "Serverpool", "name": "serverpool"}] | None = ...,
        https_incoming_port: str | None = ...,
        secure_web_proxy_cert: list[dict[str, Any]] | None = ...,
        client_cert: Literal[{"description": "Disable client certificate request", "help": "Disable client certificate request.", "label": "Disable", "name": "disable"}, {"description": "Enable client certificate request", "help": "Enable client certificate request.", "label": "Enable", "name": "enable"}] | None = ...,
        user_agent_detect: Literal[{"description": "Disable to detect unknown device by HTTP user-agent if no client certificate provided", "help": "Disable to detect unknown device by HTTP user-agent if no client certificate provided.", "label": "Disable", "name": "disable"}, {"description": "Enable to detect unknown device by HTTP user-agent if no client certificate provided", "help": "Enable to detect unknown device by HTTP user-agent if no client certificate provided.", "label": "Enable", "name": "enable"}] | None = ...,
        empty_cert_action: Literal[{"description": "Accept the SSL handshake if the client certificate is empty", "help": "Accept the SSL handshake if the client certificate is empty.", "label": "Accept", "name": "accept"}, {"description": "Block the SSL handshake if the client certificate is empty", "help": "Block the SSL handshake if the client certificate is empty.", "label": "Block", "name": "block"}, {"description": "Accept the SSL handshake only if the end-point is unmanageable", "help": "Accept the SSL handshake only if the end-point is unmanageable.", "label": "Accept Unmanageable", "name": "accept-unmanageable"}] | None = ...,
        ssl_dh_bits: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}] | None = ...,
        ftp_incoming_port: str | None = ...,
        socks_incoming_port: str | None = ...,
        incoming_ip: str | None = ...,
        outgoing_ip: list[dict[str, Any]] | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        ipv6_status: Literal[{"description": "Enable allowing an IPv6 web proxy destination", "help": "Enable allowing an IPv6 web proxy destination.", "label": "Enable", "name": "enable"}, {"description": "Disable allowing an IPv6 web proxy destination", "help": "Disable allowing an IPv6 web proxy destination.", "label": "Disable", "name": "disable"}] | None = ...,
        incoming_ip6: str | None = ...,
        outgoing_ip6: list[dict[str, Any]] | None = ...,
        strict_guest: Literal[{"description": "Enable strict guest user checking", "help": "Enable strict guest user checking.", "label": "Enable", "name": "enable"}, {"description": "Disable strict guest user checking", "help": "Disable strict guest user checking.", "label": "Disable", "name": "disable"}] | None = ...,
        pref_dns_result: Literal[{"description": "Send the IPv4 request first and then the IPv6 request", "help": "Send the IPv4 request first and then the IPv6 request. Use the DNS response that returns to the FortiGate first.", "label": "Ipv4", "name": "ipv4"}, {"description": "Send the IPv6 request first and then the IPv4 request", "help": "Send the IPv6 request first and then the IPv4 request. Use the DNS response that returns to the FortiGate first.", "label": "Ipv6", "name": "ipv6"}, {"description": "Use the IPv4 DNS response", "help": "Use the IPv4 DNS response. If the IPv6 DNS response arrives first, wait 50ms for the IPv4 response and then use the IPv4 response, otherwise the IPv6.", "label": "Ipv4 Strict", "name": "ipv4-strict"}, {"description": "Use the IPv6 DNS response", "help": "Use the IPv6 DNS response. If the IPv4 DNS response arrives first, wait 50ms for the IPv6 response and then use the IPv6 response, otherwise the IPv4.", "label": "Ipv6 Strict", "name": "ipv6-strict"}] | None = ...,
        unknown_http_version: Literal[{"description": "Reject or tear down HTTP sessions that do not use HTTP 0", "help": "Reject or tear down HTTP sessions that do not use HTTP 0.9, 1.0, or 1.1.", "label": "Reject", "name": "reject"}, {"description": "Assume all HTTP sessions comply with HTTP 0", "help": "Assume all HTTP sessions comply with HTTP 0.9, 1.0, or 1.1. If a session uses a different HTTP version, it may not parse correctly and the connection may be lost.", "label": "Best Effort", "name": "best-effort"}] | None = ...,
        realm: str | None = ...,
        sec_default_action: Literal[{"description": "Accept requests", "help": "Accept requests. All explicit web proxy traffic is accepted whether there is an explicit web proxy policy or not.", "label": "Accept", "name": "accept"}, {"description": "Deny requests unless there is a matching explicit web proxy policy", "help": "Deny requests unless there is a matching explicit web proxy policy.", "label": "Deny", "name": "deny"}] | None = ...,
        https_replacement_message: Literal[{"description": "Display a replacement message for HTTPS requests", "help": "Display a replacement message for HTTPS requests.", "label": "Enable", "name": "enable"}, {"description": "Do not display a replacement message for HTTPS requests", "help": "Do not display a replacement message for HTTPS requests.", "label": "Disable", "name": "disable"}] | None = ...,
        message_upon_server_error: Literal[{"description": "Display a replacement message when a server error is detected", "help": "Display a replacement message when a server error is detected.", "label": "Enable", "name": "enable"}, {"description": "Do not display a replacement message when a server error is detected", "help": "Do not display a replacement message when a server error is detected.", "label": "Disable", "name": "disable"}] | None = ...,
        pac_file_server_status: Literal[{"description": "Enable Proxy Auto-Configuration (PAC)", "help": "Enable Proxy Auto-Configuration (PAC).", "label": "Enable", "name": "enable"}, {"description": "Disable Proxy Auto-Configuration (PAC)", "help": "Disable Proxy Auto-Configuration (PAC).", "label": "Disable", "name": "disable"}] | None = ...,
        pac_file_url: str | None = ...,
        pac_file_server_port: str | None = ...,
        pac_file_through_https: Literal[{"description": "Enable to get Proxy Auto-Configuration (PAC) through HTTPS", "help": "Enable to get Proxy Auto-Configuration (PAC) through HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable to get Proxy Auto-Configuration (PAC) through HTTPS", "help": "Disable to get Proxy Auto-Configuration (PAC) through HTTPS.", "label": "Disable", "name": "disable"}] | None = ...,
        pac_file_name: str | None = ...,
        pac_file_data: str | None = ...,
        pac_policy: list[dict[str, Any]] | None = ...,
        ssl_algorithm: Literal[{"description": "High encrption", "help": "High encrption. Allow only AES and ChaCha.", "label": "High", "name": "high"}, {"description": "Medium encryption", "help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}] | None = ...,
        trace_auth_no_rsp: Literal[{"description": "Enable logging timed-out authentication requests", "help": "Enable logging timed-out authentication requests.", "label": "Enable", "name": "enable"}, {"description": "Disable logging timed-out authentication requests", "help": "Disable logging timed-out authentication requests.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: ExplicitPayload | None = ...,
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
    "Explicit",
    "ExplicitPayload",
]