from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingsPayload(TypedDict, total=False):
    """
    Type hints for dlp/settings payload fields.
    
    Configure settings for DLP.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.storage.StorageEndpoint` (via: storage-device)

    **Usage:**
        payload: SettingsPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    storage_device: NotRequired[str]  # Storage device name.
    size: NotRequired[int]  # Maximum total size of files within the DLP fingerprint datab
    db_mode: NotRequired[Literal[{"help": "Stop adding entries.", "label": "Stop Adding", "name": "stop-adding"}, {"help": "Remove modified chunks first, then oldest file entries.", "label": "Remove Modified Then Oldest", "name": "remove-modified-then-oldest"}, {"help": "Remove the oldest files first.", "label": "Remove Oldest", "name": "remove-oldest"}]]  # Behavior when the maximum size is reached in the DLP fingerp
    cache_mem_percent: NotRequired[int]  # Maximum percentage of available memory allocated to caching 
    chunk_size: NotRequired[int]  # Maximum fingerprint chunk size. Caution, changing this setti
    config_builder_timeout: NotRequired[int]  # Maximum time allowed for building a single DLP profile (defa


class Settings:
    """
    Configure settings for DLP.
    
    Path: dlp/settings
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
        storage_device: str | None = ...,
        size: int | None = ...,
        db_mode: Literal[{"help": "Stop adding entries.", "label": "Stop Adding", "name": "stop-adding"}, {"help": "Remove modified chunks first, then oldest file entries.", "label": "Remove Modified Then Oldest", "name": "remove-modified-then-oldest"}, {"help": "Remove the oldest files first.", "label": "Remove Oldest", "name": "remove-oldest"}] | None = ...,
        cache_mem_percent: int | None = ...,
        chunk_size: int | None = ...,
        config_builder_timeout: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SettingsPayload | None = ...,
        storage_device: str | None = ...,
        size: int | None = ...,
        db_mode: Literal[{"help": "Stop adding entries.", "label": "Stop Adding", "name": "stop-adding"}, {"help": "Remove modified chunks first, then oldest file entries.", "label": "Remove Modified Then Oldest", "name": "remove-modified-then-oldest"}, {"help": "Remove the oldest files first.", "label": "Remove Oldest", "name": "remove-oldest"}] | None = ...,
        cache_mem_percent: int | None = ...,
        chunk_size: int | None = ...,
        config_builder_timeout: int | None = ...,
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