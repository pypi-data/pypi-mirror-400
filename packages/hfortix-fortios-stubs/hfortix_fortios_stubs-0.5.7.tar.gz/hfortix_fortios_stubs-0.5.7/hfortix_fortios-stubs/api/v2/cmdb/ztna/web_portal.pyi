from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class WebPortalPayload(TypedDict, total=False):
    """
    Type hints for ztna/web_portal payload fields.
    
    Configure ztna web-portal.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.authentication.rule.RuleEndpoint` (via: auth-rule)
        - :class:`~.firewall.access-proxy-virtual-host.AccessProxyVirtualHostEndpoint` (via: auth-virtual-host, host)
        - :class:`~.firewall.decrypted-traffic-mirror.DecryptedTrafficMirrorEndpoint` (via: decrypted-traffic-mirror)
        - :class:`~.firewall.vip.VipEndpoint` (via: vip)
        - :class:`~.firewall.vip6.Vip6Endpoint` (via: vip6)

    **Usage:**
        payload: WebPortalPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # ZTNA proxy name.
    vip: NotRequired[str]  # Virtual IP name.
    host: NotRequired[str]  # Virtual or real host name.
    decrypted_traffic_mirror: NotRequired[str]  # Decrypted traffic mirror.
    log_blocked_traffic: NotRequired[Literal[{"description": "Do not log all traffic denied by this ZTNA web-proxy", "help": "Do not log all traffic denied by this ZTNA web-proxy.", "label": "Disable", "name": "disable"}, {"description": "Log all traffic denied by this ZTNA web-proxy", "help": "Log all traffic denied by this ZTNA web-proxy.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging of blocked traffic.
    auth_portal: NotRequired[Literal[{"description": "Disable authentication portal", "help": "Disable authentication portal.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication portal", "help": "Enable authentication portal.", "label": "Enable", "name": "enable"}]]  # Enable/disable authentication portal.
    auth_virtual_host: NotRequired[str]  # Virtual host for authentication portal.
    vip6: NotRequired[str]  # Virtual IPv6 name.
    auth_rule: NotRequired[str]  # Authentication Rule.
    display_bookmark: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable to display the web portal bookmark widget.
    focus_bookmark: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable to prioritize the placement of the bookmark section o
    display_status: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable to display the web portal status widget.
    display_history: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable to display the web portal user login history widget.
    policy_auth_sso: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable policy sso authentication.
    heading: NotRequired[str]  # Web portal heading message.
    theme: NotRequired[Literal[{"description": "Jade theme", "help": "Jade theme.", "label": "Jade", "name": "jade"}, {"description": "Neutrino theme", "help": "Neutrino theme.", "label": "Neutrino", "name": "neutrino"}, {"description": "Mariner theme", "help": "Mariner theme.", "label": "Mariner", "name": "mariner"}, {"description": "Graphite theme", "help": "Graphite theme.", "label": "Graphite", "name": "graphite"}, {"description": "Melongene theme", "help": "Melongene theme.", "label": "Melongene", "name": "melongene"}, {"description": "Jet Stream theme", "help": "Jet Stream theme.", "label": "Jet Stream", "name": "jet-stream"}, {"description": "Security Fabric theme", "help": "Security Fabric theme.", "label": "Security Fabric", "name": "security-fabric"}, {"description": "Dark Matter theme", "help": "Dark Matter theme.", "label": "Dark Matter", "name": "dark-matter"}, {"description": "Onyx theme", "help": "Onyx theme.", "label": "Onyx", "name": "onyx"}, {"description": "Eclipse theme", "help": "Eclipse theme.", "label": "Eclipse", "name": "eclipse"}]]  # Web portal color scheme.
    clipboard: NotRequired[Literal[{"description": "Enable support of RDP/VNC clipboard", "help": "Enable support of RDP/VNC clipboard.", "label": "Enable", "name": "enable"}, {"description": "Disable support of RDP/VNC clipboard", "help": "Disable support of RDP/VNC clipboard.", "label": "Disable", "name": "disable"}]]  # Enable to support RDP/VPC clipboard functionality.
    default_window_width: NotRequired[int]  # Screen width (range from 0 - 65535, default = 1024).
    default_window_height: NotRequired[int]  # Screen height (range from 0 - 65535, default = 768).
    cookie_age: NotRequired[int]  # Time in minutes that client web browsers should keep a cooki
    forticlient_download: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable download option for FortiClient.
    customize_forticlient_download_url: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable support of customized download URL for FortiClient.
    windows_forticlient_download_url: NotRequired[str]  # Download URL for Windows FortiClient.
    macos_forticlient_download_url: NotRequired[str]  # Download URL for Mac FortiClient.


class WebPortal:
    """
    Configure ztna web-portal.
    
    Path: ztna/web_portal
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
        payload_dict: WebPortalPayload | None = ...,
        name: str | None = ...,
        vip: str | None = ...,
        host: str | None = ...,
        decrypted_traffic_mirror: str | None = ...,
        log_blocked_traffic: Literal[{"description": "Do not log all traffic denied by this ZTNA web-proxy", "help": "Do not log all traffic denied by this ZTNA web-proxy.", "label": "Disable", "name": "disable"}, {"description": "Log all traffic denied by this ZTNA web-proxy", "help": "Log all traffic denied by this ZTNA web-proxy.", "label": "Enable", "name": "enable"}] | None = ...,
        auth_portal: Literal[{"description": "Disable authentication portal", "help": "Disable authentication portal.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication portal", "help": "Enable authentication portal.", "label": "Enable", "name": "enable"}] | None = ...,
        auth_virtual_host: str | None = ...,
        vip6: str | None = ...,
        auth_rule: str | None = ...,
        display_bookmark: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        focus_bookmark: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        display_status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        display_history: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        policy_auth_sso: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        heading: str | None = ...,
        theme: Literal[{"description": "Jade theme", "help": "Jade theme.", "label": "Jade", "name": "jade"}, {"description": "Neutrino theme", "help": "Neutrino theme.", "label": "Neutrino", "name": "neutrino"}, {"description": "Mariner theme", "help": "Mariner theme.", "label": "Mariner", "name": "mariner"}, {"description": "Graphite theme", "help": "Graphite theme.", "label": "Graphite", "name": "graphite"}, {"description": "Melongene theme", "help": "Melongene theme.", "label": "Melongene", "name": "melongene"}, {"description": "Jet Stream theme", "help": "Jet Stream theme.", "label": "Jet Stream", "name": "jet-stream"}, {"description": "Security Fabric theme", "help": "Security Fabric theme.", "label": "Security Fabric", "name": "security-fabric"}, {"description": "Dark Matter theme", "help": "Dark Matter theme.", "label": "Dark Matter", "name": "dark-matter"}, {"description": "Onyx theme", "help": "Onyx theme.", "label": "Onyx", "name": "onyx"}, {"description": "Eclipse theme", "help": "Eclipse theme.", "label": "Eclipse", "name": "eclipse"}] | None = ...,
        clipboard: Literal[{"description": "Enable support of RDP/VNC clipboard", "help": "Enable support of RDP/VNC clipboard.", "label": "Enable", "name": "enable"}, {"description": "Disable support of RDP/VNC clipboard", "help": "Disable support of RDP/VNC clipboard.", "label": "Disable", "name": "disable"}] | None = ...,
        default_window_width: int | None = ...,
        default_window_height: int | None = ...,
        cookie_age: int | None = ...,
        forticlient_download: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        customize_forticlient_download_url: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        windows_forticlient_download_url: str | None = ...,
        macos_forticlient_download_url: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: WebPortalPayload | None = ...,
        name: str | None = ...,
        vip: str | None = ...,
        host: str | None = ...,
        decrypted_traffic_mirror: str | None = ...,
        log_blocked_traffic: Literal[{"description": "Do not log all traffic denied by this ZTNA web-proxy", "help": "Do not log all traffic denied by this ZTNA web-proxy.", "label": "Disable", "name": "disable"}, {"description": "Log all traffic denied by this ZTNA web-proxy", "help": "Log all traffic denied by this ZTNA web-proxy.", "label": "Enable", "name": "enable"}] | None = ...,
        auth_portal: Literal[{"description": "Disable authentication portal", "help": "Disable authentication portal.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication portal", "help": "Enable authentication portal.", "label": "Enable", "name": "enable"}] | None = ...,
        auth_virtual_host: str | None = ...,
        vip6: str | None = ...,
        auth_rule: str | None = ...,
        display_bookmark: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        focus_bookmark: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        display_status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        display_history: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        policy_auth_sso: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        heading: str | None = ...,
        theme: Literal[{"description": "Jade theme", "help": "Jade theme.", "label": "Jade", "name": "jade"}, {"description": "Neutrino theme", "help": "Neutrino theme.", "label": "Neutrino", "name": "neutrino"}, {"description": "Mariner theme", "help": "Mariner theme.", "label": "Mariner", "name": "mariner"}, {"description": "Graphite theme", "help": "Graphite theme.", "label": "Graphite", "name": "graphite"}, {"description": "Melongene theme", "help": "Melongene theme.", "label": "Melongene", "name": "melongene"}, {"description": "Jet Stream theme", "help": "Jet Stream theme.", "label": "Jet Stream", "name": "jet-stream"}, {"description": "Security Fabric theme", "help": "Security Fabric theme.", "label": "Security Fabric", "name": "security-fabric"}, {"description": "Dark Matter theme", "help": "Dark Matter theme.", "label": "Dark Matter", "name": "dark-matter"}, {"description": "Onyx theme", "help": "Onyx theme.", "label": "Onyx", "name": "onyx"}, {"description": "Eclipse theme", "help": "Eclipse theme.", "label": "Eclipse", "name": "eclipse"}] | None = ...,
        clipboard: Literal[{"description": "Enable support of RDP/VNC clipboard", "help": "Enable support of RDP/VNC clipboard.", "label": "Enable", "name": "enable"}, {"description": "Disable support of RDP/VNC clipboard", "help": "Disable support of RDP/VNC clipboard.", "label": "Disable", "name": "disable"}] | None = ...,
        default_window_width: int | None = ...,
        default_window_height: int | None = ...,
        cookie_age: int | None = ...,
        forticlient_download: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        customize_forticlient_download_url: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        windows_forticlient_download_url: str | None = ...,
        macos_forticlient_download_url: str | None = ...,
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
        payload_dict: WebPortalPayload | None = ...,
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
    "WebPortal",
    "WebPortalPayload",
]