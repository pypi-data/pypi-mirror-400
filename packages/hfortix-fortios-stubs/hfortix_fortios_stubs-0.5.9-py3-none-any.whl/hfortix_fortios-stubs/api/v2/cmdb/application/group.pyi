from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class GroupPayload(TypedDict, total=False):
    """
    Type hints for application/group payload fields.
    
    Configure firewall application groups.
    
    **Usage:**
        payload: GroupPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Application group name.
    comment: NotRequired[str]  # Comments.
    type: NotRequired[Literal[{"description": "Application ID", "help": "Application ID.", "label": "Application", "name": "application"}, {"description": "Application filter", "help": "Application filter.", "label": "Filter", "name": "filter"}]]  # Application group type.
    application: NotRequired[list[dict[str, Any]]]  # Application ID list.
    category: NotRequired[list[dict[str, Any]]]  # Application category ID list.
    risk: NotRequired[list[dict[str, Any]]]  # Risk, or impact, of allowing traffic from this application t
    protocols: NotRequired[list[dict[str, Any]]]  # Application protocol filter.
    vendor: NotRequired[list[dict[str, Any]]]  # Application vendor filter.
    technology: NotRequired[list[dict[str, Any]]]  # Application technology filter.
    behavior: NotRequired[list[dict[str, Any]]]  # Application behavior filter.
    popularity: NotRequired[Literal[{"description": "Popularity level 1", "help": "Popularity level 1.", "label": "1", "name": "1"}, {"description": "Popularity level 2", "help": "Popularity level 2.", "label": "2", "name": "2"}, {"description": "Popularity level 3", "help": "Popularity level 3.", "label": "3", "name": "3"}, {"description": "Popularity level 4", "help": "Popularity level 4.", "label": "4", "name": "4"}, {"description": "Popularity level 5", "help": "Popularity level 5.", "label": "5", "name": "5"}]]  # Application popularity filter (1 - 5, from least to most pop


class Group:
    """
    Configure firewall application groups.
    
    Path: application/group
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
        payload_dict: GroupPayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        type: Literal[{"description": "Application ID", "help": "Application ID.", "label": "Application", "name": "application"}, {"description": "Application filter", "help": "Application filter.", "label": "Filter", "name": "filter"}] | None = ...,
        application: list[dict[str, Any]] | None = ...,
        category: list[dict[str, Any]] | None = ...,
        risk: list[dict[str, Any]] | None = ...,
        protocols: list[dict[str, Any]] | None = ...,
        vendor: list[dict[str, Any]] | None = ...,
        technology: list[dict[str, Any]] | None = ...,
        behavior: list[dict[str, Any]] | None = ...,
        popularity: Literal[{"description": "Popularity level 1", "help": "Popularity level 1.", "label": "1", "name": "1"}, {"description": "Popularity level 2", "help": "Popularity level 2.", "label": "2", "name": "2"}, {"description": "Popularity level 3", "help": "Popularity level 3.", "label": "3", "name": "3"}, {"description": "Popularity level 4", "help": "Popularity level 4.", "label": "4", "name": "4"}, {"description": "Popularity level 5", "help": "Popularity level 5.", "label": "5", "name": "5"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: GroupPayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        type: Literal[{"description": "Application ID", "help": "Application ID.", "label": "Application", "name": "application"}, {"description": "Application filter", "help": "Application filter.", "label": "Filter", "name": "filter"}] | None = ...,
        application: list[dict[str, Any]] | None = ...,
        category: list[dict[str, Any]] | None = ...,
        risk: list[dict[str, Any]] | None = ...,
        protocols: list[dict[str, Any]] | None = ...,
        vendor: list[dict[str, Any]] | None = ...,
        technology: list[dict[str, Any]] | None = ...,
        behavior: list[dict[str, Any]] | None = ...,
        popularity: Literal[{"description": "Popularity level 1", "help": "Popularity level 1.", "label": "1", "name": "1"}, {"description": "Popularity level 2", "help": "Popularity level 2.", "label": "2", "name": "2"}, {"description": "Popularity level 3", "help": "Popularity level 3.", "label": "3", "name": "3"}, {"description": "Popularity level 4", "help": "Popularity level 4.", "label": "4", "name": "4"}, {"description": "Popularity level 5", "help": "Popularity level 5.", "label": "5", "name": "5"}] | None = ...,
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
        payload_dict: GroupPayload | None = ...,
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
    "Group",
    "GroupPayload",
]