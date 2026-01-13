from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ObjectTaggingPayload(TypedDict, total=False):
    """
    Type hints for system/object_tagging payload fields.
    
    Configure object tagging.
    
    **Usage:**
        payload: ObjectTaggingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    category: NotRequired[str]  # Tag Category.
    address: NotRequired[Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}]]  # Address.
    device: NotRequired[Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}]]  # Device.
    interface: NotRequired[Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}]]  # Interface.
    multiple: NotRequired[Literal[{"description": "Enable multi-tagging", "help": "Enable multi-tagging.", "label": "Enable", "name": "enable"}, {"description": "Disable multi-tagging", "help": "Disable multi-tagging.", "label": "Disable", "name": "disable"}]]  # Allow multiple tag selection.
    color: NotRequired[int]  # Color of icon on the GUI.
    tags: NotRequired[list[dict[str, Any]]]  # Tags.


class ObjectTagging:
    """
    Configure object tagging.
    
    Path: system/object_tagging
    Category: cmdb
    Primary Key: category
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        category: str | None = ...,
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
        category: str,
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
        category: str | None = ...,
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
        category: str | None = ...,
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
        category: str | None = ...,
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
        payload_dict: ObjectTaggingPayload | None = ...,
        category: str | None = ...,
        address: Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}] | None = ...,
        device: Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}] | None = ...,
        interface: Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}] | None = ...,
        multiple: Literal[{"description": "Enable multi-tagging", "help": "Enable multi-tagging.", "label": "Enable", "name": "enable"}, {"description": "Disable multi-tagging", "help": "Disable multi-tagging.", "label": "Disable", "name": "disable"}] | None = ...,
        color: int | None = ...,
        tags: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ObjectTaggingPayload | None = ...,
        category: str | None = ...,
        address: Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}] | None = ...,
        device: Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}] | None = ...,
        interface: Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}] | None = ...,
        multiple: Literal[{"description": "Enable multi-tagging", "help": "Enable multi-tagging.", "label": "Enable", "name": "enable"}, {"description": "Disable multi-tagging", "help": "Disable multi-tagging.", "label": "Disable", "name": "disable"}] | None = ...,
        color: int | None = ...,
        tags: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        category: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        category: str,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: ObjectTaggingPayload | None = ...,
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
    "ObjectTagging",
    "ObjectTaggingPayload",
]