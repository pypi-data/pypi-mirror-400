from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class PeerPayload(TypedDict, total=False):
    """
    Type hints for user/peer payload fields.
    
    Configure peer users.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.user.ldap.LdapEndpoint` (via: mfa-server)
        - :class:`~.user.radius.RadiusEndpoint` (via: mfa-server)
        - :class:`~.vpn.certificate.ca.CaEndpoint` (via: ca)
        - :class:`~.vpn.certificate.ocsp-server.OcspServerEndpoint` (via: ocsp-override-server)

    **Usage:**
        payload: PeerPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Peer name.
    mandatory_ca_verify: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Determine what happens to the peer if the CA certificate is 
    ca: NotRequired[str]  # Name of the CA certificate.
    subject: NotRequired[str]  # Peer certificate name constraints.
    cn: NotRequired[str]  # Peer certificate common name.
    cn_type: NotRequired[Literal[{"description": "Normal string", "help": "Normal string.", "label": "String", "name": "string"}, {"description": "Email address", "help": "Email address.", "label": "Email", "name": "email"}, {"description": "Fully Qualified Domain Name", "help": "Fully Qualified Domain Name.", "label": "Fqdn", "name": "FQDN"}, {"description": "IPv4 address", "help": "IPv4 address.", "label": "Ipv4", "name": "ipv4"}, {"description": "IPv6 address", "help": "IPv6 address.", "label": "Ipv6", "name": "ipv6"}]]  # Peer certificate common name type.
    mfa_mode: NotRequired[Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "Specified username/password", "help": "Specified username/password.", "label": "Password", "name": "password"}, {"description": "Subject identity extracted from certificate", "help": "Subject identity extracted from certificate.", "label": "Subject Identity", "name": "subject-identity"}]]  # MFA mode for remote peer authentication/authorization.
    mfa_server: NotRequired[str]  # Name of a remote authenticator. Performs client access right
    mfa_username: NotRequired[str]  # Unified username for remote authentication.
    mfa_password: NotRequired[str]  # Unified password for remote authentication. This field may b
    ocsp_override_server: NotRequired[str]  # Online Certificate Status Protocol (OCSP) server for certifi
    two_factor: NotRequired[Literal[{"description": "Enable 2-factor authentication", "help": "Enable 2-factor authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable 2-factor authentication", "help": "Disable 2-factor authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable two-factor authentication, applying certifica
    passwd: NotRequired[str]  # Peer's password used for two-factor authentication.


class Peer:
    """
    Configure peer users.
    
    Path: user/peer
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
        payload_dict: PeerPayload | None = ...,
        name: str | None = ...,
        mandatory_ca_verify: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ca: str | None = ...,
        subject: str | None = ...,
        cn: str | None = ...,
        cn_type: Literal[{"description": "Normal string", "help": "Normal string.", "label": "String", "name": "string"}, {"description": "Email address", "help": "Email address.", "label": "Email", "name": "email"}, {"description": "Fully Qualified Domain Name", "help": "Fully Qualified Domain Name.", "label": "Fqdn", "name": "FQDN"}, {"description": "IPv4 address", "help": "IPv4 address.", "label": "Ipv4", "name": "ipv4"}, {"description": "IPv6 address", "help": "IPv6 address.", "label": "Ipv6", "name": "ipv6"}] | None = ...,
        mfa_mode: Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "Specified username/password", "help": "Specified username/password.", "label": "Password", "name": "password"}, {"description": "Subject identity extracted from certificate", "help": "Subject identity extracted from certificate.", "label": "Subject Identity", "name": "subject-identity"}] | None = ...,
        mfa_server: str | None = ...,
        mfa_username: str | None = ...,
        mfa_password: str | None = ...,
        ocsp_override_server: str | None = ...,
        two_factor: Literal[{"description": "Enable 2-factor authentication", "help": "Enable 2-factor authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable 2-factor authentication", "help": "Disable 2-factor authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        passwd: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: PeerPayload | None = ...,
        name: str | None = ...,
        mandatory_ca_verify: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ca: str | None = ...,
        subject: str | None = ...,
        cn: str | None = ...,
        cn_type: Literal[{"description": "Normal string", "help": "Normal string.", "label": "String", "name": "string"}, {"description": "Email address", "help": "Email address.", "label": "Email", "name": "email"}, {"description": "Fully Qualified Domain Name", "help": "Fully Qualified Domain Name.", "label": "Fqdn", "name": "FQDN"}, {"description": "IPv4 address", "help": "IPv4 address.", "label": "Ipv4", "name": "ipv4"}, {"description": "IPv6 address", "help": "IPv6 address.", "label": "Ipv6", "name": "ipv6"}] | None = ...,
        mfa_mode: Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "Specified username/password", "help": "Specified username/password.", "label": "Password", "name": "password"}, {"description": "Subject identity extracted from certificate", "help": "Subject identity extracted from certificate.", "label": "Subject Identity", "name": "subject-identity"}] | None = ...,
        mfa_server: str | None = ...,
        mfa_username: str | None = ...,
        mfa_password: str | None = ...,
        ocsp_override_server: str | None = ...,
        two_factor: Literal[{"description": "Enable 2-factor authentication", "help": "Enable 2-factor authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable 2-factor authentication", "help": "Disable 2-factor authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        passwd: str | None = ...,
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
        payload_dict: PeerPayload | None = ...,
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
    "Peer",
    "PeerPayload",
]