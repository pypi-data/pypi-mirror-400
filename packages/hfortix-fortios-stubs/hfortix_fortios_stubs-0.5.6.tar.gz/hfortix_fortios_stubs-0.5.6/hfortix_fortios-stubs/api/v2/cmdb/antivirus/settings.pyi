from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingsPayload(TypedDict, total=False):
    """
    Type hints for antivirus/settings payload fields.
    
    Configure AntiVirus settings.
    
    **Usage:**
        payload: SettingsPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    machine_learning_detection: NotRequired[Literal[{"description": "Enable machine learning based malware detection", "help": "Enable machine learning based malware detection.", "label": "Enable", "name": "enable"}, {"description": "Enable machine learning based malware detection for monitoring only", "help": "Enable machine learning based malware detection for monitoring only.", "label": "Monitor", "name": "monitor"}, {"description": "Disable machine learning based malware detection", "help": "Disable machine learning based malware detection.", "label": "Disable", "name": "disable"}]]  # Use machine learning based malware detection.
    use_extreme_db: NotRequired[Literal[{"description": "Enable extreme AVDB", "help": "Enable extreme AVDB.", "label": "Enable", "name": "enable"}, {"description": "Disable extreme AVDB", "help": "Disable extreme AVDB.", "label": "Disable", "name": "disable"}]]  # Enable/disable the use of Extreme AVDB.
    grayware: NotRequired[Literal[{"description": "Enable grayware detection", "help": "Enable grayware detection.", "label": "Enable", "name": "enable"}, {"description": "Disable grayware detection", "help": "Disable grayware detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable grayware detection when an AntiVirus profile 
    override_timeout: NotRequired[int]  # Override the large file scan timeout value in seconds (30 - 
    cache_infected_result: NotRequired[Literal[{"description": "Enable cache of infected scan results", "help": "Enable cache of infected scan results.", "label": "Enable", "name": "enable"}, {"description": "Disable cache of infected scan results", "help": "Disable cache of infected scan results.", "label": "Disable", "name": "disable"}]]  # Enable/disable cache of infected scan results (default = ena


class Settings:
    """
    Configure AntiVirus settings.
    
    Path: antivirus/settings
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
        payload_dict: SettingsPayload | None = ...,
        machine_learning_detection: Literal[{"description": "Enable machine learning based malware detection", "help": "Enable machine learning based malware detection.", "label": "Enable", "name": "enable"}, {"description": "Enable machine learning based malware detection for monitoring only", "help": "Enable machine learning based malware detection for monitoring only.", "label": "Monitor", "name": "monitor"}, {"description": "Disable machine learning based malware detection", "help": "Disable machine learning based malware detection.", "label": "Disable", "name": "disable"}] | None = ...,
        use_extreme_db: Literal[{"description": "Enable extreme AVDB", "help": "Enable extreme AVDB.", "label": "Enable", "name": "enable"}, {"description": "Disable extreme AVDB", "help": "Disable extreme AVDB.", "label": "Disable", "name": "disable"}] | None = ...,
        grayware: Literal[{"description": "Enable grayware detection", "help": "Enable grayware detection.", "label": "Enable", "name": "enable"}, {"description": "Disable grayware detection", "help": "Disable grayware detection.", "label": "Disable", "name": "disable"}] | None = ...,
        override_timeout: int | None = ...,
        cache_infected_result: Literal[{"description": "Enable cache of infected scan results", "help": "Enable cache of infected scan results.", "label": "Enable", "name": "enable"}, {"description": "Disable cache of infected scan results", "help": "Disable cache of infected scan results.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SettingsPayload | None = ...,
        machine_learning_detection: Literal[{"description": "Enable machine learning based malware detection", "help": "Enable machine learning based malware detection.", "label": "Enable", "name": "enable"}, {"description": "Enable machine learning based malware detection for monitoring only", "help": "Enable machine learning based malware detection for monitoring only.", "label": "Monitor", "name": "monitor"}, {"description": "Disable machine learning based malware detection", "help": "Disable machine learning based malware detection.", "label": "Disable", "name": "disable"}] | None = ...,
        use_extreme_db: Literal[{"description": "Enable extreme AVDB", "help": "Enable extreme AVDB.", "label": "Enable", "name": "enable"}, {"description": "Disable extreme AVDB", "help": "Disable extreme AVDB.", "label": "Disable", "name": "disable"}] | None = ...,
        grayware: Literal[{"description": "Enable grayware detection", "help": "Enable grayware detection.", "label": "Enable", "name": "enable"}, {"description": "Disable grayware detection", "help": "Disable grayware detection.", "label": "Disable", "name": "disable"}] | None = ...,
        override_timeout: int | None = ...,
        cache_infected_result: Literal[{"description": "Enable cache of infected scan results", "help": "Enable cache of infected scan results.", "label": "Enable", "name": "enable"}, {"description": "Disable cache of infected scan results", "help": "Disable cache of infected scan results.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: SettingsPayload | None = ...,
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
    "Settings",
    "SettingsPayload",
]