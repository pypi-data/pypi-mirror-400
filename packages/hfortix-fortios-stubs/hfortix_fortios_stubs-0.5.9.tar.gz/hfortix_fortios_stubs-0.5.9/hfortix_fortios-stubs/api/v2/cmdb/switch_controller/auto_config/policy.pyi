from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class PolicyPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/auto_config/policy payload fields.
    
    Policy definitions which can define the behavior on auto configured interfaces.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.switch-controller.qos.qos-policy.QosPolicyEndpoint` (via: qos-policy)
        - :class:`~.switch-controller.storm-control-policy.StormControlPolicyEndpoint` (via: storm-control-policy)

    **Usage:**
        payload: PolicyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Auto-config policy name.
    qos_policy: NotRequired[str]  # Auto-Config QoS policy.
    storm_control_policy: NotRequired[str]  # Auto-Config storm control policy.
    poe_status: NotRequired[Literal[{"description": "Enable PoE status", "help": "Enable PoE status.", "label": "Enable", "name": "enable"}, {"description": "Disable PoE status", "help": "Disable PoE status.", "label": "Disable", "name": "disable"}]]  # Enable/disable PoE status.
    igmp_flood_report: NotRequired[Literal[{"description": "Enable IGMP flood report", "help": "Enable IGMP flood report.", "label": "Enable", "name": "enable"}, {"description": "Disable IGMP flood report", "help": "Disable IGMP flood report.", "label": "Disable", "name": "disable"}]]  # Enable/disable IGMP flood report.
    igmp_flood_traffic: NotRequired[Literal[{"description": "Enable IGMP flood traffic", "help": "Enable IGMP flood traffic.", "label": "Enable", "name": "enable"}, {"description": "Disable IGMP flood traffic", "help": "Disable IGMP flood traffic.", "label": "Disable", "name": "disable"}]]  # Enable/disable IGMP flood traffic.


class Policy:
    """
    Policy definitions which can define the behavior on auto configured interfaces.
    
    Path: switch_controller/auto_config/policy
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
        payload_dict: PolicyPayload | None = ...,
        name: str | None = ...,
        qos_policy: str | None = ...,
        storm_control_policy: str | None = ...,
        poe_status: Literal[{"description": "Enable PoE status", "help": "Enable PoE status.", "label": "Enable", "name": "enable"}, {"description": "Disable PoE status", "help": "Disable PoE status.", "label": "Disable", "name": "disable"}] | None = ...,
        igmp_flood_report: Literal[{"description": "Enable IGMP flood report", "help": "Enable IGMP flood report.", "label": "Enable", "name": "enable"}, {"description": "Disable IGMP flood report", "help": "Disable IGMP flood report.", "label": "Disable", "name": "disable"}] | None = ...,
        igmp_flood_traffic: Literal[{"description": "Enable IGMP flood traffic", "help": "Enable IGMP flood traffic.", "label": "Enable", "name": "enable"}, {"description": "Disable IGMP flood traffic", "help": "Disable IGMP flood traffic.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: PolicyPayload | None = ...,
        name: str | None = ...,
        qos_policy: str | None = ...,
        storm_control_policy: str | None = ...,
        poe_status: Literal[{"description": "Enable PoE status", "help": "Enable PoE status.", "label": "Enable", "name": "enable"}, {"description": "Disable PoE status", "help": "Disable PoE status.", "label": "Disable", "name": "disable"}] | None = ...,
        igmp_flood_report: Literal[{"description": "Enable IGMP flood report", "help": "Enable IGMP flood report.", "label": "Enable", "name": "enable"}, {"description": "Disable IGMP flood report", "help": "Disable IGMP flood report.", "label": "Disable", "name": "disable"}] | None = ...,
        igmp_flood_traffic: Literal[{"description": "Enable IGMP flood traffic", "help": "Enable IGMP flood traffic.", "label": "Enable", "name": "enable"}, {"description": "Disable IGMP flood traffic", "help": "Disable IGMP flood traffic.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: PolicyPayload | None = ...,
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
    "Policy",
    "PolicyPayload",
]