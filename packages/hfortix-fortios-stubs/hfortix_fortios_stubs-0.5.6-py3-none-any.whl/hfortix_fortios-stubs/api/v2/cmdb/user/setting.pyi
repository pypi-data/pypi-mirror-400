from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingPayload(TypedDict, total=False):
    """
    Type hints for user/setting payload fields.
    
    Configure user authentication setting.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.user.password-policy.PasswordPolicyEndpoint` (via: default-user-password-policy)
        - :class:`~.vpn.certificate.local.LocalEndpoint` (via: auth-ca-cert, auth-cert)

    **Usage:**
        payload: SettingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    auth_type: NotRequired[Literal[{"description": "Allow HTTP authentication", "help": "Allow HTTP authentication.", "label": "Http", "name": "http"}, {"description": "Allow HTTPS authentication", "help": "Allow HTTPS authentication.", "label": "Https", "name": "https"}, {"description": "Allow FTP authentication", "help": "Allow FTP authentication.", "label": "Ftp", "name": "ftp"}, {"description": "Allow TELNET authentication", "help": "Allow TELNET authentication.", "label": "Telnet", "name": "telnet"}]]  # Supported firewall policy authentication protocols/methods.
    auth_cert: NotRequired[str]  # HTTPS server certificate for policy authentication.
    auth_ca_cert: NotRequired[str]  # HTTPS CA certificate for policy authentication.
    auth_secure_http: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable redirecting HTTP user authentication to more 
    auth_http_basic: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of HTTP basic authentication for identity
    auth_ssl_allow_renegotiation: NotRequired[Literal[{"description": "Allow SSL re-negotiation", "help": "Allow SSL re-negotiation.", "label": "Enable", "name": "enable"}, {"description": "Forbid SSL re-negotiation", "help": "Forbid SSL re-negotiation.", "label": "Disable", "name": "disable"}]]  # Allow/forbid SSL re-negotiation for HTTPS authentication.
    auth_src_mac: NotRequired[Literal[{"description": "Enable source MAC for user identity", "help": "Enable source MAC for user identity.", "label": "Enable", "name": "enable"}, {"description": "Disable source MAC for user identity", "help": "Disable source MAC for user identity.", "label": "Disable", "name": "disable"}]]  # Enable/disable source MAC for user identity.
    auth_on_demand: NotRequired[Literal[{"description": "Always trigger firewall authentication on demand", "help": "Always trigger firewall authentication on demand.", "label": "Always", "name": "always"}, {"description": "Implicitly trigger firewall authentication on demand", "help": "Implicitly trigger firewall authentication on demand.", "label": "Implicitly", "name": "implicitly"}]]  # Always/implicitly trigger firewall authentication on demand.
    auth_timeout: NotRequired[int]  # Time in minutes before the firewall user authentication time
    auth_timeout_type: NotRequired[Literal[{"description": "Idle timeout", "help": "Idle timeout.", "label": "Idle Timeout", "name": "idle-timeout"}, {"description": "Hard timeout", "help": "Hard timeout.", "label": "Hard Timeout", "name": "hard-timeout"}, {"description": "New session timeout", "help": "New session timeout.", "label": "New Session", "name": "new-session"}]]  # Control if authenticated users have to login again after a h
    auth_portal_timeout: NotRequired[int]  # Time in minutes before captive portal user have to re-authen
    radius_ses_timeout_act: NotRequired[Literal[{"description": "Use session timeout from RADIUS as hard-timeout", "help": "Use session timeout from RADIUS as hard-timeout.", "label": "Hard Timeout", "name": "hard-timeout"}, {"description": "Ignore session timeout from RADIUS", "help": "Ignore session timeout from RADIUS.", "label": "Ignore Timeout", "name": "ignore-timeout"}]]  # Set the RADIUS session timeout to a hard timeout or to ignor
    auth_blackout_time: NotRequired[int]  # Time in seconds an IP address is denied access after failing
    auth_invalid_max: NotRequired[int]  # Maximum number of failed authentication attempts before the 
    auth_lockout_threshold: NotRequired[int]  # Maximum number of failed login attempts before login lockout
    auth_lockout_duration: NotRequired[int]  # Lockout period in seconds after too many login failures.
    per_policy_disclaimer: NotRequired[Literal[{"description": "Enable per policy disclaimer", "help": "Enable per policy disclaimer.", "label": "Enable", "name": "enable"}, {"description": "Disable per policy disclaimer", "help": "Disable per policy disclaimer.", "label": "Disable", "name": "disable"}]]  # Enable/disable per policy disclaimer.
    auth_ports: NotRequired[list[dict[str, Any]]]  # Set up non-standard ports for authentication with HTTP, HTTP
    auth_ssl_min_proto_version: NotRequired[Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]]  # Minimum supported protocol version for SSL/TLS connections (
    auth_ssl_max_proto_version: NotRequired[Literal[{"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "sslv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "tlsv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "tlsv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "tlsv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "tlsv1-3"}]]  # Maximum supported protocol version for SSL/TLS connections (
    auth_ssl_sigalgs: NotRequired[Literal[{"description": "Disable RSA-PSS signature algorithms for HTTPS authentication", "help": "Disable RSA-PSS signature algorithms for HTTPS authentication.", "label": "No Rsa Pss", "name": "no-rsa-pss"}, {"description": "Enable all supported signature algorithms for HTTPS authentication", "help": "Enable all supported signature algorithms for HTTPS authentication.", "label": "All", "name": "all"}]]  # Set signature algorithms related to HTTPS authentication (af
    default_user_password_policy: NotRequired[str]  # Default password policy to apply to all local users unless o
    cors: NotRequired[Literal[{"description": "Disable allowed origins white list for CORS", "help": "Disable allowed origins white list for CORS.", "label": "Disable", "name": "disable"}, {"description": "Enable allowed origins white list for CORS", "help": "Enable allowed origins white list for CORS.", "label": "Enable", "name": "enable"}]]  # Enable/disable allowed origins white list for CORS.
    cors_allowed_origins: NotRequired[list[dict[str, Any]]]  # Allowed origins white list for CORS.


class Setting:
    """
    Configure user authentication setting.
    
    Path: user/setting
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
        auth_type: Literal[{"description": "Allow HTTP authentication", "help": "Allow HTTP authentication.", "label": "Http", "name": "http"}, {"description": "Allow HTTPS authentication", "help": "Allow HTTPS authentication.", "label": "Https", "name": "https"}, {"description": "Allow FTP authentication", "help": "Allow FTP authentication.", "label": "Ftp", "name": "ftp"}, {"description": "Allow TELNET authentication", "help": "Allow TELNET authentication.", "label": "Telnet", "name": "telnet"}] | None = ...,
        auth_cert: str | None = ...,
        auth_ca_cert: str | None = ...,
        auth_secure_http: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_http_basic: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_ssl_allow_renegotiation: Literal[{"description": "Allow SSL re-negotiation", "help": "Allow SSL re-negotiation.", "label": "Enable", "name": "enable"}, {"description": "Forbid SSL re-negotiation", "help": "Forbid SSL re-negotiation.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_src_mac: Literal[{"description": "Enable source MAC for user identity", "help": "Enable source MAC for user identity.", "label": "Enable", "name": "enable"}, {"description": "Disable source MAC for user identity", "help": "Disable source MAC for user identity.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_on_demand: Literal[{"description": "Always trigger firewall authentication on demand", "help": "Always trigger firewall authentication on demand.", "label": "Always", "name": "always"}, {"description": "Implicitly trigger firewall authentication on demand", "help": "Implicitly trigger firewall authentication on demand.", "label": "Implicitly", "name": "implicitly"}] | None = ...,
        auth_timeout: int | None = ...,
        auth_timeout_type: Literal[{"description": "Idle timeout", "help": "Idle timeout.", "label": "Idle Timeout", "name": "idle-timeout"}, {"description": "Hard timeout", "help": "Hard timeout.", "label": "Hard Timeout", "name": "hard-timeout"}, {"description": "New session timeout", "help": "New session timeout.", "label": "New Session", "name": "new-session"}] | None = ...,
        auth_portal_timeout: int | None = ...,
        radius_ses_timeout_act: Literal[{"description": "Use session timeout from RADIUS as hard-timeout", "help": "Use session timeout from RADIUS as hard-timeout.", "label": "Hard Timeout", "name": "hard-timeout"}, {"description": "Ignore session timeout from RADIUS", "help": "Ignore session timeout from RADIUS.", "label": "Ignore Timeout", "name": "ignore-timeout"}] | None = ...,
        auth_blackout_time: int | None = ...,
        auth_invalid_max: int | None = ...,
        auth_lockout_threshold: int | None = ...,
        auth_lockout_duration: int | None = ...,
        per_policy_disclaimer: Literal[{"description": "Enable per policy disclaimer", "help": "Enable per policy disclaimer.", "label": "Enable", "name": "enable"}, {"description": "Disable per policy disclaimer", "help": "Disable per policy disclaimer.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_ports: list[dict[str, Any]] | None = ...,
        auth_ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        auth_ssl_max_proto_version: Literal[{"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "sslv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "tlsv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "tlsv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "tlsv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "tlsv1-3"}] | None = ...,
        auth_ssl_sigalgs: Literal[{"description": "Disable RSA-PSS signature algorithms for HTTPS authentication", "help": "Disable RSA-PSS signature algorithms for HTTPS authentication.", "label": "No Rsa Pss", "name": "no-rsa-pss"}, {"description": "Enable all supported signature algorithms for HTTPS authentication", "help": "Enable all supported signature algorithms for HTTPS authentication.", "label": "All", "name": "all"}] | None = ...,
        default_user_password_policy: str | None = ...,
        cors: Literal[{"description": "Disable allowed origins white list for CORS", "help": "Disable allowed origins white list for CORS.", "label": "Disable", "name": "disable"}, {"description": "Enable allowed origins white list for CORS", "help": "Enable allowed origins white list for CORS.", "label": "Enable", "name": "enable"}] | None = ...,
        cors_allowed_origins: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SettingPayload | None = ...,
        auth_type: Literal[{"description": "Allow HTTP authentication", "help": "Allow HTTP authentication.", "label": "Http", "name": "http"}, {"description": "Allow HTTPS authentication", "help": "Allow HTTPS authentication.", "label": "Https", "name": "https"}, {"description": "Allow FTP authentication", "help": "Allow FTP authentication.", "label": "Ftp", "name": "ftp"}, {"description": "Allow TELNET authentication", "help": "Allow TELNET authentication.", "label": "Telnet", "name": "telnet"}] | None = ...,
        auth_cert: str | None = ...,
        auth_ca_cert: str | None = ...,
        auth_secure_http: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_http_basic: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_ssl_allow_renegotiation: Literal[{"description": "Allow SSL re-negotiation", "help": "Allow SSL re-negotiation.", "label": "Enable", "name": "enable"}, {"description": "Forbid SSL re-negotiation", "help": "Forbid SSL re-negotiation.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_src_mac: Literal[{"description": "Enable source MAC for user identity", "help": "Enable source MAC for user identity.", "label": "Enable", "name": "enable"}, {"description": "Disable source MAC for user identity", "help": "Disable source MAC for user identity.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_on_demand: Literal[{"description": "Always trigger firewall authentication on demand", "help": "Always trigger firewall authentication on demand.", "label": "Always", "name": "always"}, {"description": "Implicitly trigger firewall authentication on demand", "help": "Implicitly trigger firewall authentication on demand.", "label": "Implicitly", "name": "implicitly"}] | None = ...,
        auth_timeout: int | None = ...,
        auth_timeout_type: Literal[{"description": "Idle timeout", "help": "Idle timeout.", "label": "Idle Timeout", "name": "idle-timeout"}, {"description": "Hard timeout", "help": "Hard timeout.", "label": "Hard Timeout", "name": "hard-timeout"}, {"description": "New session timeout", "help": "New session timeout.", "label": "New Session", "name": "new-session"}] | None = ...,
        auth_portal_timeout: int | None = ...,
        radius_ses_timeout_act: Literal[{"description": "Use session timeout from RADIUS as hard-timeout", "help": "Use session timeout from RADIUS as hard-timeout.", "label": "Hard Timeout", "name": "hard-timeout"}, {"description": "Ignore session timeout from RADIUS", "help": "Ignore session timeout from RADIUS.", "label": "Ignore Timeout", "name": "ignore-timeout"}] | None = ...,
        auth_blackout_time: int | None = ...,
        auth_invalid_max: int | None = ...,
        auth_lockout_threshold: int | None = ...,
        auth_lockout_duration: int | None = ...,
        per_policy_disclaimer: Literal[{"description": "Enable per policy disclaimer", "help": "Enable per policy disclaimer.", "label": "Enable", "name": "enable"}, {"description": "Disable per policy disclaimer", "help": "Disable per policy disclaimer.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_ports: list[dict[str, Any]] | None = ...,
        auth_ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        auth_ssl_max_proto_version: Literal[{"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "sslv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "tlsv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "tlsv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "tlsv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "tlsv1-3"}] | None = ...,
        auth_ssl_sigalgs: Literal[{"description": "Disable RSA-PSS signature algorithms for HTTPS authentication", "help": "Disable RSA-PSS signature algorithms for HTTPS authentication.", "label": "No Rsa Pss", "name": "no-rsa-pss"}, {"description": "Enable all supported signature algorithms for HTTPS authentication", "help": "Enable all supported signature algorithms for HTTPS authentication.", "label": "All", "name": "all"}] | None = ...,
        default_user_password_policy: str | None = ...,
        cors: Literal[{"description": "Disable allowed origins white list for CORS", "help": "Disable allowed origins white list for CORS.", "label": "Disable", "name": "disable"}, {"description": "Enable allowed origins white list for CORS", "help": "Enable allowed origins white list for CORS.", "label": "Enable", "name": "enable"}] | None = ...,
        cors_allowed_origins: list[dict[str, Any]] | None = ...,
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