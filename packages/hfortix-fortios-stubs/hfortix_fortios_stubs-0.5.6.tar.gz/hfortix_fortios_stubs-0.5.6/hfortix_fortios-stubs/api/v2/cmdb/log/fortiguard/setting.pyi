from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingPayload(TypedDict, total=False):
    """
    Type hints for log/fortiguard/setting payload fields.
    
    Configure logging to FortiCloud.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: SettingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: NotRequired[Literal[{"description": "Enable logging to FortiCloud", "help": "Enable logging to FortiCloud.", "label": "Enable", "name": "enable"}, {"description": "Disable logging to FortiCloud", "help": "Disable logging to FortiCloud.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging to FortiCloud.
    upload_option: NotRequired[Literal[{"description": "Log to the hard disk and then upload logs to FortiCloud", "help": "Log to the hard disk and then upload logs to FortiCloud.", "label": "Store And Upload", "name": "store-and-upload"}, {"description": "Log directly to FortiCloud in real time", "help": "Log directly to FortiCloud in real time.", "label": "Realtime", "name": "realtime"}, {"description": "Log directly to FortiCloud at 1-minute intervals", "help": "Log directly to FortiCloud at 1-minute intervals.", "label": "1 Minute", "name": "1-minute"}, {"description": "Log directly to FortiCloud at 5-minute intervals", "help": "Log directly to FortiCloud at 5-minute intervals.", "label": "5 Minute", "name": "5-minute"}]]  # Configure how log messages are sent to FortiCloud.
    upload_interval: NotRequired[Literal[{"description": "Upload log files to FortiCloud once a day", "help": "Upload log files to FortiCloud once a day.", "label": "Daily", "name": "daily"}, {"description": "Upload log files to FortiCloud once a week", "help": "Upload log files to FortiCloud once a week.", "label": "Weekly", "name": "weekly"}, {"description": "Upload log files to FortiCloud once a month", "help": "Upload log files to FortiCloud once a month.", "label": "Monthly", "name": "monthly"}]]  # Frequency of uploading log files to FortiCloud.
    upload_day: NotRequired[str]  # Day of week to roll logs.
    upload_time: NotRequired[str]  # Time of day to roll logs (hh:mm).
    priority: NotRequired[Literal[{"description": "Set FortiCloud log transmission priority to default", "help": "Set FortiCloud log transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set FortiCloud log transmission priority to low", "help": "Set FortiCloud log transmission priority to low.", "label": "Low", "name": "low"}]]  # Set log transmission priority.
    max_log_rate: NotRequired[int]  # FortiCloud maximum log rate in MBps (0 = unlimited).
    access_config: NotRequired[Literal[{"description": "Enable FortiCloud access to configuration and data", "help": "Enable FortiCloud access to configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud access to configuration and data", "help": "Disable FortiCloud access to configuration and data.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiCloud access to configuration and data.
    enc_algorithm: NotRequired[Literal[{"description": "Encrypt logs using high and medium encryption", "help": "Encrypt logs using high and medium encryption.", "label": "High Medium", "name": "high-medium"}, {"description": "Encrypt logs using high encryption", "help": "Encrypt logs using high encryption.", "label": "High", "name": "high"}, {"description": "Encrypt logs using low encryption", "help": "Encrypt logs using low encryption.", "label": "Low", "name": "low"}]]  # Configure the level of SSL protection for secure communicati
    ssl_min_proto_version: NotRequired[Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]]  # Minimum supported protocol version for SSL/TLS connections (
    conn_timeout: NotRequired[int]  # FortiGate Cloud connection timeout in seconds.
    source_ip: NotRequired[str]  # Source IP address used to connect FortiCloud.
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.


class Setting:
    """
    Configure logging to FortiCloud.
    
    Path: log/fortiguard/setting
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
        status: Literal[{"description": "Enable logging to FortiCloud", "help": "Enable logging to FortiCloud.", "label": "Enable", "name": "enable"}, {"description": "Disable logging to FortiCloud", "help": "Disable logging to FortiCloud.", "label": "Disable", "name": "disable"}] | None = ...,
        upload_option: Literal[{"description": "Log to the hard disk and then upload logs to FortiCloud", "help": "Log to the hard disk and then upload logs to FortiCloud.", "label": "Store And Upload", "name": "store-and-upload"}, {"description": "Log directly to FortiCloud in real time", "help": "Log directly to FortiCloud in real time.", "label": "Realtime", "name": "realtime"}, {"description": "Log directly to FortiCloud at 1-minute intervals", "help": "Log directly to FortiCloud at 1-minute intervals.", "label": "1 Minute", "name": "1-minute"}, {"description": "Log directly to FortiCloud at 5-minute intervals", "help": "Log directly to FortiCloud at 5-minute intervals.", "label": "5 Minute", "name": "5-minute"}] | None = ...,
        upload_interval: Literal[{"description": "Upload log files to FortiCloud once a day", "help": "Upload log files to FortiCloud once a day.", "label": "Daily", "name": "daily"}, {"description": "Upload log files to FortiCloud once a week", "help": "Upload log files to FortiCloud once a week.", "label": "Weekly", "name": "weekly"}, {"description": "Upload log files to FortiCloud once a month", "help": "Upload log files to FortiCloud once a month.", "label": "Monthly", "name": "monthly"}] | None = ...,
        upload_day: str | None = ...,
        upload_time: str | None = ...,
        priority: Literal[{"description": "Set FortiCloud log transmission priority to default", "help": "Set FortiCloud log transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set FortiCloud log transmission priority to low", "help": "Set FortiCloud log transmission priority to low.", "label": "Low", "name": "low"}] | None = ...,
        max_log_rate: int | None = ...,
        access_config: Literal[{"description": "Enable FortiCloud access to configuration and data", "help": "Enable FortiCloud access to configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud access to configuration and data", "help": "Disable FortiCloud access to configuration and data.", "label": "Disable", "name": "disable"}] | None = ...,
        enc_algorithm: Literal[{"description": "Encrypt logs using high and medium encryption", "help": "Encrypt logs using high and medium encryption.", "label": "High Medium", "name": "high-medium"}, {"description": "Encrypt logs using high encryption", "help": "Encrypt logs using high encryption.", "label": "High", "name": "high"}, {"description": "Encrypt logs using low encryption", "help": "Encrypt logs using low encryption.", "label": "Low", "name": "low"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        conn_timeout: int | None = ...,
        source_ip: str | None = ...,
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
        status: Literal[{"description": "Enable logging to FortiCloud", "help": "Enable logging to FortiCloud.", "label": "Enable", "name": "enable"}, {"description": "Disable logging to FortiCloud", "help": "Disable logging to FortiCloud.", "label": "Disable", "name": "disable"}] | None = ...,
        upload_option: Literal[{"description": "Log to the hard disk and then upload logs to FortiCloud", "help": "Log to the hard disk and then upload logs to FortiCloud.", "label": "Store And Upload", "name": "store-and-upload"}, {"description": "Log directly to FortiCloud in real time", "help": "Log directly to FortiCloud in real time.", "label": "Realtime", "name": "realtime"}, {"description": "Log directly to FortiCloud at 1-minute intervals", "help": "Log directly to FortiCloud at 1-minute intervals.", "label": "1 Minute", "name": "1-minute"}, {"description": "Log directly to FortiCloud at 5-minute intervals", "help": "Log directly to FortiCloud at 5-minute intervals.", "label": "5 Minute", "name": "5-minute"}] | None = ...,
        upload_interval: Literal[{"description": "Upload log files to FortiCloud once a day", "help": "Upload log files to FortiCloud once a day.", "label": "Daily", "name": "daily"}, {"description": "Upload log files to FortiCloud once a week", "help": "Upload log files to FortiCloud once a week.", "label": "Weekly", "name": "weekly"}, {"description": "Upload log files to FortiCloud once a month", "help": "Upload log files to FortiCloud once a month.", "label": "Monthly", "name": "monthly"}] | None = ...,
        upload_day: str | None = ...,
        upload_time: str | None = ...,
        priority: Literal[{"description": "Set FortiCloud log transmission priority to default", "help": "Set FortiCloud log transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set FortiCloud log transmission priority to low", "help": "Set FortiCloud log transmission priority to low.", "label": "Low", "name": "low"}] | None = ...,
        max_log_rate: int | None = ...,
        access_config: Literal[{"description": "Enable FortiCloud access to configuration and data", "help": "Enable FortiCloud access to configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud access to configuration and data", "help": "Disable FortiCloud access to configuration and data.", "label": "Disable", "name": "disable"}] | None = ...,
        enc_algorithm: Literal[{"description": "Encrypt logs using high and medium encryption", "help": "Encrypt logs using high and medium encryption.", "label": "High Medium", "name": "high-medium"}, {"description": "Encrypt logs using high encryption", "help": "Encrypt logs using high encryption.", "label": "High", "name": "high"}, {"description": "Encrypt logs using low encryption", "help": "Encrypt logs using low encryption.", "label": "Low", "name": "low"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        conn_timeout: int | None = ...,
        source_ip: str | None = ...,
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