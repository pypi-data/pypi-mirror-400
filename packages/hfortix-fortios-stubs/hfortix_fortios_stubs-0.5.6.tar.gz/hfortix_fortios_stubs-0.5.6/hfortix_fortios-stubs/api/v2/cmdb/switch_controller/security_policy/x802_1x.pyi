from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class X8021xPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/security_policy/x802_1x payload fields.
    
    Configure 802.1x MAC Authentication Bypass (MAB) policies.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: auth-fail-vlan-id, authserver-timeout-tagged-vlanid, authserver-timeout-vlanid, +1 more)

    **Usage:**
        payload: X8021xPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Policy name.
    security_mode: NotRequired[Literal[{"help": "802.1X port based authentication.", "label": "802.1X", "name": "802.1X"}, {"help": "802.1X MAC based authentication.", "label": "802.1X Mac Based", "name": "802.1X-mac-based"}]]  # Port or MAC based 802.1X security mode.
    user_group: list[dict[str, Any]]  # Name of user-group to assign to this MAC Authentication Bypa
    mac_auth_bypass: NotRequired[Literal[{"description": "Disable MAB", "help": "Disable MAB.", "label": "Disable", "name": "disable"}, {"description": "Enable MAB", "help": "Enable MAB.", "label": "Enable", "name": "enable"}]]  # Enable/disable MAB for this policy.
    auth_order: NotRequired[Literal[{"description": "Use EAP 1X authentication first then MAB", "help": "Use EAP 1X authentication first then MAB.", "label": "Dot1X Mab", "name": "dot1x-mab"}, {"description": "Use MAB authentication first then EAP 1X", "help": "Use MAB authentication first then EAP 1X.", "label": "Mab Dot1X", "name": "mab-dot1x"}, {"description": "Use MAB authentication only", "help": "Use MAB authentication only.", "label": "Mab", "name": "mab"}]]  # Configure authentication order.
    auth_priority: NotRequired[Literal[{"description": "EAP 1X authentication has a higher priority than MAB with the legacy implementation", "help": "EAP 1X authentication has a higher priority than MAB with the legacy implementation.", "label": "Legacy", "name": "legacy"}, {"description": "EAP 1X authentication has a higher priority than MAB", "help": "EAP 1X authentication has a higher priority than MAB.", "label": "Dot1X Mab", "name": "dot1x-mab"}, {"description": "MAB authentication has a higher priority than EAP 1X", "help": "MAB authentication has a higher priority than EAP 1X.", "label": "Mab Dot1X", "name": "mab-dot1x"}]]  # Configure authentication priority.
    open_auth: NotRequired[Literal[{"description": "Disable open authentication", "help": "Disable open authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable open authentication", "help": "Enable open authentication.", "label": "Enable", "name": "enable"}]]  # Enable/disable open authentication for this policy.
    eap_passthru: NotRequired[Literal[{"description": "Disable EAP pass-through mode on this interface", "help": "Disable EAP pass-through mode on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable EAP pass-through mode on this interface", "help": "Enable EAP pass-through mode on this interface.", "label": "Enable", "name": "enable"}]]  # Enable/disable EAP pass-through mode, allowing protocols (su
    eap_auto_untagged_vlans: NotRequired[Literal[{"description": "Disable automatic inclusion of untagged VLANs", "help": "Disable automatic inclusion of untagged VLANs.", "label": "Disable", "name": "disable"}, {"description": "Enable automatic inclusion of untagged VLANs", "help": "Enable automatic inclusion of untagged VLANs.", "label": "Enable", "name": "enable"}]]  # Enable/disable automatic inclusion of untagged VLANs.
    guest_vlan: NotRequired[Literal[{"description": "Disable guest VLAN on this interface", "help": "Disable guest VLAN on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable guest VLAN on this interface", "help": "Enable guest VLAN on this interface.", "label": "Enable", "name": "enable"}]]  # Enable the guest VLAN feature to allow limited access to non
    guest_vlan_id: str  # Guest VLAN name.
    guest_auth_delay: NotRequired[int]  # Guest authentication delay (1 - 900  sec, default = 30).
    auth_fail_vlan: NotRequired[Literal[{"description": "Disable authentication fail VLAN on this interface", "help": "Disable authentication fail VLAN on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication fail VLAN on this interface", "help": "Enable authentication fail VLAN on this interface.", "label": "Enable", "name": "enable"}]]  # Enable to allow limited access to clients that cannot authen
    auth_fail_vlan_id: str  # VLAN ID on which authentication failed.
    framevid_apply: NotRequired[Literal[{"description": "Disable the capability to apply the EAP/MAB frame VLAN to the port native VLAN", "help": "Disable the capability to apply the EAP/MAB frame VLAN to the port native VLAN.", "label": "Disable", "name": "disable"}, {"description": "Enable the capability to apply the EAP/MAB frame VLAN to the port native VLAN", "help": "Enable the capability to apply the EAP/MAB frame VLAN to the port native VLAN.", "label": "Enable", "name": "enable"}]]  # Enable/disable the capability to apply the EAP/MAB frame VLA
    radius_timeout_overwrite: NotRequired[Literal[{"description": "Override the global RADIUS session timeout", "help": "Override the global RADIUS session timeout.", "label": "Disable", "name": "disable"}, {"description": "Use the global RADIUS session timeout", "help": "Use the global RADIUS session timeout.", "label": "Enable", "name": "enable"}]]  # Enable to override the global RADIUS session timeout.
    policy_type: NotRequired[Literal[{"help": "802.1X security policy.", "label": "802.1X", "name": "802.1X"}]]  # Policy type.
    authserver_timeout_period: NotRequired[int]  # Authentication server timeout period (3 - 15 sec, default = 
    authserver_timeout_vlan: NotRequired[Literal[{"description": "Disable authentication server timeout VLAN on this interface", "help": "Disable authentication server timeout VLAN on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication server timeout VLAN on this interface", "help": "Enable authentication server timeout VLAN on this interface.", "label": "Enable", "name": "enable"}]]  # Enable/disable the authentication server timeout VLAN to all
    authserver_timeout_vlanid: str  # Authentication server timeout VLAN name.
    authserver_timeout_tagged: NotRequired[Literal[{"description": "Disable authentication server timeout on this interface", "help": "Disable authentication server timeout on this interface.", "label": "Disable", "name": "disable"}, {"description": "LLDP voice timeout for the tagged VLAN on this interface", "help": "LLDP voice timeout for the tagged VLAN on this interface.", "label": "Lldp Voice", "name": "lldp-voice"}, {"description": "Static timeout for the tagged VLAN on this interface", "help": "Static timeout for the tagged VLAN on this interface.", "label": "Static", "name": "static"}]]  # Configure timeout option for the tagged VLAN which allows li
    authserver_timeout_tagged_vlanid: str  # Tagged VLAN name for which the timeout option is applied to 
    dacl: NotRequired[Literal[{"description": "Disable dynamic access control list on this interface", "help": "Disable dynamic access control list on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable dynamic access control on this interface", "help": "Enable dynamic access control on this interface.", "label": "Enable", "name": "enable"}]]  # Enable/disable dynamic access control list on this interface


