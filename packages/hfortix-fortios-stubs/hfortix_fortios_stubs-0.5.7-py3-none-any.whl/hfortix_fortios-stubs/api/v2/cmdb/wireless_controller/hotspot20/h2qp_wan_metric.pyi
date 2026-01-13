from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class H2qpWanMetricPayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/hotspot20/h2qp_wan_metric payload fields.
    
    Configure WAN metrics.
    
    **Usage:**
        payload: H2qpWanMetricPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # WAN metric name.
    link_status: NotRequired[Literal[{"description": "Link up", "help": "Link up.", "label": "Up", "name": "up"}, {"description": "Link down", "help": "Link down.", "label": "Down", "name": "down"}, {"description": "Link in test state", "help": "Link in test state.", "label": "In Test", "name": "in-test"}]]  # Link status.
    symmetric_wan_link: NotRequired[Literal[{"description": "Symmetric WAN link (uplink and downlink speeds are the same)", "help": "Symmetric WAN link (uplink and downlink speeds are the same).", "label": "Symmetric", "name": "symmetric"}, {"description": "Asymmetric WAN link (uplink and downlink speeds are not the same)", "help": "Asymmetric WAN link (uplink and downlink speeds are not the same).", "label": "Asymmetric", "name": "asymmetric"}]]  # WAN link symmetry.
    link_at_capacity: NotRequired[Literal[{"description": "Link at capacity (not allow additional mobile devices to associate)", "help": "Link at capacity (not allow additional mobile devices to associate).", "label": "Enable", "name": "enable"}, {"description": "Link not at capacity (allow additional mobile devices to associate)", "help": "Link not at capacity (allow additional mobile devices to associate).", "label": "Disable", "name": "disable"}]]  # Link at capacity.
    uplink_speed: NotRequired[int]  # Uplink speed (in kilobits/s).
    downlink_speed: NotRequired[int]  # Downlink speed (in kilobits/s).
    uplink_load: NotRequired[int]  # Uplink load.
    downlink_load: NotRequired[int]  # Downlink load.
    load_measurement_duration: NotRequired[int]  # Load measurement duration (in tenths of a second).


class H2qpWanMetric:
    """
    Configure WAN metrics.
    
    Path: wireless_controller/hotspot20/h2qp_wan_metric
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
        payload_dict: H2qpWanMetricPayload | None = ...,
        name: str | None = ...,
        link_status: Literal[{"description": "Link up", "help": "Link up.", "label": "Up", "name": "up"}, {"description": "Link down", "help": "Link down.", "label": "Down", "name": "down"}, {"description": "Link in test state", "help": "Link in test state.", "label": "In Test", "name": "in-test"}] | None = ...,
        symmetric_wan_link: Literal[{"description": "Symmetric WAN link (uplink and downlink speeds are the same)", "help": "Symmetric WAN link (uplink and downlink speeds are the same).", "label": "Symmetric", "name": "symmetric"}, {"description": "Asymmetric WAN link (uplink and downlink speeds are not the same)", "help": "Asymmetric WAN link (uplink and downlink speeds are not the same).", "label": "Asymmetric", "name": "asymmetric"}] | None = ...,
        link_at_capacity: Literal[{"description": "Link at capacity (not allow additional mobile devices to associate)", "help": "Link at capacity (not allow additional mobile devices to associate).", "label": "Enable", "name": "enable"}, {"description": "Link not at capacity (allow additional mobile devices to associate)", "help": "Link not at capacity (allow additional mobile devices to associate).", "label": "Disable", "name": "disable"}] | None = ...,
        uplink_speed: int | None = ...,
        downlink_speed: int | None = ...,
        uplink_load: int | None = ...,
        downlink_load: int | None = ...,
        load_measurement_duration: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: H2qpWanMetricPayload | None = ...,
        name: str | None = ...,
        link_status: Literal[{"description": "Link up", "help": "Link up.", "label": "Up", "name": "up"}, {"description": "Link down", "help": "Link down.", "label": "Down", "name": "down"}, {"description": "Link in test state", "help": "Link in test state.", "label": "In Test", "name": "in-test"}] | None = ...,
        symmetric_wan_link: Literal[{"description": "Symmetric WAN link (uplink and downlink speeds are the same)", "help": "Symmetric WAN link (uplink and downlink speeds are the same).", "label": "Symmetric", "name": "symmetric"}, {"description": "Asymmetric WAN link (uplink and downlink speeds are not the same)", "help": "Asymmetric WAN link (uplink and downlink speeds are not the same).", "label": "Asymmetric", "name": "asymmetric"}] | None = ...,
        link_at_capacity: Literal[{"description": "Link at capacity (not allow additional mobile devices to associate)", "help": "Link at capacity (not allow additional mobile devices to associate).", "label": "Enable", "name": "enable"}, {"description": "Link not at capacity (allow additional mobile devices to associate)", "help": "Link not at capacity (allow additional mobile devices to associate).", "label": "Disable", "name": "disable"}] | None = ...,
        uplink_speed: int | None = ...,
        downlink_speed: int | None = ...,
        uplink_load: int | None = ...,
        downlink_load: int | None = ...,
        load_measurement_duration: int | None = ...,
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
        payload_dict: H2qpWanMetricPayload | None = ...,
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
    "H2qpWanMetric",
    "H2qpWanMetricPayload",
]