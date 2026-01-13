from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SchemePayload(TypedDict, total=False):
    """
    Type hints for authentication/scheme payload fields.
    
    Configure Authentication Schemes.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.firewall.ssh.local-ca.LocalCaEndpoint` (via: ssh-ca)
        - :class:`~.user.domain-controller.DomainControllerEndpoint` (via: domain-controller)
        - :class:`~.user.external-identity-provider.ExternalIdentityProviderEndpoint` (via: external-idp)
        - :class:`~.user.fsso.FssoEndpoint` (via: fsso-agent-for-ntlm)
        - :class:`~.user.krb-keytab.KrbKeytabEndpoint` (via: kerberos-keytab)
        - :class:`~.user.saml.SamlEndpoint` (via: saml-server)

    **Usage:**
        payload: SchemePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Authentication scheme name.
    method: Literal[{"description": "NTLM authentication", "help": "NTLM authentication.", "label": "Ntlm", "name": "ntlm"}, {"description": "Basic HTTP authentication", "help": "Basic HTTP authentication.", "label": "Basic", "name": "basic"}, {"description": "Digest HTTP authentication", "help": "Digest HTTP authentication.", "label": "Digest", "name": "digest"}, {"description": "Form-based HTTP authentication", "help": "Form-based HTTP authentication.", "label": "Form", "name": "form"}, {"description": "Negotiate authentication", "help": "Negotiate authentication.", "label": "Negotiate", "name": "negotiate"}, {"description": "Fortinet Single Sign-On (FSSO) authentication", "help": "Fortinet Single Sign-On (FSSO) authentication.", "label": "Fsso", "name": "fsso"}, {"description": "RADIUS Single Sign-On (RSSO) authentication", "help": "RADIUS Single Sign-On (RSSO) authentication.", "label": "Rsso", "name": "rsso"}, {"description": "Public key based SSH authentication", "help": "Public key based SSH authentication.", "label": "Ssh Publickey", "name": "ssh-publickey"}, {"description": "Client certificate authentication", "help": "Client certificate authentication.", "label": "Cert", "name": "cert"}, {"description": "SAML authentication", "help": "SAML authentication.", "label": "Saml", "name": "saml"}, {"description": "Entra ID based Single Sign-On (SSO) authentication", "help": "Entra ID based Single Sign-On (SSO) authentication.", "label": "Entra Sso", "name": "entra-sso"}]  # Authentication methods (default = basic).
    negotiate_ntlm: NotRequired[Literal[{"description": "Enable negotiate authentication for NTLM", "help": "Enable negotiate authentication for NTLM.", "label": "Enable", "name": "enable"}, {"description": "Disable negotiate authentication for NTLM", "help": "Disable negotiate authentication for NTLM.", "label": "Disable", "name": "disable"}]]  # Enable/disable negotiate authentication for NTLM (default = 
    kerberos_keytab: NotRequired[str]  # Kerberos keytab setting.
    domain_controller: NotRequired[str]  # Domain controller setting.
    saml_server: NotRequired[str]  # SAML configuration.
    saml_timeout: NotRequired[int]  # SAML authentication timeout in seconds.
    fsso_agent_for_ntlm: NotRequired[str]  # FSSO agent to use for NTLM authentication.
    require_tfa: NotRequired[Literal[{"description": "Enable two-factor authentication", "help": "Enable two-factor authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable two-factor authentication", "help": "Disable two-factor authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable two-factor authentication (default = disable)
    fsso_guest: NotRequired[Literal[{"description": "Enable user fsso-guest authentication", "help": "Enable user fsso-guest authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable user fsso-guest authentication", "help": "Disable user fsso-guest authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable user fsso-guest authentication (default = dis
    user_cert: NotRequired[Literal[{"description": "Enable client certificate field authentication", "help": "Enable client certificate field authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable client certificate field authentication", "help": "Disable client certificate field authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable authentication with user certificate (default
    cert_http_header: NotRequired[Literal[{"description": "Enable client certificate authentication with HTTP header (RFC9440)", "help": "Enable client certificate authentication with HTTP header (RFC9440).", "label": "Enable", "name": "enable"}, {"description": "Disable client certificate authentication with HTTP header (RFC9440)", "help": "Disable client certificate authentication with HTTP header (RFC9440).", "label": "Disable", "name": "disable"}]]  # Enable/disable authentication with user certificate in Clien
    user_database: NotRequired[list[dict[str, Any]]]  # Authentication server to contain user information; "local-us
    ssh_ca: NotRequired[str]  # SSH CA name.
    external_idp: NotRequired[str]  # External identity provider configuration.
    group_attr_type: NotRequired[Literal[{"description": "Display name", "help": "Display name.", "label": "Display Name", "name": "display-name"}, {"description": "External ID", "help": "External ID.", "label": "External Id", "name": "external-id"}]]  # Group attribute type used to match SCIM groups (default = di
    digest_algo: NotRequired[Literal[{"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}, {"description": "SHA-256", "help": "SHA-256.", "label": "Sha 256", "name": "sha-256"}]]  # Digest Authentication Algorithms.
    digest_rfc2069: NotRequired[Literal[{"description": "Enable support for the deprecated RFC2069 Digest Client (no cnonce field)", "help": "Enable support for the deprecated RFC2069 Digest Client (no cnonce field).", "label": "Enable", "name": "enable"}, {"description": "Disable support for the deprecated RFC2069 Digest Client (no cnonce field)", "help": "Disable support for the deprecated RFC2069 Digest Client (no cnonce field).", "label": "Disable", "name": "disable"}]]  # Enable/disable support for the deprecated RFC2069 Digest Cli


class Scheme:
    """
    Configure Authentication Schemes.
    
    Path: authentication/scheme
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
        payload_dict: SchemePayload | None = ...,
        name: str | None = ...,
        method: Literal[{"description": "NTLM authentication", "help": "NTLM authentication.", "label": "Ntlm", "name": "ntlm"}, {"description": "Basic HTTP authentication", "help": "Basic HTTP authentication.", "label": "Basic", "name": "basic"}, {"description": "Digest HTTP authentication", "help": "Digest HTTP authentication.", "label": "Digest", "name": "digest"}, {"description": "Form-based HTTP authentication", "help": "Form-based HTTP authentication.", "label": "Form", "name": "form"}, {"description": "Negotiate authentication", "help": "Negotiate authentication.", "label": "Negotiate", "name": "negotiate"}, {"description": "Fortinet Single Sign-On (FSSO) authentication", "help": "Fortinet Single Sign-On (FSSO) authentication.", "label": "Fsso", "name": "fsso"}, {"description": "RADIUS Single Sign-On (RSSO) authentication", "help": "RADIUS Single Sign-On (RSSO) authentication.", "label": "Rsso", "name": "rsso"}, {"description": "Public key based SSH authentication", "help": "Public key based SSH authentication.", "label": "Ssh Publickey", "name": "ssh-publickey"}, {"description": "Client certificate authentication", "help": "Client certificate authentication.", "label": "Cert", "name": "cert"}, {"description": "SAML authentication", "help": "SAML authentication.", "label": "Saml", "name": "saml"}, {"description": "Entra ID based Single Sign-On (SSO) authentication", "help": "Entra ID based Single Sign-On (SSO) authentication.", "label": "Entra Sso", "name": "entra-sso"}] | None = ...,
        negotiate_ntlm: Literal[{"description": "Enable negotiate authentication for NTLM", "help": "Enable negotiate authentication for NTLM.", "label": "Enable", "name": "enable"}, {"description": "Disable negotiate authentication for NTLM", "help": "Disable negotiate authentication for NTLM.", "label": "Disable", "name": "disable"}] | None = ...,
        kerberos_keytab: str | None = ...,
        domain_controller: str | None = ...,
        saml_server: str | None = ...,
        saml_timeout: int | None = ...,
        fsso_agent_for_ntlm: str | None = ...,
        require_tfa: Literal[{"description": "Enable two-factor authentication", "help": "Enable two-factor authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable two-factor authentication", "help": "Disable two-factor authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        fsso_guest: Literal[{"description": "Enable user fsso-guest authentication", "help": "Enable user fsso-guest authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable user fsso-guest authentication", "help": "Disable user fsso-guest authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        user_cert: Literal[{"description": "Enable client certificate field authentication", "help": "Enable client certificate field authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable client certificate field authentication", "help": "Disable client certificate field authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        cert_http_header: Literal[{"description": "Enable client certificate authentication with HTTP header (RFC9440)", "help": "Enable client certificate authentication with HTTP header (RFC9440).", "label": "Enable", "name": "enable"}, {"description": "Disable client certificate authentication with HTTP header (RFC9440)", "help": "Disable client certificate authentication with HTTP header (RFC9440).", "label": "Disable", "name": "disable"}] | None = ...,
        user_database: list[dict[str, Any]] | None = ...,
        ssh_ca: str | None = ...,
        external_idp: str | None = ...,
        group_attr_type: Literal[{"description": "Display name", "help": "Display name.", "label": "Display Name", "name": "display-name"}, {"description": "External ID", "help": "External ID.", "label": "External Id", "name": "external-id"}] | None = ...,
        digest_algo: Literal[{"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}, {"description": "SHA-256", "help": "SHA-256.", "label": "Sha 256", "name": "sha-256"}] | None = ...,
        digest_rfc2069: Literal[{"description": "Enable support for the deprecated RFC2069 Digest Client (no cnonce field)", "help": "Enable support for the deprecated RFC2069 Digest Client (no cnonce field).", "label": "Enable", "name": "enable"}, {"description": "Disable support for the deprecated RFC2069 Digest Client (no cnonce field)", "help": "Disable support for the deprecated RFC2069 Digest Client (no cnonce field).", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SchemePayload | None = ...,
        name: str | None = ...,
        method: Literal[{"description": "NTLM authentication", "help": "NTLM authentication.", "label": "Ntlm", "name": "ntlm"}, {"description": "Basic HTTP authentication", "help": "Basic HTTP authentication.", "label": "Basic", "name": "basic"}, {"description": "Digest HTTP authentication", "help": "Digest HTTP authentication.", "label": "Digest", "name": "digest"}, {"description": "Form-based HTTP authentication", "help": "Form-based HTTP authentication.", "label": "Form", "name": "form"}, {"description": "Negotiate authentication", "help": "Negotiate authentication.", "label": "Negotiate", "name": "negotiate"}, {"description": "Fortinet Single Sign-On (FSSO) authentication", "help": "Fortinet Single Sign-On (FSSO) authentication.", "label": "Fsso", "name": "fsso"}, {"description": "RADIUS Single Sign-On (RSSO) authentication", "help": "RADIUS Single Sign-On (RSSO) authentication.", "label": "Rsso", "name": "rsso"}, {"description": "Public key based SSH authentication", "help": "Public key based SSH authentication.", "label": "Ssh Publickey", "name": "ssh-publickey"}, {"description": "Client certificate authentication", "help": "Client certificate authentication.", "label": "Cert", "name": "cert"}, {"description": "SAML authentication", "help": "SAML authentication.", "label": "Saml", "name": "saml"}, {"description": "Entra ID based Single Sign-On (SSO) authentication", "help": "Entra ID based Single Sign-On (SSO) authentication.", "label": "Entra Sso", "name": "entra-sso"}] | None = ...,
        negotiate_ntlm: Literal[{"description": "Enable negotiate authentication for NTLM", "help": "Enable negotiate authentication for NTLM.", "label": "Enable", "name": "enable"}, {"description": "Disable negotiate authentication for NTLM", "help": "Disable negotiate authentication for NTLM.", "label": "Disable", "name": "disable"}] | None = ...,
        kerberos_keytab: str | None = ...,
        domain_controller: str | None = ...,
        saml_server: str | None = ...,
        saml_timeout: int | None = ...,
        fsso_agent_for_ntlm: str | None = ...,
        require_tfa: Literal[{"description": "Enable two-factor authentication", "help": "Enable two-factor authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable two-factor authentication", "help": "Disable two-factor authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        fsso_guest: Literal[{"description": "Enable user fsso-guest authentication", "help": "Enable user fsso-guest authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable user fsso-guest authentication", "help": "Disable user fsso-guest authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        user_cert: Literal[{"description": "Enable client certificate field authentication", "help": "Enable client certificate field authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable client certificate field authentication", "help": "Disable client certificate field authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        cert_http_header: Literal[{"description": "Enable client certificate authentication with HTTP header (RFC9440)", "help": "Enable client certificate authentication with HTTP header (RFC9440).", "label": "Enable", "name": "enable"}, {"description": "Disable client certificate authentication with HTTP header (RFC9440)", "help": "Disable client certificate authentication with HTTP header (RFC9440).", "label": "Disable", "name": "disable"}] | None = ...,
        user_database: list[dict[str, Any]] | None = ...,
        ssh_ca: str | None = ...,
        external_idp: str | None = ...,
        group_attr_type: Literal[{"description": "Display name", "help": "Display name.", "label": "Display Name", "name": "display-name"}, {"description": "External ID", "help": "External ID.", "label": "External Id", "name": "external-id"}] | None = ...,
        digest_algo: Literal[{"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}, {"description": "SHA-256", "help": "SHA-256.", "label": "Sha 256", "name": "sha-256"}] | None = ...,
        digest_rfc2069: Literal[{"description": "Enable support for the deprecated RFC2069 Digest Client (no cnonce field)", "help": "Enable support for the deprecated RFC2069 Digest Client (no cnonce field).", "label": "Enable", "name": "enable"}, {"description": "Disable support for the deprecated RFC2069 Digest Client (no cnonce field)", "help": "Disable support for the deprecated RFC2069 Digest Client (no cnonce field).", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: SchemePayload | None = ...,
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
    "Scheme",
    "SchemePayload",
]