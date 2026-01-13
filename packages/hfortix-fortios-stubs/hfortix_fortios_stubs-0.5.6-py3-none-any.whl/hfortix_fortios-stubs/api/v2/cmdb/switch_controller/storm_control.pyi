from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class StormControlPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/storm_control payload fields.
    
    Configure FortiSwitch storm control.
    
    **Usage:**
        payload: StormControlPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    rate: NotRequired[int]  # Rate in packets per second at which storm control drops exce
    burst_size_level: NotRequired[int]  # Increase level to handle bursty traffic (0 - 4, default = 0)
    unknown_unicast: NotRequired[Literal[{"description": "Enable unknown unicast storm control", "help": "Enable unknown unicast storm control.", "label": "Enable", "name": "enable"}, {"description": "Disable unknown unicast storm control", "help": "Disable unknown unicast storm control.", "label": "Disable", "name": "disable"}]]  # Enable/disable storm control to drop unknown unicast traffic
    unknown_multicast: NotRequired[Literal[{"description": "Enable unknown multicast storm control", "help": "Enable unknown multicast storm control.", "label": "Enable", "name": "enable"}, {"description": "Disable unknown multicast storm control", "help": "Disable unknown multicast storm control.", "label": "Disable", "name": "disable"}]]  # Enable/disable storm control to drop unknown multicast traff
    broadcast: NotRequired[Literal[{"description": "Enable broadcast storm control", "help": "Enable broadcast storm control.", "label": "Enable", "name": "enable"}, {"description": "Disable broadcast storm control", "help": "Disable broadcast storm control.", "label": "Disable", "name": "disable"}]]  # Enable/disable storm control to drop broadcast traffic.


class StormControl:
    """
    Configure FortiSwitch storm control.
    
    Path: switch_controller/storm_control
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
        payload_dict: StormControlPayload | None = ...,
        rate: int | None = ...,
        burst_size_level: int | None = ...,
        unknown_unicast: Literal[{"description": "Enable unknown unicast storm control", "help": "Enable unknown unicast storm control.", "label": "Enable", "name": "enable"}, {"description": "Disable unknown unicast storm control", "help": "Disable unknown unicast storm control.", "label": "Disable", "name": "disable"}] | None = ...,
        unknown_multicast: Literal[{"description": "Enable unknown multicast storm control", "help": "Enable unknown multicast storm control.", "label": "Enable", "name": "enable"}, {"description": "Disable unknown multicast storm control", "help": "Disable unknown multicast storm control.", "label": "Disable", "name": "disable"}] | None = ...,
        broadcast: Literal[{"description": "Enable broadcast storm control", "help": "Enable broadcast storm control.", "label": "Enable", "name": "enable"}, {"description": "Disable broadcast storm control", "help": "Disable broadcast storm control.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: StormControlPayload | None = ...,
        rate: int | None = ...,
        burst_size_level: int | None = ...,
        unknown_unicast: Literal[{"description": "Enable unknown unicast storm control", "help": "Enable unknown unicast storm control.", "label": "Enable", "name": "enable"}, {"description": "Disable unknown unicast storm control", "help": "Disable unknown unicast storm control.", "label": "Disable", "name": "disable"}] | None = ...,
        unknown_multicast: Literal[{"description": "Enable unknown multicast storm control", "help": "Enable unknown multicast storm control.", "label": "Enable", "name": "enable"}, {"description": "Disable unknown multicast storm control", "help": "Disable unknown multicast storm control.", "label": "Disable", "name": "disable"}] | None = ...,
        broadcast: Literal[{"description": "Enable broadcast storm control", "help": "Enable broadcast storm control.", "label": "Enable", "name": "enable"}, {"description": "Disable broadcast storm control", "help": "Disable broadcast storm control.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: StormControlPayload | None = ...,
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
    "StormControl",
    "StormControlPayload",
]