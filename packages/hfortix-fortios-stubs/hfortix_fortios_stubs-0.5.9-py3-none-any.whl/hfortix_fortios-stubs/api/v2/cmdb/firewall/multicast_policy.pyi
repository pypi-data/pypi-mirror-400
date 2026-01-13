from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class MulticastPolicyPayload(TypedDict, total=False):
    """
    Type hints for firewall/multicast_policy payload fields.
    
    Configure multicast NAT policies.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.firewall.shaper.traffic-shaper.TrafficShaperEndpoint` (via: traffic-shaper)
        - :class:`~.ips.sensor.SensorEndpoint` (via: ips-sensor)
        - :class:`~.system.interface.InterfaceEndpoint` (via: dstintf, srcintf)
        - :class:`~.system.sdwan.zone.ZoneEndpoint` (via: dstintf, srcintf)
        - :class:`~.system.zone.ZoneEndpoint` (via: dstintf, srcintf)

    **Usage:**
        payload: MulticastPolicyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    id: NotRequired[int]  # Policy ID ((0 - 4294967294).
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    name: NotRequired[str]  # Policy name.
    comments: NotRequired[str]  # Comment.
    status: NotRequired[Literal[{"description": "Enable this policy", "help": "Enable this policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy", "help": "Disable this policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable this policy.
    srcintf: str  # Source interface name.
    dstintf: str  # Destination interface name.
    srcaddr: list[dict[str, Any]]  # Source address objects.
    dstaddr: list[dict[str, Any]]  # Destination address objects.
    snat: NotRequired[Literal[{"description": "Enable source NAT", "help": "Enable source NAT.", "label": "Enable", "name": "enable"}, {"description": "Disable source NAT", "help": "Disable source NAT.", "label": "Disable", "name": "disable"}]]  # Enable/disable substitution of the outgoing interface IP add
    snat_ip: NotRequired[str]  # IPv4 address to be used as the source address for NATed traf
    dnat: NotRequired[str]  # IPv4 DNAT address used for multicast destination addresses.
    action: NotRequired[Literal[{"description": "Accept traffic matching the policy", "help": "Accept traffic matching the policy.", "label": "Accept", "name": "accept"}, {"description": "Deny or block traffic matching the policy", "help": "Deny or block traffic matching the policy.", "label": "Deny", "name": "deny"}]]  # Accept or deny traffic matching the policy.
    protocol: NotRequired[int]  # Integer value for the protocol type as defined by IANA (0 - 
    start_port: NotRequired[int]  # Integer value for starting TCP/UDP/SCTP destination port in 
    end_port: NotRequired[int]  # Integer value for ending TCP/UDP/SCTP destination port in ra
    utm_status: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable to add an IPS security profile to the policy.
    ips_sensor: NotRequired[str]  # Name of an existing IPS sensor.
    logtraffic: NotRequired[Literal[{"description": "Enable logging traffic accepted by this policy", "help": "Enable logging traffic accepted by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}]]  # Enable or disable logging. Log all sessions or security prof
    auto_asic_offload: NotRequired[Literal[{"description": "Enable hardware acceleration offloading", "help": "Enable hardware acceleration offloading.", "label": "Enable", "name": "enable"}, {"description": "Disable offloading for hardware acceleration", "help": "Disable offloading for hardware acceleration.", "label": "Disable", "name": "disable"}]]  # Enable/disable offloading policy traffic for hardware accele
    traffic_shaper: NotRequired[str]  # Traffic shaper to apply to traffic forwarded by the multicas


class MulticastPolicy:
    """
    Configure multicast NAT policies.
    
    Path: firewall/multicast_policy
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
        payload_dict: MulticastPolicyPayload | None = ...,
        id: int | None = ...,
        uuid: str | None = ...,
        name: str | None = ...,
        comments: str | None = ...,
        status: Literal[{"description": "Enable this policy", "help": "Enable this policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy", "help": "Disable this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        srcintf: str | None = ...,
        dstintf: str | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        snat: Literal[{"description": "Enable source NAT", "help": "Enable source NAT.", "label": "Enable", "name": "enable"}, {"description": "Disable source NAT", "help": "Disable source NAT.", "label": "Disable", "name": "disable"}] | None = ...,
        snat_ip: str | None = ...,
        dnat: str | None = ...,
        action: Literal[{"description": "Accept traffic matching the policy", "help": "Accept traffic matching the policy.", "label": "Accept", "name": "accept"}, {"description": "Deny or block traffic matching the policy", "help": "Deny or block traffic matching the policy.", "label": "Deny", "name": "deny"}] | None = ...,
        protocol: int | None = ...,
        start_port: int | None = ...,
        end_port: int | None = ...,
        utm_status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ips_sensor: str | None = ...,
        logtraffic: Literal[{"description": "Enable logging traffic accepted by this policy", "help": "Enable logging traffic accepted by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        auto_asic_offload: Literal[{"description": "Enable hardware acceleration offloading", "help": "Enable hardware acceleration offloading.", "label": "Enable", "name": "enable"}, {"description": "Disable offloading for hardware acceleration", "help": "Disable offloading for hardware acceleration.", "label": "Disable", "name": "disable"}] | None = ...,
        traffic_shaper: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: MulticastPolicyPayload | None = ...,
        id: int | None = ...,
        uuid: str | None = ...,
        name: str | None = ...,
        comments: str | None = ...,
        status: Literal[{"description": "Enable this policy", "help": "Enable this policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy", "help": "Disable this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        srcintf: str | None = ...,
        dstintf: str | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        snat: Literal[{"description": "Enable source NAT", "help": "Enable source NAT.", "label": "Enable", "name": "enable"}, {"description": "Disable source NAT", "help": "Disable source NAT.", "label": "Disable", "name": "disable"}] | None = ...,
        snat_ip: str | None = ...,
        dnat: str | None = ...,
        action: Literal[{"description": "Accept traffic matching the policy", "help": "Accept traffic matching the policy.", "label": "Accept", "name": "accept"}, {"description": "Deny or block traffic matching the policy", "help": "Deny or block traffic matching the policy.", "label": "Deny", "name": "deny"}] | None = ...,
        protocol: int | None = ...,
        start_port: int | None = ...,
        end_port: int | None = ...,
        utm_status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ips_sensor: str | None = ...,
        logtraffic: Literal[{"description": "Enable logging traffic accepted by this policy", "help": "Enable logging traffic accepted by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        auto_asic_offload: Literal[{"description": "Enable hardware acceleration offloading", "help": "Enable hardware acceleration offloading.", "label": "Enable", "name": "enable"}, {"description": "Disable offloading for hardware acceleration", "help": "Disable offloading for hardware acceleration.", "label": "Disable", "name": "disable"}] | None = ...,
        traffic_shaper: str | None = ...,
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
        payload_dict: MulticastPolicyPayload | None = ...,
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
    "MulticastPolicy",
    "MulticastPolicyPayload",
]