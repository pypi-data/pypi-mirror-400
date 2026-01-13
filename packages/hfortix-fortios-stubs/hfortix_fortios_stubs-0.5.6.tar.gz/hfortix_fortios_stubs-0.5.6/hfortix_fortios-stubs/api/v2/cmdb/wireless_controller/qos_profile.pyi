from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class QosProfilePayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/qos_profile payload fields.
    
    Configure WiFi quality of service (QoS) profiles.
    
    **Usage:**
        payload: QosProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # WiFi QoS profile name.
    comment: NotRequired[str]  # Comment.
    uplink: NotRequired[int]  # Maximum uplink bandwidth for Virtual Access Points (VAPs) (0
    downlink: NotRequired[int]  # Maximum downlink bandwidth for Virtual Access Points (VAPs) 
    uplink_sta: NotRequired[int]  # Maximum uplink bandwidth for clients (0 - 2097152 Kbps, defa
    downlink_sta: NotRequired[int]  # Maximum downlink bandwidth for clients (0 - 2097152 Kbps, de
    burst: NotRequired[Literal[{"description": "Enable client rate burst", "help": "Enable client rate burst.", "label": "Enable", "name": "enable"}, {"description": "Disable client rate burst", "help": "Disable client rate burst.", "label": "Disable", "name": "disable"}]]  # Enable/disable client rate burst.
    wmm: NotRequired[Literal[{"description": "Enable WiFi multi-media (WMM) control", "help": "Enable WiFi multi-media (WMM) control.", "label": "Enable", "name": "enable"}, {"description": "Disable WiFi multi-media (WMM) control", "help": "Disable WiFi multi-media (WMM) control.", "label": "Disable", "name": "disable"}]]  # Enable/disable WiFi multi-media (WMM) control.
    wmm_uapsd: NotRequired[Literal[{"description": "Enable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode", "help": "Enable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode", "help": "Disable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode.", "label": "Disable", "name": "disable"}]]  # Enable/disable WMM Unscheduled Automatic Power Save Delivery
    call_admission_control: NotRequired[Literal[{"description": "Enable WMM call admission control", "help": "Enable WMM call admission control.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM call admission control", "help": "Disable WMM call admission control.", "label": "Disable", "name": "disable"}]]  # Enable/disable WMM call admission control.
    call_capacity: NotRequired[int]  # Maximum number of Voice over WLAN (VoWLAN) phones allowed (0
    bandwidth_admission_control: NotRequired[Literal[{"description": "Enable WMM bandwidth admission control", "help": "Enable WMM bandwidth admission control.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM bandwidth admission control", "help": "Disable WMM bandwidth admission control.", "label": "Disable", "name": "disable"}]]  # Enable/disable WMM bandwidth admission control.
    bandwidth_capacity: NotRequired[int]  # Maximum bandwidth capacity allowed (1 - 600000 Kbps, default
    dscp_wmm_mapping: NotRequired[Literal[{"description": "Enable Differentiated Services Code Point (DSCP) mapping", "help": "Enable Differentiated Services Code Point (DSCP) mapping.", "label": "Enable", "name": "enable"}, {"description": "Disable Differentiated Services Code Point (DSCP) mapping", "help": "Disable Differentiated Services Code Point (DSCP) mapping.", "label": "Disable", "name": "disable"}]]  # Enable/disable Differentiated Services Code Point (DSCP) map
    dscp_wmm_vo: NotRequired[list[dict[str, Any]]]  # DSCP mapping for voice access (default = 48 56).
    dscp_wmm_vi: NotRequired[list[dict[str, Any]]]  # DSCP mapping for video access (default = 32 40).
    dscp_wmm_be: NotRequired[list[dict[str, Any]]]  # DSCP mapping for best effort access (default = 0 24).
    dscp_wmm_bk: NotRequired[list[dict[str, Any]]]  # DSCP mapping for background access (default = 8 16).
    wmm_dscp_marking: NotRequired[Literal[{"description": "Enable WMM Differentiated Services Code Point (DSCP) marking", "help": "Enable WMM Differentiated Services Code Point (DSCP) marking.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM Differentiated Services Code Point (DSCP) marking", "help": "Disable WMM Differentiated Services Code Point (DSCP) marking.", "label": "Disable", "name": "disable"}]]  # Enable/disable WMM Differentiated Services Code Point (DSCP)
    wmm_vo_dscp: NotRequired[int]  # DSCP marking for voice access (default = 48).
    wmm_vi_dscp: NotRequired[int]  # DSCP marking for video access (default = 32).
    wmm_be_dscp: NotRequired[int]  # DSCP marking for best effort access (default = 0).
    wmm_bk_dscp: NotRequired[int]  # DSCP marking for background access (default = 8).


