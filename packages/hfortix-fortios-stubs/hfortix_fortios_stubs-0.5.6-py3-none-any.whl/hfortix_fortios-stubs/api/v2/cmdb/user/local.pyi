from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class LocalPayload(TypedDict, total=False):
    """
    Type hints for user/local payload fields.
    
    Configure local users.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.sms-server.SmsServerEndpoint` (via: sms-custom-server)
        - :class:`~.user.fortitoken.FortitokenEndpoint` (via: fortitoken)
        - :class:`~.user.ldap.LdapEndpoint` (via: ldap-server)
        - :class:`~.user.password-policy.PasswordPolicyEndpoint` (via: passwd-policy)
        - :class:`~.user.radius.RadiusEndpoint` (via: radius-server)
        - :class:`~.user.saml.SamlEndpoint` (via: saml-server)
        - :class:`~.user.tacacs+.TacacsPlusEndpoint` (via: tacacs+-server)
        - :class:`~.vpn.qkd.QkdEndpoint` (via: qkd-profile)

    **Usage:**
        payload: LocalPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Local user name.
    id: NotRequired[int]  # User ID.
    status: Literal[{"description": "Enable user", "help": "Enable user.", "label": "Enable", "name": "enable"}, {"description": "Disable user", "help": "Disable user.", "label": "Disable", "name": "disable"}]  # Enable/disable allowing the local user to authenticate with 
    type: Literal[{"description": "Password authentication", "help": "Password authentication.", "label": "Password", "name": "password"}, {"description": "RADIUS server authentication", "help": "RADIUS server authentication.", "label": "Radius", "name": "radius"}, {"description": "TACACS+ server authentication", "help": "TACACS+ server authentication.", "label": "Tacacs+", "name": "tacacs+"}, {"description": "LDAP server authentication", "help": "LDAP server authentication.", "label": "Ldap", "name": "ldap"}, {"description": "SAML server authentication", "help": "SAML server authentication.", "label": "Saml", "name": "saml"}]  # Authentication method.
    passwd: str  # User's password.
    ldap_server: str  # Name of LDAP server with which the user must authenticate.
    radius_server: str  # Name of RADIUS server with which the user must authenticate.
    tacacs_plus_server: str  # Name of TACACS+ server with which the user must authenticate
    saml_server: str  # Name of SAML server with which the user must authenticate.
    two_factor: NotRequired[Literal[{"description": "disable    fortitoken:FortiToken    fortitoken-cloud:FortiToken Cloud Service", "help": "disable", "label": "Disable", "name": "disable"}, {"help": "FortiToken", "label": "Fortitoken", "name": "fortitoken"}, {"help": "FortiToken Cloud Service.", "label": "Fortitoken Cloud", "name": "fortitoken-cloud"}, {"description": "Email authentication code", "help": "Email authentication code.", "label": "Email", "name": "email"}, {"description": "SMS authentication code", "help": "SMS authentication code.", "label": "Sms", "name": "sms"}]]  # Enable/disable two-factor authentication.
    two_factor_authentication: NotRequired[Literal[{"description": "FortiToken authentication", "help": "FortiToken authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "Email one time password", "help": "Email one time password.", "label": "Email", "name": "email"}, {"description": "SMS one time password", "help": "SMS one time password.", "label": "Sms", "name": "sms"}]]  # Authentication method by FortiToken Cloud.
    two_factor_notification: NotRequired[Literal[{"description": "Email notification for activation code", "help": "Email notification for activation code.", "label": "Email", "name": "email"}, {"description": "SMS notification for activation code", "help": "SMS notification for activation code.", "label": "Sms", "name": "sms"}]]  # Notification method for user activation by FortiToken Cloud.
    fortitoken: NotRequired[str]  # Two-factor recipient's FortiToken serial number.
    email_to: NotRequired[str]  # Two-factor recipient's email address.
    sms_server: NotRequired[Literal[{"description": "Send SMS by FortiGuard", "help": "Send SMS by FortiGuard.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Send SMS by custom server", "help": "Send SMS by custom server.", "label": "Custom", "name": "custom"}]]  # Send SMS through FortiGuard or other external server.
    sms_custom_server: NotRequired[str]  # Two-factor recipient's SMS server.
    sms_phone: NotRequired[str]  # Two-factor recipient's mobile phone number.
    passwd_policy: NotRequired[str]  # Password policy to apply to this user, as defined in config 
    passwd_time: NotRequired[str]  # Time of the last password update.
    authtimeout: NotRequired[int]  # Time in minutes before the authentication timeout for a user
    workstation: NotRequired[str]  # Name of the remote user workstation, if you want to limit th
    auth_concurrent_override: NotRequired[Literal[{"description": "Enable auth-concurrent-override", "help": "Enable auth-concurrent-override.", "label": "Enable", "name": "enable"}, {"description": "Disable auth-concurrent-override", "help": "Disable auth-concurrent-override.", "label": "Disable", "name": "disable"}]]  # Enable/disable overriding the policy-auth-concurrent under c
    auth_concurrent_value: NotRequired[int]  # Maximum number of concurrent logins permitted from the same 
    ppk_secret: NotRequired[str]  # IKEv2 Postquantum Preshared Key (ASCII string or hexadecimal
    ppk_identity: NotRequired[str]  # IKEv2 Postquantum Preshared Key Identity.
    qkd_profile: NotRequired[str]  # Quantum Key Distribution (QKD) profile.
    username_sensitivity: NotRequired[Literal[{"description": "Ignore case and accents", "help": "Ignore case and accents. Username at prompt not required to match case or accents.", "label": "Disable", "name": "disable"}, {"description": "Do not ignore case and accents", "help": "Do not ignore case and accents. Username at prompt must be an exact match.", "label": "Enable", "name": "enable"}]]  # Enable/disable case and accent sensitivity when performing u


class Local:
    """
    Configure local users.
    
    Path: user/local
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
        payload_dict: LocalPayload | None = ...,
        name: str | None = ...,
        id: int | None = ...,
        status: Literal[{"description": "Enable user", "help": "Enable user.", "label": "Enable", "name": "enable"}, {"description": "Disable user", "help": "Disable user.", "label": "Disable", "name": "disable"}] | None = ...,
        type: Literal[{"description": "Password authentication", "help": "Password authentication.", "label": "Password", "name": "password"}, {"description": "RADIUS server authentication", "help": "RADIUS server authentication.", "label": "Radius", "name": "radius"}, {"description": "TACACS+ server authentication", "help": "TACACS+ server authentication.", "label": "Tacacs+", "name": "tacacs+"}, {"description": "LDAP server authentication", "help": "LDAP server authentication.", "label": "Ldap", "name": "ldap"}, {"description": "SAML server authentication", "help": "SAML server authentication.", "label": "Saml", "name": "saml"}] | None = ...,
        passwd: str | None = ...,
        ldap_server: str | None = ...,
        radius_server: str | None = ...,
        tacacs_plus_server: str | None = ...,
        saml_server: str | None = ...,
        two_factor: Literal[{"description": "disable    fortitoken:FortiToken    fortitoken-cloud:FortiToken Cloud Service", "help": "disable", "label": "Disable", "name": "disable"}, {"help": "FortiToken", "label": "Fortitoken", "name": "fortitoken"}, {"help": "FortiToken Cloud Service.", "label": "Fortitoken Cloud", "name": "fortitoken-cloud"}, {"description": "Email authentication code", "help": "Email authentication code.", "label": "Email", "name": "email"}, {"description": "SMS authentication code", "help": "SMS authentication code.", "label": "Sms", "name": "sms"}] | None = ...,
        two_factor_authentication: Literal[{"description": "FortiToken authentication", "help": "FortiToken authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "Email one time password", "help": "Email one time password.", "label": "Email", "name": "email"}, {"description": "SMS one time password", "help": "SMS one time password.", "label": "Sms", "name": "sms"}] | None = ...,
        two_factor_notification: Literal[{"description": "Email notification for activation code", "help": "Email notification for activation code.", "label": "Email", "name": "email"}, {"description": "SMS notification for activation code", "help": "SMS notification for activation code.", "label": "Sms", "name": "sms"}] | None = ...,
        fortitoken: str | None = ...,
        email_to: str | None = ...,
        sms_server: Literal[{"description": "Send SMS by FortiGuard", "help": "Send SMS by FortiGuard.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Send SMS by custom server", "help": "Send SMS by custom server.", "label": "Custom", "name": "custom"}] | None = ...,
        sms_custom_server: str | None = ...,
        sms_phone: str | None = ...,
        passwd_policy: str | None = ...,
        passwd_time: str | None = ...,
        authtimeout: int | None = ...,
        workstation: str | None = ...,
        auth_concurrent_override: Literal[{"description": "Enable auth-concurrent-override", "help": "Enable auth-concurrent-override.", "label": "Enable", "name": "enable"}, {"description": "Disable auth-concurrent-override", "help": "Disable auth-concurrent-override.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_concurrent_value: int | None = ...,
        ppk_secret: str | None = ...,
        ppk_identity: str | None = ...,
        qkd_profile: str | None = ...,
        username_sensitivity: Literal[{"description": "Ignore case and accents", "help": "Ignore case and accents. Username at prompt not required to match case or accents.", "label": "Disable", "name": "disable"}, {"description": "Do not ignore case and accents", "help": "Do not ignore case and accents. Username at prompt must be an exact match.", "label": "Enable", "name": "enable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: LocalPayload | None = ...,
        name: str | None = ...,
        id: int | None = ...,
        status: Literal[{"description": "Enable user", "help": "Enable user.", "label": "Enable", "name": "enable"}, {"description": "Disable user", "help": "Disable user.", "label": "Disable", "name": "disable"}] | None = ...,
        type: Literal[{"description": "Password authentication", "help": "Password authentication.", "label": "Password", "name": "password"}, {"description": "RADIUS server authentication", "help": "RADIUS server authentication.", "label": "Radius", "name": "radius"}, {"description": "TACACS+ server authentication", "help": "TACACS+ server authentication.", "label": "Tacacs+", "name": "tacacs+"}, {"description": "LDAP server authentication", "help": "LDAP server authentication.", "label": "Ldap", "name": "ldap"}, {"description": "SAML server authentication", "help": "SAML server authentication.", "label": "Saml", "name": "saml"}] | None = ...,
        passwd: str | None = ...,
        ldap_server: str | None = ...,
        radius_server: str | None = ...,
        tacacs_plus_server: str | None = ...,
        saml_server: str | None = ...,
        two_factor: Literal[{"description": "disable    fortitoken:FortiToken    fortitoken-cloud:FortiToken Cloud Service", "help": "disable", "label": "Disable", "name": "disable"}, {"help": "FortiToken", "label": "Fortitoken", "name": "fortitoken"}, {"help": "FortiToken Cloud Service.", "label": "Fortitoken Cloud", "name": "fortitoken-cloud"}, {"description": "Email authentication code", "help": "Email authentication code.", "label": "Email", "name": "email"}, {"description": "SMS authentication code", "help": "SMS authentication code.", "label": "Sms", "name": "sms"}] | None = ...,
        two_factor_authentication: Literal[{"description": "FortiToken authentication", "help": "FortiToken authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "Email one time password", "help": "Email one time password.", "label": "Email", "name": "email"}, {"description": "SMS one time password", "help": "SMS one time password.", "label": "Sms", "name": "sms"}] | None = ...,
        two_factor_notification: Literal[{"description": "Email notification for activation code", "help": "Email notification for activation code.", "label": "Email", "name": "email"}, {"description": "SMS notification for activation code", "help": "SMS notification for activation code.", "label": "Sms", "name": "sms"}] | None = ...,
        fortitoken: str | None = ...,
        email_to: str | None = ...,
        sms_server: Literal[{"description": "Send SMS by FortiGuard", "help": "Send SMS by FortiGuard.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Send SMS by custom server", "help": "Send SMS by custom server.", "label": "Custom", "name": "custom"}] | None = ...,
        sms_custom_server: str | None = ...,
        sms_phone: str | None = ...,
        passwd_policy: str | None = ...,
        passwd_time: str | None = ...,
        authtimeout: int | None = ...,
        workstation: str | None = ...,
        auth_concurrent_override: Literal[{"description": "Enable auth-concurrent-override", "help": "Enable auth-concurrent-override.", "label": "Enable", "name": "enable"}, {"description": "Disable auth-concurrent-override", "help": "Disable auth-concurrent-override.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_concurrent_value: int | None = ...,
        ppk_secret: str | None = ...,
        ppk_identity: str | None = ...,
        qkd_profile: str | None = ...,
        username_sensitivity: Literal[{"description": "Ignore case and accents", "help": "Ignore case and accents. Username at prompt not required to match case or accents.", "label": "Disable", "name": "disable"}, {"description": "Do not ignore case and accents", "help": "Do not ignore case and accents. Username at prompt must be an exact match.", "label": "Enable", "name": "enable"}] | None = ...,
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
        payload_dict: LocalPayload | None = ...,
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
    "Local",
    "LocalPayload",
]