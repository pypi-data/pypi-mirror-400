from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ArrpProfilePayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/arrp_profile payload fields.
    
    Configure WiFi Automatic Radio Resource Provisioning (ARRP) profiles.
    
    **Usage:**
        payload: ArrpProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # WiFi ARRP profile name.
    comment: NotRequired[str]  # Comment.
    selection_period: NotRequired[int]  # Period in seconds to measure average channel load, noise flo
    monitor_period: NotRequired[int]  # Period in seconds to measure average transmit retries and re
    weight_managed_ap: NotRequired[int]  # Weight in DARRP channel score calculation for managed APs (0
    weight_rogue_ap: NotRequired[int]  # Weight in DARRP channel score calculation for rogue APs (0 -
    weight_noise_floor: NotRequired[int]  # Weight in DARRP channel score calculation for noise floor (0
    weight_channel_load: NotRequired[int]  # Weight in DARRP channel score calculation for channel load (
    weight_spectral_rssi: NotRequired[int]  # Weight in DARRP channel score calculation for spectral RSSI 
    weight_weather_channel: NotRequired[int]  # Weight in DARRP channel score calculation for weather channe
    weight_dfs_channel: NotRequired[int]  # Weight in DARRP channel score calculation for DFS channel (0
    threshold_ap: NotRequired[int]  # Threshold to reject channel in DARRP channel selection phase
    threshold_noise_floor: NotRequired[str]  # Threshold in dBm to reject channel in DARRP channel selectio
    threshold_channel_load: NotRequired[int]  # Threshold in percentage to reject channel in DARRP channel s
    threshold_spectral_rssi: NotRequired[str]  # Threshold in dBm to reject channel in DARRP channel selectio
    threshold_tx_retries: NotRequired[int]  # Threshold in percentage for transmit retries to trigger chan
    threshold_rx_errors: NotRequired[int]  # Threshold in percentage for receive errors to trigger channe
    include_weather_channel: NotRequired[Literal[{"description": "Include weather channel in darrp channel selection phase 1", "help": "Include weather channel in darrp channel selection phase 1.", "label": "Enable", "name": "enable"}, {"description": "Exclude weather channel in darrp channel selection phase 1", "help": "Exclude weather channel in darrp channel selection phase 1.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of weather channel in DARRP channel selec
    include_dfs_channel: NotRequired[Literal[{"description": "Include DFS channel in darrp channel selection phase 1", "help": "Include DFS channel in darrp channel selection phase 1.", "label": "Enable", "name": "enable"}, {"description": "Exclude DFS channel in darrp channel selection phase 1", "help": "Exclude DFS channel in darrp channel selection phase 1.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of DFS channel in DARRP channel selection
    override_darrp_optimize: NotRequired[Literal[{"description": "Override setting darrp-optimize and darrp-optimize-schedules", "help": "Override setting darrp-optimize and darrp-optimize-schedules.", "label": "Enable", "name": "enable"}, {"description": "Use setting darrp-optimize and darrp-optimize-schedules", "help": "Use setting darrp-optimize and darrp-optimize-schedules.", "label": "Disable", "name": "disable"}]]  # Enable to override setting darrp-optimize and darrp-optimize
    darrp_optimize: NotRequired[int]  # Time for running Distributed Automatic Radio Resource Provis
    darrp_optimize_schedules: NotRequired[list[dict[str, Any]]]  # Firewall schedules for DARRP running time. DARRP will run pe


class ArrpProfile:
    """
    Configure WiFi Automatic Radio Resource Provisioning (ARRP) profiles.
    
    Path: wireless_controller/arrp_profile
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
        payload_dict: ArrpProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        selection_period: int | None = ...,
        monitor_period: int | None = ...,
        weight_managed_ap: int | None = ...,
        weight_rogue_ap: int | None = ...,
        weight_noise_floor: int | None = ...,
        weight_channel_load: int | None = ...,
        weight_spectral_rssi: int | None = ...,
        weight_weather_channel: int | None = ...,
        weight_dfs_channel: int | None = ...,
        threshold_ap: int | None = ...,
        threshold_noise_floor: str | None = ...,
        threshold_channel_load: int | None = ...,
        threshold_spectral_rssi: str | None = ...,
        threshold_tx_retries: int | None = ...,
        threshold_rx_errors: int | None = ...,
        include_weather_channel: Literal[{"description": "Include weather channel in darrp channel selection phase 1", "help": "Include weather channel in darrp channel selection phase 1.", "label": "Enable", "name": "enable"}, {"description": "Exclude weather channel in darrp channel selection phase 1", "help": "Exclude weather channel in darrp channel selection phase 1.", "label": "Disable", "name": "disable"}] | None = ...,
        include_dfs_channel: Literal[{"description": "Include DFS channel in darrp channel selection phase 1", "help": "Include DFS channel in darrp channel selection phase 1.", "label": "Enable", "name": "enable"}, {"description": "Exclude DFS channel in darrp channel selection phase 1", "help": "Exclude DFS channel in darrp channel selection phase 1.", "label": "Disable", "name": "disable"}] | None = ...,
        override_darrp_optimize: Literal[{"description": "Override setting darrp-optimize and darrp-optimize-schedules", "help": "Override setting darrp-optimize and darrp-optimize-schedules.", "label": "Enable", "name": "enable"}, {"description": "Use setting darrp-optimize and darrp-optimize-schedules", "help": "Use setting darrp-optimize and darrp-optimize-schedules.", "label": "Disable", "name": "disable"}] | None = ...,
        darrp_optimize: int | None = ...,
        darrp_optimize_schedules: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ArrpProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        selection_period: int | None = ...,
        monitor_period: int | None = ...,
        weight_managed_ap: int | None = ...,
        weight_rogue_ap: int | None = ...,
        weight_noise_floor: int | None = ...,
        weight_channel_load: int | None = ...,
        weight_spectral_rssi: int | None = ...,
        weight_weather_channel: int | None = ...,
        weight_dfs_channel: int | None = ...,
        threshold_ap: int | None = ...,
        threshold_noise_floor: str | None = ...,
        threshold_channel_load: int | None = ...,
        threshold_spectral_rssi: str | None = ...,
        threshold_tx_retries: int | None = ...,
        threshold_rx_errors: int | None = ...,
        include_weather_channel: Literal[{"description": "Include weather channel in darrp channel selection phase 1", "help": "Include weather channel in darrp channel selection phase 1.", "label": "Enable", "name": "enable"}, {"description": "Exclude weather channel in darrp channel selection phase 1", "help": "Exclude weather channel in darrp channel selection phase 1.", "label": "Disable", "name": "disable"}] | None = ...,
        include_dfs_channel: Literal[{"description": "Include DFS channel in darrp channel selection phase 1", "help": "Include DFS channel in darrp channel selection phase 1.", "label": "Enable", "name": "enable"}, {"description": "Exclude DFS channel in darrp channel selection phase 1", "help": "Exclude DFS channel in darrp channel selection phase 1.", "label": "Disable", "name": "disable"}] | None = ...,
        override_darrp_optimize: Literal[{"description": "Override setting darrp-optimize and darrp-optimize-schedules", "help": "Override setting darrp-optimize and darrp-optimize-schedules.", "label": "Enable", "name": "enable"}, {"description": "Use setting darrp-optimize and darrp-optimize-schedules", "help": "Use setting darrp-optimize and darrp-optimize-schedules.", "label": "Disable", "name": "disable"}] | None = ...,
        darrp_optimize: int | None = ...,
        darrp_optimize_schedules: list[dict[str, Any]] | None = ...,
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
        payload_dict: ArrpProfilePayload | None = ...,
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
    "ArrpProfile",
    "ArrpProfilePayload",
]