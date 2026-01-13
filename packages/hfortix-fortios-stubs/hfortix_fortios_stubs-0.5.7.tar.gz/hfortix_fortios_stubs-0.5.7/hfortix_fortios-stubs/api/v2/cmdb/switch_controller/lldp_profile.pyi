from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class LldpProfilePayload(TypedDict, total=False):
    """
    Type hints for switch_controller/lldp_profile payload fields.
    
    Configure FortiSwitch LLDP profiles.
    
    **Usage:**
        payload: LldpProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Profile name.
    med_tlvs: NotRequired[Literal[{"description": "Inventory management TLVs", "help": "Inventory management TLVs.", "label": "Inventory Management", "name": "inventory-management"}, {"description": "Network policy TLVs", "help": "Network policy TLVs.", "label": "Network Policy", "name": "network-policy"}, {"description": "Power manangement TLVs", "help": "Power manangement TLVs.", "label": "Power Management", "name": "power-management"}, {"description": "Location identificaion TLVs", "help": "Location identificaion TLVs.", "label": "Location Identification", "name": "location-identification"}]]  # Transmitted LLDP-MED TLVs (type-length-value descriptions).
    x802_1_tlvs: NotRequired[Literal[{"description": "Port native VLAN TLV", "help": "Port native VLAN TLV.", "label": "Port Vlan Id", "name": "port-vlan-id"}]]  # Transmitted IEEE 802.1 TLVs.
    x802_3_tlvs: NotRequired[Literal[{"description": "Maximum frame size TLV", "help": "Maximum frame size TLV.", "label": "Max Frame Size", "name": "max-frame-size"}, {"description": "PoE+ classification TLV", "help": "PoE+ classification TLV.", "label": "Power Negotiation", "name": "power-negotiation"}]]  # Transmitted IEEE 802.3 TLVs.
    auto_isl: NotRequired[Literal[{"description": "Disable automatic MCLAG inter chassis link", "help": "Disable automatic MCLAG inter chassis link.", "label": "Disable", "name": "disable"}, {"description": "Enable automatic MCLAG inter chassis link", "help": "Enable automatic MCLAG inter chassis link.", "label": "Enable", "name": "enable"}]]  # Enable/disable auto inter-switch LAG.
    auto_isl_hello_timer: NotRequired[int]  # Auto inter-switch LAG hello timer duration (1 - 30 sec, defa
    auto_isl_receive_timeout: NotRequired[int]  # Auto inter-switch LAG timeout if no response is received (3 
    auto_isl_port_group: NotRequired[int]  # Auto inter-switch LAG port group ID (0 - 9).
    auto_mclag_icl: NotRequired[Literal[{"description": "Disable auto inter-switch-LAG", "help": "Disable auto inter-switch-LAG.", "label": "Disable", "name": "disable"}, {"description": "Enable auto inter-switch-LAG", "help": "Enable auto inter-switch-LAG.", "label": "Enable", "name": "enable"}]]  # Enable/disable MCLAG inter chassis link.
    auto_isl_auth: NotRequired[Literal[{"description": "No auto inter-switch-LAG authentication", "help": "No auto inter-switch-LAG authentication.", "label": "Legacy", "name": "legacy"}, {"description": "Strict auto inter-switch-LAG authentication", "help": "Strict auto inter-switch-LAG authentication.", "label": "Strict", "name": "strict"}, {"description": "Relax auto inter-switch-LAG authentication", "help": "Relax auto inter-switch-LAG authentication.", "label": "Relax", "name": "relax"}]]  # Auto inter-switch LAG authentication mode.
    auto_isl_auth_user: NotRequired[str]  # Auto inter-switch LAG authentication user certificate.
    auto_isl_auth_identity: NotRequired[str]  # Auto inter-switch LAG authentication identity.
    auto_isl_auth_reauth: NotRequired[int]  # Auto inter-switch LAG authentication reauth period in second
    auto_isl_auth_encrypt: NotRequired[Literal[{"description": "No auto inter-switch-LAG encryption", "help": "No auto inter-switch-LAG encryption.", "label": "None", "name": "none"}, {"description": "Mixed auto inter-switch-LAG encryption", "help": "Mixed auto inter-switch-LAG encryption.", "label": "Mixed", "name": "mixed"}, {"description": "Must auto inter-switch-LAG encryption", "help": "Must auto inter-switch-LAG encryption.", "label": "Must", "name": "must"}]]  # Auto inter-switch LAG encryption mode.
    auto_isl_auth_macsec_profile: NotRequired[str]  # Auto inter-switch LAG macsec profile for encryption.
    med_network_policy: NotRequired[list[dict[str, Any]]]  # Configuration method to edit Media Endpoint Discovery (MED) 
    med_location_service: NotRequired[list[dict[str, Any]]]  # Configuration method to edit Media Endpoint Discovery (MED) 
    custom_tlvs: NotRequired[list[dict[str, Any]]]  # Configuration method to edit custom TLV entries.


class LldpProfile:
    """
    Configure FortiSwitch LLDP profiles.
    
    Path: switch_controller/lldp_profile
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
        payload_dict: LldpProfilePayload | None = ...,
        name: str | None = ...,
        med_tlvs: Literal[{"description": "Inventory management TLVs", "help": "Inventory management TLVs.", "label": "Inventory Management", "name": "inventory-management"}, {"description": "Network policy TLVs", "help": "Network policy TLVs.", "label": "Network Policy", "name": "network-policy"}, {"description": "Power manangement TLVs", "help": "Power manangement TLVs.", "label": "Power Management", "name": "power-management"}, {"description": "Location identificaion TLVs", "help": "Location identificaion TLVs.", "label": "Location Identification", "name": "location-identification"}] | None = ...,
        x802_1_tlvs: Literal[{"description": "Port native VLAN TLV", "help": "Port native VLAN TLV.", "label": "Port Vlan Id", "name": "port-vlan-id"}] | None = ...,
        x802_3_tlvs: Literal[{"description": "Maximum frame size TLV", "help": "Maximum frame size TLV.", "label": "Max Frame Size", "name": "max-frame-size"}, {"description": "PoE+ classification TLV", "help": "PoE+ classification TLV.", "label": "Power Negotiation", "name": "power-negotiation"}] | None = ...,
        auto_isl: Literal[{"description": "Disable automatic MCLAG inter chassis link", "help": "Disable automatic MCLAG inter chassis link.", "label": "Disable", "name": "disable"}, {"description": "Enable automatic MCLAG inter chassis link", "help": "Enable automatic MCLAG inter chassis link.", "label": "Enable", "name": "enable"}] | None = ...,
        auto_isl_hello_timer: int | None = ...,
        auto_isl_receive_timeout: int | None = ...,
        auto_isl_port_group: int | None = ...,
        auto_mclag_icl: Literal[{"description": "Disable auto inter-switch-LAG", "help": "Disable auto inter-switch-LAG.", "label": "Disable", "name": "disable"}, {"description": "Enable auto inter-switch-LAG", "help": "Enable auto inter-switch-LAG.", "label": "Enable", "name": "enable"}] | None = ...,
        auto_isl_auth: Literal[{"description": "No auto inter-switch-LAG authentication", "help": "No auto inter-switch-LAG authentication.", "label": "Legacy", "name": "legacy"}, {"description": "Strict auto inter-switch-LAG authentication", "help": "Strict auto inter-switch-LAG authentication.", "label": "Strict", "name": "strict"}, {"description": "Relax auto inter-switch-LAG authentication", "help": "Relax auto inter-switch-LAG authentication.", "label": "Relax", "name": "relax"}] | None = ...,
        auto_isl_auth_user: str | None = ...,
        auto_isl_auth_identity: str | None = ...,
        auto_isl_auth_reauth: int | None = ...,
        auto_isl_auth_encrypt: Literal[{"description": "No auto inter-switch-LAG encryption", "help": "No auto inter-switch-LAG encryption.", "label": "None", "name": "none"}, {"description": "Mixed auto inter-switch-LAG encryption", "help": "Mixed auto inter-switch-LAG encryption.", "label": "Mixed", "name": "mixed"}, {"description": "Must auto inter-switch-LAG encryption", "help": "Must auto inter-switch-LAG encryption.", "label": "Must", "name": "must"}] | None = ...,
        auto_isl_auth_macsec_profile: str | None = ...,
        med_network_policy: list[dict[str, Any]] | None = ...,
        med_location_service: list[dict[str, Any]] | None = ...,
        custom_tlvs: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: LldpProfilePayload | None = ...,
        name: str | None = ...,
        med_tlvs: Literal[{"description": "Inventory management TLVs", "help": "Inventory management TLVs.", "label": "Inventory Management", "name": "inventory-management"}, {"description": "Network policy TLVs", "help": "Network policy TLVs.", "label": "Network Policy", "name": "network-policy"}, {"description": "Power manangement TLVs", "help": "Power manangement TLVs.", "label": "Power Management", "name": "power-management"}, {"description": "Location identificaion TLVs", "help": "Location identificaion TLVs.", "label": "Location Identification", "name": "location-identification"}] | None = ...,
        x802_1_tlvs: Literal[{"description": "Port native VLAN TLV", "help": "Port native VLAN TLV.", "label": "Port Vlan Id", "name": "port-vlan-id"}] | None = ...,
        x802_3_tlvs: Literal[{"description": "Maximum frame size TLV", "help": "Maximum frame size TLV.", "label": "Max Frame Size", "name": "max-frame-size"}, {"description": "PoE+ classification TLV", "help": "PoE+ classification TLV.", "label": "Power Negotiation", "name": "power-negotiation"}] | None = ...,
        auto_isl: Literal[{"description": "Disable automatic MCLAG inter chassis link", "help": "Disable automatic MCLAG inter chassis link.", "label": "Disable", "name": "disable"}, {"description": "Enable automatic MCLAG inter chassis link", "help": "Enable automatic MCLAG inter chassis link.", "label": "Enable", "name": "enable"}] | None = ...,
        auto_isl_hello_timer: int | None = ...,
        auto_isl_receive_timeout: int | None = ...,
        auto_isl_port_group: int | None = ...,
        auto_mclag_icl: Literal[{"description": "Disable auto inter-switch-LAG", "help": "Disable auto inter-switch-LAG.", "label": "Disable", "name": "disable"}, {"description": "Enable auto inter-switch-LAG", "help": "Enable auto inter-switch-LAG.", "label": "Enable", "name": "enable"}] | None = ...,
        auto_isl_auth: Literal[{"description": "No auto inter-switch-LAG authentication", "help": "No auto inter-switch-LAG authentication.", "label": "Legacy", "name": "legacy"}, {"description": "Strict auto inter-switch-LAG authentication", "help": "Strict auto inter-switch-LAG authentication.", "label": "Strict", "name": "strict"}, {"description": "Relax auto inter-switch-LAG authentication", "help": "Relax auto inter-switch-LAG authentication.", "label": "Relax", "name": "relax"}] | None = ...,
        auto_isl_auth_user: str | None = ...,
        auto_isl_auth_identity: str | None = ...,
        auto_isl_auth_reauth: int | None = ...,
        auto_isl_auth_encrypt: Literal[{"description": "No auto inter-switch-LAG encryption", "help": "No auto inter-switch-LAG encryption.", "label": "None", "name": "none"}, {"description": "Mixed auto inter-switch-LAG encryption", "help": "Mixed auto inter-switch-LAG encryption.", "label": "Mixed", "name": "mixed"}, {"description": "Must auto inter-switch-LAG encryption", "help": "Must auto inter-switch-LAG encryption.", "label": "Must", "name": "must"}] | None = ...,
        auto_isl_auth_macsec_profile: str | None = ...,
        med_network_policy: list[dict[str, Any]] | None = ...,
        med_location_service: list[dict[str, Any]] | None = ...,
        custom_tlvs: list[dict[str, Any]] | None = ...,
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
        payload_dict: LldpProfilePayload | None = ...,
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
    "LldpProfile",
    "LldpProfilePayload",
]