from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_REMOTE_AUTH: Literal[{"description": "Enable remote authentication", "help": "Enable remote authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable remote authentication", "help": "Disable remote authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_WILDCARD: Literal[{"description": "Enable username wildcard", "help": "Enable username wildcard.", "label": "Enable", "name": "enable"}, {"description": "Disable username wildcard", "help": "Disable username wildcard.", "label": "Disable", "name": "disable"}]
VALID_BODY_PEER_AUTH: Literal[{"description": "Enable peer", "help": "Enable peer.", "label": "Enable", "name": "enable"}, {"description": "Disable peer", "help": "Disable peer.", "label": "Disable", "name": "disable"}]
VALID_BODY_ALLOW_REMOVE_ADMIN_SESSION: Literal[{"description": "Enable allow-remove option", "help": "Enable allow-remove option.", "label": "Enable", "name": "enable"}, {"description": "Disable allow-remove option", "help": "Disable allow-remove option.", "label": "Disable", "name": "disable"}]
VALID_BODY_ACCPROFILE_OVERRIDE: Literal[{"description": "Enable access profile override", "help": "Enable access profile override.", "label": "Enable", "name": "enable"}, {"description": "Disable access profile override", "help": "Disable access profile override.", "label": "Disable", "name": "disable"}]
VALID_BODY_VDOM_OVERRIDE: Literal[{"description": "Enable VDOM override", "help": "Enable VDOM override.", "label": "Enable", "name": "enable"}, {"description": "Disable VDOM override", "help": "Disable VDOM override.", "label": "Disable", "name": "disable"}]
VALID_BODY_FORCE_PASSWORD_CHANGE: Literal[{"description": "Enable force password change on next login", "help": "Enable force password change on next login.", "label": "Enable", "name": "enable"}, {"description": "Disable force password change on next login", "help": "Disable force password change on next login.", "label": "Disable", "name": "disable"}]
VALID_BODY_TWO_FACTOR: Literal[{"description": "Disable two-factor authentication", "help": "Disable two-factor authentication.", "label": "Disable", "name": "disable"}, {"description": "Use FortiToken or FortiToken mobile two-factor authentication", "help": "Use FortiToken or FortiToken mobile two-factor authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "FortiToken Cloud Service", "help": "FortiToken Cloud Service.", "label": "Fortitoken Cloud", "name": "fortitoken-cloud"}, {"description": "Send a two-factor authentication code to the configured email-to email address", "help": "Send a two-factor authentication code to the configured email-to email address.", "label": "Email", "name": "email"}, {"description": "Send a two-factor authentication code to the configured sms-server and sms-phone", "help": "Send a two-factor authentication code to the configured sms-server and sms-phone.", "label": "Sms", "name": "sms"}]
VALID_BODY_TWO_FACTOR_AUTHENTICATION: Literal[{"description": "FortiToken authentication", "help": "FortiToken authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "Email one time password", "help": "Email one time password.", "label": "Email", "name": "email"}, {"description": "SMS one time password", "help": "SMS one time password.", "label": "Sms", "name": "sms"}]
VALID_BODY_TWO_FACTOR_NOTIFICATION: Literal[{"description": "Email notification for activation code", "help": "Email notification for activation code.", "label": "Email", "name": "email"}, {"description": "SMS notification for activation code", "help": "SMS notification for activation code.", "label": "Sms", "name": "sms"}]
VALID_BODY_SMS_SERVER: Literal[{"description": "Send SMS by FortiGuard", "help": "Send SMS by FortiGuard.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Send SMS by custom server", "help": "Send SMS by custom server.", "label": "Custom", "name": "custom"}]
VALID_BODY_GUEST_AUTH: Literal[{"description": "Disable guest authentication", "help": "Disable guest authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable guest authentication", "help": "Enable guest authentication.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_REMOTE_AUTH",
    "VALID_BODY_WILDCARD",
    "VALID_BODY_PEER_AUTH",
    "VALID_BODY_ALLOW_REMOVE_ADMIN_SESSION",
    "VALID_BODY_ACCPROFILE_OVERRIDE",
    "VALID_BODY_VDOM_OVERRIDE",
    "VALID_BODY_FORCE_PASSWORD_CHANGE",
    "VALID_BODY_TWO_FACTOR",
    "VALID_BODY_TWO_FACTOR_AUTHENTICATION",
    "VALID_BODY_TWO_FACTOR_NOTIFICATION",
    "VALID_BODY_SMS_SERVER",
    "VALID_BODY_GUEST_AUTH",
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