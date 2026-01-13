from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ResourceLimitsPayload(TypedDict, total=False):
    """
    Type hints for system/resource_limits payload fields.
    
    Configure resource limits.
    
    **Usage:**
        payload: ResourceLimitsPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    session: NotRequired[int]  # Maximum number of sessions.
    ipsec_phase1: NotRequired[int]  # Maximum number of VPN IPsec phase1 tunnels.
    ipsec_phase2: NotRequired[int]  # Maximum number of VPN IPsec phase2 tunnels.
    ipsec_phase1_interface: NotRequired[int]  # Maximum number of VPN IPsec phase1 interface tunnels.
    ipsec_phase2_interface: NotRequired[int]  # Maximum number of VPN IPsec phase2 interface tunnels.
    dialup_tunnel: NotRequired[int]  # Maximum number of dial-up tunnels.
    firewall_policy: NotRequired[int]  # Maximum number of firewall policies (policy, DoS-policy4, Do
    firewall_address: NotRequired[int]  # Maximum number of firewall addresses (IPv4, IPv6, multicast)
    firewall_addrgrp: NotRequired[int]  # Maximum number of firewall address groups (IPv4, IPv6).
    custom_service: NotRequired[int]  # Maximum number of firewall custom services.
    service_group: NotRequired[int]  # Maximum number of firewall service groups.
    onetime_schedule: NotRequired[int]  # Maximum number of firewall one-time schedules.
    recurring_schedule: NotRequired[int]  # Maximum number of firewall recurring schedules.
    user: NotRequired[int]  # Maximum number of local users.
    user_group: NotRequired[int]  # Maximum number of user groups.
    sslvpn: NotRequired[int]  # Maximum number of Agentless VPN.
    proxy: NotRequired[int]  # Maximum number of concurrent proxy users.
    log_disk_quota: NotRequired[int]  # Log disk quota in megabytes (MB).


class ResourceLimits:
    """
    Configure resource limits.
    
    Path: system/resource_limits
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
        payload_dict: ResourceLimitsPayload | None = ...,
        session: int | None = ...,
        ipsec_phase1: int | None = ...,
        ipsec_phase2: int | None = ...,
        ipsec_phase1_interface: int | None = ...,
        ipsec_phase2_interface: int | None = ...,
        dialup_tunnel: int | None = ...,
        firewall_policy: int | None = ...,
        firewall_address: int | None = ...,
        firewall_addrgrp: int | None = ...,
        custom_service: int | None = ...,
        service_group: int | None = ...,
        onetime_schedule: int | None = ...,
        recurring_schedule: int | None = ...,
        user: int | None = ...,
        user_group: int | None = ...,
        sslvpn: int | None = ...,
        proxy: int | None = ...,
        log_disk_quota: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ResourceLimitsPayload | None = ...,
        session: int | None = ...,
        ipsec_phase1: int | None = ...,
        ipsec_phase2: int | None = ...,
        ipsec_phase1_interface: int | None = ...,
        ipsec_phase2_interface: int | None = ...,
        dialup_tunnel: int | None = ...,
        firewall_policy: int | None = ...,
        firewall_address: int | None = ...,
        firewall_addrgrp: int | None = ...,
        custom_service: int | None = ...,
        service_group: int | None = ...,
        onetime_schedule: int | None = ...,
        recurring_schedule: int | None = ...,
        user: int | None = ...,
        user_group: int | None = ...,
        sslvpn: int | None = ...,
        proxy: int | None = ...,
        log_disk_quota: int | None = ...,
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
        payload_dict: ResourceLimitsPayload | None = ...,
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
    "ResourceLimits",
    "ResourceLimitsPayload",
]