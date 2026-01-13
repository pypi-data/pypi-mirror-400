from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class OtvpPayload(TypedDict, total=False):
    """
    Type hints for rule/otvp payload fields.
    
    Show OT patch signatures.
    
    **Usage:**
        payload: OtvpPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Rule name.
    status: NotRequired[Literal[{"help": "Disable status.", "name": "disable"}, {"help": "Enable status.", "name": "enable"}]]  # Print all OT patch rules information.
    log: NotRequired[Literal[{"description": "Disable logging", "help": "Disable logging.", "label": "Disable", "name": "disable"}, {"description": "Enable logging", "help": "Enable logging.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging.
    log_packet: NotRequired[Literal[{"description": "Disable packet logging", "help": "Disable packet logging.", "label": "Disable", "name": "disable"}, {"description": "Enable packet logging", "help": "Enable packet logging.", "label": "Enable", "name": "enable"}]]  # Enable/disable packet logging.
    action: NotRequired[Literal[{"description": "Pass or allow matching traffic", "help": "Pass or allow matching traffic.", "label": "Pass", "name": "pass"}, {"description": "Block or drop matching traffic", "help": "Block or drop matching traffic.", "label": "Block", "name": "block"}]]  # Action.
    group: NotRequired[str]  # Group.
    severity: NotRequired[str]  # Severity.
    location: NotRequired[list[dict[str, Any]]]  # Vulnerable location.
    os: NotRequired[str]  # Vulnerable operation systems.
    application: NotRequired[str]  # Vulnerable applications.
    service: NotRequired[str]  # Vulnerable service.
    rule_id: NotRequired[int]  # Rule ID.
    rev: NotRequired[int]  # Revision.
    date: NotRequired[int]  # Date.
    metadata: NotRequired[list[dict[str, Any]]]  # Meta data.


class Otvp:
    """
    Show OT patch signatures.
    
    Path: rule/otvp
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
        payload_dict: OtvpPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"help": "Disable status.", "name": "disable"}, {"help": "Enable status.", "name": "enable"}] | None = ...,
        log: Literal[{"description": "Disable logging", "help": "Disable logging.", "label": "Disable", "name": "disable"}, {"description": "Enable logging", "help": "Enable logging.", "label": "Enable", "name": "enable"}] | None = ...,
        log_packet: Literal[{"description": "Disable packet logging", "help": "Disable packet logging.", "label": "Disable", "name": "disable"}, {"description": "Enable packet logging", "help": "Enable packet logging.", "label": "Enable", "name": "enable"}] | None = ...,
        action: Literal[{"description": "Pass or allow matching traffic", "help": "Pass or allow matching traffic.", "label": "Pass", "name": "pass"}, {"description": "Block or drop matching traffic", "help": "Block or drop matching traffic.", "label": "Block", "name": "block"}] | None = ...,
        group: str | None = ...,
        severity: str | None = ...,
        location: list[dict[str, Any]] | None = ...,
        os: str | None = ...,
        application: str | None = ...,
        service: str | None = ...,
        rule_id: int | None = ...,
        rev: int | None = ...,
        date: int | None = ...,
        metadata: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: OtvpPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"help": "Disable status.", "name": "disable"}, {"help": "Enable status.", "name": "enable"}] | None = ...,
        log: Literal[{"description": "Disable logging", "help": "Disable logging.", "label": "Disable", "name": "disable"}, {"description": "Enable logging", "help": "Enable logging.", "label": "Enable", "name": "enable"}] | None = ...,
        log_packet: Literal[{"description": "Disable packet logging", "help": "Disable packet logging.", "label": "Disable", "name": "disable"}, {"description": "Enable packet logging", "help": "Enable packet logging.", "label": "Enable", "name": "enable"}] | None = ...,
        action: Literal[{"description": "Pass or allow matching traffic", "help": "Pass or allow matching traffic.", "label": "Pass", "name": "pass"}, {"description": "Block or drop matching traffic", "help": "Block or drop matching traffic.", "label": "Block", "name": "block"}] | None = ...,
        group: str | None = ...,
        severity: str | None = ...,
        location: list[dict[str, Any]] | None = ...,
        os: str | None = ...,
        application: str | None = ...,
        service: str | None = ...,
        rule_id: int | None = ...,
        rev: int | None = ...,
        date: int | None = ...,
        metadata: list[dict[str, Any]] | None = ...,
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
        payload_dict: OtvpPayload | None = ...,
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
    "Otvp",
    "OtvpPayload",
]