class QosProfile:
    """
    Configure WiFi quality of service (QoS) profiles.
    
    Path: wireless_controller/qos_profile
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
        payload_dict: QosProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        uplink: int | None = ...,
        downlink: int | None = ...,
        uplink_sta: int | None = ...,
        downlink_sta: int | None = ...,
        burst: Literal[{"description": "Enable client rate burst", "help": "Enable client rate burst.", "label": "Enable", "name": "enable"}, {"description": "Disable client rate burst", "help": "Disable client rate burst.", "label": "Disable", "name": "disable"}] | None = ...,
        wmm: Literal[{"description": "Enable WiFi multi-media (WMM) control", "help": "Enable WiFi multi-media (WMM) control.", "label": "Enable", "name": "enable"}, {"description": "Disable WiFi multi-media (WMM) control", "help": "Disable WiFi multi-media (WMM) control.", "label": "Disable", "name": "disable"}] | None = ...,
        wmm_uapsd: Literal[{"description": "Enable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode", "help": "Enable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode", "help": "Disable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode.", "label": "Disable", "name": "disable"}] | None = ...,
        call_admission_control: Literal[{"description": "Enable WMM call admission control", "help": "Enable WMM call admission control.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM call admission control", "help": "Disable WMM call admission control.", "label": "Disable", "name": "disable"}] | None = ...,
        call_capacity: int | None = ...,
        bandwidth_admission_control: Literal[{"description": "Enable WMM bandwidth admission control", "help": "Enable WMM bandwidth admission control.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM bandwidth admission control", "help": "Disable WMM bandwidth admission control.", "label": "Disable", "name": "disable"}] | None = ...,
        bandwidth_capacity: int | None = ...,
        dscp_wmm_mapping: Literal[{"description": "Enable Differentiated Services Code Point (DSCP) mapping", "help": "Enable Differentiated Services Code Point (DSCP) mapping.", "label": "Enable", "name": "enable"}, {"description": "Disable Differentiated Services Code Point (DSCP) mapping", "help": "Disable Differentiated Services Code Point (DSCP) mapping.", "label": "Disable", "name": "disable"}] | None = ...,
        dscp_wmm_vo: list[dict[str, Any]] | None = ...,
        dscp_wmm_vi: list[dict[str, Any]] | None = ...,
        dscp_wmm_be: list[dict[str, Any]] | None = ...,
        dscp_wmm_bk: list[dict[str, Any]] | None = ...,
        wmm_dscp_marking: Literal[{"description": "Enable WMM Differentiated Services Code Point (DSCP) marking", "help": "Enable WMM Differentiated Services Code Point (DSCP) marking.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM Differentiated Services Code Point (DSCP) marking", "help": "Disable WMM Differentiated Services Code Point (DSCP) marking.", "label": "Disable", "name": "disable"}] | None = ...,
        wmm_vo_dscp: int | None = ...,
        wmm_vi_dscp: int | None = ...,
        wmm_be_dscp: int | None = ...,
        wmm_bk_dscp: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: QosProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        uplink: int | None = ...,
        downlink: int | None = ...,
        uplink_sta: int | None = ...,
        downlink_sta: int | None = ...,
        burst: Literal[{"description": "Enable client rate burst", "help": "Enable client rate burst.", "label": "Enable", "name": "enable"}, {"description": "Disable client rate burst", "help": "Disable client rate burst.", "label": "Disable", "name": "disable"}] | None = ...,
        wmm: Literal[{"description": "Enable WiFi multi-media (WMM) control", "help": "Enable WiFi multi-media (WMM) control.", "label": "Enable", "name": "enable"}, {"description": "Disable WiFi multi-media (WMM) control", "help": "Disable WiFi multi-media (WMM) control.", "label": "Disable", "name": "disable"}] | None = ...,
        wmm_uapsd: Literal[{"description": "Enable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode", "help": "Enable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode", "help": "Disable WMM Unscheduled Automatic Power Save Delivery (U-APSD) power save mode.", "label": "Disable", "name": "disable"}] | None = ...,
        call_admission_control: Literal[{"description": "Enable WMM call admission control", "help": "Enable WMM call admission control.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM call admission control", "help": "Disable WMM call admission control.", "label": "Disable", "name": "disable"}] | None = ...,
        call_capacity: int | None = ...,
        bandwidth_admission_control: Literal[{"description": "Enable WMM bandwidth admission control", "help": "Enable WMM bandwidth admission control.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM bandwidth admission control", "help": "Disable WMM bandwidth admission control.", "label": "Disable", "name": "disable"}] | None = ...,
        bandwidth_capacity: int | None = ...,
        dscp_wmm_mapping: Literal[{"description": "Enable Differentiated Services Code Point (DSCP) mapping", "help": "Enable Differentiated Services Code Point (DSCP) mapping.", "label": "Enable", "name": "enable"}, {"description": "Disable Differentiated Services Code Point (DSCP) mapping", "help": "Disable Differentiated Services Code Point (DSCP) mapping.", "label": "Disable", "name": "disable"}] | None = ...,
        dscp_wmm_vo: list[dict[str, Any]] | None = ...,
        dscp_wmm_vi: list[dict[str, Any]] | None = ...,
        dscp_wmm_be: list[dict[str, Any]] | None = ...,
        dscp_wmm_bk: list[dict[str, Any]] | None = ...,
        wmm_dscp_marking: Literal[{"description": "Enable WMM Differentiated Services Code Point (DSCP) marking", "help": "Enable WMM Differentiated Services Code Point (DSCP) marking.", "label": "Enable", "name": "enable"}, {"description": "Disable WMM Differentiated Services Code Point (DSCP) marking", "help": "Disable WMM Differentiated Services Code Point (DSCP) marking.", "label": "Disable", "name": "disable"}] | None = ...,
        wmm_vo_dscp: int | None = ...,
        wmm_vi_dscp: int | None = ...,
        wmm_be_dscp: int | None = ...,
        wmm_bk_dscp: int | None = ...,
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
        payload_dict: QosProfilePayload | None = ...,
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
    "QosProfile",
    "QosProfilePayload",
]