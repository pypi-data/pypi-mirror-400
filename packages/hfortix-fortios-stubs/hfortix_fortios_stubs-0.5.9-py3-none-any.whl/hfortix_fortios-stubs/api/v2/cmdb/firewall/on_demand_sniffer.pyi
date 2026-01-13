from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class OnDemandSnifferPayload(TypedDict, total=False):
    """
    Type hints for firewall/on_demand_sniffer payload fields.
    
    Configure on-demand packet sniffer.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: OnDemandSnifferPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # On-demand packet sniffer name.
    interface: str  # Interface name that on-demand packet sniffer will take place
    max_packet_count: int  # Maximum number of packets to capture per on-demand packet sn
    hosts: NotRequired[list[dict[str, Any]]]  # IPv4 or IPv6 hosts to filter in this traffic sniffer.
    ports: NotRequired[list[dict[str, Any]]]  # Ports to filter for in this traffic sniffer.
    protocols: NotRequired[list[dict[str, Any]]]  # Protocols to filter in this traffic sniffer.
    non_ip_packet: NotRequired[Literal[{"description": "Enable non-IP packets to be included capture", "help": "Enable non-IP packets to be included capture.", "label": "Enable", "name": "enable"}, {"description": "Disable non-IP packets to be included in capture", "help": "Disable non-IP packets to be included in capture.", "label": "Disable", "name": "disable"}]]  # Include non-IP packets.
    advanced_filter: NotRequired[str]  # Advanced freeform filter that will be used over existing fil


class OnDemandSniffer:
    """
    Configure on-demand packet sniffer.
    
    Path: firewall/on_demand_sniffer
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
        payload_dict: OnDemandSnifferPayload | None = ...,
        name: str | None = ...,
        interface: str | None = ...,
        max_packet_count: int | None = ...,
        hosts: list[dict[str, Any]] | None = ...,
        ports: list[dict[str, Any]] | None = ...,
        protocols: list[dict[str, Any]] | None = ...,
        non_ip_packet: Literal[{"description": "Enable non-IP packets to be included capture", "help": "Enable non-IP packets to be included capture.", "label": "Enable", "name": "enable"}, {"description": "Disable non-IP packets to be included in capture", "help": "Disable non-IP packets to be included in capture.", "label": "Disable", "name": "disable"}] | None = ...,
        advanced_filter: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: OnDemandSnifferPayload | None = ...,
        name: str | None = ...,
        interface: str | None = ...,
        max_packet_count: int | None = ...,
        hosts: list[dict[str, Any]] | None = ...,
        ports: list[dict[str, Any]] | None = ...,
        protocols: list[dict[str, Any]] | None = ...,
        non_ip_packet: Literal[{"description": "Enable non-IP packets to be included capture", "help": "Enable non-IP packets to be included capture.", "label": "Enable", "name": "enable"}, {"description": "Disable non-IP packets to be included in capture", "help": "Disable non-IP packets to be included in capture.", "label": "Disable", "name": "disable"}] | None = ...,
        advanced_filter: str | None = ...,
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
        payload_dict: OnDemandSnifferPayload | None = ...,
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
    "OnDemandSniffer",
    "OnDemandSnifferPayload",
]