from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class AdminPayload(TypedDict, total=False):
    """
    Type hints for system/admin payload fields.
    
    Configure admin users.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.remote.RemoteEndpoint` (via: ssh-certificate)
        - :class:`~.system.accprofile.AccprofileEndpoint` (via: accprofile)
        - :class:`~.system.custom-language.CustomLanguageEndpoint` (via: guest-lang)
        - :class:`~.system.sms-server.SmsServerEndpoint` (via: sms-custom-server)

    **Usage:**
        payload: AdminPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # User name.
    vdom: NotRequired[list[dict[str, Any]]]  # Virtual domain(s) that the administrator can access.
    remote_auth: NotRequired[Literal[{"description": "Enable remote authentication", "help": "Enable remote authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable remote authentication", "help": "Disable remote authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable authentication using a remote RADIUS, LDAP, o
    remote_group: str  # User group name used for remote auth.
    wildcard: NotRequired[Literal[{"description": "Enable username wildcard", "help": "Enable username wildcard.", "label": "Enable", "name": "enable"}, {"description": "Disable username wildcard", "help": "Disable username wildcard.", "label": "Disable", "name": "disable"}]]  # Enable/disable wildcard RADIUS authentication.
    password: str  # Admin user password.
    peer_auth: NotRequired[Literal[{"description": "Enable peer", "help": "Enable peer.", "label": "Enable", "name": "enable"}, {"description": "Disable peer", "help": "Disable peer.", "label": "Disable", "name": "disable"}]]  # Set to enable peer certificate authentication (for HTTPS adm
    peer_group: str  # Name of peer group defined under config user group which has
    trusthost1: NotRequired[str]  # Any IPv4 address or subnet address and netmask from which th
    trusthost2: NotRequired[str]  # Any IPv4 address or subnet address and netmask from which th
    trusthost3: NotRequired[str]  # Any IPv4 address or subnet address and netmask from which th
    trusthost4: NotRequired[str]  # Any IPv4 address or subnet address and netmask from which th
    trusthost5: NotRequired[str]  # Any IPv4 address or subnet address and netmask from which th
    trusthost6: NotRequired[str]  # Any IPv4 address or subnet address and netmask from which th
    trusthost7: NotRequired[str]  # Any IPv4 address or subnet address and netmask from which th
    trusthost8: NotRequired[str]  # Any IPv4 address or subnet address and netmask from which th
    trusthost9: NotRequired[str]  # Any IPv4 address or subnet address and netmask from which th
    trusthost10: NotRequired[str]  # Any IPv4 address or subnet address and netmask from which th
    ip6_trusthost1: NotRequired[str]  # Any IPv6 address from which the administrator can connect to
    ip6_trusthost2: NotRequired[str]  # Any IPv6 address from which the administrator can connect to
    ip6_trusthost3: NotRequired[str]  # Any IPv6 address from which the administrator can connect to
    ip6_trusthost4: NotRequired[str]  # Any IPv6 address from which the administrator can connect to
    ip6_trusthost5: NotRequired[str]  # Any IPv6 address from which the administrator can connect to
    ip6_trusthost6: NotRequired[str]  # Any IPv6 address from which the administrator can connect to
    ip6_trusthost7: NotRequired[str]  # Any IPv6 address from which the administrator can connect to
    ip6_trusthost8: NotRequired[str]  # Any IPv6 address from which the administrator can connect to
    ip6_trusthost9: NotRequired[str]  # Any IPv6 address from which the administrator can connect to
    ip6_trusthost10: NotRequired[str]  # Any IPv6 address from which the administrator can connect to
    accprofile: NotRequired[str]  # Access profile for this administrator. Access profiles contr
    allow_remove_admin_session: NotRequired[Literal[{"description": "Enable allow-remove option", "help": "Enable allow-remove option.", "label": "Enable", "name": "enable"}, {"description": "Disable allow-remove option", "help": "Disable allow-remove option.", "label": "Disable", "name": "disable"}]]  # Enable/disable allow admin session to be removed by privileg
    comments: NotRequired[str]  # Comment.
    ssh_public_key1: NotRequired[str]  # Public key of an SSH client. The client is authenticated wit
    ssh_public_key2: NotRequired[str]  # Public key of an SSH client. The client is authenticated wit
    ssh_public_key3: NotRequired[str]  # Public key of an SSH client. The client is authenticated wit
    ssh_certificate: NotRequired[str]  # Select the certificate to be used by the FortiGate for authe
    schedule: NotRequired[str]  # Firewall schedule used to restrict when the administrator ca
    accprofile_override: NotRequired[Literal[{"description": "Enable access profile override", "help": "Enable access profile override.", "label": "Enable", "name": "enable"}, {"description": "Disable access profile override", "help": "Disable access profile override.", "label": "Disable", "name": "disable"}]]  # Enable to use the name of an access profile provided by the 
    vdom_override: NotRequired[Literal[{"description": "Enable VDOM override", "help": "Enable VDOM override.", "label": "Enable", "name": "enable"}, {"description": "Disable VDOM override", "help": "Disable VDOM override.", "label": "Disable", "name": "disable"}]]  # Enable to use the names of VDOMs provided by the remote auth
    password_expire: NotRequired[str]  # Password expire time.
    force_password_change: NotRequired[Literal[{"description": "Enable force password change on next login", "help": "Enable force password change on next login.", "label": "Enable", "name": "enable"}, {"description": "Disable force password change on next login", "help": "Disable force password change on next login.", "label": "Disable", "name": "disable"}]]  # Enable/disable force password change on next login.
    two_factor: NotRequired[Literal[{"description": "Disable two-factor authentication", "help": "Disable two-factor authentication.", "label": "Disable", "name": "disable"}, {"description": "Use FortiToken or FortiToken mobile two-factor authentication", "help": "Use FortiToken or FortiToken mobile two-factor authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "FortiToken Cloud Service", "help": "FortiToken Cloud Service.", "label": "Fortitoken Cloud", "name": "fortitoken-cloud"}, {"description": "Send a two-factor authentication code to the configured email-to email address", "help": "Send a two-factor authentication code to the configured email-to email address.", "label": "Email", "name": "email"}, {"description": "Send a two-factor authentication code to the configured sms-server and sms-phone", "help": "Send a two-factor authentication code to the configured sms-server and sms-phone.", "label": "Sms", "name": "sms"}]]  # Enable/disable two-factor authentication.
    two_factor_authentication: NotRequired[Literal[{"description": "FortiToken authentication", "help": "FortiToken authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "Email one time password", "help": "Email one time password.", "label": "Email", "name": "email"}, {"description": "SMS one time password", "help": "SMS one time password.", "label": "Sms", "name": "sms"}]]  # Authentication method by FortiToken Cloud.
    two_factor_notification: NotRequired[Literal[{"description": "Email notification for activation code", "help": "Email notification for activation code.", "label": "Email", "name": "email"}, {"description": "SMS notification for activation code", "help": "SMS notification for activation code.", "label": "Sms", "name": "sms"}]]  # Notification method for user activation by FortiToken Cloud.
    fortitoken: NotRequired[str]  # This administrator's FortiToken serial number.
    email_to: NotRequired[str]  # This administrator's email address.
    sms_server: NotRequired[Literal[{"description": "Send SMS by FortiGuard", "help": "Send SMS by FortiGuard.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Send SMS by custom server", "help": "Send SMS by custom server.", "label": "Custom", "name": "custom"}]]  # Send SMS messages using the FortiGuard SMS server or a custo
    sms_custom_server: NotRequired[str]  # Custom SMS server to send SMS messages to.
    sms_phone: NotRequired[str]  # Phone number on which the administrator receives SMS message
    guest_auth: NotRequired[Literal[{"description": "Disable guest authentication", "help": "Disable guest authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable guest authentication", "help": "Enable guest authentication.", "label": "Enable", "name": "enable"}]]  # Enable/disable guest authentication.
    guest_usergroups: NotRequired[list[dict[str, Any]]]  # Select guest user groups.
    guest_lang: NotRequired[str]  # Guest management portal language.
    status: NotRequired[str]  # print admin status information
    list: NotRequired[str]  # print admin list information


class Admin:
    """
    Configure admin users.
    
    Path: system/admin
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
        payload_dict: AdminPayload | None = ...,
        name: str | None = ...,
        remote_auth: Literal[{"description": "Enable remote authentication", "help": "Enable remote authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable remote authentication", "help": "Disable remote authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        remote_group: str | None = ...,
        wildcard: Literal[{"description": "Enable username wildcard", "help": "Enable username wildcard.", "label": "Enable", "name": "enable"}, {"description": "Disable username wildcard", "help": "Disable username wildcard.", "label": "Disable", "name": "disable"}] | None = ...,
        password: str | None = ...,
        peer_auth: Literal[{"description": "Enable peer", "help": "Enable peer.", "label": "Enable", "name": "enable"}, {"description": "Disable peer", "help": "Disable peer.", "label": "Disable", "name": "disable"}] | None = ...,
        peer_group: str | None = ...,
        trusthost1: str | None = ...,
        trusthost2: str | None = ...,
        trusthost3: str | None = ...,
        trusthost4: str | None = ...,
        trusthost5: str | None = ...,
        trusthost6: str | None = ...,
        trusthost7: str | None = ...,
        trusthost8: str | None = ...,
        trusthost9: str | None = ...,
        trusthost10: str | None = ...,
        ip6_trusthost1: str | None = ...,
        ip6_trusthost2: str | None = ...,
        ip6_trusthost3: str | None = ...,
        ip6_trusthost4: str | None = ...,
        ip6_trusthost5: str | None = ...,
        ip6_trusthost6: str | None = ...,
        ip6_trusthost7: str | None = ...,
        ip6_trusthost8: str | None = ...,
        ip6_trusthost9: str | None = ...,
        ip6_trusthost10: str | None = ...,
        accprofile: str | None = ...,
        allow_remove_admin_session: Literal[{"description": "Enable allow-remove option", "help": "Enable allow-remove option.", "label": "Enable", "name": "enable"}, {"description": "Disable allow-remove option", "help": "Disable allow-remove option.", "label": "Disable", "name": "disable"}] | None = ...,
        comments: str | None = ...,
        ssh_public_key1: str | None = ...,
        ssh_public_key2: str | None = ...,
        ssh_public_key3: str | None = ...,
        ssh_certificate: str | None = ...,
        schedule: str | None = ...,
        accprofile_override: Literal[{"description": "Enable access profile override", "help": "Enable access profile override.", "label": "Enable", "name": "enable"}, {"description": "Disable access profile override", "help": "Disable access profile override.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom_override: Literal[{"description": "Enable VDOM override", "help": "Enable VDOM override.", "label": "Enable", "name": "enable"}, {"description": "Disable VDOM override", "help": "Disable VDOM override.", "label": "Disable", "name": "disable"}] | None = ...,
        password_expire: str | None = ...,
        force_password_change: Literal[{"description": "Enable force password change on next login", "help": "Enable force password change on next login.", "label": "Enable", "name": "enable"}, {"description": "Disable force password change on next login", "help": "Disable force password change on next login.", "label": "Disable", "name": "disable"}] | None = ...,
        two_factor: Literal[{"description": "Disable two-factor authentication", "help": "Disable two-factor authentication.", "label": "Disable", "name": "disable"}, {"description": "Use FortiToken or FortiToken mobile two-factor authentication", "help": "Use FortiToken or FortiToken mobile two-factor authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "FortiToken Cloud Service", "help": "FortiToken Cloud Service.", "label": "Fortitoken Cloud", "name": "fortitoken-cloud"}, {"description": "Send a two-factor authentication code to the configured email-to email address", "help": "Send a two-factor authentication code to the configured email-to email address.", "label": "Email", "name": "email"}, {"description": "Send a two-factor authentication code to the configured sms-server and sms-phone", "help": "Send a two-factor authentication code to the configured sms-server and sms-phone.", "label": "Sms", "name": "sms"}] | None = ...,
        two_factor_authentication: Literal[{"description": "FortiToken authentication", "help": "FortiToken authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "Email one time password", "help": "Email one time password.", "label": "Email", "name": "email"}, {"description": "SMS one time password", "help": "SMS one time password.", "label": "Sms", "name": "sms"}] | None = ...,
        two_factor_notification: Literal[{"description": "Email notification for activation code", "help": "Email notification for activation code.", "label": "Email", "name": "email"}, {"description": "SMS notification for activation code", "help": "SMS notification for activation code.", "label": "Sms", "name": "sms"}] | None = ...,
        fortitoken: str | None = ...,
        email_to: str | None = ...,
        sms_server: Literal[{"description": "Send SMS by FortiGuard", "help": "Send SMS by FortiGuard.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Send SMS by custom server", "help": "Send SMS by custom server.", "label": "Custom", "name": "custom"}] | None = ...,
        sms_custom_server: str | None = ...,
        sms_phone: str | None = ...,
        guest_auth: Literal[{"description": "Disable guest authentication", "help": "Disable guest authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable guest authentication", "help": "Enable guest authentication.", "label": "Enable", "name": "enable"}] | None = ...,
        guest_usergroups: list[dict[str, Any]] | None = ...,
        guest_lang: str | None = ...,
        status: str | None = ...,
        list: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: AdminPayload | None = ...,
        name: str | None = ...,
        remote_auth: Literal[{"description": "Enable remote authentication", "help": "Enable remote authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable remote authentication", "help": "Disable remote authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        remote_group: str | None = ...,
        wildcard: Literal[{"description": "Enable username wildcard", "help": "Enable username wildcard.", "label": "Enable", "name": "enable"}, {"description": "Disable username wildcard", "help": "Disable username wildcard.", "label": "Disable", "name": "disable"}] | None = ...,
        password: str | None = ...,
        peer_auth: Literal[{"description": "Enable peer", "help": "Enable peer.", "label": "Enable", "name": "enable"}, {"description": "Disable peer", "help": "Disable peer.", "label": "Disable", "name": "disable"}] | None = ...,
        peer_group: str | None = ...,
        trusthost1: str | None = ...,
        trusthost2: str | None = ...,
        trusthost3: str | None = ...,
        trusthost4: str | None = ...,
        trusthost5: str | None = ...,
        trusthost6: str | None = ...,
        trusthost7: str | None = ...,
        trusthost8: str | None = ...,
        trusthost9: str | None = ...,
        trusthost10: str | None = ...,
        ip6_trusthost1: str | None = ...,
        ip6_trusthost2: str | None = ...,
        ip6_trusthost3: str | None = ...,
        ip6_trusthost4: str | None = ...,
        ip6_trusthost5: str | None = ...,
        ip6_trusthost6: str | None = ...,
        ip6_trusthost7: str | None = ...,
        ip6_trusthost8: str | None = ...,
        ip6_trusthost9: str | None = ...,
        ip6_trusthost10: str | None = ...,
        accprofile: str | None = ...,
        allow_remove_admin_session: Literal[{"description": "Enable allow-remove option", "help": "Enable allow-remove option.", "label": "Enable", "name": "enable"}, {"description": "Disable allow-remove option", "help": "Disable allow-remove option.", "label": "Disable", "name": "disable"}] | None = ...,
        comments: str | None = ...,
        ssh_public_key1: str | None = ...,
        ssh_public_key2: str | None = ...,
        ssh_public_key3: str | None = ...,
        ssh_certificate: str | None = ...,
        schedule: str | None = ...,
        accprofile_override: Literal[{"description": "Enable access profile override", "help": "Enable access profile override.", "label": "Enable", "name": "enable"}, {"description": "Disable access profile override", "help": "Disable access profile override.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom_override: Literal[{"description": "Enable VDOM override", "help": "Enable VDOM override.", "label": "Enable", "name": "enable"}, {"description": "Disable VDOM override", "help": "Disable VDOM override.", "label": "Disable", "name": "disable"}] | None = ...,
        password_expire: str | None = ...,
        force_password_change: Literal[{"description": "Enable force password change on next login", "help": "Enable force password change on next login.", "label": "Enable", "name": "enable"}, {"description": "Disable force password change on next login", "help": "Disable force password change on next login.", "label": "Disable", "name": "disable"}] | None = ...,
        two_factor: Literal[{"description": "Disable two-factor authentication", "help": "Disable two-factor authentication.", "label": "Disable", "name": "disable"}, {"description": "Use FortiToken or FortiToken mobile two-factor authentication", "help": "Use FortiToken or FortiToken mobile two-factor authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "FortiToken Cloud Service", "help": "FortiToken Cloud Service.", "label": "Fortitoken Cloud", "name": "fortitoken-cloud"}, {"description": "Send a two-factor authentication code to the configured email-to email address", "help": "Send a two-factor authentication code to the configured email-to email address.", "label": "Email", "name": "email"}, {"description": "Send a two-factor authentication code to the configured sms-server and sms-phone", "help": "Send a two-factor authentication code to the configured sms-server and sms-phone.", "label": "Sms", "name": "sms"}] | None = ...,
        two_factor_authentication: Literal[{"description": "FortiToken authentication", "help": "FortiToken authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "Email one time password", "help": "Email one time password.", "label": "Email", "name": "email"}, {"description": "SMS one time password", "help": "SMS one time password.", "label": "Sms", "name": "sms"}] | None = ...,
        two_factor_notification: Literal[{"description": "Email notification for activation code", "help": "Email notification for activation code.", "label": "Email", "name": "email"}, {"description": "SMS notification for activation code", "help": "SMS notification for activation code.", "label": "Sms", "name": "sms"}] | None = ...,
        fortitoken: str | None = ...,
        email_to: str | None = ...,
        sms_server: Literal[{"description": "Send SMS by FortiGuard", "help": "Send SMS by FortiGuard.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Send SMS by custom server", "help": "Send SMS by custom server.", "label": "Custom", "name": "custom"}] | None = ...,
        sms_custom_server: str | None = ...,
        sms_phone: str | None = ...,
        guest_auth: Literal[{"description": "Disable guest authentication", "help": "Disable guest authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable guest authentication", "help": "Enable guest authentication.", "label": "Enable", "name": "enable"}] | None = ...,
        guest_usergroups: list[dict[str, Any]] | None = ...,
        guest_lang: str | None = ...,
        status: str | None = ...,
        list: str | None = ...,
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
        payload_dict: AdminPayload | None = ...,
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
    "Admin",
    "AdminPayload",
]