from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class HealthCheckFortiguardPayload(TypedDict, total=False):
    """
    Type hints for system/health_check_fortiguard payload fields.
    
    SD-WAN status checking or health checking. Identify a server predefine by FortiGuard and determine how SD-WAN verifies that FGT can communicate with it.
    
    **Usage:**
        payload: HealthCheckFortiguardPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Status check or predefined health-check targets name.
    server: str  # Status check or predefined health-check domain name.
    obsolete: NotRequired[int]  # Indicates whether Health Check service can be used.
    protocol: Literal[{"description": "Use PING to test the link with the server", "help": "Use PING to test the link with the server.", "label": "Ping", "name": "ping"}, {"description": "Use TCP echo to test the link with the server", "help": "Use TCP echo to test the link with the server.", "label": "Tcp Echo", "name": "tcp-echo"}, {"description": "Use UDP echo to test the link with the server", "help": "Use UDP echo to test the link with the server.", "label": "Udp Echo", "name": "udp-echo"}, {"description": "Use HTTP-GET to test the link with the server", "help": "Use HTTP-GET to test the link with the server.", "label": "Http", "name": "http"}, {"description": "Use HTTPS-GET to test the link with the server", "help": "Use HTTPS-GET to test the link with the server.", "label": "Https", "name": "https"}, {"description": "Use TWAMP to test the link with the server", "help": "Use TWAMP to test the link with the server.", "label": "Twamp", "name": "twamp"}, {"description": "Use DNS query to test the link with the server", "help": "Use DNS query to test the link with the server.", "label": "Dns", "name": "dns"}, {"description": "Use a full TCP connection to test the link with the server", "help": "Use a full TCP connection to test the link with the server.", "label": "Tcp Connect", "name": "tcp-connect"}, {"description": "Use FTP to test the link with the server", "help": "Use FTP to test the link with the server.", "label": "Ftp", "name": "ftp"}]  # Protocol name.


class HealthCheckFortiguard:
    """
    SD-WAN status checking or health checking. Identify a server predefine by FortiGuard and determine how SD-WAN verifies that FGT can communicate with it.
    
    Path: system/health_check_fortiguard
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
        payload_dict: HealthCheckFortiguardPayload | None = ...,
        name: str | None = ...,
        server: str | None = ...,
        obsolete: int | None = ...,
        protocol: Literal[{"description": "Use PING to test the link with the server", "help": "Use PING to test the link with the server.", "label": "Ping", "name": "ping"}, {"description": "Use TCP echo to test the link with the server", "help": "Use TCP echo to test the link with the server.", "label": "Tcp Echo", "name": "tcp-echo"}, {"description": "Use UDP echo to test the link with the server", "help": "Use UDP echo to test the link with the server.", "label": "Udp Echo", "name": "udp-echo"}, {"description": "Use HTTP-GET to test the link with the server", "help": "Use HTTP-GET to test the link with the server.", "label": "Http", "name": "http"}, {"description": "Use HTTPS-GET to test the link with the server", "help": "Use HTTPS-GET to test the link with the server.", "label": "Https", "name": "https"}, {"description": "Use TWAMP to test the link with the server", "help": "Use TWAMP to test the link with the server.", "label": "Twamp", "name": "twamp"}, {"description": "Use DNS query to test the link with the server", "help": "Use DNS query to test the link with the server.", "label": "Dns", "name": "dns"}, {"description": "Use a full TCP connection to test the link with the server", "help": "Use a full TCP connection to test the link with the server.", "label": "Tcp Connect", "name": "tcp-connect"}, {"description": "Use FTP to test the link with the server", "help": "Use FTP to test the link with the server.", "label": "Ftp", "name": "ftp"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: HealthCheckFortiguardPayload | None = ...,
        name: str | None = ...,
        server: str | None = ...,
        obsolete: int | None = ...,
        protocol: Literal[{"description": "Use PING to test the link with the server", "help": "Use PING to test the link with the server.", "label": "Ping", "name": "ping"}, {"description": "Use TCP echo to test the link with the server", "help": "Use TCP echo to test the link with the server.", "label": "Tcp Echo", "name": "tcp-echo"}, {"description": "Use UDP echo to test the link with the server", "help": "Use UDP echo to test the link with the server.", "label": "Udp Echo", "name": "udp-echo"}, {"description": "Use HTTP-GET to test the link with the server", "help": "Use HTTP-GET to test the link with the server.", "label": "Http", "name": "http"}, {"description": "Use HTTPS-GET to test the link with the server", "help": "Use HTTPS-GET to test the link with the server.", "label": "Https", "name": "https"}, {"description": "Use TWAMP to test the link with the server", "help": "Use TWAMP to test the link with the server.", "label": "Twamp", "name": "twamp"}, {"description": "Use DNS query to test the link with the server", "help": "Use DNS query to test the link with the server.", "label": "Dns", "name": "dns"}, {"description": "Use a full TCP connection to test the link with the server", "help": "Use a full TCP connection to test the link with the server.", "label": "Tcp Connect", "name": "tcp-connect"}, {"description": "Use FTP to test the link with the server", "help": "Use FTP to test the link with the server.", "label": "Ftp", "name": "ftp"}] | None = ...,
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
        payload_dict: HealthCheckFortiguardPayload | None = ...,
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
    "HealthCheckFortiguard",
    "HealthCheckFortiguardPayload",
]