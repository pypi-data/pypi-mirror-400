from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingsPayload(TypedDict, total=False):
    """
    Type hints for ips/settings payload fields.
    
    Configure IPS VDOM parameter.
    
    **Usage:**
        payload: SettingsPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    packet_log_history: NotRequired[int]  # Number of packets to capture before and including the one in
    packet_log_post_attack: NotRequired[int]  # Number of packets to log after the IPS signature is detected
    packet_log_memory: NotRequired[int]  # Maximum memory can be used by packet log (64 - 8192 kB).
    ips_packet_quota: NotRequired[int]  # Maximum amount of disk space in MB for logged packets when l
    proxy_inline_ips: NotRequired[Literal[{"description": "Do not allow inline IPS in proxy-mode policy", "help": "Do not allow inline IPS in proxy-mode policy.", "label": "Disable", "name": "disable"}, {"description": "Allow inline IPS in proxy-mode policy", "help": "Allow inline IPS in proxy-mode policy.", "label": "Enable", "name": "enable"}]]  # Enable/disable proxy-mode policy inline IPS support.
    ha_session_pickup: NotRequired[Literal[{"description": "Prefer session continuity", "help": "Prefer session continuity.", "label": "Connectivity", "name": "connectivity"}, {"description": "Prefer session complete security", "help": "Prefer session complete security.", "label": "Security", "name": "security"}]]  # IPS HA failover session pickup preference.


class Settings:
    """
    Configure IPS VDOM parameter.
    
    Path: ips/settings
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
        packet_log_history: int | None = ...,
        packet_log_post_attack: int | None = ...,
        packet_log_memory: int | None = ...,
        ips_packet_quota: int | None = ...,
        proxy_inline_ips: Literal[{"description": "Do not allow inline IPS in proxy-mode policy", "help": "Do not allow inline IPS in proxy-mode policy.", "label": "Disable", "name": "disable"}, {"description": "Allow inline IPS in proxy-mode policy", "help": "Allow inline IPS in proxy-mode policy.", "label": "Enable", "name": "enable"}] | None = ...,
        ha_session_pickup: Literal[{"description": "Prefer session continuity", "help": "Prefer session continuity.", "label": "Connectivity", "name": "connectivity"}, {"description": "Prefer session complete security", "help": "Prefer session complete security.", "label": "Security", "name": "security"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SettingsPayload | None = ...,
        packet_log_history: int | None = ...,
        packet_log_post_attack: int | None = ...,
        packet_log_memory: int | None = ...,
        ips_packet_quota: int | None = ...,
        proxy_inline_ips: Literal[{"description": "Do not allow inline IPS in proxy-mode policy", "help": "Do not allow inline IPS in proxy-mode policy.", "label": "Disable", "name": "disable"}, {"description": "Allow inline IPS in proxy-mode policy", "help": "Allow inline IPS in proxy-mode policy.", "label": "Enable", "name": "enable"}] | None = ...,
        ha_session_pickup: Literal[{"description": "Prefer session continuity", "help": "Prefer session continuity.", "label": "Connectivity", "name": "connectivity"}, {"description": "Prefer session complete security", "help": "Prefer session complete security.", "label": "Security", "name": "security"}] | None = ...,
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