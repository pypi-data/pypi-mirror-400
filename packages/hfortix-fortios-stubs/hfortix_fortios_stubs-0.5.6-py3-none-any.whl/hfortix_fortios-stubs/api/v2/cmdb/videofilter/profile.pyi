from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ProfilePayload(TypedDict, total=False):
    """
    Type hints for videofilter/profile payload fields.
    
    Configure VideoFilter profile.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.replacemsg-group.ReplacemsgGroupEndpoint` (via: replacemsg-group)

    **Usage:**
        payload: ProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Name.
    comment: NotRequired[str]  # Comment.
    filters: list[dict[str, Any]]  # YouTube filter entries.
    youtube: NotRequired[Literal[{"description": "Enable YouTube source", "help": "Enable YouTube source.", "label": "Enable", "name": "enable"}, {"description": "Disable YouTube source", "help": "Disable YouTube source.", "label": "Disable", "name": "disable"}]]  # Enable/disable YouTube video source.
    vimeo: NotRequired[Literal[{"description": "Enable Vimeo source", "help": "Enable Vimeo source.", "label": "Enable", "name": "enable"}, {"description": "Disable Vimeo source", "help": "Disable Vimeo source.", "label": "Disable", "name": "disable"}]]  # Enable/disable Vimeo video source.
    dailymotion: NotRequired[Literal[{"description": "Enable Dailymotion source", "help": "Enable Dailymotion source.", "label": "Enable", "name": "enable"}, {"description": "Disable Dailymotion source", "help": "Disable Dailymotion source.", "label": "Disable", "name": "disable"}]]  # Enable/disable Dailymotion video source.
    replacemsg_group: NotRequired[str]  # Replacement message group.


class Profile:
    """
    Configure VideoFilter profile.
    
    Path: videofilter/profile
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
        payload_dict: ProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        filters: list[dict[str, Any]] | None = ...,
        youtube: Literal[{"description": "Enable YouTube source", "help": "Enable YouTube source.", "label": "Enable", "name": "enable"}, {"description": "Disable YouTube source", "help": "Disable YouTube source.", "label": "Disable", "name": "disable"}] | None = ...,
        vimeo: Literal[{"description": "Enable Vimeo source", "help": "Enable Vimeo source.", "label": "Enable", "name": "enable"}, {"description": "Disable Vimeo source", "help": "Disable Vimeo source.", "label": "Disable", "name": "disable"}] | None = ...,
        dailymotion: Literal[{"description": "Enable Dailymotion source", "help": "Enable Dailymotion source.", "label": "Enable", "name": "enable"}, {"description": "Disable Dailymotion source", "help": "Disable Dailymotion source.", "label": "Disable", "name": "disable"}] | None = ...,
        replacemsg_group: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        filters: list[dict[str, Any]] | None = ...,
        youtube: Literal[{"description": "Enable YouTube source", "help": "Enable YouTube source.", "label": "Enable", "name": "enable"}, {"description": "Disable YouTube source", "help": "Disable YouTube source.", "label": "Disable", "name": "disable"}] | None = ...,
        vimeo: Literal[{"description": "Enable Vimeo source", "help": "Enable Vimeo source.", "label": "Enable", "name": "enable"}, {"description": "Disable Vimeo source", "help": "Disable Vimeo source.", "label": "Disable", "name": "disable"}] | None = ...,
        dailymotion: Literal[{"description": "Enable Dailymotion source", "help": "Enable Dailymotion source.", "label": "Enable", "name": "enable"}, {"description": "Disable Dailymotion source", "help": "Disable Dailymotion source.", "label": "Disable", "name": "disable"}] | None = ...,
        replacemsg_group: str | None = ...,
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
        payload_dict: ProfilePayload | None = ...,
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
    "Profile",
    "ProfilePayload",
]