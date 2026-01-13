from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class LocalInPolicy6Payload(TypedDict, total=False):
    """
    Type hints for firewall/local_in_policy6 payload fields.
    
    Configure user defined IPv6 local-in policies.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.firewall.schedule.group.GroupEndpoint` (via: schedule)
        - :class:`~.firewall.schedule.onetime.OnetimeEndpoint` (via: schedule)
        - :class:`~.firewall.schedule.recurring.RecurringEndpoint` (via: schedule)

    **Usage:**
        payload: LocalInPolicy6Payload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    policyid: NotRequired[int]  # User defined local in policy ID.
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    intf: list[dict[str, Any]]  # Incoming interface name from available options.
    srcaddr: list[dict[str, Any]]  # Source address object from available options.
    srcaddr_negate: NotRequired[Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negate", "help": "Disable source address negate.", "label": "Disable", "name": "disable"}]]  # When enabled srcaddr specifies what the source address must 
    dstaddr: list[dict[str, Any]]  # Destination address object from available options.
    internet_service6_src: NotRequired[Literal[{"description": "Enable use of IPv6 Internet Services source in local-in policy", "help": "Enable use of IPv6 Internet Services source in local-in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services source in local-in policy", "help": "Disable use of IPv6 Internet Services source in local-in policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of IPv6 Internet Services in source for t
    internet_service6_src_name: NotRequired[list[dict[str, Any]]]  # IPv6 Internet Service source name.
    internet_service6_src_group: NotRequired[list[dict[str, Any]]]  # Internet Service6 source group name.
    internet_service6_src_custom: NotRequired[list[dict[str, Any]]]  # Custom IPv6 Internet Service source name.
    internet_service6_src_custom_group: NotRequired[list[dict[str, Any]]]  # Custom Internet Service6 source group name.
    internet_service6_src_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard IPv6 Internet Service source name.
    dstaddr_negate: NotRequired[Literal[{"description": "Enable destination address negate", "help": "Enable destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}]]  # When enabled dstaddr specifies what the destination address 
    action: NotRequired[Literal[{"description": "Allow local-in traffic matching this policy", "help": "Allow local-in traffic matching this policy.", "label": "Accept", "name": "accept"}, {"description": "Deny or block local-in traffic matching this policy", "help": "Deny or block local-in traffic matching this policy.", "label": "Deny", "name": "deny"}]]  # Action performed on traffic matching the policy (default = d
    service: list[dict[str, Any]]  # Service object from available options. Separate names with a
    service_negate: NotRequired[Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}]]  # When enabled service specifies what the service must NOT be.
    internet_service6_src_negate: NotRequired[Literal[{"description": "Enable negated IPv6 Internet Service source match", "help": "Enable negated IPv6 Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service source match", "help": "Disable negated IPv6 Internet Service source match.", "label": "Disable", "name": "disable"}]]  # When enabled internet-service6-src specifies what the servic
    schedule: str  # Schedule object from available options.
    status: NotRequired[Literal[{"description": "Enable this local-in policy", "help": "Enable this local-in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this local-in policy", "help": "Disable this local-in policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable this local-in policy.
    virtual_patch: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable the virtual patching feature.
    logtraffic: NotRequired[Literal[{"description": "Enable local-in traffic logging", "help": "Enable local-in traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in traffic logging", "help": "Disable local-in traffic logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable local-in traffic logging.
    comments: NotRequired[str]  # Comment.


class LocalInPolicy6:
    """
    Configure user defined IPv6 local-in policies.
    
    Path: firewall/local_in_policy6
    Category: cmdb
    Primary Key: policyid
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        policyid: int | None = ...,
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
        policyid: int,
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
        policyid: int | None = ...,
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
        policyid: int | None = ...,
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
        policyid: int | None = ...,
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
        payload_dict: LocalInPolicy6Payload | None = ...,
        policyid: int | None = ...,
        uuid: str | None = ...,
        intf: list[dict[str, Any]] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        srcaddr_negate: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negate", "help": "Disable source address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        internet_service6_src: Literal[{"description": "Enable use of IPv6 Internet Services source in local-in policy", "help": "Enable use of IPv6 Internet Services source in local-in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services source in local-in policy", "help": "Disable use of IPv6 Internet Services source in local-in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_src_name: list[dict[str, Any]] | None = ...,
        internet_service6_src_group: list[dict[str, Any]] | None = ...,
        internet_service6_src_custom: list[dict[str, Any]] | None = ...,
        internet_service6_src_custom_group: list[dict[str, Any]] | None = ...,
        internet_service6_src_fortiguard: list[dict[str, Any]] | None = ...,
        dstaddr_negate: Literal[{"description": "Enable destination address negate", "help": "Enable destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        action: Literal[{"description": "Allow local-in traffic matching this policy", "help": "Allow local-in traffic matching this policy.", "label": "Accept", "name": "accept"}, {"description": "Deny or block local-in traffic matching this policy", "help": "Deny or block local-in traffic matching this policy.", "label": "Deny", "name": "deny"}] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        service_negate: Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_src_negate: Literal[{"description": "Enable negated IPv6 Internet Service source match", "help": "Enable negated IPv6 Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service source match", "help": "Disable negated IPv6 Internet Service source match.", "label": "Disable", "name": "disable"}] | None = ...,
        schedule: str | None = ...,
        status: Literal[{"description": "Enable this local-in policy", "help": "Enable this local-in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this local-in policy", "help": "Disable this local-in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        virtual_patch: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        logtraffic: Literal[{"description": "Enable local-in traffic logging", "help": "Enable local-in traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in traffic logging", "help": "Disable local-in traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        comments: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: LocalInPolicy6Payload | None = ...,
        policyid: int | None = ...,
        uuid: str | None = ...,
        intf: list[dict[str, Any]] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        srcaddr_negate: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negate", "help": "Disable source address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        internet_service6_src: Literal[{"description": "Enable use of IPv6 Internet Services source in local-in policy", "help": "Enable use of IPv6 Internet Services source in local-in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services source in local-in policy", "help": "Disable use of IPv6 Internet Services source in local-in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_src_name: list[dict[str, Any]] | None = ...,
        internet_service6_src_group: list[dict[str, Any]] | None = ...,
        internet_service6_src_custom: list[dict[str, Any]] | None = ...,
        internet_service6_src_custom_group: list[dict[str, Any]] | None = ...,
        internet_service6_src_fortiguard: list[dict[str, Any]] | None = ...,
        dstaddr_negate: Literal[{"description": "Enable destination address negate", "help": "Enable destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        action: Literal[{"description": "Allow local-in traffic matching this policy", "help": "Allow local-in traffic matching this policy.", "label": "Accept", "name": "accept"}, {"description": "Deny or block local-in traffic matching this policy", "help": "Deny or block local-in traffic matching this policy.", "label": "Deny", "name": "deny"}] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        service_negate: Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_src_negate: Literal[{"description": "Enable negated IPv6 Internet Service source match", "help": "Enable negated IPv6 Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service source match", "help": "Disable negated IPv6 Internet Service source match.", "label": "Disable", "name": "disable"}] | None = ...,
        schedule: str | None = ...,
        status: Literal[{"description": "Enable this local-in policy", "help": "Enable this local-in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this local-in policy", "help": "Disable this local-in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        virtual_patch: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        logtraffic: Literal[{"description": "Enable local-in traffic logging", "help": "Enable local-in traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in traffic logging", "help": "Disable local-in traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        comments: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        policyid: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        policyid: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: LocalInPolicy6Payload | None = ...,
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
    "LocalInPolicy6",
    "LocalInPolicy6Payload",
]