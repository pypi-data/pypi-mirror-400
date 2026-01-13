from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SyslogProfilePayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/syslog_profile payload fields.
    
    Configure Wireless Termination Points (WTP) system log server profile.
    
    **Usage:**
        payload: SyslogProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # WTP system log server profile name.
    comment: NotRequired[str]  # Comment.
    server_status: NotRequired[Literal[{"description": "Enable syslog server", "help": "Enable syslog server.", "label": "Enable", "name": "enable"}, {"description": "Disable syslog server", "help": "Disable syslog server.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiAP units to send log messages to a syslo
    server: NotRequired[str]  # Syslog server CN domain name or IP address.
    server_port: NotRequired[int]  # Port number of syslog server that FortiAP units send log mes
    server_type: NotRequired[Literal[{"description": "Standard syslog server hosted on an server endpoint", "help": "Standard syslog server hosted on an server endpoint.", "label": "Standard", "name": "standard"}, {"description": "Syslog server hosted on a FortiAnalyzer device", "help": "Syslog server hosted on a FortiAnalyzer device.", "label": "Fortianalyzer", "name": "fortianalyzer"}]]  # Configure syslog server type (default = standard).
    log_level: NotRequired[Literal[{"description": "Level 0    alert:Level 1    critical:Level 2    error:Level 3    warning:Level 4    notification:Level 5    information:Level 6    debugging:Level 7", "help": "Level 0", "label": "Emergency", "name": "emergency"}, {"help": "Level 1", "label": "Alert", "name": "alert"}, {"help": "Level 2", "label": "Critical", "name": "critical"}, {"help": "Level 3", "label": "Error", "name": "error"}, {"help": "Level 4", "label": "Warning", "name": "warning"}, {"help": "Level 5", "label": "Notification", "name": "notification"}, {"help": "Level 6", "label": "Information", "name": "information"}, {"help": "Level 7", "label": "Debugging", "name": "debugging"}]]  # Lowest level of log messages that FortiAP units send to this


class SyslogProfile:
    """
    Configure Wireless Termination Points (WTP) system log server profile.
    
    Path: wireless_controller/syslog_profile
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
        payload_dict: SyslogProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        server_status: Literal[{"description": "Enable syslog server", "help": "Enable syslog server.", "label": "Enable", "name": "enable"}, {"description": "Disable syslog server", "help": "Disable syslog server.", "label": "Disable", "name": "disable"}] | None = ...,
        server: str | None = ...,
        server_port: int | None = ...,
        server_type: Literal[{"description": "Standard syslog server hosted on an server endpoint", "help": "Standard syslog server hosted on an server endpoint.", "label": "Standard", "name": "standard"}, {"description": "Syslog server hosted on a FortiAnalyzer device", "help": "Syslog server hosted on a FortiAnalyzer device.", "label": "Fortianalyzer", "name": "fortianalyzer"}] | None = ...,
        log_level: Literal[{"description": "Level 0    alert:Level 1    critical:Level 2    error:Level 3    warning:Level 4    notification:Level 5    information:Level 6    debugging:Level 7", "help": "Level 0", "label": "Emergency", "name": "emergency"}, {"help": "Level 1", "label": "Alert", "name": "alert"}, {"help": "Level 2", "label": "Critical", "name": "critical"}, {"help": "Level 3", "label": "Error", "name": "error"}, {"help": "Level 4", "label": "Warning", "name": "warning"}, {"help": "Level 5", "label": "Notification", "name": "notification"}, {"help": "Level 6", "label": "Information", "name": "information"}, {"help": "Level 7", "label": "Debugging", "name": "debugging"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SyslogProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        server_status: Literal[{"description": "Enable syslog server", "help": "Enable syslog server.", "label": "Enable", "name": "enable"}, {"description": "Disable syslog server", "help": "Disable syslog server.", "label": "Disable", "name": "disable"}] | None = ...,
        server: str | None = ...,
        server_port: int | None = ...,
        server_type: Literal[{"description": "Standard syslog server hosted on an server endpoint", "help": "Standard syslog server hosted on an server endpoint.", "label": "Standard", "name": "standard"}, {"description": "Syslog server hosted on a FortiAnalyzer device", "help": "Syslog server hosted on a FortiAnalyzer device.", "label": "Fortianalyzer", "name": "fortianalyzer"}] | None = ...,
        log_level: Literal[{"description": "Level 0    alert:Level 1    critical:Level 2    error:Level 3    warning:Level 4    notification:Level 5    information:Level 6    debugging:Level 7", "help": "Level 0", "label": "Emergency", "name": "emergency"}, {"help": "Level 1", "label": "Alert", "name": "alert"}, {"help": "Level 2", "label": "Critical", "name": "critical"}, {"help": "Level 3", "label": "Error", "name": "error"}, {"help": "Level 4", "label": "Warning", "name": "warning"}, {"help": "Level 5", "label": "Notification", "name": "notification"}, {"help": "Level 6", "label": "Information", "name": "information"}, {"help": "Level 7", "label": "Debugging", "name": "debugging"}] | None = ...,
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
        payload_dict: SyslogProfilePayload | None = ...,
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
    "SyslogProfile",
    "SyslogProfilePayload",
]