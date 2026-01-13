from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class UtmProfilePayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/utm_profile payload fields.
    
    Configure UTM (Unified Threat Management) profile.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.antivirus.profile.ProfileEndpoint` (via: antivirus-profile)
        - :class:`~.application.list.ListEndpoint` (via: application-list)
        - :class:`~.ips.sensor.SensorEndpoint` (via: ips-sensor)
        - :class:`~.webfilter.profile.ProfileEndpoint` (via: webfilter-profile)

    **Usage:**
        payload: UtmProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # UTM profile name.
    comment: NotRequired[str]  # Comment.
    utm_log: NotRequired[Literal[{"description": "Enable UTM logging", "help": "Enable UTM logging.", "label": "Enable", "name": "enable"}, {"description": "Disable UTM logging", "help": "Disable UTM logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable UTM logging.
    ips_sensor: NotRequired[str]  # IPS sensor name.
    application_list: NotRequired[str]  # Application control list name.
    antivirus_profile: NotRequired[str]  # AntiVirus profile name.
    webfilter_profile: NotRequired[str]  # WebFilter profile name.
    scan_botnet_connections: NotRequired[Literal[{"description": "Do not scan connections to botnet servers", "help": "Do not scan connections to botnet servers.", "label": "Disable", "name": "disable"}, {"description": "Log connections to botnet servers", "help": "Log connections to botnet servers.", "label": "Monitor", "name": "monitor"}, {"description": "Block connections to botnet servers", "help": "Block connections to botnet servers.", "label": "Block", "name": "block"}]]  # Block or monitor connections to Botnet servers or disable Bo


class UtmProfile:
    """
    Configure UTM (Unified Threat Management) profile.
    
    Path: wireless_controller/utm_profile
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
        payload_dict: UtmProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        utm_log: Literal[{"description": "Enable UTM logging", "help": "Enable UTM logging.", "label": "Enable", "name": "enable"}, {"description": "Disable UTM logging", "help": "Disable UTM logging.", "label": "Disable", "name": "disable"}] | None = ...,
        ips_sensor: str | None = ...,
        application_list: str | None = ...,
        antivirus_profile: str | None = ...,
        webfilter_profile: str | None = ...,
        scan_botnet_connections: Literal[{"description": "Do not scan connections to botnet servers", "help": "Do not scan connections to botnet servers.", "label": "Disable", "name": "disable"}, {"description": "Log connections to botnet servers", "help": "Log connections to botnet servers.", "label": "Monitor", "name": "monitor"}, {"description": "Block connections to botnet servers", "help": "Block connections to botnet servers.", "label": "Block", "name": "block"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: UtmProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        utm_log: Literal[{"description": "Enable UTM logging", "help": "Enable UTM logging.", "label": "Enable", "name": "enable"}, {"description": "Disable UTM logging", "help": "Disable UTM logging.", "label": "Disable", "name": "disable"}] | None = ...,
        ips_sensor: str | None = ...,
        application_list: str | None = ...,
        antivirus_profile: str | None = ...,
        webfilter_profile: str | None = ...,
        scan_botnet_connections: Literal[{"description": "Do not scan connections to botnet servers", "help": "Do not scan connections to botnet servers.", "label": "Disable", "name": "disable"}, {"description": "Log connections to botnet servers", "help": "Log connections to botnet servers.", "label": "Monitor", "name": "monitor"}, {"description": "Block connections to botnet servers", "help": "Block connections to botnet servers.", "label": "Block", "name": "block"}] | None = ...,
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
        payload_dict: UtmProfilePayload | None = ...,
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
    "UtmProfile",
    "UtmProfilePayload",
]