from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SCIM_USER_ATTR_TYPE: Literal[{"description": "User name", "help": "User name.", "label": "User Name", "name": "user-name"}, {"description": "Display name", "help": "Display name.", "label": "Display Name", "name": "display-name"}, {"description": "External ID", "help": "External ID.", "label": "External Id", "name": "external-id"}, {"description": "Email", "help": "Email.", "label": "Email", "name": "email"}]
VALID_BODY_SCIM_GROUP_ATTR_TYPE: Literal[{"description": "Display name", "help": "Display name.", "label": "Display Name", "name": "display-name"}, {"description": "External ID", "help": "External ID.", "label": "External Id", "name": "external-id"}]
VALID_BODY_DIGEST_METHOD: Literal[{"description": "Digest Method Algorithm is SHA1", "help": "Digest Method Algorithm is SHA1.", "label": "Sha1", "name": "sha1"}, {"description": "Digest Method Algorithm is SHA256", "help": "Digest Method Algorithm is SHA256.", "label": "Sha256", "name": "sha256"}]
VALID_BODY_REQUIRE_SIGNED_RESP_AND_ASRT: Literal[{"description": "Both response and assertion must be signed and valid", "help": "Both response and assertion must be signed and valid.", "label": "Enable", "name": "enable"}, {"description": "At least one of response or assertion must be signed and valid", "help": "At least one of response or assertion must be signed and valid.", "label": "Disable", "name": "disable"}]
VALID_BODY_LIMIT_RELAYSTATE: Literal[{"description": "Enable limiting of relay-state parameter when it exceeds SAML 2", "help": "Enable limiting of relay-state parameter when it exceeds SAML 2.0 specification limits (80 bytes).", "label": "Enable", "name": "enable"}, {"description": "Disable limiting of relay-state parameter when it exceeds SAML 2", "help": "Disable limiting of relay-state parameter when it exceeds SAML 2.0 specification limits (80 bytes).", "label": "Disable", "name": "disable"}]
VALID_BODY_ADFS_CLAIM: Literal[{"description": "Enable ADFS Claim for user/group attribute in assertion statement", "help": "Enable ADFS Claim for user/group attribute in assertion statement.", "label": "Enable", "name": "enable"}, {"description": "Disable ADFS Claim for user/group attribute in assertion statement", "help": "Disable ADFS Claim for user/group attribute in assertion statement.", "label": "Disable", "name": "disable"}]
VALID_BODY_USER_CLAIM_TYPE: Literal[{"description": "E-mail address of the user", "help": "E-mail address of the user.", "label": "Email", "name": "email"}, {"description": "Given name of the user", "help": "Given name of the user.", "label": "Given Name", "name": "given-name"}, {"description": "Unique name of the user", "help": "Unique name of the user.", "label": "Name", "name": "name"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn", "name": "upn"}, {"description": "Common name of the user", "help": "Common name of the user.", "label": "Common Name", "name": "common-name"}, {"description": "E-mail address of the user when interoperating with AD FS 1", "help": "E-mail address of the user when interoperating with AD FS 1.1 or ADFS 1.0.", "label": "Email Adfs 1X", "name": "email-adfs-1x"}, {"description": "Group that the user is a member of", "help": "Group that the user is a member of.", "label": "Group", "name": "group"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn Adfs 1X", "name": "upn-adfs-1x"}, {"description": "Role that the user has", "help": "Role that the user has.", "label": "Role", "name": "role"}, {"description": "Surname of the user    ppid:Private identifier of the user", "help": "Surname of the user", "label": "Sur Name", "name": "sur-name"}, {"help": "Private identifier of the user.", "label": "Ppid", "name": "ppid"}, {"description": "SAML name identifier of the user", "help": "SAML name identifier of the user.", "label": "Name Identifier", "name": "name-identifier"}, {"description": "Method used to authenticate the user", "help": "Method used to authenticate the user.", "label": "Authentication Method", "name": "authentication-method"}, {"description": "Deny-only group SID of the user", "help": "Deny-only group SID of the user.", "label": "Deny Only Group Sid", "name": "deny-only-group-sid"}, {"description": "Deny-only primary SID of the user", "help": "Deny-only primary SID of the user.", "label": "Deny Only Primary Sid", "name": "deny-only-primary-sid"}, {"description": "Deny-only primary group SID of the user", "help": "Deny-only primary group SID of the user.", "label": "Deny Only Primary Group Sid", "name": "deny-only-primary-group-sid"}, {"description": "Group SID of the user", "help": "Group SID of the user.", "label": "Group Sid", "name": "group-sid"}, {"description": "Primary group SID of the user", "help": "Primary group SID of the user.", "label": "Primary Group Sid", "name": "primary-group-sid"}, {"description": "Primary SID of the user", "help": "Primary SID of the user.", "label": "Primary Sid", "name": "primary-sid"}, {"description": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e", "help": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e.", "label": "Windows Account Name", "name": "windows-account-name"}]
VALID_BODY_GROUP_CLAIM_TYPE: Literal[{"description": "E-mail address of the user", "help": "E-mail address of the user.", "label": "Email", "name": "email"}, {"description": "Given name of the user", "help": "Given name of the user.", "label": "Given Name", "name": "given-name"}, {"description": "Unique name of the user", "help": "Unique name of the user.", "label": "Name", "name": "name"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn", "name": "upn"}, {"description": "Common name of the user", "help": "Common name of the user.", "label": "Common Name", "name": "common-name"}, {"description": "E-mail address of the user when interoperating with AD FS 1", "help": "E-mail address of the user when interoperating with AD FS 1.1 or ADFS 1.0.", "label": "Email Adfs 1X", "name": "email-adfs-1x"}, {"description": "Group that the user is a member of", "help": "Group that the user is a member of.", "label": "Group", "name": "group"}, {"description": "User principal name (UPN) of the user", "help": "User principal name (UPN) of the user.", "label": "Upn Adfs 1X", "name": "upn-adfs-1x"}, {"description": "Role that the user has", "help": "Role that the user has.", "label": "Role", "name": "role"}, {"description": "Surname of the user    ppid:Private identifier of the user", "help": "Surname of the user", "label": "Sur Name", "name": "sur-name"}, {"help": "Private identifier of the user.", "label": "Ppid", "name": "ppid"}, {"description": "SAML name identifier of the user", "help": "SAML name identifier of the user.", "label": "Name Identifier", "name": "name-identifier"}, {"description": "Method used to authenticate the user", "help": "Method used to authenticate the user.", "label": "Authentication Method", "name": "authentication-method"}, {"description": "Deny-only group SID of the user", "help": "Deny-only group SID of the user.", "label": "Deny Only Group Sid", "name": "deny-only-group-sid"}, {"description": "Deny-only primary SID of the user", "help": "Deny-only primary SID of the user.", "label": "Deny Only Primary Sid", "name": "deny-only-primary-sid"}, {"description": "Deny-only primary group SID of the user", "help": "Deny-only primary group SID of the user.", "label": "Deny Only Primary Group Sid", "name": "deny-only-primary-group-sid"}, {"description": "Group SID of the user", "help": "Group SID of the user.", "label": "Group Sid", "name": "group-sid"}, {"description": "Primary group SID of the user", "help": "Primary group SID of the user.", "label": "Primary Group Sid", "name": "primary-group-sid"}, {"description": "Primary SID of the user", "help": "Primary SID of the user.", "label": "Primary Sid", "name": "primary-sid"}, {"description": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e", "help": "Domain account name of the user in the form of \u003cdomain\u003e\\\u003cuser\u003e.", "label": "Windows Account Name", "name": "windows-account-name"}]
VALID_BODY_REAUTH: Literal[{"description": "Enable signalling of IDP to force user re-authentication", "help": "Enable signalling of IDP to force user re-authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable signalling of IDP to force user re-authentication", "help": "Disable signalling of IDP to force user re-authentication.", "label": "Disable", "name": "disable"}]

