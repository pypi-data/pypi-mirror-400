from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class GroupPayload(TypedDict, total=False):
    """
    Type hints for user/group payload fields.
    
    Configure user groups.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.sms-server.SmsServerEndpoint` (via: sms-custom-server)

    **Usage:**
        payload: GroupPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Group name.
    id: NotRequired[int]  # Group ID.
    group_type: NotRequired[Literal[{"description": "Firewall", "help": "Firewall.", "label": "Firewall", "name": "firewall"}, {"description": "Fortinet Single Sign-On Service", "help": "Fortinet Single Sign-On Service.", "label": "Fsso Service", "name": "fsso-service"}, {"description": "RADIUS based Single Sign-On Service", "help": "RADIUS based Single Sign-On Service.", "label": "Rsso", "name": "rsso"}, {"description": "Guest", "help": "Guest.", "label": "Guest", "name": "guest"}]]  # Set the group to be for firewall authentication, FSSO, RSSO,
    authtimeout: NotRequired[int]  # Authentication timeout in minutes for this user group. 0 to 
    auth_concurrent_override: NotRequired[Literal[{"description": "Enable auth-concurrent-override", "help": "Enable auth-concurrent-override.", "label": "Enable", "name": "enable"}, {"description": "Disable auth-concurrent-override", "help": "Disable auth-concurrent-override.", "label": "Disable", "name": "disable"}]]  # Enable/disable overriding the global number of concurrent au
    auth_concurrent_value: NotRequired[int]  # Maximum number of concurrent authenticated connections per u
    http_digest_realm: NotRequired[str]  # Realm attribute for MD5-digest authentication.
    sso_attribute_value: NotRequired[str]  # RADIUS attribute value.
    member: NotRequired[list[dict[str, Any]]]  # Names of users, peers, LDAP severs, RADIUS servers or extern
    match: NotRequired[list[dict[str, Any]]]  # Group matches.
    user_id: NotRequired[Literal[{"description": "Email address", "help": "Email address.", "label": "Email", "name": "email"}, {"description": "Automatically generate", "help": "Automatically generate.", "label": "Auto Generate", "name": "auto-generate"}, {"description": "Specify", "help": "Specify.", "label": "Specify", "name": "specify"}]]  # Guest user ID type.
    password: NotRequired[Literal[{"description": "Automatically generate", "help": "Automatically generate.", "label": "Auto Generate", "name": "auto-generate"}, {"description": "Specify", "help": "Specify.", "label": "Specify", "name": "specify"}, {"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}]]  # Guest user password type.
    user_name: NotRequired[Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}]]  # Enable/disable the guest user name entry.
    sponsor: NotRequired[Literal[{"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Disabled", "help": "Disabled.", "label": "Disabled", "name": "disabled"}]]  # Set the action for the sponsor guest user field.
    company: NotRequired[Literal[{"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Disabled", "help": "Disabled.", "label": "Disabled", "name": "disabled"}]]  # Set the action for the company guest user field.
    email: NotRequired[Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}]]  # Enable/disable the guest user email address field.
    mobile_phone: NotRequired[Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}]]  # Enable/disable the guest user mobile phone number field.
    sms_server: NotRequired[Literal[{"description": "Send SMS by FortiGuard", "help": "Send SMS by FortiGuard.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Send SMS by custom server", "help": "Send SMS by custom server.", "label": "Custom", "name": "custom"}]]  # Send SMS through FortiGuard or other external server.
    sms_custom_server: NotRequired[str]  # SMS server.
    expire_type: NotRequired[Literal[{"description": "Immediately", "help": "Immediately.", "label": "Immediately", "name": "immediately"}, {"description": "First successful login", "help": "First successful login.", "label": "First Successful Login", "name": "first-successful-login"}]]  # Determine when the expiration countdown begins.
    expire: NotRequired[int]  # Time in seconds before guest user accounts expire (1 - 31536
    max_accounts: NotRequired[int]  # Maximum number of guest accounts that can be created for thi
    multiple_guest_add: NotRequired[Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}]]  # Enable/disable addition of multiple guests.
    guest: NotRequired[list[dict[str, Any]]]  # Guest User.


class Group:
    """
    Configure user groups.
    
    Path: user/group
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
        payload_dict: GroupPayload | None = ...,
        name: str | None = ...,
        id: int | None = ...,
        group_type: Literal[{"description": "Firewall", "help": "Firewall.", "label": "Firewall", "name": "firewall"}, {"description": "Fortinet Single Sign-On Service", "help": "Fortinet Single Sign-On Service.", "label": "Fsso Service", "name": "fsso-service"}, {"description": "RADIUS based Single Sign-On Service", "help": "RADIUS based Single Sign-On Service.", "label": "Rsso", "name": "rsso"}, {"description": "Guest", "help": "Guest.", "label": "Guest", "name": "guest"}] | None = ...,
        authtimeout: int | None = ...,
        auth_concurrent_override: Literal[{"description": "Enable auth-concurrent-override", "help": "Enable auth-concurrent-override.", "label": "Enable", "name": "enable"}, {"description": "Disable auth-concurrent-override", "help": "Disable auth-concurrent-override.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_concurrent_value: int | None = ...,
        http_digest_realm: str | None = ...,
        sso_attribute_value: str | None = ...,
        member: list[dict[str, Any]] | None = ...,
        match: list[dict[str, Any]] | None = ...,
        user_id: Literal[{"description": "Email address", "help": "Email address.", "label": "Email", "name": "email"}, {"description": "Automatically generate", "help": "Automatically generate.", "label": "Auto Generate", "name": "auto-generate"}, {"description": "Specify", "help": "Specify.", "label": "Specify", "name": "specify"}] | None = ...,
        password: Literal[{"description": "Automatically generate", "help": "Automatically generate.", "label": "Auto Generate", "name": "auto-generate"}, {"description": "Specify", "help": "Specify.", "label": "Specify", "name": "specify"}, {"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}] | None = ...,
        user_name: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}] | None = ...,
        sponsor: Literal[{"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Disabled", "help": "Disabled.", "label": "Disabled", "name": "disabled"}] | None = ...,
        company: Literal[{"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Disabled", "help": "Disabled.", "label": "Disabled", "name": "disabled"}] | None = ...,
        email: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}] | None = ...,
        mobile_phone: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}] | None = ...,
        sms_server: Literal[{"description": "Send SMS by FortiGuard", "help": "Send SMS by FortiGuard.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Send SMS by custom server", "help": "Send SMS by custom server.", "label": "Custom", "name": "custom"}] | None = ...,
        sms_custom_server: str | None = ...,
        expire_type: Literal[{"description": "Immediately", "help": "Immediately.", "label": "Immediately", "name": "immediately"}, {"description": "First successful login", "help": "First successful login.", "label": "First Successful Login", "name": "first-successful-login"}] | None = ...,
        expire: int | None = ...,
        max_accounts: int | None = ...,
        multiple_guest_add: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}] | None = ...,
        guest: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: GroupPayload | None = ...,
        name: str | None = ...,
        id: int | None = ...,
        group_type: Literal[{"description": "Firewall", "help": "Firewall.", "label": "Firewall", "name": "firewall"}, {"description": "Fortinet Single Sign-On Service", "help": "Fortinet Single Sign-On Service.", "label": "Fsso Service", "name": "fsso-service"}, {"description": "RADIUS based Single Sign-On Service", "help": "RADIUS based Single Sign-On Service.", "label": "Rsso", "name": "rsso"}, {"description": "Guest", "help": "Guest.", "label": "Guest", "name": "guest"}] | None = ...,
        authtimeout: int | None = ...,
        auth_concurrent_override: Literal[{"description": "Enable auth-concurrent-override", "help": "Enable auth-concurrent-override.", "label": "Enable", "name": "enable"}, {"description": "Disable auth-concurrent-override", "help": "Disable auth-concurrent-override.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_concurrent_value: int | None = ...,
        http_digest_realm: str | None = ...,
        sso_attribute_value: str | None = ...,
        member: list[dict[str, Any]] | None = ...,
        match: list[dict[str, Any]] | None = ...,
        user_id: Literal[{"description": "Email address", "help": "Email address.", "label": "Email", "name": "email"}, {"description": "Automatically generate", "help": "Automatically generate.", "label": "Auto Generate", "name": "auto-generate"}, {"description": "Specify", "help": "Specify.", "label": "Specify", "name": "specify"}] | None = ...,
        password: Literal[{"description": "Automatically generate", "help": "Automatically generate.", "label": "Auto Generate", "name": "auto-generate"}, {"description": "Specify", "help": "Specify.", "label": "Specify", "name": "specify"}, {"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}] | None = ...,
        user_name: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}] | None = ...,
        sponsor: Literal[{"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Disabled", "help": "Disabled.", "label": "Disabled", "name": "disabled"}] | None = ...,
        company: Literal[{"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Disabled", "help": "Disabled.", "label": "Disabled", "name": "disabled"}] | None = ...,
        email: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}] | None = ...,
        mobile_phone: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}] | None = ...,
        sms_server: Literal[{"description": "Send SMS by FortiGuard", "help": "Send SMS by FortiGuard.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Send SMS by custom server", "help": "Send SMS by custom server.", "label": "Custom", "name": "custom"}] | None = ...,
        sms_custom_server: str | None = ...,
        expire_type: Literal[{"description": "Immediately", "help": "Immediately.", "label": "Immediately", "name": "immediately"}, {"description": "First successful login", "help": "First successful login.", "label": "First Successful Login", "name": "first-successful-login"}] | None = ...,
        expire: int | None = ...,
        max_accounts: int | None = ...,
        multiple_guest_add: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}] | None = ...,
        guest: list[dict[str, Any]] | None = ...,
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
        payload_dict: GroupPayload | None = ...,
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
    "Group",
    "GroupPayload",
]