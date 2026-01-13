from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class IpsecAggregatePayload(TypedDict, total=False):
    """
    Type hints for system/ipsec_aggregate payload fields.
    
    Configure an aggregate of IPsec tunnels.
    
    **Usage:**
        payload: IpsecAggregatePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # IPsec aggregate name.
    member: list[dict[str, Any]]  # Member tunnels of the aggregate.
    algorithm: NotRequired[Literal[{"description": "Use layer 3 address for distribution", "help": "Use layer 3 address for distribution.", "label": "L3", "name": "L3"}, {"description": "Use layer 4 information for distribution", "help": "Use layer 4 information for distribution.", "label": "L4", "name": "L4"}, {"description": "Per-packet round-robin distribution", "help": "Per-packet round-robin distribution.", "label": "Round Robin", "name": "round-robin"}, {"description": "Use first tunnel that is up for all traffic", "help": "Use first tunnel that is up for all traffic.", "label": "Redundant", "name": "redundant"}, {"description": "Weighted round-robin distribution", "help": "Weighted round-robin distribution.", "label": "Weighted Round Robin", "name": "weighted-round-robin"}]]  # Frame distribution algorithm.


class IpsecAggregate:
    """
    Configure an aggregate of IPsec tunnels.
    
    Path: system/ipsec_aggregate
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
        payload_dict: IpsecAggregatePayload | None = ...,
        name: str | None = ...,
        member: list[dict[str, Any]] | None = ...,
        algorithm: Literal[{"description": "Use layer 3 address for distribution", "help": "Use layer 3 address for distribution.", "label": "L3", "name": "L3"}, {"description": "Use layer 4 information for distribution", "help": "Use layer 4 information for distribution.", "label": "L4", "name": "L4"}, {"description": "Per-packet round-robin distribution", "help": "Per-packet round-robin distribution.", "label": "Round Robin", "name": "round-robin"}, {"description": "Use first tunnel that is up for all traffic", "help": "Use first tunnel that is up for all traffic.", "label": "Redundant", "name": "redundant"}, {"description": "Weighted round-robin distribution", "help": "Weighted round-robin distribution.", "label": "Weighted Round Robin", "name": "weighted-round-robin"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: IpsecAggregatePayload | None = ...,
        name: str | None = ...,
        member: list[dict[str, Any]] | None = ...,
        algorithm: Literal[{"description": "Use layer 3 address for distribution", "help": "Use layer 3 address for distribution.", "label": "L3", "name": "L3"}, {"description": "Use layer 4 information for distribution", "help": "Use layer 4 information for distribution.", "label": "L4", "name": "L4"}, {"description": "Per-packet round-robin distribution", "help": "Per-packet round-robin distribution.", "label": "Round Robin", "name": "round-robin"}, {"description": "Use first tunnel that is up for all traffic", "help": "Use first tunnel that is up for all traffic.", "label": "Redundant", "name": "redundant"}, {"description": "Weighted round-robin distribution", "help": "Weighted round-robin distribution.", "label": "Weighted Round Robin", "name": "weighted-round-robin"}] | None = ...,
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
        payload_dict: IpsecAggregatePayload | None = ...,
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
    "IpsecAggregate",
    "IpsecAggregatePayload",
]