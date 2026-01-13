from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class StandaloneClusterPayload(TypedDict, total=False):
    """
    Type hints for system/standalone_cluster payload fields.
    
    Configure FortiGate Session Life Support Protocol (FGSP) cluster attributes.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: session-sync-dev)

    **Usage:**
        payload: StandaloneClusterPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    standalone_group_id: NotRequired[int]  # Cluster group ID (0 - 255). Must be the same for all members
    group_member_id: NotRequired[int]  # Cluster member ID (0 - 15).
    layer2_connection: NotRequired[Literal[{"description": "There exist layer 2 connections among FGSP members", "help": "There exist layer 2 connections among FGSP members.", "label": "Available", "name": "available"}, {"description": "There does not exist layer 2 connection among FGSP members", "help": "There does not exist layer 2 connection among FGSP members.", "label": "Unavailable", "name": "unavailable"}]]  # Indicate whether layer 2 connections are present among FGSP 
    session_sync_dev: NotRequired[list[dict[str, Any]]]  # Offload session-sync process to kernel and sync sessions usi
    encryption: NotRequired[Literal[{"description": "Enable encryption when synchronizing sessions", "help": "Enable encryption when synchronizing sessions.", "label": "Enable", "name": "enable"}, {"description": "Disable encryption when synchronizing sessions", "help": "Disable encryption when synchronizing sessions.", "label": "Disable", "name": "disable"}]]  # Enable/disable encryption when synchronizing sessions.
    psksecret: str  # Pre-shared secret for session synchronization (ASCII string 
    asymmetric_traffic_control: NotRequired[Literal[{"description": "Connection per second (CPS) preferred", "help": "Connection per second (CPS) preferred.", "label": "Cps Preferred", "name": "cps-preferred"}, {"description": "Strict anti-replay check", "help": "Strict anti-replay check.", "label": "Strict Anti Replay", "name": "strict-anti-replay"}]]  # Asymmetric traffic control mode.
    cluster_peer: NotRequired[list[dict[str, Any]]]  # Configure FortiGate Session Life Support Protocol (FGSP) ses
    monitor_interface: NotRequired[list[dict[str, Any]]]  # Configure a list of interfaces on which to monitor itself. M
    pingsvr_monitor_interface: NotRequired[list[dict[str, Any]]]  # List of pingsvr monitor interface to check for remote IP mon
    monitor_prefix: NotRequired[list[dict[str, Any]]]  # Configure a list of routing prefixes to monitor.
    helper_traffic_bounce: NotRequired[Literal[{"description": "Enable helper related traffic bounce", "help": "Enable helper related traffic bounce.", "label": "Enable", "name": "enable"}, {"description": "Disable helper related traffic bounce", "help": "Disable helper related traffic bounce.", "label": "Disable", "name": "disable"}]]  # Enable/disable helper related traffic bounce.
    utm_traffic_bounce: NotRequired[Literal[{"description": "Enable UTM related traffic bounce", "help": "Enable UTM related traffic bounce.", "label": "Enable", "name": "enable"}, {"description": "Disable UTM related traffic bounce", "help": "Disable UTM related traffic bounce.", "label": "Disable", "name": "disable"}]]  # Enable/disable UTM related traffic bounce.


class StandaloneCluster:
    """
    Configure FortiGate Session Life Support Protocol (FGSP) cluster attributes.
    
    Path: system/standalone_cluster
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
        payload_dict: StandaloneClusterPayload | None = ...,
        standalone_group_id: int | None = ...,
        group_member_id: int | None = ...,
        layer2_connection: Literal[{"description": "There exist layer 2 connections among FGSP members", "help": "There exist layer 2 connections among FGSP members.", "label": "Available", "name": "available"}, {"description": "There does not exist layer 2 connection among FGSP members", "help": "There does not exist layer 2 connection among FGSP members.", "label": "Unavailable", "name": "unavailable"}] | None = ...,
        session_sync_dev: list[dict[str, Any]] | None = ...,
        encryption: Literal[{"description": "Enable encryption when synchronizing sessions", "help": "Enable encryption when synchronizing sessions.", "label": "Enable", "name": "enable"}, {"description": "Disable encryption when synchronizing sessions", "help": "Disable encryption when synchronizing sessions.", "label": "Disable", "name": "disable"}] | None = ...,
        psksecret: str | None = ...,
        asymmetric_traffic_control: Literal[{"description": "Connection per second (CPS) preferred", "help": "Connection per second (CPS) preferred.", "label": "Cps Preferred", "name": "cps-preferred"}, {"description": "Strict anti-replay check", "help": "Strict anti-replay check.", "label": "Strict Anti Replay", "name": "strict-anti-replay"}] | None = ...,
        cluster_peer: list[dict[str, Any]] | None = ...,
        monitor_interface: list[dict[str, Any]] | None = ...,
        pingsvr_monitor_interface: list[dict[str, Any]] | None = ...,
        monitor_prefix: list[dict[str, Any]] | None = ...,
        helper_traffic_bounce: Literal[{"description": "Enable helper related traffic bounce", "help": "Enable helper related traffic bounce.", "label": "Enable", "name": "enable"}, {"description": "Disable helper related traffic bounce", "help": "Disable helper related traffic bounce.", "label": "Disable", "name": "disable"}] | None = ...,
        utm_traffic_bounce: Literal[{"description": "Enable UTM related traffic bounce", "help": "Enable UTM related traffic bounce.", "label": "Enable", "name": "enable"}, {"description": "Disable UTM related traffic bounce", "help": "Disable UTM related traffic bounce.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: StandaloneClusterPayload | None = ...,
        standalone_group_id: int | None = ...,
        group_member_id: int | None = ...,
        layer2_connection: Literal[{"description": "There exist layer 2 connections among FGSP members", "help": "There exist layer 2 connections among FGSP members.", "label": "Available", "name": "available"}, {"description": "There does not exist layer 2 connection among FGSP members", "help": "There does not exist layer 2 connection among FGSP members.", "label": "Unavailable", "name": "unavailable"}] | None = ...,
        session_sync_dev: list[dict[str, Any]] | None = ...,
        encryption: Literal[{"description": "Enable encryption when synchronizing sessions", "help": "Enable encryption when synchronizing sessions.", "label": "Enable", "name": "enable"}, {"description": "Disable encryption when synchronizing sessions", "help": "Disable encryption when synchronizing sessions.", "label": "Disable", "name": "disable"}] | None = ...,
        psksecret: str | None = ...,
        asymmetric_traffic_control: Literal[{"description": "Connection per second (CPS) preferred", "help": "Connection per second (CPS) preferred.", "label": "Cps Preferred", "name": "cps-preferred"}, {"description": "Strict anti-replay check", "help": "Strict anti-replay check.", "label": "Strict Anti Replay", "name": "strict-anti-replay"}] | None = ...,
        cluster_peer: list[dict[str, Any]] | None = ...,
        monitor_interface: list[dict[str, Any]] | None = ...,
        pingsvr_monitor_interface: list[dict[str, Any]] | None = ...,
        monitor_prefix: list[dict[str, Any]] | None = ...,
        helper_traffic_bounce: Literal[{"description": "Enable helper related traffic bounce", "help": "Enable helper related traffic bounce.", "label": "Enable", "name": "enable"}, {"description": "Disable helper related traffic bounce", "help": "Disable helper related traffic bounce.", "label": "Disable", "name": "disable"}] | None = ...,
        utm_traffic_bounce: Literal[{"description": "Enable UTM related traffic bounce", "help": "Enable UTM related traffic bounce.", "label": "Enable", "name": "enable"}, {"description": "Disable UTM related traffic bounce", "help": "Disable UTM related traffic bounce.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: StandaloneClusterPayload | None = ...,
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
    "StandaloneCluster",
    "StandaloneClusterPayload",
]