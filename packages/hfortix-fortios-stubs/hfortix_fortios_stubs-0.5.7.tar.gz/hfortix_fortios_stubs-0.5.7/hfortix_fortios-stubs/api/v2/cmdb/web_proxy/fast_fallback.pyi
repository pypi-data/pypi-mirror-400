from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class FastFallbackPayload(TypedDict, total=False):
    """
    Type hints for web_proxy/fast_fallback payload fields.
    
    Proxy destination connection fast-fallback.
    
    **Usage:**
        payload: FastFallbackPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Configure a name for the fast-fallback entry.
    status: NotRequired[Literal[{"description": "Enable Status of the entry", "help": "Enable Status of the entry.", "label": "Enable", "name": "enable"}, {"description": "Disable Status of the entry", "help": "Disable Status of the entry.", "label": "Disable", "name": "disable"}]]  # Enable/disable the fast-fallback entry.
    connection_mode: NotRequired[Literal[{"description": "Connect the different destinations sequentially", "help": "Connect the different destinations sequentially.", "label": "Sequentially", "name": "sequentially"}, {"description": "Connect the different destinations simultaneously", "help": "Connect the different destinations simultaneously.", "label": "Simultaneously", "name": "simultaneously"}]]  # Connection mode for multiple destinations.
    protocol: NotRequired[Literal[{"description": "Connect IPv4 destinations first", "help": "Connect IPv4 destinations first.", "label": "Ipv4 First", "name": "IPv4-first"}, {"description": "Connect IPv6 destinations first", "help": "Connect IPv6 destinations first.", "label": "Ipv6 First", "name": "IPv6-first"}, {"description": "Connect IPv4 destinations only", "help": "Connect IPv4 destinations only.", "label": "Ipv4 Only", "name": "IPv4-only"}, {"description": "Connect IPv6 destinations only", "help": "Connect IPv6 destinations only.", "label": "Ipv6 Only", "name": "IPv6-only"}]]  # Connection protocols for multiple destinations.
    connection_timeout: NotRequired[int]  # Number of milliseconds to wait before starting another conne


class FastFallback:
    """
    Proxy destination connection fast-fallback.
    
    Path: web_proxy/fast_fallback
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
        payload_dict: FastFallbackPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Enable Status of the entry", "help": "Enable Status of the entry.", "label": "Enable", "name": "enable"}, {"description": "Disable Status of the entry", "help": "Disable Status of the entry.", "label": "Disable", "name": "disable"}] | None = ...,
        connection_mode: Literal[{"description": "Connect the different destinations sequentially", "help": "Connect the different destinations sequentially.", "label": "Sequentially", "name": "sequentially"}, {"description": "Connect the different destinations simultaneously", "help": "Connect the different destinations simultaneously.", "label": "Simultaneously", "name": "simultaneously"}] | None = ...,
        protocol: Literal[{"description": "Connect IPv4 destinations first", "help": "Connect IPv4 destinations first.", "label": "Ipv4 First", "name": "IPv4-first"}, {"description": "Connect IPv6 destinations first", "help": "Connect IPv6 destinations first.", "label": "Ipv6 First", "name": "IPv6-first"}, {"description": "Connect IPv4 destinations only", "help": "Connect IPv4 destinations only.", "label": "Ipv4 Only", "name": "IPv4-only"}, {"description": "Connect IPv6 destinations only", "help": "Connect IPv6 destinations only.", "label": "Ipv6 Only", "name": "IPv6-only"}] | None = ...,
        connection_timeout: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: FastFallbackPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Enable Status of the entry", "help": "Enable Status of the entry.", "label": "Enable", "name": "enable"}, {"description": "Disable Status of the entry", "help": "Disable Status of the entry.", "label": "Disable", "name": "disable"}] | None = ...,
        connection_mode: Literal[{"description": "Connect the different destinations sequentially", "help": "Connect the different destinations sequentially.", "label": "Sequentially", "name": "sequentially"}, {"description": "Connect the different destinations simultaneously", "help": "Connect the different destinations simultaneously.", "label": "Simultaneously", "name": "simultaneously"}] | None = ...,
        protocol: Literal[{"description": "Connect IPv4 destinations first", "help": "Connect IPv4 destinations first.", "label": "Ipv4 First", "name": "IPv4-first"}, {"description": "Connect IPv6 destinations first", "help": "Connect IPv6 destinations first.", "label": "Ipv6 First", "name": "IPv6-first"}, {"description": "Connect IPv4 destinations only", "help": "Connect IPv4 destinations only.", "label": "Ipv4 Only", "name": "IPv4-only"}, {"description": "Connect IPv6 destinations only", "help": "Connect IPv6 destinations only.", "label": "Ipv6 Only", "name": "IPv6-only"}] | None = ...,
        connection_timeout: int | None = ...,
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
        payload_dict: FastFallbackPayload | None = ...,
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
    "FastFallback",
    "FastFallbackPayload",
]