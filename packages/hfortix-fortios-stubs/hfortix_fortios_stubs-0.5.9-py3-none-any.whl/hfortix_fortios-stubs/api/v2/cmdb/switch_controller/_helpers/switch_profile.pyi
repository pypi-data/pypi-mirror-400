from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_LOGIN_PASSWD_OVERRIDE: Literal[{"description": "Override a managed FortiSwitch\u0027s admin administrator password", "help": "Override a managed FortiSwitch\u0027s admin administrator password.", "label": "Enable", "name": "enable"}, {"description": "Use the managed FortiSwitch admin administrator account password", "help": "Use the managed FortiSwitch admin administrator account password.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOGIN: Literal[{"description": "Enable FortiSwitch serial console", "help": "Enable FortiSwitch serial console.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiSwitch serial console", "help": "Disable FortiSwitch serial console.", "label": "Disable", "name": "disable"}]
VALID_BODY_REVISION_BACKUP_ON_LOGOUT: Literal[{"description": "Enable automatic revision backup upon logout from FortiSwitch", "help": "Enable automatic revision backup upon logout from FortiSwitch.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic revision backup upon logout from FortiSwitch", "help": "Disable automatic revision backup upon logout from FortiSwitch.", "label": "Disable", "name": "disable"}]
VALID_BODY_REVISION_BACKUP_ON_UPGRADE: Literal[{"description": "Enable automatic revision backup upon FortiSwitch image upgrade", "help": "Enable automatic revision backup upon FortiSwitch image upgrade.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic revision backup upon FortiSwitch image upgrade", "help": "Disable automatic revision backup upon FortiSwitch image upgrade.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_LOGIN_PASSWD_OVERRIDE",
    "VALID_BODY_LOGIN",
    "VALID_BODY_REVISION_BACKUP_ON_LOGOUT",
    "VALID_BODY_REVISION_BACKUP_ON_UPGRADE",
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