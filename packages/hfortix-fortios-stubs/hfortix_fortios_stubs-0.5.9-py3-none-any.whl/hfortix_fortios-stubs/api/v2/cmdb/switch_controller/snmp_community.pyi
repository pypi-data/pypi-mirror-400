from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SnmpCommunityPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/snmp_community payload fields.
    
    Configure FortiSwitch SNMP v1/v2c communities globally.
    
    **Usage:**
        payload: SnmpCommunityPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    id: int  # SNMP community ID.
    name: str  # SNMP community name.
    status: NotRequired[Literal[{"description": "Disable SNMP community", "help": "Disable SNMP community.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP community", "help": "Enable SNMP community.", "label": "Enable", "name": "enable"}]]  # Enable/disable this SNMP community.
    hosts: NotRequired[list[dict[str, Any]]]  # Configure IPv4 SNMP managers (hosts).
    query_v1_status: NotRequired[Literal[{"description": "Disable SNMP v1 queries", "help": "Disable SNMP v1 queries.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v1 queries", "help": "Enable SNMP v1 queries.", "label": "Enable", "name": "enable"}]]  # Enable/disable SNMP v1 queries.
    query_v1_port: NotRequired[int]  # SNMP v1 query port (default = 161).
    query_v2c_status: NotRequired[Literal[{"description": "Disable SNMP v2c queries", "help": "Disable SNMP v2c queries.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v2c queries", "help": "Enable SNMP v2c queries.", "label": "Enable", "name": "enable"}]]  # Enable/disable SNMP v2c queries.
    query_v2c_port: NotRequired[int]  # SNMP v2c query port (default = 161).
    trap_v1_status: NotRequired[Literal[{"description": "Disable SNMP v1 traps", "help": "Disable SNMP v1 traps.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v1 traps", "help": "Enable SNMP v1 traps.", "label": "Enable", "name": "enable"}]]  # Enable/disable SNMP v1 traps.
    trap_v1_lport: NotRequired[int]  # SNMP v2c trap local port (default = 162).
    trap_v1_rport: NotRequired[int]  # SNMP v2c trap remote port (default = 162).
    trap_v2c_status: NotRequired[Literal[{"description": "Disable SNMP v2c traps", "help": "Disable SNMP v2c traps.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v2c traps", "help": "Enable SNMP v2c traps.", "label": "Enable", "name": "enable"}]]  # Enable/disable SNMP v2c traps.
    trap_v2c_lport: NotRequired[int]  # SNMP v2c trap local port (default = 162).
    trap_v2c_rport: NotRequired[int]  # SNMP v2c trap remote port (default = 162).
    events: NotRequired[Literal[{"description": "Send a trap when CPU usage too high", "help": "Send a trap when CPU usage too high.", "label": "Cpu High", "name": "cpu-high"}, {"description": "Send a trap when available memory is low", "help": "Send a trap when available memory is low.", "label": "Mem Low", "name": "mem-low"}, {"description": "Send a trap when log disk space becomes low", "help": "Send a trap when log disk space becomes low.", "label": "Log Full", "name": "log-full"}, {"description": "Send a trap when an interface IP address is changed", "help": "Send a trap when an interface IP address is changed.", "label": "Intf Ip", "name": "intf-ip"}, {"description": "Send a trap when an entity MIB change occurs (RFC4133)", "help": "Send a trap when an entity MIB change occurs (RFC4133).", "label": "Ent Conf Change", "name": "ent-conf-change"}, {"description": "Send a trap for Learning event (add/delete/movefrom/moveto)", "help": "Send a trap for Learning event (add/delete/movefrom/moveto).", "label": "L2Mac", "name": "l2mac"}]]  # SNMP notifications (traps) to send.


