from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class VlanPolicyPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/vlan_policy payload fields.
    
    Configure VLAN policy to be applied on the managed FortiSwitch ports through dynamic-port-policy.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: fortilink, vlan)

    **Usage:**
        payload: VlanPolicyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # VLAN policy name.
    description: NotRequired[str]  # Description for the VLAN policy.
    fortilink: str  # FortiLink interface for which this VLAN policy belongs to.
    vlan: NotRequired[str]  # Native VLAN to be applied when using this VLAN policy.
    allowed_vlans: NotRequired[list[dict[str, Any]]]  # Allowed VLANs to be applied when using this VLAN policy.
    untagged_vlans: NotRequired[list[dict[str, Any]]]  # Untagged VLANs to be applied when using this VLAN policy.
    allowed_vlans_all: NotRequired[Literal[{"description": "Enable all defined VLANs", "help": "Enable all defined VLANs.", "label": "Enable", "name": "enable"}, {"description": "Disable all defined VLANs", "help": "Disable all defined VLANs.", "label": "Disable", "name": "disable"}]]  # Enable/disable all defined VLANs when using this VLAN policy
    discard_mode: NotRequired[Literal[{"description": "Discard disabled", "help": "Discard disabled.", "label": "None", "name": "none"}, {"description": "Discard all frames that are untagged", "help": "Discard all frames that are untagged.", "label": "All Untagged", "name": "all-untagged"}, {"description": "Discard all frames that are tagged", "help": "Discard all frames that are tagged.", "label": "All Tagged", "name": "all-tagged"}]]  # Discard mode to be applied when using this VLAN policy.


class VlanPolicy:
    """
    Configure VLAN policy to be applied on the managed FortiSwitch ports through dynamic-port-policy.
    
    Path: switch_controller/vlan_policy
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
        payload_dict: VlanPolicyPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        fortilink: str | None = ...,
        vlan: str | None = ...,
        allowed_vlans: list[dict[str, Any]] | None = ...,
        untagged_vlans: list[dict[str, Any]] | None = ...,
        allowed_vlans_all: Literal[{"description": "Enable all defined VLANs", "help": "Enable all defined VLANs.", "label": "Enable", "name": "enable"}, {"description": "Disable all defined VLANs", "help": "Disable all defined VLANs.", "label": "Disable", "name": "disable"}] | None = ...,
        discard_mode: Literal[{"description": "Discard disabled", "help": "Discard disabled.", "label": "None", "name": "none"}, {"description": "Discard all frames that are untagged", "help": "Discard all frames that are untagged.", "label": "All Untagged", "name": "all-untagged"}, {"description": "Discard all frames that are tagged", "help": "Discard all frames that are tagged.", "label": "All Tagged", "name": "all-tagged"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: VlanPolicyPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        fortilink: str | None = ...,
        vlan: str | None = ...,
        allowed_vlans: list[dict[str, Any]] | None = ...,
        untagged_vlans: list[dict[str, Any]] | None = ...,
        allowed_vlans_all: Literal[{"description": "Enable all defined VLANs", "help": "Enable all defined VLANs.", "label": "Enable", "name": "enable"}, {"description": "Disable all defined VLANs", "help": "Disable all defined VLANs.", "label": "Disable", "name": "disable"}] | None = ...,
        discard_mode: Literal[{"description": "Discard disabled", "help": "Discard disabled.", "label": "None", "name": "none"}, {"description": "Discard all frames that are untagged", "help": "Discard all frames that are untagged.", "label": "All Untagged", "name": "all-untagged"}, {"description": "Discard all frames that are tagged", "help": "Discard all frames that are tagged.", "label": "All Tagged", "name": "all-tagged"}] | None = ...,
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
        payload_dict: VlanPolicyPayload | None = ...,
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
    "VlanPolicy",
    "VlanPolicyPayload",
]