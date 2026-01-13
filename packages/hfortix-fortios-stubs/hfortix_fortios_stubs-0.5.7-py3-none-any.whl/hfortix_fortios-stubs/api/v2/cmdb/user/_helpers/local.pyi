from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable user", "help": "Enable user.", "label": "Enable", "name": "enable"}, {"description": "Disable user", "help": "Disable user.", "label": "Disable", "name": "disable"}]
VALID_BODY_TYPE: Literal[{"description": "Password authentication", "help": "Password authentication.", "label": "Password", "name": "password"}, {"description": "RADIUS server authentication", "help": "RADIUS server authentication.", "label": "Radius", "name": "radius"}, {"description": "TACACS+ server authentication", "help": "TACACS+ server authentication.", "label": "Tacacs+", "name": "tacacs+"}, {"description": "LDAP server authentication", "help": "LDAP server authentication.", "label": "Ldap", "name": "ldap"}, {"description": "SAML server authentication", "help": "SAML server authentication.", "label": "Saml", "name": "saml"}]
VALID_BODY_TWO_FACTOR: Literal[{"description": "disable    fortitoken:FortiToken    fortitoken-cloud:FortiToken Cloud Service", "help": "disable", "label": "Disable", "name": "disable"}, {"help": "FortiToken", "label": "Fortitoken", "name": "fortitoken"}, {"help": "FortiToken Cloud Service.", "label": "Fortitoken Cloud", "name": "fortitoken-cloud"}, {"description": "Email authentication code", "help": "Email authentication code.", "label": "Email", "name": "email"}, {"description": "SMS authentication code", "help": "SMS authentication code.", "label": "Sms", "name": "sms"}]
VALID_BODY_TWO_FACTOR_AUTHENTICATION: Literal[{"description": "FortiToken authentication", "help": "FortiToken authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "Email one time password", "help": "Email one time password.", "label": "Email", "name": "email"}, {"description": "SMS one time password", "help": "SMS one time password.", "label": "Sms", "name": "sms"}]
VALID_BODY_TWO_FACTOR_NOTIFICATION: Literal[{"description": "Email notification for activation code", "help": "Email notification for activation code.", "label": "Email", "name": "email"}, {"description": "SMS notification for activation code", "help": "SMS notification for activation code.", "label": "Sms", "name": "sms"}]
VALID_BODY_SMS_SERVER: Literal[{"description": "Send SMS by FortiGuard", "help": "Send SMS by FortiGuard.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Send SMS by custom server", "help": "Send SMS by custom server.", "label": "Custom", "name": "custom"}]
VALID_BODY_AUTH_CONCURRENT_OVERRIDE: Literal[{"description": "Enable auth-concurrent-override", "help": "Enable auth-concurrent-override.", "label": "Enable", "name": "enable"}, {"description": "Disable auth-concurrent-override", "help": "Disable auth-concurrent-override.", "label": "Disable", "name": "disable"}]
VALID_BODY_USERNAME_SENSITIVITY: Literal[{"description": "Ignore case and accents", "help": "Ignore case and accents. Username at prompt not required to match case or accents.", "label": "Disable", "name": "disable"}, {"description": "Do not ignore case and accents", "help": "Do not ignore case and accents. Username at prompt must be an exact match.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_STATUS",
    "VALID_BODY_TYPE",
    "VALID_BODY_TWO_FACTOR",
    "VALID_BODY_TWO_FACTOR_AUTHENTICATION",
    "VALID_BODY_TWO_FACTOR_NOTIFICATION",
    "VALID_BODY_SMS_SERVER",
    "VALID_BODY_AUTH_CONCURRENT_OVERRIDE",
    "VALID_BODY_USERNAME_SENSITIVITY",
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