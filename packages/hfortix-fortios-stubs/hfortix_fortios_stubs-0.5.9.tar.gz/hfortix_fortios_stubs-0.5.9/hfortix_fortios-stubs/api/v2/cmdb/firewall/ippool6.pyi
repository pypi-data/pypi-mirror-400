from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class Ippool6Payload(TypedDict, total=False):
    """
    Type hints for firewall/ippool6 payload fields.
    
    Configure IPv6 IP pools.
    
    **Usage:**
        payload: Ippool6Payload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # IPv6 IP pool name.
    type: NotRequired[Literal[{"description": "IPv6 addresses in the IP pool can be shared by clients", "help": "IPv6 addresses in the IP pool can be shared by clients.", "label": "Overload", "name": "overload"}, {"description": "NPTv6 one to one mapping", "help": "NPTv6 one to one mapping.", "label": "Nptv6", "name": "nptv6"}]]  # Configure IPv6 pool type (overload or NPTv6).
    startip: str  # First IPv6 address (inclusive) in the range for the address 
    endip: str  # Final IPv6 address (inclusive) in the range for the address 
    internal_prefix: str  # Internal NPTv6 prefix length (32 - 64).
    external_prefix: str  # External NPTv6 prefix length (32 - 64).
    comments: NotRequired[str]  # Comment.
    nat46: NotRequired[Literal[{"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}, {"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}]]  # Enable/disable NAT46.
    add_nat46_route: NotRequired[Literal[{"description": "Disable adding NAT46 route", "help": "Disable adding NAT46 route.", "label": "Disable", "name": "disable"}, {"description": "Enable adding NAT46 route", "help": "Enable adding NAT46 route.", "label": "Enable", "name": "enable"}]]  # Enable/disable adding NAT46 route.


class Ippool6:
    """
    Configure IPv6 IP pools.
    
    Path: firewall/ippool6
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
        payload_dict: Ippool6Payload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "IPv6 addresses in the IP pool can be shared by clients", "help": "IPv6 addresses in the IP pool can be shared by clients.", "label": "Overload", "name": "overload"}, {"description": "NPTv6 one to one mapping", "help": "NPTv6 one to one mapping.", "label": "Nptv6", "name": "nptv6"}] | None = ...,
        startip: str | None = ...,
        endip: str | None = ...,
        internal_prefix: str | None = ...,
        external_prefix: str | None = ...,
        comments: str | None = ...,
        nat46: Literal[{"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}, {"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}] | None = ...,
        add_nat46_route: Literal[{"description": "Disable adding NAT46 route", "help": "Disable adding NAT46 route.", "label": "Disable", "name": "disable"}, {"description": "Enable adding NAT46 route", "help": "Enable adding NAT46 route.", "label": "Enable", "name": "enable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: Ippool6Payload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "IPv6 addresses in the IP pool can be shared by clients", "help": "IPv6 addresses in the IP pool can be shared by clients.", "label": "Overload", "name": "overload"}, {"description": "NPTv6 one to one mapping", "help": "NPTv6 one to one mapping.", "label": "Nptv6", "name": "nptv6"}] | None = ...,
        startip: str | None = ...,
        endip: str | None = ...,
        internal_prefix: str | None = ...,
        external_prefix: str | None = ...,
        comments: str | None = ...,
        nat46: Literal[{"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}, {"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}] | None = ...,
        add_nat46_route: Literal[{"description": "Disable adding NAT46 route", "help": "Disable adding NAT46 route.", "label": "Disable", "name": "disable"}, {"description": "Enable adding NAT46 route", "help": "Enable adding NAT46 route.", "label": "Enable", "name": "enable"}] | None = ...,
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
        payload_dict: Ippool6Payload | None = ...,
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
    "Ippool6",
    "Ippool6Payload",
]