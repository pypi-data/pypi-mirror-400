from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SamlPayload(TypedDict, total=False):
    """
    Type hints for user/saml payload fields.
    
    SAML server entry configuration.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.user.scim.ScimEndpoint` (via: scim-client)
        - :class:`~.vpn.certificate.local.LocalEndpoint` (via: cert)
        - :class:`~.vpn.certificate.remote.RemoteEndpoint` (via: idp-cert)

    **Usage:**
        payload: SamlPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # SAML server entry name.
    cert: NotRequired[str]  # Certificate to sign SAML messages.
    entity_id: str  # SP entity ID.
    single_sign_on_url: str  # SP single sign-on URL.
    single_logout_url: NotRequired[str]  # SP single logout URL.
    idp_entity_id: str  # IDP entity ID.
    idp_single_sign_on_url: str  # IDP single sign-on URL.
    idp_single_logout_url: NotRequired[str]  # IDP single logout url.
    idp_cert: str  # IDP Certificate name.
    scim_client: NotRequired[str]  # SCIM client name.
    scim_user_attr_type: NotRequired[Literal[{"description": "User name", "help": "User name.", "label": "User Name", "name": "user-name"}, {"description": "Display name", "help": "Display name.", "label": "Display Name", "name": "display-name"}, {"description": "External ID", "help": "External ID.", "label": "External Id", "name": "external-id"}, {"description": "Email", "help": "Email.", "label": "Email", "name": "email"}]]  # User attribute type used to match SCIM users (default = user
    scim_group_attr_type: NotRequired[Literal[{"description": "Display name", "help": "Display name.", "label": "Display Name", "name": "display-name"}, {"description": "External ID", "help": "External ID.", "label": "External Id", "name": "external-id"}]]  # Group attribute type used to match SCIM groups (default = di
    user_name: NotRequired[str]  # User name in assertion statement.
    group_name: NotRequired[str]  # Group name in assertion statement.
    digest_method: NotRequired[Literal[{"description": "Digest Method Algorithm is SHA1", "help": "Digest Method Algorithm is SHA1.", "label": "Sha1", "name": "sha1"}, {"description": "Digest Method Algorithm is SHA256", "help": "Digest Method Algorithm is SHA256.", "label": "Sha256", "name": "sha256"}]]  # Digest method algorithm.
    require_signed_resp_and_asrt: NotRequired[Literal[{"description": "Both response and assertion must be signed and valid", "help": "Both response and assertion must be signed and valid.", "label": "Enable", "name": "enable"}, {"description": "At least one of response or assertion must be signed and valid", "help": "At least one of response or assertion must be signed and valid.", "label": "Disable", "name": "disable"}]]  # Require both response and assertion from IDP to be signed wh
    limit_relaystate: NotRequired[Literal[{"description": "Enable limiting of relay-state parameter when it exceeds SAML 2", "help": "Enable limiting of relay-state parameter when it exceeds SAML 2.0 specification limits (80 bytes).", "label": "Enable", "name": "enable"}, {"description": "Disable limiting of relay-state parameter when it exceeds SAML 2", "help": "Disable limiting of relay-state parameter when it exceeds SAML 2.0 specification limits (80 bytes).", "label": "Disable", "name": "disable"}]]  # Enable/disable limiting of relay-state parameter when it exc
    clock_tolerance: NotRequired[int]  # Clock skew tolerance in seconds (0 - 300, default = 15, 0 = 
    adfs_claim: NotRequired[Literal[{"description": "Enable ADFS Claim for user/group attribute in assertion statement", "help": "Enable ADFS Claim for user/group attribute in assertion statement.", "label": "Enable", "name": "enable"}, {"description": "Disable ADFS Claim for user/group attribute in assertion statement", "help": "Disable ADFS Claim for user/group attribute in assertion statement.", "label": "Disable", "name": "disable"}]]  # Enable/disable ADFS Claim for user/group attribute in assert
    user_claim_type: NotRequired[Literal[{"description": "E-mail address of the user", "help": "E-mail address of the user.", "label": "Email", "name": "email"}, {"description": "Given name of the user", "help": "Given name of the user.", "label": "Given Name", "name": "given-name"}, {"description": "Unique name of the user", "help": "Unique name of the user.", "label": "Name", "name": "name"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn", "name": "upn"}, {"description": "Common name of the user", "help": "Common name of the user.", "label": "Common Name", "name": "common-name"}, {"description": "E-mail address of the user when interoperating with AD FS 1", "help": "E-mail address of the user when interoperating with AD FS 1.1 or ADFS 1.0.", "label": "Email Adfs 1X", "name": "email-adfs-1x"}, {"description": "Group that the user is a member of", "help": "Group that the user is a member of.", "label": "Group", "name": "group"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn Adfs 1X", "name": "upn-adfs-1x"}, {"description": "Role that the user has", "help": "Role that the user has.", "label": "Role", "name": "role"}, {"description": "Surname of the user    ppid:Private identifier of the user", "help": "Surname of the user", "label": "Sur Name", "name": "sur-name"}, {"help": "Private identifier of the user.", "label": "Ppid", "name": "ppid"}, {"description": "SAML name identifier of the user", "help": "SAML name identifier of the user.", "label": "Name Identifier", "name": "name-identifier"}, {"description": "Method used to authenticate the user", "help": "Method used to authenticate the user.", "label": "Authentication Method", "name": "authentication-method"}, {"description": "Deny-only group SID of the user", "help": "Deny-only group SID of the user.", "label": "Deny Only Group Sid", "name": "deny-only-group-sid"}, {"description": "Deny-only primary SID of the user", "help": "Deny-only primary SID of the user.", "label": "Deny Only Primary Sid", "name": "deny-only-primary-sid"}, {"description": "Deny-only primary group SID of the user", "help": "Deny-only primary group SID of the user.", "label": "Deny Only Primary Group Sid", "name": "deny-only-primary-group-sid"}, {"description": "Group SID of the user", "help": "Group SID of the user.", "label": "Group Sid", "name": "group-sid"}, {"description": "Primary group SID of the user", "help": "Primary group SID of the user.", "label": "Primary Group Sid", "name": "primary-group-sid"}, {"description": "Primary SID of the user", "help": "Primary SID of the user.", "label": "Primary Sid", "name": "primary-sid"}, {"description": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e", "help": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e.", "label": "Windows Account Name", "name": "windows-account-name"}]]  # User name claim in assertion statement.
    group_claim_type: NotRequired[Literal[{"description": "E-mail address of the user", "help": "E-mail address of the user.", "label": "Email", "name": "email"}, {"description": "Given name of the user", "help": "Given name of the user.", "label": "Given Name", "name": "given-name"}, {"description": "Unique name of the user", "help": "Unique name of the user.", "label": "Name", "name": "name"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn", "name": "upn"}, {"description": "Common name of the user", "help": "Common name of the user.", "label": "Common Name", "name": "common-name"}, {"description": "E-mail address of the user when interoperating with AD FS 1", "help": "E-mail address of the user when interoperating with AD FS 1.1 or ADFS 1.0.", "label": "Email Adfs 1X", "name": "email-adfs-1x"}, {"description": "Group that the user is a member of", "help": "Group that the user is a member of.", "label": "Group", "name": "group"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn Adfs 1X", "name": "upn-adfs-1x"}, {"description": "Role that the user has", "help": "Role that the user has.", "label": "Role", "name": "role"}, {"description": "Surname of the user    ppid:Private identifier of the user", "help": "Surname of the user", "label": "Sur Name", "name": "sur-name"}, {"help": "Private identifier of the user.", "label": "Ppid", "name": "ppid"}, {"description": "SAML name identifier of the user", "help": "SAML name identifier of the user.", "label": "Name Identifier", "name": "name-identifier"}, {"description": "Method used to authenticate the user", "help": "Method used to authenticate the user.", "label": "Authentication Method", "name": "authentication-method"}, {"description": "Deny-only group SID of the user", "help": "Deny-only group SID of the user.", "label": "Deny Only Group Sid", "name": "deny-only-group-sid"}, {"description": "Deny-only primary SID of the user", "help": "Deny-only primary SID of the user.", "label": "Deny Only Primary Sid", "name": "deny-only-primary-sid"}, {"description": "Deny-only primary group SID of the user", "help": "Deny-only primary group SID of the user.", "label": "Deny Only Primary Group Sid", "name": "deny-only-primary-group-sid"}, {"description": "Group SID of the user", "help": "Group SID of the user.", "label": "Group Sid", "name": "group-sid"}, {"description": "Primary group SID of the user", "help": "Primary group SID of the user.", "label": "Primary Group Sid", "name": "primary-group-sid"}, {"description": "Primary SID of the user", "help": "Primary SID of the user.", "label": "Primary Sid", "name": "primary-sid"}, {"description": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e", "help": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e.", "label": "Windows Account Name", "name": "windows-account-name"}]]  # Group claim in assertion statement.
    reauth: NotRequired[Literal[{"description": "Enable signalling of IDP to force user re-authentication", "help": "Enable signalling of IDP to force user re-authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable signalling of IDP to force user re-authentication", "help": "Disable signalling of IDP to force user re-authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable signalling of IDP to force user re-authentica


class Saml:
    """
    SAML server entry configuration.
    
    Path: user/saml
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
        payload_dict: SamlPayload | None = ...,
        name: str | None = ...,
        cert: str | None = ...,
        entity_id: str | None = ...,
        single_sign_on_url: str | None = ...,
        single_logout_url: str | None = ...,
        idp_entity_id: str | None = ...,
        idp_single_sign_on_url: str | None = ...,
        idp_single_logout_url: str | None = ...,
        idp_cert: str | None = ...,
        scim_client: str | None = ...,
        scim_user_attr_type: Literal[{"description": "User name", "help": "User name.", "label": "User Name", "name": "user-name"}, {"description": "Display name", "help": "Display name.", "label": "Display Name", "name": "display-name"}, {"description": "External ID", "help": "External ID.", "label": "External Id", "name": "external-id"}, {"description": "Email", "help": "Email.", "label": "Email", "name": "email"}] | None = ...,
        scim_group_attr_type: Literal[{"description": "Display name", "help": "Display name.", "label": "Display Name", "name": "display-name"}, {"description": "External ID", "help": "External ID.", "label": "External Id", "name": "external-id"}] | None = ...,
        user_name: str | None = ...,
        group_name: str | None = ...,
        digest_method: Literal[{"description": "Digest Method Algorithm is SHA1", "help": "Digest Method Algorithm is SHA1.", "label": "Sha1", "name": "sha1"}, {"description": "Digest Method Algorithm is SHA256", "help": "Digest Method Algorithm is SHA256.", "label": "Sha256", "name": "sha256"}] | None = ...,
        require_signed_resp_and_asrt: Literal[{"description": "Both response and assertion must be signed and valid", "help": "Both response and assertion must be signed and valid.", "label": "Enable", "name": "enable"}, {"description": "At least one of response or assertion must be signed and valid", "help": "At least one of response or assertion must be signed and valid.", "label": "Disable", "name": "disable"}] | None = ...,
        limit_relaystate: Literal[{"description": "Enable limiting of relay-state parameter when it exceeds SAML 2", "help": "Enable limiting of relay-state parameter when it exceeds SAML 2.0 specification limits (80 bytes).", "label": "Enable", "name": "enable"}, {"description": "Disable limiting of relay-state parameter when it exceeds SAML 2", "help": "Disable limiting of relay-state parameter when it exceeds SAML 2.0 specification limits (80 bytes).", "label": "Disable", "name": "disable"}] | None = ...,
        clock_tolerance: int | None = ...,
        adfs_claim: Literal[{"description": "Enable ADFS Claim for user/group attribute in assertion statement", "help": "Enable ADFS Claim for user/group attribute in assertion statement.", "label": "Enable", "name": "enable"}, {"description": "Disable ADFS Claim for user/group attribute in assertion statement", "help": "Disable ADFS Claim for user/group attribute in assertion statement.", "label": "Disable", "name": "disable"}] | None = ...,
        user_claim_type: Literal[{"description": "E-mail address of the user", "help": "E-mail address of the user.", "label": "Email", "name": "email"}, {"description": "Given name of the user", "help": "Given name of the user.", "label": "Given Name", "name": "given-name"}, {"description": "Unique name of the user", "help": "Unique name of the user.", "label": "Name", "name": "name"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn", "name": "upn"}, {"description": "Common name of the user", "help": "Common name of the user.", "label": "Common Name", "name": "common-name"}, {"description": "E-mail address of the user when interoperating with AD FS 1", "help": "E-mail address of the user when interoperating with AD FS 1.1 or ADFS 1.0.", "label": "Email Adfs 1X", "name": "email-adfs-1x"}, {"description": "Group that the user is a member of", "help": "Group that the user is a member of.", "label": "Group", "name": "group"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn Adfs 1X", "name": "upn-adfs-1x"}, {"description": "Role that the user has", "help": "Role that the user has.", "label": "Role", "name": "role"}, {"description": "Surname of the user    ppid:Private identifier of the user", "help": "Surname of the user", "label": "Sur Name", "name": "sur-name"}, {"help": "Private identifier of the user.", "label": "Ppid", "name": "ppid"}, {"description": "SAML name identifier of the user", "help": "SAML name identifier of the user.", "label": "Name Identifier", "name": "name-identifier"}, {"description": "Method used to authenticate the user", "help": "Method used to authenticate the user.", "label": "Authentication Method", "name": "authentication-method"}, {"description": "Deny-only group SID of the user", "help": "Deny-only group SID of the user.", "label": "Deny Only Group Sid", "name": "deny-only-group-sid"}, {"description": "Deny-only primary SID of the user", "help": "Deny-only primary SID of the user.", "label": "Deny Only Primary Sid", "name": "deny-only-primary-sid"}, {"description": "Deny-only primary group SID of the user", "help": "Deny-only primary group SID of the user.", "label": "Deny Only Primary Group Sid", "name": "deny-only-primary-group-sid"}, {"description": "Group SID of the user", "help": "Group SID of the user.", "label": "Group Sid", "name": "group-sid"}, {"description": "Primary group SID of the user", "help": "Primary group SID of the user.", "label": "Primary Group Sid", "name": "primary-group-sid"}, {"description": "Primary SID of the user", "help": "Primary SID of the user.", "label": "Primary Sid", "name": "primary-sid"}, {"description": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e", "help": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e.", "label": "Windows Account Name", "name": "windows-account-name"}] | None = ...,
        group_claim_type: Literal[{"description": "E-mail address of the user", "help": "E-mail address of the user.", "label": "Email", "name": "email"}, {"description": "Given name of the user", "help": "Given name of the user.", "label": "Given Name", "name": "given-name"}, {"description": "Unique name of the user", "help": "Unique name of the user.", "label": "Name", "name": "name"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn", "name": "upn"}, {"description": "Common name of the user", "help": "Common name of the user.", "label": "Common Name", "name": "common-name"}, {"description": "E-mail address of the user when interoperating with AD FS 1", "help": "E-mail address of the user when interoperating with AD FS 1.1 or ADFS 1.0.", "label": "Email Adfs 1X", "name": "email-adfs-1x"}, {"description": "Group that the user is a member of", "help": "Group that the user is a member of.", "label": "Group", "name": "group"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn Adfs 1X", "name": "upn-adfs-1x"}, {"description": "Role that the user has", "help": "Role that the user has.", "label": "Role", "name": "role"}, {"description": "Surname of the user    ppid:Private identifier of the user", "help": "Surname of the user", "label": "Sur Name", "name": "sur-name"}, {"help": "Private identifier of the user.", "label": "Ppid", "name": "ppid"}, {"description": "SAML name identifier of the user", "help": "SAML name identifier of the user.", "label": "Name Identifier", "name": "name-identifier"}, {"description": "Method used to authenticate the user", "help": "Method used to authenticate the user.", "label": "Authentication Method", "name": "authentication-method"}, {"description": "Deny-only group SID of the user", "help": "Deny-only group SID of the user.", "label": "Deny Only Group Sid", "name": "deny-only-group-sid"}, {"description": "Deny-only primary SID of the user", "help": "Deny-only primary SID of the user.", "label": "Deny Only Primary Sid", "name": "deny-only-primary-sid"}, {"description": "Deny-only primary group SID of the user", "help": "Deny-only primary group SID of the user.", "label": "Deny Only Primary Group Sid", "name": "deny-only-primary-group-sid"}, {"description": "Group SID of the user", "help": "Group SID of the user.", "label": "Group Sid", "name": "group-sid"}, {"description": "Primary group SID of the user", "help": "Primary group SID of the user.", "label": "Primary Group Sid", "name": "primary-group-sid"}, {"description": "Primary SID of the user", "help": "Primary SID of the user.", "label": "Primary Sid", "name": "primary-sid"}, {"description": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e", "help": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e.", "label": "Windows Account Name", "name": "windows-account-name"}] | None = ...,
        reauth: Literal[{"description": "Enable signalling of IDP to force user re-authentication", "help": "Enable signalling of IDP to force user re-authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable signalling of IDP to force user re-authentication", "help": "Disable signalling of IDP to force user re-authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SamlPayload | None = ...,
        name: str | None = ...,
        cert: str | None = ...,
        entity_id: str | None = ...,
        single_sign_on_url: str | None = ...,
        single_logout_url: str | None = ...,
        idp_entity_id: str | None = ...,
        idp_single_sign_on_url: str | None = ...,
        idp_single_logout_url: str | None = ...,
        idp_cert: str | None = ...,
        scim_client: str | None = ...,
        scim_user_attr_type: Literal[{"description": "User name", "help": "User name.", "label": "User Name", "name": "user-name"}, {"description": "Display name", "help": "Display name.", "label": "Display Name", "name": "display-name"}, {"description": "External ID", "help": "External ID.", "label": "External Id", "name": "external-id"}, {"description": "Email", "help": "Email.", "label": "Email", "name": "email"}] | None = ...,
        scim_group_attr_type: Literal[{"description": "Display name", "help": "Display name.", "label": "Display Name", "name": "display-name"}, {"description": "External ID", "help": "External ID.", "label": "External Id", "name": "external-id"}] | None = ...,
        user_name: str | None = ...,
        group_name: str | None = ...,
        digest_method: Literal[{"description": "Digest Method Algorithm is SHA1", "help": "Digest Method Algorithm is SHA1.", "label": "Sha1", "name": "sha1"}, {"description": "Digest Method Algorithm is SHA256", "help": "Digest Method Algorithm is SHA256.", "label": "Sha256", "name": "sha256"}] | None = ...,
        require_signed_resp_and_asrt: Literal[{"description": "Both response and assertion must be signed and valid", "help": "Both response and assertion must be signed and valid.", "label": "Enable", "name": "enable"}, {"description": "At least one of response or assertion must be signed and valid", "help": "At least one of response or assertion must be signed and valid.", "label": "Disable", "name": "disable"}] | None = ...,
        limit_relaystate: Literal[{"description": "Enable limiting of relay-state parameter when it exceeds SAML 2", "help": "Enable limiting of relay-state parameter when it exceeds SAML 2.0 specification limits (80 bytes).", "label": "Enable", "name": "enable"}, {"description": "Disable limiting of relay-state parameter when it exceeds SAML 2", "help": "Disable limiting of relay-state parameter when it exceeds SAML 2.0 specification limits (80 bytes).", "label": "Disable", "name": "disable"}] | None = ...,
        clock_tolerance: int | None = ...,
        adfs_claim: Literal[{"description": "Enable ADFS Claim for user/group attribute in assertion statement", "help": "Enable ADFS Claim for user/group attribute in assertion statement.", "label": "Enable", "name": "enable"}, {"description": "Disable ADFS Claim for user/group attribute in assertion statement", "help": "Disable ADFS Claim for user/group attribute in assertion statement.", "label": "Disable", "name": "disable"}] | None = ...,
        user_claim_type: Literal[{"description": "E-mail address of the user", "help": "E-mail address of the user.", "label": "Email", "name": "email"}, {"description": "Given name of the user", "help": "Given name of the user.", "label": "Given Name", "name": "given-name"}, {"description": "Unique name of the user", "help": "Unique name of the user.", "label": "Name", "name": "name"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn", "name": "upn"}, {"description": "Common name of the user", "help": "Common name of the user.", "label": "Common Name", "name": "common-name"}, {"description": "E-mail address of the user when interoperating with AD FS 1", "help": "E-mail address of the user when interoperating with AD FS 1.1 or ADFS 1.0.", "label": "Email Adfs 1X", "name": "email-adfs-1x"}, {"description": "Group that the user is a member of", "help": "Group that the user is a member of.", "label": "Group", "name": "group"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn Adfs 1X", "name": "upn-adfs-1x"}, {"description": "Role that the user has", "help": "Role that the user has.", "label": "Role", "name": "role"}, {"description": "Surname of the user    ppid:Private identifier of the user", "help": "Surname of the user", "label": "Sur Name", "name": "sur-name"}, {"help": "Private identifier of the user.", "label": "Ppid", "name": "ppid"}, {"description": "SAML name identifier of the user", "help": "SAML name identifier of the user.", "label": "Name Identifier", "name": "name-identifier"}, {"description": "Method used to authenticate the user", "help": "Method used to authenticate the user.", "label": "Authentication Method", "name": "authentication-method"}, {"description": "Deny-only group SID of the user", "help": "Deny-only group SID of the user.", "label": "Deny Only Group Sid", "name": "deny-only-group-sid"}, {"description": "Deny-only primary SID of the user", "help": "Deny-only primary SID of the user.", "label": "Deny Only Primary Sid", "name": "deny-only-primary-sid"}, {"description": "Deny-only primary group SID of the user", "help": "Deny-only primary group SID of the user.", "label": "Deny Only Primary Group Sid", "name": "deny-only-primary-group-sid"}, {"description": "Group SID of the user", "help": "Group SID of the user.", "label": "Group Sid", "name": "group-sid"}, {"description": "Primary group SID of the user", "help": "Primary group SID of the user.", "label": "Primary Group Sid", "name": "primary-group-sid"}, {"description": "Primary SID of the user", "help": "Primary SID of the user.", "label": "Primary Sid", "name": "primary-sid"}, {"description": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e", "help": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e.", "label": "Windows Account Name", "name": "windows-account-name"}] | None = ...,
        group_claim_type: Literal[{"description": "E-mail address of the user", "help": "E-mail address of the user.", "label": "Email", "name": "email"}, {"description": "Given name of the user", "help": "Given name of the user.", "label": "Given Name", "name": "given-name"}, {"description": "Unique name of the user", "help": "Unique name of the user.", "label": "Name", "name": "name"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn", "name": "upn"}, {"description": "Common name of the user", "help": "Common name of the user.", "label": "Common Name", "name": "common-name"}, {"description": "E-mail address of the user when interoperating with AD FS 1", "help": "E-mail address of the user when interoperating with AD FS 1.1 or ADFS 1.0.", "label": "Email Adfs 1X", "name": "email-adfs-1x"}, {"description": "Group that the user is a member of", "help": "Group that the user is a member of.", "label": "Group", "name": "group"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn Adfs 1X", "name": "upn-adfs-1x"}, {"description": "Role that the user has", "help": "Role that the user has.", "label": "Role", "name": "role"}, {"description": "Surname of the user    ppid:Private identifier of the user", "help": "Surname of the user", "label": "Sur Name", "name": "sur-name"}, {"help": "Private identifier of the user.", "label": "Ppid", "name": "ppid"}, {"description": "SAML name identifier of the user", "help": "SAML name identifier of the user.", "label": "Name Identifier", "name": "name-identifier"}, {"description": "Method used to authenticate the user", "help": "Method used to authenticate the user.", "label": "Authentication Method", "name": "authentication-method"}, {"description": "Deny-only group SID of the user", "help": "Deny-only group SID of the user.", "label": "Deny Only Group Sid", "name": "deny-only-group-sid"}, {"description": "Deny-only primary SID of the user", "help": "Deny-only primary SID of the user.", "label": "Deny Only Primary Sid", "name": "deny-only-primary-sid"}, {"description": "Deny-only primary group SID of the user", "help": "Deny-only primary group SID of the user.", "label": "Deny Only Primary Group Sid", "name": "deny-only-primary-group-sid"}, {"description": "Group SID of the user", "help": "Group SID of the user.", "label": "Group Sid", "name": "group-sid"}, {"description": "Primary group SID of the user", "help": "Primary group SID of the user.", "label": "Primary Group Sid", "name": "primary-group-sid"}, {"description": "Primary SID of the user", "help": "Primary SID of the user.", "label": "Primary Sid", "name": "primary-sid"}, {"description": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e", "help": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e.", "label": "Windows Account Name", "name": "windows-account-name"}] | None = ...,
        reauth: Literal[{"description": "Enable signalling of IDP to force user re-authentication", "help": "Enable signalling of IDP to force user re-authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable signalling of IDP to force user re-authentication", "help": "Disable signalling of IDP to force user re-authentication.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: SamlPayload | None = ...,
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
    "Saml",
    "SamlPayload",
]