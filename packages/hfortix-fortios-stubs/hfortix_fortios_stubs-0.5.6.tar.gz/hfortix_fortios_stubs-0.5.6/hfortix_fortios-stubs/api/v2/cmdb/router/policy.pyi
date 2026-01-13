from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class PolicyPayload(TypedDict, total=False):
    """
    Type hints for router/policy payload fields.
    
    Configure IPv4 routing policies.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: output-device)

    **Usage:**
        payload: PolicyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    seq_num: NotRequired[int]  # Sequence number(1-65535).
    input_device: NotRequired[list[dict[str, Any]]]  # Incoming interface name.
    input_device_negate: NotRequired[Literal[{"description": "Enable negation of input device match", "help": "Enable negation of input device match.", "label": "Enable", "name": "enable"}, {"description": "Disable negation of input device match", "help": "Disable negation of input device match.", "label": "Disable", "name": "disable"}]]  # Enable/disable negation of input device match.
    src: NotRequired[list[dict[str, Any]]]  # Source IP and mask (x.x.x.x/x).
    srcaddr: NotRequired[list[dict[str, Any]]]  # Source address name.
    src_negate: NotRequired[Literal[{"description": "Enable source address negation", "help": "Enable source address negation.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negation", "help": "Disable source address negation.", "label": "Disable", "name": "disable"}]]  # Enable/disable negating source address match.
    dst: NotRequired[list[dict[str, Any]]]  # Destination IP and mask (x.x.x.x/x).
    dstaddr: NotRequired[list[dict[str, Any]]]  # Destination address name.
    dst_negate: NotRequired[Literal[{"description": "Enable destination address negation", "help": "Enable destination address negation.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negation", "help": "Disable destination address negation.", "label": "Disable", "name": "disable"}]]  # Enable/disable negating destination address match.
    action: NotRequired[Literal[{"description": "Do not search policy route table", "help": "Do not search policy route table.", "label": "Deny", "name": "deny"}, {"description": "Use this policy route for forwarding", "help": "Use this policy route for forwarding.", "label": "Permit", "name": "permit"}]]  # Action of the policy route.
    protocol: NotRequired[int]  # Protocol number (0 - 255).
    start_port: NotRequired[int]  # Start destination port number (0 - 65535).
    end_port: NotRequired[int]  # End destination port number (0 - 65535).
    start_source_port: NotRequired[int]  # Start source port number (0 - 65535).
    end_source_port: NotRequired[int]  # End source port number (0 - 65535).
    gateway: NotRequired[str]  # IP address of the gateway.
    output_device: NotRequired[str]  # Outgoing interface name.
    tos: NotRequired[str]  # Type of service bit pattern.
    tos_mask: NotRequired[str]  # Type of service evaluated bits.
    status: NotRequired[Literal[{"description": "Enable this policy route", "help": "Enable this policy route.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy route", "help": "Disable this policy route.", "label": "Disable", "name": "disable"}]]  # Enable/disable this policy route.
    comments: NotRequired[str]  # Optional comments.
    internet_service_id: NotRequired[list[dict[str, Any]]]  # Destination Internet Service ID.
    internet_service_custom: NotRequired[list[dict[str, Any]]]  # Custom Destination Internet Service name.
    internet_service_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard Destination Internet Service name.
    users: NotRequired[list[dict[str, Any]]]  # List of users.
    groups: NotRequired[list[dict[str, Any]]]  # List of user groups.


class Policy:
    """
    Configure IPv4 routing policies.
    
    Path: router/policy
    Category: cmdb
    Primary Key: seq-num
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        seq_num: int | None = ...,
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
        seq_num: int,
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
        seq_num: int | None = ...,
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
        seq_num: int | None = ...,
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
        seq_num: int | None = ...,
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
        payload_dict: PolicyPayload | None = ...,
        seq_num: int | None = ...,
        input_device: list[dict[str, Any]] | None = ...,
        input_device_negate: Literal[{"description": "Enable negation of input device match", "help": "Enable negation of input device match.", "label": "Enable", "name": "enable"}, {"description": "Disable negation of input device match", "help": "Disable negation of input device match.", "label": "Disable", "name": "disable"}] | None = ...,
        src: list[dict[str, Any]] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        src_negate: Literal[{"description": "Enable source address negation", "help": "Enable source address negation.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negation", "help": "Disable source address negation.", "label": "Disable", "name": "disable"}] | None = ...,
        dst: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        dst_negate: Literal[{"description": "Enable destination address negation", "help": "Enable destination address negation.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negation", "help": "Disable destination address negation.", "label": "Disable", "name": "disable"}] | None = ...,
        action: Literal[{"description": "Do not search policy route table", "help": "Do not search policy route table.", "label": "Deny", "name": "deny"}, {"description": "Use this policy route for forwarding", "help": "Use this policy route for forwarding.", "label": "Permit", "name": "permit"}] | None = ...,
        protocol: int | None = ...,
        start_port: int | None = ...,
        end_port: int | None = ...,
        start_source_port: int | None = ...,
        end_source_port: int | None = ...,
        gateway: str | None = ...,
        output_device: str | None = ...,
        tos: str | None = ...,
        tos_mask: str | None = ...,
        status: Literal[{"description": "Enable this policy route", "help": "Enable this policy route.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy route", "help": "Disable this policy route.", "label": "Disable", "name": "disable"}] | None = ...,
        comments: str | None = ...,
        internet_service_id: list[dict[str, Any]] | None = ...,
        internet_service_custom: list[dict[str, Any]] | None = ...,
        internet_service_fortiguard: list[dict[str, Any]] | None = ...,
        users: list[dict[str, Any]] | None = ...,
        groups: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: PolicyPayload | None = ...,
        seq_num: int | None = ...,
        input_device: list[dict[str, Any]] | None = ...,
        input_device_negate: Literal[{"description": "Enable negation of input device match", "help": "Enable negation of input device match.", "label": "Enable", "name": "enable"}, {"description": "Disable negation of input device match", "help": "Disable negation of input device match.", "label": "Disable", "name": "disable"}] | None = ...,
        src: list[dict[str, Any]] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        src_negate: Literal[{"description": "Enable source address negation", "help": "Enable source address negation.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negation", "help": "Disable source address negation.", "label": "Disable", "name": "disable"}] | None = ...,
        dst: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        dst_negate: Literal[{"description": "Enable destination address negation", "help": "Enable destination address negation.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negation", "help": "Disable destination address negation.", "label": "Disable", "name": "disable"}] | None = ...,
        action: Literal[{"description": "Do not search policy route table", "help": "Do not search policy route table.", "label": "Deny", "name": "deny"}, {"description": "Use this policy route for forwarding", "help": "Use this policy route for forwarding.", "label": "Permit", "name": "permit"}] | None = ...,
        protocol: int | None = ...,
        start_port: int | None = ...,
        end_port: int | None = ...,
        start_source_port: int | None = ...,
        end_source_port: int | None = ...,
        gateway: str | None = ...,
        output_device: str | None = ...,
        tos: str | None = ...,
        tos_mask: str | None = ...,
        status: Literal[{"description": "Enable this policy route", "help": "Enable this policy route.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy route", "help": "Disable this policy route.", "label": "Disable", "name": "disable"}] | None = ...,
        comments: str | None = ...,
        internet_service_id: list[dict[str, Any]] | None = ...,
        internet_service_custom: list[dict[str, Any]] | None = ...,
        internet_service_fortiguard: list[dict[str, Any]] | None = ...,
        users: list[dict[str, Any]] | None = ...,
        groups: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        seq_num: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        seq_num: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: PolicyPayload | None = ...,
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
    "Policy",
    "PolicyPayload",
]