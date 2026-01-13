from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class GenevePayload(TypedDict, total=False):
    """
    Type hints for system/geneve payload fields.
    
    Configure GENEVE devices.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: GenevePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # GENEVE device or interface name. Must be an unique interface
    interface: str  # Outgoing interface for GENEVE encapsulated traffic.
    vni: int  # GENEVE network ID.
    type: Literal[{"description": "Internal packet includes Ethernet header", "help": "Internal packet includes Ethernet header.", "label": "Ethernet", "name": "ethernet"}, {"description": "Internal packet does not include Ethernet header", "help": "Internal packet does not include Ethernet header.", "label": "Ppp", "name": "ppp"}]  # GENEVE type.
    ip_version: Literal[{"description": "Use IPv4 unicast addressing over the GENEVE", "help": "Use IPv4 unicast addressing over the GENEVE.", "label": "Ipv4 Unicast", "name": "ipv4-unicast"}, {"description": "Use IPv6 unicast addressing over the GENEVE", "help": "Use IPv6 unicast addressing over the GENEVE.", "label": "Ipv6 Unicast", "name": "ipv6-unicast"}]  # IP version to use for the GENEVE interface and so for commun
    remote_ip: str  # IPv4 address of the GENEVE interface on the device at the re
    remote_ip6: str  # IPv6 IP address of the GENEVE interface on the device at the
    dstport: NotRequired[int]  # GENEVE destination port (1 - 65535, default = 6081).


class Geneve:
    """
    Configure GENEVE devices.
    
    Path: system/geneve
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
        payload_dict: GenevePayload | None = ...,
        name: str | None = ...,
        interface: str | None = ...,
        vni: int | None = ...,
        type: Literal[{"description": "Internal packet includes Ethernet header", "help": "Internal packet includes Ethernet header.", "label": "Ethernet", "name": "ethernet"}, {"description": "Internal packet does not include Ethernet header", "help": "Internal packet does not include Ethernet header.", "label": "Ppp", "name": "ppp"}] | None = ...,
        ip_version: Literal[{"description": "Use IPv4 unicast addressing over the GENEVE", "help": "Use IPv4 unicast addressing over the GENEVE.", "label": "Ipv4 Unicast", "name": "ipv4-unicast"}, {"description": "Use IPv6 unicast addressing over the GENEVE", "help": "Use IPv6 unicast addressing over the GENEVE.", "label": "Ipv6 Unicast", "name": "ipv6-unicast"}] | None = ...,
        remote_ip: str | None = ...,
        remote_ip6: str | None = ...,
        dstport: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: GenevePayload | None = ...,
        name: str | None = ...,
        interface: str | None = ...,
        vni: int | None = ...,
        type: Literal[{"description": "Internal packet includes Ethernet header", "help": "Internal packet includes Ethernet header.", "label": "Ethernet", "name": "ethernet"}, {"description": "Internal packet does not include Ethernet header", "help": "Internal packet does not include Ethernet header.", "label": "Ppp", "name": "ppp"}] | None = ...,
        ip_version: Literal[{"description": "Use IPv4 unicast addressing over the GENEVE", "help": "Use IPv4 unicast addressing over the GENEVE.", "label": "Ipv4 Unicast", "name": "ipv4-unicast"}, {"description": "Use IPv6 unicast addressing over the GENEVE", "help": "Use IPv6 unicast addressing over the GENEVE.", "label": "Ipv6 Unicast", "name": "ipv6-unicast"}] | None = ...,
        remote_ip: str | None = ...,
        remote_ip6: str | None = ...,
        dstport: int | None = ...,
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
        payload_dict: GenevePayload | None = ...,
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
    "Geneve",
    "GenevePayload",
]