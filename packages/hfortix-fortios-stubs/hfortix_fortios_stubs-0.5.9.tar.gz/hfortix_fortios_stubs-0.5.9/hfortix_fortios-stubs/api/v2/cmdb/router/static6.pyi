from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class Static6Payload(TypedDict, total=False):
    """
    Type hints for router/static6 payload fields.
    
    Configure IPv6 static routing tables.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.firewall.address6.Address6Endpoint` (via: dstaddr)
        - :class:`~.firewall.addrgrp6.Addrgrp6Endpoint` (via: dstaddr)
        - :class:`~.system.interface.InterfaceEndpoint` (via: device)

    **Usage:**
        payload: Static6Payload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    seq_num: NotRequired[int]  # Sequence number.
    status: NotRequired[Literal[{"description": "Enable static route", "help": "Enable static route.", "label": "Enable", "name": "enable"}, {"description": "Disable static route", "help": "Disable static route.", "label": "Disable", "name": "disable"}]]  # Enable/disable this static route.
    dst: str  # Destination IPv6 prefix.
    gateway: NotRequired[str]  # IPv6 address of the gateway.
    device: str  # Gateway out interface or tunnel.
    devindex: NotRequired[int]  # Device index (0 - 4294967295).
    distance: NotRequired[int]  # Administrative distance (1 - 255).
    weight: NotRequired[int]  # Administrative weight (0 - 255).
    priority: NotRequired[int]  # Administrative priority (1 - 65535).
    comment: NotRequired[str]  # Optional comments.
    blackhole: NotRequired[Literal[{"description": "Enable black hole", "help": "Enable black hole.", "label": "Enable", "name": "enable"}, {"description": "Disable black hole", "help": "Disable black hole.", "label": "Disable", "name": "disable"}]]  # Enable/disable black hole.
    dynamic_gateway: NotRequired[Literal[{"description": "Enable dynamic gateway", "help": "Enable dynamic gateway.", "label": "Enable", "name": "enable"}, {"description": "Disable dynamic gateway", "help": "Disable dynamic gateway.", "label": "Disable", "name": "disable"}]]  # Enable use of dynamic gateway retrieved from Router Advertis
    sdwan_zone: NotRequired[list[dict[str, Any]]]  # Choose SD-WAN Zone.
    dstaddr: NotRequired[str]  # Name of firewall address or address group.
    link_monitor_exempt: NotRequired[Literal[{"description": "Keep this static route when link monitor or health check is down", "help": "Keep this static route when link monitor or health check is down.", "label": "Enable", "name": "enable"}, {"description": "Withdraw this static route when link monitor or health check is down", "help": "Withdraw this static route when link monitor or health check is down. (default)", "label": "Disable", "name": "disable"}]]  # Enable/disable withdrawal of this static route when link mon
    vrf: NotRequired[int]  # Virtual Routing Forwarding ID.
    bfd: NotRequired[Literal[{"description": "Enable Bidirectional Forwarding Detection (BFD)", "help": "Enable Bidirectional Forwarding Detection (BFD).", "label": "Enable", "name": "enable"}, {"description": "Disable Bidirectional Forwarding Detection (BFD)", "help": "Disable Bidirectional Forwarding Detection (BFD).", "label": "Disable", "name": "disable"}]]  # Enable/disable Bidirectional Forwarding Detection (BFD).
    tag: NotRequired[int]  # Route tag.


class Static6:
    """
    Configure IPv6 static routing tables.
    
    Path: router/static6
    Category: cmdb
    Primary Key: seq-num
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        seq_num: int | None = ...,
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
        seq_num: int,
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
        seq_num: int | None = ...,
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
        seq_num: int | None = ...,
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
        seq_num: int | None = ...,
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
        payload_dict: Static6Payload | None = ...,
        seq_num: int | None = ...,
        status: Literal[{"description": "Enable static route", "help": "Enable static route.", "label": "Enable", "name": "enable"}, {"description": "Disable static route", "help": "Disable static route.", "label": "Disable", "name": "disable"}] | None = ...,
        dst: str | None = ...,
        gateway: str | None = ...,
        device: str | None = ...,
        devindex: int | None = ...,
        distance: int | None = ...,
        weight: int | None = ...,
        priority: int | None = ...,
        comment: str | None = ...,
        blackhole: Literal[{"description": "Enable black hole", "help": "Enable black hole.", "label": "Enable", "name": "enable"}, {"description": "Disable black hole", "help": "Disable black hole.", "label": "Disable", "name": "disable"}] | None = ...,
        dynamic_gateway: Literal[{"description": "Enable dynamic gateway", "help": "Enable dynamic gateway.", "label": "Enable", "name": "enable"}, {"description": "Disable dynamic gateway", "help": "Disable dynamic gateway.", "label": "Disable", "name": "disable"}] | None = ...,
        sdwan_zone: list[dict[str, Any]] | None = ...,
        dstaddr: str | None = ...,
        link_monitor_exempt: Literal[{"description": "Keep this static route when link monitor or health check is down", "help": "Keep this static route when link monitor or health check is down.", "label": "Enable", "name": "enable"}, {"description": "Withdraw this static route when link monitor or health check is down", "help": "Withdraw this static route when link monitor or health check is down. (default)", "label": "Disable", "name": "disable"}] | None = ...,
        vrf: int | None = ...,
        bfd: Literal[{"description": "Enable Bidirectional Forwarding Detection (BFD)", "help": "Enable Bidirectional Forwarding Detection (BFD).", "label": "Enable", "name": "enable"}, {"description": "Disable Bidirectional Forwarding Detection (BFD)", "help": "Disable Bidirectional Forwarding Detection (BFD).", "label": "Disable", "name": "disable"}] | None = ...,
        tag: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: Static6Payload | None = ...,
        seq_num: int | None = ...,
        status: Literal[{"description": "Enable static route", "help": "Enable static route.", "label": "Enable", "name": "enable"}, {"description": "Disable static route", "help": "Disable static route.", "label": "Disable", "name": "disable"}] | None = ...,
        dst: str | None = ...,
        gateway: str | None = ...,
        device: str | None = ...,
        devindex: int | None = ...,
        distance: int | None = ...,
        weight: int | None = ...,
        priority: int | None = ...,
        comment: str | None = ...,
        blackhole: Literal[{"description": "Enable black hole", "help": "Enable black hole.", "label": "Enable", "name": "enable"}, {"description": "Disable black hole", "help": "Disable black hole.", "label": "Disable", "name": "disable"}] | None = ...,
        dynamic_gateway: Literal[{"description": "Enable dynamic gateway", "help": "Enable dynamic gateway.", "label": "Enable", "name": "enable"}, {"description": "Disable dynamic gateway", "help": "Disable dynamic gateway.", "label": "Disable", "name": "disable"}] | None = ...,
        sdwan_zone: list[dict[str, Any]] | None = ...,
        dstaddr: str | None = ...,
        link_monitor_exempt: Literal[{"description": "Keep this static route when link monitor or health check is down", "help": "Keep this static route when link monitor or health check is down.", "label": "Enable", "name": "enable"}, {"description": "Withdraw this static route when link monitor or health check is down", "help": "Withdraw this static route when link monitor or health check is down. (default)", "label": "Disable", "name": "disable"}] | None = ...,
        vrf: int | None = ...,
        bfd: Literal[{"description": "Enable Bidirectional Forwarding Detection (BFD)", "help": "Enable Bidirectional Forwarding Detection (BFD).", "label": "Enable", "name": "enable"}, {"description": "Disable Bidirectional Forwarding Detection (BFD)", "help": "Disable Bidirectional Forwarding Detection (BFD).", "label": "Disable", "name": "disable"}] | None = ...,
        tag: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        seq_num: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        seq_num: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: Static6Payload | None = ...,
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
    "Static6",
    "Static6Payload",
]