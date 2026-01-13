from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class TrafficShaperPayload(TypedDict, total=False):
    """
    Type hints for firewall/shaper/traffic_shaper payload fields.
    
    Configure shared traffic shaper.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.firewall.traffic-class.TrafficClassEndpoint` (via: exceed-class-id)

    **Usage:**
        payload: TrafficShaperPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Traffic shaper name.
    guaranteed_bandwidth: NotRequired[int]  # Amount of bandwidth guaranteed for this shaper (0 - 80000000
    maximum_bandwidth: NotRequired[int]  # Upper bandwidth limit enforced by this shaper (0 - 80000000)
    bandwidth_unit: NotRequired[Literal[{"description": "Kilobits per second", "help": "Kilobits per second.", "label": "Kbps", "name": "kbps"}, {"description": "Megabits per second", "help": "Megabits per second.", "label": "Mbps", "name": "mbps"}, {"description": "Gigabits per second", "help": "Gigabits per second.", "label": "Gbps", "name": "gbps"}]]  # Unit of measurement for guaranteed and maximum bandwidth for
    priority: NotRequired[Literal[{"description": "Low priority", "help": "Low priority.", "label": "Low", "name": "low"}, {"description": "Medium priority", "help": "Medium priority.", "label": "Medium", "name": "medium"}, {"description": "High priority", "help": "High priority.", "label": "High", "name": "high"}]]  # Higher priority traffic is more likely to be forwarded witho
    per_policy: NotRequired[Literal[{"description": "All referring policies share one traffic shaper", "help": "All referring policies share one traffic shaper.", "label": "Disable", "name": "disable"}, {"description": "Each referring policy has its own traffic shaper", "help": "Each referring policy has its own traffic shaper.", "label": "Enable", "name": "enable"}]]  # Enable/disable applying a separate shaper for each policy. F
    diffserv: NotRequired[Literal[{"description": "Enable setting traffic DiffServ", "help": "Enable setting traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting traffic DiffServ", "help": "Disable setting traffic DiffServ.", "label": "Disable", "name": "disable"}]]  # Enable/disable changing the DiffServ setting applied to traf
    diffservcode: NotRequired[str]  # DiffServ setting to be applied to traffic accepted by this s
    dscp_marking_method: NotRequired[Literal[{"description": "Multistage marking", "help": "Multistage marking.", "label": "Multi Stage", "name": "multi-stage"}, {"description": "Static marking", "help": "Static marking.", "label": "Static", "name": "static"}]]  # Select DSCP marking method.
    exceed_bandwidth: NotRequired[int]  # Exceed bandwidth used for DSCP/VLAN CoS multi-stage marking.
    exceed_dscp: NotRequired[str]  # DSCP mark for traffic in guaranteed-bandwidth and exceed-ban
    maximum_dscp: NotRequired[str]  # DSCP mark for traffic in exceed-bandwidth and maximum-bandwi
    cos_marking: NotRequired[Literal[{"description": "Enable VLAN CoS marking", "help": "Enable VLAN CoS marking.", "label": "Enable", "name": "enable"}, {"description": "Disable VLAN CoS marking", "help": "Disable VLAN CoS marking.", "label": "Disable", "name": "disable"}]]  # Enable/disable VLAN CoS marking.
    cos_marking_method: NotRequired[Literal[{"description": "Multi stage marking", "help": "Multi stage marking.", "label": "Multi Stage", "name": "multi-stage"}, {"description": "Static marking", "help": "Static marking.", "label": "Static", "name": "static"}]]  # Select VLAN CoS marking method.
    cos: NotRequired[str]  # VLAN CoS mark.
    exceed_cos: NotRequired[str]  # VLAN CoS mark for traffic in [guaranteed-bandwidth, exceed-b
    maximum_cos: NotRequired[str]  # VLAN CoS mark for traffic in [exceed-bandwidth, maximum-band
    overhead: NotRequired[int]  # Per-packet size overhead used in rate computations.
    exceed_class_id: NotRequired[int]  # Class ID for traffic in guaranteed-bandwidth and maximum-ban


class TrafficShaper:
    """
    Configure shared traffic shaper.
    
    Path: firewall/shaper/traffic_shaper
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
        payload_dict: TrafficShaperPayload | None = ...,
        name: str | None = ...,
        guaranteed_bandwidth: int | None = ...,
        maximum_bandwidth: int | None = ...,
        bandwidth_unit: Literal[{"description": "Kilobits per second", "help": "Kilobits per second.", "label": "Kbps", "name": "kbps"}, {"description": "Megabits per second", "help": "Megabits per second.", "label": "Mbps", "name": "mbps"}, {"description": "Gigabits per second", "help": "Gigabits per second.", "label": "Gbps", "name": "gbps"}] | None = ...,
        priority: Literal[{"description": "Low priority", "help": "Low priority.", "label": "Low", "name": "low"}, {"description": "Medium priority", "help": "Medium priority.", "label": "Medium", "name": "medium"}, {"description": "High priority", "help": "High priority.", "label": "High", "name": "high"}] | None = ...,
        per_policy: Literal[{"description": "All referring policies share one traffic shaper", "help": "All referring policies share one traffic shaper.", "label": "Disable", "name": "disable"}, {"description": "Each referring policy has its own traffic shaper", "help": "Each referring policy has its own traffic shaper.", "label": "Enable", "name": "enable"}] | None = ...,
        diffserv: Literal[{"description": "Enable setting traffic DiffServ", "help": "Enable setting traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting traffic DiffServ", "help": "Disable setting traffic DiffServ.", "label": "Disable", "name": "disable"}] | None = ...,
        diffservcode: str | None = ...,
        dscp_marking_method: Literal[{"description": "Multistage marking", "help": "Multistage marking.", "label": "Multi Stage", "name": "multi-stage"}, {"description": "Static marking", "help": "Static marking.", "label": "Static", "name": "static"}] | None = ...,
        exceed_bandwidth: int | None = ...,
        exceed_dscp: str | None = ...,
        maximum_dscp: str | None = ...,
        cos_marking: Literal[{"description": "Enable VLAN CoS marking", "help": "Enable VLAN CoS marking.", "label": "Enable", "name": "enable"}, {"description": "Disable VLAN CoS marking", "help": "Disable VLAN CoS marking.", "label": "Disable", "name": "disable"}] | None = ...,
        cos_marking_method: Literal[{"description": "Multi stage marking", "help": "Multi stage marking.", "label": "Multi Stage", "name": "multi-stage"}, {"description": "Static marking", "help": "Static marking.", "label": "Static", "name": "static"}] | None = ...,
        cos: str | None = ...,
        exceed_cos: str | None = ...,
        maximum_cos: str | None = ...,
        overhead: int | None = ...,
        exceed_class_id: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: TrafficShaperPayload | None = ...,
        name: str | None = ...,
        guaranteed_bandwidth: int | None = ...,
        maximum_bandwidth: int | None = ...,
        bandwidth_unit: Literal[{"description": "Kilobits per second", "help": "Kilobits per second.", "label": "Kbps", "name": "kbps"}, {"description": "Megabits per second", "help": "Megabits per second.", "label": "Mbps", "name": "mbps"}, {"description": "Gigabits per second", "help": "Gigabits per second.", "label": "Gbps", "name": "gbps"}] | None = ...,
        priority: Literal[{"description": "Low priority", "help": "Low priority.", "label": "Low", "name": "low"}, {"description": "Medium priority", "help": "Medium priority.", "label": "Medium", "name": "medium"}, {"description": "High priority", "help": "High priority.", "label": "High", "name": "high"}] | None = ...,
        per_policy: Literal[{"description": "All referring policies share one traffic shaper", "help": "All referring policies share one traffic shaper.", "label": "Disable", "name": "disable"}, {"description": "Each referring policy has its own traffic shaper", "help": "Each referring policy has its own traffic shaper.", "label": "Enable", "name": "enable"}] | None = ...,
        diffserv: Literal[{"description": "Enable setting traffic DiffServ", "help": "Enable setting traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting traffic DiffServ", "help": "Disable setting traffic DiffServ.", "label": "Disable", "name": "disable"}] | None = ...,
        diffservcode: str | None = ...,
        dscp_marking_method: Literal[{"description": "Multistage marking", "help": "Multistage marking.", "label": "Multi Stage", "name": "multi-stage"}, {"description": "Static marking", "help": "Static marking.", "label": "Static", "name": "static"}] | None = ...,
        exceed_bandwidth: int | None = ...,
        exceed_dscp: str | None = ...,
        maximum_dscp: str | None = ...,
        cos_marking: Literal[{"description": "Enable VLAN CoS marking", "help": "Enable VLAN CoS marking.", "label": "Enable", "name": "enable"}, {"description": "Disable VLAN CoS marking", "help": "Disable VLAN CoS marking.", "label": "Disable", "name": "disable"}] | None = ...,
        cos_marking_method: Literal[{"description": "Multi stage marking", "help": "Multi stage marking.", "label": "Multi Stage", "name": "multi-stage"}, {"description": "Static marking", "help": "Static marking.", "label": "Static", "name": "static"}] | None = ...,
        cos: str | None = ...,
        exceed_cos: str | None = ...,
        maximum_cos: str | None = ...,
        overhead: int | None = ...,
        exceed_class_id: int | None = ...,
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
        payload_dict: TrafficShaperPayload | None = ...,
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
    "TrafficShaper",
    "TrafficShaperPayload",
]