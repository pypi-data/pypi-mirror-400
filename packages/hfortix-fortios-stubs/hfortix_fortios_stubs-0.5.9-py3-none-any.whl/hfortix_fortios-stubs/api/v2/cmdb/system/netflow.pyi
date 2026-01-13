from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class NetflowPayload(TypedDict, total=False):
    """
    Type hints for system/netflow payload fields.
    
    Configure NetFlow.
    
    **Usage:**
        payload: NetflowPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    active_flow_timeout: NotRequired[int]  # Timeout to report active flows (60 - 3600 sec, default = 180
    inactive_flow_timeout: NotRequired[int]  # Timeout for periodic report of finished flows (10 - 600 sec,
    template_tx_timeout: NotRequired[int]  # Timeout for periodic template flowset transmission (60 - 864
    template_tx_counter: NotRequired[int]  # Counter of flowset records before resending a template flows
    session_cache_size: NotRequired[Literal[{"description": "Up to 0", "help": "Up to 0.5% of system RAM.", "label": "Min", "name": "min"}, {"description": "Up to 1% of system RAM", "help": "Up to 1% of system RAM.", "label": "Default", "name": "default"}, {"description": "Up to 2% of system RAM", "help": "Up to 2% of system RAM.", "label": "Max", "name": "max"}]]  # Maximum RAM usage allowed for Netflow session cache.
    exclusion_filters: NotRequired[list[dict[str, Any]]]  # Exclusion filters
    collectors: NotRequired[list[dict[str, Any]]]  # Netflow collectors.


class Netflow:
    """
    Configure NetFlow.
    
    Path: system/netflow
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
        payload_dict: NetflowPayload | None = ...,
        active_flow_timeout: int | None = ...,
        inactive_flow_timeout: int | None = ...,
        template_tx_timeout: int | None = ...,
        template_tx_counter: int | None = ...,
        session_cache_size: Literal[{"description": "Up to 0", "help": "Up to 0.5% of system RAM.", "label": "Min", "name": "min"}, {"description": "Up to 1% of system RAM", "help": "Up to 1% of system RAM.", "label": "Default", "name": "default"}, {"description": "Up to 2% of system RAM", "help": "Up to 2% of system RAM.", "label": "Max", "name": "max"}] | None = ...,
        exclusion_filters: list[dict[str, Any]] | None = ...,
        collectors: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: NetflowPayload | None = ...,
        active_flow_timeout: int | None = ...,
        inactive_flow_timeout: int | None = ...,
        template_tx_timeout: int | None = ...,
        template_tx_counter: int | None = ...,
        session_cache_size: Literal[{"description": "Up to 0", "help": "Up to 0.5% of system RAM.", "label": "Min", "name": "min"}, {"description": "Up to 1% of system RAM", "help": "Up to 1% of system RAM.", "label": "Default", "name": "default"}, {"description": "Up to 2% of system RAM", "help": "Up to 2% of system RAM.", "label": "Max", "name": "max"}] | None = ...,
        exclusion_filters: list[dict[str, Any]] | None = ...,
        collectors: list[dict[str, Any]] | None = ...,
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
        payload_dict: NetflowPayload | None = ...,
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
    "Netflow",
    "NetflowPayload",
]