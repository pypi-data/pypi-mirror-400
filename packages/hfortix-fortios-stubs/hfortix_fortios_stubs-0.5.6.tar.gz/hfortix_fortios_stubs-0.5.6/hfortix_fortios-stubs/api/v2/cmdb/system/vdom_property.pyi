from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class VdomPropertyPayload(TypedDict, total=False):
    """
    Type hints for system/vdom_property payload fields.
    
    Configure VDOM property.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.vdom.VdomEndpoint` (via: name)

    **Usage:**
        payload: VdomPropertyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # VDOM name.
    description: NotRequired[str]  # Description.
    snmp_index: NotRequired[int]  # Permanent SNMP Index of the virtual domain (1 - 2147483647).
    session: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of sessions.
    ipsec_phase1: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of VPN IPsec phase 1 tunnels.
    ipsec_phase2: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of VPN IPsec phase 2 tunnels.
    ipsec_phase1_interface: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of VPN IPsec phase1 interface tunn
    ipsec_phase2_interface: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of VPN IPsec phase2 interface tunn
    dialup_tunnel: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of dial-up tunnels.
    firewall_policy: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of firewall policies (policy, DoS-
    firewall_address: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of firewall addresses (IPv4, IPv6,
    firewall_addrgrp: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of firewall address groups (IPv4, 
    custom_service: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of firewall custom services.
    service_group: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of firewall service groups.
    onetime_schedule: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of firewall one-time schedules..
    recurring_schedule: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of firewall recurring schedules.
    user: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of local users.
    user_group: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of user groups.
    sslvpn: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of Agentless VPNs.
    proxy: NotRequired[list[dict[str, Any]]]  # Maximum guaranteed number of concurrent proxy users.
    log_disk_quota: NotRequired[list[dict[str, Any]]]  # Log disk quota in megabytes (MB). Range depends on how much 


class VdomProperty:
    """
    Configure VDOM property.
    
    Path: system/vdom_property
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
        payload_dict: VdomPropertyPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        snmp_index: int | None = ...,
        session: list[dict[str, Any]] | None = ...,
        ipsec_phase1: list[dict[str, Any]] | None = ...,
        ipsec_phase2: list[dict[str, Any]] | None = ...,
        ipsec_phase1_interface: list[dict[str, Any]] | None = ...,
        ipsec_phase2_interface: list[dict[str, Any]] | None = ...,
        dialup_tunnel: list[dict[str, Any]] | None = ...,
        firewall_policy: list[dict[str, Any]] | None = ...,
        firewall_address: list[dict[str, Any]] | None = ...,
        firewall_addrgrp: list[dict[str, Any]] | None = ...,
        custom_service: list[dict[str, Any]] | None = ...,
        service_group: list[dict[str, Any]] | None = ...,
        onetime_schedule: list[dict[str, Any]] | None = ...,
        recurring_schedule: list[dict[str, Any]] | None = ...,
        user: list[dict[str, Any]] | None = ...,
        user_group: list[dict[str, Any]] | None = ...,
        sslvpn: list[dict[str, Any]] | None = ...,
        proxy: list[dict[str, Any]] | None = ...,
        log_disk_quota: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: VdomPropertyPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        snmp_index: int | None = ...,
        session: list[dict[str, Any]] | None = ...,
        ipsec_phase1: list[dict[str, Any]] | None = ...,
        ipsec_phase2: list[dict[str, Any]] | None = ...,
        ipsec_phase1_interface: list[dict[str, Any]] | None = ...,
        ipsec_phase2_interface: list[dict[str, Any]] | None = ...,
        dialup_tunnel: list[dict[str, Any]] | None = ...,
        firewall_policy: list[dict[str, Any]] | None = ...,
        firewall_address: list[dict[str, Any]] | None = ...,
        firewall_addrgrp: list[dict[str, Any]] | None = ...,
        custom_service: list[dict[str, Any]] | None = ...,
        service_group: list[dict[str, Any]] | None = ...,
        onetime_schedule: list[dict[str, Any]] | None = ...,
        recurring_schedule: list[dict[str, Any]] | None = ...,
        user: list[dict[str, Any]] | None = ...,
        user_group: list[dict[str, Any]] | None = ...,
        sslvpn: list[dict[str, Any]] | None = ...,
        proxy: list[dict[str, Any]] | None = ...,
        log_disk_quota: list[dict[str, Any]] | None = ...,
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
        payload_dict: VdomPropertyPayload | None = ...,
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
    "VdomProperty",
    "VdomPropertyPayload",
]