from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class IppoolPayload(TypedDict, total=False):
    """
    Type hints for firewall/ippool payload fields.
    
    Configure IPv4 IP pools.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: arp-intf, associated-interface)

    **Usage:**
        payload: IppoolPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # IP pool name.
    type: NotRequired[Literal[{"help": "IP addresses in the IP pool can be shared by clients.", "label": "Overload", "name": "overload"}, {"description": "One to one mapping", "help": "One to one mapping.", "label": "One To One", "name": "one-to-one"}, {"description": "Fixed port range", "help": "Fixed port range.", "label": "Fixed Port Range", "name": "fixed-port-range"}, {"description": "Port block allocation", "help": "Port block allocation.", "label": "Port Block Allocation", "name": "port-block-allocation"}]]  # IP pool type: overload, one-to-one, fixed-port-range, port-b
    startip: str  # First IPv4 address (inclusive) in the range for the address 
    endip: str  # Final IPv4 address (inclusive) in the range for the address 
    startport: int  # First port number (inclusive) in the range for the address p
    endport: int  # Final port number (inclusive) in the range for the address p
    source_startip: str  # First IPv4 address (inclusive) in the range of the source ad
    source_endip: str  # Final IPv4 address (inclusive) in the range of the source ad
    block_size: int  # Number of addresses in a block (64 - 4096, default = 128).
    port_per_user: int  # Number of port for each user (32 - 60416, default = 0, which
    num_blocks_per_user: int  # Number of addresses blocks that can be used by a user (1 to 
    pba_timeout: NotRequired[int]  # Port block allocation timeout (seconds).
    pba_interim_log: NotRequired[int]  # Port block allocation interim logging interval (600 - 86400 
    permit_any_host: NotRequired[Literal[{"description": "Disable full cone NAT", "help": "Disable full cone NAT.", "label": "Disable", "name": "disable"}, {"description": "Enable full cone NAT", "help": "Enable full cone NAT.", "label": "Enable", "name": "enable"}]]  # Enable/disable fullcone NAT. Accept UDP packets from any hos
    arp_reply: NotRequired[Literal[{"description": "Disable ARP reply", "help": "Disable ARP reply.", "label": "Disable", "name": "disable"}, {"description": "Enable ARP reply", "help": "Enable ARP reply.", "label": "Enable", "name": "enable"}]]  # Enable/disable replying to ARP requests when an IP Pool is a
    arp_intf: NotRequired[str]  # Select an interface from available options that will reply t
    associated_interface: NotRequired[str]  # Associated interface name.
    comments: NotRequired[str]  # Comment.
    nat64: NotRequired[Literal[{"description": "Disable DNAT64", "help": "Disable DNAT64.", "label": "Disable", "name": "disable"}, {"description": "Enable DNAT64", "help": "Enable DNAT64.", "label": "Enable", "name": "enable"}]]  # Enable/disable NAT64.
    add_nat64_route: NotRequired[Literal[{"description": "Disable adding NAT64 route", "help": "Disable adding NAT64 route.", "label": "Disable", "name": "disable"}, {"description": "Enable adding NAT64 route", "help": "Enable adding NAT64 route.", "label": "Enable", "name": "enable"}]]  # Enable/disable adding NAT64 route.
    source_prefix6: str  # Source IPv6 network to be translated (format = xxxx:xxxx:xxx
    client_prefix_length: int  # Subnet length of a single deterministic NAT64 client (1 - 12
    tcp_session_quota: NotRequired[int]  # Maximum number of concurrent TCP sessions allowed per client
    udp_session_quota: NotRequired[int]  # Maximum number of concurrent UDP sessions allowed per client
    icmp_session_quota: NotRequired[int]  # Maximum number of concurrent ICMP sessions allowed per clien
    privileged_port_use_pba: NotRequired[Literal[{"description": "Select new nat port for privileged source ports from priviliged range 512-1023", "help": "Select new nat port for privileged source ports from priviliged range 512-1023.", "label": "Disable", "name": "disable"}, {"description": "Select new nat port for privileged source ports from client\u0027s port block", "help": "Select new nat port for privileged source ports from client\u0027s port block", "label": "Enable", "name": "enable"}]]  # Enable/disable selection of the external port from the port 
    subnet_broadcast_in_ippool: NotRequired[Literal[{"description": "Do not include the subnetwork address and broadcast IP address in the NAT64 IP pool", "help": "Do not include the subnetwork address and broadcast IP address in the NAT64 IP pool.", "label": "Disable", "name": "disable"}]]  # Enable/disable inclusion of the subnetwork address and broad


class Ippool:
    """
    Configure IPv4 IP pools.
    
    Path: firewall/ippool
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
        payload_dict: IppoolPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"help": "IP addresses in the IP pool can be shared by clients.", "label": "Overload", "name": "overload"}, {"description": "One to one mapping", "help": "One to one mapping.", "label": "One To One", "name": "one-to-one"}, {"description": "Fixed port range", "help": "Fixed port range.", "label": "Fixed Port Range", "name": "fixed-port-range"}, {"description": "Port block allocation", "help": "Port block allocation.", "label": "Port Block Allocation", "name": "port-block-allocation"}] | None = ...,
        startip: str | None = ...,
        endip: str | None = ...,
        startport: int | None = ...,
        endport: int | None = ...,
        source_startip: str | None = ...,
        source_endip: str | None = ...,
        block_size: int | None = ...,
        port_per_user: int | None = ...,
        num_blocks_per_user: int | None = ...,
        pba_timeout: int | None = ...,
        pba_interim_log: int | None = ...,
        permit_any_host: Literal[{"description": "Disable full cone NAT", "help": "Disable full cone NAT.", "label": "Disable", "name": "disable"}, {"description": "Enable full cone NAT", "help": "Enable full cone NAT.", "label": "Enable", "name": "enable"}] | None = ...,
        arp_reply: Literal[{"description": "Disable ARP reply", "help": "Disable ARP reply.", "label": "Disable", "name": "disable"}, {"description": "Enable ARP reply", "help": "Enable ARP reply.", "label": "Enable", "name": "enable"}] | None = ...,
        arp_intf: str | None = ...,
        associated_interface: str | None = ...,
        comments: str | None = ...,
        nat64: Literal[{"description": "Disable DNAT64", "help": "Disable DNAT64.", "label": "Disable", "name": "disable"}, {"description": "Enable DNAT64", "help": "Enable DNAT64.", "label": "Enable", "name": "enable"}] | None = ...,
        add_nat64_route: Literal[{"description": "Disable adding NAT64 route", "help": "Disable adding NAT64 route.", "label": "Disable", "name": "disable"}, {"description": "Enable adding NAT64 route", "help": "Enable adding NAT64 route.", "label": "Enable", "name": "enable"}] | None = ...,
        source_prefix6: str | None = ...,
        client_prefix_length: int | None = ...,
        tcp_session_quota: int | None = ...,
        udp_session_quota: int | None = ...,
        icmp_session_quota: int | None = ...,
        privileged_port_use_pba: Literal[{"description": "Select new nat port for privileged source ports from priviliged range 512-1023", "help": "Select new nat port for privileged source ports from priviliged range 512-1023.", "label": "Disable", "name": "disable"}, {"description": "Select new nat port for privileged source ports from client\u0027s port block", "help": "Select new nat port for privileged source ports from client\u0027s port block", "label": "Enable", "name": "enable"}] | None = ...,
        subnet_broadcast_in_ippool: Literal[{"description": "Do not include the subnetwork address and broadcast IP address in the NAT64 IP pool", "help": "Do not include the subnetwork address and broadcast IP address in the NAT64 IP pool.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: IppoolPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"help": "IP addresses in the IP pool can be shared by clients.", "label": "Overload", "name": "overload"}, {"description": "One to one mapping", "help": "One to one mapping.", "label": "One To One", "name": "one-to-one"}, {"description": "Fixed port range", "help": "Fixed port range.", "label": "Fixed Port Range", "name": "fixed-port-range"}, {"description": "Port block allocation", "help": "Port block allocation.", "label": "Port Block Allocation", "name": "port-block-allocation"}] | None = ...,
        startip: str | None = ...,
        endip: str | None = ...,
        startport: int | None = ...,
        endport: int | None = ...,
        source_startip: str | None = ...,
        source_endip: str | None = ...,
        block_size: int | None = ...,
        port_per_user: int | None = ...,
        num_blocks_per_user: int | None = ...,
        pba_timeout: int | None = ...,
        pba_interim_log: int | None = ...,
        permit_any_host: Literal[{"description": "Disable full cone NAT", "help": "Disable full cone NAT.", "label": "Disable", "name": "disable"}, {"description": "Enable full cone NAT", "help": "Enable full cone NAT.", "label": "Enable", "name": "enable"}] | None = ...,
        arp_reply: Literal[{"description": "Disable ARP reply", "help": "Disable ARP reply.", "label": "Disable", "name": "disable"}, {"description": "Enable ARP reply", "help": "Enable ARP reply.", "label": "Enable", "name": "enable"}] | None = ...,
        arp_intf: str | None = ...,
        associated_interface: str | None = ...,
        comments: str | None = ...,
        nat64: Literal[{"description": "Disable DNAT64", "help": "Disable DNAT64.", "label": "Disable", "name": "disable"}, {"description": "Enable DNAT64", "help": "Enable DNAT64.", "label": "Enable", "name": "enable"}] | None = ...,
        add_nat64_route: Literal[{"description": "Disable adding NAT64 route", "help": "Disable adding NAT64 route.", "label": "Disable", "name": "disable"}, {"description": "Enable adding NAT64 route", "help": "Enable adding NAT64 route.", "label": "Enable", "name": "enable"}] | None = ...,
        source_prefix6: str | None = ...,
        client_prefix_length: int | None = ...,
        tcp_session_quota: int | None = ...,
        udp_session_quota: int | None = ...,
        icmp_session_quota: int | None = ...,
        privileged_port_use_pba: Literal[{"description": "Select new nat port for privileged source ports from priviliged range 512-1023", "help": "Select new nat port for privileged source ports from priviliged range 512-1023.", "label": "Disable", "name": "disable"}, {"description": "Select new nat port for privileged source ports from client\u0027s port block", "help": "Select new nat port for privileged source ports from client\u0027s port block", "label": "Enable", "name": "enable"}] | None = ...,
        subnet_broadcast_in_ippool: Literal[{"description": "Do not include the subnetwork address and broadcast IP address in the NAT64 IP pool", "help": "Do not include the subnetwork address and broadcast IP address in the NAT64 IP pool.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: IppoolPayload | None = ...,
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
    "Ippool",
    "IppoolPayload",
]