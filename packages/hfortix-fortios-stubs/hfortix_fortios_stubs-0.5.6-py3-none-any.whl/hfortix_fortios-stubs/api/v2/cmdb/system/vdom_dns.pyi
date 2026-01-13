from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class VdomDnsPayload(TypedDict, total=False):
    """
    Type hints for system/vdom_dns payload fields.
    
    Configure DNS servers for a non-management VDOM.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.local.LocalEndpoint` (via: ssl-certificate)
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface, source-ip-interface)

    **Usage:**
        payload: VdomDnsPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    vdom_dns: NotRequired[Literal[{"description": "Enable configuring DNS servers for the current VDOM", "help": "Enable configuring DNS servers for the current VDOM.", "label": "Enable", "name": "enable"}, {"description": "Disable configuring DNS servers for the current VDOM", "help": "Disable configuring DNS servers for the current VDOM.", "label": "Disable", "name": "disable"}]]  # Enable/disable configuring DNS servers for the current VDOM.
    primary: str  # Primary DNS server IP address for the VDOM.
    secondary: NotRequired[str]  # Secondary DNS server IP address for the VDOM.
    protocol: NotRequired[Literal[{"description": "DNS over UDP/53, DNS over TCP/53", "help": "DNS over UDP/53, DNS over TCP/53.", "label": "Cleartext", "name": "cleartext"}, {"description": "DNS over TLS/853", "help": "DNS over TLS/853.", "label": "Dot", "name": "dot"}, {"description": "DNS over HTTPS/443", "help": "DNS over HTTPS/443.", "label": "Doh", "name": "doh"}]]  # DNS transport protocols.
    ssl_certificate: NotRequired[str]  # Name of local certificate for SSL connections.
    server_hostname: NotRequired[list[dict[str, Any]]]  # DNS server host name list.
    ip6_primary: NotRequired[str]  # Primary IPv6 DNS server IP address for the VDOM.
    ip6_secondary: NotRequired[str]  # Secondary IPv6 DNS server IP address for the VDOM.
    source_ip: NotRequired[str]  # Source IP for communications with the DNS server.
    source_ip_interface: NotRequired[str]  # IP address of the specified interface as the source IP addre
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.
    server_select_method: NotRequired[Literal[{"description": "Select servers based on least round trip time", "help": "Select servers based on least round trip time.", "label": "Least Rtt", "name": "least-rtt"}, {"description": "Select servers based on the order they are configured", "help": "Select servers based on the order they are configured.", "label": "Failover", "name": "failover"}]]  # Specify how configured servers are prioritized.
    alt_primary: NotRequired[str]  # Alternate primary DNS server. This is not used as a failover
    alt_secondary: NotRequired[str]  # Alternate secondary DNS server. This is not used as a failov


class VdomDns:
    """
    Configure DNS servers for a non-management VDOM.
    
    Path: system/vdom_dns
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
        payload_dict: VdomDnsPayload | None = ...,
        vdom_dns: Literal[{"description": "Enable configuring DNS servers for the current VDOM", "help": "Enable configuring DNS servers for the current VDOM.", "label": "Enable", "name": "enable"}, {"description": "Disable configuring DNS servers for the current VDOM", "help": "Disable configuring DNS servers for the current VDOM.", "label": "Disable", "name": "disable"}] | None = ...,
        primary: str | None = ...,
        secondary: str | None = ...,
        protocol: Literal[{"description": "DNS over UDP/53, DNS over TCP/53", "help": "DNS over UDP/53, DNS over TCP/53.", "label": "Cleartext", "name": "cleartext"}, {"description": "DNS over TLS/853", "help": "DNS over TLS/853.", "label": "Dot", "name": "dot"}, {"description": "DNS over HTTPS/443", "help": "DNS over HTTPS/443.", "label": "Doh", "name": "doh"}] | None = ...,
        ssl_certificate: str | None = ...,
        server_hostname: list[dict[str, Any]] | None = ...,
        ip6_primary: str | None = ...,
        ip6_secondary: str | None = ...,
        source_ip: str | None = ...,
        source_ip_interface: str | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        server_select_method: Literal[{"description": "Select servers based on least round trip time", "help": "Select servers based on least round trip time.", "label": "Least Rtt", "name": "least-rtt"}, {"description": "Select servers based on the order they are configured", "help": "Select servers based on the order they are configured.", "label": "Failover", "name": "failover"}] | None = ...,
        alt_primary: str | None = ...,
        alt_secondary: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: VdomDnsPayload | None = ...,
        vdom_dns: Literal[{"description": "Enable configuring DNS servers for the current VDOM", "help": "Enable configuring DNS servers for the current VDOM.", "label": "Enable", "name": "enable"}, {"description": "Disable configuring DNS servers for the current VDOM", "help": "Disable configuring DNS servers for the current VDOM.", "label": "Disable", "name": "disable"}] | None = ...,
        primary: str | None = ...,
        secondary: str | None = ...,
        protocol: Literal[{"description": "DNS over UDP/53, DNS over TCP/53", "help": "DNS over UDP/53, DNS over TCP/53.", "label": "Cleartext", "name": "cleartext"}, {"description": "DNS over TLS/853", "help": "DNS over TLS/853.", "label": "Dot", "name": "dot"}, {"description": "DNS over HTTPS/443", "help": "DNS over HTTPS/443.", "label": "Doh", "name": "doh"}] | None = ...,
        ssl_certificate: str | None = ...,
        server_hostname: list[dict[str, Any]] | None = ...,
        ip6_primary: str | None = ...,
        ip6_secondary: str | None = ...,
        source_ip: str | None = ...,
        source_ip_interface: str | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        server_select_method: Literal[{"description": "Select servers based on least round trip time", "help": "Select servers based on least round trip time.", "label": "Least Rtt", "name": "least-rtt"}, {"description": "Select servers based on the order they are configured", "help": "Select servers based on the order they are configured.", "label": "Failover", "name": "failover"}] | None = ...,
        alt_primary: str | None = ...,
        alt_secondary: str | None = ...,
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
        payload_dict: VdomDnsPayload | None = ...,
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
    "VdomDns",
    "VdomDnsPayload",
]