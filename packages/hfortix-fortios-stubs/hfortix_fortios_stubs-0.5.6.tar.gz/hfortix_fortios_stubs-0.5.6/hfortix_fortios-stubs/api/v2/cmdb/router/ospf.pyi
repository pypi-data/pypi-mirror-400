from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class OspfPayload(TypedDict, total=False):
    """
    Type hints for router/ospf payload fields.
    
    Configure OSPF.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.router.access-list.AccessListEndpoint` (via: distribute-list-in)
        - :class:`~.router.prefix-list.PrefixListEndpoint` (via: distribute-list-in)
        - :class:`~.router.route-map.RouteMapEndpoint` (via: default-information-route-map, distribute-route-map-in)

    **Usage:**
        payload: OspfPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    abr_type: NotRequired[Literal[{"description": "Cisco", "help": "Cisco.", "label": "Cisco", "name": "cisco"}, {"description": "IBM", "help": "IBM.", "label": "Ibm", "name": "ibm"}, {"description": "Shortcut", "help": "Shortcut.", "label": "Shortcut", "name": "shortcut"}, {"description": "Standard", "help": "Standard.", "label": "Standard", "name": "standard"}]]  # Area border router type.
    auto_cost_ref_bandwidth: NotRequired[int]  # Reference bandwidth in terms of megabits per second.
    distance_external: NotRequired[int]  # Administrative external distance.
    distance_inter_area: NotRequired[int]  # Administrative inter-area distance.
    distance_intra_area: NotRequired[int]  # Administrative intra-area distance.
    database_overflow: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable database overflow.
    database_overflow_max_lsas: NotRequired[int]  # Database overflow maximum LSAs.
    database_overflow_time_to_recover: NotRequired[int]  # Database overflow time to recover (sec).
    default_information_originate: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Always advertise the default router", "help": "Always advertise the default router.", "label": "Always", "name": "always"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable generation of default route.
    default_information_metric: NotRequired[int]  # Default information metric.
    default_information_metric_type: NotRequired[Literal[{"description": "Type 1", "help": "Type 1.", "label": "1", "name": "1"}, {"description": "Type 2", "help": "Type 2.", "label": "2", "name": "2"}]]  # Default information metric type.
    default_information_route_map: NotRequired[str]  # Default information route map.
    default_metric: NotRequired[int]  # Default metric of redistribute routes.
    distance: NotRequired[int]  # Distance of the route.
    lsa_refresh_interval: NotRequired[int]  # The minimal OSPF LSA update time interval
    rfc1583_compatible: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable RFC1583 compatibility.
    router_id: str  # Router ID.
    spf_timers: NotRequired[str]  # SPF calculation frequency.
    bfd: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Bidirectional Forwarding Detection (BFD).
    log_neighbour_changes: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Log of OSPF neighbor changes.
    distribute_list_in: NotRequired[str]  # Filter incoming routes.
    distribute_route_map_in: NotRequired[str]  # Filter incoming external routes by route-map.
    restart_mode: NotRequired[Literal[{"description": "Hitless restart disabled", "help": "Hitless restart disabled.", "label": "None", "name": "none"}, {"description": "LLS mode", "help": "LLS mode.", "label": "Lls", "name": "lls"}, {"description": "Graceful Restart Mode", "help": "Graceful Restart Mode.", "label": "Graceful Restart", "name": "graceful-restart"}]]  # OSPF restart mode (graceful or LLS).
    restart_period: NotRequired[int]  # Graceful restart period.
    restart_on_topology_change: NotRequired[Literal[{"description": "Continue graceful restart upon topology change", "help": "Continue graceful restart upon topology change.", "label": "Enable", "name": "enable"}, {"description": "Exit graceful restart upon topology change", "help": "Exit graceful restart upon topology change.", "label": "Disable", "name": "disable"}]]  # Enable/disable continuing graceful restart upon topology cha
    area: NotRequired[list[dict[str, Any]]]  # OSPF area configuration.
    ospf_interface: NotRequired[list[dict[str, Any]]]  # OSPF interface configuration.
    network: NotRequired[list[dict[str, Any]]]  # OSPF network configuration.
    neighbor: NotRequired[list[dict[str, Any]]]  # OSPF neighbor configuration are used when OSPF runs on non-b
    passive_interface: NotRequired[list[dict[str, Any]]]  # Passive interface configuration.
    summary_address: NotRequired[list[dict[str, Any]]]  # IP address summary configuration.
    distribute_list: NotRequired[list[dict[str, Any]]]  # Distribute list configuration.
    redistribute: NotRequired[list[dict[str, Any]]]  # Redistribute configuration.


class Ospf:
    """
    Configure OSPF.
    
    Path: router/ospf
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
        payload_dict: OspfPayload | None = ...,
        abr_type: Literal[{"description": "Cisco", "help": "Cisco.", "label": "Cisco", "name": "cisco"}, {"description": "IBM", "help": "IBM.", "label": "Ibm", "name": "ibm"}, {"description": "Shortcut", "help": "Shortcut.", "label": "Shortcut", "name": "shortcut"}, {"description": "Standard", "help": "Standard.", "label": "Standard", "name": "standard"}] | None = ...,
        auto_cost_ref_bandwidth: int | None = ...,
        distance_external: int | None = ...,
        distance_inter_area: int | None = ...,
        distance_intra_area: int | None = ...,
        database_overflow: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        database_overflow_max_lsas: int | None = ...,
        database_overflow_time_to_recover: int | None = ...,
        default_information_originate: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Always advertise the default router", "help": "Always advertise the default router.", "label": "Always", "name": "always"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        default_information_metric: int | None = ...,
        default_information_metric_type: Literal[{"description": "Type 1", "help": "Type 1.", "label": "1", "name": "1"}, {"description": "Type 2", "help": "Type 2.", "label": "2", "name": "2"}] | None = ...,
        default_information_route_map: str | None = ...,
        default_metric: int | None = ...,
        distance: int | None = ...,
        lsa_refresh_interval: int | None = ...,
        rfc1583_compatible: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        router_id: str | None = ...,
        spf_timers: str | None = ...,
        bfd: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        log_neighbour_changes: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        distribute_list_in: str | None = ...,
        distribute_route_map_in: str | None = ...,
        restart_mode: Literal[{"description": "Hitless restart disabled", "help": "Hitless restart disabled.", "label": "None", "name": "none"}, {"description": "LLS mode", "help": "LLS mode.", "label": "Lls", "name": "lls"}, {"description": "Graceful Restart Mode", "help": "Graceful Restart Mode.", "label": "Graceful Restart", "name": "graceful-restart"}] | None = ...,
        restart_period: int | None = ...,
        restart_on_topology_change: Literal[{"description": "Continue graceful restart upon topology change", "help": "Continue graceful restart upon topology change.", "label": "Enable", "name": "enable"}, {"description": "Exit graceful restart upon topology change", "help": "Exit graceful restart upon topology change.", "label": "Disable", "name": "disable"}] | None = ...,
        area: list[dict[str, Any]] | None = ...,
        ospf_interface: list[dict[str, Any]] | None = ...,
        network: list[dict[str, Any]] | None = ...,
        neighbor: list[dict[str, Any]] | None = ...,
        passive_interface: list[dict[str, Any]] | None = ...,
        summary_address: list[dict[str, Any]] | None = ...,
        distribute_list: list[dict[str, Any]] | None = ...,
        redistribute: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: OspfPayload | None = ...,
        abr_type: Literal[{"description": "Cisco", "help": "Cisco.", "label": "Cisco", "name": "cisco"}, {"description": "IBM", "help": "IBM.", "label": "Ibm", "name": "ibm"}, {"description": "Shortcut", "help": "Shortcut.", "label": "Shortcut", "name": "shortcut"}, {"description": "Standard", "help": "Standard.", "label": "Standard", "name": "standard"}] | None = ...,
        auto_cost_ref_bandwidth: int | None = ...,
        distance_external: int | None = ...,
        distance_inter_area: int | None = ...,
        distance_intra_area: int | None = ...,
        database_overflow: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        database_overflow_max_lsas: int | None = ...,
        database_overflow_time_to_recover: int | None = ...,
        default_information_originate: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Always advertise the default router", "help": "Always advertise the default router.", "label": "Always", "name": "always"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        default_information_metric: int | None = ...,
        default_information_metric_type: Literal[{"description": "Type 1", "help": "Type 1.", "label": "1", "name": "1"}, {"description": "Type 2", "help": "Type 2.", "label": "2", "name": "2"}] | None = ...,
        default_information_route_map: str | None = ...,
        default_metric: int | None = ...,
        distance: int | None = ...,
        lsa_refresh_interval: int | None = ...,
        rfc1583_compatible: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        router_id: str | None = ...,
        spf_timers: str | None = ...,
        bfd: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        log_neighbour_changes: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        distribute_list_in: str | None = ...,
        distribute_route_map_in: str | None = ...,
        restart_mode: Literal[{"description": "Hitless restart disabled", "help": "Hitless restart disabled.", "label": "None", "name": "none"}, {"description": "LLS mode", "help": "LLS mode.", "label": "Lls", "name": "lls"}, {"description": "Graceful Restart Mode", "help": "Graceful Restart Mode.", "label": "Graceful Restart", "name": "graceful-restart"}] | None = ...,
        restart_period: int | None = ...,
        restart_on_topology_change: Literal[{"description": "Continue graceful restart upon topology change", "help": "Continue graceful restart upon topology change.", "label": "Enable", "name": "enable"}, {"description": "Exit graceful restart upon topology change", "help": "Exit graceful restart upon topology change.", "label": "Disable", "name": "disable"}] | None = ...,
        area: list[dict[str, Any]] | None = ...,
        ospf_interface: list[dict[str, Any]] | None = ...,
        network: list[dict[str, Any]] | None = ...,
        neighbor: list[dict[str, Any]] | None = ...,
        passive_interface: list[dict[str, Any]] | None = ...,
        summary_address: list[dict[str, Any]] | None = ...,
        distribute_list: list[dict[str, Any]] | None = ...,
        redistribute: list[dict[str, Any]] | None = ...,
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
        payload_dict: OspfPayload | None = ...,
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
    "Ospf",
    "OspfPayload",
]