from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ForwardServerPayload(TypedDict, total=False):
    """
    Type hints for web_proxy/forward_server payload fields.
    
    Configure forward-server addresses.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: ForwardServerPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Server name.
    addr_type: NotRequired[Literal[{"description": "Use an IPv4 address for the forwarding proxy server", "help": "Use an IPv4 address for the forwarding proxy server.", "label": "Ip", "name": "ip"}, {"description": "Use an IPv6 address for the forwarding proxy server", "help": "Use an IPv6 address for the forwarding proxy server.", "label": "Ipv6", "name": "ipv6"}, {"description": "Use the FQDN for the forwarding proxy server", "help": "Use the FQDN for the forwarding proxy server.", "label": "Fqdn", "name": "fqdn"}]]  # Address type of the forwarding proxy server: IP or FQDN.
    ip: NotRequired[str]  # Forward proxy server IP address.
    ipv6: NotRequired[str]  # Forward proxy server IPv6 address.
    fqdn: NotRequired[str]  # Forward server Fully Qualified Domain Name (FQDN).
    port: NotRequired[int]  # Port number that the forwarding server expects to receive HT
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.
    comment: NotRequired[str]  # Comment.
    masquerade: NotRequired[Literal[{"help": "Enable use of the IP address of the outgoing interface as the client IP address.", "label": "Enable", "name": "enable"}, {"description": "Disable use of the IP address of the outgoing interface as the client IP address", "help": "Disable use of the IP address of the outgoing interface as the client IP address.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of the IP address of the outgoing interfa
    healthcheck: NotRequired[Literal[{"description": "Disable health checking", "help": "Disable health checking.", "label": "Disable", "name": "disable"}, {"description": "Enable health checking", "help": "Enable health checking.", "label": "Enable", "name": "enable"}]]  # Enable/disable forward server health checking. Attempts to c
    monitor: NotRequired[str]  # URL for forward server health check monitoring (default = ww
    server_down_option: NotRequired[Literal[{"description": "Block sessions until the server is back up", "help": "Block sessions until the server is back up.", "label": "Block", "name": "block"}, {"description": "Pass sessions to their destination bypassing the forward server", "help": "Pass sessions to their destination bypassing the forward server.", "label": "Pass", "name": "pass"}]]  # Action to take when the forward server is found to be down: 
    username: NotRequired[str]  # HTTP authentication user name.
    password: NotRequired[str]  # HTTP authentication password.


class ForwardServer:
    """
    Configure forward-server addresses.
    
    Path: web_proxy/forward_server
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
        payload_dict: ForwardServerPayload | None = ...,
        name: str | None = ...,
        addr_type: Literal[{"description": "Use an IPv4 address for the forwarding proxy server", "help": "Use an IPv4 address for the forwarding proxy server.", "label": "Ip", "name": "ip"}, {"description": "Use an IPv6 address for the forwarding proxy server", "help": "Use an IPv6 address for the forwarding proxy server.", "label": "Ipv6", "name": "ipv6"}, {"description": "Use the FQDN for the forwarding proxy server", "help": "Use the FQDN for the forwarding proxy server.", "label": "Fqdn", "name": "fqdn"}] | None = ...,
        ip: str | None = ...,
        ipv6: str | None = ...,
        fqdn: str | None = ...,
        port: int | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        comment: str | None = ...,
        masquerade: Literal[{"help": "Enable use of the IP address of the outgoing interface as the client IP address.", "label": "Enable", "name": "enable"}, {"description": "Disable use of the IP address of the outgoing interface as the client IP address", "help": "Disable use of the IP address of the outgoing interface as the client IP address.", "label": "Disable", "name": "disable"}] | None = ...,
        healthcheck: Literal[{"description": "Disable health checking", "help": "Disable health checking.", "label": "Disable", "name": "disable"}, {"description": "Enable health checking", "help": "Enable health checking.", "label": "Enable", "name": "enable"}] | None = ...,
        monitor: str | None = ...,
        server_down_option: Literal[{"description": "Block sessions until the server is back up", "help": "Block sessions until the server is back up.", "label": "Block", "name": "block"}, {"description": "Pass sessions to their destination bypassing the forward server", "help": "Pass sessions to their destination bypassing the forward server.", "label": "Pass", "name": "pass"}] | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ForwardServerPayload | None = ...,
        name: str | None = ...,
        addr_type: Literal[{"description": "Use an IPv4 address for the forwarding proxy server", "help": "Use an IPv4 address for the forwarding proxy server.", "label": "Ip", "name": "ip"}, {"description": "Use an IPv6 address for the forwarding proxy server", "help": "Use an IPv6 address for the forwarding proxy server.", "label": "Ipv6", "name": "ipv6"}, {"description": "Use the FQDN for the forwarding proxy server", "help": "Use the FQDN for the forwarding proxy server.", "label": "Fqdn", "name": "fqdn"}] | None = ...,
        ip: str | None = ...,
        ipv6: str | None = ...,
        fqdn: str | None = ...,
        port: int | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        comment: str | None = ...,
        masquerade: Literal[{"help": "Enable use of the IP address of the outgoing interface as the client IP address.", "label": "Enable", "name": "enable"}, {"description": "Disable use of the IP address of the outgoing interface as the client IP address", "help": "Disable use of the IP address of the outgoing interface as the client IP address.", "label": "Disable", "name": "disable"}] | None = ...,
        healthcheck: Literal[{"description": "Disable health checking", "help": "Disable health checking.", "label": "Disable", "name": "disable"}, {"description": "Enable health checking", "help": "Enable health checking.", "label": "Enable", "name": "enable"}] | None = ...,
        monitor: str | None = ...,
        server_down_option: Literal[{"description": "Block sessions until the server is back up", "help": "Block sessions until the server is back up.", "label": "Block", "name": "block"}, {"description": "Pass sessions to their destination bypassing the forward server", "help": "Pass sessions to their destination bypassing the forward server.", "label": "Pass", "name": "pass"}] | None = ...,
        username: str | None = ...,
        password: str | None = ...,
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
        payload_dict: ForwardServerPayload | None = ...,
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
    "ForwardServer",
    "ForwardServerPayload",
]