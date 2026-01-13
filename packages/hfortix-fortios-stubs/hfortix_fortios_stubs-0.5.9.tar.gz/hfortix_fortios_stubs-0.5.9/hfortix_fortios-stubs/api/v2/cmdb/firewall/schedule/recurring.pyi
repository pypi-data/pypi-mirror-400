from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class RecurringPayload(TypedDict, total=False):
    """
    Type hints for firewall/schedule/recurring payload fields.
    
    Recurring schedule configuration.
    
    **Usage:**
        payload: RecurringPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Recurring schedule name.
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    start: str  # Time of day to start the schedule, format hh:mm.
    end: str  # Time of day to end the schedule, format hh:mm.
    day: NotRequired[Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}, {"description": "None", "help": "None.", "label": "None", "name": "none"}]]  # One or more days of the week on which the schedule is valid.
    label_day: NotRequired[Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "1 AM - 4 AM    early-morning:4 AM - 7 AM", "help": "1 AM - 4 AM", "label": "Over Night", "name": "over-night"}, {"help": "4 AM - 7 AM.", "label": "Early Morning", "name": "early-morning"}, {"description": "7 AM - 10 AM", "help": "7 AM - 10 AM.", "label": "Morning", "name": "morning"}, {"description": "10 AM - 1 PM", "help": "10 AM - 1 PM.", "label": "Midday", "name": "midday"}, {"description": "1 PM - 4 PM", "help": "1 PM - 4 PM.", "label": "Afternoon", "name": "afternoon"}, {"description": "4 PM - 7 PM", "help": "4 PM - 7 PM.", "label": "Evening", "name": "evening"}, {"description": "7 PM - 10 PM", "help": "7 PM - 10 PM.", "label": "Night", "name": "night"}, {"description": "10 PM - 1 AM", "help": "10 PM - 1 AM.", "label": "Late Night", "name": "late-night"}]]  # Configure a window during the time of day in which the sched
    color: NotRequired[int]  # Color of icon on the GUI.
    fabric_object: NotRequired[Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}]]  # Security Fabric global object setting.


class Recurring:
    """
    Recurring schedule configuration.
    
    Path: firewall/schedule/recurring
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
        payload_dict: RecurringPayload | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        start: str | None = ...,
        end: str | None = ...,
        day: Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}, {"description": "None", "help": "None.", "label": "None", "name": "none"}] | None = ...,
        label_day: Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "1 AM - 4 AM    early-morning:4 AM - 7 AM", "help": "1 AM - 4 AM", "label": "Over Night", "name": "over-night"}, {"help": "4 AM - 7 AM.", "label": "Early Morning", "name": "early-morning"}, {"description": "7 AM - 10 AM", "help": "7 AM - 10 AM.", "label": "Morning", "name": "morning"}, {"description": "10 AM - 1 PM", "help": "10 AM - 1 PM.", "label": "Midday", "name": "midday"}, {"description": "1 PM - 4 PM", "help": "1 PM - 4 PM.", "label": "Afternoon", "name": "afternoon"}, {"description": "4 PM - 7 PM", "help": "4 PM - 7 PM.", "label": "Evening", "name": "evening"}, {"description": "7 PM - 10 PM", "help": "7 PM - 10 PM.", "label": "Night", "name": "night"}, {"description": "10 PM - 1 AM", "help": "10 PM - 1 AM.", "label": "Late Night", "name": "late-night"}] | None = ...,
        color: int | None = ...,
        fabric_object: Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: RecurringPayload | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        start: str | None = ...,
        end: str | None = ...,
        day: Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}, {"description": "None", "help": "None.", "label": "None", "name": "none"}] | None = ...,
        label_day: Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "1 AM - 4 AM    early-morning:4 AM - 7 AM", "help": "1 AM - 4 AM", "label": "Over Night", "name": "over-night"}, {"help": "4 AM - 7 AM.", "label": "Early Morning", "name": "early-morning"}, {"description": "7 AM - 10 AM", "help": "7 AM - 10 AM.", "label": "Morning", "name": "morning"}, {"description": "10 AM - 1 PM", "help": "10 AM - 1 PM.", "label": "Midday", "name": "midday"}, {"description": "1 PM - 4 PM", "help": "1 PM - 4 PM.", "label": "Afternoon", "name": "afternoon"}, {"description": "4 PM - 7 PM", "help": "4 PM - 7 PM.", "label": "Evening", "name": "evening"}, {"description": "7 PM - 10 PM", "help": "7 PM - 10 PM.", "label": "Night", "name": "night"}, {"description": "10 PM - 1 AM", "help": "10 PM - 1 AM.", "label": "Late Night", "name": "late-night"}] | None = ...,
        color: int | None = ...,
        fabric_object: Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: RecurringPayload | None = ...,
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
    "Recurring",
    "RecurringPayload",
]