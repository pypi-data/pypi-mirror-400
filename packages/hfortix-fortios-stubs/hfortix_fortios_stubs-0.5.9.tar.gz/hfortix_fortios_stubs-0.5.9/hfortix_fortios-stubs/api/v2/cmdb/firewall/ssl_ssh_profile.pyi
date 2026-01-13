from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SslSshProfilePayload(TypedDict, total=False):
    """
    Type hints for firewall/ssl_ssh_profile payload fields.
    
    Configure SSL/SSH protocol options.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.vpn.certificate.hsm-local.HsmLocalEndpoint` (via: caname, untrusted-caname)
        - :class:`~.vpn.certificate.local.LocalEndpoint` (via: caname, untrusted-caname)

    **Usage:**
        payload: SslSshProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Name.
    comment: NotRequired[str]  # Optional comments.
    ssl: NotRequired[str]  # Configure SSL options.
    https: NotRequired[str]  # Configure HTTPS options.
    ftps: NotRequired[str]  # Configure FTPS options.
    imaps: NotRequired[str]  # Configure IMAPS options.
    pop3s: NotRequired[str]  # Configure POP3S options.
    smtps: NotRequired[str]  # Configure SMTPS options.
    ssh: NotRequired[str]  # Configure SSH options.
    dot: NotRequired[str]  # Configure DNS over TLS options.
    allowlist: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable exempting servers by FortiGuard allowlist.
    block_blocklisted_certificates: NotRequired[Literal[{"description": "Disable FortiGuard certificate blocklist", "help": "Disable FortiGuard certificate blocklist.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiGuard certificate blocklist", "help": "Enable FortiGuard certificate blocklist.", "label": "Enable", "name": "enable"}]]  # Enable/disable blocking SSL-based botnet communication by Fo
    ssl_exempt: NotRequired[list[dict[str, Any]]]  # Servers to exempt from SSL inspection.
    ech_outer_sni: NotRequired[list[dict[str, Any]]]  # ClientHelloOuter SNIs to be blocked.
    server_cert_mode: Literal[{"description": "Multiple clients connecting to multiple servers", "help": "Multiple clients connecting to multiple servers.", "label": "Re Sign", "name": "re-sign"}, {"description": "Protect an SSL server", "help": "Protect an SSL server.", "label": "Replace", "name": "replace"}]  # Re-sign or replace the server's certificate.
    use_ssl_server: NotRequired[Literal[{"description": "Don\u0027t use SSL server configuration", "help": "Don\u0027t use SSL server configuration.", "label": "Disable", "name": "disable"}, {"description": "Use SSL server configuration", "help": "Use SSL server configuration.", "label": "Enable", "name": "enable"}]]  # Enable/disable the use of SSL server table for SSL offloadin
    caname: str  # CA certificate used by SSL Inspection.
    untrusted_caname: str  # Untrusted CA certificate used by SSL Inspection.
    server_cert: NotRequired[list[dict[str, Any]]]  # Certificate used by SSL Inspection to replace server certifi
    ssl_server: list[dict[str, Any]]  # SSL server settings used for client certificate request.
    ssl_exemption_ip_rating: NotRequired[Literal[{"description": "Enable IP based URL rating", "help": "Enable IP based URL rating.", "label": "Enable", "name": "enable"}, {"description": "Disable IP based URL rating", "help": "Disable IP based URL rating.", "label": "Disable", "name": "disable"}]]  # Enable/disable IP based URL rating.
    ssl_exemption_log: NotRequired[Literal[{"description": "Disable logging of SSL exemptions", "help": "Disable logging of SSL exemptions.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of SSL exemptions", "help": "Enable logging of SSL exemptions.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging of SSL exemptions.
    ssl_anomaly_log: NotRequired[Literal[{"description": "Disable logging of SSL anomalies", "help": "Disable logging of SSL anomalies.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of SSL anomalies", "help": "Enable logging of SSL anomalies.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging of SSL anomalies.
    ssl_negotiation_log: NotRequired[Literal[{"description": "Disable logging of SSL negotiation events", "help": "Disable logging of SSL negotiation events.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of SSL negotiation events", "help": "Enable logging of SSL negotiation events.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging of SSL negotiation events.
    ssl_server_cert_log: NotRequired[Literal[{"description": "Disable logging of server certificate information", "help": "Disable logging of server certificate information.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of server certificate information", "help": "Enable logging of server certificate information.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging of server certificate information.
    ssl_handshake_log: NotRequired[Literal[{"description": "Disable logging of TLS handshakes", "help": "Disable logging of TLS handshakes.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of TLS handshakes", "help": "Enable logging of TLS handshakes.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging of TLS handshakes.
    rpc_over_https: NotRequired[Literal[{"description": "Enable inspection of RPC over HTTPS", "help": "Enable inspection of RPC over HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable inspection of RPC over HTTPS", "help": "Disable inspection of RPC over HTTPS.", "label": "Disable", "name": "disable"}]]  # Enable/disable inspection of RPC over HTTPS.
    mapi_over_https: NotRequired[Literal[{"description": "Enable inspection of MAPI over HTTPS", "help": "Enable inspection of MAPI over HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable inspection of MAPI over HTTPS", "help": "Disable inspection of MAPI over HTTPS.", "label": "Disable", "name": "disable"}]]  # Enable/disable inspection of MAPI over HTTPS.
    supported_alpn: NotRequired[Literal[{"description": "Enable all ALPN including HTTP1", "help": "Enable all ALPN including HTTP1.1 except HTTP2 and SPDY.", "label": "Http1 1", "name": "http1-1"}, {"description": "Enable all ALPN including HTTP2 except HTTP1", "help": "Enable all ALPN including HTTP2 except HTTP1.1 and SPDY.", "label": "Http2", "name": "http2"}, {"description": "Allow all ALPN extensions except SPDY", "help": "Allow all ALPN extensions except SPDY.", "label": "All", "name": "all"}, {"description": "Do not use ALPN", "help": "Do not use ALPN.", "label": "None", "name": "none"}]]  # Configure ALPN option.


class SslSshProfile:
    """
    Configure SSL/SSH protocol options.
    
    Path: firewall/ssl_ssh_profile
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
        payload_dict: SslSshProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        ssl: str | None = ...,
        https: str | None = ...,
        ftps: str | None = ...,
        imaps: str | None = ...,
        pop3s: str | None = ...,
        smtps: str | None = ...,
        ssh: str | None = ...,
        dot: str | None = ...,
        allowlist: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        block_blocklisted_certificates: Literal[{"description": "Disable FortiGuard certificate blocklist", "help": "Disable FortiGuard certificate blocklist.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiGuard certificate blocklist", "help": "Enable FortiGuard certificate blocklist.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_exempt: list[dict[str, Any]] | None = ...,
        ech_outer_sni: list[dict[str, Any]] | None = ...,
        server_cert_mode: Literal[{"description": "Multiple clients connecting to multiple servers", "help": "Multiple clients connecting to multiple servers.", "label": "Re Sign", "name": "re-sign"}, {"description": "Protect an SSL server", "help": "Protect an SSL server.", "label": "Replace", "name": "replace"}] | None = ...,
        use_ssl_server: Literal[{"description": "Don\u0027t use SSL server configuration", "help": "Don\u0027t use SSL server configuration.", "label": "Disable", "name": "disable"}, {"description": "Use SSL server configuration", "help": "Use SSL server configuration.", "label": "Enable", "name": "enable"}] | None = ...,
        caname: str | None = ...,
        untrusted_caname: str | None = ...,
        server_cert: list[dict[str, Any]] | None = ...,
        ssl_server: list[dict[str, Any]] | None = ...,
        ssl_exemption_ip_rating: Literal[{"description": "Enable IP based URL rating", "help": "Enable IP based URL rating.", "label": "Enable", "name": "enable"}, {"description": "Disable IP based URL rating", "help": "Disable IP based URL rating.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_exemption_log: Literal[{"description": "Disable logging of SSL exemptions", "help": "Disable logging of SSL exemptions.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of SSL exemptions", "help": "Enable logging of SSL exemptions.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_anomaly_log: Literal[{"description": "Disable logging of SSL anomalies", "help": "Disable logging of SSL anomalies.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of SSL anomalies", "help": "Enable logging of SSL anomalies.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_negotiation_log: Literal[{"description": "Disable logging of SSL negotiation events", "help": "Disable logging of SSL negotiation events.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of SSL negotiation events", "help": "Enable logging of SSL negotiation events.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_server_cert_log: Literal[{"description": "Disable logging of server certificate information", "help": "Disable logging of server certificate information.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of server certificate information", "help": "Enable logging of server certificate information.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_handshake_log: Literal[{"description": "Disable logging of TLS handshakes", "help": "Disable logging of TLS handshakes.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of TLS handshakes", "help": "Enable logging of TLS handshakes.", "label": "Enable", "name": "enable"}] | None = ...,
        rpc_over_https: Literal[{"description": "Enable inspection of RPC over HTTPS", "help": "Enable inspection of RPC over HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable inspection of RPC over HTTPS", "help": "Disable inspection of RPC over HTTPS.", "label": "Disable", "name": "disable"}] | None = ...,
        mapi_over_https: Literal[{"description": "Enable inspection of MAPI over HTTPS", "help": "Enable inspection of MAPI over HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable inspection of MAPI over HTTPS", "help": "Disable inspection of MAPI over HTTPS.", "label": "Disable", "name": "disable"}] | None = ...,
        supported_alpn: Literal[{"description": "Enable all ALPN including HTTP1", "help": "Enable all ALPN including HTTP1.1 except HTTP2 and SPDY.", "label": "Http1 1", "name": "http1-1"}, {"description": "Enable all ALPN including HTTP2 except HTTP1", "help": "Enable all ALPN including HTTP2 except HTTP1.1 and SPDY.", "label": "Http2", "name": "http2"}, {"description": "Allow all ALPN extensions except SPDY", "help": "Allow all ALPN extensions except SPDY.", "label": "All", "name": "all"}, {"description": "Do not use ALPN", "help": "Do not use ALPN.", "label": "None", "name": "none"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SslSshProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        ssl: str | None = ...,
        https: str | None = ...,
        ftps: str | None = ...,
        imaps: str | None = ...,
        pop3s: str | None = ...,
        smtps: str | None = ...,
        ssh: str | None = ...,
        dot: str | None = ...,
        allowlist: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        block_blocklisted_certificates: Literal[{"description": "Disable FortiGuard certificate blocklist", "help": "Disable FortiGuard certificate blocklist.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiGuard certificate blocklist", "help": "Enable FortiGuard certificate blocklist.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_exempt: list[dict[str, Any]] | None = ...,
        ech_outer_sni: list[dict[str, Any]] | None = ...,
        server_cert_mode: Literal[{"description": "Multiple clients connecting to multiple servers", "help": "Multiple clients connecting to multiple servers.", "label": "Re Sign", "name": "re-sign"}, {"description": "Protect an SSL server", "help": "Protect an SSL server.", "label": "Replace", "name": "replace"}] | None = ...,
        use_ssl_server: Literal[{"description": "Don\u0027t use SSL server configuration", "help": "Don\u0027t use SSL server configuration.", "label": "Disable", "name": "disable"}, {"description": "Use SSL server configuration", "help": "Use SSL server configuration.", "label": "Enable", "name": "enable"}] | None = ...,
        caname: str | None = ...,
        untrusted_caname: str | None = ...,
        server_cert: list[dict[str, Any]] | None = ...,
        ssl_server: list[dict[str, Any]] | None = ...,
        ssl_exemption_ip_rating: Literal[{"description": "Enable IP based URL rating", "help": "Enable IP based URL rating.", "label": "Enable", "name": "enable"}, {"description": "Disable IP based URL rating", "help": "Disable IP based URL rating.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_exemption_log: Literal[{"description": "Disable logging of SSL exemptions", "help": "Disable logging of SSL exemptions.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of SSL exemptions", "help": "Enable logging of SSL exemptions.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_anomaly_log: Literal[{"description": "Disable logging of SSL anomalies", "help": "Disable logging of SSL anomalies.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of SSL anomalies", "help": "Enable logging of SSL anomalies.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_negotiation_log: Literal[{"description": "Disable logging of SSL negotiation events", "help": "Disable logging of SSL negotiation events.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of SSL negotiation events", "help": "Enable logging of SSL negotiation events.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_server_cert_log: Literal[{"description": "Disable logging of server certificate information", "help": "Disable logging of server certificate information.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of server certificate information", "help": "Enable logging of server certificate information.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_handshake_log: Literal[{"description": "Disable logging of TLS handshakes", "help": "Disable logging of TLS handshakes.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of TLS handshakes", "help": "Enable logging of TLS handshakes.", "label": "Enable", "name": "enable"}] | None = ...,
        rpc_over_https: Literal[{"description": "Enable inspection of RPC over HTTPS", "help": "Enable inspection of RPC over HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable inspection of RPC over HTTPS", "help": "Disable inspection of RPC over HTTPS.", "label": "Disable", "name": "disable"}] | None = ...,
        mapi_over_https: Literal[{"description": "Enable inspection of MAPI over HTTPS", "help": "Enable inspection of MAPI over HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable inspection of MAPI over HTTPS", "help": "Disable inspection of MAPI over HTTPS.", "label": "Disable", "name": "disable"}] | None = ...,
        supported_alpn: Literal[{"description": "Enable all ALPN including HTTP1", "help": "Enable all ALPN including HTTP1.1 except HTTP2 and SPDY.", "label": "Http1 1", "name": "http1-1"}, {"description": "Enable all ALPN including HTTP2 except HTTP1", "help": "Enable all ALPN including HTTP2 except HTTP1.1 and SPDY.", "label": "Http2", "name": "http2"}, {"description": "Allow all ALPN extensions except SPDY", "help": "Allow all ALPN extensions except SPDY.", "label": "All", "name": "all"}, {"description": "Do not use ALPN", "help": "Do not use ALPN.", "label": "None", "name": "none"}] | None = ...,
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
        payload_dict: SslSshProfilePayload | None = ...,
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
    "SslSshProfile",
    "SslSshProfilePayload",
]