from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class CustomPayload(TypedDict, total=False):
    """
    Type hints for ips/custom payload fields.
    
    Configure IPS custom signature.
    
    **Usage:**
        payload: CustomPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    tag: NotRequired[str]  # Signature tag.
    signature: NotRequired[str]  # Custom signature enclosed in single quotes.
    rule_id: NotRequired[int]  # Signature ID.
    severity: NotRequired[str]  # Relative severity of the signature, from info to critical. L
    location: NotRequired[list[dict[str, Any]]]  # Protect client or server traffic.
    os: NotRequired[list[dict[str, Any]]]  # Operating system(s) that the signature protects. Blank for a
    application: NotRequired[list[dict[str, Any]]]  # Applications to be protected. Blank for all applications.
    protocol: NotRequired[str]  # Protocol(s) that the signature scans. Blank for all protocol
    status: NotRequired[Literal[{"description": "Disable status", "help": "Disable status.", "label": "Disable", "name": "disable"}, {"description": "Enable status", "help": "Enable status.", "label": "Enable", "name": "enable"}]]  # Enable/disable this signature.
    log: NotRequired[Literal[{"description": "Disable logging", "help": "Disable logging.", "label": "Disable", "name": "disable"}, {"description": "Enable logging", "help": "Enable logging.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging.
    log_packet: NotRequired[Literal[{"description": "Disable packet logging", "help": "Disable packet logging.", "label": "Disable", "name": "disable"}, {"description": "Enable packet logging", "help": "Enable packet logging.", "label": "Enable", "name": "enable"}]]  # Enable/disable packet logging.
    action: NotRequired[Literal[{"description": "Pass or allow matching traffic", "help": "Pass or allow matching traffic.", "label": "Pass", "name": "pass"}, {"description": "Block or drop matching traffic", "help": "Block or drop matching traffic.", "label": "Block", "name": "block"}]]  # Default action (pass or block) for this signature.
    comment: NotRequired[str]  # Comment.


class Custom:
    """
    Configure IPS custom signature.
    
    Path: ips/custom
    Category: cmdb
    Primary Key: tag
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        tag: str | None = ...,
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
        tag: str,
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
        tag: str | None = ...,
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
        tag: str | None = ...,
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
        tag: str | None = ...,
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
        payload_dict: CustomPayload | None = ...,
        tag: str | None = ...,
        signature: str | None = ...,
        rule_id: int | None = ...,
        severity: str | None = ...,
        location: list[dict[str, Any]] | None = ...,
        os: list[dict[str, Any]] | None = ...,
        application: list[dict[str, Any]] | None = ...,
        protocol: str | None = ...,
        status: Literal[{"description": "Disable status", "help": "Disable status.", "label": "Disable", "name": "disable"}, {"description": "Enable status", "help": "Enable status.", "label": "Enable", "name": "enable"}] | None = ...,
        log: Literal[{"description": "Disable logging", "help": "Disable logging.", "label": "Disable", "name": "disable"}, {"description": "Enable logging", "help": "Enable logging.", "label": "Enable", "name": "enable"}] | None = ...,
        log_packet: Literal[{"description": "Disable packet logging", "help": "Disable packet logging.", "label": "Disable", "name": "disable"}, {"description": "Enable packet logging", "help": "Enable packet logging.", "label": "Enable", "name": "enable"}] | None = ...,
        action: Literal[{"description": "Pass or allow matching traffic", "help": "Pass or allow matching traffic.", "label": "Pass", "name": "pass"}, {"description": "Block or drop matching traffic", "help": "Block or drop matching traffic.", "label": "Block", "name": "block"}] | None = ...,
        comment: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: CustomPayload | None = ...,
        tag: str | None = ...,
        signature: str | None = ...,
        rule_id: int | None = ...,
        severity: str | None = ...,
        location: list[dict[str, Any]] | None = ...,
        os: list[dict[str, Any]] | None = ...,
        application: list[dict[str, Any]] | None = ...,
        protocol: str | None = ...,
        status: Literal[{"description": "Disable status", "help": "Disable status.", "label": "Disable", "name": "disable"}, {"description": "Enable status", "help": "Enable status.", "label": "Enable", "name": "enable"}] | None = ...,
        log: Literal[{"description": "Disable logging", "help": "Disable logging.", "label": "Disable", "name": "disable"}, {"description": "Enable logging", "help": "Enable logging.", "label": "Enable", "name": "enable"}] | None = ...,
        log_packet: Literal[{"description": "Disable packet logging", "help": "Disable packet logging.", "label": "Disable", "name": "disable"}, {"description": "Enable packet logging", "help": "Enable packet logging.", "label": "Enable", "name": "enable"}] | None = ...,
        action: Literal[{"description": "Pass or allow matching traffic", "help": "Pass or allow matching traffic.", "label": "Pass", "name": "pass"}, {"description": "Block or drop matching traffic", "help": "Block or drop matching traffic.", "label": "Block", "name": "block"}] | None = ...,
        comment: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        tag: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        tag: str,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: CustomPayload | None = ...,
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
    "Custom",
    "CustomPayload",
]