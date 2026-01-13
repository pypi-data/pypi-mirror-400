from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SdnVpnPayload(TypedDict, total=False):
    """
    Type hints for system/sdn_vpn payload fields.
    
    Configure public cloud VPN service.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: internal-interface, tunnel-interface)
        - :class:`~.system.sdn-connector.SdnConnectorEndpoint` (via: sdn)

    **Usage:**
        payload: SdnVpnPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Public cloud VPN name.
    sdn: str  # SDN connector name.
    remote_type: Literal[{"description": "Virtual private gateway", "help": "Virtual private gateway.", "label": "Vgw", "name": "vgw"}, {"description": "Transit gateway", "help": "Transit gateway.", "label": "Tgw", "name": "tgw"}]  # Type of remote device.
    routing_type: Literal[{"description": "Static routing", "help": "Static routing.", "label": "Static", "name": "static"}, {"description": "Dynamic routing", "help": "Dynamic routing.", "label": "Dynamic", "name": "dynamic"}]  # Type of routing.
    vgw_id: str  # Virtual private gateway id.
    tgw_id: str  # Transit gateway id.
    subnet_id: NotRequired[str]  # AWS subnet id for TGW route propagation.
    bgp_as: int  # BGP Router AS number.
    cgw_gateway: str  # Public IP address of the customer gateway.
    nat_traversal: NotRequired[Literal[{"description": "Disable NAT traversal", "help": "Disable NAT traversal.", "label": "Disable", "name": "disable"}, {"description": "Enable NAT traversal", "help": "Enable NAT traversal.", "label": "Enable", "name": "enable"}]]  # Enable/disable use for NAT traversal. Please enable if your 
    tunnel_interface: str  # Tunnel interface with public IP.
    internal_interface: str  # Internal interface with local subnet.
    local_cidr: str  # Local subnet address and subnet mask.
    remote_cidr: str  # Remote subnet address and subnet mask.
    cgw_name: NotRequired[str]  # AWS customer gateway name to be created.
    psksecret: NotRequired[str]  # Pre-shared secret for PSK authentication. Auto-generated if 
    type: NotRequired[int]  # SDN VPN type.
    status: NotRequired[int]  # SDN VPN status.
    code: NotRequired[int]  # SDN VPN error code.


class SdnVpn:
    """
    Configure public cloud VPN service.
    
    Path: system/sdn_vpn
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
        payload_dict: SdnVpnPayload | None = ...,
        name: str | None = ...,
        sdn: str | None = ...,
        remote_type: Literal[{"description": "Virtual private gateway", "help": "Virtual private gateway.", "label": "Vgw", "name": "vgw"}, {"description": "Transit gateway", "help": "Transit gateway.", "label": "Tgw", "name": "tgw"}] | None = ...,
        routing_type: Literal[{"description": "Static routing", "help": "Static routing.", "label": "Static", "name": "static"}, {"description": "Dynamic routing", "help": "Dynamic routing.", "label": "Dynamic", "name": "dynamic"}] | None = ...,
        vgw_id: str | None = ...,
        tgw_id: str | None = ...,
        subnet_id: str | None = ...,
        bgp_as: int | None = ...,
        cgw_gateway: str | None = ...,
        nat_traversal: Literal[{"description": "Disable NAT traversal", "help": "Disable NAT traversal.", "label": "Disable", "name": "disable"}, {"description": "Enable NAT traversal", "help": "Enable NAT traversal.", "label": "Enable", "name": "enable"}] | None = ...,
        tunnel_interface: str | None = ...,
        internal_interface: str | None = ...,
        local_cidr: str | None = ...,
        remote_cidr: str | None = ...,
        cgw_name: str | None = ...,
        psksecret: str | None = ...,
        type: int | None = ...,
        status: int | None = ...,
        code: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SdnVpnPayload | None = ...,
        name: str | None = ...,
        sdn: str | None = ...,
        remote_type: Literal[{"description": "Virtual private gateway", "help": "Virtual private gateway.", "label": "Vgw", "name": "vgw"}, {"description": "Transit gateway", "help": "Transit gateway.", "label": "Tgw", "name": "tgw"}] | None = ...,
        routing_type: Literal[{"description": "Static routing", "help": "Static routing.", "label": "Static", "name": "static"}, {"description": "Dynamic routing", "help": "Dynamic routing.", "label": "Dynamic", "name": "dynamic"}] | None = ...,
        vgw_id: str | None = ...,
        tgw_id: str | None = ...,
        subnet_id: str | None = ...,
        bgp_as: int | None = ...,
        cgw_gateway: str | None = ...,
        nat_traversal: Literal[{"description": "Disable NAT traversal", "help": "Disable NAT traversal.", "label": "Disable", "name": "disable"}, {"description": "Enable NAT traversal", "help": "Enable NAT traversal.", "label": "Enable", "name": "enable"}] | None = ...,
        tunnel_interface: str | None = ...,
        internal_interface: str | None = ...,
        local_cidr: str | None = ...,
        remote_cidr: str | None = ...,
        cgw_name: str | None = ...,
        psksecret: str | None = ...,
        type: int | None = ...,
        status: int | None = ...,
        code: int | None = ...,
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
        payload_dict: SdnVpnPayload | None = ...,
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
    "SdnVpn",
    "SdnVpnPayload",
]