from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingPayload(TypedDict, total=False):
    """
    Type hints for authentication/setting payload fields.
    
    Configure authentication setting.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.authentication.scheme.SchemeEndpoint` (via: active-auth-scheme, sso-auth-scheme)
        - :class:`~.firewall.address.AddressEndpoint` (via: captive-portal, cert-captive-portal)
        - :class:`~.firewall.address6.Address6Endpoint` (via: captive-portal6)

    **Usage:**
        payload: SettingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    active_auth_scheme: NotRequired[str]  # Active authentication method (scheme name).
    sso_auth_scheme: NotRequired[str]  # Single-Sign-On authentication method (scheme name).
    update_time: NotRequired[str]  # Time of the last update.
    persistent_cookie: NotRequired[Literal[{"description": "Enable persistent cookie", "help": "Enable persistent cookie.", "label": "Enable", "name": "enable"}, {"description": "Disable persistent cookie", "help": "Disable persistent cookie.", "label": "Disable", "name": "disable"}]]  # Enable/disable persistent cookie on web portal authenticatio
    ip_auth_cookie: NotRequired[Literal[{"description": "Enable persistent cookie for IP-based authentication", "help": "Enable persistent cookie for IP-based authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable persistent cookie for IP-based authentication", "help": "Disable persistent cookie for IP-based authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable persistent cookie on IP based web portal auth
    cookie_max_age: NotRequired[int]  # Persistent web portal cookie maximum age in minutes (30 - 10
    cookie_refresh_div: NotRequired[int]  # Refresh rate divider of persistent web portal cookie (defaul
    captive_portal_type: NotRequired[Literal[{"description": "Use FQDN for captive portal", "help": "Use FQDN for captive portal.", "label": "Fqdn", "name": "fqdn"}, {"description": "Use an IP address for captive portal", "help": "Use an IP address for captive portal.", "label": "Ip", "name": "ip"}]]  # Captive portal type.
    captive_portal_ip: NotRequired[str]  # Captive portal IP address.
    captive_portal_ip6: NotRequired[str]  # Captive portal IPv6 address.
    captive_portal: NotRequired[str]  # Captive portal host name.
    captive_portal6: NotRequired[str]  # IPv6 captive portal host name.
    cert_auth: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable redirecting certificate authentication to HTT
    cert_captive_portal: NotRequired[str]  # Certificate captive portal host name.
    cert_captive_portal_ip: NotRequired[str]  # Certificate captive portal IP address.
    cert_captive_portal_port: NotRequired[int]  # Certificate captive portal port number (1 - 65535, default =
    captive_portal_port: NotRequired[int]  # Captive portal port number (1 - 65535, default = 7830).
    auth_https: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable redirecting HTTP user authentication to HTTPS
    captive_portal_ssl_port: NotRequired[int]  # Captive portal SSL port number (1 - 65535, default = 7831).
    user_cert_ca: NotRequired[list[dict[str, Any]]]  # CA certificate used for client certificate verification.
    dev_range: NotRequired[list[dict[str, Any]]]  # Address range for the IP based device query.


class Setting:
    """
    Configure authentication setting.
    
    Path: authentication/setting
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
        payload_dict: SettingPayload | None = ...,
        active_auth_scheme: str | None = ...,
        sso_auth_scheme: str | None = ...,
        update_time: str | None = ...,
        persistent_cookie: Literal[{"description": "Enable persistent cookie", "help": "Enable persistent cookie.", "label": "Enable", "name": "enable"}, {"description": "Disable persistent cookie", "help": "Disable persistent cookie.", "label": "Disable", "name": "disable"}] | None = ...,
        ip_auth_cookie: Literal[{"description": "Enable persistent cookie for IP-based authentication", "help": "Enable persistent cookie for IP-based authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable persistent cookie for IP-based authentication", "help": "Disable persistent cookie for IP-based authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        cookie_max_age: int | None = ...,
        cookie_refresh_div: int | None = ...,
        captive_portal_type: Literal[{"description": "Use FQDN for captive portal", "help": "Use FQDN for captive portal.", "label": "Fqdn", "name": "fqdn"}, {"description": "Use an IP address for captive portal", "help": "Use an IP address for captive portal.", "label": "Ip", "name": "ip"}] | None = ...,
        captive_portal_ip: str | None = ...,
        captive_portal_ip6: str | None = ...,
        captive_portal: str | None = ...,
        captive_portal6: str | None = ...,
        cert_auth: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        cert_captive_portal: str | None = ...,
        cert_captive_portal_ip: str | None = ...,
        cert_captive_portal_port: int | None = ...,
        captive_portal_port: int | None = ...,
        auth_https: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        captive_portal_ssl_port: int | None = ...,
        user_cert_ca: list[dict[str, Any]] | None = ...,
        dev_range: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SettingPayload | None = ...,
        active_auth_scheme: str | None = ...,
        sso_auth_scheme: str | None = ...,
        update_time: str | None = ...,
        persistent_cookie: Literal[{"description": "Enable persistent cookie", "help": "Enable persistent cookie.", "label": "Enable", "name": "enable"}, {"description": "Disable persistent cookie", "help": "Disable persistent cookie.", "label": "Disable", "name": "disable"}] | None = ...,
        ip_auth_cookie: Literal[{"description": "Enable persistent cookie for IP-based authentication", "help": "Enable persistent cookie for IP-based authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable persistent cookie for IP-based authentication", "help": "Disable persistent cookie for IP-based authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        cookie_max_age: int | None = ...,
        cookie_refresh_div: int | None = ...,
        captive_portal_type: Literal[{"description": "Use FQDN for captive portal", "help": "Use FQDN for captive portal.", "label": "Fqdn", "name": "fqdn"}, {"description": "Use an IP address for captive portal", "help": "Use an IP address for captive portal.", "label": "Ip", "name": "ip"}] | None = ...,
        captive_portal_ip: str | None = ...,
        captive_portal_ip6: str | None = ...,
        captive_portal: str | None = ...,
        captive_portal6: str | None = ...,
        cert_auth: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        cert_captive_portal: str | None = ...,
        cert_captive_portal_ip: str | None = ...,
        cert_captive_portal_port: int | None = ...,
        captive_portal_port: int | None = ...,
        auth_https: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        captive_portal_ssl_port: int | None = ...,
        user_cert_ca: list[dict[str, Any]] | None = ...,
        dev_range: list[dict[str, Any]] | None = ...,
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
        payload_dict: SettingPayload | None = ...,
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
    "Setting",
    "SettingPayload",
]