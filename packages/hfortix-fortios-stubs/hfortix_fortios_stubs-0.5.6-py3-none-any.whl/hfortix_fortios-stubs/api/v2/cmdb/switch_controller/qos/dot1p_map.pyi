from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class Dot1pMapPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/qos/dot1p_map payload fields.
    
    Configure FortiSwitch QoS 802.1p.
    
    **Usage:**
        payload: Dot1pMapPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Dot1p map name.
    description: NotRequired[str]  # Description of the 802.1p name.
    egress_pri_tagging: Literal[{"description": "Disable egress priority tagging", "help": "Disable egress priority tagging.", "label": "Disable", "name": "disable"}, {"description": "Enable egress priority tagging", "help": "Enable egress priority tagging.", "label": "Enable", "name": "enable"}]  # Enable/disable egress priority-tag frame.
    priority_0: NotRequired[Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}]]  # COS queue mapped to dot1p priority number.
    priority_1: NotRequired[Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}]]  # COS queue mapped to dot1p priority number.
    priority_2: NotRequired[Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}]]  # COS queue mapped to dot1p priority number.
    priority_3: NotRequired[Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}]]  # COS queue mapped to dot1p priority number.
    priority_4: NotRequired[Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}]]  # COS queue mapped to dot1p priority number.
    priority_5: NotRequired[Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}]]  # COS queue mapped to dot1p priority number.
    priority_6: NotRequired[Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}]]  # COS queue mapped to dot1p priority number.
    priority_7: NotRequired[Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}]]  # COS queue mapped to dot1p priority number.


class Dot1pMap:
    """
    Configure FortiSwitch QoS 802.1p.
    
    Path: switch_controller/qos/dot1p_map
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
        payload_dict: Dot1pMapPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        egress_pri_tagging: Literal[{"description": "Disable egress priority tagging", "help": "Disable egress priority tagging.", "label": "Disable", "name": "disable"}, {"description": "Enable egress priority tagging", "help": "Enable egress priority tagging.", "label": "Enable", "name": "enable"}] | None = ...,
        priority_0: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_1: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_2: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_3: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_4: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_5: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_6: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_7: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: Dot1pMapPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        egress_pri_tagging: Literal[{"description": "Disable egress priority tagging", "help": "Disable egress priority tagging.", "label": "Disable", "name": "disable"}, {"description": "Enable egress priority tagging", "help": "Enable egress priority tagging.", "label": "Enable", "name": "enable"}] | None = ...,
        priority_0: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_1: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_2: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_3: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_4: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_5: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_6: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
        priority_7: Literal[{"description": "COS queue 0 (lowest priority)", "help": "COS queue 0 (lowest priority).", "label": "Queue 0", "name": "queue-0"}, {"description": "COS queue 1", "help": "COS queue 1.", "label": "Queue 1", "name": "queue-1"}, {"description": "COS queue 2", "help": "COS queue 2.", "label": "Queue 2", "name": "queue-2"}, {"description": "COS queue 3", "help": "COS queue 3.", "label": "Queue 3", "name": "queue-3"}, {"description": "COS queue 4", "help": "COS queue 4.", "label": "Queue 4", "name": "queue-4"}, {"description": "COS queue 5", "help": "COS queue 5.", "label": "Queue 5", "name": "queue-5"}, {"description": "COS queue 6", "help": "COS queue 6.", "label": "Queue 6", "name": "queue-6"}, {"description": "COS queue 7 (highest priority)", "help": "COS queue 7 (highest priority).", "label": "Queue 7", "name": "queue-7"}] | None = ...,
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
        payload_dict: Dot1pMapPayload | None = ...,
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
    "Dot1pMap",
    "Dot1pMapPayload",
]