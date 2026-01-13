from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class FssoPollingPayload(TypedDict, total=False):
    """
    Type hints for system/fsso_polling payload fields.
    
    Configure Fortinet Single Sign On (FSSO) server.
    
    **Usage:**
        payload: FssoPollingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: NotRequired[Literal[{"description": "Enable FSSO Polling Mode", "help": "Enable FSSO Polling Mode.", "label": "Enable", "name": "enable"}, {"description": "Disable FSSO Polling Mode", "help": "Disable FSSO Polling Mode.", "label": "Disable", "name": "disable"}]]  # Enable/disable FSSO Polling Mode.
    listening_port: NotRequired[int]  # Listening port to accept clients (1 - 65535).
    authentication: NotRequired[Literal[{"description": "Enable FSSO Agent Authentication", "help": "Enable FSSO Agent Authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable FSSO Agent Authentication", "help": "Disable FSSO Agent Authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable FSSO Agent Authentication.
    auth_password: NotRequired[str]  # Password to connect to FSSO Agent.


class FssoPolling:
    """
    Configure Fortinet Single Sign On (FSSO) server.
    
    Path: system/fsso_polling
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
        payload_dict: FssoPollingPayload | None = ...,
        status: Literal[{"description": "Enable FSSO Polling Mode", "help": "Enable FSSO Polling Mode.", "label": "Enable", "name": "enable"}, {"description": "Disable FSSO Polling Mode", "help": "Disable FSSO Polling Mode.", "label": "Disable", "name": "disable"}] | None = ...,
        listening_port: int | None = ...,
        authentication: Literal[{"description": "Enable FSSO Agent Authentication", "help": "Enable FSSO Agent Authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable FSSO Agent Authentication", "help": "Disable FSSO Agent Authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_password: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: FssoPollingPayload | None = ...,
        status: Literal[{"description": "Enable FSSO Polling Mode", "help": "Enable FSSO Polling Mode.", "label": "Enable", "name": "enable"}, {"description": "Disable FSSO Polling Mode", "help": "Disable FSSO Polling Mode.", "label": "Disable", "name": "disable"}] | None = ...,
        listening_port: int | None = ...,
        authentication: Literal[{"description": "Enable FSSO Agent Authentication", "help": "Enable FSSO Agent Authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable FSSO Agent Authentication", "help": "Disable FSSO Agent Authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_password: str | None = ...,
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
        payload_dict: FssoPollingPayload | None = ...,
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
    "FssoPolling",
    "FssoPollingPayload",
]