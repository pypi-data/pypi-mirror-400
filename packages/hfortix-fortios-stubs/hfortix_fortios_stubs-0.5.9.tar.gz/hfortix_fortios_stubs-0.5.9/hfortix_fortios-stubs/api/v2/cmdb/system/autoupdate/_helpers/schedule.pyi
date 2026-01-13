from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_FREQUENCY: Literal[{"description": "Time interval", "help": "Time interval.", "label": "Every", "name": "every"}, {"description": "Every day", "help": "Every day.", "label": "Daily", "name": "daily"}, {"description": "Every week", "help": "Every week.", "label": "Weekly", "name": "weekly"}, {"description": "Update automatically within every one hour period", "help": "Update automatically within every one hour period.", "label": "Automatic", "name": "automatic"}]
VALID_BODY_DAY: Literal[{"description": "Update every Sunday", "help": "Update every Sunday.", "label": "Sunday", "name": "Sunday"}, {"description": "Update every Monday", "help": "Update every Monday.", "label": "Monday", "name": "Monday"}, {"description": "Update every Tuesday", "help": "Update every Tuesday.", "label": "Tuesday", "name": "Tuesday"}, {"description": "Update every Wednesday", "help": "Update every Wednesday.", "label": "Wednesday", "name": "Wednesday"}, {"description": "Update every Thursday", "help": "Update every Thursday.", "label": "Thursday", "name": "Thursday"}, {"description": "Update every Friday", "help": "Update every Friday.", "label": "Friday", "name": "Friday"}, {"description": "Update every Saturday", "help": "Update every Saturday.", "label": "Saturday", "name": "Saturday"}]

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
    "VALID_BODY_FREQUENCY",
    "VALID_BODY_DAY",
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