class SnmpCommunity:
    """
    Configure FortiSwitch SNMP v1/v2c communities globally.
    
    Path: switch_controller/snmp_community
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
        payload_dict: SnmpCommunityPayload | None = ...,
        id: int | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Disable SNMP community", "help": "Disable SNMP community.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP community", "help": "Enable SNMP community.", "label": "Enable", "name": "enable"}] | None = ...,
        hosts: list[dict[str, Any]] | None = ...,
        query_v1_status: Literal[{"description": "Disable SNMP v1 queries", "help": "Disable SNMP v1 queries.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v1 queries", "help": "Enable SNMP v1 queries.", "label": "Enable", "name": "enable"}] | None = ...,
        query_v1_port: int | None = ...,
        query_v2c_status: Literal[{"description": "Disable SNMP v2c queries", "help": "Disable SNMP v2c queries.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v2c queries", "help": "Enable SNMP v2c queries.", "label": "Enable", "name": "enable"}] | None = ...,
        query_v2c_port: int | None = ...,
        trap_v1_status: Literal[{"description": "Disable SNMP v1 traps", "help": "Disable SNMP v1 traps.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v1 traps", "help": "Enable SNMP v1 traps.", "label": "Enable", "name": "enable"}] | None = ...,
        trap_v1_lport: int | None = ...,
        trap_v1_rport: int | None = ...,
        trap_v2c_status: Literal[{"description": "Disable SNMP v2c traps", "help": "Disable SNMP v2c traps.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v2c traps", "help": "Enable SNMP v2c traps.", "label": "Enable", "name": "enable"}] | None = ...,
        trap_v2c_lport: int | None = ...,
        trap_v2c_rport: int | None = ...,
        events: Literal[{"description": "Send a trap when CPU usage too high", "help": "Send a trap when CPU usage too high.", "label": "Cpu High", "name": "cpu-high"}, {"description": "Send a trap when available memory is low", "help": "Send a trap when available memory is low.", "label": "Mem Low", "name": "mem-low"}, {"description": "Send a trap when log disk space becomes low", "help": "Send a trap when log disk space becomes low.", "label": "Log Full", "name": "log-full"}, {"description": "Send a trap when an interface IP address is changed", "help": "Send a trap when an interface IP address is changed.", "label": "Intf Ip", "name": "intf-ip"}, {"description": "Send a trap when an entity MIB change occurs (RFC4133)", "help": "Send a trap when an entity MIB change occurs (RFC4133).", "label": "Ent Conf Change", "name": "ent-conf-change"}, {"description": "Send a trap for Learning event (add/delete/movefrom/moveto)", "help": "Send a trap for Learning event (add/delete/movefrom/moveto).", "label": "L2Mac", "name": "l2mac"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SnmpCommunityPayload | None = ...,
        id: int | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Disable SNMP community", "help": "Disable SNMP community.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP community", "help": "Enable SNMP community.", "label": "Enable", "name": "enable"}] | None = ...,
        hosts: list[dict[str, Any]] | None = ...,
        query_v1_status: Literal[{"description": "Disable SNMP v1 queries", "help": "Disable SNMP v1 queries.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v1 queries", "help": "Enable SNMP v1 queries.", "label": "Enable", "name": "enable"}] | None = ...,
        query_v1_port: int | None = ...,
        query_v2c_status: Literal[{"description": "Disable SNMP v2c queries", "help": "Disable SNMP v2c queries.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v2c queries", "help": "Enable SNMP v2c queries.", "label": "Enable", "name": "enable"}] | None = ...,
        query_v2c_port: int | None = ...,
        trap_v1_status: Literal[{"description": "Disable SNMP v1 traps", "help": "Disable SNMP v1 traps.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v1 traps", "help": "Enable SNMP v1 traps.", "label": "Enable", "name": "enable"}] | None = ...,
        trap_v1_lport: int | None = ...,
        trap_v1_rport: int | None = ...,
        trap_v2c_status: Literal[{"description": "Disable SNMP v2c traps", "help": "Disable SNMP v2c traps.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v2c traps", "help": "Enable SNMP v2c traps.", "label": "Enable", "name": "enable"}] | None = ...,
        trap_v2c_lport: int | None = ...,
        trap_v2c_rport: int | None = ...,
        events: Literal[{"description": "Send a trap when CPU usage too high", "help": "Send a trap when CPU usage too high.", "label": "Cpu High", "name": "cpu-high"}, {"description": "Send a trap when available memory is low", "help": "Send a trap when available memory is low.", "label": "Mem Low", "name": "mem-low"}, {"description": "Send a trap when log disk space becomes low", "help": "Send a trap when log disk space becomes low.", "label": "Log Full", "name": "log-full"}, {"description": "Send a trap when an interface IP address is changed", "help": "Send a trap when an interface IP address is changed.", "label": "Intf Ip", "name": "intf-ip"}, {"description": "Send a trap when an entity MIB change occurs (RFC4133)", "help": "Send a trap when an entity MIB change occurs (RFC4133).", "label": "Ent Conf Change", "name": "ent-conf-change"}, {"description": "Send a trap for Learning event (add/delete/movefrom/moveto)", "help": "Send a trap for Learning event (add/delete/movefrom/moveto).", "label": "L2Mac", "name": "l2mac"}] | None = ...,
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
        payload_dict: SnmpCommunityPayload | None = ...,
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
    "SnmpCommunity",
    "SnmpCommunityPayload",
]