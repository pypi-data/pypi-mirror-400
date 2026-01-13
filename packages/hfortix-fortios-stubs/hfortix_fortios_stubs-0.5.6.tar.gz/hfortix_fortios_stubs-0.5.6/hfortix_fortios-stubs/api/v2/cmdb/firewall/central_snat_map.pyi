from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class CentralSnatMapPayload(TypedDict, total=False):
    """
    Type hints for firewall/central_snat_map payload fields.
    
    Configure IPv4 and IPv6 central SNAT policies.
    
    **Usage:**
        payload: CentralSnatMapPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    policyid: NotRequired[int]  # Policy ID.
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    status: NotRequired[Literal[{"description": "Enable this policy", "help": "Enable this policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy", "help": "Disable this policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable the active status of this policy.
    type: NotRequired[Literal[{"description": "Perform IPv4 source NAT", "help": "Perform IPv4 source NAT.", "label": "Ipv4", "name": "ipv4"}, {"description": "Perform IPv6 source NAT", "help": "Perform IPv6 source NAT.", "label": "Ipv6", "name": "ipv6"}]]  # IPv4/IPv6 source NAT.
    srcintf: list[dict[str, Any]]  # Source interface name from available interfaces.
    dstintf: list[dict[str, Any]]  # Destination interface name from available interfaces.
    orig_addr: list[dict[str, Any]]  # IPv4 Original address.
    orig_addr6: list[dict[str, Any]]  # IPv6 Original address.
    dst_addr: list[dict[str, Any]]  # IPv4 Destination address.
    dst_addr6: list[dict[str, Any]]  # IPv6 Destination address.
    protocol: NotRequired[int]  # Integer value for the protocol type (0 - 255).
    orig_port: NotRequired[str]  # Original TCP port (1 to 65535, 0 means any port).
    nat: NotRequired[Literal[{"description": "Disable source NAT", "help": "Disable source NAT.", "label": "Disable", "name": "disable"}, {"description": "Enable source NAT", "help": "Enable source NAT.", "label": "Enable", "name": "enable"}]]  # Enable/disable source NAT.
    nat46: NotRequired[Literal[{"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}]]  # Enable/disable NAT46.
    nat64: NotRequired[Literal[{"description": "Enable NAT64", "help": "Enable NAT64.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT64", "help": "Disable NAT64.", "label": "Disable", "name": "disable"}]]  # Enable/disable NAT64.
    nat_ippool: NotRequired[list[dict[str, Any]]]  # Name of the IP pools to be used to translate addresses from 
    nat_ippool6: NotRequired[list[dict[str, Any]]]  # IPv6 pools to be used for source NAT.
    port_preserve: NotRequired[Literal[{"description": "Use the original source port if it has not been used", "help": "Use the original source port if it has not been used.", "label": "Enable", "name": "enable"}, {"description": "Source NAT always changes the source port", "help": "Source NAT always changes the source port.", "label": "Disable", "name": "disable"}]]  # Enable/disable preservation of the original source port from
    port_random: NotRequired[Literal[{"description": "Enable random source port selection for source NAT", "help": "Enable random source port selection for source NAT.", "label": "Enable", "name": "enable"}, {"description": "Disable random source port selection for source NAT", "help": "Disable random source port selection for source NAT.", "label": "Disable", "name": "disable"}]]  # Enable/disable random source port selection for source NAT.
    nat_port: NotRequired[str]  # Translated port or port range (1 to 65535, 0 means any port)
    dst_port: NotRequired[str]  # Destination port or port range (1 to 65535, 0 means any port
    comments: NotRequired[str]  # Comment.


class CentralSnatMap:
    """
    Configure IPv4 and IPv6 central SNAT policies.
    
    Path: firewall/central_snat_map
    Category: cmdb
    Primary Key: policyid
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        policyid: int | None = ...,
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
        policyid: int,
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
        policyid: int | None = ...,
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
        policyid: int | None = ...,
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
        policyid: int | None = ...,
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
        payload_dict: CentralSnatMapPayload | None = ...,
        policyid: int | None = ...,
        uuid: str | None = ...,
        status: Literal[{"description": "Enable this policy", "help": "Enable this policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy", "help": "Disable this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        type: Literal[{"description": "Perform IPv4 source NAT", "help": "Perform IPv4 source NAT.", "label": "Ipv4", "name": "ipv4"}, {"description": "Perform IPv6 source NAT", "help": "Perform IPv6 source NAT.", "label": "Ipv6", "name": "ipv6"}] | None = ...,
        srcintf: list[dict[str, Any]] | None = ...,
        dstintf: list[dict[str, Any]] | None = ...,
        orig_addr: list[dict[str, Any]] | None = ...,
        orig_addr6: list[dict[str, Any]] | None = ...,
        dst_addr: list[dict[str, Any]] | None = ...,
        dst_addr6: list[dict[str, Any]] | None = ...,
        protocol: int | None = ...,
        orig_port: str | None = ...,
        nat: Literal[{"description": "Disable source NAT", "help": "Disable source NAT.", "label": "Disable", "name": "disable"}, {"description": "Enable source NAT", "help": "Enable source NAT.", "label": "Enable", "name": "enable"}] | None = ...,
        nat46: Literal[{"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}] | None = ...,
        nat64: Literal[{"description": "Enable NAT64", "help": "Enable NAT64.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT64", "help": "Disable NAT64.", "label": "Disable", "name": "disable"}] | None = ...,
        nat_ippool: list[dict[str, Any]] | None = ...,
        nat_ippool6: list[dict[str, Any]] | None = ...,
        port_preserve: Literal[{"description": "Use the original source port if it has not been used", "help": "Use the original source port if it has not been used.", "label": "Enable", "name": "enable"}, {"description": "Source NAT always changes the source port", "help": "Source NAT always changes the source port.", "label": "Disable", "name": "disable"}] | None = ...,
        port_random: Literal[{"description": "Enable random source port selection for source NAT", "help": "Enable random source port selection for source NAT.", "label": "Enable", "name": "enable"}, {"description": "Disable random source port selection for source NAT", "help": "Disable random source port selection for source NAT.", "label": "Disable", "name": "disable"}] | None = ...,
        nat_port: str | None = ...,
        dst_port: str | None = ...,
        comments: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: CentralSnatMapPayload | None = ...,
        policyid: int | None = ...,
        uuid: str | None = ...,
        status: Literal[{"description": "Enable this policy", "help": "Enable this policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy", "help": "Disable this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        type: Literal[{"description": "Perform IPv4 source NAT", "help": "Perform IPv4 source NAT.", "label": "Ipv4", "name": "ipv4"}, {"description": "Perform IPv6 source NAT", "help": "Perform IPv6 source NAT.", "label": "Ipv6", "name": "ipv6"}] | None = ...,
        srcintf: list[dict[str, Any]] | None = ...,
        dstintf: list[dict[str, Any]] | None = ...,
        orig_addr: list[dict[str, Any]] | None = ...,
        orig_addr6: list[dict[str, Any]] | None = ...,
        dst_addr: list[dict[str, Any]] | None = ...,
        dst_addr6: list[dict[str, Any]] | None = ...,
        protocol: int | None = ...,
        orig_port: str | None = ...,
        nat: Literal[{"description": "Disable source NAT", "help": "Disable source NAT.", "label": "Disable", "name": "disable"}, {"description": "Enable source NAT", "help": "Enable source NAT.", "label": "Enable", "name": "enable"}] | None = ...,
        nat46: Literal[{"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}] | None = ...,
        nat64: Literal[{"description": "Enable NAT64", "help": "Enable NAT64.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT64", "help": "Disable NAT64.", "label": "Disable", "name": "disable"}] | None = ...,
        nat_ippool: list[dict[str, Any]] | None = ...,
        nat_ippool6: list[dict[str, Any]] | None = ...,
        port_preserve: Literal[{"description": "Use the original source port if it has not been used", "help": "Use the original source port if it has not been used.", "label": "Enable", "name": "enable"}, {"description": "Source NAT always changes the source port", "help": "Source NAT always changes the source port.", "label": "Disable", "name": "disable"}] | None = ...,
        port_random: Literal[{"description": "Enable random source port selection for source NAT", "help": "Enable random source port selection for source NAT.", "label": "Enable", "name": "enable"}, {"description": "Disable random source port selection for source NAT", "help": "Disable random source port selection for source NAT.", "label": "Disable", "name": "disable"}] | None = ...,
        nat_port: str | None = ...,
        dst_port: str | None = ...,
        comments: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        policyid: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        policyid: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: CentralSnatMapPayload | None = ...,
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
    "CentralSnatMap",
    "CentralSnatMapPayload",
]