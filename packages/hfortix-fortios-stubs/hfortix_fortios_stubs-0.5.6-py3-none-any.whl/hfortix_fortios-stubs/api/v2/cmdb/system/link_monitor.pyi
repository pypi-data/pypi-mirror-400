from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class LinkMonitorPayload(TypedDict, total=False):
    """
    Type hints for system/link_monitor payload fields.
    
    Configure Link Health Monitor.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.firewall.traffic-class.TrafficClassEndpoint` (via: class-id)
        - :class:`~.system.interface.InterfaceEndpoint` (via: srcintf)

    **Usage:**
        payload: LinkMonitorPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Link monitor name.
    addr_mode: NotRequired[Literal[{"description": "IPv4 mode", "help": "IPv4 mode.", "label": "Ipv4", "name": "ipv4"}, {"description": "IPv6 mode", "help": "IPv6 mode.", "label": "Ipv6", "name": "ipv6"}]]  # Address mode (IPv4 or IPv6).
    srcintf: NotRequired[str]  # Interface that receives the traffic to be monitored.
    server_config: NotRequired[Literal[{"description": "All servers share the same attributes", "help": "All servers share the same attributes.", "label": "Default", "name": "default"}, {"description": "Some attributes can be specified for individual servers", "help": "Some attributes can be specified for individual servers.", "label": "Individual", "name": "individual"}]]  # Mode of server configuration.
    server_type: NotRequired[Literal[{"description": "Static servers", "help": "Static servers.", "label": "Static", "name": "static"}, {"description": "Dynamic servers", "help": "Dynamic servers.", "label": "Dynamic", "name": "dynamic"}]]  # Server type (static or dynamic).
    server: list[dict[str, Any]]  # IP address of the server(s) to be monitored.
    protocol: NotRequired[Literal[{"description": "PING link monitor", "help": "PING link monitor.", "label": "Ping", "name": "ping"}, {"description": "TCP echo link monitor", "help": "TCP echo link monitor.", "label": "Tcp Echo", "name": "tcp-echo"}, {"description": "UDP echo link monitor", "help": "UDP echo link monitor.", "label": "Udp Echo", "name": "udp-echo"}, {"description": "HTTP-GET link monitor", "help": "HTTP-GET link monitor.", "label": "Http", "name": "http"}, {"description": "HTTPS-GET link monitor", "help": "HTTPS-GET link monitor.", "label": "Https", "name": "https"}, {"description": "TWAMP link monitor", "help": "TWAMP link monitor.", "label": "Twamp", "name": "twamp"}]]  # Protocols used to monitor the server.
    port: NotRequired[int]  # Port number of the traffic to be used to monitor the server.
    gateway_ip: NotRequired[str]  # Gateway IP address used to probe the server.
    gateway_ip6: NotRequired[str]  # Gateway IPv6 address used to probe the server.
    route: NotRequired[list[dict[str, Any]]]  # Subnet to monitor.
    source_ip: NotRequired[str]  # Source IP address used in packet to the server.
    source_ip6: NotRequired[str]  # Source IPv6 address used in packet to the server.
    http_get: str  # If you are monitoring an HTML server you can send an HTTP-GE
    http_agent: NotRequired[str]  # String in the http-agent field in the HTTP header.
    http_match: NotRequired[str]  # String that you expect to see in the HTTP-GET requests of th
    interval: NotRequired[int]  # Detection interval in milliseconds (20 - 3600 * 1000 msec, d
    probe_timeout: NotRequired[int]  # Time to wait before a probe packet is considered lost (20 - 
    failtime: NotRequired[int]  # Number of retry attempts before the server is considered dow
    recoverytime: NotRequired[int]  # Number of successful responses received before server is con
    probe_count: NotRequired[int]  # Number of most recent probes that should be used to calculat
    security_mode: NotRequired[Literal[{"description": "Unauthenticated mode", "help": "Unauthenticated mode.", "label": "None", "name": "none"}, {"description": "Authenticated mode", "help": "Authenticated mode.", "label": "Authentication", "name": "authentication"}]]  # Twamp controller security mode.
    password: NotRequired[str]  # TWAMP controller password in authentication mode.
    packet_size: NotRequired[int]  # Packet size of a TWAMP test session (124/158 - 1024).
    ha_priority: NotRequired[int]  # HA election priority (1 - 50).
    fail_weight: NotRequired[int]  # Threshold weight to trigger link failure alert.
    update_cascade_interface: NotRequired[Literal[{"description": "Enable update cascade interface", "help": "Enable update cascade interface.", "label": "Enable", "name": "enable"}, {"description": "Disable update cascade interface", "help": "Disable update cascade interface.", "label": "Disable", "name": "disable"}]]  # Enable/disable update cascade interface.
    update_static_route: NotRequired[Literal[{"description": "Enable updating the static route", "help": "Enable updating the static route.", "label": "Enable", "name": "enable"}, {"description": "Disable updating the static route", "help": "Disable updating the static route.", "label": "Disable", "name": "disable"}]]  # Enable/disable updating the static route.
    update_policy_route: NotRequired[Literal[{"description": "Enable updating the policy route", "help": "Enable updating the policy route.", "label": "Enable", "name": "enable"}, {"description": "Disable updating the policy route", "help": "Disable updating the policy route.", "label": "Disable", "name": "disable"}]]  # Enable/disable updating the policy route.
    status: NotRequired[Literal[{"description": "Enable this link monitor", "help": "Enable this link monitor.", "label": "Enable", "name": "enable"}, {"description": "Disable this link monitor", "help": "Disable this link monitor.", "label": "Disable", "name": "disable"}]]  # Enable/disable this link monitor.
    diffservcode: NotRequired[str]  # Differentiated services code point (DSCP) in the IP header o
    class_id: NotRequired[int]  # Traffic class ID.
    service_detection: NotRequired[Literal[{"description": "Only use monitor for service-detection", "help": "Only use monitor for service-detection.", "label": "Enable", "name": "enable"}, {"description": "Monitor will update routes/interfaces on link failure", "help": "Monitor will update routes/interfaces on link failure.", "label": "Disable", "name": "disable"}]]  # Only use monitor to read quality values. If enabled, static 
    server_list: NotRequired[list[dict[str, Any]]]  # Servers for link-monitor to monitor.


class LinkMonitor:
    """
    Configure Link Health Monitor.
    
    Path: system/link_monitor
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
        payload_dict: LinkMonitorPayload | None = ...,
        name: str | None = ...,
        addr_mode: Literal[{"description": "IPv4 mode", "help": "IPv4 mode.", "label": "Ipv4", "name": "ipv4"}, {"description": "IPv6 mode", "help": "IPv6 mode.", "label": "Ipv6", "name": "ipv6"}] | None = ...,
        srcintf: str | None = ...,
        server_config: Literal[{"description": "All servers share the same attributes", "help": "All servers share the same attributes.", "label": "Default", "name": "default"}, {"description": "Some attributes can be specified for individual servers", "help": "Some attributes can be specified for individual servers.", "label": "Individual", "name": "individual"}] | None = ...,
        server_type: Literal[{"description": "Static servers", "help": "Static servers.", "label": "Static", "name": "static"}, {"description": "Dynamic servers", "help": "Dynamic servers.", "label": "Dynamic", "name": "dynamic"}] | None = ...,
        server: list[dict[str, Any]] | None = ...,
        protocol: Literal[{"description": "PING link monitor", "help": "PING link monitor.", "label": "Ping", "name": "ping"}, {"description": "TCP echo link monitor", "help": "TCP echo link monitor.", "label": "Tcp Echo", "name": "tcp-echo"}, {"description": "UDP echo link monitor", "help": "UDP echo link monitor.", "label": "Udp Echo", "name": "udp-echo"}, {"description": "HTTP-GET link monitor", "help": "HTTP-GET link monitor.", "label": "Http", "name": "http"}, {"description": "HTTPS-GET link monitor", "help": "HTTPS-GET link monitor.", "label": "Https", "name": "https"}, {"description": "TWAMP link monitor", "help": "TWAMP link monitor.", "label": "Twamp", "name": "twamp"}] | None = ...,
        port: int | None = ...,
        gateway_ip: str | None = ...,
        gateway_ip6: str | None = ...,
        route: list[dict[str, Any]] | None = ...,
        source_ip: str | None = ...,
        source_ip6: str | None = ...,
        http_get: str | None = ...,
        http_agent: str | None = ...,
        http_match: str | None = ...,
        interval: int | None = ...,
        probe_timeout: int | None = ...,
        failtime: int | None = ...,
        recoverytime: int | None = ...,
        probe_count: int | None = ...,
        security_mode: Literal[{"description": "Unauthenticated mode", "help": "Unauthenticated mode.", "label": "None", "name": "none"}, {"description": "Authenticated mode", "help": "Authenticated mode.", "label": "Authentication", "name": "authentication"}] | None = ...,
        password: str | None = ...,
        packet_size: int | None = ...,
        ha_priority: int | None = ...,
        fail_weight: int | None = ...,
        update_cascade_interface: Literal[{"description": "Enable update cascade interface", "help": "Enable update cascade interface.", "label": "Enable", "name": "enable"}, {"description": "Disable update cascade interface", "help": "Disable update cascade interface.", "label": "Disable", "name": "disable"}] | None = ...,
        update_static_route: Literal[{"description": "Enable updating the static route", "help": "Enable updating the static route.", "label": "Enable", "name": "enable"}, {"description": "Disable updating the static route", "help": "Disable updating the static route.", "label": "Disable", "name": "disable"}] | None = ...,
        update_policy_route: Literal[{"description": "Enable updating the policy route", "help": "Enable updating the policy route.", "label": "Enable", "name": "enable"}, {"description": "Disable updating the policy route", "help": "Disable updating the policy route.", "label": "Disable", "name": "disable"}] | None = ...,
        status: Literal[{"description": "Enable this link monitor", "help": "Enable this link monitor.", "label": "Enable", "name": "enable"}, {"description": "Disable this link monitor", "help": "Disable this link monitor.", "label": "Disable", "name": "disable"}] | None = ...,
        diffservcode: str | None = ...,
        class_id: int | None = ...,
        service_detection: Literal[{"description": "Only use monitor for service-detection", "help": "Only use monitor for service-detection.", "label": "Enable", "name": "enable"}, {"description": "Monitor will update routes/interfaces on link failure", "help": "Monitor will update routes/interfaces on link failure.", "label": "Disable", "name": "disable"}] | None = ...,
        server_list: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: LinkMonitorPayload | None = ...,
        name: str | None = ...,
        addr_mode: Literal[{"description": "IPv4 mode", "help": "IPv4 mode.", "label": "Ipv4", "name": "ipv4"}, {"description": "IPv6 mode", "help": "IPv6 mode.", "label": "Ipv6", "name": "ipv6"}] | None = ...,
        srcintf: str | None = ...,
        server_config: Literal[{"description": "All servers share the same attributes", "help": "All servers share the same attributes.", "label": "Default", "name": "default"}, {"description": "Some attributes can be specified for individual servers", "help": "Some attributes can be specified for individual servers.", "label": "Individual", "name": "individual"}] | None = ...,
        server_type: Literal[{"description": "Static servers", "help": "Static servers.", "label": "Static", "name": "static"}, {"description": "Dynamic servers", "help": "Dynamic servers.", "label": "Dynamic", "name": "dynamic"}] | None = ...,
        server: list[dict[str, Any]] | None = ...,
        protocol: Literal[{"description": "PING link monitor", "help": "PING link monitor.", "label": "Ping", "name": "ping"}, {"description": "TCP echo link monitor", "help": "TCP echo link monitor.", "label": "Tcp Echo", "name": "tcp-echo"}, {"description": "UDP echo link monitor", "help": "UDP echo link monitor.", "label": "Udp Echo", "name": "udp-echo"}, {"description": "HTTP-GET link monitor", "help": "HTTP-GET link monitor.", "label": "Http", "name": "http"}, {"description": "HTTPS-GET link monitor", "help": "HTTPS-GET link monitor.", "label": "Https", "name": "https"}, {"description": "TWAMP link monitor", "help": "TWAMP link monitor.", "label": "Twamp", "name": "twamp"}] | None = ...,
        port: int | None = ...,
        gateway_ip: str | None = ...,
        gateway_ip6: str | None = ...,
        route: list[dict[str, Any]] | None = ...,
        source_ip: str | None = ...,
        source_ip6: str | None = ...,
        http_get: str | None = ...,
        http_agent: str | None = ...,
        http_match: str | None = ...,
        interval: int | None = ...,
        probe_timeout: int | None = ...,
        failtime: int | None = ...,
        recoverytime: int | None = ...,
        probe_count: int | None = ...,
        security_mode: Literal[{"description": "Unauthenticated mode", "help": "Unauthenticated mode.", "label": "None", "name": "none"}, {"description": "Authenticated mode", "help": "Authenticated mode.", "label": "Authentication", "name": "authentication"}] | None = ...,
        password: str | None = ...,
        packet_size: int | None = ...,
        ha_priority: int | None = ...,
        fail_weight: int | None = ...,
        update_cascade_interface: Literal[{"description": "Enable update cascade interface", "help": "Enable update cascade interface.", "label": "Enable", "name": "enable"}, {"description": "Disable update cascade interface", "help": "Disable update cascade interface.", "label": "Disable", "name": "disable"}] | None = ...,
        update_static_route: Literal[{"description": "Enable updating the static route", "help": "Enable updating the static route.", "label": "Enable", "name": "enable"}, {"description": "Disable updating the static route", "help": "Disable updating the static route.", "label": "Disable", "name": "disable"}] | None = ...,
        update_policy_route: Literal[{"description": "Enable updating the policy route", "help": "Enable updating the policy route.", "label": "Enable", "name": "enable"}, {"description": "Disable updating the policy route", "help": "Disable updating the policy route.", "label": "Disable", "name": "disable"}] | None = ...,
        status: Literal[{"description": "Enable this link monitor", "help": "Enable this link monitor.", "label": "Enable", "name": "enable"}, {"description": "Disable this link monitor", "help": "Disable this link monitor.", "label": "Disable", "name": "disable"}] | None = ...,
        diffservcode: str | None = ...,
        class_id: int | None = ...,
        service_detection: Literal[{"description": "Only use monitor for service-detection", "help": "Only use monitor for service-detection.", "label": "Enable", "name": "enable"}, {"description": "Monitor will update routes/interfaces on link failure", "help": "Monitor will update routes/interfaces on link failure.", "label": "Disable", "name": "disable"}] | None = ...,
        server_list: list[dict[str, Any]] | None = ...,
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
        payload_dict: LinkMonitorPayload | None = ...,
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
    "LinkMonitor",
    "LinkMonitorPayload",
]