from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class InterControllerPayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/inter_controller payload fields.
    
    Configure inter wireless controller operation.
    
    **Usage:**
        payload: InterControllerPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    inter_controller_mode: NotRequired[Literal[{"description": "Disable inter-controller mode", "help": "Disable inter-controller mode.", "label": "Disable", "name": "disable"}, {"description": "Enable layer 2 roaming support between inter-controllers", "help": "Enable layer 2 roaming support between inter-controllers.", "label": "L2 Roaming", "name": "l2-roaming"}, {"description": "Enable 1+1 fast failover mode", "help": "Enable 1+1 fast failover mode.", "label": "1+1", "name": "1+1"}]]  # Configure inter-controller mode (disable, l2-roaming, 1+1, d
    l3_roaming: NotRequired[Literal[{"description": "Enable layer 3 roaming", "help": "Enable layer 3 roaming.", "label": "Enable", "name": "enable"}, {"description": "Disable layer 3 roaming", "help": "Disable layer 3 roaming.", "label": "Disable", "name": "disable"}]]  # Enable/disable layer 3 roaming (default = disable).
    inter_controller_key: NotRequired[str]  # Secret key for inter-controller communications.
    inter_controller_pri: NotRequired[Literal[{"description": "Primary fast failover mode", "help": "Primary fast failover mode.", "label": "Primary", "name": "primary"}, {"description": "Secondary fast failover mode", "help": "Secondary fast failover mode.", "label": "Secondary", "name": "secondary"}]]  # Configure inter-controller's priority (primary or secondary,
    fast_failover_max: NotRequired[int]  # Maximum number of retransmissions for fast failover HA messa
    fast_failover_wait: NotRequired[int]  # Minimum wait time before an AP transitions from secondary co
    inter_controller_peer: NotRequired[list[dict[str, Any]]]  # Fast failover peer wireless controller list.


class InterController:
    """
    Configure inter wireless controller operation.
    
    Path: wireless_controller/inter_controller
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
        payload_dict: InterControllerPayload | None = ...,
        inter_controller_mode: Literal[{"description": "Disable inter-controller mode", "help": "Disable inter-controller mode.", "label": "Disable", "name": "disable"}, {"description": "Enable layer 2 roaming support between inter-controllers", "help": "Enable layer 2 roaming support between inter-controllers.", "label": "L2 Roaming", "name": "l2-roaming"}, {"description": "Enable 1+1 fast failover mode", "help": "Enable 1+1 fast failover mode.", "label": "1+1", "name": "1+1"}] | None = ...,
        l3_roaming: Literal[{"description": "Enable layer 3 roaming", "help": "Enable layer 3 roaming.", "label": "Enable", "name": "enable"}, {"description": "Disable layer 3 roaming", "help": "Disable layer 3 roaming.", "label": "Disable", "name": "disable"}] | None = ...,
        inter_controller_key: str | None = ...,
        inter_controller_pri: Literal[{"description": "Primary fast failover mode", "help": "Primary fast failover mode.", "label": "Primary", "name": "primary"}, {"description": "Secondary fast failover mode", "help": "Secondary fast failover mode.", "label": "Secondary", "name": "secondary"}] | None = ...,
        fast_failover_max: int | None = ...,
        fast_failover_wait: int | None = ...,
        inter_controller_peer: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: InterControllerPayload | None = ...,
        inter_controller_mode: Literal[{"description": "Disable inter-controller mode", "help": "Disable inter-controller mode.", "label": "Disable", "name": "disable"}, {"description": "Enable layer 2 roaming support between inter-controllers", "help": "Enable layer 2 roaming support between inter-controllers.", "label": "L2 Roaming", "name": "l2-roaming"}, {"description": "Enable 1+1 fast failover mode", "help": "Enable 1+1 fast failover mode.", "label": "1+1", "name": "1+1"}] | None = ...,
        l3_roaming: Literal[{"description": "Enable layer 3 roaming", "help": "Enable layer 3 roaming.", "label": "Enable", "name": "enable"}, {"description": "Disable layer 3 roaming", "help": "Disable layer 3 roaming.", "label": "Disable", "name": "disable"}] | None = ...,
        inter_controller_key: str | None = ...,
        inter_controller_pri: Literal[{"description": "Primary fast failover mode", "help": "Primary fast failover mode.", "label": "Primary", "name": "primary"}, {"description": "Secondary fast failover mode", "help": "Secondary fast failover mode.", "label": "Secondary", "name": "secondary"}] | None = ...,
        fast_failover_max: int | None = ...,
        fast_failover_wait: int | None = ...,
        inter_controller_peer: list[dict[str, Any]] | None = ...,
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
        payload_dict: InterControllerPayload | None = ...,
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
    "InterController",
    "InterControllerPayload",
]