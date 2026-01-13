from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_METHOD: Literal[{"description": "NTLM authentication", "help": "NTLM authentication.", "label": "Ntlm", "name": "ntlm"}, {"description": "Basic HTTP authentication", "help": "Basic HTTP authentication.", "label": "Basic", "name": "basic"}, {"description": "Digest HTTP authentication", "help": "Digest HTTP authentication.", "label": "Digest", "name": "digest"}, {"description": "Form-based HTTP authentication", "help": "Form-based HTTP authentication.", "label": "Form", "name": "form"}, {"description": "Negotiate authentication", "help": "Negotiate authentication.", "label": "Negotiate", "name": "negotiate"}, {"description": "Fortinet Single Sign-On (FSSO) authentication", "help": "Fortinet Single Sign-On (FSSO) authentication.", "label": "Fsso", "name": "fsso"}, {"description": "RADIUS Single Sign-On (RSSO) authentication", "help": "RADIUS Single Sign-On (RSSO) authentication.", "label": "Rsso", "name": "rsso"}, {"description": "Public key based SSH authentication", "help": "Public key based SSH authentication.", "label": "Ssh Publickey", "name": "ssh-publickey"}, {"description": "Client certificate authentication", "help": "Client certificate authentication.", "label": "Cert", "name": "cert"}, {"description": "SAML authentication", "help": "SAML authentication.", "label": "Saml", "name": "saml"}, {"description": "Entra ID based Single Sign-On (SSO) authentication", "help": "Entra ID based Single Sign-On (SSO) authentication.", "label": "Entra Sso", "name": "entra-sso"}]
VALID_BODY_NEGOTIATE_NTLM: Literal[{"description": "Enable negotiate authentication for NTLM", "help": "Enable negotiate authentication for NTLM.", "label": "Enable", "name": "enable"}, {"description": "Disable negotiate authentication for NTLM", "help": "Disable negotiate authentication for NTLM.", "label": "Disable", "name": "disable"}]
VALID_BODY_REQUIRE_TFA: Literal[{"description": "Enable two-factor authentication", "help": "Enable two-factor authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable two-factor authentication", "help": "Disable two-factor authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_FSSO_GUEST: Literal[{"description": "Enable user fsso-guest authentication", "help": "Enable user fsso-guest authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable user fsso-guest authentication", "help": "Disable user fsso-guest authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_USER_CERT: Literal[{"description": "Enable client certificate field authentication", "help": "Enable client certificate field authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable client certificate field authentication", "help": "Disable client certificate field authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_CERT_HTTP_HEADER: Literal[{"description": "Enable client certificate authentication with HTTP header (RFC9440)", "help": "Enable client certificate authentication with HTTP header (RFC9440).", "label": "Enable", "name": "enable"}, {"description": "Disable client certificate authentication with HTTP header (RFC9440)", "help": "Disable client certificate authentication with HTTP header (RFC9440).", "label": "Disable", "name": "disable"}]
VALID_BODY_GROUP_ATTR_TYPE: Literal[{"description": "Display name", "help": "Display name.", "label": "Display Name", "name": "display-name"}, {"description": "External ID", "help": "External ID.", "label": "External Id", "name": "external-id"}]
VALID_BODY_DIGEST_ALGO: Literal[{"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}, {"description": "SHA-256", "help": "SHA-256.", "label": "Sha 256", "name": "sha-256"}]
VALID_BODY_DIGEST_RFC2069: Literal[{"description": "Enable support for the deprecated RFC2069 Digest Client (no cnonce field)", "help": "Enable support for the deprecated RFC2069 Digest Client (no cnonce field).", "label": "Enable", "name": "enable"}, {"description": "Disable support for the deprecated RFC2069 Digest Client (no cnonce field)", "help": "Disable support for the deprecated RFC2069 Digest Client (no cnonce field).", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_METHOD",
    "VALID_BODY_NEGOTIATE_NTLM",
    "VALID_BODY_REQUIRE_TFA",
    "VALID_BODY_FSSO_GUEST",
    "VALID_BODY_USER_CERT",
    "VALID_BODY_CERT_HTTP_HEADER",
    "VALID_BODY_GROUP_ATTR_TYPE",
    "VALID_BODY_DIGEST_ALGO",
    "VALID_BODY_DIGEST_RFC2069",
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