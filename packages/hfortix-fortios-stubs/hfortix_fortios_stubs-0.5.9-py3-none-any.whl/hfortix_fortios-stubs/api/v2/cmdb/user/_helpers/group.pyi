from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_GROUP_TYPE: Literal[{"description": "Firewall", "help": "Firewall.", "label": "Firewall", "name": "firewall"}, {"description": "Fortinet Single Sign-On Service", "help": "Fortinet Single Sign-On Service.", "label": "Fsso Service", "name": "fsso-service"}, {"description": "RADIUS based Single Sign-On Service", "help": "RADIUS based Single Sign-On Service.", "label": "Rsso", "name": "rsso"}, {"description": "Guest", "help": "Guest.", "label": "Guest", "name": "guest"}]
VALID_BODY_AUTH_CONCURRENT_OVERRIDE: Literal[{"description": "Enable auth-concurrent-override", "help": "Enable auth-concurrent-override.", "label": "Enable", "name": "enable"}, {"description": "Disable auth-concurrent-override", "help": "Disable auth-concurrent-override.", "label": "Disable", "name": "disable"}]
VALID_BODY_USER_ID: Literal[{"description": "Email address", "help": "Email address.", "label": "Email", "name": "email"}, {"description": "Automatically generate", "help": "Automatically generate.", "label": "Auto Generate", "name": "auto-generate"}, {"description": "Specify", "help": "Specify.", "label": "Specify", "name": "specify"}]
VALID_BODY_PASSWORD: Literal[{"description": "Automatically generate", "help": "Automatically generate.", "label": "Auto Generate", "name": "auto-generate"}, {"description": "Specify", "help": "Specify.", "label": "Specify", "name": "specify"}, {"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}]
VALID_BODY_USER_NAME: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}]
VALID_BODY_SPONSOR: Literal[{"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Disabled", "help": "Disabled.", "label": "Disabled", "name": "disabled"}]
VALID_BODY_COMPANY: Literal[{"description": "Optional", "help": "Optional.", "label": "Optional", "name": "optional"}, {"description": "Mandatory", "help": "Mandatory.", "label": "Mandatory", "name": "mandatory"}, {"description": "Disabled", "help": "Disabled.", "label": "Disabled", "name": "disabled"}]
VALID_BODY_EMAIL: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}]
VALID_BODY_MOBILE_PHONE: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}]
VALID_BODY_SMS_SERVER: Literal[{"description": "Send SMS by FortiGuard", "help": "Send SMS by FortiGuard.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Send SMS by custom server", "help": "Send SMS by custom server.", "label": "Custom", "name": "custom"}]
VALID_BODY_EXPIRE_TYPE: Literal[{"description": "Immediately", "help": "Immediately.", "label": "Immediately", "name": "immediately"}, {"description": "First successful login", "help": "First successful login.", "label": "First Successful Login", "name": "first-successful-login"}]
VALID_BODY_MULTIPLE_GUEST_ADD: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_GROUP_TYPE",
    "VALID_BODY_AUTH_CONCURRENT_OVERRIDE",
    "VALID_BODY_USER_ID",
    "VALID_BODY_PASSWORD",
    "VALID_BODY_USER_NAME",
    "VALID_BODY_SPONSOR",
    "VALID_BODY_COMPANY",
    "VALID_BODY_EMAIL",
    "VALID_BODY_MOBILE_PHONE",
    "VALID_BODY_SMS_SERVER",
    "VALID_BODY_EXPIRE_TYPE",
    "VALID_BODY_MULTIPLE_GUEST_ADD",
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