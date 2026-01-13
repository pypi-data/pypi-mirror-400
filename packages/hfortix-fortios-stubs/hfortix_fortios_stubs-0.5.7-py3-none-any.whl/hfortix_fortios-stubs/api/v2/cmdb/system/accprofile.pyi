from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class AccprofilePayload(TypedDict, total=False):
    """
    Type hints for system/accprofile payload fields.
    
    Configure access profiles for system administrators.
    
    **Usage:**
        payload: AccprofilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Profile name.
    scope: NotRequired[Literal[{"description": "VDOM access", "help": "VDOM access.", "label": "Vdom", "name": "vdom"}, {"description": "Global access", "help": "Global access.", "label": "Global", "name": "global"}]]  # Scope of admin access: global or specific VDOM(s).
    comments: NotRequired[str]  # Comment.
    secfabgrp: NotRequired[Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}]]  # Security Fabric.
    ftviewgrp: NotRequired[Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}]]  # FortiView.
    authgrp: NotRequired[Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}]]  # Administrator access to Users and Devices.
    sysgrp: NotRequired[Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}]]  # System Configuration.
    netgrp: NotRequired[Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}]]  # Network Configuration.
    loggrp: NotRequired[Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}]]  # Administrator access to Logging and Reporting including view
    fwgrp: NotRequired[Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}]]  # Administrator access to the Firewall configuration.
    vpngrp: NotRequired[Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}]]  # Administrator access to IPsec, SSL, PPTP, and L2TP VPN.
    utmgrp: NotRequired[Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}]]  # Administrator access to Security Profiles.
    wanoptgrp: NotRequired[Literal[{"help": "No access.", "label": "None", "name": "none"}, {"help": "Read access.", "label": "Read", "name": "read"}, {"help": "Read/write access.", "label": "Read Write", "name": "read-write"}]]  # Administrator access to WAN Opt & Cache.
    wifi: NotRequired[Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}]]  # Administrator access to the WiFi controller and Switch contr
    netgrp_permission: NotRequired[str]  # Custom network permission.
    sysgrp_permission: NotRequired[str]  # Custom system permission.
    fwgrp_permission: NotRequired[str]  # Custom firewall permission.
    loggrp_permission: NotRequired[str]  # Custom Log & Report permission.
    utmgrp_permission: NotRequired[str]  # Custom Security Profile permissions.
    secfabgrp_permission: NotRequired[str]  # Custom Security Fabric permissions.
    admintimeout_override: NotRequired[Literal[{"description": "Enable overriding the global administrator idle timeout", "help": "Enable overriding the global administrator idle timeout.", "label": "Enable", "name": "enable"}, {"description": "Disable overriding the global administrator idle timeout", "help": "Disable overriding the global administrator idle timeout.", "label": "Disable", "name": "disable"}]]  # Enable/disable overriding the global administrator idle time
    admintimeout: NotRequired[int]  # Administrator timeout for this access profile (0 - 480 min, 
    cli_diagnose: NotRequired[Literal[{"description": "Enable permission to run diagnostic commands", "help": "Enable permission to run diagnostic commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run diagnostic commands", "help": "Disable permission to run diagnostic commands.", "label": "Disable", "name": "disable"}]]  # Enable/disable permission to run diagnostic commands.
    cli_get: NotRequired[Literal[{"description": "Enable permission to run get commands", "help": "Enable permission to run get commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run get commands", "help": "Disable permission to run get commands.", "label": "Disable", "name": "disable"}]]  # Enable/disable permission to run get commands.
    cli_show: NotRequired[Literal[{"description": "Enable permission to run show commands", "help": "Enable permission to run show commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run show commands", "help": "Disable permission to run show commands.", "label": "Disable", "name": "disable"}]]  # Enable/disable permission to run show commands.
    cli_exec: NotRequired[Literal[{"description": "Enable permission to run execute commands", "help": "Enable permission to run execute commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run execute commands", "help": "Disable permission to run execute commands.", "label": "Disable", "name": "disable"}]]  # Enable/disable permission to run execute commands.
    cli_config: NotRequired[Literal[{"description": "Enable permission to run config commands", "help": "Enable permission to run config commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run config commands", "help": "Disable permission to run config commands.", "label": "Disable", "name": "disable"}]]  # Enable/disable permission to run config commands.
    system_execute_ssh: NotRequired[Literal[{"description": "Enable permission to execute SSH commands", "help": "Enable permission to execute SSH commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to execute SSH commands", "help": "Disable permission to execute SSH commands.", "label": "Disable", "name": "disable"}]]  # Enable/disable permission to execute SSH commands.
    system_execute_telnet: NotRequired[Literal[{"description": "Enable permission to execute TELNET commands", "help": "Enable permission to execute TELNET commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to execute TELNET commands", "help": "Disable permission to execute TELNET commands.", "label": "Disable", "name": "disable"}]]  # Enable/disable permission to execute TELNET commands.


class Accprofile:
    """
    Configure access profiles for system administrators.
    
    Path: system/accprofile
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
        payload_dict: AccprofilePayload | None = ...,
        name: str | None = ...,
        scope: Literal[{"description": "VDOM access", "help": "VDOM access.", "label": "Vdom", "name": "vdom"}, {"description": "Global access", "help": "Global access.", "label": "Global", "name": "global"}] | None = ...,
        comments: str | None = ...,
        secfabgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}] | None = ...,
        ftviewgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}] | None = ...,
        authgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}] | None = ...,
        sysgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}] | None = ...,
        netgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}] | None = ...,
        loggrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}] | None = ...,
        fwgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}] | None = ...,
        vpngrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}] | None = ...,
        utmgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}] | None = ...,
        wanoptgrp: Literal[{"help": "No access.", "label": "None", "name": "none"}, {"help": "Read access.", "label": "Read", "name": "read"}, {"help": "Read/write access.", "label": "Read Write", "name": "read-write"}] | None = ...,
        wifi: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}] | None = ...,
        netgrp_permission: str | None = ...,
        sysgrp_permission: str | None = ...,
        fwgrp_permission: str | None = ...,
        loggrp_permission: str | None = ...,
        utmgrp_permission: str | None = ...,
        secfabgrp_permission: str | None = ...,
        admintimeout_override: Literal[{"description": "Enable overriding the global administrator idle timeout", "help": "Enable overriding the global administrator idle timeout.", "label": "Enable", "name": "enable"}, {"description": "Disable overriding the global administrator idle timeout", "help": "Disable overriding the global administrator idle timeout.", "label": "Disable", "name": "disable"}] | None = ...,
        admintimeout: int | None = ...,
        cli_diagnose: Literal[{"description": "Enable permission to run diagnostic commands", "help": "Enable permission to run diagnostic commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run diagnostic commands", "help": "Disable permission to run diagnostic commands.", "label": "Disable", "name": "disable"}] | None = ...,
        cli_get: Literal[{"description": "Enable permission to run get commands", "help": "Enable permission to run get commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run get commands", "help": "Disable permission to run get commands.", "label": "Disable", "name": "disable"}] | None = ...,
        cli_show: Literal[{"description": "Enable permission to run show commands", "help": "Enable permission to run show commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run show commands", "help": "Disable permission to run show commands.", "label": "Disable", "name": "disable"}] | None = ...,
        cli_exec: Literal[{"description": "Enable permission to run execute commands", "help": "Enable permission to run execute commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run execute commands", "help": "Disable permission to run execute commands.", "label": "Disable", "name": "disable"}] | None = ...,
        cli_config: Literal[{"description": "Enable permission to run config commands", "help": "Enable permission to run config commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run config commands", "help": "Disable permission to run config commands.", "label": "Disable", "name": "disable"}] | None = ...,
        system_execute_ssh: Literal[{"description": "Enable permission to execute SSH commands", "help": "Enable permission to execute SSH commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to execute SSH commands", "help": "Disable permission to execute SSH commands.", "label": "Disable", "name": "disable"}] | None = ...,
        system_execute_telnet: Literal[{"description": "Enable permission to execute TELNET commands", "help": "Enable permission to execute TELNET commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to execute TELNET commands", "help": "Disable permission to execute TELNET commands.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: AccprofilePayload | None = ...,
        name: str | None = ...,
        scope: Literal[{"description": "VDOM access", "help": "VDOM access.", "label": "Vdom", "name": "vdom"}, {"description": "Global access", "help": "Global access.", "label": "Global", "name": "global"}] | None = ...,
        comments: str | None = ...,
        secfabgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}] | None = ...,
        ftviewgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}] | None = ...,
        authgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}] | None = ...,
        sysgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}] | None = ...,
        netgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}] | None = ...,
        loggrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}] | None = ...,
        fwgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}] | None = ...,
        vpngrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}] | None = ...,
        utmgrp: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}] | None = ...,
        wanoptgrp: Literal[{"help": "No access.", "label": "None", "name": "none"}, {"help": "Read access.", "label": "Read", "name": "read"}, {"help": "Read/write access.", "label": "Read Write", "name": "read-write"}] | None = ...,
        wifi: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}] | None = ...,
        netgrp_permission: str | None = ...,
        sysgrp_permission: str | None = ...,
        fwgrp_permission: str | None = ...,
        loggrp_permission: str | None = ...,
        utmgrp_permission: str | None = ...,
        secfabgrp_permission: str | None = ...,
        admintimeout_override: Literal[{"description": "Enable overriding the global administrator idle timeout", "help": "Enable overriding the global administrator idle timeout.", "label": "Enable", "name": "enable"}, {"description": "Disable overriding the global administrator idle timeout", "help": "Disable overriding the global administrator idle timeout.", "label": "Disable", "name": "disable"}] | None = ...,
        admintimeout: int | None = ...,
        cli_diagnose: Literal[{"description": "Enable permission to run diagnostic commands", "help": "Enable permission to run diagnostic commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run diagnostic commands", "help": "Disable permission to run diagnostic commands.", "label": "Disable", "name": "disable"}] | None = ...,
        cli_get: Literal[{"description": "Enable permission to run get commands", "help": "Enable permission to run get commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run get commands", "help": "Disable permission to run get commands.", "label": "Disable", "name": "disable"}] | None = ...,
        cli_show: Literal[{"description": "Enable permission to run show commands", "help": "Enable permission to run show commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run show commands", "help": "Disable permission to run show commands.", "label": "Disable", "name": "disable"}] | None = ...,
        cli_exec: Literal[{"description": "Enable permission to run execute commands", "help": "Enable permission to run execute commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run execute commands", "help": "Disable permission to run execute commands.", "label": "Disable", "name": "disable"}] | None = ...,
        cli_config: Literal[{"description": "Enable permission to run config commands", "help": "Enable permission to run config commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run config commands", "help": "Disable permission to run config commands.", "label": "Disable", "name": "disable"}] | None = ...,
        system_execute_ssh: Literal[{"description": "Enable permission to execute SSH commands", "help": "Enable permission to execute SSH commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to execute SSH commands", "help": "Disable permission to execute SSH commands.", "label": "Disable", "name": "disable"}] | None = ...,
        system_execute_telnet: Literal[{"description": "Enable permission to execute TELNET commands", "help": "Enable permission to execute TELNET commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to execute TELNET commands", "help": "Disable permission to execute TELNET commands.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: AccprofilePayload | None = ...,
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
    "Accprofile",
    "AccprofilePayload",
]