from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_MANDATORY_CA_VERIFY: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_CN_TYPE: Literal[{"description": "Normal string", "help": "Normal string.", "label": "String", "name": "string"}, {"description": "Email address", "help": "Email address.", "label": "Email", "name": "email"}, {"description": "Fully Qualified Domain Name", "help": "Fully Qualified Domain Name.", "label": "Fqdn", "name": "FQDN"}, {"description": "IPv4 address", "help": "IPv4 address.", "label": "Ipv4", "name": "ipv4"}, {"description": "IPv6 address", "help": "IPv6 address.", "label": "Ipv6", "name": "ipv6"}]
VALID_BODY_MFA_MODE: Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "Specified username/password", "help": "Specified username/password.", "label": "Password", "name": "password"}, {"description": "Subject identity extracted from certificate", "help": "Subject identity extracted from certificate.", "label": "Subject Identity", "name": "subject-identity"}]
VALID_BODY_TWO_FACTOR: Literal[{"description": "Enable 2-factor authentication", "help": "Enable 2-factor authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable 2-factor authentication", "help": "Disable 2-factor authentication.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_MANDATORY_CA_VERIFY",
    "VALID_BODY_CN_TYPE",
    "VALID_BODY_MFA_MODE",
    "VALID_BODY_TWO_FACTOR",
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