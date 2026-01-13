from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SERVER_IDENTITY_CHECK: Literal[{"description": "Enable server identity check", "help": "Enable server identity check.", "label": "Enable", "name": "enable"}, {"description": "Disable server identity check", "help": "Disable server identity check.", "label": "Disable", "name": "disable"}]
VALID_BODY_TYPE: Literal[{"description": "Simple password authentication without search", "help": "Simple password authentication without search.", "label": "Simple", "name": "simple"}, {"description": "Bind using anonymous user search", "help": "Bind using anonymous user search.", "label": "Anonymous", "name": "anonymous"}, {"description": "Bind using username/password and then search", "help": "Bind using username/password and then search.", "label": "Regular", "name": "regular"}]
VALID_BODY_TWO_FACTOR: Literal[{"description": "disable two-factor authentication", "help": "disable two-factor authentication.", "label": "Disable", "name": "disable"}, {"description": "FortiToken Cloud Service", "help": "FortiToken Cloud Service.", "label": "Fortitoken Cloud", "name": "fortitoken-cloud"}]
VALID_BODY_TWO_FACTOR_AUTHENTICATION: Literal[{"description": "FortiToken authentication", "help": "FortiToken authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "Email one time password", "help": "Email one time password.", "label": "Email", "name": "email"}, {"description": "SMS one time password", "help": "SMS one time password.", "label": "Sms", "name": "sms"}]
VALID_BODY_TWO_FACTOR_NOTIFICATION: Literal[{"description": "Email notification for activation code", "help": "Email notification for activation code.", "label": "Email", "name": "email"}, {"description": "SMS notification for activation code", "help": "SMS notification for activation code.", "label": "Sms", "name": "sms"}]
VALID_BODY_GROUP_MEMBER_CHECK: Literal[{"description": "User attribute checking", "help": "User attribute checking.", "label": "User Attr", "name": "user-attr"}, {"description": "Group object checking", "help": "Group object checking.", "label": "Group Object", "name": "group-object"}, {"description": "POSIX group object checking", "help": "POSIX group object checking.", "label": "Posix Group Object", "name": "posix-group-object"}]
VALID_BODY_SECURE: Literal[{"description": "No SSL", "help": "No SSL.", "label": "Disable", "name": "disable"}, {"description": "Use StartTLS", "help": "Use StartTLS.", "label": "Starttls", "name": "starttls"}, {"description": "Use LDAPS", "help": "Use LDAPS.", "label": "Ldaps", "name": "ldaps"}]
VALID_BODY_SSL_MIN_PROTO_VERSION: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]
VALID_BODY_PASSWORD_EXPIRY_WARNING: Literal[{"description": "Enable password expiry warnings", "help": "Enable password expiry warnings.", "label": "Enable", "name": "enable"}, {"description": "Disable password expiry warnings", "help": "Disable password expiry warnings.", "label": "Disable", "name": "disable"}]
VALID_BODY_PASSWORD_RENEWAL: Literal[{"description": "Enable online password renewal", "help": "Enable online password renewal.", "label": "Enable", "name": "enable"}, {"description": "Disable online password renewal", "help": "Disable online password renewal.", "label": "Disable", "name": "disable"}]
VALID_BODY_ACCOUNT_KEY_PROCESSING: Literal[{"description": "Same as subject identity field", "help": "Same as subject identity field.", "label": "Same", "name": "same"}, {"description": "Strip domain string from subject identity field", "help": "Strip domain string from subject identity field.", "label": "Strip", "name": "strip"}]
VALID_BODY_ACCOUNT_KEY_CERT_FIELD: Literal[{"description": "Other name in SAN", "help": "Other name in SAN.", "label": "Othername", "name": "othername"}, {"description": "RFC822 email address in SAN", "help": "RFC822 email address in SAN.", "label": "Rfc822Name", "name": "rfc822name"}, {"description": "DNS name in SAN", "help": "DNS name in SAN.", "label": "Dnsname", "name": "dnsname"}, {"description": "CN in subject", "help": "CN in subject.", "label": "Cn", "name": "cn"}]
VALID_BODY_SEARCH_TYPE: Literal[{"description": "Recursively retrieve the user-group chain information of a user in a particular Microsoft AD domain", "help": "Recursively retrieve the user-group chain information of a user in a particular Microsoft AD domain.", "label": "Recursive", "name": "recursive"}]
VALID_BODY_CLIENT_CERT_AUTH: Literal[{"description": "Enable using client certificate for TLS authentication", "help": "Enable using client certificate for TLS authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable using client certificate for TLS authentication", "help": "Disable using client certificate for TLS authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_OBTAIN_USER_INFO: Literal[{"description": "Enable obtaining of user information", "help": "Enable obtaining of user information.", "label": "Enable", "name": "enable"}, {"description": "Disable obtaining of user information", "help": "Disable obtaining of user information.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]
VALID_BODY_ANTIPHISH: Literal[{"description": "Enable AntiPhishing credential backend", "help": "Enable AntiPhishing credential backend.", "label": "Enable", "name": "enable"}, {"description": "Disable AntiPhishing credential backend", "help": "Disable AntiPhishing credential backend.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_SERVER_IDENTITY_CHECK",
    "VALID_BODY_TYPE",
    "VALID_BODY_TWO_FACTOR",
    "VALID_BODY_TWO_FACTOR_AUTHENTICATION",
    "VALID_BODY_TWO_FACTOR_NOTIFICATION",
    "VALID_BODY_GROUP_MEMBER_CHECK",
    "VALID_BODY_SECURE",
    "VALID_BODY_SSL_MIN_PROTO_VERSION",
    "VALID_BODY_PASSWORD_EXPIRY_WARNING",
    "VALID_BODY_PASSWORD_RENEWAL",
    "VALID_BODY_ACCOUNT_KEY_PROCESSING",
    "VALID_BODY_ACCOUNT_KEY_CERT_FIELD",
    "VALID_BODY_SEARCH_TYPE",
    "VALID_BODY_CLIENT_CERT_AUTH",
    "VALID_BODY_OBTAIN_USER_INFO",
    "VALID_BODY_INTERFACE_SELECT_METHOD",
    "VALID_BODY_ANTIPHISH",
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