from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SEVERITY: Literal[{"description": "info    low:low    medium:medium    high:high    critical:critical", "help": "info", "label": "Info", "name": "info"}, {"help": "low", "label": "Low", "name": "low"}, {"help": "medium", "label": "Medium", "name": "medium"}, {"help": "high", "label": "High", "name": "high"}, {"help": "critical", "label": "Critical", "name": "critical"}]
VALID_BODY_ACTION: Literal[{"description": "Allows session that match the profile", "help": "Allows session that match the profile.", "label": "Pass", "name": "pass"}, {"description": "Blocks sessions that match the profile", "help": "Blocks sessions that match the profile.", "label": "Block", "name": "block"}]
VALID_BODY_LOG: Literal[{"description": "Enable logging", "help": "Enable logging.", "label": "Enable", "name": "enable"}, {"description": "Disable logging", "help": "Disable logging.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_SEVERITY",
    "VALID_BODY_ACTION",
    "VALID_BODY_LOG",
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