from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SwitchInterfacePayload(TypedDict, total=False):
    """
    Type hints for system/switch_interface payload fields.
    
    Configure software switch interfaces by grouping physical and WiFi interfaces.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: span-dest-port)
        - :class:`~.system.vdom.VdomEndpoint` (via: vdom)

    **Usage:**
        payload: SwitchInterfacePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Interface name (name cannot be in use by any other interface
    vdom: str  # VDOM that the software switch belongs to.
    span_dest_port: NotRequired[str]  # SPAN destination port name. All traffic on the SPAN source p
    span_source_port: NotRequired[list[dict[str, Any]]]  # Physical interface name. Port spanning echoes all traffic on
    member: NotRequired[list[dict[str, Any]]]  # Names of the interfaces that belong to the virtual switch.
    type: NotRequired[Literal[{"description": "Switch for normal switch functionality (available in NAT mode only)", "help": "Switch for normal switch functionality (available in NAT mode only).", "label": "Switch", "name": "switch"}, {"description": "Hub to duplicate packets to all member ports", "help": "Hub to duplicate packets to all member ports.", "label": "Hub", "name": "hub"}]]  # Type of switch based on functionality: switch for normal fun
    intra_switch_policy: NotRequired[Literal[{"description": "Traffic between switch members is implicitly allowed", "help": "Traffic between switch members is implicitly allowed.", "label": "Implicit", "name": "implicit"}, {"description": "Traffic between switch members must match firewall policies", "help": "Traffic between switch members must match firewall policies.", "label": "Explicit", "name": "explicit"}]]  # Allow any traffic between switch interfaces or require firew
    mac_ttl: NotRequired[int]  # Duration for which MAC addresses are held in the ARP table (
    span: NotRequired[Literal[{"description": "Disable port spanning", "help": "Disable port spanning.", "label": "Disable", "name": "disable"}, {"description": "Enable port spanning", "help": "Enable port spanning.", "label": "Enable", "name": "enable"}]]  # Enable/disable port spanning. Port spanning echoes traffic r
    span_direction: NotRequired[Literal[{"description": "Copies only received packets from source SPAN ports to the destination SPAN port", "help": "Copies only received packets from source SPAN ports to the destination SPAN port.", "label": "Rx", "name": "rx"}, {"description": "Copies only transmitted packets from source SPAN ports to the destination SPAN port", "help": "Copies only transmitted packets from source SPAN ports to the destination SPAN port.", "label": "Tx", "name": "tx"}, {"description": "Copies both received and transmitted packets from source SPAN ports to the destination SPAN port", "help": "Copies both received and transmitted packets from source SPAN ports to the destination SPAN port.", "label": "Both", "name": "both"}]]  # The direction in which the SPAN port operates, either: rx, t


class SwitchInterface:
    """
    Configure software switch interfaces by grouping physical and WiFi interfaces.
    
    Path: system/switch_interface
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
        payload_dict: SwitchInterfacePayload | None = ...,
        name: str | None = ...,
        span_dest_port: str | None = ...,
        span_source_port: list[dict[str, Any]] | None = ...,
        member: list[dict[str, Any]] | None = ...,
        type: Literal[{"description": "Switch for normal switch functionality (available in NAT mode only)", "help": "Switch for normal switch functionality (available in NAT mode only).", "label": "Switch", "name": "switch"}, {"description": "Hub to duplicate packets to all member ports", "help": "Hub to duplicate packets to all member ports.", "label": "Hub", "name": "hub"}] | None = ...,
        intra_switch_policy: Literal[{"description": "Traffic between switch members is implicitly allowed", "help": "Traffic between switch members is implicitly allowed.", "label": "Implicit", "name": "implicit"}, {"description": "Traffic between switch members must match firewall policies", "help": "Traffic between switch members must match firewall policies.", "label": "Explicit", "name": "explicit"}] | None = ...,
        mac_ttl: int | None = ...,
        span: Literal[{"description": "Disable port spanning", "help": "Disable port spanning.", "label": "Disable", "name": "disable"}, {"description": "Enable port spanning", "help": "Enable port spanning.", "label": "Enable", "name": "enable"}] | None = ...,
        span_direction: Literal[{"description": "Copies only received packets from source SPAN ports to the destination SPAN port", "help": "Copies only received packets from source SPAN ports to the destination SPAN port.", "label": "Rx", "name": "rx"}, {"description": "Copies only transmitted packets from source SPAN ports to the destination SPAN port", "help": "Copies only transmitted packets from source SPAN ports to the destination SPAN port.", "label": "Tx", "name": "tx"}, {"description": "Copies both received and transmitted packets from source SPAN ports to the destination SPAN port", "help": "Copies both received and transmitted packets from source SPAN ports to the destination SPAN port.", "label": "Both", "name": "both"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SwitchInterfacePayload | None = ...,
        name: str | None = ...,
        span_dest_port: str | None = ...,
        span_source_port: list[dict[str, Any]] | None = ...,
        member: list[dict[str, Any]] | None = ...,
        type: Literal[{"description": "Switch for normal switch functionality (available in NAT mode only)", "help": "Switch for normal switch functionality (available in NAT mode only).", "label": "Switch", "name": "switch"}, {"description": "Hub to duplicate packets to all member ports", "help": "Hub to duplicate packets to all member ports.", "label": "Hub", "name": "hub"}] | None = ...,
        intra_switch_policy: Literal[{"description": "Traffic between switch members is implicitly allowed", "help": "Traffic between switch members is implicitly allowed.", "label": "Implicit", "name": "implicit"}, {"description": "Traffic between switch members must match firewall policies", "help": "Traffic between switch members must match firewall policies.", "label": "Explicit", "name": "explicit"}] | None = ...,
        mac_ttl: int | None = ...,
        span: Literal[{"description": "Disable port spanning", "help": "Disable port spanning.", "label": "Disable", "name": "disable"}, {"description": "Enable port spanning", "help": "Enable port spanning.", "label": "Enable", "name": "enable"}] | None = ...,
        span_direction: Literal[{"description": "Copies only received packets from source SPAN ports to the destination SPAN port", "help": "Copies only received packets from source SPAN ports to the destination SPAN port.", "label": "Rx", "name": "rx"}, {"description": "Copies only transmitted packets from source SPAN ports to the destination SPAN port", "help": "Copies only transmitted packets from source SPAN ports to the destination SPAN port.", "label": "Tx", "name": "tx"}, {"description": "Copies both received and transmitted packets from source SPAN ports to the destination SPAN port", "help": "Copies both received and transmitted packets from source SPAN ports to the destination SPAN port.", "label": "Both", "name": "both"}] | None = ...,
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
        payload_dict: SwitchInterfacePayload | None = ...,
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
    "SwitchInterface",
    "SwitchInterfacePayload",
]