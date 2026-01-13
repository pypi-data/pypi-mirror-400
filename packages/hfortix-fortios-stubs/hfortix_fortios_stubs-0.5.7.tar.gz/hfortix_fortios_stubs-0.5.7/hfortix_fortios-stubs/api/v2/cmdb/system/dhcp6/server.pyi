from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ServerPayload(TypedDict, total=False):
    """
    Type hints for system/dhcp6/server payload fields.
    
    Configure DHCPv6 servers.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface, upstream-interface)

    **Usage:**
        payload: ServerPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    id: int  # ID.
    status: NotRequired[Literal[{"description": "Enable this DHCPv6 server configuration", "help": "Enable this DHCPv6 server configuration.", "label": "Disable", "name": "disable"}, {"description": "Disable this DHCPv6 server configuration", "help": "Disable this DHCPv6 server configuration.", "label": "Enable", "name": "enable"}]]  # Enable/disable this DHCPv6 configuration.
    rapid_commit: NotRequired[Literal[{"description": "Do not allow rapid commit", "help": "Do not allow rapid commit.", "label": "Disable", "name": "disable"}, {"description": "Allow rapid commit", "help": "Allow rapid commit.", "label": "Enable", "name": "enable"}]]  # Enable/disable allow/disallow rapid commit.
    lease_time: NotRequired[int]  # Lease time in seconds, 0 means unlimited.
    dns_service: NotRequired[Literal[{"description": "Delegated DNS settings", "help": "Delegated DNS settings.", "label": "Delegated", "name": "delegated"}, {"description": "Clients are assigned the FortiGate\u0027s configured DNS servers", "help": "Clients are assigned the FortiGate\u0027s configured DNS servers.", "label": "Default", "name": "default"}, {"description": "Specify up to 3 DNS servers in the DHCPv6 server configuration", "help": "Specify up to 3 DNS servers in the DHCPv6 server configuration.", "label": "Specify", "name": "specify"}]]  # Options for assigning DNS servers to DHCPv6 clients.
    dns_search_list: NotRequired[Literal[{"description": "Delegated the DNS search list", "help": "Delegated the DNS search list.", "label": "Delegated", "name": "delegated"}, {"description": "Specify the DNS search list", "help": "Specify the DNS search list.", "label": "Specify", "name": "specify"}]]  # DNS search list options.
    dns_server1: NotRequired[str]  # DNS server 1.
    dns_server2: NotRequired[str]  # DNS server 2.
    dns_server3: NotRequired[str]  # DNS server 3.
    dns_server4: NotRequired[str]  # DNS server 4.
    domain: NotRequired[str]  # Domain name suffix for the IP addresses that the DHCP server
    subnet: str  # Subnet or subnet-id if the IP mode is delegated.
    interface: str  # DHCP server can assign IP configurations to clients connecte
    delegated_prefix_route: NotRequired[Literal[{"description": "Disable automatically adding of routing for delegated prefix", "help": "Disable automatically adding of routing for delegated prefix.", "label": "Disable", "name": "disable"}, {"description": "Enable automatically adding of routing for delegated prefix", "help": "Enable automatically adding of routing for delegated prefix.", "label": "Enable", "name": "enable"}]]  # Enable/disable automatically adding of routing for delegated
    options: NotRequired[list[dict[str, Any]]]  # DHCPv6 options.
    upstream_interface: str  # Interface name from where delegated information is provided.
    delegated_prefix_iaid: int  # IAID of obtained delegated-prefix from the upstream interfac
    ip_mode: NotRequired[Literal[{"description": "Use range defined by start IP/end IP to assign client IP", "help": "Use range defined by start IP/end IP to assign client IP.", "label": "Range", "name": "range"}, {"description": "Use delegated prefix method to assign client IP", "help": "Use delegated prefix method to assign client IP.", "label": "Delegated", "name": "delegated"}]]  # Method used to assign client IP.
    prefix_mode: NotRequired[Literal[{"description": "Use delegated prefix from a DHCPv6 client", "help": "Use delegated prefix from a DHCPv6 client.", "label": "Dhcp6", "name": "dhcp6"}, {"description": "Use prefix from RA", "help": "Use prefix from RA.", "label": "Ra", "name": "ra"}]]  # Assigning a prefix from a DHCPv6 client or RA.
    prefix_range: NotRequired[list[dict[str, Any]]]  # DHCP prefix configuration.
    ip_range: NotRequired[list[dict[str, Any]]]  # DHCP IP range configuration.


class Server:
    """
    Configure DHCPv6 servers.
    
    Path: system/dhcp6/server
    Category: cmdb
    Primary Key: id
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        id: int | None = ...,
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
        id: int,
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
        id: int | None = ...,
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
        id: int | None = ...,
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
        id: int | None = ...,
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
        payload_dict: ServerPayload | None = ...,
        id: int | None = ...,
        status: Literal[{"description": "Enable this DHCPv6 server configuration", "help": "Enable this DHCPv6 server configuration.", "label": "Disable", "name": "disable"}, {"description": "Disable this DHCPv6 server configuration", "help": "Disable this DHCPv6 server configuration.", "label": "Enable", "name": "enable"}] | None = ...,
        rapid_commit: Literal[{"description": "Do not allow rapid commit", "help": "Do not allow rapid commit.", "label": "Disable", "name": "disable"}, {"description": "Allow rapid commit", "help": "Allow rapid commit.", "label": "Enable", "name": "enable"}] | None = ...,
        lease_time: int | None = ...,
        dns_service: Literal[{"description": "Delegated DNS settings", "help": "Delegated DNS settings.", "label": "Delegated", "name": "delegated"}, {"description": "Clients are assigned the FortiGate\u0027s configured DNS servers", "help": "Clients are assigned the FortiGate\u0027s configured DNS servers.", "label": "Default", "name": "default"}, {"description": "Specify up to 3 DNS servers in the DHCPv6 server configuration", "help": "Specify up to 3 DNS servers in the DHCPv6 server configuration.", "label": "Specify", "name": "specify"}] | None = ...,
        dns_search_list: Literal[{"description": "Delegated the DNS search list", "help": "Delegated the DNS search list.", "label": "Delegated", "name": "delegated"}, {"description": "Specify the DNS search list", "help": "Specify the DNS search list.", "label": "Specify", "name": "specify"}] | None = ...,
        dns_server1: str | None = ...,
        dns_server2: str | None = ...,
        dns_server3: str | None = ...,
        dns_server4: str | None = ...,
        domain: str | None = ...,
        subnet: str | None = ...,
        interface: str | None = ...,
        delegated_prefix_route: Literal[{"description": "Disable automatically adding of routing for delegated prefix", "help": "Disable automatically adding of routing for delegated prefix.", "label": "Disable", "name": "disable"}, {"description": "Enable automatically adding of routing for delegated prefix", "help": "Enable automatically adding of routing for delegated prefix.", "label": "Enable", "name": "enable"}] | None = ...,
        options: list[dict[str, Any]] | None = ...,
        upstream_interface: str | None = ...,
        delegated_prefix_iaid: int | None = ...,
        ip_mode: Literal[{"description": "Use range defined by start IP/end IP to assign client IP", "help": "Use range defined by start IP/end IP to assign client IP.", "label": "Range", "name": "range"}, {"description": "Use delegated prefix method to assign client IP", "help": "Use delegated prefix method to assign client IP.", "label": "Delegated", "name": "delegated"}] | None = ...,
        prefix_mode: Literal[{"description": "Use delegated prefix from a DHCPv6 client", "help": "Use delegated prefix from a DHCPv6 client.", "label": "Dhcp6", "name": "dhcp6"}, {"description": "Use prefix from RA", "help": "Use prefix from RA.", "label": "Ra", "name": "ra"}] | None = ...,
        prefix_range: list[dict[str, Any]] | None = ...,
        ip_range: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ServerPayload | None = ...,
        id: int | None = ...,
        status: Literal[{"description": "Enable this DHCPv6 server configuration", "help": "Enable this DHCPv6 server configuration.", "label": "Disable", "name": "disable"}, {"description": "Disable this DHCPv6 server configuration", "help": "Disable this DHCPv6 server configuration.", "label": "Enable", "name": "enable"}] | None = ...,
        rapid_commit: Literal[{"description": "Do not allow rapid commit", "help": "Do not allow rapid commit.", "label": "Disable", "name": "disable"}, {"description": "Allow rapid commit", "help": "Allow rapid commit.", "label": "Enable", "name": "enable"}] | None = ...,
        lease_time: int | None = ...,
        dns_service: Literal[{"description": "Delegated DNS settings", "help": "Delegated DNS settings.", "label": "Delegated", "name": "delegated"}, {"description": "Clients are assigned the FortiGate\u0027s configured DNS servers", "help": "Clients are assigned the FortiGate\u0027s configured DNS servers.", "label": "Default", "name": "default"}, {"description": "Specify up to 3 DNS servers in the DHCPv6 server configuration", "help": "Specify up to 3 DNS servers in the DHCPv6 server configuration.", "label": "Specify", "name": "specify"}] | None = ...,
        dns_search_list: Literal[{"description": "Delegated the DNS search list", "help": "Delegated the DNS search list.", "label": "Delegated", "name": "delegated"}, {"description": "Specify the DNS search list", "help": "Specify the DNS search list.", "label": "Specify", "name": "specify"}] | None = ...,
        dns_server1: str | None = ...,
        dns_server2: str | None = ...,
        dns_server3: str | None = ...,
        dns_server4: str | None = ...,
        domain: str | None = ...,
        subnet: str | None = ...,
        interface: str | None = ...,
        delegated_prefix_route: Literal[{"description": "Disable automatically adding of routing for delegated prefix", "help": "Disable automatically adding of routing for delegated prefix.", "label": "Disable", "name": "disable"}, {"description": "Enable automatically adding of routing for delegated prefix", "help": "Enable automatically adding of routing for delegated prefix.", "label": "Enable", "name": "enable"}] | None = ...,
        options: list[dict[str, Any]] | None = ...,
        upstream_interface: str | None = ...,
        delegated_prefix_iaid: int | None = ...,
        ip_mode: Literal[{"description": "Use range defined by start IP/end IP to assign client IP", "help": "Use range defined by start IP/end IP to assign client IP.", "label": "Range", "name": "range"}, {"description": "Use delegated prefix method to assign client IP", "help": "Use delegated prefix method to assign client IP.", "label": "Delegated", "name": "delegated"}] | None = ...,
        prefix_mode: Literal[{"description": "Use delegated prefix from a DHCPv6 client", "help": "Use delegated prefix from a DHCPv6 client.", "label": "Dhcp6", "name": "dhcp6"}, {"description": "Use prefix from RA", "help": "Use prefix from RA.", "label": "Ra", "name": "ra"}] | None = ...,
        prefix_range: list[dict[str, Any]] | None = ...,
        ip_range: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        id: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        id: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: ServerPayload | None = ...,
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
    "Server",
    "ServerPayload",
]