# Metadata dictionaries
FIELD_TYPES: dict[str, str]
FIELD_DESCRIPTIONS: dict[str, str]
FIELD_CONSTRAINTS: dict[str, dict[str, Any]]
NESTED_SCHEMAS: dict[str, dict[str, Any]]
FIELDS_WITH_DEFAULTS: dict[str, Any]

# Helper functions
def get_field_type(field_name: str) -> str | None: ...
def get_field_description(field_name: str) -> str | None: ...
def get_field_default(field_name: str) -> Any: ...
def get_field_constraints(field_name: str) -> dict[str, Any]: ...
def get_nested_schema(field_name: str) -> dict[str, Any] | None: ...
def get_field_metadata(field_name: str) -> dict[str, Any]: ...
def validate_field_value(field_name: str, value: Any) -> bool: ...
def get_all_fields() -> list[str]: ...
def get_required_fields() -> list[str]: ...
def get_schema_info() -> dict[str, Any]: ...


__all__ = [
    "VALID_BODY_SCIM_USER_ATTR_TYPE",
    "VALID_BODY_SCIM_GROUP_ATTR_TYPE",
    "VALID_BODY_DIGEST_METHOD",
    "VALID_BODY_REQUIRE_SIGNED_RESP_AND_ASRT",
    "VALID_BODY_LIMIT_RELAYSTATE",
    "VALID_BODY_ADFS_CLAIM",
    "VALID_BODY_USER_CLAIM_TYPE",
    "VALID_BODY_GROUP_CLAIM_TYPE",
    "VALID_BODY_REAUTH",
    "FIELD_TYPES",
    "FIELD_DESCRIPTIONS",
    "FIELD_CONSTRAINTS",
    "NESTED_SCHEMAS",
    "FIELDS_WITH_DEFAULTS",
    "get_field_type",
    "get_field_description",
    "get_field_default",
    "get_field_constraints",
    "get_nested_schema",
    "get_field_metadata",
    "validate_field_value",
    "get_all_fields",
    "get_required_fields",
    "get_schema_info",
]