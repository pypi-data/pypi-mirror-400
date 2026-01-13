from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class VdomExceptionPayload(TypedDict, total=False):
    """
    Type hints for system/vdom_exception payload fields.
    
    Global configuration objects that can be configured independently across different ha peers for all VDOMs or for the defined VDOM scope.
    
    **Usage:**
        payload: VdomExceptionPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    id: NotRequired[int]  # Index (1 - 4096).
    object: Literal[{"help": "log.fortianalyzer.setting", "label": "Log.Fortianalyzer.Setting", "name": "log.fortianalyzer.setting"}, {"help": "log.fortianalyzer.override-setting", "label": "Log.Fortianalyzer.Override Setting", "name": "log.fortianalyzer.override-setting"}, {"help": "log.fortianalyzer2.setting", "label": "Log.Fortianalyzer2.Setting", "name": "log.fortianalyzer2.setting"}, {"help": "log.fortianalyzer2.override-setting", "label": "Log.Fortianalyzer2.Override Setting", "name": "log.fortianalyzer2.override-setting"}, {"help": "log.fortianalyzer3.setting", "label": "Log.Fortianalyzer3.Setting", "name": "log.fortianalyzer3.setting"}, {"help": "log.fortianalyzer3.override-setting", "label": "Log.Fortianalyzer3.Override Setting", "name": "log.fortianalyzer3.override-setting"}, {"help": "log.fortianalyzer-cloud.setting", "label": "Log.Fortianalyzer Cloud.Setting", "name": "log.fortianalyzer-cloud.setting"}, {"help": "log.fortianalyzer-cloud.override-setting", "label": "Log.Fortianalyzer Cloud.Override Setting", "name": "log.fortianalyzer-cloud.override-setting"}, {"help": "log.syslogd.setting", "label": "Log.Syslogd.Setting", "name": "log.syslogd.setting"}, {"help": "log.syslogd.override-setting", "label": "Log.Syslogd.Override Setting", "name": "log.syslogd.override-setting"}, {"help": "log.syslogd2.setting", "label": "Log.Syslogd2.Setting", "name": "log.syslogd2.setting"}, {"help": "log.syslogd2.override-setting", "label": "Log.Syslogd2.Override Setting", "name": "log.syslogd2.override-setting"}, {"help": "log.syslogd3.setting", "label": "Log.Syslogd3.Setting", "name": "log.syslogd3.setting"}, {"help": "log.syslogd3.override-setting", "label": "Log.Syslogd3.Override Setting", "name": "log.syslogd3.override-setting"}, {"help": "log.syslogd4.setting", "label": "Log.Syslogd4.Setting", "name": "log.syslogd4.setting"}, {"help": "log.syslogd4.override-setting", "label": "Log.Syslogd4.Override Setting", "name": "log.syslogd4.override-setting"}, {"help": "system.gre-tunnel", "label": "System.Gre Tunnel", "name": "system.gre-tunnel"}, {"help": "system.central-management", "label": "System.Central Management", "name": "system.central-management"}, {"help": "system.csf", "label": "System.Csf", "name": "system.csf"}, {"help": "user.radius", "label": "User.Radius", "name": "user.radius"}, {"help": "system.interface", "label": "System.Interface", "name": "system.interface"}, {"help": "vpn.ipsec.phase1-interface", "label": "Vpn.Ipsec.Phase1 Interface", "name": "vpn.ipsec.phase1-interface"}, {"help": "vpn.ipsec.phase2-interface", "label": "Vpn.Ipsec.Phase2 Interface", "name": "vpn.ipsec.phase2-interface"}, {"help": "router.bgp", "label": "Router.Bgp", "name": "router.bgp"}, {"help": "router.route-map", "label": "Router.Route Map", "name": "router.route-map"}, {"help": "router.prefix-list", "label": "Router.Prefix List", "name": "router.prefix-list"}, {"help": "firewall.ippool", "label": "Firewall.Ippool", "name": "firewall.ippool"}, {"help": "firewall.ippool6", "label": "Firewall.Ippool6", "name": "firewall.ippool6"}, {"help": "router.static", "label": "Router.Static", "name": "router.static"}, {"help": "router.static6", "label": "Router.Static6", "name": "router.static6"}, {"help": "firewall.vip", "label": "Firewall.Vip", "name": "firewall.vip"}, {"help": "firewall.vip6", "label": "Firewall.Vip6", "name": "firewall.vip6"}, {"help": "system.sdwan", "label": "System.Sdwan", "name": "system.sdwan"}, {"help": "system.saml", "label": "System.Saml", "name": "system.saml"}, {"help": "router.policy", "label": "Router.Policy", "name": "router.policy"}, {"help": "router.policy6", "label": "Router.Policy6", "name": "router.policy6"}, {"help": "log.syslogd.setting", "label": "Log.Syslogd.Setting", "name": "log.syslogd.setting"}, {"help": "log.syslogd.override-setting", "label": "Log.Syslogd.Override Setting", "name": "log.syslogd.override-setting"}, {"help": "firewall.address", "label": "Firewall.Address", "name": "firewall.address"}]  # Name of the configuration object that can be configured inde
    scope: NotRequired[Literal[{"description": "Object configuration independent for all VDOMs", "help": "Object configuration independent for all VDOMs.", "label": "All", "name": "all"}, {"description": "Object configuration independent for the listed VDOMs", "help": "Object configuration independent for the listed VDOMs. Other VDOMs use the global configuration.", "label": "Inclusive", "name": "inclusive"}, {"description": "Use the global object configuration for the listed VDOMs", "help": "Use the global object configuration for the listed VDOMs. Other VDOMs can be configured independently.", "label": "Exclusive", "name": "exclusive"}]]  # Determine whether the configuration object can be configured
    vdom: NotRequired[list[dict[str, Any]]]  # Names of the VDOMs.


class VdomException:
    """
    Global configuration objects that can be configured independently across different ha peers for all VDOMs or for the defined VDOM scope.
    
    Path: system/vdom_exception
    Category: cmdb
    Primary Key: id
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        id: int | None = ...,
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
        id: int,
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
        id: int | None = ...,
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
        id: int | None = ...,
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
        id: int | None = ...,
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
        payload_dict: VdomExceptionPayload | None = ...,
        id: int | None = ...,
        object: Literal[{"help": "log.fortianalyzer.setting", "label": "Log.Fortianalyzer.Setting", "name": "log.fortianalyzer.setting"}, {"help": "log.fortianalyzer.override-setting", "label": "Log.Fortianalyzer.Override Setting", "name": "log.fortianalyzer.override-setting"}, {"help": "log.fortianalyzer2.setting", "label": "Log.Fortianalyzer2.Setting", "name": "log.fortianalyzer2.setting"}, {"help": "log.fortianalyzer2.override-setting", "label": "Log.Fortianalyzer2.Override Setting", "name": "log.fortianalyzer2.override-setting"}, {"help": "log.fortianalyzer3.setting", "label": "Log.Fortianalyzer3.Setting", "name": "log.fortianalyzer3.setting"}, {"help": "log.fortianalyzer3.override-setting", "label": "Log.Fortianalyzer3.Override Setting", "name": "log.fortianalyzer3.override-setting"}, {"help": "log.fortianalyzer-cloud.setting", "label": "Log.Fortianalyzer Cloud.Setting", "name": "log.fortianalyzer-cloud.setting"}, {"help": "log.fortianalyzer-cloud.override-setting", "label": "Log.Fortianalyzer Cloud.Override Setting", "name": "log.fortianalyzer-cloud.override-setting"}, {"help": "log.syslogd.setting", "label": "Log.Syslogd.Setting", "name": "log.syslogd.setting"}, {"help": "log.syslogd.override-setting", "label": "Log.Syslogd.Override Setting", "name": "log.syslogd.override-setting"}, {"help": "log.syslogd2.setting", "label": "Log.Syslogd2.Setting", "name": "log.syslogd2.setting"}, {"help": "log.syslogd2.override-setting", "label": "Log.Syslogd2.Override Setting", "name": "log.syslogd2.override-setting"}, {"help": "log.syslogd3.setting", "label": "Log.Syslogd3.Setting", "name": "log.syslogd3.setting"}, {"help": "log.syslogd3.override-setting", "label": "Log.Syslogd3.Override Setting", "name": "log.syslogd3.override-setting"}, {"help": "log.syslogd4.setting", "label": "Log.Syslogd4.Setting", "name": "log.syslogd4.setting"}, {"help": "log.syslogd4.override-setting", "label": "Log.Syslogd4.Override Setting", "name": "log.syslogd4.override-setting"}, {"help": "system.gre-tunnel", "label": "System.Gre Tunnel", "name": "system.gre-tunnel"}, {"help": "system.central-management", "label": "System.Central Management", "name": "system.central-management"}, {"help": "system.csf", "label": "System.Csf", "name": "system.csf"}, {"help": "user.radius", "label": "User.Radius", "name": "user.radius"}, {"help": "system.interface", "label": "System.Interface", "name": "system.interface"}, {"help": "vpn.ipsec.phase1-interface", "label": "Vpn.Ipsec.Phase1 Interface", "name": "vpn.ipsec.phase1-interface"}, {"help": "vpn.ipsec.phase2-interface", "label": "Vpn.Ipsec.Phase2 Interface", "name": "vpn.ipsec.phase2-interface"}, {"help": "router.bgp", "label": "Router.Bgp", "name": "router.bgp"}, {"help": "router.route-map", "label": "Router.Route Map", "name": "router.route-map"}, {"help": "router.prefix-list", "label": "Router.Prefix List", "name": "router.prefix-list"}, {"help": "firewall.ippool", "label": "Firewall.Ippool", "name": "firewall.ippool"}, {"help": "firewall.ippool6", "label": "Firewall.Ippool6", "name": "firewall.ippool6"}, {"help": "router.static", "label": "Router.Static", "name": "router.static"}, {"help": "router.static6", "label": "Router.Static6", "name": "router.static6"}, {"help": "firewall.vip", "label": "Firewall.Vip", "name": "firewall.vip"}, {"help": "firewall.vip6", "label": "Firewall.Vip6", "name": "firewall.vip6"}, {"help": "system.sdwan", "label": "System.Sdwan", "name": "system.sdwan"}, {"help": "system.saml", "label": "System.Saml", "name": "system.saml"}, {"help": "router.policy", "label": "Router.Policy", "name": "router.policy"}, {"help": "router.policy6", "label": "Router.Policy6", "name": "router.policy6"}, {"help": "log.syslogd.setting", "label": "Log.Syslogd.Setting", "name": "log.syslogd.setting"}, {"help": "log.syslogd.override-setting", "label": "Log.Syslogd.Override Setting", "name": "log.syslogd.override-setting"}, {"help": "firewall.address", "label": "Firewall.Address", "name": "firewall.address"}] | None = ...,
        scope: Literal[{"description": "Object configuration independent for all VDOMs", "help": "Object configuration independent for all VDOMs.", "label": "All", "name": "all"}, {"description": "Object configuration independent for the listed VDOMs", "help": "Object configuration independent for the listed VDOMs. Other VDOMs use the global configuration.", "label": "Inclusive", "name": "inclusive"}, {"description": "Use the global object configuration for the listed VDOMs", "help": "Use the global object configuration for the listed VDOMs. Other VDOMs can be configured independently.", "label": "Exclusive", "name": "exclusive"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: VdomExceptionPayload | None = ...,
        id: int | None = ...,
        object: Literal[{"help": "log.fortianalyzer.setting", "label": "Log.Fortianalyzer.Setting", "name": "log.fortianalyzer.setting"}, {"help": "log.fortianalyzer.override-setting", "label": "Log.Fortianalyzer.Override Setting", "name": "log.fortianalyzer.override-setting"}, {"help": "log.fortianalyzer2.setting", "label": "Log.Fortianalyzer2.Setting", "name": "log.fortianalyzer2.setting"}, {"help": "log.fortianalyzer2.override-setting", "label": "Log.Fortianalyzer2.Override Setting", "name": "log.fortianalyzer2.override-setting"}, {"help": "log.fortianalyzer3.setting", "label": "Log.Fortianalyzer3.Setting", "name": "log.fortianalyzer3.setting"}, {"help": "log.fortianalyzer3.override-setting", "label": "Log.Fortianalyzer3.Override Setting", "name": "log.fortianalyzer3.override-setting"}, {"help": "log.fortianalyzer-cloud.setting", "label": "Log.Fortianalyzer Cloud.Setting", "name": "log.fortianalyzer-cloud.setting"}, {"help": "log.fortianalyzer-cloud.override-setting", "label": "Log.Fortianalyzer Cloud.Override Setting", "name": "log.fortianalyzer-cloud.override-setting"}, {"help": "log.syslogd.setting", "label": "Log.Syslogd.Setting", "name": "log.syslogd.setting"}, {"help": "log.syslogd.override-setting", "label": "Log.Syslogd.Override Setting", "name": "log.syslogd.override-setting"}, {"help": "log.syslogd2.setting", "label": "Log.Syslogd2.Setting", "name": "log.syslogd2.setting"}, {"help": "log.syslogd2.override-setting", "label": "Log.Syslogd2.Override Setting", "name": "log.syslogd2.override-setting"}, {"help": "log.syslogd3.setting", "label": "Log.Syslogd3.Setting", "name": "log.syslogd3.setting"}, {"help": "log.syslogd3.override-setting", "label": "Log.Syslogd3.Override Setting", "name": "log.syslogd3.override-setting"}, {"help": "log.syslogd4.setting", "label": "Log.Syslogd4.Setting", "name": "log.syslogd4.setting"}, {"help": "log.syslogd4.override-setting", "label": "Log.Syslogd4.Override Setting", "name": "log.syslogd4.override-setting"}, {"help": "system.gre-tunnel", "label": "System.Gre Tunnel", "name": "system.gre-tunnel"}, {"help": "system.central-management", "label": "System.Central Management", "name": "system.central-management"}, {"help": "system.csf", "label": "System.Csf", "name": "system.csf"}, {"help": "user.radius", "label": "User.Radius", "name": "user.radius"}, {"help": "system.interface", "label": "System.Interface", "name": "system.interface"}, {"help": "vpn.ipsec.phase1-interface", "label": "Vpn.Ipsec.Phase1 Interface", "name": "vpn.ipsec.phase1-interface"}, {"help": "vpn.ipsec.phase2-interface", "label": "Vpn.Ipsec.Phase2 Interface", "name": "vpn.ipsec.phase2-interface"}, {"help": "router.bgp", "label": "Router.Bgp", "name": "router.bgp"}, {"help": "router.route-map", "label": "Router.Route Map", "name": "router.route-map"}, {"help": "router.prefix-list", "label": "Router.Prefix List", "name": "router.prefix-list"}, {"help": "firewall.ippool", "label": "Firewall.Ippool", "name": "firewall.ippool"}, {"help": "firewall.ippool6", "label": "Firewall.Ippool6", "name": "firewall.ippool6"}, {"help": "router.static", "label": "Router.Static", "name": "router.static"}, {"help": "router.static6", "label": "Router.Static6", "name": "router.static6"}, {"help": "firewall.vip", "label": "Firewall.Vip", "name": "firewall.vip"}, {"help": "firewall.vip6", "label": "Firewall.Vip6", "name": "firewall.vip6"}, {"help": "system.sdwan", "label": "System.Sdwan", "name": "system.sdwan"}, {"help": "system.saml", "label": "System.Saml", "name": "system.saml"}, {"help": "router.policy", "label": "Router.Policy", "name": "router.policy"}, {"help": "router.policy6", "label": "Router.Policy6", "name": "router.policy6"}, {"help": "log.syslogd.setting", "label": "Log.Syslogd.Setting", "name": "log.syslogd.setting"}, {"help": "log.syslogd.override-setting", "label": "Log.Syslogd.Override Setting", "name": "log.syslogd.override-setting"}, {"help": "firewall.address", "label": "Firewall.Address", "name": "firewall.address"}] | None = ...,
        scope: Literal[{"description": "Object configuration independent for all VDOMs", "help": "Object configuration independent for all VDOMs.", "label": "All", "name": "all"}, {"description": "Object configuration independent for the listed VDOMs", "help": "Object configuration independent for the listed VDOMs. Other VDOMs use the global configuration.", "label": "Inclusive", "name": "inclusive"}, {"description": "Use the global object configuration for the listed VDOMs", "help": "Use the global object configuration for the listed VDOMs. Other VDOMs can be configured independently.", "label": "Exclusive", "name": "exclusive"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        id: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        id: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: VdomExceptionPayload | None = ...,
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
    "VdomException",
    "VdomExceptionPayload",
]