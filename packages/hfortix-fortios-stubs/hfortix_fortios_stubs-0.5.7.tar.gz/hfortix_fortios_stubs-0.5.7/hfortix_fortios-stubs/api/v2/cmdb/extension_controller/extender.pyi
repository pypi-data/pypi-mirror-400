from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ExtenderPayload(TypedDict, total=False):
    """
    Type hints for extension_controller/extender payload fields.
    
    Extender controller configuration.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.extension-controller.extender-profile.ExtenderProfileEndpoint` (via: profile)

    **Usage:**
        payload: ExtenderPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # FortiExtender entry name.
    id: str  # FortiExtender serial number.
    authorized: Literal[{"description": "Controller discovered this FortiExtender", "help": "Controller discovered this FortiExtender.", "label": "Discovered", "name": "discovered"}, {"description": "Controller is configured to not provide service to this FortiExtender", "help": "Controller is configured to not provide service to this FortiExtender.", "label": "Disable", "name": "disable"}, {"description": "Controller is configured to provide service to this FortiExtender", "help": "Controller is configured to provide service to this FortiExtender.", "label": "Enable", "name": "enable"}]  # FortiExtender Administration (enable or disable).
    ext_name: NotRequired[str]  # FortiExtender name.
    description: NotRequired[str]  # Description.
    vdom: NotRequired[int]  # VDOM.
    device_id: NotRequired[int]  # Device ID.
    extension_type: Literal[{"description": "FortiExtender WAN extension mode", "help": "FortiExtender WAN extension mode.", "label": "Wan Extension", "name": "wan-extension"}, {"description": "FortiExtender LAN extension mode", "help": "FortiExtender LAN extension mode.", "label": "Lan Extension", "name": "lan-extension"}]  # Extension type for this FortiExtender.
    profile: NotRequired[str]  # FortiExtender profile configuration.
    override_allowaccess: NotRequired[Literal[{"description": "Override the extender profile management access configuration", "help": "Override the extender profile management access configuration.", "label": "Enable", "name": "enable"}, {"description": "Use the extender profile management access configuration", "help": "Use the extender profile management access configuration.", "label": "Disable", "name": "disable"}]]  # Enable to override the extender profile management access co
    allowaccess: NotRequired[Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}]]  # Control management access to the managed extender. Separate 
    override_login_password_change: NotRequired[Literal[{"description": "Override the WTP profile login-password (administrator password) setting", "help": "Override the WTP profile login-password (administrator password) setting.", "label": "Enable", "name": "enable"}, {"description": "Use the the WTP profile login-password (administrator password) setting", "help": "Use the the WTP profile login-password (administrator password) setting.", "label": "Disable", "name": "disable"}]]  # Enable to override the extender profile login-password (admi
    login_password_change: NotRequired[Literal[{"description": "Change the managed extender\u0027s administrator password", "help": "Change the managed extender\u0027s administrator password. Use the login-password option to set the password.", "label": "Yes", "name": "yes"}, {"description": "Keep the managed extender\u0027s administrator password set to the factory default", "help": "Keep the managed extender\u0027s administrator password set to the factory default.", "label": "Default", "name": "default"}, {"description": "Do not change the managed extender\u0027s administrator password", "help": "Do not change the managed extender\u0027s administrator password.", "label": "No", "name": "no"}]]  # Change or reset the administrator password of a managed exte
    login_password: str  # Set the managed extender's administrator password.
    override_enforce_bandwidth: NotRequired[Literal[{"description": "Enable override of FortiExtender profile bandwidth setting", "help": "Enable override of FortiExtender profile bandwidth setting.", "label": "Enable", "name": "enable"}, {"description": "Disable override of FortiExtender profile bandwidth setting", "help": "Disable override of FortiExtender profile bandwidth setting.", "label": "Disable", "name": "disable"}]]  # Enable to override the extender profile enforce-bandwidth se
    enforce_bandwidth: NotRequired[Literal[{"description": "Enable to enforce bandwidth limit on LAN extension interface", "help": "Enable to enforce bandwidth limit on LAN extension interface.", "label": "Enable", "name": "enable"}, {"description": "Disable to enforce bandwidth limit on LAN extension interface", "help": "Disable to enforce bandwidth limit on LAN extension interface.", "label": "Disable", "name": "disable"}]]  # Enable/disable enforcement of bandwidth on LAN extension int
    bandwidth_limit: int  # FortiExtender LAN extension bandwidth limit (Mbps).
    wan_extension: NotRequired[str]  # FortiExtender wan extension configuration.
    firmware_provision_latest: NotRequired[Literal[{"description": "Do not automatically provision the latest available firmware", "help": "Do not automatically provision the latest available firmware.", "label": "Disable", "name": "disable"}, {"description": "Automatically attempt a one-time upgrade to the latest available firmware version", "help": "Automatically attempt a one-time upgrade to the latest available firmware version.", "label": "Once", "name": "once"}]]  # Enable/disable one-time automatic provisioning of the latest


class Extender:
    """
    Extender controller configuration.
    
    Path: extension_controller/extender
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
        payload_dict: ExtenderPayload | None = ...,
        name: str | None = ...,
        id: str | None = ...,
        authorized: Literal[{"description": "Controller discovered this FortiExtender", "help": "Controller discovered this FortiExtender.", "label": "Discovered", "name": "discovered"}, {"description": "Controller is configured to not provide service to this FortiExtender", "help": "Controller is configured to not provide service to this FortiExtender.", "label": "Disable", "name": "disable"}, {"description": "Controller is configured to provide service to this FortiExtender", "help": "Controller is configured to provide service to this FortiExtender.", "label": "Enable", "name": "enable"}] | None = ...,
        ext_name: str | None = ...,
        description: str | None = ...,
        device_id: int | None = ...,
        extension_type: Literal[{"description": "FortiExtender WAN extension mode", "help": "FortiExtender WAN extension mode.", "label": "Wan Extension", "name": "wan-extension"}, {"description": "FortiExtender LAN extension mode", "help": "FortiExtender LAN extension mode.", "label": "Lan Extension", "name": "lan-extension"}] | None = ...,
        profile: str | None = ...,
        override_allowaccess: Literal[{"description": "Override the extender profile management access configuration", "help": "Override the extender profile management access configuration.", "label": "Enable", "name": "enable"}, {"description": "Use the extender profile management access configuration", "help": "Use the extender profile management access configuration.", "label": "Disable", "name": "disable"}] | None = ...,
        allowaccess: Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}] | None = ...,
        override_login_password_change: Literal[{"description": "Override the WTP profile login-password (administrator password) setting", "help": "Override the WTP profile login-password (administrator password) setting.", "label": "Enable", "name": "enable"}, {"description": "Use the the WTP profile login-password (administrator password) setting", "help": "Use the the WTP profile login-password (administrator password) setting.", "label": "Disable", "name": "disable"}] | None = ...,
        login_password_change: Literal[{"description": "Change the managed extender\u0027s administrator password", "help": "Change the managed extender\u0027s administrator password. Use the login-password option to set the password.", "label": "Yes", "name": "yes"}, {"description": "Keep the managed extender\u0027s administrator password set to the factory default", "help": "Keep the managed extender\u0027s administrator password set to the factory default.", "label": "Default", "name": "default"}, {"description": "Do not change the managed extender\u0027s administrator password", "help": "Do not change the managed extender\u0027s administrator password.", "label": "No", "name": "no"}] | None = ...,
        login_password: str | None = ...,
        override_enforce_bandwidth: Literal[{"description": "Enable override of FortiExtender profile bandwidth setting", "help": "Enable override of FortiExtender profile bandwidth setting.", "label": "Enable", "name": "enable"}, {"description": "Disable override of FortiExtender profile bandwidth setting", "help": "Disable override of FortiExtender profile bandwidth setting.", "label": "Disable", "name": "disable"}] | None = ...,
        enforce_bandwidth: Literal[{"description": "Enable to enforce bandwidth limit on LAN extension interface", "help": "Enable to enforce bandwidth limit on LAN extension interface.", "label": "Enable", "name": "enable"}, {"description": "Disable to enforce bandwidth limit on LAN extension interface", "help": "Disable to enforce bandwidth limit on LAN extension interface.", "label": "Disable", "name": "disable"}] | None = ...,
        bandwidth_limit: int | None = ...,
        wan_extension: str | None = ...,
        firmware_provision_latest: Literal[{"description": "Do not automatically provision the latest available firmware", "help": "Do not automatically provision the latest available firmware.", "label": "Disable", "name": "disable"}, {"description": "Automatically attempt a one-time upgrade to the latest available firmware version", "help": "Automatically attempt a one-time upgrade to the latest available firmware version.", "label": "Once", "name": "once"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ExtenderPayload | None = ...,
        name: str | None = ...,
        id: str | None = ...,
        authorized: Literal[{"description": "Controller discovered this FortiExtender", "help": "Controller discovered this FortiExtender.", "label": "Discovered", "name": "discovered"}, {"description": "Controller is configured to not provide service to this FortiExtender", "help": "Controller is configured to not provide service to this FortiExtender.", "label": "Disable", "name": "disable"}, {"description": "Controller is configured to provide service to this FortiExtender", "help": "Controller is configured to provide service to this FortiExtender.", "label": "Enable", "name": "enable"}] | None = ...,
        ext_name: str | None = ...,
        description: str | None = ...,
        device_id: int | None = ...,
        extension_type: Literal[{"description": "FortiExtender WAN extension mode", "help": "FortiExtender WAN extension mode.", "label": "Wan Extension", "name": "wan-extension"}, {"description": "FortiExtender LAN extension mode", "help": "FortiExtender LAN extension mode.", "label": "Lan Extension", "name": "lan-extension"}] | None = ...,
        profile: str | None = ...,
        override_allowaccess: Literal[{"description": "Override the extender profile management access configuration", "help": "Override the extender profile management access configuration.", "label": "Enable", "name": "enable"}, {"description": "Use the extender profile management access configuration", "help": "Use the extender profile management access configuration.", "label": "Disable", "name": "disable"}] | None = ...,
        allowaccess: Literal[{"description": "PING access", "help": "PING access.", "label": "Ping", "name": "ping"}, {"description": "TELNET access", "help": "TELNET access.", "label": "Telnet", "name": "telnet"}, {"description": "HTTP access", "help": "HTTP access.", "label": "Http", "name": "http"}, {"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}] | None = ...,
        override_login_password_change: Literal[{"description": "Override the WTP profile login-password (administrator password) setting", "help": "Override the WTP profile login-password (administrator password) setting.", "label": "Enable", "name": "enable"}, {"description": "Use the the WTP profile login-password (administrator password) setting", "help": "Use the the WTP profile login-password (administrator password) setting.", "label": "Disable", "name": "disable"}] | None = ...,
        login_password_change: Literal[{"description": "Change the managed extender\u0027s administrator password", "help": "Change the managed extender\u0027s administrator password. Use the login-password option to set the password.", "label": "Yes", "name": "yes"}, {"description": "Keep the managed extender\u0027s administrator password set to the factory default", "help": "Keep the managed extender\u0027s administrator password set to the factory default.", "label": "Default", "name": "default"}, {"description": "Do not change the managed extender\u0027s administrator password", "help": "Do not change the managed extender\u0027s administrator password.", "label": "No", "name": "no"}] | None = ...,
        login_password: str | None = ...,
        override_enforce_bandwidth: Literal[{"description": "Enable override of FortiExtender profile bandwidth setting", "help": "Enable override of FortiExtender profile bandwidth setting.", "label": "Enable", "name": "enable"}, {"description": "Disable override of FortiExtender profile bandwidth setting", "help": "Disable override of FortiExtender profile bandwidth setting.", "label": "Disable", "name": "disable"}] | None = ...,
        enforce_bandwidth: Literal[{"description": "Enable to enforce bandwidth limit on LAN extension interface", "help": "Enable to enforce bandwidth limit on LAN extension interface.", "label": "Enable", "name": "enable"}, {"description": "Disable to enforce bandwidth limit on LAN extension interface", "help": "Disable to enforce bandwidth limit on LAN extension interface.", "label": "Disable", "name": "disable"}] | None = ...,
        bandwidth_limit: int | None = ...,
        wan_extension: str | None = ...,
        firmware_provision_latest: Literal[{"description": "Do not automatically provision the latest available firmware", "help": "Do not automatically provision the latest available firmware.", "label": "Disable", "name": "disable"}, {"description": "Automatically attempt a one-time upgrade to the latest available firmware version", "help": "Automatically attempt a one-time upgrade to the latest available firmware version.", "label": "Once", "name": "once"}] | None = ...,
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
        payload_dict: ExtenderPayload | None = ...,
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
    "Extender",
    "ExtenderPayload",
]