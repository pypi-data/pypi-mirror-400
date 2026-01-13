from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class VlansPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/initial_config/vlans payload fields.
    
    Configure initial template for auto-generated VLAN interfaces.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.switch-controller.initial-config.template.TemplateEndpoint` (via: default-vlan, nac, nac-segment, +4 more)

    **Usage:**
        payload: VlansPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    optional_vlans: NotRequired[Literal[{"description": "Enable auto-generated VLANs", "help": "Enable auto-generated VLANs.", "label": "Enable", "name": "enable"}, {"description": "Disable auto-generated VLANs", "help": "Disable auto-generated VLANs.", "label": "Disable", "name": "disable"}]]  # Auto-generate pre-configured VLANs upon switch discovery.
    default_vlan: NotRequired[str]  # Default VLAN (native) assigned to all switch ports upon disc
    quarantine: NotRequired[str]  # VLAN for quarantined traffic.
    rspan: NotRequired[str]  # VLAN for RSPAN/ERSPAN mirrored traffic.
    voice: NotRequired[str]  # VLAN dedicated for voice devices.
    video: NotRequired[str]  # VLAN dedicated for video devices.
    nac: NotRequired[str]  # VLAN for NAC onboarding devices.
    nac_segment: NotRequired[str]  # VLAN for NAC segment primary interface.


class Vlans:
    """
    Configure initial template for auto-generated VLAN interfaces.
    
    Path: switch_controller/initial_config/vlans
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
        payload_dict: VlansPayload | None = ...,
        optional_vlans: Literal[{"description": "Enable auto-generated VLANs", "help": "Enable auto-generated VLANs.", "label": "Enable", "name": "enable"}, {"description": "Disable auto-generated VLANs", "help": "Disable auto-generated VLANs.", "label": "Disable", "name": "disable"}] | None = ...,
        default_vlan: str | None = ...,
        quarantine: str | None = ...,
        rspan: str | None = ...,
        voice: str | None = ...,
        video: str | None = ...,
        nac: str | None = ...,
        nac_segment: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: VlansPayload | None = ...,
        optional_vlans: Literal[{"description": "Enable auto-generated VLANs", "help": "Enable auto-generated VLANs.", "label": "Enable", "name": "enable"}, {"description": "Disable auto-generated VLANs", "help": "Disable auto-generated VLANs.", "label": "Disable", "name": "disable"}] | None = ...,
        default_vlan: str | None = ...,
        quarantine: str | None = ...,
        rspan: str | None = ...,
        voice: str | None = ...,
        video: str | None = ...,
        nac: str | None = ...,
        nac_segment: str | None = ...,
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
        payload_dict: VlansPayload | None = ...,
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
    "Vlans",
    "VlansPayload",
]