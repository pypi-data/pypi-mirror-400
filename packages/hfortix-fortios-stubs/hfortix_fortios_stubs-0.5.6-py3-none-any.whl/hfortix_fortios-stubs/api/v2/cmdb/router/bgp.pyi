from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class BgpPayload(TypedDict, total=False):
    """
    Type hints for router/bgp payload fields.
    
    Configure BGP.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.router.route-map.RouteMapEndpoint` (via: dampening-route-map)

    **Usage:**
        payload: BgpPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    asn: str  # Router AS number, asplain/asdot/asdot+ format, 0 to disable 
    router_id: NotRequired[str]  # Router ID.
    keepalive_timer: NotRequired[int]  # Frequency to send keep alive requests.
    holdtime_timer: NotRequired[int]  # Number of seconds to mark peer as dead.
    always_compare_med: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable always compare MED.
    bestpath_as_path_ignore: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable ignore AS path.
    bestpath_cmp_confed_aspath: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable compare federation AS path length.
    bestpath_cmp_routerid: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable compare router ID for identical EBGP paths.
    bestpath_med_confed: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable compare MED among confederation paths.
    bestpath_med_missing_as_worst: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable treat missing MED as least preferred.
    client_to_client_reflection: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable client-to-client route reflection.
    dampening: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable route-flap dampening.
    deterministic_med: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable enforce deterministic comparison of MED.
    ebgp_multipath: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable EBGP multi-path.
    ibgp_multipath: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable IBGP multi-path.
    enforce_first_as: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable enforce first AS for EBGP routes.
    fast_external_failover: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable reset peer BGP session if link goes down.
    log_neighbour_changes: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Log BGP neighbor changes.
    network_import_check: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable ensure BGP network route exists in IGP.
    ignore_optional_capability: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Do not send unknown optional capability notification message
    additional_path: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable selection of BGP IPv4 additional paths.
    additional_path6: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable selection of BGP IPv6 additional paths.
    additional_path_vpnv4: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable selection of BGP VPNv4 additional paths.
    additional_path_vpnv6: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable selection of BGP VPNv6 additional paths.
    multipath_recursive_distance: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of recursive distance to select multipath
    recursive_next_hop: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable recursive resolution of next-hop using BGP ro
    recursive_inherit_priority: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable priority inheritance for recursive resolution
    tag_resolve_mode: NotRequired[Literal[{"description": "Disable tag-match mode", "help": "Disable tag-match mode.", "label": "Disable", "name": "disable"}, {"description": "Use tag-match if a BGP route resolution with another route containing the same tag is successful", "help": "Use tag-match if a BGP route resolution with another route containing the same tag is successful.", "label": "Preferred", "name": "preferred"}, {"description": "Merge tag-match with best-match if they are using different routes", "help": "Merge tag-match with best-match if they are using different routes. The result will exclude the next hops of tag-match whose interfaces or child interfaces have appeared in best-match.", "label": "Merge", "name": "merge"}, {"description": "Merge tag-match with best-match if they are using different routes", "help": "Merge tag-match with best-match if they are using different routes. The result will exclude the next hops of tag-match whose interfaces have appeared in best-match.", "label": "Merge All", "name": "merge-all"}]]  # Configure tag-match mode. Resolves BGP routes with other rou
    cluster_id: NotRequired[str]  # Route reflector cluster ID.
    confederation_identifier: NotRequired[int]  # Confederation identifier.
    confederation_peers: NotRequired[list[dict[str, Any]]]  # Confederation peers.
    dampening_route_map: NotRequired[str]  # Criteria for dampening.
    dampening_reachability_half_life: NotRequired[int]  # Reachability half-life time for penalty (min).
    dampening_reuse: NotRequired[int]  # Threshold to reuse routes.
    dampening_suppress: NotRequired[int]  # Threshold to suppress routes.
    dampening_max_suppress_time: NotRequired[int]  # Maximum minutes a route can be suppressed.
    dampening_unreachability_half_life: NotRequired[int]  # Unreachability half-life time for penalty (min).
    default_local_preference: NotRequired[int]  # Default local preference.
    scan_time: NotRequired[int]  # Background scanner interval (sec), 0 to disable it.
    distance_external: NotRequired[int]  # Distance for routes external to the AS.
    distance_internal: NotRequired[int]  # Distance for routes internal to the AS.
    distance_local: NotRequired[int]  # Distance for routes local to the AS.
    synchronization: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable only advertise routes from iBGP if routes pre
    graceful_restart: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable BGP graceful restart capabilities.
    graceful_restart_time: NotRequired[int]  # Time needed for neighbors to restart (sec).
    graceful_stalepath_time: NotRequired[int]  # Time to hold stale paths of restarting neighbor (sec).
    graceful_update_delay: NotRequired[int]  # Route advertisement/selection delay after restart (sec).
    graceful_end_on_timer: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable to exit graceful restart on timer only.
    additional_path_select: NotRequired[int]  # Number of additional paths to be selected for each IPv4 NLRI
    additional_path_select6: NotRequired[int]  # Number of additional paths to be selected for each IPv6 NLRI
    additional_path_select_vpnv4: NotRequired[int]  # Number of additional paths to be selected for each VPNv4 NLR
    additional_path_select_vpnv6: NotRequired[int]  # Number of additional paths to be selected for each VPNv6 NLR
    cross_family_conditional_adv: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable cross address family conditional advertisemen
    aggregate_address: NotRequired[list[dict[str, Any]]]  # BGP aggregate address table.
    aggregate_address6: NotRequired[list[dict[str, Any]]]  # BGP IPv6 aggregate address table.
    neighbor: NotRequired[list[dict[str, Any]]]  # BGP neighbor table.
    neighbor_group: NotRequired[list[dict[str, Any]]]  # BGP neighbor group table.
    neighbor_range: NotRequired[list[dict[str, Any]]]  # BGP neighbor range table.
    neighbor_range6: NotRequired[list[dict[str, Any]]]  # BGP IPv6 neighbor range table.
    network: NotRequired[list[dict[str, Any]]]  # BGP network table.
    network6: NotRequired[list[dict[str, Any]]]  # BGP IPv6 network table.
    redistribute: NotRequired[list[dict[str, Any]]]  # BGP IPv4 redistribute table.
    redistribute6: NotRequired[list[dict[str, Any]]]  # BGP IPv6 redistribute table.
    admin_distance: NotRequired[list[dict[str, Any]]]  # Administrative distance modifications.
    vrf: NotRequired[list[dict[str, Any]]]  # BGP VRF leaking table.
    vrf6: NotRequired[list[dict[str, Any]]]  # BGP IPv6 VRF leaking table.


class Bgp:
    """
    Configure BGP.
    
    Path: router/bgp
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
        payload_dict: BgpPayload | None = ...,
        asn: str | None = ...,
        router_id: str | None = ...,
        keepalive_timer: int | None = ...,
        holdtime_timer: int | None = ...,
        always_compare_med: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        bestpath_as_path_ignore: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        bestpath_cmp_confed_aspath: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        bestpath_cmp_routerid: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        bestpath_med_confed: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        bestpath_med_missing_as_worst: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        client_to_client_reflection: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        dampening: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        deterministic_med: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ebgp_multipath: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ibgp_multipath: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        enforce_first_as: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        fast_external_failover: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        log_neighbour_changes: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        network_import_check: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ignore_optional_capability: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        additional_path: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        additional_path6: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        additional_path_vpnv4: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        additional_path_vpnv6: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        multipath_recursive_distance: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        recursive_next_hop: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        recursive_inherit_priority: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        tag_resolve_mode: Literal[{"description": "Disable tag-match mode", "help": "Disable tag-match mode.", "label": "Disable", "name": "disable"}, {"description": "Use tag-match if a BGP route resolution with another route containing the same tag is successful", "help": "Use tag-match if a BGP route resolution with another route containing the same tag is successful.", "label": "Preferred", "name": "preferred"}, {"description": "Merge tag-match with best-match if they are using different routes", "help": "Merge tag-match with best-match if they are using different routes. The result will exclude the next hops of tag-match whose interfaces or child interfaces have appeared in best-match.", "label": "Merge", "name": "merge"}, {"description": "Merge tag-match with best-match if they are using different routes", "help": "Merge tag-match with best-match if they are using different routes. The result will exclude the next hops of tag-match whose interfaces have appeared in best-match.", "label": "Merge All", "name": "merge-all"}] | None = ...,
        cluster_id: str | None = ...,
        confederation_identifier: int | None = ...,
        confederation_peers: list[dict[str, Any]] | None = ...,
        dampening_route_map: str | None = ...,
        dampening_reachability_half_life: int | None = ...,
        dampening_reuse: int | None = ...,
        dampening_suppress: int | None = ...,
        dampening_max_suppress_time: int | None = ...,
        dampening_unreachability_half_life: int | None = ...,
        default_local_preference: int | None = ...,
        scan_time: int | None = ...,
        distance_external: int | None = ...,
        distance_internal: int | None = ...,
        distance_local: int | None = ...,
        synchronization: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        graceful_restart: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        graceful_restart_time: int | None = ...,
        graceful_stalepath_time: int | None = ...,
        graceful_update_delay: int | None = ...,
        graceful_end_on_timer: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        additional_path_select: int | None = ...,
        additional_path_select6: int | None = ...,
        additional_path_select_vpnv4: int | None = ...,
        additional_path_select_vpnv6: int | None = ...,
        cross_family_conditional_adv: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        aggregate_address: list[dict[str, Any]] | None = ...,
        aggregate_address6: list[dict[str, Any]] | None = ...,
        neighbor: list[dict[str, Any]] | None = ...,
        neighbor_group: list[dict[str, Any]] | None = ...,
        neighbor_range: list[dict[str, Any]] | None = ...,
        neighbor_range6: list[dict[str, Any]] | None = ...,
        network: list[dict[str, Any]] | None = ...,
        network6: list[dict[str, Any]] | None = ...,
        redistribute: list[dict[str, Any]] | None = ...,
        redistribute6: list[dict[str, Any]] | None = ...,
        admin_distance: list[dict[str, Any]] | None = ...,
        vrf: list[dict[str, Any]] | None = ...,
        vrf6: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: BgpPayload | None = ...,
        asn: str | None = ...,
        router_id: str | None = ...,
        keepalive_timer: int | None = ...,
        holdtime_timer: int | None = ...,
        always_compare_med: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        bestpath_as_path_ignore: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        bestpath_cmp_confed_aspath: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        bestpath_cmp_routerid: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        bestpath_med_confed: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        bestpath_med_missing_as_worst: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        client_to_client_reflection: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        dampening: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        deterministic_med: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ebgp_multipath: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ibgp_multipath: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        enforce_first_as: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        fast_external_failover: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        log_neighbour_changes: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        network_import_check: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ignore_optional_capability: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        additional_path: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        additional_path6: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        additional_path_vpnv4: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        additional_path_vpnv6: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        multipath_recursive_distance: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        recursive_next_hop: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        recursive_inherit_priority: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        tag_resolve_mode: Literal[{"description": "Disable tag-match mode", "help": "Disable tag-match mode.", "label": "Disable", "name": "disable"}, {"description": "Use tag-match if a BGP route resolution with another route containing the same tag is successful", "help": "Use tag-match if a BGP route resolution with another route containing the same tag is successful.", "label": "Preferred", "name": "preferred"}, {"description": "Merge tag-match with best-match if they are using different routes", "help": "Merge tag-match with best-match if they are using different routes. The result will exclude the next hops of tag-match whose interfaces or child interfaces have appeared in best-match.", "label": "Merge", "name": "merge"}, {"description": "Merge tag-match with best-match if they are using different routes", "help": "Merge tag-match with best-match if they are using different routes. The result will exclude the next hops of tag-match whose interfaces have appeared in best-match.", "label": "Merge All", "name": "merge-all"}] | None = ...,
        cluster_id: str | None = ...,
        confederation_identifier: int | None = ...,
        confederation_peers: list[dict[str, Any]] | None = ...,
        dampening_route_map: str | None = ...,
        dampening_reachability_half_life: int | None = ...,
        dampening_reuse: int | None = ...,
        dampening_suppress: int | None = ...,
        dampening_max_suppress_time: int | None = ...,
        dampening_unreachability_half_life: int | None = ...,
        default_local_preference: int | None = ...,
        scan_time: int | None = ...,
        distance_external: int | None = ...,
        distance_internal: int | None = ...,
        distance_local: int | None = ...,
        synchronization: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        graceful_restart: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        graceful_restart_time: int | None = ...,
        graceful_stalepath_time: int | None = ...,
        graceful_update_delay: int | None = ...,
        graceful_end_on_timer: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        additional_path_select: int | None = ...,
        additional_path_select6: int | None = ...,
        additional_path_select_vpnv4: int | None = ...,
        additional_path_select_vpnv6: int | None = ...,
        cross_family_conditional_adv: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        aggregate_address: list[dict[str, Any]] | None = ...,
        aggregate_address6: list[dict[str, Any]] | None = ...,
        neighbor: list[dict[str, Any]] | None = ...,
        neighbor_group: list[dict[str, Any]] | None = ...,
        neighbor_range: list[dict[str, Any]] | None = ...,
        neighbor_range6: list[dict[str, Any]] | None = ...,
        network: list[dict[str, Any]] | None = ...,
        network6: list[dict[str, Any]] | None = ...,
        redistribute: list[dict[str, Any]] | None = ...,
        redistribute6: list[dict[str, Any]] | None = ...,
        admin_distance: list[dict[str, Any]] | None = ...,
        vrf: list[dict[str, Any]] | None = ...,
        vrf6: list[dict[str, Any]] | None = ...,
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
        payload_dict: BgpPayload | None = ...,
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
    "Bgp",
    "BgpPayload",
]