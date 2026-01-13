from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable password policy", "help": "Enable password policy.", "label": "Enable", "name": "enable"}, {"description": "Disable password policy", "help": "Disable password policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_APPLY_TO: Literal[{"description": "Apply to administrator passwords", "help": "Apply to administrator passwords.", "label": "Admin Password", "name": "admin-password"}, {"description": "Apply to IPsec pre-shared keys", "help": "Apply to IPsec pre-shared keys.", "label": "Ipsec Preshared Key", "name": "ipsec-preshared-key"}]
VALID_BODY_EXPIRE_STATUS: Literal[{"description": "Passwords expire after expire-day days", "help": "Passwords expire after expire-day days.", "label": "Enable", "name": "enable"}, {"description": "Passwords do not expire", "help": "Passwords do not expire.", "label": "Disable", "name": "disable"}]
VALID_BODY_REUSE_PASSWORD: Literal[{"description": "Administrators are allowed to reuse the same password up to a limit", "help": "Administrators are allowed to reuse the same password up to a limit.", "label": "Enable", "name": "enable"}, {"description": "Administrators must create a new password", "help": "Administrators must create a new password.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOGIN_LOCKOUT_UPON_WEAKER_ENCRYPTION: Literal[{"description": "Enable administrative user login lockout upon downgrade", "help": "Enable administrative user login lockout upon downgrade.", "label": "Enable", "name": "enable"}, {"description": "Disable administrative user login lockout upon downgrade", "help": "Disable administrative user login lockout upon downgrade.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_APPLY_TO",
    "VALID_BODY_EXPIRE_STATUS",
    "VALID_BODY_REUSE_PASSWORD",
    "VALID_BODY_LOGIN_LOCKOUT_UPON_WEAKER_ENCRYPTION",
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