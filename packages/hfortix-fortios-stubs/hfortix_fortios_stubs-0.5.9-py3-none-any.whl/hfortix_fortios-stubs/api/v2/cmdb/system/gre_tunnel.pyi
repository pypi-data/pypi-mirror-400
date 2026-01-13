from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class GreTunnelPayload(TypedDict, total=False):
    """
    Type hints for system/gre_tunnel payload fields.
    
    Configure GRE tunnel.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: GreTunnelPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Tunnel name.
    interface: NotRequired[str]  # Interface name.
    ip_version: NotRequired[Literal[{"description": "Use IPv4 addressing for gateways", "help": "Use IPv4 addressing for gateways.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for gateways", "help": "Use IPv6 addressing for gateways.", "label": "6", "name": "6"}]]  # IP version to use for VPN interface.
    remote_gw6: str  # IPv6 address of the remote gateway.
    local_gw6: str  # IPv6 address of the local gateway.
    remote_gw: str  # IP address of the remote gateway.
    local_gw: str  # IP address of the local gateway.
    use_sdwan: NotRequired[Literal[{"description": "Disable use of SD-WAN to reach remote gateway", "help": "Disable use of SD-WAN to reach remote gateway.", "label": "Disable", "name": "disable"}, {"description": "Enable use of SD-WAN to reach remote gateway", "help": "Enable use of SD-WAN to reach remote gateway.", "label": "Enable", "name": "enable"}]]  # Enable/disable use of SD-WAN to reach remote gateway.
    sequence_number_transmission: NotRequired[Literal[{"description": "Include sequence numbers in transmitted GRE packets", "help": "Include sequence numbers in transmitted GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Do not  include sequence numbers in transmitted GRE packets", "help": "Do not  include sequence numbers in transmitted GRE packets.", "label": "Enable", "name": "enable"}]]  # Enable/disable including of sequence numbers in transmitted 
    sequence_number_reception: NotRequired[Literal[{"description": "Do not validate sequence number in received GRE packets", "help": "Do not validate sequence number in received GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Validate sequence numbers in received GRE packets", "help": "Validate sequence numbers in received GRE packets.", "label": "Enable", "name": "enable"}]]  # Enable/disable validating sequence numbers in received GRE p
    checksum_transmission: NotRequired[Literal[{"description": "Do not include checksums in transmitted GRE packets", "help": "Do not include checksums in transmitted GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Include checksums in transmitted GRE packets", "help": "Include checksums in transmitted GRE packets.", "label": "Enable", "name": "enable"}]]  # Enable/disable including checksums in transmitted GRE packet
    checksum_reception: NotRequired[Literal[{"description": "Do not validate checksums in received GRE packets", "help": "Do not validate checksums in received GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Validate checksums in received GRE packets", "help": "Validate checksums in received GRE packets.", "label": "Enable", "name": "enable"}]]  # Enable/disable validating checksums in received GRE packets.
    key_outbound: NotRequired[int]  # Include this key in transmitted GRE packets (0 - 4294967295)
    key_inbound: NotRequired[int]  # Require received GRE packets contain this key (0 - 429496729
    dscp_copying: NotRequired[Literal[{"description": "Disable DSCP copying", "help": "Disable DSCP copying.", "label": "Disable", "name": "disable"}, {"description": "Enable DSCP copying", "help": "Enable DSCP copying.", "label": "Enable", "name": "enable"}]]  # Enable/disable DSCP copying.
    diffservcode: NotRequired[str]  # DiffServ setting to be applied to GRE tunnel outer IP header
    keepalive_interval: NotRequired[int]  # Keepalive message interval (0 - 32767, 0 = disabled).
    keepalive_failtimes: NotRequired[int]  # Number of consecutive unreturned keepalive messages before a


class GreTunnel:
    """
    Configure GRE tunnel.
    
    Path: system/gre_tunnel
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
        payload_dict: GreTunnelPayload | None = ...,
        name: str | None = ...,
        interface: str | None = ...,
        ip_version: Literal[{"description": "Use IPv4 addressing for gateways", "help": "Use IPv4 addressing for gateways.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for gateways", "help": "Use IPv6 addressing for gateways.", "label": "6", "name": "6"}] | None = ...,
        remote_gw6: str | None = ...,
        local_gw6: str | None = ...,
        remote_gw: str | None = ...,
        local_gw: str | None = ...,
        use_sdwan: Literal[{"description": "Disable use of SD-WAN to reach remote gateway", "help": "Disable use of SD-WAN to reach remote gateway.", "label": "Disable", "name": "disable"}, {"description": "Enable use of SD-WAN to reach remote gateway", "help": "Enable use of SD-WAN to reach remote gateway.", "label": "Enable", "name": "enable"}] | None = ...,
        sequence_number_transmission: Literal[{"description": "Include sequence numbers in transmitted GRE packets", "help": "Include sequence numbers in transmitted GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Do not  include sequence numbers in transmitted GRE packets", "help": "Do not  include sequence numbers in transmitted GRE packets.", "label": "Enable", "name": "enable"}] | None = ...,
        sequence_number_reception: Literal[{"description": "Do not validate sequence number in received GRE packets", "help": "Do not validate sequence number in received GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Validate sequence numbers in received GRE packets", "help": "Validate sequence numbers in received GRE packets.", "label": "Enable", "name": "enable"}] | None = ...,
        checksum_transmission: Literal[{"description": "Do not include checksums in transmitted GRE packets", "help": "Do not include checksums in transmitted GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Include checksums in transmitted GRE packets", "help": "Include checksums in transmitted GRE packets.", "label": "Enable", "name": "enable"}] | None = ...,
        checksum_reception: Literal[{"description": "Do not validate checksums in received GRE packets", "help": "Do not validate checksums in received GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Validate checksums in received GRE packets", "help": "Validate checksums in received GRE packets.", "label": "Enable", "name": "enable"}] | None = ...,
        key_outbound: int | None = ...,
        key_inbound: int | None = ...,
        dscp_copying: Literal[{"description": "Disable DSCP copying", "help": "Disable DSCP copying.", "label": "Disable", "name": "disable"}, {"description": "Enable DSCP copying", "help": "Enable DSCP copying.", "label": "Enable", "name": "enable"}] | None = ...,
        diffservcode: str | None = ...,
        keepalive_interval: int | None = ...,
        keepalive_failtimes: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: GreTunnelPayload | None = ...,
        name: str | None = ...,
        interface: str | None = ...,
        ip_version: Literal[{"description": "Use IPv4 addressing for gateways", "help": "Use IPv4 addressing for gateways.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for gateways", "help": "Use IPv6 addressing for gateways.", "label": "6", "name": "6"}] | None = ...,
        remote_gw6: str | None = ...,
        local_gw6: str | None = ...,
        remote_gw: str | None = ...,
        local_gw: str | None = ...,
        use_sdwan: Literal[{"description": "Disable use of SD-WAN to reach remote gateway", "help": "Disable use of SD-WAN to reach remote gateway.", "label": "Disable", "name": "disable"}, {"description": "Enable use of SD-WAN to reach remote gateway", "help": "Enable use of SD-WAN to reach remote gateway.", "label": "Enable", "name": "enable"}] | None = ...,
        sequence_number_transmission: Literal[{"description": "Include sequence numbers in transmitted GRE packets", "help": "Include sequence numbers in transmitted GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Do not  include sequence numbers in transmitted GRE packets", "help": "Do not  include sequence numbers in transmitted GRE packets.", "label": "Enable", "name": "enable"}] | None = ...,
        sequence_number_reception: Literal[{"description": "Do not validate sequence number in received GRE packets", "help": "Do not validate sequence number in received GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Validate sequence numbers in received GRE packets", "help": "Validate sequence numbers in received GRE packets.", "label": "Enable", "name": "enable"}] | None = ...,
        checksum_transmission: Literal[{"description": "Do not include checksums in transmitted GRE packets", "help": "Do not include checksums in transmitted GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Include checksums in transmitted GRE packets", "help": "Include checksums in transmitted GRE packets.", "label": "Enable", "name": "enable"}] | None = ...,
        checksum_reception: Literal[{"description": "Do not validate checksums in received GRE packets", "help": "Do not validate checksums in received GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Validate checksums in received GRE packets", "help": "Validate checksums in received GRE packets.", "label": "Enable", "name": "enable"}] | None = ...,
        key_outbound: int | None = ...,
        key_inbound: int | None = ...,
        dscp_copying: Literal[{"description": "Disable DSCP copying", "help": "Disable DSCP copying.", "label": "Disable", "name": "disable"}, {"description": "Enable DSCP copying", "help": "Enable DSCP copying.", "label": "Enable", "name": "enable"}] | None = ...,
        diffservcode: str | None = ...,
        keepalive_interval: int | None = ...,
        keepalive_failtimes: int | None = ...,
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
        payload_dict: GreTunnelPayload | None = ...,
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
    "GreTunnel",
    "GreTunnelPayload",
]