from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ThreatWeightPayload(TypedDict, total=False):
    """
    Type hints for log/threat_weight payload fields.
    
    Configure threat weight settings.
    
    **Usage:**
        payload: ThreatWeightPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: NotRequired[Literal[{"description": "Enable the threat weight feature", "help": "Enable the threat weight feature.", "label": "Enable", "name": "enable"}, {"description": "Disable the threat weight feature", "help": "Disable the threat weight feature.", "label": "Disable", "name": "disable"}]]  # Enable/disable the threat weight feature.
    level: NotRequired[str]  # Score mapping for threat weight levels.
    blocked_connection: NotRequired[Literal[{"description": "Disable threat weight scoring for blocked connections", "help": "Disable threat weight scoring for blocked connections.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for blocked connections", "help": "Use the low level score for blocked connections.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for blocked connections", "help": "Use the medium level score for blocked connections.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for blocked connections", "help": "Use the high level score for blocked connections.", "label": "High", "name": "high"}, {"description": "Use the critical level score for blocked connections", "help": "Use the critical level score for blocked connections.", "label": "Critical", "name": "critical"}]]  # Threat weight score for blocked connections.
    failed_connection: NotRequired[Literal[{"description": "Disable threat weight scoring for failed connections", "help": "Disable threat weight scoring for failed connections.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for failed connections", "help": "Use the low level score for failed connections.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for failed connections", "help": "Use the medium level score for failed connections.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for failed connections", "help": "Use the high level score for failed connections.", "label": "High", "name": "high"}, {"description": "Use the critical level score for failed connections", "help": "Use the critical level score for failed connections.", "label": "Critical", "name": "critical"}]]  # Threat weight score for failed connections.
    url_block_detected: NotRequired[Literal[{"description": "Disable threat weight scoring for URL blocking", "help": "Disable threat weight scoring for URL blocking.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for URL blocking", "help": "Use the low level score for URL blocking.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for URL blocking", "help": "Use the medium level score for URL blocking.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for URL blocking", "help": "Use the high level score for URL blocking.", "label": "High", "name": "high"}, {"description": "Use the critical level score for URL blocking", "help": "Use the critical level score for URL blocking.", "label": "Critical", "name": "critical"}]]  # Threat weight score for URL blocking.
    botnet_connection_detected: NotRequired[Literal[{"description": "Disable threat weight scoring for detected botnet connections", "help": "Disable threat weight scoring for detected botnet connections.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for detected botnet connections", "help": "Use the low level score for detected botnet connections.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for detected botnet connections", "help": "Use the medium level score for detected botnet connections.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for detected botnet connections", "help": "Use the high level score for detected botnet connections.", "label": "High", "name": "high"}, {"description": "Use the critical level score for detected botnet connections", "help": "Use the critical level score for detected botnet connections.", "label": "Critical", "name": "critical"}]]  # Threat weight score for detected botnet connections.
    malware: NotRequired[str]  # Anti-virus malware threat weight settings.
    ips: NotRequired[str]  # IPS threat weight settings.
    web: NotRequired[list[dict[str, Any]]]  # Web filtering threat weight settings.
    geolocation: NotRequired[list[dict[str, Any]]]  # Geolocation-based threat weight settings.
    application: NotRequired[list[dict[str, Any]]]  # Application-control threat weight settings.


class ThreatWeight:
    """
    Configure threat weight settings.
    
    Path: log/threat_weight
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
        payload_dict: ThreatWeightPayload | None = ...,
        status: Literal[{"description": "Enable the threat weight feature", "help": "Enable the threat weight feature.", "label": "Enable", "name": "enable"}, {"description": "Disable the threat weight feature", "help": "Disable the threat weight feature.", "label": "Disable", "name": "disable"}] | None = ...,
        level: str | None = ...,
        blocked_connection: Literal[{"description": "Disable threat weight scoring for blocked connections", "help": "Disable threat weight scoring for blocked connections.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for blocked connections", "help": "Use the low level score for blocked connections.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for blocked connections", "help": "Use the medium level score for blocked connections.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for blocked connections", "help": "Use the high level score for blocked connections.", "label": "High", "name": "high"}, {"description": "Use the critical level score for blocked connections", "help": "Use the critical level score for blocked connections.", "label": "Critical", "name": "critical"}] | None = ...,
        failed_connection: Literal[{"description": "Disable threat weight scoring for failed connections", "help": "Disable threat weight scoring for failed connections.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for failed connections", "help": "Use the low level score for failed connections.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for failed connections", "help": "Use the medium level score for failed connections.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for failed connections", "help": "Use the high level score for failed connections.", "label": "High", "name": "high"}, {"description": "Use the critical level score for failed connections", "help": "Use the critical level score for failed connections.", "label": "Critical", "name": "critical"}] | None = ...,
        url_block_detected: Literal[{"description": "Disable threat weight scoring for URL blocking", "help": "Disable threat weight scoring for URL blocking.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for URL blocking", "help": "Use the low level score for URL blocking.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for URL blocking", "help": "Use the medium level score for URL blocking.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for URL blocking", "help": "Use the high level score for URL blocking.", "label": "High", "name": "high"}, {"description": "Use the critical level score for URL blocking", "help": "Use the critical level score for URL blocking.", "label": "Critical", "name": "critical"}] | None = ...,
        botnet_connection_detected: Literal[{"description": "Disable threat weight scoring for detected botnet connections", "help": "Disable threat weight scoring for detected botnet connections.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for detected botnet connections", "help": "Use the low level score for detected botnet connections.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for detected botnet connections", "help": "Use the medium level score for detected botnet connections.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for detected botnet connections", "help": "Use the high level score for detected botnet connections.", "label": "High", "name": "high"}, {"description": "Use the critical level score for detected botnet connections", "help": "Use the critical level score for detected botnet connections.", "label": "Critical", "name": "critical"}] | None = ...,
        malware: str | None = ...,
        ips: str | None = ...,
        web: list[dict[str, Any]] | None = ...,
        geolocation: list[dict[str, Any]] | None = ...,
        application: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ThreatWeightPayload | None = ...,
        status: Literal[{"description": "Enable the threat weight feature", "help": "Enable the threat weight feature.", "label": "Enable", "name": "enable"}, {"description": "Disable the threat weight feature", "help": "Disable the threat weight feature.", "label": "Disable", "name": "disable"}] | None = ...,
        level: str | None = ...,
        blocked_connection: Literal[{"description": "Disable threat weight scoring for blocked connections", "help": "Disable threat weight scoring for blocked connections.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for blocked connections", "help": "Use the low level score for blocked connections.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for blocked connections", "help": "Use the medium level score for blocked connections.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for blocked connections", "help": "Use the high level score for blocked connections.", "label": "High", "name": "high"}, {"description": "Use the critical level score for blocked connections", "help": "Use the critical level score for blocked connections.", "label": "Critical", "name": "critical"}] | None = ...,
        failed_connection: Literal[{"description": "Disable threat weight scoring for failed connections", "help": "Disable threat weight scoring for failed connections.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for failed connections", "help": "Use the low level score for failed connections.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for failed connections", "help": "Use the medium level score for failed connections.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for failed connections", "help": "Use the high level score for failed connections.", "label": "High", "name": "high"}, {"description": "Use the critical level score for failed connections", "help": "Use the critical level score for failed connections.", "label": "Critical", "name": "critical"}] | None = ...,
        url_block_detected: Literal[{"description": "Disable threat weight scoring for URL blocking", "help": "Disable threat weight scoring for URL blocking.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for URL blocking", "help": "Use the low level score for URL blocking.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for URL blocking", "help": "Use the medium level score for URL blocking.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for URL blocking", "help": "Use the high level score for URL blocking.", "label": "High", "name": "high"}, {"description": "Use the critical level score for URL blocking", "help": "Use the critical level score for URL blocking.", "label": "Critical", "name": "critical"}] | None = ...,
        botnet_connection_detected: Literal[{"description": "Disable threat weight scoring for detected botnet connections", "help": "Disable threat weight scoring for detected botnet connections.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for detected botnet connections", "help": "Use the low level score for detected botnet connections.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for detected botnet connections", "help": "Use the medium level score for detected botnet connections.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for detected botnet connections", "help": "Use the high level score for detected botnet connections.", "label": "High", "name": "high"}, {"description": "Use the critical level score for detected botnet connections", "help": "Use the critical level score for detected botnet connections.", "label": "Critical", "name": "critical"}] | None = ...,
        malware: str | None = ...,
        ips: str | None = ...,
        web: list[dict[str, Any]] | None = ...,
        geolocation: list[dict[str, Any]] | None = ...,
        application: list[dict[str, Any]] | None = ...,
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
        payload_dict: ThreatWeightPayload | None = ...,
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
    "ThreatWeight",
    "ThreatWeightPayload",
]