from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class DnsPayload(TypedDict, total=False):
    """
    Type hints for system/dns payload fields.
    
    Configure DNS.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.local.LocalEndpoint` (via: ssl-certificate)
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface, source-ip-interface)

    **Usage:**
        payload: DnsPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    primary: str  # Primary DNS server IP address.
    secondary: NotRequired[str]  # Secondary DNS server IP address.
    protocol: NotRequired[Literal[{"description": "DNS over UDP/53, DNS over TCP/53", "help": "DNS over UDP/53, DNS over TCP/53.", "label": "Cleartext", "name": "cleartext"}, {"description": "DNS over TLS/853", "help": "DNS over TLS/853.", "label": "Dot", "name": "dot"}, {"description": "DNS over HTTPS/443", "help": "DNS over HTTPS/443.", "label": "Doh", "name": "doh"}]]  # DNS transport protocols.
    ssl_certificate: NotRequired[str]  # Name of local certificate for SSL connections.
    server_hostname: NotRequired[list[dict[str, Any]]]  # DNS server host name list.
    domain: NotRequired[list[dict[str, Any]]]  # Search suffix list for hostname lookup.
    ip6_primary: NotRequired[str]  # Primary DNS server IPv6 address.
    ip6_secondary: NotRequired[str]  # Secondary DNS server IPv6 address.
    timeout: NotRequired[int]  # DNS query timeout interval in seconds (1 - 10).
    retry: NotRequired[int]  # Number of times to retry (0 - 5).
    dns_cache_limit: NotRequired[int]  # Maximum number of records in the DNS cache.
    dns_cache_ttl: NotRequired[int]  # Duration in seconds that the DNS cache retains information.
    cache_notfound_responses: NotRequired[Literal[{"description": "Disable cache NOTFOUND responses from DNS server", "help": "Disable cache NOTFOUND responses from DNS server.", "label": "Disable", "name": "disable"}, {"description": "Enable cache NOTFOUND responses from DNS server", "help": "Enable cache NOTFOUND responses from DNS server.", "label": "Enable", "name": "enable"}]]  # Enable/disable response from the DNS server when a record is
    source_ip: NotRequired[str]  # IP address used by the DNS server as its source IP.
    source_ip_interface: NotRequired[str]  # IP address of the specified interface as the source IP addre
    root_servers: NotRequired[list[dict[str, Any]]]  # Configure up to two preferred servers that serve the DNS roo
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.
    server_select_method: NotRequired[Literal[{"description": "Select servers based on least round trip time", "help": "Select servers based on least round trip time.", "label": "Least Rtt", "name": "least-rtt"}, {"description": "Select servers based on the order they are configured", "help": "Select servers based on the order they are configured.", "label": "Failover", "name": "failover"}]]  # Specify how configured servers are prioritized.
    alt_primary: NotRequired[str]  # Alternate primary DNS server. This is not used as a failover
    alt_secondary: NotRequired[str]  # Alternate secondary DNS server. This is not used as a failov
    log: NotRequired[Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Enable local DNS error log", "help": "Enable local DNS error log.", "label": "Error", "name": "error"}, {"description": "Enable local DNS log", "help": "Enable local DNS log.", "label": "All", "name": "all"}]]  # Local DNS log setting.
    fqdn_cache_ttl: NotRequired[int]  # FQDN cache time to live in seconds (0 - 86400, default = 0).
    fqdn_max_refresh: NotRequired[int]  # FQDN cache maximum refresh time in seconds (3600 - 86400, de
    fqdn_min_refresh: NotRequired[int]  # FQDN cache minimum refresh time in seconds (10 - 3600, defau
    hostname_ttl: NotRequired[int]  # TTL of hostname table entries (60 - 86400).
    hostname_limit: NotRequired[int]  # Limit of the number of hostname table entries (0 - 50000).


class Dns:
    """
    Configure DNS.
    
    Path: system/dns
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
        payload_dict: DnsPayload | None = ...,
        primary: str | None = ...,
        secondary: str | None = ...,
        protocol: Literal[{"description": "DNS over UDP/53, DNS over TCP/53", "help": "DNS over UDP/53, DNS over TCP/53.", "label": "Cleartext", "name": "cleartext"}, {"description": "DNS over TLS/853", "help": "DNS over TLS/853.", "label": "Dot", "name": "dot"}, {"description": "DNS over HTTPS/443", "help": "DNS over HTTPS/443.", "label": "Doh", "name": "doh"}] | None = ...,
        ssl_certificate: str | None = ...,
        server_hostname: list[dict[str, Any]] | None = ...,
        domain: list[dict[str, Any]] | None = ...,
        ip6_primary: str | None = ...,
        ip6_secondary: str | None = ...,
        timeout: int | None = ...,
        retry: int | None = ...,
        dns_cache_limit: int | None = ...,
        dns_cache_ttl: int | None = ...,
        cache_notfound_responses: Literal[{"description": "Disable cache NOTFOUND responses from DNS server", "help": "Disable cache NOTFOUND responses from DNS server.", "label": "Disable", "name": "disable"}, {"description": "Enable cache NOTFOUND responses from DNS server", "help": "Enable cache NOTFOUND responses from DNS server.", "label": "Enable", "name": "enable"}] | None = ...,
        source_ip: str | None = ...,
        source_ip_interface: str | None = ...,
        root_servers: list[dict[str, Any]] | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        server_select_method: Literal[{"description": "Select servers based on least round trip time", "help": "Select servers based on least round trip time.", "label": "Least Rtt", "name": "least-rtt"}, {"description": "Select servers based on the order they are configured", "help": "Select servers based on the order they are configured.", "label": "Failover", "name": "failover"}] | None = ...,
        alt_primary: str | None = ...,
        alt_secondary: str | None = ...,
        log: Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Enable local DNS error log", "help": "Enable local DNS error log.", "label": "Error", "name": "error"}, {"description": "Enable local DNS log", "help": "Enable local DNS log.", "label": "All", "name": "all"}] | None = ...,
        fqdn_cache_ttl: int | None = ...,
        fqdn_max_refresh: int | None = ...,
        fqdn_min_refresh: int | None = ...,
        hostname_ttl: int | None = ...,
        hostname_limit: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: DnsPayload | None = ...,
        primary: str | None = ...,
        secondary: str | None = ...,
        protocol: Literal[{"description": "DNS over UDP/53, DNS over TCP/53", "help": "DNS over UDP/53, DNS over TCP/53.", "label": "Cleartext", "name": "cleartext"}, {"description": "DNS over TLS/853", "help": "DNS over TLS/853.", "label": "Dot", "name": "dot"}, {"description": "DNS over HTTPS/443", "help": "DNS over HTTPS/443.", "label": "Doh", "name": "doh"}] | None = ...,
        ssl_certificate: str | None = ...,
        server_hostname: list[dict[str, Any]] | None = ...,
        domain: list[dict[str, Any]] | None = ...,
        ip6_primary: str | None = ...,
        ip6_secondary: str | None = ...,
        timeout: int | None = ...,
        retry: int | None = ...,
        dns_cache_limit: int | None = ...,
        dns_cache_ttl: int | None = ...,
        cache_notfound_responses: Literal[{"description": "Disable cache NOTFOUND responses from DNS server", "help": "Disable cache NOTFOUND responses from DNS server.", "label": "Disable", "name": "disable"}, {"description": "Enable cache NOTFOUND responses from DNS server", "help": "Enable cache NOTFOUND responses from DNS server.", "label": "Enable", "name": "enable"}] | None = ...,
        source_ip: str | None = ...,
        source_ip_interface: str | None = ...,
        root_servers: list[dict[str, Any]] | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        server_select_method: Literal[{"description": "Select servers based on least round trip time", "help": "Select servers based on least round trip time.", "label": "Least Rtt", "name": "least-rtt"}, {"description": "Select servers based on the order they are configured", "help": "Select servers based on the order they are configured.", "label": "Failover", "name": "failover"}] | None = ...,
        alt_primary: str | None = ...,
        alt_secondary: str | None = ...,
        log: Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Enable local DNS error log", "help": "Enable local DNS error log.", "label": "Error", "name": "error"}, {"description": "Enable local DNS log", "help": "Enable local DNS log.", "label": "All", "name": "all"}] | None = ...,
        fqdn_cache_ttl: int | None = ...,
        fqdn_max_refresh: int | None = ...,
        fqdn_min_refresh: int | None = ...,
        hostname_ttl: int | None = ...,
        hostname_limit: int | None = ...,
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
        payload_dict: DnsPayload | None = ...,
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
    "Dns",
    "DnsPayload",
]