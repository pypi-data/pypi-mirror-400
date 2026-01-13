from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ApcfgProfilePayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/apcfg_profile payload fields.
    
    Configure AP local configuration profiles.
    
    **Usage:**
        payload: ApcfgProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # AP local configuration profile name.
    ap_family: NotRequired[Literal[{"description": "FortiAP Family", "help": "FortiAP Family.", "label": "Fap", "name": "fap"}, {"description": "FortiAP-U Family", "help": "FortiAP-U Family.", "label": "Fap U", "name": "fap-u"}, {"description": "FortiAP-C Family", "help": "FortiAP-C Family.", "label": "Fap C", "name": "fap-c"}]]  # FortiAP family type (default = fap).
    comment: NotRequired[str]  # Comment.
    ac_type: NotRequired[Literal[{"description": "This controller is the one and only controller that the AP could join after applying AP local configuration", "help": "This controller is the one and only controller that the AP could join after applying AP local configuration.", "label": "Default", "name": "default"}, {"description": "Specified controller is the one and only controller that the AP could join after applying AP local configuration", "help": "Specified controller is the one and only controller that the AP could join after applying AP local configuration.", "label": "Specify", "name": "specify"}, {"description": "Any controller defined by AP local configuration after applying AP local configuration", "help": "Any controller defined by AP local configuration after applying AP local configuration.", "label": "Apcfg", "name": "apcfg"}]]  # Validation controller type (default = default).
    ac_timer: NotRequired[int]  # Maximum waiting time for the AP to join the validation contr
    ac_ip: NotRequired[str]  # IP address of the validation controller that AP must be able
    ac_port: NotRequired[int]  # Port of the validation controller that AP must be able to jo
    command_list: NotRequired[list[dict[str, Any]]]  # AP local configuration command list.


class ApcfgProfile:
    """
    Configure AP local configuration profiles.
    
    Path: wireless_controller/apcfg_profile
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
        payload_dict: ApcfgProfilePayload | None = ...,
        name: str | None = ...,
        ap_family: Literal[{"description": "FortiAP Family", "help": "FortiAP Family.", "label": "Fap", "name": "fap"}, {"description": "FortiAP-U Family", "help": "FortiAP-U Family.", "label": "Fap U", "name": "fap-u"}, {"description": "FortiAP-C Family", "help": "FortiAP-C Family.", "label": "Fap C", "name": "fap-c"}] | None = ...,
        comment: str | None = ...,
        ac_type: Literal[{"description": "This controller is the one and only controller that the AP could join after applying AP local configuration", "help": "This controller is the one and only controller that the AP could join after applying AP local configuration.", "label": "Default", "name": "default"}, {"description": "Specified controller is the one and only controller that the AP could join after applying AP local configuration", "help": "Specified controller is the one and only controller that the AP could join after applying AP local configuration.", "label": "Specify", "name": "specify"}, {"description": "Any controller defined by AP local configuration after applying AP local configuration", "help": "Any controller defined by AP local configuration after applying AP local configuration.", "label": "Apcfg", "name": "apcfg"}] | None = ...,
        ac_timer: int | None = ...,
        ac_ip: str | None = ...,
        ac_port: int | None = ...,
        command_list: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ApcfgProfilePayload | None = ...,
        name: str | None = ...,
        ap_family: Literal[{"description": "FortiAP Family", "help": "FortiAP Family.", "label": "Fap", "name": "fap"}, {"description": "FortiAP-U Family", "help": "FortiAP-U Family.", "label": "Fap U", "name": "fap-u"}, {"description": "FortiAP-C Family", "help": "FortiAP-C Family.", "label": "Fap C", "name": "fap-c"}] | None = ...,
        comment: str | None = ...,
        ac_type: Literal[{"description": "This controller is the one and only controller that the AP could join after applying AP local configuration", "help": "This controller is the one and only controller that the AP could join after applying AP local configuration.", "label": "Default", "name": "default"}, {"description": "Specified controller is the one and only controller that the AP could join after applying AP local configuration", "help": "Specified controller is the one and only controller that the AP could join after applying AP local configuration.", "label": "Specify", "name": "specify"}, {"description": "Any controller defined by AP local configuration after applying AP local configuration", "help": "Any controller defined by AP local configuration after applying AP local configuration.", "label": "Apcfg", "name": "apcfg"}] | None = ...,
        ac_timer: int | None = ...,
        ac_ip: str | None = ...,
        ac_port: int | None = ...,
        command_list: list[dict[str, Any]] | None = ...,
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
        payload_dict: ApcfgProfilePayload | None = ...,
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
    "ApcfgProfile",
    "ApcfgProfilePayload",
]