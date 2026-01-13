from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class WccpPayload(TypedDict, total=False):
    """
    Type hints for system/wccp payload fields.
    
    Configure WCCP.
    
    **Usage:**
        payload: WccpPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    service_id: NotRequired[str]  # Service ID.
    router_id: NotRequired[str]  # IP address known to all cache engines. If all cache engines 
    cache_id: NotRequired[str]  # IP address known to all routers. If the addresses are the sa
    group_address: NotRequired[str]  # IP multicast address used by the cache routers. For the Fort
    server_list: NotRequired[list[dict[str, Any]]]  # IP addresses and netmasks for up to four cache servers.
    router_list: NotRequired[list[dict[str, Any]]]  # IP addresses of one or more WCCP routers.
    ports_defined: NotRequired[Literal[{"description": "Source port match", "help": "Source port match.", "label": "Source", "name": "source"}, {"description": "Destination port match", "help": "Destination port match.", "label": "Destination", "name": "destination"}]]  # Match method.
    server_type: NotRequired[Literal[{"description": "Forward server", "help": "Forward server.", "label": "Forward", "name": "forward"}, {"description": "Proxy server", "help": "Proxy server.", "label": "Proxy", "name": "proxy"}]]  # Cache server type.
    ports: NotRequired[list[dict[str, Any]]]  # Service ports.
    authentication: NotRequired[Literal[{"description": "Enable MD5 authentication", "help": "Enable MD5 authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable MD5 authentication", "help": "Disable MD5 authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable MD5 authentication.
    password: NotRequired[str]  # Password for MD5 authentication.
    forward_method: NotRequired[Literal[{"description": "GRE encapsulation", "help": "GRE encapsulation.", "label": "Gre", "name": "GRE"}, {"description": "L2 rewrite", "help": "L2 rewrite.", "label": "L2", "name": "L2"}, {"description": "GRE or L2", "help": "GRE or L2.", "label": "Any", "name": "any"}]]  # Method used to forward traffic to the cache servers.
    cache_engine_method: NotRequired[Literal[{"description": "GRE encapsulation", "help": "GRE encapsulation.", "label": "Gre", "name": "GRE"}, {"description": "L2 rewrite", "help": "L2 rewrite.", "label": "L2", "name": "L2"}]]  # Method used to forward traffic to the routers or to return t
    service_type: NotRequired[Literal[{"description": "auto    standard:Standard service", "help": "auto", "label": "Auto", "name": "auto"}, {"help": "Standard service.", "label": "Standard", "name": "standard"}, {"description": "Dynamic service", "help": "Dynamic service.", "label": "Dynamic", "name": "dynamic"}]]  # WCCP service type used by the cache server for logical inter
    primary_hash: NotRequired[Literal[{"description": "Source IP hash", "help": "Source IP hash.", "label": "Src Ip", "name": "src-ip"}, {"description": "Destination IP hash", "help": "Destination IP hash.", "label": "Dst Ip", "name": "dst-ip"}, {"description": "Source port hash", "help": "Source port hash.", "label": "Src Port", "name": "src-port"}, {"description": "Destination port hash", "help": "Destination port hash.", "label": "Dst Port", "name": "dst-port"}]]  # Hash method.
    priority: NotRequired[int]  # Service priority.
    protocol: NotRequired[int]  # Service protocol.
    assignment_weight: NotRequired[int]  # Assignment of hash weight/ratio for the WCCP cache engine.
    assignment_bucket_format: NotRequired[Literal[{"description": "WCCP-v2 bucket format", "help": "WCCP-v2 bucket format.", "label": "Wccp V2", "name": "wccp-v2"}, {"description": "Cisco bucket format", "help": "Cisco bucket format.", "label": "Cisco Implementation", "name": "cisco-implementation"}]]  # Assignment bucket format for the WCCP cache engine.
    return_method: NotRequired[Literal[{"description": "GRE encapsulation", "help": "GRE encapsulation.", "label": "Gre", "name": "GRE"}, {"description": "L2 rewrite", "help": "L2 rewrite.", "label": "L2", "name": "L2"}, {"description": "GRE or L2", "help": "GRE or L2.", "label": "Any", "name": "any"}]]  # Method used to decline a redirected packet and return it to 
    assignment_method: NotRequired[Literal[{"description": "HASH assignment method", "help": "HASH assignment method.", "label": "Hash", "name": "HASH"}, {"description": "MASK assignment method", "help": "MASK assignment method.", "label": "Mask", "name": "MASK"}, {"description": "HASH or MASK", "help": "HASH or MASK.", "label": "Any", "name": "any"}]]  # Hash key assignment preference.
    assignment_srcaddr_mask: NotRequired[str]  # Assignment source address mask.
    assignment_dstaddr_mask: NotRequired[str]  # Assignment destination address mask.


class Wccp:
    """
    Configure WCCP.
    
    Path: system/wccp
    Category: cmdb
    Primary Key: service-id
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        service_id: str | None = ...,
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
        service_id: str,
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
        service_id: str | None = ...,
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
        service_id: str | None = ...,
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
        service_id: str | None = ...,
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
        payload_dict: WccpPayload | None = ...,
        service_id: str | None = ...,
        router_id: str | None = ...,
        cache_id: str | None = ...,
        group_address: str | None = ...,
        server_list: list[dict[str, Any]] | None = ...,
        router_list: list[dict[str, Any]] | None = ...,
        ports_defined: Literal[{"description": "Source port match", "help": "Source port match.", "label": "Source", "name": "source"}, {"description": "Destination port match", "help": "Destination port match.", "label": "Destination", "name": "destination"}] | None = ...,
        server_type: Literal[{"description": "Forward server", "help": "Forward server.", "label": "Forward", "name": "forward"}, {"description": "Proxy server", "help": "Proxy server.", "label": "Proxy", "name": "proxy"}] | None = ...,
        ports: list[dict[str, Any]] | None = ...,
        authentication: Literal[{"description": "Enable MD5 authentication", "help": "Enable MD5 authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable MD5 authentication", "help": "Disable MD5 authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        password: str | None = ...,
        forward_method: Literal[{"description": "GRE encapsulation", "help": "GRE encapsulation.", "label": "Gre", "name": "GRE"}, {"description": "L2 rewrite", "help": "L2 rewrite.", "label": "L2", "name": "L2"}, {"description": "GRE or L2", "help": "GRE or L2.", "label": "Any", "name": "any"}] | None = ...,
        cache_engine_method: Literal[{"description": "GRE encapsulation", "help": "GRE encapsulation.", "label": "Gre", "name": "GRE"}, {"description": "L2 rewrite", "help": "L2 rewrite.", "label": "L2", "name": "L2"}] | None = ...,
        service_type: Literal[{"description": "auto    standard:Standard service", "help": "auto", "label": "Auto", "name": "auto"}, {"help": "Standard service.", "label": "Standard", "name": "standard"}, {"description": "Dynamic service", "help": "Dynamic service.", "label": "Dynamic", "name": "dynamic"}] | None = ...,
        primary_hash: Literal[{"description": "Source IP hash", "help": "Source IP hash.", "label": "Src Ip", "name": "src-ip"}, {"description": "Destination IP hash", "help": "Destination IP hash.", "label": "Dst Ip", "name": "dst-ip"}, {"description": "Source port hash", "help": "Source port hash.", "label": "Src Port", "name": "src-port"}, {"description": "Destination port hash", "help": "Destination port hash.", "label": "Dst Port", "name": "dst-port"}] | None = ...,
        priority: int | None = ...,
        protocol: int | None = ...,
        assignment_weight: int | None = ...,
        assignment_bucket_format: Literal[{"description": "WCCP-v2 bucket format", "help": "WCCP-v2 bucket format.", "label": "Wccp V2", "name": "wccp-v2"}, {"description": "Cisco bucket format", "help": "Cisco bucket format.", "label": "Cisco Implementation", "name": "cisco-implementation"}] | None = ...,
        return_method: Literal[{"description": "GRE encapsulation", "help": "GRE encapsulation.", "label": "Gre", "name": "GRE"}, {"description": "L2 rewrite", "help": "L2 rewrite.", "label": "L2", "name": "L2"}, {"description": "GRE or L2", "help": "GRE or L2.", "label": "Any", "name": "any"}] | None = ...,
        assignment_method: Literal[{"description": "HASH assignment method", "help": "HASH assignment method.", "label": "Hash", "name": "HASH"}, {"description": "MASK assignment method", "help": "MASK assignment method.", "label": "Mask", "name": "MASK"}, {"description": "HASH or MASK", "help": "HASH or MASK.", "label": "Any", "name": "any"}] | None = ...,
        assignment_srcaddr_mask: str | None = ...,
        assignment_dstaddr_mask: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: WccpPayload | None = ...,
        service_id: str | None = ...,
        router_id: str | None = ...,
        cache_id: str | None = ...,
        group_address: str | None = ...,
        server_list: list[dict[str, Any]] | None = ...,
        router_list: list[dict[str, Any]] | None = ...,
        ports_defined: Literal[{"description": "Source port match", "help": "Source port match.", "label": "Source", "name": "source"}, {"description": "Destination port match", "help": "Destination port match.", "label": "Destination", "name": "destination"}] | None = ...,
        server_type: Literal[{"description": "Forward server", "help": "Forward server.", "label": "Forward", "name": "forward"}, {"description": "Proxy server", "help": "Proxy server.", "label": "Proxy", "name": "proxy"}] | None = ...,
        ports: list[dict[str, Any]] | None = ...,
        authentication: Literal[{"description": "Enable MD5 authentication", "help": "Enable MD5 authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable MD5 authentication", "help": "Disable MD5 authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        password: str | None = ...,
        forward_method: Literal[{"description": "GRE encapsulation", "help": "GRE encapsulation.", "label": "Gre", "name": "GRE"}, {"description": "L2 rewrite", "help": "L2 rewrite.", "label": "L2", "name": "L2"}, {"description": "GRE or L2", "help": "GRE or L2.", "label": "Any", "name": "any"}] | None = ...,
        cache_engine_method: Literal[{"description": "GRE encapsulation", "help": "GRE encapsulation.", "label": "Gre", "name": "GRE"}, {"description": "L2 rewrite", "help": "L2 rewrite.", "label": "L2", "name": "L2"}] | None = ...,
        service_type: Literal[{"description": "auto    standard:Standard service", "help": "auto", "label": "Auto", "name": "auto"}, {"help": "Standard service.", "label": "Standard", "name": "standard"}, {"description": "Dynamic service", "help": "Dynamic service.", "label": "Dynamic", "name": "dynamic"}] | None = ...,
        primary_hash: Literal[{"description": "Source IP hash", "help": "Source IP hash.", "label": "Src Ip", "name": "src-ip"}, {"description": "Destination IP hash", "help": "Destination IP hash.", "label": "Dst Ip", "name": "dst-ip"}, {"description": "Source port hash", "help": "Source port hash.", "label": "Src Port", "name": "src-port"}, {"description": "Destination port hash", "help": "Destination port hash.", "label": "Dst Port", "name": "dst-port"}] | None = ...,
        priority: int | None = ...,
        protocol: int | None = ...,
        assignment_weight: int | None = ...,
        assignment_bucket_format: Literal[{"description": "WCCP-v2 bucket format", "help": "WCCP-v2 bucket format.", "label": "Wccp V2", "name": "wccp-v2"}, {"description": "Cisco bucket format", "help": "Cisco bucket format.", "label": "Cisco Implementation", "name": "cisco-implementation"}] | None = ...,
        return_method: Literal[{"description": "GRE encapsulation", "help": "GRE encapsulation.", "label": "Gre", "name": "GRE"}, {"description": "L2 rewrite", "help": "L2 rewrite.", "label": "L2", "name": "L2"}, {"description": "GRE or L2", "help": "GRE or L2.", "label": "Any", "name": "any"}] | None = ...,
        assignment_method: Literal[{"description": "HASH assignment method", "help": "HASH assignment method.", "label": "Hash", "name": "HASH"}, {"description": "MASK assignment method", "help": "MASK assignment method.", "label": "Mask", "name": "MASK"}, {"description": "HASH or MASK", "help": "HASH or MASK.", "label": "Any", "name": "any"}] | None = ...,
        assignment_srcaddr_mask: str | None = ...,
        assignment_dstaddr_mask: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        service_id: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        service_id: str,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: WccpPayload | None = ...,
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
    "Wccp",
    "WccpPayload",
]