from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class DictionaryPayload(TypedDict, total=False):
    """
    Type hints for dlp/dictionary payload fields.
    
    Configure dictionaries used by DLP blocking.
    
    **Usage:**
        payload: DictionaryPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    name: str  # Name of table containing the dictionary.
    match_type: Literal[{"description": "Match all entries", "help": "Match all entries.", "label": "Match All", "name": "match-all"}, {"description": "Match any entries", "help": "Match any entries.", "label": "Match Any", "name": "match-any"}]  # Logical relation between entries (default = match-any).
    match_around: NotRequired[Literal[{"description": "Enable match-around support", "help": "Enable match-around support.", "label": "Enable", "name": "enable"}, {"description": "Disable match-around support", "help": "Disable match-around support.", "label": "Disable", "name": "disable"}]]  # Enable/disable match-around support.
    comment: NotRequired[str]  # Optional comments.
    entries: list[dict[str, Any]]  # DLP dictionary entries.


class Dictionary:
    """
    Configure dictionaries used by DLP blocking.
    
    Path: dlp/dictionary
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
        payload_dict: DictionaryPayload | None = ...,
        uuid: str | None = ...,
        name: str | None = ...,
        match_type: Literal[{"description": "Match all entries", "help": "Match all entries.", "label": "Match All", "name": "match-all"}, {"description": "Match any entries", "help": "Match any entries.", "label": "Match Any", "name": "match-any"}] | None = ...,
        match_around: Literal[{"description": "Enable match-around support", "help": "Enable match-around support.", "label": "Enable", "name": "enable"}, {"description": "Disable match-around support", "help": "Disable match-around support.", "label": "Disable", "name": "disable"}] | None = ...,
        comment: str | None = ...,
        entries: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: DictionaryPayload | None = ...,
        uuid: str | None = ...,
        name: str | None = ...,
        match_type: Literal[{"description": "Match all entries", "help": "Match all entries.", "label": "Match All", "name": "match-all"}, {"description": "Match any entries", "help": "Match any entries.", "label": "Match Any", "name": "match-any"}] | None = ...,
        match_around: Literal[{"description": "Enable match-around support", "help": "Enable match-around support.", "label": "Enable", "name": "enable"}, {"description": "Disable match-around support", "help": "Disable match-around support.", "label": "Disable", "name": "disable"}] | None = ...,
        comment: str | None = ...,
        entries: list[dict[str, Any]] | None = ...,
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
        payload_dict: DictionaryPayload | None = ...,
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
    "Dictionary",
    "DictionaryPayload",
]