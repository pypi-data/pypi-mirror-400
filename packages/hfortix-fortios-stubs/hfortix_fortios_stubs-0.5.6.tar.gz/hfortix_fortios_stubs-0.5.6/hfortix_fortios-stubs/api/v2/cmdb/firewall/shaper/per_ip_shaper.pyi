from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class PerIpShaperPayload(TypedDict, total=False):
    """
    Type hints for firewall/shaper/per_ip_shaper payload fields.
    
    Configure per-IP traffic shaper.
    
    **Usage:**
        payload: PerIpShaperPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Traffic shaper name.
    max_bandwidth: NotRequired[int]  # Upper bandwidth limit enforced by this shaper (0 - 80000000)
    bandwidth_unit: NotRequired[Literal[{"description": "Kilobits per second", "help": "Kilobits per second.", "label": "Kbps", "name": "kbps"}, {"description": "Megabits per second", "help": "Megabits per second.", "label": "Mbps", "name": "mbps"}, {"description": "Gigabits per second", "help": "Gigabits per second.", "label": "Gbps", "name": "gbps"}]]  # Unit of measurement for maximum bandwidth for this shaper (K
    max_concurrent_session: NotRequired[int]  # Maximum number of concurrent sessions allowed by this shaper
    max_concurrent_tcp_session: NotRequired[int]  # Maximum number of concurrent TCP sessions allowed by this sh
    max_concurrent_udp_session: NotRequired[int]  # Maximum number of concurrent UDP sessions allowed by this sh
    diffserv_forward: NotRequired[Literal[{"description": "Enable setting forward (original) traffic DiffServ", "help": "Enable setting forward (original) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting forward (original) traffic DiffServ", "help": "Disable setting forward (original) traffic DiffServ.", "label": "Disable", "name": "disable"}]]  # Enable/disable changing the Forward (original) DiffServ sett
    diffserv_reverse: NotRequired[Literal[{"description": "Enable setting reverse (reply) traffic DiffServ", "help": "Enable setting reverse (reply) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting reverse (reply) traffic DiffServ", "help": "Disable setting reverse (reply) traffic DiffServ.", "label": "Disable", "name": "disable"}]]  # Enable/disable changing the Reverse (reply) DiffServ setting
    diffservcode_forward: NotRequired[str]  # Forward (original) DiffServ setting to be applied to traffic
    diffservcode_rev: NotRequired[str]  # Reverse (reply) DiffServ setting to be applied to traffic ac


class PerIpShaper:
    """
    Configure per-IP traffic shaper.
    
    Path: firewall/shaper/per_ip_shaper
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
        payload_dict: PerIpShaperPayload | None = ...,
        name: str | None = ...,
        max_bandwidth: int | None = ...,
        bandwidth_unit: Literal[{"description": "Kilobits per second", "help": "Kilobits per second.", "label": "Kbps", "name": "kbps"}, {"description": "Megabits per second", "help": "Megabits per second.", "label": "Mbps", "name": "mbps"}, {"description": "Gigabits per second", "help": "Gigabits per second.", "label": "Gbps", "name": "gbps"}] | None = ...,
        max_concurrent_session: int | None = ...,
        max_concurrent_tcp_session: int | None = ...,
        max_concurrent_udp_session: int | None = ...,
        diffserv_forward: Literal[{"description": "Enable setting forward (original) traffic DiffServ", "help": "Enable setting forward (original) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting forward (original) traffic DiffServ", "help": "Disable setting forward (original) traffic DiffServ.", "label": "Disable", "name": "disable"}] | None = ...,
        diffserv_reverse: Literal[{"description": "Enable setting reverse (reply) traffic DiffServ", "help": "Enable setting reverse (reply) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting reverse (reply) traffic DiffServ", "help": "Disable setting reverse (reply) traffic DiffServ.", "label": "Disable", "name": "disable"}] | None = ...,
        diffservcode_forward: str | None = ...,
        diffservcode_rev: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: PerIpShaperPayload | None = ...,
        name: str | None = ...,
        max_bandwidth: int | None = ...,
        bandwidth_unit: Literal[{"description": "Kilobits per second", "help": "Kilobits per second.", "label": "Kbps", "name": "kbps"}, {"description": "Megabits per second", "help": "Megabits per second.", "label": "Mbps", "name": "mbps"}, {"description": "Gigabits per second", "help": "Gigabits per second.", "label": "Gbps", "name": "gbps"}] | None = ...,
        max_concurrent_session: int | None = ...,
        max_concurrent_tcp_session: int | None = ...,
        max_concurrent_udp_session: int | None = ...,
        diffserv_forward: Literal[{"description": "Enable setting forward (original) traffic DiffServ", "help": "Enable setting forward (original) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting forward (original) traffic DiffServ", "help": "Disable setting forward (original) traffic DiffServ.", "label": "Disable", "name": "disable"}] | None = ...,
        diffserv_reverse: Literal[{"description": "Enable setting reverse (reply) traffic DiffServ", "help": "Enable setting reverse (reply) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting reverse (reply) traffic DiffServ", "help": "Disable setting reverse (reply) traffic DiffServ.", "label": "Disable", "name": "disable"}] | None = ...,
        diffservcode_forward: str | None = ...,
        diffservcode_rev: str | None = ...,
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
        payload_dict: PerIpShaperPayload | None = ...,
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
    "PerIpShaper",
    "PerIpShaperPayload",
]