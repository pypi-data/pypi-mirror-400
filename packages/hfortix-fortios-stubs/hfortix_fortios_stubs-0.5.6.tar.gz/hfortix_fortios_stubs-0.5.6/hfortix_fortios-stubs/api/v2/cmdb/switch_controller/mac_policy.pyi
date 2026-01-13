from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class MacPolicyPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/mac_policy payload fields.
    
    Configure MAC policy to be applied on the managed FortiSwitch devices through NAC device.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.switch-controller.traffic-policy.TrafficPolicyEndpoint` (via: traffic-policy)
        - :class:`~.system.interface.InterfaceEndpoint` (via: fortilink, vlan)

    **Usage:**
        payload: MacPolicyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # MAC policy name.
    description: NotRequired[str]  # Description for the MAC policy.
    fortilink: str  # FortiLink interface for which this MAC policy belongs to.
    vlan: NotRequired[str]  # Ingress traffic VLAN assignment for the MAC address matching
    traffic_policy: NotRequired[str]  # Traffic policy to be applied when using this MAC policy.
    count: NotRequired[Literal[{"description": "Enable packet count on the NAC device", "help": "Enable packet count on the NAC device.", "label": "Disable", "name": "disable"}, {"description": "Disable packet count on the NAC device", "help": "Disable packet count on the NAC device.", "label": "Enable", "name": "enable"}]]  # Enable/disable packet count on the NAC device.
    bounce_port_link: NotRequired[Literal[{"description": "Disable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied", "help": "Disable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied.", "label": "Disable", "name": "disable"}, {"description": "Enable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied", "help": "Enable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied.", "label": "Enable", "name": "enable"}]]  # Enable/disable bouncing (administratively bring the link dow
    bounce_port_duration: NotRequired[int]  # Bounce duration in seconds of a switch port where this mac-p
    poe_reset: NotRequired[Literal[{"description": "Disable POE reset of a switch port where this mac-policy is applied", "help": "Disable POE reset of a switch port where this mac-policy is applied.", "label": "Disable", "name": "disable"}, {"description": "Enable POE reset of a switch port where this mac-policy is applied", "help": "Enable POE reset of a switch port where this mac-policy is applied.", "label": "Enable", "name": "enable"}]]  # Enable/disable POE reset of a switch port where this mac-pol


class MacPolicy:
    """
    Configure MAC policy to be applied on the managed FortiSwitch devices through NAC device.
    
    Path: switch_controller/mac_policy
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
        payload_dict: MacPolicyPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        fortilink: str | None = ...,
        vlan: str | None = ...,
        traffic_policy: str | None = ...,
        count: Literal[{"description": "Enable packet count on the NAC device", "help": "Enable packet count on the NAC device.", "label": "Disable", "name": "disable"}, {"description": "Disable packet count on the NAC device", "help": "Disable packet count on the NAC device.", "label": "Enable", "name": "enable"}] | None = ...,
        bounce_port_link: Literal[{"description": "Disable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied", "help": "Disable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied.", "label": "Disable", "name": "disable"}, {"description": "Enable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied", "help": "Enable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied.", "label": "Enable", "name": "enable"}] | None = ...,
        bounce_port_duration: int | None = ...,
        poe_reset: Literal[{"description": "Disable POE reset of a switch port where this mac-policy is applied", "help": "Disable POE reset of a switch port where this mac-policy is applied.", "label": "Disable", "name": "disable"}, {"description": "Enable POE reset of a switch port where this mac-policy is applied", "help": "Enable POE reset of a switch port where this mac-policy is applied.", "label": "Enable", "name": "enable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: MacPolicyPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        fortilink: str | None = ...,
        vlan: str | None = ...,
        traffic_policy: str | None = ...,
        count: Literal[{"description": "Enable packet count on the NAC device", "help": "Enable packet count on the NAC device.", "label": "Disable", "name": "disable"}, {"description": "Disable packet count on the NAC device", "help": "Disable packet count on the NAC device.", "label": "Enable", "name": "enable"}] | None = ...,
        bounce_port_link: Literal[{"description": "Disable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied", "help": "Disable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied.", "label": "Disable", "name": "disable"}, {"description": "Enable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied", "help": "Enable bouncing (administratively bring the link down, up) of a switch port where this mac-policy is applied.", "label": "Enable", "name": "enable"}] | None = ...,
        bounce_port_duration: int | None = ...,
        poe_reset: Literal[{"description": "Disable POE reset of a switch port where this mac-policy is applied", "help": "Disable POE reset of a switch port where this mac-policy is applied.", "label": "Disable", "name": "disable"}, {"description": "Enable POE reset of a switch port where this mac-policy is applied", "help": "Enable POE reset of a switch port where this mac-policy is applied.", "label": "Enable", "name": "enable"}] | None = ...,
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
        payload_dict: MacPolicyPayload | None = ...,
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
    "MacPolicy",
    "MacPolicyPayload",
]