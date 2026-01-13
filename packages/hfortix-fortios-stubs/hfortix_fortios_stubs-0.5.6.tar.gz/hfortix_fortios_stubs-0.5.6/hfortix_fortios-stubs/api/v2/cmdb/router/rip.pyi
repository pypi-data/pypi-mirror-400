from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class RipPayload(TypedDict, total=False):
    """
    Type hints for router/rip payload fields.
    
    Configure RIP.
    
    **Usage:**
        payload: RipPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    default_information_originate: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable generation of default route.
    default_metric: NotRequired[int]  # Default metric.
    max_out_metric: NotRequired[int]  # Maximum metric allowed to output(0 means 'not set').
    distance: NotRequired[list[dict[str, Any]]]  # Distance.
    distribute_list: NotRequired[list[dict[str, Any]]]  # Distribute list.
    neighbor: NotRequired[list[dict[str, Any]]]  # Neighbor.
    network: NotRequired[list[dict[str, Any]]]  # Network.
    offset_list: NotRequired[list[dict[str, Any]]]  # Offset list.
    passive_interface: NotRequired[list[dict[str, Any]]]  # Passive interface configuration.
    redistribute: NotRequired[list[dict[str, Any]]]  # Redistribute configuration.
    update_timer: NotRequired[int]  # Update timer in seconds.
    timeout_timer: NotRequired[int]  # Timeout timer in seconds.
    garbage_timer: NotRequired[int]  # Garbage timer in seconds.
    version: NotRequired[Literal[{"description": "Version 1", "help": "Version 1.", "label": "1", "name": "1"}, {"description": "Version 2", "help": "Version 2.", "label": "2", "name": "2"}]]  # RIP version.
    interface: NotRequired[list[dict[str, Any]]]  # RIP interface configuration.


class Rip:
    """
    Configure RIP.
    
    Path: router/rip
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
        payload_dict: RipPayload | None = ...,
        default_information_originate: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        default_metric: int | None = ...,
        max_out_metric: int | None = ...,
        distance: list[dict[str, Any]] | None = ...,
        distribute_list: list[dict[str, Any]] | None = ...,
        neighbor: list[dict[str, Any]] | None = ...,
        network: list[dict[str, Any]] | None = ...,
        offset_list: list[dict[str, Any]] | None = ...,
        passive_interface: list[dict[str, Any]] | None = ...,
        redistribute: list[dict[str, Any]] | None = ...,
        update_timer: int | None = ...,
        timeout_timer: int | None = ...,
        garbage_timer: int | None = ...,
        version: Literal[{"description": "Version 1", "help": "Version 1.", "label": "1", "name": "1"}, {"description": "Version 2", "help": "Version 2.", "label": "2", "name": "2"}] | None = ...,
        interface: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: RipPayload | None = ...,
        default_information_originate: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        default_metric: int | None = ...,
        max_out_metric: int | None = ...,
        distance: list[dict[str, Any]] | None = ...,
        distribute_list: list[dict[str, Any]] | None = ...,
        neighbor: list[dict[str, Any]] | None = ...,
        network: list[dict[str, Any]] | None = ...,
        offset_list: list[dict[str, Any]] | None = ...,
        passive_interface: list[dict[str, Any]] | None = ...,
        redistribute: list[dict[str, Any]] | None = ...,
        update_timer: int | None = ...,
        timeout_timer: int | None = ...,
        garbage_timer: int | None = ...,
        version: Literal[{"description": "Version 1", "help": "Version 1.", "label": "1", "name": "1"}, {"description": "Version 2", "help": "Version 2.", "label": "2", "name": "2"}] | None = ...,
        interface: list[dict[str, Any]] | None = ...,
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
        payload_dict: RipPayload | None = ...,
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
    "Rip",
    "RipPayload",
]