class X8021x:
    """
    Configure 802.1x MAC Authentication Bypass (MAB) policies.
    
    Path: switch_controller/security_policy/x802_1x
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
        payload_dict: X8021xPayload | None = ...,
        name: str | None = ...,
        security_mode: Literal[{"help": "802.1X port based authentication.", "label": "802.1X", "name": "802.1X"}, {"help": "802.1X MAC based authentication.", "label": "802.1X Mac Based", "name": "802.1X-mac-based"}] | None = ...,
        user_group: list[dict[str, Any]] | None = ...,
        mac_auth_bypass: Literal[{"description": "Disable MAB", "help": "Disable MAB.", "label": "Disable", "name": "disable"}, {"description": "Enable MAB", "help": "Enable MAB.", "label": "Enable", "name": "enable"}] | None = ...,
        auth_order: Literal[{"description": "Use EAP 1X authentication first then MAB", "help": "Use EAP 1X authentication first then MAB.", "label": "Dot1X Mab", "name": "dot1x-mab"}, {"description": "Use MAB authentication first then EAP 1X", "help": "Use MAB authentication first then EAP 1X.", "label": "Mab Dot1X", "name": "mab-dot1x"}, {"description": "Use MAB authentication only", "help": "Use MAB authentication only.", "label": "Mab", "name": "mab"}] | None = ...,
        auth_priority: Literal[{"description": "EAP 1X authentication has a higher priority than MAB with the legacy implementation", "help": "EAP 1X authentication has a higher priority than MAB with the legacy implementation.", "label": "Legacy", "name": "legacy"}, {"description": "EAP 1X authentication has a higher priority than MAB", "help": "EAP 1X authentication has a higher priority than MAB.", "label": "Dot1X Mab", "name": "dot1x-mab"}, {"description": "MAB authentication has a higher priority than EAP 1X", "help": "MAB authentication has a higher priority than EAP 1X.", "label": "Mab Dot1X", "name": "mab-dot1x"}] | None = ...,
        open_auth: Literal[{"description": "Disable open authentication", "help": "Disable open authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable open authentication", "help": "Enable open authentication.", "label": "Enable", "name": "enable"}] | None = ...,
        eap_passthru: Literal[{"description": "Disable EAP pass-through mode on this interface", "help": "Disable EAP pass-through mode on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable EAP pass-through mode on this interface", "help": "Enable EAP pass-through mode on this interface.", "label": "Enable", "name": "enable"}] | None = ...,
        eap_auto_untagged_vlans: Literal[{"description": "Disable automatic inclusion of untagged VLANs", "help": "Disable automatic inclusion of untagged VLANs.", "label": "Disable", "name": "disable"}, {"description": "Enable automatic inclusion of untagged VLANs", "help": "Enable automatic inclusion of untagged VLANs.", "label": "Enable", "name": "enable"}] | None = ...,
        guest_vlan: Literal[{"description": "Disable guest VLAN on this interface", "help": "Disable guest VLAN on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable guest VLAN on this interface", "help": "Enable guest VLAN on this interface.", "label": "Enable", "name": "enable"}] | None = ...,
        guest_vlan_id: str | None = ...,
        guest_auth_delay: int | None = ...,
        auth_fail_vlan: Literal[{"description": "Disable authentication fail VLAN on this interface", "help": "Disable authentication fail VLAN on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication fail VLAN on this interface", "help": "Enable authentication fail VLAN on this interface.", "label": "Enable", "name": "enable"}] | None = ...,
        auth_fail_vlan_id: str | None = ...,
        framevid_apply: Literal[{"description": "Disable the capability to apply the EAP/MAB frame VLAN to the port native VLAN", "help": "Disable the capability to apply the EAP/MAB frame VLAN to the port native VLAN.", "label": "Disable", "name": "disable"}, {"description": "Enable the capability to apply the EAP/MAB frame VLAN to the port native VLAN", "help": "Enable the capability to apply the EAP/MAB frame VLAN to the port native VLAN.", "label": "Enable", "name": "enable"}] | None = ...,
        radius_timeout_overwrite: Literal[{"description": "Override the global RADIUS session timeout", "help": "Override the global RADIUS session timeout.", "label": "Disable", "name": "disable"}, {"description": "Use the global RADIUS session timeout", "help": "Use the global RADIUS session timeout.", "label": "Enable", "name": "enable"}] | None = ...,
        policy_type: Literal[{"help": "802.1X security policy.", "label": "802.1X", "name": "802.1X"}] | None = ...,
        authserver_timeout_period: int | None = ...,
        authserver_timeout_vlan: Literal[{"description": "Disable authentication server timeout VLAN on this interface", "help": "Disable authentication server timeout VLAN on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication server timeout VLAN on this interface", "help": "Enable authentication server timeout VLAN on this interface.", "label": "Enable", "name": "enable"}] | None = ...,
        authserver_timeout_vlanid: str | None = ...,
        authserver_timeout_tagged: Literal[{"description": "Disable authentication server timeout on this interface", "help": "Disable authentication server timeout on this interface.", "label": "Disable", "name": "disable"}, {"description": "LLDP voice timeout for the tagged VLAN on this interface", "help": "LLDP voice timeout for the tagged VLAN on this interface.", "label": "Lldp Voice", "name": "lldp-voice"}, {"description": "Static timeout for the tagged VLAN on this interface", "help": "Static timeout for the tagged VLAN on this interface.", "label": "Static", "name": "static"}] | None = ...,
        authserver_timeout_tagged_vlanid: str | None = ...,
        dacl: Literal[{"description": "Disable dynamic access control list on this interface", "help": "Disable dynamic access control list on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable dynamic access control on this interface", "help": "Enable dynamic access control on this interface.", "label": "Enable", "name": "enable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: X8021xPayload | None = ...,
        name: str | None = ...,
        security_mode: Literal[{"help": "802.1X port based authentication.", "label": "802.1X", "name": "802.1X"}, {"help": "802.1X MAC based authentication.", "label": "802.1X Mac Based", "name": "802.1X-mac-based"}] | None = ...,
        user_group: list[dict[str, Any]] | None = ...,
        mac_auth_bypass: Literal[{"description": "Disable MAB", "help": "Disable MAB.", "label": "Disable", "name": "disable"}, {"description": "Enable MAB", "help": "Enable MAB.", "label": "Enable", "name": "enable"}] | None = ...,
        auth_order: Literal[{"description": "Use EAP 1X authentication first then MAB", "help": "Use EAP 1X authentication first then MAB.", "label": "Dot1X Mab", "name": "dot1x-mab"}, {"description": "Use MAB authentication first then EAP 1X", "help": "Use MAB authentication first then EAP 1X.", "label": "Mab Dot1X", "name": "mab-dot1x"}, {"description": "Use MAB authentication only", "help": "Use MAB authentication only.", "label": "Mab", "name": "mab"}] | None = ...,
        auth_priority: Literal[{"description": "EAP 1X authentication has a higher priority than MAB with the legacy implementation", "help": "EAP 1X authentication has a higher priority than MAB with the legacy implementation.", "label": "Legacy", "name": "legacy"}, {"description": "EAP 1X authentication has a higher priority than MAB", "help": "EAP 1X authentication has a higher priority than MAB.", "label": "Dot1X Mab", "name": "dot1x-mab"}, {"description": "MAB authentication has a higher priority than EAP 1X", "help": "MAB authentication has a higher priority than EAP 1X.", "label": "Mab Dot1X", "name": "mab-dot1x"}] | None = ...,
        open_auth: Literal[{"description": "Disable open authentication", "help": "Disable open authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable open authentication", "help": "Enable open authentication.", "label": "Enable", "name": "enable"}] | None = ...,
        eap_passthru: Literal[{"description": "Disable EAP pass-through mode on this interface", "help": "Disable EAP pass-through mode on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable EAP pass-through mode on this interface", "help": "Enable EAP pass-through mode on this interface.", "label": "Enable", "name": "enable"}] | None = ...,
        eap_auto_untagged_vlans: Literal[{"description": "Disable automatic inclusion of untagged VLANs", "help": "Disable automatic inclusion of untagged VLANs.", "label": "Disable", "name": "disable"}, {"description": "Enable automatic inclusion of untagged VLANs", "help": "Enable automatic inclusion of untagged VLANs.", "label": "Enable", "name": "enable"}] | None = ...,
        guest_vlan: Literal[{"description": "Disable guest VLAN on this interface", "help": "Disable guest VLAN on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable guest VLAN on this interface", "help": "Enable guest VLAN on this interface.", "label": "Enable", "name": "enable"}] | None = ...,
        guest_vlan_id: str | None = ...,
        guest_auth_delay: int | None = ...,
        auth_fail_vlan: Literal[{"description": "Disable authentication fail VLAN on this interface", "help": "Disable authentication fail VLAN on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication fail VLAN on this interface", "help": "Enable authentication fail VLAN on this interface.", "label": "Enable", "name": "enable"}] | None = ...,
        auth_fail_vlan_id: str | None = ...,
        framevid_apply: Literal[{"description": "Disable the capability to apply the EAP/MAB frame VLAN to the port native VLAN", "help": "Disable the capability to apply the EAP/MAB frame VLAN to the port native VLAN.", "label": "Disable", "name": "disable"}, {"description": "Enable the capability to apply the EAP/MAB frame VLAN to the port native VLAN", "help": "Enable the capability to apply the EAP/MAB frame VLAN to the port native VLAN.", "label": "Enable", "name": "enable"}] | None = ...,
        radius_timeout_overwrite: Literal[{"description": "Override the global RADIUS session timeout", "help": "Override the global RADIUS session timeout.", "label": "Disable", "name": "disable"}, {"description": "Use the global RADIUS session timeout", "help": "Use the global RADIUS session timeout.", "label": "Enable", "name": "enable"}] | None = ...,
        policy_type: Literal[{"help": "802.1X security policy.", "label": "802.1X", "name": "802.1X"}] | None = ...,
        authserver_timeout_period: int | None = ...,
        authserver_timeout_vlan: Literal[{"description": "Disable authentication server timeout VLAN on this interface", "help": "Disable authentication server timeout VLAN on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication server timeout VLAN on this interface", "help": "Enable authentication server timeout VLAN on this interface.", "label": "Enable", "name": "enable"}] | None = ...,
        authserver_timeout_vlanid: str | None = ...,
        authserver_timeout_tagged: Literal[{"description": "Disable authentication server timeout on this interface", "help": "Disable authentication server timeout on this interface.", "label": "Disable", "name": "disable"}, {"description": "LLDP voice timeout for the tagged VLAN on this interface", "help": "LLDP voice timeout for the tagged VLAN on this interface.", "label": "Lldp Voice", "name": "lldp-voice"}, {"description": "Static timeout for the tagged VLAN on this interface", "help": "Static timeout for the tagged VLAN on this interface.", "label": "Static", "name": "static"}] | None = ...,
        authserver_timeout_tagged_vlanid: str | None = ...,
        dacl: Literal[{"description": "Disable dynamic access control list on this interface", "help": "Disable dynamic access control list on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable dynamic access control on this interface", "help": "Enable dynamic access control on this interface.", "label": "Enable", "name": "enable"}] | None = ...,
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
        payload_dict: X8021xPayload | None = ...,
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
    "X8021x",
    "X8021xPayload",
]