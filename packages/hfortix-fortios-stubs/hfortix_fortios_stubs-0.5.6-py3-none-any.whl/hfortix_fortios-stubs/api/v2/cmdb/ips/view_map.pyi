from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ViewMapPayload(TypedDict, total=False):
    """
    Type hints for ips/view_map payload fields.
    
    Configure IPS view-map.
    
    **Usage:**
        payload: ViewMapPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    id: NotRequired[int]  # View ID.
    vdom_id: NotRequired[int]  # VDOM ID.
    policy_id: NotRequired[int]  # Policy ID.
    id_policy_id: NotRequired[int]  # ID-based policy ID.
    which: NotRequired[Literal[{"description": "Firewall policy", "help": "Firewall policy.", "label": "Firewall", "name": "firewall"}, {"description": "Interface policy", "help": "Interface policy.", "label": "Interface", "name": "interface"}, {"description": "Interface policy6", "help": "Interface policy6.", "label": "Interface6", "name": "interface6"}, {"description": "Sniffer policy", "help": "Sniffer policy.", "label": "Sniffer", "name": "sniffer"}, {"description": "Sniffer policy6", "help": "Sniffer policy6.", "label": "Sniffer6", "name": "sniffer6"}, {"description": "explicit proxy policy", "help": "explicit proxy policy.", "label": "Explicit", "name": "explicit"}]]  # Policy.


class ViewMap:
    """
    Configure IPS view-map.
    
    Path: ips/view_map
    Category: cmdb
    Primary Key: id
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        id: int | None = ...,
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
        id: int,
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
        id: int | None = ...,
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
        id: int | None = ...,
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
        id: int | None = ...,
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
        payload_dict: ViewMapPayload | None = ...,
        id: int | None = ...,
        vdom_id: int | None = ...,
        policy_id: int | None = ...,
        id_policy_id: int | None = ...,
        which: Literal[{"description": "Firewall policy", "help": "Firewall policy.", "label": "Firewall", "name": "firewall"}, {"description": "Interface policy", "help": "Interface policy.", "label": "Interface", "name": "interface"}, {"description": "Interface policy6", "help": "Interface policy6.", "label": "Interface6", "name": "interface6"}, {"description": "Sniffer policy", "help": "Sniffer policy.", "label": "Sniffer", "name": "sniffer"}, {"description": "Sniffer policy6", "help": "Sniffer policy6.", "label": "Sniffer6", "name": "sniffer6"}, {"description": "explicit proxy policy", "help": "explicit proxy policy.", "label": "Explicit", "name": "explicit"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ViewMapPayload | None = ...,
        id: int | None = ...,
        vdom_id: int | None = ...,
        policy_id: int | None = ...,
        id_policy_id: int | None = ...,
        which: Literal[{"description": "Firewall policy", "help": "Firewall policy.", "label": "Firewall", "name": "firewall"}, {"description": "Interface policy", "help": "Interface policy.", "label": "Interface", "name": "interface"}, {"description": "Interface policy6", "help": "Interface policy6.", "label": "Interface6", "name": "interface6"}, {"description": "Sniffer policy", "help": "Sniffer policy.", "label": "Sniffer", "name": "sniffer"}, {"description": "Sniffer policy6", "help": "Sniffer policy6.", "label": "Sniffer6", "name": "sniffer6"}, {"description": "explicit proxy policy", "help": "explicit proxy policy.", "label": "Explicit", "name": "explicit"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        id: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        id: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: ViewMapPayload | None = ...,
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
    "ViewMap",
    "ViewMapPayload",
]