from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class GlobalPayload(TypedDict, total=False):
    """
    Type hints for web_proxy/global_ payload fields.
    
    Configure Web proxy global settings.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.vpn.certificate.hsm-local.HsmLocalEndpoint` (via: ssl-ca-cert)
        - :class:`~.vpn.certificate.local.LocalEndpoint` (via: ssl-ca-cert, ssl-cert)
        - :class:`~.web-proxy.profile.ProfileEndpoint` (via: webproxy-profile)

    **Usage:**
        payload: GlobalPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    ssl_cert: NotRequired[str]  # SSL certificate for SSL interception.
    ssl_ca_cert: NotRequired[str]  # SSL CA certificate for SSL interception.
    fast_policy_match: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable fast matching algorithm for explicit and tran
    ldap_user_cache: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable LDAP user cache for explicit and transparent 
    proxy_fqdn: str  # Fully Qualified Domain Name of the explicit web proxy (defau
    max_request_length: NotRequired[int]  # Maximum length of HTTP request line (2 - 64 Kbytes, default 
    max_message_length: NotRequired[int]  # Maximum length of HTTP message, not including body (16 - 256
    http2_client_window_size: NotRequired[int]  # HTTP/2 client initial window size in bytes (65535 - 21474836
    http2_server_window_size: NotRequired[int]  # HTTP/2 server initial window size in bytes (65535 - 21474836
    auth_sign_timeout: NotRequired[int]  # Proxy auth query sign timeout in seconds (30 - 3600, default
    strict_web_check: NotRequired[Literal[{"description": "Enable strict web checking", "help": "Enable strict web checking.", "label": "Enable", "name": "enable"}, {"description": "Disable strict web checking", "help": "Disable strict web checking.", "label": "Disable", "name": "disable"}]]  # Enable/disable strict web checking to block web sites that s
    forward_proxy_auth: NotRequired[Literal[{"description": "Enable forwarding proxy authentication headers", "help": "Enable forwarding proxy authentication headers.", "label": "Enable", "name": "enable"}, {"description": "Disable forwarding proxy authentication headers", "help": "Disable forwarding proxy authentication headers.", "label": "Disable", "name": "disable"}]]  # Enable/disable forwarding proxy authentication headers.
    forward_server_affinity_timeout: NotRequired[int]  # Period of time before the source IP's traffic is no longer a
    max_waf_body_cache_length: NotRequired[int]  # Maximum length of HTTP messages processed by Web Application
    webproxy_profile: NotRequired[str]  # Name of the web proxy profile to apply when explicit proxy t
    learn_client_ip: NotRequired[Literal[{"description": "Enable learning the client\u0027s IP address from headers", "help": "Enable learning the client\u0027s IP address from headers.", "label": "Enable", "name": "enable"}, {"description": "Disable learning the client\u0027s IP address from headers", "help": "Disable learning the client\u0027s IP address from headers.", "label": "Disable", "name": "disable"}]]  # Enable/disable learning the client's IP address from headers
    always_learn_client_ip: NotRequired[Literal[{"description": "Enable learning the client\u0027s IP address from headers for every request", "help": "Enable learning the client\u0027s IP address from headers for every request.", "label": "Enable", "name": "enable"}, {"description": "Disable learning the client\u0027s IP address from headers for every request", "help": "Disable learning the client\u0027s IP address from headers for every request.", "label": "Disable", "name": "disable"}]]  # Enable/disable learning the client's IP address from headers
    learn_client_ip_from_header: NotRequired[Literal[{"description": "Learn the client IP address from the True-Client-IP header", "help": "Learn the client IP address from the True-Client-IP header.", "label": "True Client Ip", "name": "true-client-ip"}, {"description": "Learn the client IP address from the X-Real-IP header", "help": "Learn the client IP address from the X-Real-IP header.", "label": "X Real Ip", "name": "x-real-ip"}, {"description": "Learn the client IP address from the X-Forwarded-For header", "help": "Learn the client IP address from the X-Forwarded-For header.", "label": "X Forwarded For", "name": "x-forwarded-for"}]]  # Learn client IP address from the specified headers.
    learn_client_ip_srcaddr: NotRequired[list[dict[str, Any]]]  # Source address name (srcaddr or srcaddr6 must be set).
    learn_client_ip_srcaddr6: NotRequired[list[dict[str, Any]]]  # IPv6 Source address name (srcaddr or srcaddr6 must be set).
    src_affinity_exempt_addr: NotRequired[list[dict[str, Any]]]  # IPv4 source addresses to exempt proxy affinity.
    src_affinity_exempt_addr6: NotRequired[list[dict[str, Any]]]  # IPv6 source addresses to exempt proxy affinity.
    policy_partial_match: NotRequired[Literal[{"description": "Enable policy partial matching", "help": "Enable policy partial matching.", "label": "Enable", "name": "enable"}, {"description": "Disable policy partial matching", "help": "Disable policy partial matching.", "label": "Disable", "name": "disable"}]]  # Enable/disable policy partial matching.
    log_policy_pending: NotRequired[Literal[{"description": "Enable logging sessions that are pending on policy matching", "help": "Enable logging sessions that are pending on policy matching.", "label": "Enable", "name": "enable"}, {"description": "Disable logging sessions that are pending on policy matching", "help": "Disable logging sessions that are pending on policy matching.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging sessions that are pending on policy m
    log_forward_server: NotRequired[Literal[{"description": "Enable logging forward server name in forward traffic log", "help": "Enable logging forward server name in forward traffic log.", "label": "Enable", "name": "enable"}, {"description": "Disable logging forward server name in forward traffic log", "help": "Disable logging forward server name in forward traffic log.", "label": "Disable", "name": "disable"}]]  # Enable/disable forward server name logging in forward traffi
    log_app_id: NotRequired[Literal[{"description": "Enable logging application type in traffic log", "help": "Enable logging application type in traffic log.", "label": "Enable", "name": "enable"}, {"description": "Disable logging application type in traffic log", "help": "Disable logging application type in traffic log.", "label": "Disable", "name": "disable"}]]  # Enable/disable always log application type in traffic log.
    proxy_transparent_cert_inspection: NotRequired[Literal[{"description": "Enable proxying certificate inspection in transparent mode", "help": "Enable proxying certificate inspection in transparent mode.", "label": "Enable", "name": "enable"}, {"description": "Disable proxying certificate inspection in transparent mode", "help": "Disable proxying certificate inspection in transparent mode.", "label": "Disable", "name": "disable"}]]  # Enable/disable transparent proxy certificate inspection.
    request_obs_fold: NotRequired[Literal[{"description": "Replace CRLF in obs-fold with SP in the request header for HTTP/1", "help": "Replace CRLF in obs-fold with SP in the request header for HTTP/1.x.", "label": "Replace With Sp", "name": "replace-with-sp"}, {"description": "Block HTTP/1", "help": "Block HTTP/1.x request with obs-fold.", "label": "Block", "name": "block"}, {"description": "Keep obs-fold in the request header for HTTP/1", "help": "Keep obs-fold in the request header for HTTP/1.x. There are known security risks.", "label": "Keep", "name": "keep"}]]  # Action when HTTP/1.x request header contains obs-fold (defau


class Global:
    """
    Configure Web proxy global settings.
    
    Path: web_proxy/global_
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
        payload_dict: GlobalPayload | None = ...,
        ssl_cert: str | None = ...,
        ssl_ca_cert: str | None = ...,
        fast_policy_match: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ldap_user_cache: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        proxy_fqdn: str | None = ...,
        max_request_length: int | None = ...,
        max_message_length: int | None = ...,
        http2_client_window_size: int | None = ...,
        http2_server_window_size: int | None = ...,
        auth_sign_timeout: int | None = ...,
        strict_web_check: Literal[{"description": "Enable strict web checking", "help": "Enable strict web checking.", "label": "Enable", "name": "enable"}, {"description": "Disable strict web checking", "help": "Disable strict web checking.", "label": "Disable", "name": "disable"}] | None = ...,
        forward_proxy_auth: Literal[{"description": "Enable forwarding proxy authentication headers", "help": "Enable forwarding proxy authentication headers.", "label": "Enable", "name": "enable"}, {"description": "Disable forwarding proxy authentication headers", "help": "Disable forwarding proxy authentication headers.", "label": "Disable", "name": "disable"}] | None = ...,
        forward_server_affinity_timeout: int | None = ...,
        max_waf_body_cache_length: int | None = ...,
        webproxy_profile: str | None = ...,
        learn_client_ip: Literal[{"description": "Enable learning the client\u0027s IP address from headers", "help": "Enable learning the client\u0027s IP address from headers.", "label": "Enable", "name": "enable"}, {"description": "Disable learning the client\u0027s IP address from headers", "help": "Disable learning the client\u0027s IP address from headers.", "label": "Disable", "name": "disable"}] | None = ...,
        always_learn_client_ip: Literal[{"description": "Enable learning the client\u0027s IP address from headers for every request", "help": "Enable learning the client\u0027s IP address from headers for every request.", "label": "Enable", "name": "enable"}, {"description": "Disable learning the client\u0027s IP address from headers for every request", "help": "Disable learning the client\u0027s IP address from headers for every request.", "label": "Disable", "name": "disable"}] | None = ...,
        learn_client_ip_from_header: Literal[{"description": "Learn the client IP address from the True-Client-IP header", "help": "Learn the client IP address from the True-Client-IP header.", "label": "True Client Ip", "name": "true-client-ip"}, {"description": "Learn the client IP address from the X-Real-IP header", "help": "Learn the client IP address from the X-Real-IP header.", "label": "X Real Ip", "name": "x-real-ip"}, {"description": "Learn the client IP address from the X-Forwarded-For header", "help": "Learn the client IP address from the X-Forwarded-For header.", "label": "X Forwarded For", "name": "x-forwarded-for"}] | None = ...,
        learn_client_ip_srcaddr: list[dict[str, Any]] | None = ...,
        learn_client_ip_srcaddr6: list[dict[str, Any]] | None = ...,
        src_affinity_exempt_addr: list[dict[str, Any]] | None = ...,
        src_affinity_exempt_addr6: list[dict[str, Any]] | None = ...,
        policy_partial_match: Literal[{"description": "Enable policy partial matching", "help": "Enable policy partial matching.", "label": "Enable", "name": "enable"}, {"description": "Disable policy partial matching", "help": "Disable policy partial matching.", "label": "Disable", "name": "disable"}] | None = ...,
        log_policy_pending: Literal[{"description": "Enable logging sessions that are pending on policy matching", "help": "Enable logging sessions that are pending on policy matching.", "label": "Enable", "name": "enable"}, {"description": "Disable logging sessions that are pending on policy matching", "help": "Disable logging sessions that are pending on policy matching.", "label": "Disable", "name": "disable"}] | None = ...,
        log_forward_server: Literal[{"description": "Enable logging forward server name in forward traffic log", "help": "Enable logging forward server name in forward traffic log.", "label": "Enable", "name": "enable"}, {"description": "Disable logging forward server name in forward traffic log", "help": "Disable logging forward server name in forward traffic log.", "label": "Disable", "name": "disable"}] | None = ...,
        log_app_id: Literal[{"description": "Enable logging application type in traffic log", "help": "Enable logging application type in traffic log.", "label": "Enable", "name": "enable"}, {"description": "Disable logging application type in traffic log", "help": "Disable logging application type in traffic log.", "label": "Disable", "name": "disable"}] | None = ...,
        proxy_transparent_cert_inspection: Literal[{"description": "Enable proxying certificate inspection in transparent mode", "help": "Enable proxying certificate inspection in transparent mode.", "label": "Enable", "name": "enable"}, {"description": "Disable proxying certificate inspection in transparent mode", "help": "Disable proxying certificate inspection in transparent mode.", "label": "Disable", "name": "disable"}] | None = ...,
        request_obs_fold: Literal[{"description": "Replace CRLF in obs-fold with SP in the request header for HTTP/1", "help": "Replace CRLF in obs-fold with SP in the request header for HTTP/1.x.", "label": "Replace With Sp", "name": "replace-with-sp"}, {"description": "Block HTTP/1", "help": "Block HTTP/1.x request with obs-fold.", "label": "Block", "name": "block"}, {"description": "Keep obs-fold in the request header for HTTP/1", "help": "Keep obs-fold in the request header for HTTP/1.x. There are known security risks.", "label": "Keep", "name": "keep"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: GlobalPayload | None = ...,
        ssl_cert: str | None = ...,
        ssl_ca_cert: str | None = ...,
        fast_policy_match: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ldap_user_cache: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        proxy_fqdn: str | None = ...,
        max_request_length: int | None = ...,
        max_message_length: int | None = ...,
        http2_client_window_size: int | None = ...,
        http2_server_window_size: int | None = ...,
        auth_sign_timeout: int | None = ...,
        strict_web_check: Literal[{"description": "Enable strict web checking", "help": "Enable strict web checking.", "label": "Enable", "name": "enable"}, {"description": "Disable strict web checking", "help": "Disable strict web checking.", "label": "Disable", "name": "disable"}] | None = ...,
        forward_proxy_auth: Literal[{"description": "Enable forwarding proxy authentication headers", "help": "Enable forwarding proxy authentication headers.", "label": "Enable", "name": "enable"}, {"description": "Disable forwarding proxy authentication headers", "help": "Disable forwarding proxy authentication headers.", "label": "Disable", "name": "disable"}] | None = ...,
        forward_server_affinity_timeout: int | None = ...,
        max_waf_body_cache_length: int | None = ...,
        webproxy_profile: str | None = ...,
        learn_client_ip: Literal[{"description": "Enable learning the client\u0027s IP address from headers", "help": "Enable learning the client\u0027s IP address from headers.", "label": "Enable", "name": "enable"}, {"description": "Disable learning the client\u0027s IP address from headers", "help": "Disable learning the client\u0027s IP address from headers.", "label": "Disable", "name": "disable"}] | None = ...,
        always_learn_client_ip: Literal[{"description": "Enable learning the client\u0027s IP address from headers for every request", "help": "Enable learning the client\u0027s IP address from headers for every request.", "label": "Enable", "name": "enable"}, {"description": "Disable learning the client\u0027s IP address from headers for every request", "help": "Disable learning the client\u0027s IP address from headers for every request.", "label": "Disable", "name": "disable"}] | None = ...,
        learn_client_ip_from_header: Literal[{"description": "Learn the client IP address from the True-Client-IP header", "help": "Learn the client IP address from the True-Client-IP header.", "label": "True Client Ip", "name": "true-client-ip"}, {"description": "Learn the client IP address from the X-Real-IP header", "help": "Learn the client IP address from the X-Real-IP header.", "label": "X Real Ip", "name": "x-real-ip"}, {"description": "Learn the client IP address from the X-Forwarded-For header", "help": "Learn the client IP address from the X-Forwarded-For header.", "label": "X Forwarded For", "name": "x-forwarded-for"}] | None = ...,
        learn_client_ip_srcaddr: list[dict[str, Any]] | None = ...,
        learn_client_ip_srcaddr6: list[dict[str, Any]] | None = ...,
        src_affinity_exempt_addr: list[dict[str, Any]] | None = ...,
        src_affinity_exempt_addr6: list[dict[str, Any]] | None = ...,
        policy_partial_match: Literal[{"description": "Enable policy partial matching", "help": "Enable policy partial matching.", "label": "Enable", "name": "enable"}, {"description": "Disable policy partial matching", "help": "Disable policy partial matching.", "label": "Disable", "name": "disable"}] | None = ...,
        log_policy_pending: Literal[{"description": "Enable logging sessions that are pending on policy matching", "help": "Enable logging sessions that are pending on policy matching.", "label": "Enable", "name": "enable"}, {"description": "Disable logging sessions that are pending on policy matching", "help": "Disable logging sessions that are pending on policy matching.", "label": "Disable", "name": "disable"}] | None = ...,
        log_forward_server: Literal[{"description": "Enable logging forward server name in forward traffic log", "help": "Enable logging forward server name in forward traffic log.", "label": "Enable", "name": "enable"}, {"description": "Disable logging forward server name in forward traffic log", "help": "Disable logging forward server name in forward traffic log.", "label": "Disable", "name": "disable"}] | None = ...,
        log_app_id: Literal[{"description": "Enable logging application type in traffic log", "help": "Enable logging application type in traffic log.", "label": "Enable", "name": "enable"}, {"description": "Disable logging application type in traffic log", "help": "Disable logging application type in traffic log.", "label": "Disable", "name": "disable"}] | None = ...,
        proxy_transparent_cert_inspection: Literal[{"description": "Enable proxying certificate inspection in transparent mode", "help": "Enable proxying certificate inspection in transparent mode.", "label": "Enable", "name": "enable"}, {"description": "Disable proxying certificate inspection in transparent mode", "help": "Disable proxying certificate inspection in transparent mode.", "label": "Disable", "name": "disable"}] | None = ...,
        request_obs_fold: Literal[{"description": "Replace CRLF in obs-fold with SP in the request header for HTTP/1", "help": "Replace CRLF in obs-fold with SP in the request header for HTTP/1.x.", "label": "Replace With Sp", "name": "replace-with-sp"}, {"description": "Block HTTP/1", "help": "Block HTTP/1.x request with obs-fold.", "label": "Block", "name": "block"}, {"description": "Keep obs-fold in the request header for HTTP/1", "help": "Keep obs-fold in the request header for HTTP/1.x. There are known security risks.", "label": "Keep", "name": "keep"}] | None = ...,
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
        payload_dict: GlobalPayload | None = ...,
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
    "Global",
    "GlobalPayload",
]