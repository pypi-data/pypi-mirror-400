from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingPayload(TypedDict, total=False):
    """
    Type hints for report/setting payload fields.
    
    Report setting configuration.
    
    **Usage:**
        payload: SettingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    pdf_report: NotRequired[Literal[{"description": "Enable PDF report", "help": "Enable PDF report.", "label": "Enable", "name": "enable"}, {"description": "Disable PDF report", "help": "Disable PDF report.", "label": "Disable", "name": "disable"}]]  # Enable/disable PDF report.
    fortiview: NotRequired[Literal[{"description": "Enable historical FortiView", "help": "Enable historical FortiView.", "label": "Enable", "name": "enable"}, {"description": "Disable historical FortiView", "help": "Disable historical FortiView.", "label": "Disable", "name": "disable"}]]  # Enable/disable historical FortiView.
    report_source: NotRequired[Literal[{"description": "Report includes forward traffic logs", "help": "Report includes forward traffic logs.", "label": "Forward Traffic", "name": "forward-traffic"}, {"description": "Report includes sniffer traffic logs", "help": "Report includes sniffer traffic logs.", "label": "Sniffer Traffic", "name": "sniffer-traffic"}, {"description": "Report includes local deny traffic logs", "help": "Report includes local deny traffic logs.", "label": "Local Deny Traffic", "name": "local-deny-traffic"}]]  # Report log source.
    web_browsing_threshold: NotRequired[int]  # Web browsing time calculation threshold (3 - 15 min).
    top_n: NotRequired[int]  # Number of items to populate (1000 - 20000).


class Setting:
    """
    Report setting configuration.
    
    Path: report/setting
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
        payload_dict: SettingPayload | None = ...,
        pdf_report: Literal[{"description": "Enable PDF report", "help": "Enable PDF report.", "label": "Enable", "name": "enable"}, {"description": "Disable PDF report", "help": "Disable PDF report.", "label": "Disable", "name": "disable"}] | None = ...,
        fortiview: Literal[{"description": "Enable historical FortiView", "help": "Enable historical FortiView.", "label": "Enable", "name": "enable"}, {"description": "Disable historical FortiView", "help": "Disable historical FortiView.", "label": "Disable", "name": "disable"}] | None = ...,
        report_source: Literal[{"description": "Report includes forward traffic logs", "help": "Report includes forward traffic logs.", "label": "Forward Traffic", "name": "forward-traffic"}, {"description": "Report includes sniffer traffic logs", "help": "Report includes sniffer traffic logs.", "label": "Sniffer Traffic", "name": "sniffer-traffic"}, {"description": "Report includes local deny traffic logs", "help": "Report includes local deny traffic logs.", "label": "Local Deny Traffic", "name": "local-deny-traffic"}] | None = ...,
        web_browsing_threshold: int | None = ...,
        top_n: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SettingPayload | None = ...,
        pdf_report: Literal[{"description": "Enable PDF report", "help": "Enable PDF report.", "label": "Enable", "name": "enable"}, {"description": "Disable PDF report", "help": "Disable PDF report.", "label": "Disable", "name": "disable"}] | None = ...,
        fortiview: Literal[{"description": "Enable historical FortiView", "help": "Enable historical FortiView.", "label": "Enable", "name": "enable"}, {"description": "Disable historical FortiView", "help": "Disable historical FortiView.", "label": "Disable", "name": "disable"}] | None = ...,
        report_source: Literal[{"description": "Report includes forward traffic logs", "help": "Report includes forward traffic logs.", "label": "Forward Traffic", "name": "forward-traffic"}, {"description": "Report includes sniffer traffic logs", "help": "Report includes sniffer traffic logs.", "label": "Sniffer Traffic", "name": "sniffer-traffic"}, {"description": "Report includes local deny traffic logs", "help": "Report includes local deny traffic logs.", "label": "Local Deny Traffic", "name": "local-deny-traffic"}] | None = ...,
        web_browsing_threshold: int | None = ...,
        top_n: int | None = ...,
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
        payload_dict: SettingPayload | None = ...,
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
    "Setting",
    "SettingPayload",
]