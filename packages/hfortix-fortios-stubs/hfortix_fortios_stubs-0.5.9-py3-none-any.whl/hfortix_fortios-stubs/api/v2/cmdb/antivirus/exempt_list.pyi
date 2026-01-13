from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ExemptListPayload(TypedDict, total=False):
    """
    Type hints for antivirus/exempt_list payload fields.
    
    Configure a list of hashes to be exempt from AV scanning.
    
    **Usage:**
        payload: ExemptListPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Table entry name.
    comment: NotRequired[str]  # Comment.
    hash_type: NotRequired[Literal[{"description": "MD5 hash value (32 characters in length)", "help": "MD5 hash value (32 characters in length).", "label": "Md5", "name": "md5"}, {"description": "SHA1 hash value (40 characters in length)", "help": "SHA1 hash value (40 characters in length).", "label": "Sha1", "name": "sha1"}, {"description": "SHA256 hash value (64 characters in length)", "help": "SHA256 hash value (64 characters in length).", "label": "Sha256", "name": "sha256"}]]  # Hash type.
    hash: str  # Hash value to be matched.
    status: NotRequired[Literal[{"description": "Disable AV exempt-list table entry", "help": "Disable AV exempt-list table entry.", "label": "Disable", "name": "disable"}, {"description": "Enable AV exempt-list table entry", "help": "Enable AV exempt-list table entry.", "label": "Enable", "name": "enable"}]]  # Enable/disable table entry.


class ExemptList:
    """
    Configure a list of hashes to be exempt from AV scanning.
    
    Path: antivirus/exempt_list
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
        payload_dict: ExemptListPayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        hash_type: Literal[{"description": "MD5 hash value (32 characters in length)", "help": "MD5 hash value (32 characters in length).", "label": "Md5", "name": "md5"}, {"description": "SHA1 hash value (40 characters in length)", "help": "SHA1 hash value (40 characters in length).", "label": "Sha1", "name": "sha1"}, {"description": "SHA256 hash value (64 characters in length)", "help": "SHA256 hash value (64 characters in length).", "label": "Sha256", "name": "sha256"}] | None = ...,
        hash: str | None = ...,
        status: Literal[{"description": "Disable AV exempt-list table entry", "help": "Disable AV exempt-list table entry.", "label": "Disable", "name": "disable"}, {"description": "Enable AV exempt-list table entry", "help": "Enable AV exempt-list table entry.", "label": "Enable", "name": "enable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ExemptListPayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        hash_type: Literal[{"description": "MD5 hash value (32 characters in length)", "help": "MD5 hash value (32 characters in length).", "label": "Md5", "name": "md5"}, {"description": "SHA1 hash value (40 characters in length)", "help": "SHA1 hash value (40 characters in length).", "label": "Sha1", "name": "sha1"}, {"description": "SHA256 hash value (64 characters in length)", "help": "SHA256 hash value (64 characters in length).", "label": "Sha256", "name": "sha256"}] | None = ...,
        hash: str | None = ...,
        status: Literal[{"description": "Disable AV exempt-list table entry", "help": "Disable AV exempt-list table entry.", "label": "Disable", "name": "disable"}, {"description": "Enable AV exempt-list table entry", "help": "Enable AV exempt-list table entry.", "label": "Enable", "name": "enable"}] | None = ...,
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
        payload_dict: ExemptListPayload | None = ...,
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
    "ExemptList",
    "ExemptListPayload",
]