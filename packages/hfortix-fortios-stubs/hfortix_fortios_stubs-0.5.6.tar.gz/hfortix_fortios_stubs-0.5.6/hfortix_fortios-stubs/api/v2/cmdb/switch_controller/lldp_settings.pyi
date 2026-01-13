from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class LldpSettingsPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/lldp_settings payload fields.
    
    Configure FortiSwitch LLDP settings.
    
    **Usage:**
        payload: LldpSettingsPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    tx_hold: NotRequired[int]  # Number of tx-intervals before local LLDP data expires (1 - 1
    tx_interval: NotRequired[int]  # Frequency of LLDP PDU transmission from FortiSwitch (5 - 409
    fast_start_interval: NotRequired[int]  # Frequency of LLDP PDU transmission from FortiSwitch for the 
    management_interface: NotRequired[Literal[{"description": "Use internal interface", "help": "Use internal interface.", "label": "Internal", "name": "internal"}, {"description": "Use management interface", "help": "Use management interface.", "label": "Mgmt", "name": "mgmt"}]]  # Primary management interface to be advertised in LLDP and CD
    device_detection: NotRequired[Literal[{"description": "Disable dynamic detection of LLDP neighbor devices", "help": "Disable dynamic detection of LLDP neighbor devices.", "label": "Disable", "name": "disable"}, {"description": "Enable dynamic detection of LLDP neighbor devices", "help": "Enable dynamic detection of LLDP neighbor devices.", "label": "Enable", "name": "enable"}]]  # Enable/disable dynamic detection of LLDP neighbor devices fo


class LldpSettings:
    """
    Configure FortiSwitch LLDP settings.
    
    Path: switch_controller/lldp_settings
    Category: cmdb
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
        payload_dict: LldpSettingsPayload | None = ...,
        tx_hold: int | None = ...,
        tx_interval: int | None = ...,
        fast_start_interval: int | None = ...,
        management_interface: Literal[{"description": "Use internal interface", "help": "Use internal interface.", "label": "Internal", "name": "internal"}, {"description": "Use management interface", "help": "Use management interface.", "label": "Mgmt", "name": "mgmt"}] | None = ...,
        device_detection: Literal[{"description": "Disable dynamic detection of LLDP neighbor devices", "help": "Disable dynamic detection of LLDP neighbor devices.", "label": "Disable", "name": "disable"}, {"description": "Enable dynamic detection of LLDP neighbor devices", "help": "Enable dynamic detection of LLDP neighbor devices.", "label": "Enable", "name": "enable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: LldpSettingsPayload | None = ...,
        tx_hold: int | None = ...,
        tx_interval: int | None = ...,
        fast_start_interval: int | None = ...,
        management_interface: Literal[{"description": "Use internal interface", "help": "Use internal interface.", "label": "Internal", "name": "internal"}, {"description": "Use management interface", "help": "Use management interface.", "label": "Mgmt", "name": "mgmt"}] | None = ...,
        device_detection: Literal[{"description": "Disable dynamic detection of LLDP neighbor devices", "help": "Disable dynamic detection of LLDP neighbor devices.", "label": "Disable", "name": "disable"}, {"description": "Enable dynamic detection of LLDP neighbor devices", "help": "Enable dynamic detection of LLDP neighbor devices.", "label": "Enable", "name": "enable"}] | None = ...,
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
        payload_dict: LldpSettingsPayload | None = ...,
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
    "LldpSettings",
    "LldpSettingsPayload",
]