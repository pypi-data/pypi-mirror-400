from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class OverrideSettingPayload(TypedDict, total=False):
    """
    Type hints for log/fortiguard/override_setting payload fields.
    
    Override global FortiCloud logging settings for this VDOM.
    
    **Usage:**
        payload: OverrideSettingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    override: NotRequired[Literal[{"description": "Override FortiCloud logging settings", "help": "Override FortiCloud logging settings.", "label": "Enable", "name": "enable"}, {"description": "Use global FortiCloud logging settings", "help": "Use global FortiCloud logging settings.", "label": "Disable", "name": "disable"}]]  # Overriding FortiCloud settings for this VDOM or use global s
    status: NotRequired[Literal[{"description": "Enable logging to FortiCloud", "help": "Enable logging to FortiCloud.", "label": "Enable", "name": "enable"}, {"description": "Disable logging to FortiCloud", "help": "Disable logging to FortiCloud.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging to FortiCloud.
    upload_option: NotRequired[Literal[{"description": "Log to the hard disk and then upload logs to FortiCloud", "help": "Log to the hard disk and then upload logs to FortiCloud.", "label": "Store And Upload", "name": "store-and-upload"}, {"description": "Log directly to FortiCloud in real time", "help": "Log directly to FortiCloud in real time.", "label": "Realtime", "name": "realtime"}, {"description": "Log directly to FortiCloud at 1-minute intervals", "help": "Log directly to FortiCloud at 1-minute intervals.", "label": "1 Minute", "name": "1-minute"}, {"description": "Log directly to FortiCloud at 5-minute intervals", "help": "Log directly to FortiCloud at 5-minute intervals.", "label": "5 Minute", "name": "5-minute"}]]  # Configure how log messages are sent to FortiCloud.
    upload_interval: NotRequired[Literal[{"description": "Upload log files to FortiCloud once a day", "help": "Upload log files to FortiCloud once a day.", "label": "Daily", "name": "daily"}, {"description": "Upload log files to FortiCloud once a week", "help": "Upload log files to FortiCloud once a week.", "label": "Weekly", "name": "weekly"}, {"description": "Upload log files to FortiCloud once a month", "help": "Upload log files to FortiCloud once a month.", "label": "Monthly", "name": "monthly"}]]  # Frequency of uploading log files to FortiCloud.
    upload_day: NotRequired[str]  # Day of week to roll logs.
    upload_time: NotRequired[str]  # Time of day to roll logs (hh:mm).
    priority: NotRequired[Literal[{"description": "Set FortiCloud log transmission priority to default", "help": "Set FortiCloud log transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set FortiCloud log transmission priority to low", "help": "Set FortiCloud log transmission priority to low.", "label": "Low", "name": "low"}]]  # Set log transmission priority.
    max_log_rate: NotRequired[int]  # FortiCloud maximum log rate in MBps (0 = unlimited).
    access_config: NotRequired[Literal[{"description": "Enable FortiCloud access to configuration and data", "help": "Enable FortiCloud access to configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud access to configuration and data", "help": "Disable FortiCloud access to configuration and data.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiCloud access to configuration and data.


class OverrideSetting:
    """
    Override global FortiCloud logging settings for this VDOM.
    
    Path: log/fortiguard/override_setting
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
        payload_dict: OverrideSettingPayload | None = ...,
        override: Literal[{"description": "Override FortiCloud logging settings", "help": "Override FortiCloud logging settings.", "label": "Enable", "name": "enable"}, {"description": "Use global FortiCloud logging settings", "help": "Use global FortiCloud logging settings.", "label": "Disable", "name": "disable"}] | None = ...,
        status: Literal[{"description": "Enable logging to FortiCloud", "help": "Enable logging to FortiCloud.", "label": "Enable", "name": "enable"}, {"description": "Disable logging to FortiCloud", "help": "Disable logging to FortiCloud.", "label": "Disable", "name": "disable"}] | None = ...,
        upload_option: Literal[{"description": "Log to the hard disk and then upload logs to FortiCloud", "help": "Log to the hard disk and then upload logs to FortiCloud.", "label": "Store And Upload", "name": "store-and-upload"}, {"description": "Log directly to FortiCloud in real time", "help": "Log directly to FortiCloud in real time.", "label": "Realtime", "name": "realtime"}, {"description": "Log directly to FortiCloud at 1-minute intervals", "help": "Log directly to FortiCloud at 1-minute intervals.", "label": "1 Minute", "name": "1-minute"}, {"description": "Log directly to FortiCloud at 5-minute intervals", "help": "Log directly to FortiCloud at 5-minute intervals.", "label": "5 Minute", "name": "5-minute"}] | None = ...,
        upload_interval: Literal[{"description": "Upload log files to FortiCloud once a day", "help": "Upload log files to FortiCloud once a day.", "label": "Daily", "name": "daily"}, {"description": "Upload log files to FortiCloud once a week", "help": "Upload log files to FortiCloud once a week.", "label": "Weekly", "name": "weekly"}, {"description": "Upload log files to FortiCloud once a month", "help": "Upload log files to FortiCloud once a month.", "label": "Monthly", "name": "monthly"}] | None = ...,
        upload_day: str | None = ...,
        upload_time: str | None = ...,
        priority: Literal[{"description": "Set FortiCloud log transmission priority to default", "help": "Set FortiCloud log transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set FortiCloud log transmission priority to low", "help": "Set FortiCloud log transmission priority to low.", "label": "Low", "name": "low"}] | None = ...,
        max_log_rate: int | None = ...,
        access_config: Literal[{"description": "Enable FortiCloud access to configuration and data", "help": "Enable FortiCloud access to configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud access to configuration and data", "help": "Disable FortiCloud access to configuration and data.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: OverrideSettingPayload | None = ...,
        override: Literal[{"description": "Override FortiCloud logging settings", "help": "Override FortiCloud logging settings.", "label": "Enable", "name": "enable"}, {"description": "Use global FortiCloud logging settings", "help": "Use global FortiCloud logging settings.", "label": "Disable", "name": "disable"}] | None = ...,
        status: Literal[{"description": "Enable logging to FortiCloud", "help": "Enable logging to FortiCloud.", "label": "Enable", "name": "enable"}, {"description": "Disable logging to FortiCloud", "help": "Disable logging to FortiCloud.", "label": "Disable", "name": "disable"}] | None = ...,
        upload_option: Literal[{"description": "Log to the hard disk and then upload logs to FortiCloud", "help": "Log to the hard disk and then upload logs to FortiCloud.", "label": "Store And Upload", "name": "store-and-upload"}, {"description": "Log directly to FortiCloud in real time", "help": "Log directly to FortiCloud in real time.", "label": "Realtime", "name": "realtime"}, {"description": "Log directly to FortiCloud at 1-minute intervals", "help": "Log directly to FortiCloud at 1-minute intervals.", "label": "1 Minute", "name": "1-minute"}, {"description": "Log directly to FortiCloud at 5-minute intervals", "help": "Log directly to FortiCloud at 5-minute intervals.", "label": "5 Minute", "name": "5-minute"}] | None = ...,
        upload_interval: Literal[{"description": "Upload log files to FortiCloud once a day", "help": "Upload log files to FortiCloud once a day.", "label": "Daily", "name": "daily"}, {"description": "Upload log files to FortiCloud once a week", "help": "Upload log files to FortiCloud once a week.", "label": "Weekly", "name": "weekly"}, {"description": "Upload log files to FortiCloud once a month", "help": "Upload log files to FortiCloud once a month.", "label": "Monthly", "name": "monthly"}] | None = ...,
        upload_day: str | None = ...,
        upload_time: str | None = ...,
        priority: Literal[{"description": "Set FortiCloud log transmission priority to default", "help": "Set FortiCloud log transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set FortiCloud log transmission priority to low", "help": "Set FortiCloud log transmission priority to low.", "label": "Low", "name": "low"}] | None = ...,
        max_log_rate: int | None = ...,
        access_config: Literal[{"description": "Enable FortiCloud access to configuration and data", "help": "Enable FortiCloud access to configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud access to configuration and data", "help": "Disable FortiCloud access to configuration and data.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: OverrideSettingPayload | None = ...,
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
    "OverrideSetting",
    "OverrideSettingPayload",
]