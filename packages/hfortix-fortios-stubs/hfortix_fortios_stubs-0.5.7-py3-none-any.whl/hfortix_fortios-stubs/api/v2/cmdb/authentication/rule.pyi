from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class RulePayload(TypedDict, total=False):
    """
    Type hints for authentication/rule payload fields.
    
    Configure Authentication Rules.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.authentication.scheme.SchemeEndpoint` (via: active-auth-method, sso-auth-method)

    **Usage:**
        payload: RulePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Authentication rule name.
    status: NotRequired[Literal[{"description": "Enable this authentication rule", "help": "Enable this authentication rule.", "label": "Enable", "name": "enable"}, {"description": "Disable this authentication rule", "help": "Disable this authentication rule.", "label": "Disable", "name": "disable"}]]  # Enable/disable this authentication rule.
    protocol: NotRequired[Literal[{"description": "HTTP traffic is matched and authentication is required", "help": "HTTP traffic is matched and authentication is required.", "label": "Http", "name": "http"}, {"description": "FTP traffic is matched and authentication is required", "help": "FTP traffic is matched and authentication is required.", "label": "Ftp", "name": "ftp"}, {"description": "SOCKS traffic is matched and authentication is required", "help": "SOCKS traffic is matched and authentication is required.", "label": "Socks", "name": "socks"}, {"description": "SSH traffic is matched and authentication is required", "help": "SSH traffic is matched and authentication is required.", "label": "Ssh", "name": "ssh"}, {"description": "ZTNA portal traffic is matched and authentication is required", "help": "ZTNA portal traffic is matched and authentication is required.", "label": "Ztna Portal", "name": "ztna-portal"}]]  # Authentication is required for the selected protocol (defaul
    srcintf: NotRequired[list[dict[str, Any]]]  # Incoming (ingress) interface.
    srcaddr: NotRequired[list[dict[str, Any]]]  # Authentication is required for the selected IPv4 source addr
    dstaddr: NotRequired[list[dict[str, Any]]]  # Select an IPv4 destination address from available options. R
    srcaddr6: NotRequired[list[dict[str, Any]]]  # Authentication is required for the selected IPv6 source addr
    dstaddr6: NotRequired[list[dict[str, Any]]]  # Select an IPv6 destination address from available options. R
    ip_based: NotRequired[Literal[{"description": "Enable IP-based authentication", "help": "Enable IP-based authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable IP-based authentication", "help": "Disable IP-based authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable IP-based authentication. When enabled, previo
    active_auth_method: NotRequired[str]  # Select an active authentication method.
    sso_auth_method: NotRequired[str]  # Select a single-sign on (SSO) authentication method.
    web_auth_cookie: NotRequired[Literal[{"description": "Enable Web authentication cookie", "help": "Enable Web authentication cookie.", "label": "Enable", "name": "enable"}, {"description": "Disable Web authentication cookie", "help": "Disable Web authentication cookie.", "label": "Disable", "name": "disable"}]]  # Enable/disable Web authentication cookies (default = disable
    cors_stateful: NotRequired[Literal[{"description": "Enable allowance of CORS access    disable:Disable allowance of CORS access", "help": "Enable allowance of CORS access", "label": "Enable", "name": "enable"}, {"help": "Disable allowance of CORS access", "label": "Disable", "name": "disable"}]]  # Enable/disable allowance of CORS access (default = disable).
    cors_depth: NotRequired[int]  # Depth to allow CORS access (default = 3).
    cert_auth_cookie: NotRequired[Literal[{"description": "Enable device certificate as authentication cookie", "help": "Enable device certificate as authentication cookie.", "label": "Enable", "name": "enable"}, {"description": "Disable device certificate as authentication cookie", "help": "Disable device certificate as authentication cookie.", "label": "Disable", "name": "disable"}]]  # Enable/disable to use device certificate as authentication c
    transaction_based: NotRequired[Literal[{"description": "Enable transaction based authentication", "help": "Enable transaction based authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable transaction based authentication", "help": "Disable transaction based authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable transaction based authentication (default = d
    web_portal: NotRequired[Literal[{"description": "Enable web-portal", "help": "Enable web-portal.", "label": "Enable", "name": "enable"}, {"description": "Disable web-portal", "help": "Disable web-portal.", "label": "Disable", "name": "disable"}]]  # Enable/disable web portal for proxy transparent policy (defa
    comments: NotRequired[str]  # Comment.
    session_logout: NotRequired[Literal[{"description": "Enable logout of a user from the current session", "help": "Enable logout of a user from the current session.", "label": "Enable", "name": "enable"}, {"description": "Disable logout of a user from the current session", "help": "Disable logout of a user from the current session.", "label": "Disable", "name": "disable"}]]  # Enable/disable logout of a user from the current session.


class Rule:
    """
    Configure Authentication Rules.
    
    Path: authentication/rule
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
        payload_dict: RulePayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Enable this authentication rule", "help": "Enable this authentication rule.", "label": "Enable", "name": "enable"}, {"description": "Disable this authentication rule", "help": "Disable this authentication rule.", "label": "Disable", "name": "disable"}] | None = ...,
        protocol: Literal[{"description": "HTTP traffic is matched and authentication is required", "help": "HTTP traffic is matched and authentication is required.", "label": "Http", "name": "http"}, {"description": "FTP traffic is matched and authentication is required", "help": "FTP traffic is matched and authentication is required.", "label": "Ftp", "name": "ftp"}, {"description": "SOCKS traffic is matched and authentication is required", "help": "SOCKS traffic is matched and authentication is required.", "label": "Socks", "name": "socks"}, {"description": "SSH traffic is matched and authentication is required", "help": "SSH traffic is matched and authentication is required.", "label": "Ssh", "name": "ssh"}, {"description": "ZTNA portal traffic is matched and authentication is required", "help": "ZTNA portal traffic is matched and authentication is required.", "label": "Ztna Portal", "name": "ztna-portal"}] | None = ...,
        srcintf: list[dict[str, Any]] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        srcaddr6: list[dict[str, Any]] | None = ...,
        dstaddr6: list[dict[str, Any]] | None = ...,
        ip_based: Literal[{"description": "Enable IP-based authentication", "help": "Enable IP-based authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable IP-based authentication", "help": "Disable IP-based authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        active_auth_method: str | None = ...,
        sso_auth_method: str | None = ...,
        web_auth_cookie: Literal[{"description": "Enable Web authentication cookie", "help": "Enable Web authentication cookie.", "label": "Enable", "name": "enable"}, {"description": "Disable Web authentication cookie", "help": "Disable Web authentication cookie.", "label": "Disable", "name": "disable"}] | None = ...,
        cors_stateful: Literal[{"description": "Enable allowance of CORS access    disable:Disable allowance of CORS access", "help": "Enable allowance of CORS access", "label": "Enable", "name": "enable"}, {"help": "Disable allowance of CORS access", "label": "Disable", "name": "disable"}] | None = ...,
        cors_depth: int | None = ...,
        cert_auth_cookie: Literal[{"description": "Enable device certificate as authentication cookie", "help": "Enable device certificate as authentication cookie.", "label": "Enable", "name": "enable"}, {"description": "Disable device certificate as authentication cookie", "help": "Disable device certificate as authentication cookie.", "label": "Disable", "name": "disable"}] | None = ...,
        transaction_based: Literal[{"description": "Enable transaction based authentication", "help": "Enable transaction based authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable transaction based authentication", "help": "Disable transaction based authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        web_portal: Literal[{"description": "Enable web-portal", "help": "Enable web-portal.", "label": "Enable", "name": "enable"}, {"description": "Disable web-portal", "help": "Disable web-portal.", "label": "Disable", "name": "disable"}] | None = ...,
        comments: str | None = ...,
        session_logout: Literal[{"description": "Enable logout of a user from the current session", "help": "Enable logout of a user from the current session.", "label": "Enable", "name": "enable"}, {"description": "Disable logout of a user from the current session", "help": "Disable logout of a user from the current session.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: RulePayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Enable this authentication rule", "help": "Enable this authentication rule.", "label": "Enable", "name": "enable"}, {"description": "Disable this authentication rule", "help": "Disable this authentication rule.", "label": "Disable", "name": "disable"}] | None = ...,
        protocol: Literal[{"description": "HTTP traffic is matched and authentication is required", "help": "HTTP traffic is matched and authentication is required.", "label": "Http", "name": "http"}, {"description": "FTP traffic is matched and authentication is required", "help": "FTP traffic is matched and authentication is required.", "label": "Ftp", "name": "ftp"}, {"description": "SOCKS traffic is matched and authentication is required", "help": "SOCKS traffic is matched and authentication is required.", "label": "Socks", "name": "socks"}, {"description": "SSH traffic is matched and authentication is required", "help": "SSH traffic is matched and authentication is required.", "label": "Ssh", "name": "ssh"}, {"description": "ZTNA portal traffic is matched and authentication is required", "help": "ZTNA portal traffic is matched and authentication is required.", "label": "Ztna Portal", "name": "ztna-portal"}] | None = ...,
        srcintf: list[dict[str, Any]] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        srcaddr6: list[dict[str, Any]] | None = ...,
        dstaddr6: list[dict[str, Any]] | None = ...,
        ip_based: Literal[{"description": "Enable IP-based authentication", "help": "Enable IP-based authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable IP-based authentication", "help": "Disable IP-based authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        active_auth_method: str | None = ...,
        sso_auth_method: str | None = ...,
        web_auth_cookie: Literal[{"description": "Enable Web authentication cookie", "help": "Enable Web authentication cookie.", "label": "Enable", "name": "enable"}, {"description": "Disable Web authentication cookie", "help": "Disable Web authentication cookie.", "label": "Disable", "name": "disable"}] | None = ...,
        cors_stateful: Literal[{"description": "Enable allowance of CORS access    disable:Disable allowance of CORS access", "help": "Enable allowance of CORS access", "label": "Enable", "name": "enable"}, {"help": "Disable allowance of CORS access", "label": "Disable", "name": "disable"}] | None = ...,
        cors_depth: int | None = ...,
        cert_auth_cookie: Literal[{"description": "Enable device certificate as authentication cookie", "help": "Enable device certificate as authentication cookie.", "label": "Enable", "name": "enable"}, {"description": "Disable device certificate as authentication cookie", "help": "Disable device certificate as authentication cookie.", "label": "Disable", "name": "disable"}] | None = ...,
        transaction_based: Literal[{"description": "Enable transaction based authentication", "help": "Enable transaction based authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable transaction based authentication", "help": "Disable transaction based authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        web_portal: Literal[{"description": "Enable web-portal", "help": "Enable web-portal.", "label": "Enable", "name": "enable"}, {"description": "Disable web-portal", "help": "Disable web-portal.", "label": "Disable", "name": "disable"}] | None = ...,
        comments: str | None = ...,
        session_logout: Literal[{"description": "Enable logout of a user from the current session", "help": "Enable logout of a user from the current session.", "label": "Enable", "name": "enable"}, {"description": "Disable logout of a user from the current session", "help": "Disable logout of a user from the current session.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: RulePayload | None = ...,
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
    "Rule",
    "RulePayload",
]