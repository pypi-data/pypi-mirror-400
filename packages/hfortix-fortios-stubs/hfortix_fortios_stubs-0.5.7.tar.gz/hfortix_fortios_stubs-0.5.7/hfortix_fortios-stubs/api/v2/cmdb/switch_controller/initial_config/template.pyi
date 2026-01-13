from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class TemplatePayload(TypedDict, total=False):
    """
    Type hints for switch_controller/initial_config/template payload fields.
    
    Configure template for auto-generated VLANs.
    
    **Usage:**
        payload: TemplatePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Initial config template name.
    vlanid: int  # Unique VLAN ID.
    ip: NotRequired[str]  # Interface IPv4 address and subnet mask.
    allowaccess: NotRequired[Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "FortiManager access", "help": "FortiManager access.", "label": "Fgfm", "name": "fgfm"}, {"description": "RADIUS accounting access", "help": "RADIUS accounting access.", "label": "Radius Acct", "name": "radius-acct"}, {"description": "Probe access", "help": "Probe access.", "label": "Probe Response", "name": "probe-response"}, {"description": "Security Fabric access", "help": "Security Fabric access.", "label": "Fabric", "name": "fabric"}, {"description": "FTM access", "help": "FTM access.", "label": "Ftm", "name": "ftm"}]]  # Permitted types of management access to this interface.
    auto_ip: NotRequired[Literal[{"description": "Enable auto-ip status", "help": "Enable auto-ip status.", "label": "Enable", "name": "enable"}, {"description": "Disable auto-ip status", "help": "Disable auto-ip status.", "label": "Disable", "name": "disable"}]]  # Automatically allocate interface address and subnet block.
    dhcp_server: NotRequired[Literal[{"description": "Enable DHCP server", "help": "Enable DHCP server.", "label": "Enable", "name": "enable"}, {"description": "Disable DHCP server", "help": "Disable DHCP server.", "label": "Disable", "name": "disable"}]]  # Enable/disable a DHCP server on this interface.


class Template:
    """
    Configure template for auto-generated VLANs.
    
    Path: switch_controller/initial_config/template
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
        payload_dict: TemplatePayload | None = ...,
        name: str | None = ...,
        vlanid: int | None = ...,
        ip: str | None = ...,
        allowaccess: Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "FortiManager access", "help": "FortiManager access.", "label": "Fgfm", "name": "fgfm"}, {"description": "RADIUS accounting access", "help": "RADIUS accounting access.", "label": "Radius Acct", "name": "radius-acct"}, {"description": "Probe access", "help": "Probe access.", "label": "Probe Response", "name": "probe-response"}, {"description": "Security Fabric access", "help": "Security Fabric access.", "label": "Fabric", "name": "fabric"}, {"description": "FTM access", "help": "FTM access.", "label": "Ftm", "name": "ftm"}] | None = ...,
        auto_ip: Literal[{"description": "Enable auto-ip status", "help": "Enable auto-ip status.", "label": "Enable", "name": "enable"}, {"description": "Disable auto-ip status", "help": "Disable auto-ip status.", "label": "Disable", "name": "disable"}] | None = ...,
        dhcp_server: Literal[{"description": "Enable DHCP server", "help": "Enable DHCP server.", "label": "Enable", "name": "enable"}, {"description": "Disable DHCP server", "help": "Disable DHCP server.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: TemplatePayload | None = ...,
        name: str | None = ...,
        vlanid: int | None = ...,
        ip: str | None = ...,
        allowaccess: Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "FortiManager access", "help": "FortiManager access.", "label": "Fgfm", "name": "fgfm"}, {"description": "RADIUS accounting access", "help": "RADIUS accounting access.", "label": "Radius Acct", "name": "radius-acct"}, {"description": "Probe access", "help": "Probe access.", "label": "Probe Response", "name": "probe-response"}, {"description": "Security Fabric access", "help": "Security Fabric access.", "label": "Fabric", "name": "fabric"}, {"description": "FTM access", "help": "FTM access.", "label": "Ftm", "name": "ftm"}] | None = ...,
        auto_ip: Literal[{"description": "Enable auto-ip status", "help": "Enable auto-ip status.", "label": "Enable", "name": "enable"}, {"description": "Disable auto-ip status", "help": "Disable auto-ip status.", "label": "Disable", "name": "disable"}] | None = ...,
        dhcp_server: Literal[{"description": "Enable DHCP server", "help": "Enable DHCP server.", "label": "Enable", "name": "enable"}, {"description": "Disable DHCP server", "help": "Disable DHCP server.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: TemplatePayload | None = ...,
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
    "Template",
    "TemplatePayload",
]