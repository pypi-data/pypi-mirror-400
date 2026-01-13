from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ExtenderVapPayload(TypedDict, total=False):
    """
    Type hints for extension_controller/extender_vap payload fields.
    
    FortiExtender wifi vap configuration.
    
    **Usage:**
        payload: ExtenderVapPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Wi-Fi VAP name.
    type: Literal[{"description": "Local VAP", "help": "Local VAP.", "label": "Local Vap", "name": "local-vap"}, {"description": "Lan Extension VAP", "help": "Lan Extension VAP.", "label": "Lan Ext Vap", "name": "lan-ext-vap"}]  # Wi-Fi VAP type local-vap / lan-extension-vap.
    ssid: str  # Wi-Fi SSID.
    max_clients: NotRequired[int]  # Wi-Fi max clients (0 - 512), default = 0 (no limit) 
    broadcast_ssid: NotRequired[Literal[{"description": "Disable broadcast SSID", "help": "Disable broadcast SSID.", "label": "Disable", "name": "disable"}, {"description": "Enable broadcast SSID", "help": "Enable broadcast SSID.", "label": "Enable", "name": "enable"}]]  # Wi-Fi broadcast SSID enable / disable.
    security: Literal[{"description": "Wi-Fi security OPEN    WPA2-Personal:Wi-Fi security WPA2 Personal    WPA-WPA2-Personal:Wi-Fi security WPA-WPA2 Personal    WPA3-SAE:Wi-Fi security WPA3 SAE    WPA3-SAE-Transition:Wi-Fi security WPA3 SAE Transition    WPA2-Enterprise:Wi-Fi security WPA2 Enterprise    WPA3-Enterprise-only:Wi-Fi security WPA3 Enterprise only    WPA3-Enterprise-transition:Wi-Fi security WPA3 Enterprise Transition    WPA3-Enterprise-192-bit:Wi-Fi security WPA3 Enterprise 192-bit", "help": "Wi-Fi security OPEN", "label": "Open", "name": "OPEN"}, {"help": "Wi-Fi security WPA2 Personal", "label": "Wpa2 Personal", "name": "WPA2-Personal"}, {"help": "Wi-Fi security WPA-WPA2 Personal", "label": "Wpa Wpa2 Personal", "name": "WPA-WPA2-Personal"}, {"help": "Wi-Fi security WPA3 SAE", "label": "Wpa3 Sae", "name": "WPA3-SAE"}, {"help": "Wi-Fi security WPA3 SAE Transition", "label": "Wpa3 Sae Transition", "name": "WPA3-SAE-Transition"}, {"help": "Wi-Fi security WPA2 Enterprise", "label": "Wpa2 Enterprise", "name": "WPA2-Enterprise"}, {"help": "Wi-Fi security WPA3 Enterprise only", "label": "Wpa3 Enterprise Only", "name": "WPA3-Enterprise-only"}, {"help": "Wi-Fi security WPA3 Enterprise Transition", "label": "Wpa3 Enterprise Transition", "name": "WPA3-Enterprise-transition"}, {"help": "Wi-Fi security WPA3 Enterprise 192-bit", "label": "Wpa3 Enterprise 192 Bit", "name": "WPA3-Enterprise-192-bit"}]  # Wi-Fi security.
    dtim: NotRequired[int]  # Wi-Fi DTIM (1 - 255) default = 1.
    rts_threshold: NotRequired[int]  # Wi-Fi RTS Threshold (256 - 2347), default = 2347 (RTS/CTS di
    pmf: NotRequired[Literal[{"description": "Disable PMF (Protected Management Frames)", "help": "Disable PMF (Protected Management Frames).", "label": "Disabled", "name": "disabled"}, {"description": "Set PMF (Protected Management Frames) optional", "help": "Set PMF (Protected Management Frames) optional.", "label": "Optional", "name": "optional"}, {"description": "Require PMF (Protected Management Frames)", "help": "Require PMF (Protected Management Frames).", "label": "Required", "name": "required"}]]  # Wi-Fi pmf enable/disable, default = disable.
    target_wake_time: NotRequired[Literal[{"description": "Disable target wake time", "help": "Disable target wake time.", "label": "Disable", "name": "disable"}, {"description": "Enable target wake time", "help": "Enable target wake time.", "label": "Enable", "name": "enable"}]]  # Wi-Fi 802.11AX target wake time enable / disable, default = 
    bss_color_partial: NotRequired[Literal[{"description": "Disable bss color partial", "help": "Disable bss color partial.", "label": "Disable", "name": "disable"}, {"description": "Enable bss color partial", "help": "Enable bss color partial.", "label": "Enable", "name": "enable"}]]  # Wi-Fi 802.11AX bss color partial enable / disable, default =
    mu_mimo: NotRequired[Literal[{"description": "Disable multi-user MIMO", "help": "Disable multi-user MIMO.", "label": "Disable", "name": "disable"}, {"description": "Enable multi-user MIMO", "help": "Enable multi-user MIMO.", "label": "Enable", "name": "enable"}]]  # Wi-Fi multi-user MIMO enable / disable, default = enable.
    passphrase: str  # Wi-Fi passphrase.
    sae_password: str  # Wi-Fi SAE Password.
    auth_server_address: str  # Wi-Fi Authentication Server Address (IPv4 format).
    auth_server_port: int  # Wi-Fi Authentication Server Port.
    auth_server_secret: str  # Wi-Fi Authentication Server Secret.
    ip_address: NotRequired[str]  # Extender ip address.
    start_ip: NotRequired[str]  # Start ip address.
    end_ip: NotRequired[str]  # End ip address.
    allowaccess: NotRequired[Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}]]  # Control management access to the managed extender. Separate 


class ExtenderVap:
    """
    FortiExtender wifi vap configuration.
    
    Path: extension_controller/extender_vap
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
        payload_dict: ExtenderVapPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "Local VAP", "help": "Local VAP.", "label": "Local Vap", "name": "local-vap"}, {"description": "Lan Extension VAP", "help": "Lan Extension VAP.", "label": "Lan Ext Vap", "name": "lan-ext-vap"}] | None = ...,
        ssid: str | None = ...,
        max_clients: int | None = ...,
        broadcast_ssid: Literal[{"description": "Disable broadcast SSID", "help": "Disable broadcast SSID.", "label": "Disable", "name": "disable"}, {"description": "Enable broadcast SSID", "help": "Enable broadcast SSID.", "label": "Enable", "name": "enable"}] | None = ...,
        security: Literal[{"description": "Wi-Fi security OPEN    WPA2-Personal:Wi-Fi security WPA2 Personal    WPA-WPA2-Personal:Wi-Fi security WPA-WPA2 Personal    WPA3-SAE:Wi-Fi security WPA3 SAE    WPA3-SAE-Transition:Wi-Fi security WPA3 SAE Transition    WPA2-Enterprise:Wi-Fi security WPA2 Enterprise    WPA3-Enterprise-only:Wi-Fi security WPA3 Enterprise only    WPA3-Enterprise-transition:Wi-Fi security WPA3 Enterprise Transition    WPA3-Enterprise-192-bit:Wi-Fi security WPA3 Enterprise 192-bit", "help": "Wi-Fi security OPEN", "label": "Open", "name": "OPEN"}, {"help": "Wi-Fi security WPA2 Personal", "label": "Wpa2 Personal", "name": "WPA2-Personal"}, {"help": "Wi-Fi security WPA-WPA2 Personal", "label": "Wpa Wpa2 Personal", "name": "WPA-WPA2-Personal"}, {"help": "Wi-Fi security WPA3 SAE", "label": "Wpa3 Sae", "name": "WPA3-SAE"}, {"help": "Wi-Fi security WPA3 SAE Transition", "label": "Wpa3 Sae Transition", "name": "WPA3-SAE-Transition"}, {"help": "Wi-Fi security WPA2 Enterprise", "label": "Wpa2 Enterprise", "name": "WPA2-Enterprise"}, {"help": "Wi-Fi security WPA3 Enterprise only", "label": "Wpa3 Enterprise Only", "name": "WPA3-Enterprise-only"}, {"help": "Wi-Fi security WPA3 Enterprise Transition", "label": "Wpa3 Enterprise Transition", "name": "WPA3-Enterprise-transition"}, {"help": "Wi-Fi security WPA3 Enterprise 192-bit", "label": "Wpa3 Enterprise 192 Bit", "name": "WPA3-Enterprise-192-bit"}] | None = ...,
        dtim: int | None = ...,
        rts_threshold: int | None = ...,
        pmf: Literal[{"description": "Disable PMF (Protected Management Frames)", "help": "Disable PMF (Protected Management Frames).", "label": "Disabled", "name": "disabled"}, {"description": "Set PMF (Protected Management Frames) optional", "help": "Set PMF (Protected Management Frames) optional.", "label": "Optional", "name": "optional"}, {"description": "Require PMF (Protected Management Frames)", "help": "Require PMF (Protected Management Frames).", "label": "Required", "name": "required"}] | None = ...,
        target_wake_time: Literal[{"description": "Disable target wake time", "help": "Disable target wake time.", "label": "Disable", "name": "disable"}, {"description": "Enable target wake time", "help": "Enable target wake time.", "label": "Enable", "name": "enable"}] | None = ...,
        bss_color_partial: Literal[{"description": "Disable bss color partial", "help": "Disable bss color partial.", "label": "Disable", "name": "disable"}, {"description": "Enable bss color partial", "help": "Enable bss color partial.", "label": "Enable", "name": "enable"}] | None = ...,
        mu_mimo: Literal[{"description": "Disable multi-user MIMO", "help": "Disable multi-user MIMO.", "label": "Disable", "name": "disable"}, {"description": "Enable multi-user MIMO", "help": "Enable multi-user MIMO.", "label": "Enable", "name": "enable"}] | None = ...,
        passphrase: str | None = ...,
        sae_password: str | None = ...,
        auth_server_address: str | None = ...,
        auth_server_port: int | None = ...,
        auth_server_secret: str | None = ...,
        ip_address: str | None = ...,
        start_ip: str | None = ...,
        end_ip: str | None = ...,
        allowaccess: Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ExtenderVapPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "Local VAP", "help": "Local VAP.", "label": "Local Vap", "name": "local-vap"}, {"description": "Lan Extension VAP", "help": "Lan Extension VAP.", "label": "Lan Ext Vap", "name": "lan-ext-vap"}] | None = ...,
        ssid: str | None = ...,
        max_clients: int | None = ...,
        broadcast_ssid: Literal[{"description": "Disable broadcast SSID", "help": "Disable broadcast SSID.", "label": "Disable", "name": "disable"}, {"description": "Enable broadcast SSID", "help": "Enable broadcast SSID.", "label": "Enable", "name": "enable"}] | None = ...,
        security: Literal[{"description": "Wi-Fi security OPEN    WPA2-Personal:Wi-Fi security WPA2 Personal    WPA-WPA2-Personal:Wi-Fi security WPA-WPA2 Personal    WPA3-SAE:Wi-Fi security WPA3 SAE    WPA3-SAE-Transition:Wi-Fi security WPA3 SAE Transition    WPA2-Enterprise:Wi-Fi security WPA2 Enterprise    WPA3-Enterprise-only:Wi-Fi security WPA3 Enterprise only    WPA3-Enterprise-transition:Wi-Fi security WPA3 Enterprise Transition    WPA3-Enterprise-192-bit:Wi-Fi security WPA3 Enterprise 192-bit", "help": "Wi-Fi security OPEN", "label": "Open", "name": "OPEN"}, {"help": "Wi-Fi security WPA2 Personal", "label": "Wpa2 Personal", "name": "WPA2-Personal"}, {"help": "Wi-Fi security WPA-WPA2 Personal", "label": "Wpa Wpa2 Personal", "name": "WPA-WPA2-Personal"}, {"help": "Wi-Fi security WPA3 SAE", "label": "Wpa3 Sae", "name": "WPA3-SAE"}, {"help": "Wi-Fi security WPA3 SAE Transition", "label": "Wpa3 Sae Transition", "name": "WPA3-SAE-Transition"}, {"help": "Wi-Fi security WPA2 Enterprise", "label": "Wpa2 Enterprise", "name": "WPA2-Enterprise"}, {"help": "Wi-Fi security WPA3 Enterprise only", "label": "Wpa3 Enterprise Only", "name": "WPA3-Enterprise-only"}, {"help": "Wi-Fi security WPA3 Enterprise Transition", "label": "Wpa3 Enterprise Transition", "name": "WPA3-Enterprise-transition"}, {"help": "Wi-Fi security WPA3 Enterprise 192-bit", "label": "Wpa3 Enterprise 192 Bit", "name": "WPA3-Enterprise-192-bit"}] | None = ...,
        dtim: int | None = ...,
        rts_threshold: int | None = ...,
        pmf: Literal[{"description": "Disable PMF (Protected Management Frames)", "help": "Disable PMF (Protected Management Frames).", "label": "Disabled", "name": "disabled"}, {"description": "Set PMF (Protected Management Frames) optional", "help": "Set PMF (Protected Management Frames) optional.", "label": "Optional", "name": "optional"}, {"description": "Require PMF (Protected Management Frames)", "help": "Require PMF (Protected Management Frames).", "label": "Required", "name": "required"}] | None = ...,
        target_wake_time: Literal[{"description": "Disable target wake time", "help": "Disable target wake time.", "label": "Disable", "name": "disable"}, {"description": "Enable target wake time", "help": "Enable target wake time.", "label": "Enable", "name": "enable"}] | None = ...,
        bss_color_partial: Literal[{"description": "Disable bss color partial", "help": "Disable bss color partial.", "label": "Disable", "name": "disable"}, {"description": "Enable bss color partial", "help": "Enable bss color partial.", "label": "Enable", "name": "enable"}] | None = ...,
        mu_mimo: Literal[{"description": "Disable multi-user MIMO", "help": "Disable multi-user MIMO.", "label": "Disable", "name": "disable"}, {"description": "Enable multi-user MIMO", "help": "Enable multi-user MIMO.", "label": "Enable", "name": "enable"}] | None = ...,
        passphrase: str | None = ...,
        sae_password: str | None = ...,
        auth_server_address: str | None = ...,
        auth_server_port: int | None = ...,
        auth_server_secret: str | None = ...,
        ip_address: str | None = ...,
        start_ip: str | None = ...,
        end_ip: str | None = ...,
        allowaccess: Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}] | None = ...,
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
        payload_dict: ExtenderVapPayload | None = ...,
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
    "ExtenderVap",
    "ExtenderVapPayload",
]