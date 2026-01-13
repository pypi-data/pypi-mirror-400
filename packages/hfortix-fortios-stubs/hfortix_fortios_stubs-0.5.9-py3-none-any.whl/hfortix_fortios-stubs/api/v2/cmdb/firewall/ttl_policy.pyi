from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class TtlPolicyPayload(TypedDict, total=False):
    """
    Type hints for firewall/ttl_policy payload fields.
    
    Configure TTL policies.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.firewall.schedule.group.GroupEndpoint` (via: schedule)
        - :class:`~.firewall.schedule.onetime.OnetimeEndpoint` (via: schedule)
        - :class:`~.firewall.schedule.recurring.RecurringEndpoint` (via: schedule)
        - :class:`~.system.interface.InterfaceEndpoint` (via: srcintf)
        - :class:`~.system.sdwan.zone.ZoneEndpoint` (via: srcintf)
        - :class:`~.system.zone.ZoneEndpoint` (via: srcintf)

    **Usage:**
        payload: TtlPolicyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    id: int  # ID.
    status: NotRequired[Literal[{"description": "Enable this TTL policy", "help": "Enable this TTL policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this TTL policy", "help": "Disable this TTL policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable this TTL policy.
    action: NotRequired[Literal[{"description": "Allow traffic matching this policy", "help": "Allow traffic matching this policy.", "label": "Accept", "name": "accept"}, {"description": "Deny or block traffic matching this policy", "help": "Deny or block traffic matching this policy.", "label": "Deny", "name": "deny"}]]  # Action to be performed on traffic matching this policy (defa
    srcintf: str  # Source interface name from available interfaces.
    srcaddr: list[dict[str, Any]]  # Source address object(s) from available options. Separate mu
    service: list[dict[str, Any]]  # Service object(s) from available options. Separate multiple 
    schedule: str  # Schedule object from available options.
    ttl: str  # Value/range to match against the packet's Time to Live value


class TtlPolicy:
    """
    Configure TTL policies.
    
    Path: firewall/ttl_policy
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
        payload_dict: TtlPolicyPayload | None = ...,
        id: int | None = ...,
        status: Literal[{"description": "Enable this TTL policy", "help": "Enable this TTL policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this TTL policy", "help": "Disable this TTL policy.", "label": "Disable", "name": "disable"}] | None = ...,
        action: Literal[{"description": "Allow traffic matching this policy", "help": "Allow traffic matching this policy.", "label": "Accept", "name": "accept"}, {"description": "Deny or block traffic matching this policy", "help": "Deny or block traffic matching this policy.", "label": "Deny", "name": "deny"}] | None = ...,
        srcintf: str | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        schedule: str | None = ...,
        ttl: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: TtlPolicyPayload | None = ...,
        id: int | None = ...,
        status: Literal[{"description": "Enable this TTL policy", "help": "Enable this TTL policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this TTL policy", "help": "Disable this TTL policy.", "label": "Disable", "name": "disable"}] | None = ...,
        action: Literal[{"description": "Allow traffic matching this policy", "help": "Allow traffic matching this policy.", "label": "Accept", "name": "accept"}, {"description": "Deny or block traffic matching this policy", "help": "Deny or block traffic matching this policy.", "label": "Deny", "name": "deny"}] | None = ...,
        srcintf: str | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        schedule: str | None = ...,
        ttl: str | None = ...,
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
        payload_dict: TtlPolicyPayload | None = ...,
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
    "TtlPolicy",
    "TtlPolicyPayload",
]