from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class MpskProfilePayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/mpsk_profile payload fields.
    
    Configure MPSK profile.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.user.radius.RadiusEndpoint` (via: mpsk-external-server)

    **Usage:**
        payload: MpskProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # MPSK profile name.
    mpsk_concurrent_clients: NotRequired[int]  # Maximum number of concurrent clients that connect using the 
    mpsk_external_server_auth: NotRequired[Literal[{"description": "Enable MPSK external server authentication", "help": "Enable MPSK external server authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable MPSK external server authentication", "help": "Disable MPSK external server authentication.", "label": "Disable", "name": "disable"}]]  # Enable/Disable MPSK external server authentication (default 
    mpsk_external_server: NotRequired[str]  # RADIUS server to be used to authenticate MPSK users.
    mpsk_type: NotRequired[Literal[{"description": "WPA2 personal", "help": "WPA2 personal.", "label": "Wpa2 Personal", "name": "wpa2-personal"}, {"description": "WPA3 SAE", "help": "WPA3 SAE.", "label": "Wpa3 Sae", "name": "wpa3-sae"}, {"description": "WPA3 SAE transition", "help": "WPA3 SAE transition.", "label": "Wpa3 Sae Transition", "name": "wpa3-sae-transition"}]]  # Select the security type of keys for this profile.
    mpsk_group: NotRequired[list[dict[str, Any]]]  # List of multiple PSK groups.


class MpskProfile:
    """
    Configure MPSK profile.
    
    Path: wireless_controller/mpsk_profile
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
        payload_dict: MpskProfilePayload | None = ...,
        name: str | None = ...,
        mpsk_concurrent_clients: int | None = ...,
        mpsk_external_server_auth: Literal[{"description": "Enable MPSK external server authentication", "help": "Enable MPSK external server authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable MPSK external server authentication", "help": "Disable MPSK external server authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        mpsk_external_server: str | None = ...,
        mpsk_type: Literal[{"description": "WPA2 personal", "help": "WPA2 personal.", "label": "Wpa2 Personal", "name": "wpa2-personal"}, {"description": "WPA3 SAE", "help": "WPA3 SAE.", "label": "Wpa3 Sae", "name": "wpa3-sae"}, {"description": "WPA3 SAE transition", "help": "WPA3 SAE transition.", "label": "Wpa3 Sae Transition", "name": "wpa3-sae-transition"}] | None = ...,
        mpsk_group: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: MpskProfilePayload | None = ...,
        name: str | None = ...,
        mpsk_concurrent_clients: int | None = ...,
        mpsk_external_server_auth: Literal[{"description": "Enable MPSK external server authentication", "help": "Enable MPSK external server authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable MPSK external server authentication", "help": "Disable MPSK external server authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        mpsk_external_server: str | None = ...,
        mpsk_type: Literal[{"description": "WPA2 personal", "help": "WPA2 personal.", "label": "Wpa2 Personal", "name": "wpa2-personal"}, {"description": "WPA3 SAE", "help": "WPA3 SAE.", "label": "Wpa3 Sae", "name": "wpa3-sae"}, {"description": "WPA3 SAE transition", "help": "WPA3 SAE transition.", "label": "Wpa3 Sae Transition", "name": "wpa3-sae-transition"}] | None = ...,
        mpsk_group: list[dict[str, Any]] | None = ...,
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
        payload_dict: MpskProfilePayload | None = ...,
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
    "MpskProfile",
    "MpskProfilePayload",
]