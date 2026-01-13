from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ServerGroupPayload(TypedDict, total=False):
    """
    Type hints for icap/server_group payload fields.
    
    Configure an ICAP server group consisting of multiple forward servers. Supports failover and load balancing.
    
    **Usage:**
        payload: ServerGroupPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Configure an ICAP server group consisting one or multiple fo
    ldb_method: NotRequired[Literal[{"description": "Load balance traffic to forward servers based on assigned weights", "help": "Load balance traffic to forward servers based on assigned weights.", "label": "Weighted", "name": "weighted"}, {"description": "Send new sessions to the server with lowest session count", "help": "Send new sessions to the server with lowest session count.", "label": "Least Session", "name": "least-session"}, {"description": "Send new sessions to active server with high weight", "help": "Send new sessions to active server with high weight.", "label": "Active Passive", "name": "active-passive"}]]  # Load balance method.
    server_list: NotRequired[list[dict[str, Any]]]  # Add ICAP servers to a list to form a server group. Optionall


class ServerGroup:
    """
    Configure an ICAP server group consisting of multiple forward servers. Supports failover and load balancing.
    
    Path: icap/server_group
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
        payload_dict: ServerGroupPayload | None = ...,
        name: str | None = ...,
        ldb_method: Literal[{"description": "Load balance traffic to forward servers based on assigned weights", "help": "Load balance traffic to forward servers based on assigned weights.", "label": "Weighted", "name": "weighted"}, {"description": "Send new sessions to the server with lowest session count", "help": "Send new sessions to the server with lowest session count.", "label": "Least Session", "name": "least-session"}, {"description": "Send new sessions to active server with high weight", "help": "Send new sessions to active server with high weight.", "label": "Active Passive", "name": "active-passive"}] | None = ...,
        server_list: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ServerGroupPayload | None = ...,
        name: str | None = ...,
        ldb_method: Literal[{"description": "Load balance traffic to forward servers based on assigned weights", "help": "Load balance traffic to forward servers based on assigned weights.", "label": "Weighted", "name": "weighted"}, {"description": "Send new sessions to the server with lowest session count", "help": "Send new sessions to the server with lowest session count.", "label": "Least Session", "name": "least-session"}, {"description": "Send new sessions to active server with high weight", "help": "Send new sessions to active server with high weight.", "label": "Active Passive", "name": "active-passive"}] | None = ...,
        server_list: list[dict[str, Any]] | None = ...,
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
        payload_dict: ServerGroupPayload | None = ...,
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
    "ServerGroup",
    "ServerGroupPayload",
]