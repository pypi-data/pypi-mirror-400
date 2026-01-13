from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SystemPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/system payload fields.
    
    Configure system-wide switch controller settings.
    
    **Usage:**
        payload: SystemPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    parallel_process_override: NotRequired[Literal[{"description": "Disable maximum parallel process override", "help": "Disable maximum parallel process override.", "label": "Disable", "name": "disable"}, {"description": "Enable maximum parallel process override", "help": "Enable maximum parallel process override.", "label": "Enable", "name": "enable"}]]  # Enable/disable parallel process override.
    parallel_process: NotRequired[int]  # Maximum number of parallel processes.
    data_sync_interval: NotRequired[int]  # Time interval between collection of switch data (30 - 1800 s
    iot_weight_threshold: NotRequired[int]  # MAC entry's confidence value. Value is re-queried when below
    iot_scan_interval: NotRequired[int]  # IoT scan interval (2 - 10080 mins, default = 60 mins, 0 = di
    iot_holdoff: NotRequired[int]  # MAC entry's creation time. Time must be greater than this va
    iot_mac_idle: NotRequired[int]  # MAC entry's idle time. MAC entry is removed after this value
    nac_periodic_interval: NotRequired[int]  # Periodic time interval to run NAC engine (5 - 180 sec, defau
    dynamic_periodic_interval: NotRequired[int]  # Periodic time interval to run Dynamic port policy engine (5 
    tunnel_mode: NotRequired[Literal[{"description": "Least restrictive", "help": "Least restrictive. Supports the lowest levels of security but highest compatibility between all FortiSwitch and FortiGate devices. 3rd party certificates permitted.", "label": "Compatible", "name": "compatible"}, {"description": "Moderate level of security", "help": "Moderate level of security. 3rd party certificates permitted.", "label": "Moderate", "name": "moderate"}, {"description": "Highest level of security requirements", "help": "Highest level of security requirements. If enabled, the FortiGate device follows the same security mode requirements as in FIPS/CC mode.", "label": "Strict", "name": "strict"}]]  # Compatible/strict tunnel mode.
    caputp_echo_interval: NotRequired[int]  # Echo interval for the caputp echo requests from swtp.
    caputp_max_retransmit: NotRequired[int]  # Maximum retransmission count for the caputp tunnel packets.


class System:
    """
    Configure system-wide switch controller settings.
    
    Path: switch_controller/system
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
        payload_dict: SystemPayload | None = ...,
        parallel_process_override: Literal[{"description": "Disable maximum parallel process override", "help": "Disable maximum parallel process override.", "label": "Disable", "name": "disable"}, {"description": "Enable maximum parallel process override", "help": "Enable maximum parallel process override.", "label": "Enable", "name": "enable"}] | None = ...,
        parallel_process: int | None = ...,
        data_sync_interval: int | None = ...,
        iot_weight_threshold: int | None = ...,
        iot_scan_interval: int | None = ...,
        iot_holdoff: int | None = ...,
        iot_mac_idle: int | None = ...,
        nac_periodic_interval: int | None = ...,
        dynamic_periodic_interval: int | None = ...,
        tunnel_mode: Literal[{"description": "Least restrictive", "help": "Least restrictive. Supports the lowest levels of security but highest compatibility between all FortiSwitch and FortiGate devices. 3rd party certificates permitted.", "label": "Compatible", "name": "compatible"}, {"description": "Moderate level of security", "help": "Moderate level of security. 3rd party certificates permitted.", "label": "Moderate", "name": "moderate"}, {"description": "Highest level of security requirements", "help": "Highest level of security requirements. If enabled, the FortiGate device follows the same security mode requirements as in FIPS/CC mode.", "label": "Strict", "name": "strict"}] | None = ...,
        caputp_echo_interval: int | None = ...,
        caputp_max_retransmit: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SystemPayload | None = ...,
        parallel_process_override: Literal[{"description": "Disable maximum parallel process override", "help": "Disable maximum parallel process override.", "label": "Disable", "name": "disable"}, {"description": "Enable maximum parallel process override", "help": "Enable maximum parallel process override.", "label": "Enable", "name": "enable"}] | None = ...,
        parallel_process: int | None = ...,
        data_sync_interval: int | None = ...,
        iot_weight_threshold: int | None = ...,
        iot_scan_interval: int | None = ...,
        iot_holdoff: int | None = ...,
        iot_mac_idle: int | None = ...,
        nac_periodic_interval: int | None = ...,
        dynamic_periodic_interval: int | None = ...,
        tunnel_mode: Literal[{"description": "Least restrictive", "help": "Least restrictive. Supports the lowest levels of security but highest compatibility between all FortiSwitch and FortiGate devices. 3rd party certificates permitted.", "label": "Compatible", "name": "compatible"}, {"description": "Moderate level of security", "help": "Moderate level of security. 3rd party certificates permitted.", "label": "Moderate", "name": "moderate"}, {"description": "Highest level of security requirements", "help": "Highest level of security requirements. If enabled, the FortiGate device follows the same security mode requirements as in FIPS/CC mode.", "label": "Strict", "name": "strict"}] | None = ...,
        caputp_echo_interval: int | None = ...,
        caputp_max_retransmit: int | None = ...,
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
        payload_dict: SystemPayload | None = ...,
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
    "System",
    "SystemPayload",
]