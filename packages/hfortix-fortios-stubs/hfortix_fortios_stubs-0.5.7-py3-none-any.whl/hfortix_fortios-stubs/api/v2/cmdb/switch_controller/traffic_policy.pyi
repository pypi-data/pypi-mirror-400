from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class TrafficPolicyPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/traffic_policy payload fields.
    
    Configure FortiSwitch traffic policy.
    
    **Usage:**
        payload: TrafficPolicyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Traffic policy name.
    description: NotRequired[str]  # Description of the traffic policy.
    policer_status: NotRequired[Literal[{"description": "Enable policer config on the traffic policy", "help": "Enable policer config on the traffic policy.", "label": "Enable", "name": "enable"}, {"description": "Disable policer config on the traffic policy", "help": "Disable policer config on the traffic policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable policer config on the traffic policy.
    guaranteed_bandwidth: NotRequired[int]  # Guaranteed bandwidth in kbps (max value = 524287000).
    guaranteed_burst: NotRequired[int]  # Guaranteed burst size in bytes (max value = 4294967295).
    maximum_burst: NotRequired[int]  # Maximum burst size in bytes (max value = 4294967295).
    type: NotRequired[Literal[{"description": "Ingress policy", "help": "Ingress policy.", "label": "Ingress", "name": "ingress"}, {"description": "Egress policy", "help": "Egress policy.", "label": "Egress", "name": "egress"}]]  # Configure type of policy(ingress/egress).
    cos_queue: NotRequired[int]  # COS queue(0 - 7), or unset to disable.


class TrafficPolicy:
    """
    Configure FortiSwitch traffic policy.
    
    Path: switch_controller/traffic_policy
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
        payload_dict: TrafficPolicyPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        policer_status: Literal[{"description": "Enable policer config on the traffic policy", "help": "Enable policer config on the traffic policy.", "label": "Enable", "name": "enable"}, {"description": "Disable policer config on the traffic policy", "help": "Disable policer config on the traffic policy.", "label": "Disable", "name": "disable"}] | None = ...,
        guaranteed_bandwidth: int | None = ...,
        guaranteed_burst: int | None = ...,
        maximum_burst: int | None = ...,
        type: Literal[{"description": "Ingress policy", "help": "Ingress policy.", "label": "Ingress", "name": "ingress"}, {"description": "Egress policy", "help": "Egress policy.", "label": "Egress", "name": "egress"}] | None = ...,
        cos_queue: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: TrafficPolicyPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        policer_status: Literal[{"description": "Enable policer config on the traffic policy", "help": "Enable policer config on the traffic policy.", "label": "Enable", "name": "enable"}, {"description": "Disable policer config on the traffic policy", "help": "Disable policer config on the traffic policy.", "label": "Disable", "name": "disable"}] | None = ...,
        guaranteed_bandwidth: int | None = ...,
        guaranteed_burst: int | None = ...,
        maximum_burst: int | None = ...,
        type: Literal[{"description": "Ingress policy", "help": "Ingress policy.", "label": "Ingress", "name": "ingress"}, {"description": "Egress policy", "help": "Egress policy.", "label": "Egress", "name": "egress"}] | None = ...,
        cos_queue: int | None = ...,
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
        payload_dict: TrafficPolicyPayload | None = ...,
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
    "TrafficPolicy",
    "TrafficPolicyPayload",
]