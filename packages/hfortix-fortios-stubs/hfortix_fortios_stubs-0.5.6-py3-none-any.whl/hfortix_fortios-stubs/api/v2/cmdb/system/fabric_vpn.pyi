from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class FabricVpnPayload(TypedDict, total=False):
    """
    Type hints for system/fabric_vpn payload fields.
    
    Setup for self orchestrated fabric auto discovery VPN.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.fabric-vpn.advertised-subnets.AdvertisedSubnetsEndpoint` (via: loopback-advertised-subnet)
        - :class:`~.system.interface.InterfaceEndpoint` (via: loopback-interface)
        - :class:`~.system.sdwan.health-check.HealthCheckEndpoint` (via: health-checks)
        - :class:`~.system.sdwan.zone.ZoneEndpoint` (via: sdwan-zone)

    **Usage:**
        payload: FabricVpnPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: Literal[{"description": "Enable Fabric VPN", "help": "Enable Fabric VPN.", "label": "Enable", "name": "enable"}, {"description": "Disable Fabric VPN", "help": "Disable Fabric VPN.", "label": "Disable", "name": "disable"}]  # Enable/disable Fabric VPN.
    sync_mode: Literal[{"description": "Enable fabric led configuration synchronization", "help": "Enable fabric led configuration synchronization.", "label": "Enable", "name": "enable"}, {"description": "Disable fabric led configuration synchronization", "help": "Disable fabric led configuration synchronization.", "label": "Disable", "name": "disable"}]  # Setting synchronized by fabric or manual.
    branch_name: NotRequired[str]  # Branch name.
    policy_rule: NotRequired[Literal[{"description": "Create health check policy automatically", "help": "Create health check policy automatically.", "label": "Health Check", "name": "health-check"}, {"description": "All policies will be created manually", "help": "All policies will be created manually.", "label": "Manual", "name": "manual"}, {"description": "Automatically create allow policies", "help": "Automatically create allow policies.", "label": "Auto", "name": "auto"}]]  # Policy creation rule.
    vpn_role: Literal[{"description": "VPN hub", "help": "VPN hub.", "label": "Hub", "name": "hub"}, {"description": "VPN spoke", "help": "VPN spoke.", "label": "Spoke", "name": "spoke"}]  # Fabric VPN role.
    overlays: NotRequired[list[dict[str, Any]]]  # Local overlay interfaces table.
    advertised_subnets: NotRequired[list[dict[str, Any]]]  # Local advertised subnets.
    loopback_address_block: str  # IPv4 address and subnet mask for hub's loopback address, syn
    loopback_interface: NotRequired[str]  # Loopback interface.
    loopback_advertised_subnet: NotRequired[int]  # Loopback advertised subnet reference.
    psksecret: str  # Pre-shared secret for ADVPN.
    bgp_as: str  # BGP Router AS number, asplain/asdot/asdot+ format.
    sdwan_zone: NotRequired[str]  # Reference to created SD-WAN zone.
    health_checks: NotRequired[list[dict[str, Any]]]  # Underlying health checks.


class FabricVpn:
    """
    Setup for self orchestrated fabric auto discovery VPN.
    
    Path: system/fabric_vpn
    Category: cmdb
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
        payload_dict: FabricVpnPayload | None = ...,
        status: Literal[{"description": "Enable Fabric VPN", "help": "Enable Fabric VPN.", "label": "Enable", "name": "enable"}, {"description": "Disable Fabric VPN", "help": "Disable Fabric VPN.", "label": "Disable", "name": "disable"}] | None = ...,
        sync_mode: Literal[{"description": "Enable fabric led configuration synchronization", "help": "Enable fabric led configuration synchronization.", "label": "Enable", "name": "enable"}, {"description": "Disable fabric led configuration synchronization", "help": "Disable fabric led configuration synchronization.", "label": "Disable", "name": "disable"}] | None = ...,
        branch_name: str | None = ...,
        policy_rule: Literal[{"description": "Create health check policy automatically", "help": "Create health check policy automatically.", "label": "Health Check", "name": "health-check"}, {"description": "All policies will be created manually", "help": "All policies will be created manually.", "label": "Manual", "name": "manual"}, {"description": "Automatically create allow policies", "help": "Automatically create allow policies.", "label": "Auto", "name": "auto"}] | None = ...,
        vpn_role: Literal[{"description": "VPN hub", "help": "VPN hub.", "label": "Hub", "name": "hub"}, {"description": "VPN spoke", "help": "VPN spoke.", "label": "Spoke", "name": "spoke"}] | None = ...,
        overlays: list[dict[str, Any]] | None = ...,
        advertised_subnets: list[dict[str, Any]] | None = ...,
        loopback_address_block: str | None = ...,
        loopback_interface: str | None = ...,
        loopback_advertised_subnet: int | None = ...,
        psksecret: str | None = ...,
        bgp_as: str | None = ...,
        sdwan_zone: str | None = ...,
        health_checks: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: FabricVpnPayload | None = ...,
        status: Literal[{"description": "Enable Fabric VPN", "help": "Enable Fabric VPN.", "label": "Enable", "name": "enable"}, {"description": "Disable Fabric VPN", "help": "Disable Fabric VPN.", "label": "Disable", "name": "disable"}] | None = ...,
        sync_mode: Literal[{"description": "Enable fabric led configuration synchronization", "help": "Enable fabric led configuration synchronization.", "label": "Enable", "name": "enable"}, {"description": "Disable fabric led configuration synchronization", "help": "Disable fabric led configuration synchronization.", "label": "Disable", "name": "disable"}] | None = ...,
        branch_name: str | None = ...,
        policy_rule: Literal[{"description": "Create health check policy automatically", "help": "Create health check policy automatically.", "label": "Health Check", "name": "health-check"}, {"description": "All policies will be created manually", "help": "All policies will be created manually.", "label": "Manual", "name": "manual"}, {"description": "Automatically create allow policies", "help": "Automatically create allow policies.", "label": "Auto", "name": "auto"}] | None = ...,
        vpn_role: Literal[{"description": "VPN hub", "help": "VPN hub.", "label": "Hub", "name": "hub"}, {"description": "VPN spoke", "help": "VPN spoke.", "label": "Spoke", "name": "spoke"}] | None = ...,
        overlays: list[dict[str, Any]] | None = ...,
        advertised_subnets: list[dict[str, Any]] | None = ...,
        loopback_address_block: str | None = ...,
        loopback_interface: str | None = ...,
        loopback_advertised_subnet: int | None = ...,
        psksecret: str | None = ...,
        bgp_as: str | None = ...,
        sdwan_zone: str | None = ...,
        health_checks: list[dict[str, Any]] | None = ...,
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
        payload_dict: FabricVpnPayload | None = ...,
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
    "FabricVpn",
    "FabricVpnPayload",
]