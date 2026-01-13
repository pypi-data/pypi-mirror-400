from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ShapingPolicyPayload(TypedDict, total=False):
    """
    Type hints for firewall/shaping_policy payload fields.
    
    Configure shaping policies.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.firewall.schedule.group.GroupEndpoint` (via: schedule)
        - :class:`~.firewall.schedule.onetime.OnetimeEndpoint` (via: schedule)
        - :class:`~.firewall.schedule.recurring.RecurringEndpoint` (via: schedule)
        - :class:`~.firewall.shaper.per-ip-shaper.PerIpShaperEndpoint` (via: per-ip-shaper)
        - :class:`~.firewall.shaper.traffic-shaper.TrafficShaperEndpoint` (via: traffic-shaper, traffic-shaper-reverse)
        - :class:`~.firewall.traffic-class.TrafficClassEndpoint` (via: class-id)

    **Usage:**
        payload: ShapingPolicyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    id: NotRequired[int]  # Shaping policy ID (0 - 4294967295).
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    name: NotRequired[str]  # Shaping policy name.
    comment: NotRequired[str]  # Comments.
    status: NotRequired[Literal[{"description": "Enable traffic shaping policy", "help": "Enable traffic shaping policy.", "label": "Enable", "name": "enable"}, {"description": "Disable traffic shaping policy", "help": "Disable traffic shaping policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable this traffic shaping policy.
    ip_version: NotRequired[Literal[{"description": "Use IPv4 addressing for Configuration Method", "help": "Use IPv4 addressing for Configuration Method.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for Configuration Method", "help": "Use IPv6 addressing for Configuration Method.", "label": "6", "name": "6"}]]  # Apply this traffic shaping policy to IPv4 or IPv6 traffic.
    traffic_type: NotRequired[Literal[{"description": "Forwarding traffic", "help": "Forwarding traffic.", "label": "Forwarding", "name": "forwarding"}, {"description": "Local-in traffic", "help": "Local-in traffic.", "label": "Local In", "name": "local-in"}, {"description": "Local-out traffic", "help": "Local-out traffic.", "label": "Local Out", "name": "local-out"}]]  # Traffic type.
    srcaddr: list[dict[str, Any]]  # IPv4 source address and address group names.
    dstaddr: list[dict[str, Any]]  # IPv4 destination address and address group names.
    srcaddr6: list[dict[str, Any]]  # IPv6 source address and address group names.
    dstaddr6: list[dict[str, Any]]  # IPv6 destination address and address group names.
    internet_service: NotRequired[Literal[{"description": "Enable use of Internet Service in shaping-policy", "help": "Enable use of Internet Service in shaping-policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Service in shaping-policy", "help": "Disable use of Internet Service in shaping-policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of Internet Services for this policy. If 
    internet_service_name: NotRequired[list[dict[str, Any]]]  # Internet Service ID.
    internet_service_group: NotRequired[list[dict[str, Any]]]  # Internet Service group name.
    internet_service_custom: NotRequired[list[dict[str, Any]]]  # Custom Internet Service name.
    internet_service_custom_group: NotRequired[list[dict[str, Any]]]  # Custom Internet Service group name.
    internet_service_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard Internet Service name.
    internet_service_src: NotRequired[Literal[{"description": "Enable use of Internet Service source in shaping-policy", "help": "Enable use of Internet Service source in shaping-policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Service source in shaping-policy", "help": "Disable use of Internet Service source in shaping-policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of Internet Services in source for this p
    internet_service_src_name: NotRequired[list[dict[str, Any]]]  # Internet Service source name.
    internet_service_src_group: NotRequired[list[dict[str, Any]]]  # Internet Service source group name.
    internet_service_src_custom: NotRequired[list[dict[str, Any]]]  # Custom Internet Service source name.
    internet_service_src_custom_group: NotRequired[list[dict[str, Any]]]  # Custom Internet Service source group name.
    internet_service_src_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard Internet Service source name.
    service: list[dict[str, Any]]  # Service and service group names.
    schedule: NotRequired[str]  # Schedule name.
    users: NotRequired[list[dict[str, Any]]]  # Apply this traffic shaping policy to individual users that h
    groups: NotRequired[list[dict[str, Any]]]  # Apply this traffic shaping policy to user groups that have a
    application: NotRequired[list[dict[str, Any]]]  # IDs of one or more applications that this shaper applies app
    app_category: NotRequired[list[dict[str, Any]]]  # IDs of one or more application categories that this shaper a
    app_group: NotRequired[list[dict[str, Any]]]  # One or more application group names.
    url_category: NotRequired[list[dict[str, Any]]]  # IDs of one or more FortiGuard Web Filtering categories that 
    srcintf: NotRequired[list[dict[str, Any]]]  # One or more incoming (ingress) interfaces.
    dstintf: list[dict[str, Any]]  # One or more outgoing (egress) interfaces.
    tos_mask: NotRequired[str]  # Non-zero bit positions are used for comparison while zero bi
    tos: NotRequired[str]  # ToS (Type of Service) value used for comparison.
    tos_negate: NotRequired[Literal[{"description": "Enable TOS match negate", "help": "Enable TOS match negate.", "label": "Enable", "name": "enable"}, {"description": "Disable TOS match negate", "help": "Disable TOS match negate.", "label": "Disable", "name": "disable"}]]  # Enable negated TOS match.
    traffic_shaper: NotRequired[str]  # Traffic shaper to apply to traffic forwarded by the firewall
    traffic_shaper_reverse: NotRequired[str]  # Traffic shaper to apply to response traffic received by the 
    per_ip_shaper: NotRequired[str]  # Per-IP traffic shaper to apply with this policy.
    class_id: NotRequired[int]  # Traffic class ID.
    diffserv_forward: NotRequired[Literal[{"description": "Enable setting forward (original) traffic DiffServ", "help": "Enable setting forward (original) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting forward (original) traffic DiffServ", "help": "Disable setting forward (original) traffic DiffServ.", "label": "Disable", "name": "disable"}]]  # Enable to change packet's DiffServ values to the specified d
    diffserv_reverse: NotRequired[Literal[{"description": "Enable setting reverse (reply) traffic DiffServ", "help": "Enable setting reverse (reply) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting reverse (reply) traffic DiffServ", "help": "Disable setting reverse (reply) traffic DiffServ.", "label": "Disable", "name": "disable"}]]  # Enable to change packet's reverse (reply) DiffServ values to
    diffservcode_forward: NotRequired[str]  # Change packet's DiffServ to this value.
    diffservcode_rev: NotRequired[str]  # Change packet's reverse (reply) DiffServ to this value.
    cos_mask: NotRequired[str]  # VLAN CoS evaluated bits.
    cos: NotRequired[str]  # VLAN CoS bit pattern.


class ShapingPolicy:
    """
    Configure shaping policies.
    
    Path: firewall/shaping_policy
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
        payload_dict: ShapingPolicyPayload | None = ...,
        id: int | None = ...,
        uuid: str | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        status: Literal[{"description": "Enable traffic shaping policy", "help": "Enable traffic shaping policy.", "label": "Enable", "name": "enable"}, {"description": "Disable traffic shaping policy", "help": "Disable traffic shaping policy.", "label": "Disable", "name": "disable"}] | None = ...,
        ip_version: Literal[{"description": "Use IPv4 addressing for Configuration Method", "help": "Use IPv4 addressing for Configuration Method.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for Configuration Method", "help": "Use IPv6 addressing for Configuration Method.", "label": "6", "name": "6"}] | None = ...,
        traffic_type: Literal[{"description": "Forwarding traffic", "help": "Forwarding traffic.", "label": "Forwarding", "name": "forwarding"}, {"description": "Local-in traffic", "help": "Local-in traffic.", "label": "Local In", "name": "local-in"}, {"description": "Local-out traffic", "help": "Local-out traffic.", "label": "Local Out", "name": "local-out"}] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        srcaddr6: list[dict[str, Any]] | None = ...,
        dstaddr6: list[dict[str, Any]] | None = ...,
        internet_service: Literal[{"description": "Enable use of Internet Service in shaping-policy", "help": "Enable use of Internet Service in shaping-policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Service in shaping-policy", "help": "Disable use of Internet Service in shaping-policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_name: list[dict[str, Any]] | None = ...,
        internet_service_group: list[dict[str, Any]] | None = ...,
        internet_service_custom: list[dict[str, Any]] | None = ...,
        internet_service_custom_group: list[dict[str, Any]] | None = ...,
        internet_service_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service_src: Literal[{"description": "Enable use of Internet Service source in shaping-policy", "help": "Enable use of Internet Service source in shaping-policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Service source in shaping-policy", "help": "Disable use of Internet Service source in shaping-policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_src_name: list[dict[str, Any]] | None = ...,
        internet_service_src_group: list[dict[str, Any]] | None = ...,
        internet_service_src_custom: list[dict[str, Any]] | None = ...,
        internet_service_src_custom_group: list[dict[str, Any]] | None = ...,
        internet_service_src_fortiguard: list[dict[str, Any]] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        schedule: str | None = ...,
        users: list[dict[str, Any]] | None = ...,
        groups: list[dict[str, Any]] | None = ...,
        application: list[dict[str, Any]] | None = ...,
        app_category: list[dict[str, Any]] | None = ...,
        app_group: list[dict[str, Any]] | None = ...,
        url_category: list[dict[str, Any]] | None = ...,
        srcintf: list[dict[str, Any]] | None = ...,
        dstintf: list[dict[str, Any]] | None = ...,
        tos_mask: str | None = ...,
        tos: str | None = ...,
        tos_negate: Literal[{"description": "Enable TOS match negate", "help": "Enable TOS match negate.", "label": "Enable", "name": "enable"}, {"description": "Disable TOS match negate", "help": "Disable TOS match negate.", "label": "Disable", "name": "disable"}] | None = ...,
        traffic_shaper: str | None = ...,
        traffic_shaper_reverse: str | None = ...,
        per_ip_shaper: str | None = ...,
        class_id: int | None = ...,
        diffserv_forward: Literal[{"description": "Enable setting forward (original) traffic DiffServ", "help": "Enable setting forward (original) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting forward (original) traffic DiffServ", "help": "Disable setting forward (original) traffic DiffServ.", "label": "Disable", "name": "disable"}] | None = ...,
        diffserv_reverse: Literal[{"description": "Enable setting reverse (reply) traffic DiffServ", "help": "Enable setting reverse (reply) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting reverse (reply) traffic DiffServ", "help": "Disable setting reverse (reply) traffic DiffServ.", "label": "Disable", "name": "disable"}] | None = ...,
        diffservcode_forward: str | None = ...,
        diffservcode_rev: str | None = ...,
        cos_mask: str | None = ...,
        cos: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ShapingPolicyPayload | None = ...,
        id: int | None = ...,
        uuid: str | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        status: Literal[{"description": "Enable traffic shaping policy", "help": "Enable traffic shaping policy.", "label": "Enable", "name": "enable"}, {"description": "Disable traffic shaping policy", "help": "Disable traffic shaping policy.", "label": "Disable", "name": "disable"}] | None = ...,
        ip_version: Literal[{"description": "Use IPv4 addressing for Configuration Method", "help": "Use IPv4 addressing for Configuration Method.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for Configuration Method", "help": "Use IPv6 addressing for Configuration Method.", "label": "6", "name": "6"}] | None = ...,
        traffic_type: Literal[{"description": "Forwarding traffic", "help": "Forwarding traffic.", "label": "Forwarding", "name": "forwarding"}, {"description": "Local-in traffic", "help": "Local-in traffic.", "label": "Local In", "name": "local-in"}, {"description": "Local-out traffic", "help": "Local-out traffic.", "label": "Local Out", "name": "local-out"}] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        srcaddr6: list[dict[str, Any]] | None = ...,
        dstaddr6: list[dict[str, Any]] | None = ...,
        internet_service: Literal[{"description": "Enable use of Internet Service in shaping-policy", "help": "Enable use of Internet Service in shaping-policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Service in shaping-policy", "help": "Disable use of Internet Service in shaping-policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_name: list[dict[str, Any]] | None = ...,
        internet_service_group: list[dict[str, Any]] | None = ...,
        internet_service_custom: list[dict[str, Any]] | None = ...,
        internet_service_custom_group: list[dict[str, Any]] | None = ...,
        internet_service_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service_src: Literal[{"description": "Enable use of Internet Service source in shaping-policy", "help": "Enable use of Internet Service source in shaping-policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Service source in shaping-policy", "help": "Disable use of Internet Service source in shaping-policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_src_name: list[dict[str, Any]] | None = ...,
        internet_service_src_group: list[dict[str, Any]] | None = ...,
        internet_service_src_custom: list[dict[str, Any]] | None = ...,
        internet_service_src_custom_group: list[dict[str, Any]] | None = ...,
        internet_service_src_fortiguard: list[dict[str, Any]] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        schedule: str | None = ...,
        users: list[dict[str, Any]] | None = ...,
        groups: list[dict[str, Any]] | None = ...,
        application: list[dict[str, Any]] | None = ...,
        app_category: list[dict[str, Any]] | None = ...,
        app_group: list[dict[str, Any]] | None = ...,
        url_category: list[dict[str, Any]] | None = ...,
        srcintf: list[dict[str, Any]] | None = ...,
        dstintf: list[dict[str, Any]] | None = ...,
        tos_mask: str | None = ...,
        tos: str | None = ...,
        tos_negate: Literal[{"description": "Enable TOS match negate", "help": "Enable TOS match negate.", "label": "Enable", "name": "enable"}, {"description": "Disable TOS match negate", "help": "Disable TOS match negate.", "label": "Disable", "name": "disable"}] | None = ...,
        traffic_shaper: str | None = ...,
        traffic_shaper_reverse: str | None = ...,
        per_ip_shaper: str | None = ...,
        class_id: int | None = ...,
        diffserv_forward: Literal[{"description": "Enable setting forward (original) traffic DiffServ", "help": "Enable setting forward (original) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting forward (original) traffic DiffServ", "help": "Disable setting forward (original) traffic DiffServ.", "label": "Disable", "name": "disable"}] | None = ...,
        diffserv_reverse: Literal[{"description": "Enable setting reverse (reply) traffic DiffServ", "help": "Enable setting reverse (reply) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting reverse (reply) traffic DiffServ", "help": "Disable setting reverse (reply) traffic DiffServ.", "label": "Disable", "name": "disable"}] | None = ...,
        diffservcode_forward: str | None = ...,
        diffservcode_rev: str | None = ...,
        cos_mask: str | None = ...,
        cos: str | None = ...,
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
        payload_dict: ShapingPolicyPayload | None = ...,
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
    "ShapingPolicy",
    "ShapingPolicyPayload",
]