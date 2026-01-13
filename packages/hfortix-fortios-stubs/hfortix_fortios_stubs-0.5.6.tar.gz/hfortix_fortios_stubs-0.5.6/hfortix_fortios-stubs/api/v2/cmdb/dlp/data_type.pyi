from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class DataTypePayload(TypedDict, total=False):
    """
    Type hints for dlp/data_type payload fields.
    
    Configure predefined data type used by DLP blocking.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.dlp.dictionary.DictionaryEndpoint` (via: match-around)

    **Usage:**
        payload: DataTypePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Name of table containing the data type.
    pattern: NotRequired[str]  # Regular expression pattern string without look around.
    verify: NotRequired[str]  # Regular expression pattern string used to verify the data ty
    verify2: NotRequired[str]  # Extra regular expression pattern string used to verify the d
    match_around: NotRequired[str]  # Dictionary to check whether it has a match around (Only supp
    look_back: int  # Number of characters required to save for verification (1 - 
    look_ahead: int  # Number of characters to obtain in advance for verification (
    match_back: int  # Number of characters in front for match-around (1 - 4096, de
    match_ahead: int  # Number of characters behind for match-around (1 - 4096, defa
    transform: NotRequired[str]  # Template to transform user input to a pattern using capture 
    verify_transformed_pattern: NotRequired[Literal[{"description": "Enable verification for transformed pattern", "help": "Enable verification for transformed pattern.", "label": "Enable", "name": "enable"}, {"description": "Disable verification for transformed pattern", "help": "Disable verification for transformed pattern.", "label": "Disable", "name": "disable"}]]  # Enable/disable verification for transformed pattern.
    comment: NotRequired[str]  # Optional comments.


class DataType:
    """
    Configure predefined data type used by DLP blocking.
    
    Path: dlp/data_type
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
        payload_dict: DataTypePayload | None = ...,
        name: str | None = ...,
        pattern: str | None = ...,
        verify: str | None = ...,
        verify2: str | None = ...,
        match_around: str | None = ...,
        look_back: int | None = ...,
        look_ahead: int | None = ...,
        match_back: int | None = ...,
        match_ahead: int | None = ...,
        transform: str | None = ...,
        verify_transformed_pattern: Literal[{"description": "Enable verification for transformed pattern", "help": "Enable verification for transformed pattern.", "label": "Enable", "name": "enable"}, {"description": "Disable verification for transformed pattern", "help": "Disable verification for transformed pattern.", "label": "Disable", "name": "disable"}] | None = ...,
        comment: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: DataTypePayload | None = ...,
        name: str | None = ...,
        pattern: str | None = ...,
        verify: str | None = ...,
        verify2: str | None = ...,
        match_around: str | None = ...,
        look_back: int | None = ...,
        look_ahead: int | None = ...,
        match_back: int | None = ...,
        match_ahead: int | None = ...,
        transform: str | None = ...,
        verify_transformed_pattern: Literal[{"description": "Enable verification for transformed pattern", "help": "Enable verification for transformed pattern.", "label": "Enable", "name": "enable"}, {"description": "Disable verification for transformed pattern", "help": "Disable verification for transformed pattern.", "label": "Disable", "name": "disable"}] | None = ...,
        comment: str | None = ...,
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
        payload_dict: DataTypePayload | None = ...,
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
    "DataType",
    "DataTypePayload",
]