from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class FortitokenPayload(TypedDict, total=False):
    """
    Type hints for user/fortitoken payload fields.
    
    Configure FortiToken.
    
    **Usage:**
        payload: FortitokenPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    serial_number: NotRequired[str]  # Serial number.
    status: NotRequired[Literal[{"description": "Activate FortiToken", "help": "Activate FortiToken.", "label": "Active", "name": "active"}, {"description": "Lock FortiToken", "help": "Lock FortiToken.", "label": "Lock", "name": "lock"}]]  # Status.
    comments: NotRequired[str]  # Comment.
    license: NotRequired[str]  # Mobile token license.
    activation_code: NotRequired[str]  # Mobile token user activation-code.
    activation_expire: NotRequired[int]  # Mobile token user activation-code expire time.
    reg_id: NotRequired[str]  # Device Reg ID.
    os_ver: NotRequired[str]  # Device Mobile Version.


class Fortitoken:
    """
    Configure FortiToken.
    
    Path: user/fortitoken
    Category: cmdb
    Primary Key: serial-number
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        serial_number: str | None = ...,
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
        serial_number: str,
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
        serial_number: str | None = ...,
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
        serial_number: str | None = ...,
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
        serial_number: str | None = ...,
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
        payload_dict: FortitokenPayload | None = ...,
        serial_number: str | None = ...,
        status: Literal[{"description": "Activate FortiToken", "help": "Activate FortiToken.", "label": "Active", "name": "active"}, {"description": "Lock FortiToken", "help": "Lock FortiToken.", "label": "Lock", "name": "lock"}] | None = ...,
        comments: str | None = ...,
        license: str | None = ...,
        activation_code: str | None = ...,
        activation_expire: int | None = ...,
        reg_id: str | None = ...,
        os_ver: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: FortitokenPayload | None = ...,
        serial_number: str | None = ...,
        status: Literal[{"description": "Activate FortiToken", "help": "Activate FortiToken.", "label": "Active", "name": "active"}, {"description": "Lock FortiToken", "help": "Lock FortiToken.", "label": "Lock", "name": "lock"}] | None = ...,
        comments: str | None = ...,
        license: str | None = ...,
        activation_code: str | None = ...,
        activation_expire: int | None = ...,
        reg_id: str | None = ...,
        os_ver: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        serial_number: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        serial_number: str,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: FortitokenPayload | None = ...,
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
    "Fortitoken",
    "FortitokenPayload",
]