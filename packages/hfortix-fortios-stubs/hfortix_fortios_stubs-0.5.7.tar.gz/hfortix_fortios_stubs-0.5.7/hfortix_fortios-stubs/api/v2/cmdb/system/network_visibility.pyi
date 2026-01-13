from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class NetworkVisibilityPayload(TypedDict, total=False):
    """
    Type hints for system/network_visibility payload fields.
    
    Configure network visibility settings.
    
    **Usage:**
        payload: NetworkVisibilityPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    destination_visibility: NotRequired[Literal[{"description": "Disable logging of destination visibility", "help": "Disable logging of destination visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of destination visibility", "help": "Enable logging of destination visibility.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging of destination visibility.
    source_location: NotRequired[Literal[{"description": "Disable logging of source geographical location visibility", "help": "Disable logging of source geographical location visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of source geographical location visibility", "help": "Enable logging of source geographical location visibility.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging of source geographical location visib
    destination_hostname_visibility: NotRequired[Literal[{"description": "Disable logging of destination hostname visibility", "help": "Disable logging of destination hostname visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of destination hostname visibility", "help": "Enable logging of destination hostname visibility.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging of destination hostname visibility.
    destination_location: NotRequired[Literal[{"description": "Disable logging of destination geographical location visibility", "help": "Disable logging of destination geographical location visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of destination geographical location visibility", "help": "Enable logging of destination geographical location visibility.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging of destination geographical location 


class NetworkVisibility:
    """
    Configure network visibility settings.
    
    Path: system/network_visibility
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
        payload_dict: NetworkVisibilityPayload | None = ...,
        destination_visibility: Literal[{"description": "Disable logging of destination visibility", "help": "Disable logging of destination visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of destination visibility", "help": "Enable logging of destination visibility.", "label": "Enable", "name": "enable"}] | None = ...,
        source_location: Literal[{"description": "Disable logging of source geographical location visibility", "help": "Disable logging of source geographical location visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of source geographical location visibility", "help": "Enable logging of source geographical location visibility.", "label": "Enable", "name": "enable"}] | None = ...,
        destination_hostname_visibility: Literal[{"description": "Disable logging of destination hostname visibility", "help": "Disable logging of destination hostname visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of destination hostname visibility", "help": "Enable logging of destination hostname visibility.", "label": "Enable", "name": "enable"}] | None = ...,
        destination_location: Literal[{"description": "Disable logging of destination geographical location visibility", "help": "Disable logging of destination geographical location visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of destination geographical location visibility", "help": "Enable logging of destination geographical location visibility.", "label": "Enable", "name": "enable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: NetworkVisibilityPayload | None = ...,
        destination_visibility: Literal[{"description": "Disable logging of destination visibility", "help": "Disable logging of destination visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of destination visibility", "help": "Enable logging of destination visibility.", "label": "Enable", "name": "enable"}] | None = ...,
        source_location: Literal[{"description": "Disable logging of source geographical location visibility", "help": "Disable logging of source geographical location visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of source geographical location visibility", "help": "Enable logging of source geographical location visibility.", "label": "Enable", "name": "enable"}] | None = ...,
        destination_hostname_visibility: Literal[{"description": "Disable logging of destination hostname visibility", "help": "Disable logging of destination hostname visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of destination hostname visibility", "help": "Enable logging of destination hostname visibility.", "label": "Enable", "name": "enable"}] | None = ...,
        destination_location: Literal[{"description": "Disable logging of destination geographical location visibility", "help": "Disable logging of destination geographical location visibility.", "label": "Disable", "name": "disable"}, {"description": "Enable logging of destination geographical location visibility", "help": "Enable logging of destination geographical location visibility.", "label": "Enable", "name": "enable"}] | None = ...,
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
        payload_dict: NetworkVisibilityPayload | None = ...,
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
    "NetworkVisibility",
    "NetworkVisibilityPayload",
]