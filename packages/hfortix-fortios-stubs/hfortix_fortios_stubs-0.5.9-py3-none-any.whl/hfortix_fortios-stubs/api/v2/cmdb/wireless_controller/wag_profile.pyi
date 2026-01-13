from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class WagProfilePayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/wag_profile payload fields.
    
    Configure wireless access gateway (WAG) profiles used for tunnels on AP.
    
    **Usage:**
        payload: WagProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Tunnel profile name.
    comment: NotRequired[str]  # Comment.
    tunnel_type: NotRequired[Literal[{"description": "L2TPV3 Ethernet Pseudowire", "help": "L2TPV3 Ethernet Pseudowire.", "label": "L2Tpv3", "name": "l2tpv3"}, {"description": "GRE Ethernet tunnel", "help": "GRE Ethernet tunnel.", "label": "Gre", "name": "gre"}]]  # Tunnel type.
    wag_ip: NotRequired[str]  # IP Address of the wireless access gateway.
    wag_port: NotRequired[int]  # UDP port of the wireless access gateway.
    ping_interval: NotRequired[int]  # Interval between two tunnel monitoring echo packets (1 - 655
    ping_number: NotRequired[int]  # Number of the tunnel monitoring echo packets (1 - 65535, def
    return_packet_timeout: NotRequired[int]  # Window of time for the return packets from the tunnel's remo
    dhcp_ip_addr: NotRequired[str]  # IP address of the monitoring DHCP request packet sent throug


class WagProfile:
    """
    Configure wireless access gateway (WAG) profiles used for tunnels on AP.
    
    Path: wireless_controller/wag_profile
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
        payload_dict: WagProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        tunnel_type: Literal[{"description": "L2TPV3 Ethernet Pseudowire", "help": "L2TPV3 Ethernet Pseudowire.", "label": "L2Tpv3", "name": "l2tpv3"}, {"description": "GRE Ethernet tunnel", "help": "GRE Ethernet tunnel.", "label": "Gre", "name": "gre"}] | None = ...,
        wag_ip: str | None = ...,
        wag_port: int | None = ...,
        ping_interval: int | None = ...,
        ping_number: int | None = ...,
        return_packet_timeout: int | None = ...,
        dhcp_ip_addr: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: WagProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        tunnel_type: Literal[{"description": "L2TPV3 Ethernet Pseudowire", "help": "L2TPV3 Ethernet Pseudowire.", "label": "L2Tpv3", "name": "l2tpv3"}, {"description": "GRE Ethernet tunnel", "help": "GRE Ethernet tunnel.", "label": "Gre", "name": "gre"}] | None = ...,
        wag_ip: str | None = ...,
        wag_port: int | None = ...,
        ping_interval: int | None = ...,
        ping_number: int | None = ...,
        return_packet_timeout: int | None = ...,
        dhcp_ip_addr: str | None = ...,
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
        payload_dict: WagProfilePayload | None = ...,
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
    "WagProfile",
    "WagProfilePayload",
]