from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class LdbMonitorPayload(TypedDict, total=False):
    """
    Type hints for firewall/ldb_monitor payload fields.
    
    Configure server load balancing health monitors.
    
    **Usage:**
        payload: LdbMonitorPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Monitor name.
    type: Literal[{"description": "PING health monitor", "help": "PING health monitor.", "label": "Ping", "name": "ping"}, {"description": "TCP-connect health monitor", "help": "TCP-connect health monitor.", "label": "Tcp", "name": "tcp"}, {"description": "HTTP-GET health monitor", "help": "HTTP-GET health monitor.", "label": "Http", "name": "http"}, {"description": "HTTP-GET health monitor with SSL", "help": "HTTP-GET health monitor with SSL.", "label": "Https", "name": "https"}, {"description": "DNS health monitor", "help": "DNS health monitor.", "label": "Dns", "name": "dns"}]  # Select the Monitor type used by the health check monitor to 
    interval: NotRequired[int]  # Time between health checks (5 - 65535 sec, default = 10).
    timeout: NotRequired[int]  # Time to wait to receive response to a health check from a se
    retry: NotRequired[int]  # Number health check attempts before the server is considered
    port: NotRequired[int]  # Service port used to perform the health check. If 0, health 
    src_ip: NotRequired[str]  # Source IP for ldb-monitor.
    http_get: NotRequired[str]  # Request URI used to send a GET request to check the health o
    http_match: NotRequired[str]  # String to match the value expected in response to an HTTP-GE
    http_max_redirects: NotRequired[int]  # The maximum number of HTTP redirects to be allowed (0 - 5, d
    dns_protocol: NotRequired[Literal[{"description": "UDP", "help": "UDP.", "label": "Udp", "name": "udp"}, {"description": "TCP", "help": "TCP.", "label": "Tcp", "name": "tcp"}]]  # Select the protocol used by the DNS health check monitor to 
    dns_request_domain: NotRequired[str]  # Fully qualified domain name to resolve for the DNS probe.
    dns_match_ip: NotRequired[str]  # Response IP expected from DNS server.


class LdbMonitor:
    """
    Configure server load balancing health monitors.
    
    Path: firewall/ldb_monitor
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
        payload_dict: LdbMonitorPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "PING health monitor", "help": "PING health monitor.", "label": "Ping", "name": "ping"}, {"description": "TCP-connect health monitor", "help": "TCP-connect health monitor.", "label": "Tcp", "name": "tcp"}, {"description": "HTTP-GET health monitor", "help": "HTTP-GET health monitor.", "label": "Http", "name": "http"}, {"description": "HTTP-GET health monitor with SSL", "help": "HTTP-GET health monitor with SSL.", "label": "Https", "name": "https"}, {"description": "DNS health monitor", "help": "DNS health monitor.", "label": "Dns", "name": "dns"}] | None = ...,
        interval: int | None = ...,
        timeout: int | None = ...,
        retry: int | None = ...,
        port: int | None = ...,
        src_ip: str | None = ...,
        http_get: str | None = ...,
        http_match: str | None = ...,
        http_max_redirects: int | None = ...,
        dns_protocol: Literal[{"description": "UDP", "help": "UDP.", "label": "Udp", "name": "udp"}, {"description": "TCP", "help": "TCP.", "label": "Tcp", "name": "tcp"}] | None = ...,
        dns_request_domain: str | None = ...,
        dns_match_ip: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: LdbMonitorPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "PING health monitor", "help": "PING health monitor.", "label": "Ping", "name": "ping"}, {"description": "TCP-connect health monitor", "help": "TCP-connect health monitor.", "label": "Tcp", "name": "tcp"}, {"description": "HTTP-GET health monitor", "help": "HTTP-GET health monitor.", "label": "Http", "name": "http"}, {"description": "HTTP-GET health monitor with SSL", "help": "HTTP-GET health monitor with SSL.", "label": "Https", "name": "https"}, {"description": "DNS health monitor", "help": "DNS health monitor.", "label": "Dns", "name": "dns"}] | None = ...,
        interval: int | None = ...,
        timeout: int | None = ...,
        retry: int | None = ...,
        port: int | None = ...,
        src_ip: str | None = ...,
        http_get: str | None = ...,
        http_match: str | None = ...,
        http_max_redirects: int | None = ...,
        dns_protocol: Literal[{"description": "UDP", "help": "UDP.", "label": "Udp", "name": "udp"}, {"description": "TCP", "help": "TCP.", "label": "Tcp", "name": "tcp"}] | None = ...,
        dns_request_domain: str | None = ...,
        dns_match_ip: str | None = ...,
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
        payload_dict: LdbMonitorPayload | None = ...,
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
    "LdbMonitor",
    "LdbMonitorPayload",
]