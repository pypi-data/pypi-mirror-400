from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SdwanPayload(TypedDict, total=False):
    """
    Type hints for system/sdwan payload fields.
    
    Configure redundant Internet connections with multiple outbound links and health-check profiles.
    
    **Usage:**
        payload: SdwanPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: NotRequired[Literal[{"description": "Disable SD-WAN", "help": "Disable SD-WAN.", "label": "Disable", "name": "disable"}, {"description": "Enable SD-WAN", "help": "Enable SD-WAN.", "label": "Enable", "name": "enable"}]]  # Enable/disable SD-WAN.
    load_balance_mode: NotRequired[Literal[{"description": "Source IP load balancing", "help": "Source IP load balancing. All traffic from a source IP is sent to the same interface.", "label": "Source Ip Based", "name": "source-ip-based"}, {"description": "Weight-based load balancing", "help": "Weight-based load balancing. Interfaces with higher weights have higher priority and get more traffic.", "label": "Weight Based", "name": "weight-based"}, {"description": "Usage-based load balancing", "help": "Usage-based load balancing. All traffic is sent to the first interface on the list. When the bandwidth on that interface exceeds the spill-over limit new traffic is sent to the next interface.", "label": "Usage Based", "name": "usage-based"}, {"description": "Source and destination IP load balancing", "help": "Source and destination IP load balancing. All traffic from a source IP to a destination IP is sent to the same interface.", "label": "Source Dest Ip Based", "name": "source-dest-ip-based"}, {"description": "Volume-based load balancing", "help": "Volume-based load balancing. Traffic is load balanced based on traffic volume (in bytes). More traffic is sent to interfaces with higher volume ratios.", "label": "Measured Volume Based", "name": "measured-volume-based"}]]  # Algorithm or mode to use for load balancing Internet traffic
    speedtest_bypass_routing: NotRequired[Literal[{"description": "Disable SD-WAN", "help": "Disable SD-WAN.", "label": "Disable", "name": "disable"}, {"description": "Enable SD-WAN", "help": "Enable SD-WAN.", "label": "Enable", "name": "enable"}]]  # Enable/disable bypass routing when speedtest on a SD-WAN mem
    duplication_max_num: NotRequired[int]  # Maximum number of interface members a packet is duplicated i
    duplication_max_discrepancy: NotRequired[int]  # Maximum discrepancy between two packets for deduplication in
    neighbor_hold_down: NotRequired[Literal[{"description": "Enable hold switching from the secondary neighbor to the primary neighbor", "help": "Enable hold switching from the secondary neighbor to the primary neighbor.", "label": "Enable", "name": "enable"}, {"description": "Disable hold switching from the secondary neighbor to the primary neighbor", "help": "Disable hold switching from the secondary neighbor to the primary neighbor.", "label": "Disable", "name": "disable"}]]  # Enable/disable hold switching from the secondary neighbor to
    neighbor_hold_down_time: NotRequired[int]  # Waiting period in seconds when switching from the secondary 
    app_perf_log_period: NotRequired[int]  # Time interval in seconds that application performance logs a
    neighbor_hold_boot_time: NotRequired[int]  # Waiting period in seconds when switching from the primary ne
    fail_detect: NotRequired[Literal[{"description": "Enable status checking", "help": "Enable status checking.", "label": "Enable", "name": "enable"}, {"description": "Disable status checking", "help": "Disable status checking.", "label": "Disable", "name": "disable"}]]  # Enable/disable SD-WAN Internet connection status checking (f
    fail_alert_interfaces: NotRequired[list[dict[str, Any]]]  # Physical interfaces that will be alerted.
    zone: NotRequired[list[dict[str, Any]]]  # Configure SD-WAN zones.
    members: NotRequired[list[dict[str, Any]]]  # FortiGate interfaces added to the SD-WAN.
    health_check: NotRequired[list[dict[str, Any]]]  # SD-WAN status checking or health checking. Identify a server
    service: NotRequired[list[dict[str, Any]]]  # Create SD-WAN rules (also called services) to control how se
    neighbor: NotRequired[list[dict[str, Any]]]  # Create SD-WAN neighbor from BGP neighbor table to control ro
    duplication: NotRequired[list[dict[str, Any]]]  # Create SD-WAN duplication rule.


class Sdwan:
    """
    Configure redundant Internet connections with multiple outbound links and health-check profiles.
    
    Path: system/sdwan
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
        payload_dict: SdwanPayload | None = ...,
        status: Literal[{"description": "Disable SD-WAN", "help": "Disable SD-WAN.", "label": "Disable", "name": "disable"}, {"description": "Enable SD-WAN", "help": "Enable SD-WAN.", "label": "Enable", "name": "enable"}] | None = ...,
        load_balance_mode: Literal[{"description": "Source IP load balancing", "help": "Source IP load balancing. All traffic from a source IP is sent to the same interface.", "label": "Source Ip Based", "name": "source-ip-based"}, {"description": "Weight-based load balancing", "help": "Weight-based load balancing. Interfaces with higher weights have higher priority and get more traffic.", "label": "Weight Based", "name": "weight-based"}, {"description": "Usage-based load balancing", "help": "Usage-based load balancing. All traffic is sent to the first interface on the list. When the bandwidth on that interface exceeds the spill-over limit new traffic is sent to the next interface.", "label": "Usage Based", "name": "usage-based"}, {"description": "Source and destination IP load balancing", "help": "Source and destination IP load balancing. All traffic from a source IP to a destination IP is sent to the same interface.", "label": "Source Dest Ip Based", "name": "source-dest-ip-based"}, {"description": "Volume-based load balancing", "help": "Volume-based load balancing. Traffic is load balanced based on traffic volume (in bytes). More traffic is sent to interfaces with higher volume ratios.", "label": "Measured Volume Based", "name": "measured-volume-based"}] | None = ...,
        speedtest_bypass_routing: Literal[{"description": "Disable SD-WAN", "help": "Disable SD-WAN.", "label": "Disable", "name": "disable"}, {"description": "Enable SD-WAN", "help": "Enable SD-WAN.", "label": "Enable", "name": "enable"}] | None = ...,
        duplication_max_num: int | None = ...,
        duplication_max_discrepancy: int | None = ...,
        neighbor_hold_down: Literal[{"description": "Enable hold switching from the secondary neighbor to the primary neighbor", "help": "Enable hold switching from the secondary neighbor to the primary neighbor.", "label": "Enable", "name": "enable"}, {"description": "Disable hold switching from the secondary neighbor to the primary neighbor", "help": "Disable hold switching from the secondary neighbor to the primary neighbor.", "label": "Disable", "name": "disable"}] | None = ...,
        neighbor_hold_down_time: int | None = ...,
        app_perf_log_period: int | None = ...,
        neighbor_hold_boot_time: int | None = ...,
        fail_detect: Literal[{"description": "Enable status checking", "help": "Enable status checking.", "label": "Enable", "name": "enable"}, {"description": "Disable status checking", "help": "Disable status checking.", "label": "Disable", "name": "disable"}] | None = ...,
        fail_alert_interfaces: list[dict[str, Any]] | None = ...,
        zone: list[dict[str, Any]] | None = ...,
        members: list[dict[str, Any]] | None = ...,
        health_check: list[dict[str, Any]] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        neighbor: list[dict[str, Any]] | None = ...,
        duplication: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SdwanPayload | None = ...,
        status: Literal[{"description": "Disable SD-WAN", "help": "Disable SD-WAN.", "label": "Disable", "name": "disable"}, {"description": "Enable SD-WAN", "help": "Enable SD-WAN.", "label": "Enable", "name": "enable"}] | None = ...,
        load_balance_mode: Literal[{"description": "Source IP load balancing", "help": "Source IP load balancing. All traffic from a source IP is sent to the same interface.", "label": "Source Ip Based", "name": "source-ip-based"}, {"description": "Weight-based load balancing", "help": "Weight-based load balancing. Interfaces with higher weights have higher priority and get more traffic.", "label": "Weight Based", "name": "weight-based"}, {"description": "Usage-based load balancing", "help": "Usage-based load balancing. All traffic is sent to the first interface on the list. When the bandwidth on that interface exceeds the spill-over limit new traffic is sent to the next interface.", "label": "Usage Based", "name": "usage-based"}, {"description": "Source and destination IP load balancing", "help": "Source and destination IP load balancing. All traffic from a source IP to a destination IP is sent to the same interface.", "label": "Source Dest Ip Based", "name": "source-dest-ip-based"}, {"description": "Volume-based load balancing", "help": "Volume-based load balancing. Traffic is load balanced based on traffic volume (in bytes). More traffic is sent to interfaces with higher volume ratios.", "label": "Measured Volume Based", "name": "measured-volume-based"}] | None = ...,
        speedtest_bypass_routing: Literal[{"description": "Disable SD-WAN", "help": "Disable SD-WAN.", "label": "Disable", "name": "disable"}, {"description": "Enable SD-WAN", "help": "Enable SD-WAN.", "label": "Enable", "name": "enable"}] | None = ...,
        duplication_max_num: int | None = ...,
        duplication_max_discrepancy: int | None = ...,
        neighbor_hold_down: Literal[{"description": "Enable hold switching from the secondary neighbor to the primary neighbor", "help": "Enable hold switching from the secondary neighbor to the primary neighbor.", "label": "Enable", "name": "enable"}, {"description": "Disable hold switching from the secondary neighbor to the primary neighbor", "help": "Disable hold switching from the secondary neighbor to the primary neighbor.", "label": "Disable", "name": "disable"}] | None = ...,
        neighbor_hold_down_time: int | None = ...,
        app_perf_log_period: int | None = ...,
        neighbor_hold_boot_time: int | None = ...,
        fail_detect: Literal[{"description": "Enable status checking", "help": "Enable status checking.", "label": "Enable", "name": "enable"}, {"description": "Disable status checking", "help": "Disable status checking.", "label": "Disable", "name": "disable"}] | None = ...,
        fail_alert_interfaces: list[dict[str, Any]] | None = ...,
        zone: list[dict[str, Any]] | None = ...,
        members: list[dict[str, Any]] | None = ...,
        health_check: list[dict[str, Any]] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        neighbor: list[dict[str, Any]] | None = ...,
        duplication: list[dict[str, Any]] | None = ...,
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
        payload_dict: SdwanPayload | None = ...,
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
    "Sdwan",
    "SdwanPayload",
]