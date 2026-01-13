from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class VxlanPayload(TypedDict, total=False):
    """
    Type hints for system/vxlan payload fields.
    
    Configure VXLAN devices.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.evpn.EvpnEndpoint` (via: evpn-id)
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: VxlanPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # VXLAN device or interface name. Must be a unique interface n
    interface: str  # Outgoing interface for VXLAN encapsulated traffic.
    vni: int  # VXLAN network ID.
    ip_version: Literal[{"description": "Use IPv4 unicast addressing over the VXLAN", "help": "Use IPv4 unicast addressing over the VXLAN.", "label": "Ipv4 Unicast", "name": "ipv4-unicast"}, {"description": "Use IPv6 unicast addressing over the VXLAN", "help": "Use IPv6 unicast addressing over the VXLAN.", "label": "Ipv6 Unicast", "name": "ipv6-unicast"}, {"description": "Use IPv4 multicast addressing over the VXLAN", "help": "Use IPv4 multicast addressing over the VXLAN.", "label": "Ipv4 Multicast", "name": "ipv4-multicast"}, {"description": "Use IPv6 multicast addressing over the VXLAN", "help": "Use IPv6 multicast addressing over the VXLAN.", "label": "Ipv6 Multicast", "name": "ipv6-multicast"}]  # IP version to use for the VXLAN interface and so for communi
    remote_ip: NotRequired[list[dict[str, Any]]]  # IPv4 address of the VXLAN interface on the device at the rem
    local_ip: NotRequired[str]  # IPv4 address to use as the source address for egress VXLAN p
    remote_ip6: list[dict[str, Any]]  # IPv6 IP address of the VXLAN interface on the device at the 
    local_ip6: NotRequired[str]  # IPv6 address to use as the source address for egress VXLAN p
    dstport: NotRequired[int]  # VXLAN destination port (1 - 65535, default = 4789).
    multicast_ttl: int  # VXLAN multicast TTL (1-255, default = 0).
    evpn_id: NotRequired[int]  # EVPN instance.
    learn_from_traffic: NotRequired[Literal[{"description": "Enable VXLAN MAC learning from traffic", "help": "Enable VXLAN MAC learning from traffic.", "label": "Enable", "name": "enable"}, {"description": "Disable VXLAN MAC learning from traffic", "help": "Disable VXLAN MAC learning from traffic.", "label": "Disable", "name": "disable"}]]  # Enable/disable VXLAN MAC learning from traffic.


class Vxlan:
    """
    Configure VXLAN devices.
    
    Path: system/vxlan
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
        payload_dict: VxlanPayload | None = ...,
        name: str | None = ...,
        interface: str | None = ...,
        vni: int | None = ...,
        ip_version: Literal[{"description": "Use IPv4 unicast addressing over the VXLAN", "help": "Use IPv4 unicast addressing over the VXLAN.", "label": "Ipv4 Unicast", "name": "ipv4-unicast"}, {"description": "Use IPv6 unicast addressing over the VXLAN", "help": "Use IPv6 unicast addressing over the VXLAN.", "label": "Ipv6 Unicast", "name": "ipv6-unicast"}, {"description": "Use IPv4 multicast addressing over the VXLAN", "help": "Use IPv4 multicast addressing over the VXLAN.", "label": "Ipv4 Multicast", "name": "ipv4-multicast"}, {"description": "Use IPv6 multicast addressing over the VXLAN", "help": "Use IPv6 multicast addressing over the VXLAN.", "label": "Ipv6 Multicast", "name": "ipv6-multicast"}] | None = ...,
        remote_ip: list[dict[str, Any]] | None = ...,
        local_ip: str | None = ...,
        remote_ip6: list[dict[str, Any]] | None = ...,
        local_ip6: str | None = ...,
        dstport: int | None = ...,
        multicast_ttl: int | None = ...,
        evpn_id: int | None = ...,
        learn_from_traffic: Literal[{"description": "Enable VXLAN MAC learning from traffic", "help": "Enable VXLAN MAC learning from traffic.", "label": "Enable", "name": "enable"}, {"description": "Disable VXLAN MAC learning from traffic", "help": "Disable VXLAN MAC learning from traffic.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: VxlanPayload | None = ...,
        name: str | None = ...,
        interface: str | None = ...,
        vni: int | None = ...,
        ip_version: Literal[{"description": "Use IPv4 unicast addressing over the VXLAN", "help": "Use IPv4 unicast addressing over the VXLAN.", "label": "Ipv4 Unicast", "name": "ipv4-unicast"}, {"description": "Use IPv6 unicast addressing over the VXLAN", "help": "Use IPv6 unicast addressing over the VXLAN.", "label": "Ipv6 Unicast", "name": "ipv6-unicast"}, {"description": "Use IPv4 multicast addressing over the VXLAN", "help": "Use IPv4 multicast addressing over the VXLAN.", "label": "Ipv4 Multicast", "name": "ipv4-multicast"}, {"description": "Use IPv6 multicast addressing over the VXLAN", "help": "Use IPv6 multicast addressing over the VXLAN.", "label": "Ipv6 Multicast", "name": "ipv6-multicast"}] | None = ...,
        remote_ip: list[dict[str, Any]] | None = ...,
        local_ip: str | None = ...,
        remote_ip6: list[dict[str, Any]] | None = ...,
        local_ip6: str | None = ...,
        dstport: int | None = ...,
        multicast_ttl: int | None = ...,
        evpn_id: int | None = ...,
        learn_from_traffic: Literal[{"description": "Enable VXLAN MAC learning from traffic", "help": "Enable VXLAN MAC learning from traffic.", "label": "Enable", "name": "enable"}, {"description": "Disable VXLAN MAC learning from traffic", "help": "Disable VXLAN MAC learning from traffic.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: VxlanPayload | None = ...,
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
    "Vxlan",
    "VxlanPayload",
]