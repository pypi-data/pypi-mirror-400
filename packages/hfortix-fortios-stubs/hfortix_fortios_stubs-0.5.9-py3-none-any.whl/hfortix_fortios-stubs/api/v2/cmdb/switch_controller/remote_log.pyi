from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class RemoteLogPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/remote_log payload fields.
    
    Configure logging by FortiSwitch device to a remote syslog server.
    
    **Usage:**
        payload: RemoteLogPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Remote log name.
    status: NotRequired[Literal[{"description": "Enable logging by FortiSwitch device to a remote syslog server", "help": "Enable logging by FortiSwitch device to a remote syslog server.", "label": "Enable", "name": "enable"}, {"description": "Disable logging by FortiSwitch device to a remote syslog server", "help": "Disable logging by FortiSwitch device to a remote syslog server.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging by FortiSwitch device to a remote sys
    server: str  # IPv4 address of the remote syslog server.
    port: NotRequired[int]  # Remote syslog server listening port.
    severity: NotRequired[Literal[{"description": "Emergency level", "help": "Emergency level.", "label": "Emergency", "name": "emergency"}, {"description": "Alert level", "help": "Alert level.", "label": "Alert", "name": "alert"}, {"description": "Critical level", "help": "Critical level.", "label": "Critical", "name": "critical"}, {"description": "Error level", "help": "Error level.", "label": "Error", "name": "error"}, {"description": "Warning level", "help": "Warning level.", "label": "Warning", "name": "warning"}, {"description": "Notification level", "help": "Notification level.", "label": "Notification", "name": "notification"}, {"description": "Information level", "help": "Information level.", "label": "Information", "name": "information"}, {"description": "Debug level", "help": "Debug level.", "label": "Debug", "name": "debug"}]]  # Severity of logs to be transferred to remote log server.
    csv: NotRequired[Literal[{"description": "Enable comma-separated value (CSV) strings", "help": "Enable comma-separated value (CSV) strings.", "label": "Enable", "name": "enable"}, {"description": "Disable comma-separated value (CSV) strings", "help": "Disable comma-separated value (CSV) strings.", "label": "Disable", "name": "disable"}]]  # Enable/disable comma-separated value (CSV) strings.
    facility: NotRequired[Literal[{"description": "Kernel messages", "help": "Kernel messages.", "label": "Kernel", "name": "kernel"}, {"description": "Random user-level messages", "help": "Random user-level messages.", "label": "User", "name": "user"}, {"description": "Mail system", "help": "Mail system.", "label": "Mail", "name": "mail"}, {"description": "System daemons", "help": "System daemons.", "label": "Daemon", "name": "daemon"}, {"description": "Security/authorization messages", "help": "Security/authorization messages.", "label": "Auth", "name": "auth"}, {"description": "Messages generated internally by syslogd", "help": "Messages generated internally by syslogd.", "label": "Syslog", "name": "syslog"}, {"description": "Line printer subsystem", "help": "Line printer subsystem.", "label": "Lpr", "name": "lpr"}, {"description": "Network news subsystem", "help": "Network news subsystem.", "label": "News", "name": "news"}, {"description": "UUCP server messages", "help": "UUCP server messages.", "label": "Uucp", "name": "uucp"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Cron", "name": "cron"}, {"description": "Security/authorization messages (private)", "help": "Security/authorization messages (private).", "label": "Authpriv", "name": "authpriv"}, {"description": "FTP daemon", "help": "FTP daemon.", "label": "Ftp", "name": "ftp"}, {"description": "NTP daemon", "help": "NTP daemon.", "label": "Ntp", "name": "ntp"}, {"description": "Log audit", "help": "Log audit.", "label": "Audit", "name": "audit"}, {"description": "Log alert", "help": "Log alert.", "label": "Alert", "name": "alert"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Clock", "name": "clock"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local0", "name": "local0"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local1", "name": "local1"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local2", "name": "local2"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local3", "name": "local3"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local4", "name": "local4"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local5", "name": "local5"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local6", "name": "local6"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local7", "name": "local7"}]]  # Facility to log to remote syslog server.


class RemoteLog:
    """
    Configure logging by FortiSwitch device to a remote syslog server.
    
    Path: switch_controller/remote_log
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
        payload_dict: RemoteLogPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Enable logging by FortiSwitch device to a remote syslog server", "help": "Enable logging by FortiSwitch device to a remote syslog server.", "label": "Enable", "name": "enable"}, {"description": "Disable logging by FortiSwitch device to a remote syslog server", "help": "Disable logging by FortiSwitch device to a remote syslog server.", "label": "Disable", "name": "disable"}] | None = ...,
        server: str | None = ...,
        port: int | None = ...,
        severity: Literal[{"description": "Emergency level", "help": "Emergency level.", "label": "Emergency", "name": "emergency"}, {"description": "Alert level", "help": "Alert level.", "label": "Alert", "name": "alert"}, {"description": "Critical level", "help": "Critical level.", "label": "Critical", "name": "critical"}, {"description": "Error level", "help": "Error level.", "label": "Error", "name": "error"}, {"description": "Warning level", "help": "Warning level.", "label": "Warning", "name": "warning"}, {"description": "Notification level", "help": "Notification level.", "label": "Notification", "name": "notification"}, {"description": "Information level", "help": "Information level.", "label": "Information", "name": "information"}, {"description": "Debug level", "help": "Debug level.", "label": "Debug", "name": "debug"}] | None = ...,
        csv: Literal[{"description": "Enable comma-separated value (CSV) strings", "help": "Enable comma-separated value (CSV) strings.", "label": "Enable", "name": "enable"}, {"description": "Disable comma-separated value (CSV) strings", "help": "Disable comma-separated value (CSV) strings.", "label": "Disable", "name": "disable"}] | None = ...,
        facility: Literal[{"description": "Kernel messages", "help": "Kernel messages.", "label": "Kernel", "name": "kernel"}, {"description": "Random user-level messages", "help": "Random user-level messages.", "label": "User", "name": "user"}, {"description": "Mail system", "help": "Mail system.", "label": "Mail", "name": "mail"}, {"description": "System daemons", "help": "System daemons.", "label": "Daemon", "name": "daemon"}, {"description": "Security/authorization messages", "help": "Security/authorization messages.", "label": "Auth", "name": "auth"}, {"description": "Messages generated internally by syslogd", "help": "Messages generated internally by syslogd.", "label": "Syslog", "name": "syslog"}, {"description": "Line printer subsystem", "help": "Line printer subsystem.", "label": "Lpr", "name": "lpr"}, {"description": "Network news subsystem", "help": "Network news subsystem.", "label": "News", "name": "news"}, {"description": "UUCP server messages", "help": "UUCP server messages.", "label": "Uucp", "name": "uucp"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Cron", "name": "cron"}, {"description": "Security/authorization messages (private)", "help": "Security/authorization messages (private).", "label": "Authpriv", "name": "authpriv"}, {"description": "FTP daemon", "help": "FTP daemon.", "label": "Ftp", "name": "ftp"}, {"description": "NTP daemon", "help": "NTP daemon.", "label": "Ntp", "name": "ntp"}, {"description": "Log audit", "help": "Log audit.", "label": "Audit", "name": "audit"}, {"description": "Log alert", "help": "Log alert.", "label": "Alert", "name": "alert"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Clock", "name": "clock"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local0", "name": "local0"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local1", "name": "local1"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local2", "name": "local2"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local3", "name": "local3"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local4", "name": "local4"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local5", "name": "local5"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local6", "name": "local6"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local7", "name": "local7"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: RemoteLogPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Enable logging by FortiSwitch device to a remote syslog server", "help": "Enable logging by FortiSwitch device to a remote syslog server.", "label": "Enable", "name": "enable"}, {"description": "Disable logging by FortiSwitch device to a remote syslog server", "help": "Disable logging by FortiSwitch device to a remote syslog server.", "label": "Disable", "name": "disable"}] | None = ...,
        server: str | None = ...,
        port: int | None = ...,
        severity: Literal[{"description": "Emergency level", "help": "Emergency level.", "label": "Emergency", "name": "emergency"}, {"description": "Alert level", "help": "Alert level.", "label": "Alert", "name": "alert"}, {"description": "Critical level", "help": "Critical level.", "label": "Critical", "name": "critical"}, {"description": "Error level", "help": "Error level.", "label": "Error", "name": "error"}, {"description": "Warning level", "help": "Warning level.", "label": "Warning", "name": "warning"}, {"description": "Notification level", "help": "Notification level.", "label": "Notification", "name": "notification"}, {"description": "Information level", "help": "Information level.", "label": "Information", "name": "information"}, {"description": "Debug level", "help": "Debug level.", "label": "Debug", "name": "debug"}] | None = ...,
        csv: Literal[{"description": "Enable comma-separated value (CSV) strings", "help": "Enable comma-separated value (CSV) strings.", "label": "Enable", "name": "enable"}, {"description": "Disable comma-separated value (CSV) strings", "help": "Disable comma-separated value (CSV) strings.", "label": "Disable", "name": "disable"}] | None = ...,
        facility: Literal[{"description": "Kernel messages", "help": "Kernel messages.", "label": "Kernel", "name": "kernel"}, {"description": "Random user-level messages", "help": "Random user-level messages.", "label": "User", "name": "user"}, {"description": "Mail system", "help": "Mail system.", "label": "Mail", "name": "mail"}, {"description": "System daemons", "help": "System daemons.", "label": "Daemon", "name": "daemon"}, {"description": "Security/authorization messages", "help": "Security/authorization messages.", "label": "Auth", "name": "auth"}, {"description": "Messages generated internally by syslogd", "help": "Messages generated internally by syslogd.", "label": "Syslog", "name": "syslog"}, {"description": "Line printer subsystem", "help": "Line printer subsystem.", "label": "Lpr", "name": "lpr"}, {"description": "Network news subsystem", "help": "Network news subsystem.", "label": "News", "name": "news"}, {"description": "UUCP server messages", "help": "UUCP server messages.", "label": "Uucp", "name": "uucp"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Cron", "name": "cron"}, {"description": "Security/authorization messages (private)", "help": "Security/authorization messages (private).", "label": "Authpriv", "name": "authpriv"}, {"description": "FTP daemon", "help": "FTP daemon.", "label": "Ftp", "name": "ftp"}, {"description": "NTP daemon", "help": "NTP daemon.", "label": "Ntp", "name": "ntp"}, {"description": "Log audit", "help": "Log audit.", "label": "Audit", "name": "audit"}, {"description": "Log alert", "help": "Log alert.", "label": "Alert", "name": "alert"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Clock", "name": "clock"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local0", "name": "local0"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local1", "name": "local1"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local2", "name": "local2"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local3", "name": "local3"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local4", "name": "local4"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local5", "name": "local5"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local6", "name": "local6"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local7", "name": "local7"}] | None = ...,
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
        payload_dict: RemoteLogPayload | None = ...,
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
    "RemoteLog",
    "RemoteLogPayload",
]