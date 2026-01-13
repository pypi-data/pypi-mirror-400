from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class FilterPayload(TypedDict, total=False):
    """
    Type hints for log/syslogd3/filter payload fields.
    
    Filters for remote system server.
    
    **Usage:**
        payload: FilterPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    severity: NotRequired[Literal[{"description": "Emergency level", "help": "Emergency level.", "label": "Emergency", "name": "emergency"}, {"description": "Alert level", "help": "Alert level.", "label": "Alert", "name": "alert"}, {"description": "Critical level", "help": "Critical level.", "label": "Critical", "name": "critical"}, {"description": "Error level", "help": "Error level.", "label": "Error", "name": "error"}, {"description": "Warning level", "help": "Warning level.", "label": "Warning", "name": "warning"}, {"description": "Notification level", "help": "Notification level.", "label": "Notification", "name": "notification"}, {"description": "Information level", "help": "Information level.", "label": "Information", "name": "information"}, {"description": "Debug level", "help": "Debug level.", "label": "Debug", "name": "debug"}]]  # Lowest severity level to log.
    forward_traffic: NotRequired[Literal[{"description": "Enable forward traffic logging", "help": "Enable forward traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable forward traffic logging", "help": "Disable forward traffic logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable forward traffic logging.
    local_traffic: NotRequired[Literal[{"description": "Enable local in or out traffic logging", "help": "Enable local in or out traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local in or out traffic logging", "help": "Disable local in or out traffic logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable local in or out traffic logging.
    multicast_traffic: NotRequired[Literal[{"description": "Enable multicast traffic logging", "help": "Enable multicast traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable multicast traffic logging", "help": "Disable multicast traffic logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable multicast traffic logging.
    sniffer_traffic: NotRequired[Literal[{"description": "Enable sniffer traffic logging", "help": "Enable sniffer traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable sniffer traffic logging", "help": "Disable sniffer traffic logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable sniffer traffic logging.
    ztna_traffic: NotRequired[Literal[{"description": "Enable ztna traffic logging", "help": "Enable ztna traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable ztna traffic logging", "help": "Disable ztna traffic logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable ztna traffic logging.
    http_transaction: NotRequired[Literal[{"description": "Enable http transaction logging", "help": "Enable http transaction logging.", "label": "Enable", "name": "enable"}, {"description": "Disable http transaction logging", "help": "Disable http transaction logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable log HTTP transaction messages.
    anomaly: NotRequired[Literal[{"description": "Enable anomaly logging", "help": "Enable anomaly logging.", "label": "Enable", "name": "enable"}, {"description": "Disable anomaly logging", "help": "Disable anomaly logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable anomaly logging.
    voip: NotRequired[Literal[{"description": "Enable VoIP logging", "help": "Enable VoIP logging.", "label": "Enable", "name": "enable"}, {"description": "Disable VoIP logging", "help": "Disable VoIP logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable VoIP logging.
    gtp: NotRequired[Literal[{"help": "Enable GTP messages logging.", "label": "Enable", "name": "enable"}, {"help": "Disable GTP messages logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable GTP messages logging.
    forti_switch: NotRequired[Literal[{"description": "Enable Forti-Switch logging", "help": "Enable Forti-Switch logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Forti-Switch logging", "help": "Disable Forti-Switch logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable Forti-Switch logging.
    debug: NotRequired[Literal[{"description": "Enable Debug logging", "help": "Enable Debug logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Debug logging", "help": "Disable Debug logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable debug logging.
    free_style: NotRequired[list[dict[str, Any]]]  # Free style filters.


class Filter:
    """
    Filters for remote system server.
    
    Path: log/syslogd3/filter
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
        payload_dict: FilterPayload | None = ...,
        severity: Literal[{"description": "Emergency level", "help": "Emergency level.", "label": "Emergency", "name": "emergency"}, {"description": "Alert level", "help": "Alert level.", "label": "Alert", "name": "alert"}, {"description": "Critical level", "help": "Critical level.", "label": "Critical", "name": "critical"}, {"description": "Error level", "help": "Error level.", "label": "Error", "name": "error"}, {"description": "Warning level", "help": "Warning level.", "label": "Warning", "name": "warning"}, {"description": "Notification level", "help": "Notification level.", "label": "Notification", "name": "notification"}, {"description": "Information level", "help": "Information level.", "label": "Information", "name": "information"}, {"description": "Debug level", "help": "Debug level.", "label": "Debug", "name": "debug"}] | None = ...,
        forward_traffic: Literal[{"description": "Enable forward traffic logging", "help": "Enable forward traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable forward traffic logging", "help": "Disable forward traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_traffic: Literal[{"description": "Enable local in or out traffic logging", "help": "Enable local in or out traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local in or out traffic logging", "help": "Disable local in or out traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        multicast_traffic: Literal[{"description": "Enable multicast traffic logging", "help": "Enable multicast traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable multicast traffic logging", "help": "Disable multicast traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        sniffer_traffic: Literal[{"description": "Enable sniffer traffic logging", "help": "Enable sniffer traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable sniffer traffic logging", "help": "Disable sniffer traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        ztna_traffic: Literal[{"description": "Enable ztna traffic logging", "help": "Enable ztna traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable ztna traffic logging", "help": "Disable ztna traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        http_transaction: Literal[{"description": "Enable http transaction logging", "help": "Enable http transaction logging.", "label": "Enable", "name": "enable"}, {"description": "Disable http transaction logging", "help": "Disable http transaction logging.", "label": "Disable", "name": "disable"}] | None = ...,
        anomaly: Literal[{"description": "Enable anomaly logging", "help": "Enable anomaly logging.", "label": "Enable", "name": "enable"}, {"description": "Disable anomaly logging", "help": "Disable anomaly logging.", "label": "Disable", "name": "disable"}] | None = ...,
        voip: Literal[{"description": "Enable VoIP logging", "help": "Enable VoIP logging.", "label": "Enable", "name": "enable"}, {"description": "Disable VoIP logging", "help": "Disable VoIP logging.", "label": "Disable", "name": "disable"}] | None = ...,
        gtp: Literal[{"help": "Enable GTP messages logging.", "label": "Enable", "name": "enable"}, {"help": "Disable GTP messages logging.", "label": "Disable", "name": "disable"}] | None = ...,
        forti_switch: Literal[{"description": "Enable Forti-Switch logging", "help": "Enable Forti-Switch logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Forti-Switch logging", "help": "Disable Forti-Switch logging.", "label": "Disable", "name": "disable"}] | None = ...,
        debug: Literal[{"description": "Enable Debug logging", "help": "Enable Debug logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Debug logging", "help": "Disable Debug logging.", "label": "Disable", "name": "disable"}] | None = ...,
        free_style: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: FilterPayload | None = ...,
        severity: Literal[{"description": "Emergency level", "help": "Emergency level.", "label": "Emergency", "name": "emergency"}, {"description": "Alert level", "help": "Alert level.", "label": "Alert", "name": "alert"}, {"description": "Critical level", "help": "Critical level.", "label": "Critical", "name": "critical"}, {"description": "Error level", "help": "Error level.", "label": "Error", "name": "error"}, {"description": "Warning level", "help": "Warning level.", "label": "Warning", "name": "warning"}, {"description": "Notification level", "help": "Notification level.", "label": "Notification", "name": "notification"}, {"description": "Information level", "help": "Information level.", "label": "Information", "name": "information"}, {"description": "Debug level", "help": "Debug level.", "label": "Debug", "name": "debug"}] | None = ...,
        forward_traffic: Literal[{"description": "Enable forward traffic logging", "help": "Enable forward traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable forward traffic logging", "help": "Disable forward traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_traffic: Literal[{"description": "Enable local in or out traffic logging", "help": "Enable local in or out traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local in or out traffic logging", "help": "Disable local in or out traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        multicast_traffic: Literal[{"description": "Enable multicast traffic logging", "help": "Enable multicast traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable multicast traffic logging", "help": "Disable multicast traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        sniffer_traffic: Literal[{"description": "Enable sniffer traffic logging", "help": "Enable sniffer traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable sniffer traffic logging", "help": "Disable sniffer traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        ztna_traffic: Literal[{"description": "Enable ztna traffic logging", "help": "Enable ztna traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable ztna traffic logging", "help": "Disable ztna traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        http_transaction: Literal[{"description": "Enable http transaction logging", "help": "Enable http transaction logging.", "label": "Enable", "name": "enable"}, {"description": "Disable http transaction logging", "help": "Disable http transaction logging.", "label": "Disable", "name": "disable"}] | None = ...,
        anomaly: Literal[{"description": "Enable anomaly logging", "help": "Enable anomaly logging.", "label": "Enable", "name": "enable"}, {"description": "Disable anomaly logging", "help": "Disable anomaly logging.", "label": "Disable", "name": "disable"}] | None = ...,
        voip: Literal[{"description": "Enable VoIP logging", "help": "Enable VoIP logging.", "label": "Enable", "name": "enable"}, {"description": "Disable VoIP logging", "help": "Disable VoIP logging.", "label": "Disable", "name": "disable"}] | None = ...,
        gtp: Literal[{"help": "Enable GTP messages logging.", "label": "Enable", "name": "enable"}, {"help": "Disable GTP messages logging.", "label": "Disable", "name": "disable"}] | None = ...,
        forti_switch: Literal[{"description": "Enable Forti-Switch logging", "help": "Enable Forti-Switch logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Forti-Switch logging", "help": "Disable Forti-Switch logging.", "label": "Disable", "name": "disable"}] | None = ...,
        debug: Literal[{"description": "Enable Debug logging", "help": "Enable Debug logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Debug logging", "help": "Disable Debug logging.", "label": "Disable", "name": "disable"}] | None = ...,
        free_style: list[dict[str, Any]] | None = ...,
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
        payload_dict: FilterPayload | None = ...,
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
    "Filter",
    "FilterPayload",
]