from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ExtenderProfilePayload(TypedDict, total=False):
    """
    Type hints for extension_controller/extender_profile payload fields.
    
    FortiExtender extender profile configuration.
    
    **Usage:**
        payload: ExtenderProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # FortiExtender profile name.
    id: NotRequired[int]  # ID.
    model: Literal[{"description": "FEX-201E model", "help": "FEX-201E model.", "label": "Fx201E", "name": "FX201E"}, {"description": "FEX-211E model", "help": "FEX-211E model.", "label": "Fx211E", "name": "FX211E"}, {"description": "FEX-200F model", "help": "FEX-200F model.", "label": "Fx200F", "name": "FX200F"}, {"description": "FEX-101F-AM model", "help": "FEX-101F-AM model.", "label": "Fxa11F", "name": "FXA11F"}, {"description": "FEX-101F-EA model", "help": "FEX-101F-EA model.", "label": "Fxe11F", "name": "FXE11F"}, {"description": "FEX-201F-AM model", "help": "FEX-201F-AM model.", "label": "Fxa21F", "name": "FXA21F"}, {"description": "FEX-201F-EA model", "help": "FEX-201F-EA model.", "label": "Fxe21F", "name": "FXE21F"}, {"description": "FEX-202F-AM model", "help": "FEX-202F-AM model.", "label": "Fxa22F", "name": "FXA22F"}, {"description": "FEX-202F-EA model", "help": "FEX-202F-EA model.", "label": "Fxe22F", "name": "FXE22F"}, {"description": "FEX-212F model", "help": "FEX-212F model.", "label": "Fx212F", "name": "FX212F"}, {"description": "FEX-311F model", "help": "FEX-311F model.", "label": "Fx311F", "name": "FX311F"}, {"description": "FEX-312F model", "help": "FEX-312F model.", "label": "Fx312F", "name": "FX312F"}, {"description": "FEX-511F model", "help": "FEX-511F model.", "label": "Fx511F", "name": "FX511F"}, {"description": "FER-511G model", "help": "FER-511G model.", "label": "Fxr51G", "name": "FXR51G"}, {"description": "FEX-511G model", "help": "FEX-511G model.", "label": "Fxn51G", "name": "FXN51G"}, {"description": "FEX-511G-Wifi model", "help": "FEX-511G-Wifi model.", "label": "Fxw51G", "name": "FXW51G"}, {"description": "FEV-211F model", "help": "FEV-211F model.", "label": "Fvg21F", "name": "FVG21F"}, {"description": "FEV-211F-AM model", "help": "FEV-211F-AM model.", "label": "Fva21F", "name": "FVA21F"}, {"description": "FEV-212F model", "help": "FEV-212F model.", "label": "Fvg22F", "name": "FVG22F"}, {"description": "FEV-212F-AM model", "help": "FEV-212F-AM model.", "label": "Fva22F", "name": "FVA22F"}, {"description": "FX40D-AMEU model", "help": "FX40D-AMEU model.", "label": "Fx04Da", "name": "FX04DA"}, {"description": "FG-CONNECTOR model", "help": "FG-CONNECTOR model.", "label": "Fg", "name": "FG"}, {"description": "FBS-10FW model", "help": "FBS-10FW model.", "label": "Bs10Fw", "name": "BS10FW"}, {"description": "FBS-20GW model", "help": "FBS-20GW model.", "label": "Bs20Gw", "name": "BS20GW"}, {"description": "FBS-20G model", "help": "FBS-20G model.", "label": "Bs20Gn", "name": "BS20GN"}, {"description": "FEV-511G model", "help": "FEV-511G model.", "label": "Fvg51G", "name": "FVG51G"}, {"description": "FEX-101G model", "help": "FEX-101G model.", "label": "Fxe11G", "name": "FXE11G"}, {"description": "FEX-211G model", "help": "FEX-211G model.", "label": "Fx211G", "name": "FX211G"}]  # Model.
    extension: Literal[{"description": "WAN extension", "help": "WAN extension.", "label": "Wan Extension", "name": "wan-extension"}, {"description": "LAN extension", "help": "LAN extension.", "label": "Lan Extension", "name": "lan-extension"}]  # Extension option.
    allowaccess: NotRequired[Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}]]  # Control management access to the managed extender. Separate 
    login_password_change: NotRequired[Literal[{"description": "Change the managed extender\u0027s administrator password", "help": "Change the managed extender\u0027s administrator password. Use the login-password option to set the password.", "label": "Yes", "name": "yes"}, {"description": "Keep the managed extender\u0027s administrator password set to the factory default", "help": "Keep the managed extender\u0027s administrator password set to the factory default.", "label": "Default", "name": "default"}, {"description": "Do not change the managed extender\u0027s administrator password", "help": "Do not change the managed extender\u0027s administrator password.", "label": "No", "name": "no"}]]  # Change or reset the administrator password of a managed exte
    login_password: str  # Set the managed extender's administrator password.
    enforce_bandwidth: NotRequired[Literal[{"description": "Enable to enforce bandwidth limit on LAN extension interface", "help": "Enable to enforce bandwidth limit on LAN extension interface.", "label": "Enable", "name": "enable"}, {"description": "Disable to enforce bandwidth limit on LAN extension interface", "help": "Disable to enforce bandwidth limit on LAN extension interface.", "label": "Disable", "name": "disable"}]]  # Enable/disable enforcement of bandwidth on LAN extension int
    bandwidth_limit: int  # FortiExtender LAN extension bandwidth limit (Mbps).
    cellular: str  # FortiExtender cellular configuration.
    wifi: NotRequired[str]  # FortiExtender Wi-Fi configuration.
    lan_extension: str  # FortiExtender LAN extension configuration.


class ExtenderProfile:
    """
    FortiExtender extender profile configuration.
    
    Path: extension_controller/extender_profile
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
        payload_dict: ExtenderProfilePayload | None = ...,
        name: str | None = ...,
        id: int | None = ...,
        model: Literal[{"description": "FEX-201E model", "help": "FEX-201E model.", "label": "Fx201E", "name": "FX201E"}, {"description": "FEX-211E model", "help": "FEX-211E model.", "label": "Fx211E", "name": "FX211E"}, {"description": "FEX-200F model", "help": "FEX-200F model.", "label": "Fx200F", "name": "FX200F"}, {"description": "FEX-101F-AM model", "help": "FEX-101F-AM model.", "label": "Fxa11F", "name": "FXA11F"}, {"description": "FEX-101F-EA model", "help": "FEX-101F-EA model.", "label": "Fxe11F", "name": "FXE11F"}, {"description": "FEX-201F-AM model", "help": "FEX-201F-AM model.", "label": "Fxa21F", "name": "FXA21F"}, {"description": "FEX-201F-EA model", "help": "FEX-201F-EA model.", "label": "Fxe21F", "name": "FXE21F"}, {"description": "FEX-202F-AM model", "help": "FEX-202F-AM model.", "label": "Fxa22F", "name": "FXA22F"}, {"description": "FEX-202F-EA model", "help": "FEX-202F-EA model.", "label": "Fxe22F", "name": "FXE22F"}, {"description": "FEX-212F model", "help": "FEX-212F model.", "label": "Fx212F", "name": "FX212F"}, {"description": "FEX-311F model", "help": "FEX-311F model.", "label": "Fx311F", "name": "FX311F"}, {"description": "FEX-312F model", "help": "FEX-312F model.", "label": "Fx312F", "name": "FX312F"}, {"description": "FEX-511F model", "help": "FEX-511F model.", "label": "Fx511F", "name": "FX511F"}, {"description": "FER-511G model", "help": "FER-511G model.", "label": "Fxr51G", "name": "FXR51G"}, {"description": "FEX-511G model", "help": "FEX-511G model.", "label": "Fxn51G", "name": "FXN51G"}, {"description": "FEX-511G-Wifi model", "help": "FEX-511G-Wifi model.", "label": "Fxw51G", "name": "FXW51G"}, {"description": "FEV-211F model", "help": "FEV-211F model.", "label": "Fvg21F", "name": "FVG21F"}, {"description": "FEV-211F-AM model", "help": "FEV-211F-AM model.", "label": "Fva21F", "name": "FVA21F"}, {"description": "FEV-212F model", "help": "FEV-212F model.", "label": "Fvg22F", "name": "FVG22F"}, {"description": "FEV-212F-AM model", "help": "FEV-212F-AM model.", "label": "Fva22F", "name": "FVA22F"}, {"description": "FX40D-AMEU model", "help": "FX40D-AMEU model.", "label": "Fx04Da", "name": "FX04DA"}, {"description": "FG-CONNECTOR model", "help": "FG-CONNECTOR model.", "label": "Fg", "name": "FG"}, {"description": "FBS-10FW model", "help": "FBS-10FW model.", "label": "Bs10Fw", "name": "BS10FW"}, {"description": "FBS-20GW model", "help": "FBS-20GW model.", "label": "Bs20Gw", "name": "BS20GW"}, {"description": "FBS-20G model", "help": "FBS-20G model.", "label": "Bs20Gn", "name": "BS20GN"}, {"description": "FEV-511G model", "help": "FEV-511G model.", "label": "Fvg51G", "name": "FVG51G"}, {"description": "FEX-101G model", "help": "FEX-101G model.", "label": "Fxe11G", "name": "FXE11G"}, {"description": "FEX-211G model", "help": "FEX-211G model.", "label": "Fx211G", "name": "FX211G"}] | None = ...,
        extension: Literal[{"description": "WAN extension", "help": "WAN extension.", "label": "Wan Extension", "name": "wan-extension"}, {"description": "LAN extension", "help": "LAN extension.", "label": "Lan Extension", "name": "lan-extension"}] | None = ...,
        allowaccess: Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}] | None = ...,
        login_password_change: Literal[{"description": "Change the managed extender\u0027s administrator password", "help": "Change the managed extender\u0027s administrator password. Use the login-password option to set the password.", "label": "Yes", "name": "yes"}, {"description": "Keep the managed extender\u0027s administrator password set to the factory default", "help": "Keep the managed extender\u0027s administrator password set to the factory default.", "label": "Default", "name": "default"}, {"description": "Do not change the managed extender\u0027s administrator password", "help": "Do not change the managed extender\u0027s administrator password.", "label": "No", "name": "no"}] | None = ...,
        login_password: str | None = ...,
        enforce_bandwidth: Literal[{"description": "Enable to enforce bandwidth limit on LAN extension interface", "help": "Enable to enforce bandwidth limit on LAN extension interface.", "label": "Enable", "name": "enable"}, {"description": "Disable to enforce bandwidth limit on LAN extension interface", "help": "Disable to enforce bandwidth limit on LAN extension interface.", "label": "Disable", "name": "disable"}] | None = ...,
        bandwidth_limit: int | None = ...,
        cellular: str | None = ...,
        wifi: str | None = ...,
        lan_extension: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ExtenderProfilePayload | None = ...,
        name: str | None = ...,
        id: int | None = ...,
        model: Literal[{"description": "FEX-201E model", "help": "FEX-201E model.", "label": "Fx201E", "name": "FX201E"}, {"description": "FEX-211E model", "help": "FEX-211E model.", "label": "Fx211E", "name": "FX211E"}, {"description": "FEX-200F model", "help": "FEX-200F model.", "label": "Fx200F", "name": "FX200F"}, {"description": "FEX-101F-AM model", "help": "FEX-101F-AM model.", "label": "Fxa11F", "name": "FXA11F"}, {"description": "FEX-101F-EA model", "help": "FEX-101F-EA model.", "label": "Fxe11F", "name": "FXE11F"}, {"description": "FEX-201F-AM model", "help": "FEX-201F-AM model.", "label": "Fxa21F", "name": "FXA21F"}, {"description": "FEX-201F-EA model", "help": "FEX-201F-EA model.", "label": "Fxe21F", "name": "FXE21F"}, {"description": "FEX-202F-AM model", "help": "FEX-202F-AM model.", "label": "Fxa22F", "name": "FXA22F"}, {"description": "FEX-202F-EA model", "help": "FEX-202F-EA model.", "label": "Fxe22F", "name": "FXE22F"}, {"description": "FEX-212F model", "help": "FEX-212F model.", "label": "Fx212F", "name": "FX212F"}, {"description": "FEX-311F model", "help": "FEX-311F model.", "label": "Fx311F", "name": "FX311F"}, {"description": "FEX-312F model", "help": "FEX-312F model.", "label": "Fx312F", "name": "FX312F"}, {"description": "FEX-511F model", "help": "FEX-511F model.", "label": "Fx511F", "name": "FX511F"}, {"description": "FER-511G model", "help": "FER-511G model.", "label": "Fxr51G", "name": "FXR51G"}, {"description": "FEX-511G model", "help": "FEX-511G model.", "label": "Fxn51G", "name": "FXN51G"}, {"description": "FEX-511G-Wifi model", "help": "FEX-511G-Wifi model.", "label": "Fxw51G", "name": "FXW51G"}, {"description": "FEV-211F model", "help": "FEV-211F model.", "label": "Fvg21F", "name": "FVG21F"}, {"description": "FEV-211F-AM model", "help": "FEV-211F-AM model.", "label": "Fva21F", "name": "FVA21F"}, {"description": "FEV-212F model", "help": "FEV-212F model.", "label": "Fvg22F", "name": "FVG22F"}, {"description": "FEV-212F-AM model", "help": "FEV-212F-AM model.", "label": "Fva22F", "name": "FVA22F"}, {"description": "FX40D-AMEU model", "help": "FX40D-AMEU model.", "label": "Fx04Da", "name": "FX04DA"}, {"description": "FG-CONNECTOR model", "help": "FG-CONNECTOR model.", "label": "Fg", "name": "FG"}, {"description": "FBS-10FW model", "help": "FBS-10FW model.", "label": "Bs10Fw", "name": "BS10FW"}, {"description": "FBS-20GW model", "help": "FBS-20GW model.", "label": "Bs20Gw", "name": "BS20GW"}, {"description": "FBS-20G model", "help": "FBS-20G model.", "label": "Bs20Gn", "name": "BS20GN"}, {"description": "FEV-511G model", "help": "FEV-511G model.", "label": "Fvg51G", "name": "FVG51G"}, {"description": "FEX-101G model", "help": "FEX-101G model.", "label": "Fxe11G", "name": "FXE11G"}, {"description": "FEX-211G model", "help": "FEX-211G model.", "label": "Fx211G", "name": "FX211G"}] | None = ...,
        extension: Literal[{"description": "WAN extension", "help": "WAN extension.", "label": "Wan Extension", "name": "wan-extension"}, {"description": "LAN extension", "help": "LAN extension.", "label": "Lan Extension", "name": "lan-extension"}] | None = ...,
        allowaccess: Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}] | None = ...,
        login_password_change: Literal[{"description": "Change the managed extender\u0027s administrator password", "help": "Change the managed extender\u0027s administrator password. Use the login-password option to set the password.", "label": "Yes", "name": "yes"}, {"description": "Keep the managed extender\u0027s administrator password set to the factory default", "help": "Keep the managed extender\u0027s administrator password set to the factory default.", "label": "Default", "name": "default"}, {"description": "Do not change the managed extender\u0027s administrator password", "help": "Do not change the managed extender\u0027s administrator password.", "label": "No", "name": "no"}] | None = ...,
        login_password: str | None = ...,
        enforce_bandwidth: Literal[{"description": "Enable to enforce bandwidth limit on LAN extension interface", "help": "Enable to enforce bandwidth limit on LAN extension interface.", "label": "Enable", "name": "enable"}, {"description": "Disable to enforce bandwidth limit on LAN extension interface", "help": "Disable to enforce bandwidth limit on LAN extension interface.", "label": "Disable", "name": "disable"}] | None = ...,
        bandwidth_limit: int | None = ...,
        cellular: str | None = ...,
        wifi: str | None = ...,
        lan_extension: str | None = ...,
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
        payload_dict: ExtenderProfilePayload | None = ...,
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
    "ExtenderProfile",
    "ExtenderProfilePayload",
]