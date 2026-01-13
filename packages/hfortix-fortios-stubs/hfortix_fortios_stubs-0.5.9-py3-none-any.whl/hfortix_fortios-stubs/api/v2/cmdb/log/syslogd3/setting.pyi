from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingPayload(TypedDict, total=False):
    """
    Type hints for log/syslogd3/setting payload fields.
    
    Global settings for remote syslog server.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.local.LocalEndpoint` (via: certificate)
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface, source-ip-interface)

    **Usage:**
        payload: SettingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: NotRequired[Literal[{"description": "Log to remote syslog server", "help": "Log to remote syslog server.", "label": "Enable", "name": "enable"}, {"description": "Do not log to remote syslog server", "help": "Do not log to remote syslog server.", "label": "Disable", "name": "disable"}]]  # Enable/disable remote syslog logging.
    server: str  # Address of remote syslog server.
    mode: NotRequired[Literal[{"description": "Enable syslogging over UDP", "help": "Enable syslogging over UDP.", "label": "Udp", "name": "udp"}, {"description": "Enable legacy reliable syslogging by RFC3195 (Reliable Delivery for Syslog)", "help": "Enable legacy reliable syslogging by RFC3195 (Reliable Delivery for Syslog).", "label": "Legacy Reliable", "name": "legacy-reliable"}, {"description": "Enable reliable syslogging by RFC6587 (Transmission of Syslog Messages over TCP)", "help": "Enable reliable syslogging by RFC6587 (Transmission of Syslog Messages over TCP).", "label": "Reliable", "name": "reliable"}]]  # Remote syslog logging over UDP/Reliable TCP.
    port: NotRequired[int]  # Server listen port.
    facility: NotRequired[Literal[{"description": "Kernel messages", "help": "Kernel messages.", "label": "Kernel", "name": "kernel"}, {"description": "Random user-level messages", "help": "Random user-level messages.", "label": "User", "name": "user"}, {"description": "Mail system", "help": "Mail system.", "label": "Mail", "name": "mail"}, {"description": "System daemons", "help": "System daemons.", "label": "Daemon", "name": "daemon"}, {"description": "Security/authorization messages", "help": "Security/authorization messages.", "label": "Auth", "name": "auth"}, {"description": "Messages generated internally by syslog", "help": "Messages generated internally by syslog.", "label": "Syslog", "name": "syslog"}, {"description": "Line printer subsystem", "help": "Line printer subsystem.", "label": "Lpr", "name": "lpr"}, {"description": "Network news subsystem", "help": "Network news subsystem.", "label": "News", "name": "news"}, {"description": "Network news subsystem", "help": "Network news subsystem.", "label": "Uucp", "name": "uucp"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Cron", "name": "cron"}, {"description": "Security/authorization messages (private)", "help": "Security/authorization messages (private).", "label": "Authpriv", "name": "authpriv"}, {"description": "FTP daemon", "help": "FTP daemon.", "label": "Ftp", "name": "ftp"}, {"description": "NTP daemon", "help": "NTP daemon.", "label": "Ntp", "name": "ntp"}, {"description": "Log audit", "help": "Log audit.", "label": "Audit", "name": "audit"}, {"description": "Log alert", "help": "Log alert.", "label": "Alert", "name": "alert"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Clock", "name": "clock"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local0", "name": "local0"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local1", "name": "local1"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local2", "name": "local2"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local3", "name": "local3"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local4", "name": "local4"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local5", "name": "local5"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local6", "name": "local6"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local7", "name": "local7"}]]  # Remote syslog facility.
    source_ip_interface: NotRequired[str]  # Source interface of syslog.
    source_ip: NotRequired[str]  # Source IP address of syslog.
    format: NotRequired[Literal[{"description": "Syslog format", "help": "Syslog format.", "label": "Default", "name": "default"}, {"description": "CSV (Comma Separated Values) format", "help": "CSV (Comma Separated Values) format.", "label": "Csv", "name": "csv"}, {"description": "CEF (Common Event Format) format", "help": "CEF (Common Event Format) format.", "label": "Cef", "name": "cef"}, {"description": "Syslog RFC5424 format", "help": "Syslog RFC5424 format.", "label": "Rfc5424", "name": "rfc5424"}, {"description": "JSON (JavaScript Object Notation) format", "help": "JSON (JavaScript Object Notation) format.", "label": "Json", "name": "json"}]]  # Log format.
    priority: NotRequired[Literal[{"description": "Set Syslog transmission priority to default", "help": "Set Syslog transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set Syslog transmission priority to low", "help": "Set Syslog transmission priority to low.", "label": "Low", "name": "low"}]]  # Set log transmission priority.
    max_log_rate: NotRequired[int]  # Syslog maximum log rate in MBps (0 = unlimited).
    enc_algorithm: NotRequired[Literal[{"description": "SSL communication with high and medium encryption algorithms", "help": "SSL communication with high and medium encryption algorithms.", "label": "High Medium", "name": "high-medium"}, {"description": "SSL communication with high encryption algorithms", "help": "SSL communication with high encryption algorithms.", "label": "High", "name": "high"}, {"description": "SSL communication with low encryption algorithms", "help": "SSL communication with low encryption algorithms.", "label": "Low", "name": "low"}, {"description": "Disable SSL communication", "help": "Disable SSL communication.", "label": "Disable", "name": "disable"}]]  # Enable/disable reliable syslogging with TLS encryption.
    ssl_min_proto_version: NotRequired[Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]]  # Minimum supported protocol version for SSL/TLS connections (
    certificate: NotRequired[str]  # Certificate used to communicate with Syslog server.
    custom_field_name: NotRequired[list[dict[str, Any]]]  # Custom field name for CEF format logging.
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.


class Setting:
    """
    Global settings for remote syslog server.
    
    Path: log/syslogd3/setting
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
        status: Literal[{"description": "Log to remote syslog server", "help": "Log to remote syslog server.", "label": "Enable", "name": "enable"}, {"description": "Do not log to remote syslog server", "help": "Do not log to remote syslog server.", "label": "Disable", "name": "disable"}] | None = ...,
        server: str | None = ...,
        mode: Literal[{"description": "Enable syslogging over UDP", "help": "Enable syslogging over UDP.", "label": "Udp", "name": "udp"}, {"description": "Enable legacy reliable syslogging by RFC3195 (Reliable Delivery for Syslog)", "help": "Enable legacy reliable syslogging by RFC3195 (Reliable Delivery for Syslog).", "label": "Legacy Reliable", "name": "legacy-reliable"}, {"description": "Enable reliable syslogging by RFC6587 (Transmission of Syslog Messages over TCP)", "help": "Enable reliable syslogging by RFC6587 (Transmission of Syslog Messages over TCP).", "label": "Reliable", "name": "reliable"}] | None = ...,
        port: int | None = ...,
        facility: Literal[{"description": "Kernel messages", "help": "Kernel messages.", "label": "Kernel", "name": "kernel"}, {"description": "Random user-level messages", "help": "Random user-level messages.", "label": "User", "name": "user"}, {"description": "Mail system", "help": "Mail system.", "label": "Mail", "name": "mail"}, {"description": "System daemons", "help": "System daemons.", "label": "Daemon", "name": "daemon"}, {"description": "Security/authorization messages", "help": "Security/authorization messages.", "label": "Auth", "name": "auth"}, {"description": "Messages generated internally by syslog", "help": "Messages generated internally by syslog.", "label": "Syslog", "name": "syslog"}, {"description": "Line printer subsystem", "help": "Line printer subsystem.", "label": "Lpr", "name": "lpr"}, {"description": "Network news subsystem", "help": "Network news subsystem.", "label": "News", "name": "news"}, {"description": "Network news subsystem", "help": "Network news subsystem.", "label": "Uucp", "name": "uucp"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Cron", "name": "cron"}, {"description": "Security/authorization messages (private)", "help": "Security/authorization messages (private).", "label": "Authpriv", "name": "authpriv"}, {"description": "FTP daemon", "help": "FTP daemon.", "label": "Ftp", "name": "ftp"}, {"description": "NTP daemon", "help": "NTP daemon.", "label": "Ntp", "name": "ntp"}, {"description": "Log audit", "help": "Log audit.", "label": "Audit", "name": "audit"}, {"description": "Log alert", "help": "Log alert.", "label": "Alert", "name": "alert"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Clock", "name": "clock"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local0", "name": "local0"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local1", "name": "local1"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local2", "name": "local2"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local3", "name": "local3"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local4", "name": "local4"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local5", "name": "local5"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local6", "name": "local6"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local7", "name": "local7"}] | None = ...,
        source_ip_interface: str | None = ...,
        source_ip: str | None = ...,
        format: Literal[{"description": "Syslog format", "help": "Syslog format.", "label": "Default", "name": "default"}, {"description": "CSV (Comma Separated Values) format", "help": "CSV (Comma Separated Values) format.", "label": "Csv", "name": "csv"}, {"description": "CEF (Common Event Format) format", "help": "CEF (Common Event Format) format.", "label": "Cef", "name": "cef"}, {"description": "Syslog RFC5424 format", "help": "Syslog RFC5424 format.", "label": "Rfc5424", "name": "rfc5424"}, {"description": "JSON (JavaScript Object Notation) format", "help": "JSON (JavaScript Object Notation) format.", "label": "Json", "name": "json"}] | None = ...,
        priority: Literal[{"description": "Set Syslog transmission priority to default", "help": "Set Syslog transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set Syslog transmission priority to low", "help": "Set Syslog transmission priority to low.", "label": "Low", "name": "low"}] | None = ...,
        max_log_rate: int | None = ...,
        enc_algorithm: Literal[{"description": "SSL communication with high and medium encryption algorithms", "help": "SSL communication with high and medium encryption algorithms.", "label": "High Medium", "name": "high-medium"}, {"description": "SSL communication with high encryption algorithms", "help": "SSL communication with high encryption algorithms.", "label": "High", "name": "high"}, {"description": "SSL communication with low encryption algorithms", "help": "SSL communication with low encryption algorithms.", "label": "Low", "name": "low"}, {"description": "Disable SSL communication", "help": "Disable SSL communication.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        certificate: str | None = ...,
        custom_field_name: list[dict[str, Any]] | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SettingPayload | None = ...,
        status: Literal[{"description": "Log to remote syslog server", "help": "Log to remote syslog server.", "label": "Enable", "name": "enable"}, {"description": "Do not log to remote syslog server", "help": "Do not log to remote syslog server.", "label": "Disable", "name": "disable"}] | None = ...,
        server: str | None = ...,
        mode: Literal[{"description": "Enable syslogging over UDP", "help": "Enable syslogging over UDP.", "label": "Udp", "name": "udp"}, {"description": "Enable legacy reliable syslogging by RFC3195 (Reliable Delivery for Syslog)", "help": "Enable legacy reliable syslogging by RFC3195 (Reliable Delivery for Syslog).", "label": "Legacy Reliable", "name": "legacy-reliable"}, {"description": "Enable reliable syslogging by RFC6587 (Transmission of Syslog Messages over TCP)", "help": "Enable reliable syslogging by RFC6587 (Transmission of Syslog Messages over TCP).", "label": "Reliable", "name": "reliable"}] | None = ...,
        port: int | None = ...,
        facility: Literal[{"description": "Kernel messages", "help": "Kernel messages.", "label": "Kernel", "name": "kernel"}, {"description": "Random user-level messages", "help": "Random user-level messages.", "label": "User", "name": "user"}, {"description": "Mail system", "help": "Mail system.", "label": "Mail", "name": "mail"}, {"description": "System daemons", "help": "System daemons.", "label": "Daemon", "name": "daemon"}, {"description": "Security/authorization messages", "help": "Security/authorization messages.", "label": "Auth", "name": "auth"}, {"description": "Messages generated internally by syslog", "help": "Messages generated internally by syslog.", "label": "Syslog", "name": "syslog"}, {"description": "Line printer subsystem", "help": "Line printer subsystem.", "label": "Lpr", "name": "lpr"}, {"description": "Network news subsystem", "help": "Network news subsystem.", "label": "News", "name": "news"}, {"description": "Network news subsystem", "help": "Network news subsystem.", "label": "Uucp", "name": "uucp"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Cron", "name": "cron"}, {"description": "Security/authorization messages (private)", "help": "Security/authorization messages (private).", "label": "Authpriv", "name": "authpriv"}, {"description": "FTP daemon", "help": "FTP daemon.", "label": "Ftp", "name": "ftp"}, {"description": "NTP daemon", "help": "NTP daemon.", "label": "Ntp", "name": "ntp"}, {"description": "Log audit", "help": "Log audit.", "label": "Audit", "name": "audit"}, {"description": "Log alert", "help": "Log alert.", "label": "Alert", "name": "alert"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Clock", "name": "clock"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local0", "name": "local0"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local1", "name": "local1"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local2", "name": "local2"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local3", "name": "local3"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local4", "name": "local4"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local5", "name": "local5"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local6", "name": "local6"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local7", "name": "local7"}] | None = ...,
        source_ip_interface: str | None = ...,
        source_ip: str | None = ...,
        format: Literal[{"description": "Syslog format", "help": "Syslog format.", "label": "Default", "name": "default"}, {"description": "CSV (Comma Separated Values) format", "help": "CSV (Comma Separated Values) format.", "label": "Csv", "name": "csv"}, {"description": "CEF (Common Event Format) format", "help": "CEF (Common Event Format) format.", "label": "Cef", "name": "cef"}, {"description": "Syslog RFC5424 format", "help": "Syslog RFC5424 format.", "label": "Rfc5424", "name": "rfc5424"}, {"description": "JSON (JavaScript Object Notation) format", "help": "JSON (JavaScript Object Notation) format.", "label": "Json", "name": "json"}] | None = ...,
        priority: Literal[{"description": "Set Syslog transmission priority to default", "help": "Set Syslog transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set Syslog transmission priority to low", "help": "Set Syslog transmission priority to low.", "label": "Low", "name": "low"}] | None = ...,
        max_log_rate: int | None = ...,
        enc_algorithm: Literal[{"description": "SSL communication with high and medium encryption algorithms", "help": "SSL communication with high and medium encryption algorithms.", "label": "High Medium", "name": "high-medium"}, {"description": "SSL communication with high encryption algorithms", "help": "SSL communication with high encryption algorithms.", "label": "High", "name": "high"}, {"description": "SSL communication with low encryption algorithms", "help": "SSL communication with low encryption algorithms.", "label": "Low", "name": "low"}, {"description": "Disable SSL communication", "help": "Disable SSL communication.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        certificate: str | None = ...,
        custom_field_name: list[dict[str, Any]] | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
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