from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class AutomationConditionPayload(TypedDict, total=False):
    """
    Type hints for system/automation_condition payload fields.
    
    Condition for automation stitches.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.vdom.VdomEndpoint` (via: vdom)

    **Usage:**
        payload: AutomationConditionPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Name.
    description: NotRequired[str]  # Description.
    condition_type: NotRequired[Literal[{"description": "CPU usage condition,    memory:Memory usage condition,    vpn:VPN state condition", "help": "CPU usage condition,", "label": "Cpu", "name": "cpu"}, {"help": "Memory usage condition,", "label": "Memory", "name": "memory"}, {"help": "VPN state condition.", "label": "Vpn", "name": "vpn"}]]  # Condition type.
    cpu_usage_percent: int  # CPU usage reaches specified percentage.
    mem_usage_percent: int  # Memory usage reaches specified percentage.
    vdom: str  # Virtual domain which the tunnel belongs to.
    vpn_tunnel_name: str  # VPN tunnel name.
    vpn_tunnel_state: NotRequired[Literal[{"description": "VPN tunnel is up", "help": "VPN tunnel is up.", "label": "Tunnel Up", "name": "tunnel-up"}, {"description": "VPN tunnel is down", "help": "VPN tunnel is down.", "label": "Tunnel Down", "name": "tunnel-down"}]]  # VPN tunnel state.


class AutomationCondition:
    """
    Condition for automation stitches.
    
    Path: system/automation_condition
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
        payload_dict: AutomationConditionPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        condition_type: Literal[{"description": "CPU usage condition,    memory:Memory usage condition,    vpn:VPN state condition", "help": "CPU usage condition,", "label": "Cpu", "name": "cpu"}, {"help": "Memory usage condition,", "label": "Memory", "name": "memory"}, {"help": "VPN state condition.", "label": "Vpn", "name": "vpn"}] | None = ...,
        cpu_usage_percent: int | None = ...,
        mem_usage_percent: int | None = ...,
        vpn_tunnel_name: str | None = ...,
        vpn_tunnel_state: Literal[{"description": "VPN tunnel is up", "help": "VPN tunnel is up.", "label": "Tunnel Up", "name": "tunnel-up"}, {"description": "VPN tunnel is down", "help": "VPN tunnel is down.", "label": "Tunnel Down", "name": "tunnel-down"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: AutomationConditionPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        condition_type: Literal[{"description": "CPU usage condition,    memory:Memory usage condition,    vpn:VPN state condition", "help": "CPU usage condition,", "label": "Cpu", "name": "cpu"}, {"help": "Memory usage condition,", "label": "Memory", "name": "memory"}, {"help": "VPN state condition.", "label": "Vpn", "name": "vpn"}] | None = ...,
        cpu_usage_percent: int | None = ...,
        mem_usage_percent: int | None = ...,
        vpn_tunnel_name: str | None = ...,
        vpn_tunnel_state: Literal[{"description": "VPN tunnel is up", "help": "VPN tunnel is up.", "label": "Tunnel Up", "name": "tunnel-up"}, {"description": "VPN tunnel is down", "help": "VPN tunnel is down.", "label": "Tunnel Down", "name": "tunnel-down"}] | None = ...,
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
        payload_dict: AutomationConditionPayload | None = ...,
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
    "AutomationCondition",
    "AutomationConditionPayload",
]