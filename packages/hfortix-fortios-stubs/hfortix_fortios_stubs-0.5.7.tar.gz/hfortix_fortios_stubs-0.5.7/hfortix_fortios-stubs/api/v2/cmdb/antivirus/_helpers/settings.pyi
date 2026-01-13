from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_MACHINE_LEARNING_DETECTION: Literal[{"description": "Enable machine learning based malware detection", "help": "Enable machine learning based malware detection.", "label": "Enable", "name": "enable"}, {"description": "Enable machine learning based malware detection for monitoring only", "help": "Enable machine learning based malware detection for monitoring only.", "label": "Monitor", "name": "monitor"}, {"description": "Disable machine learning based malware detection", "help": "Disable machine learning based malware detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_USE_EXTREME_DB: Literal[{"description": "Enable extreme AVDB", "help": "Enable extreme AVDB.", "label": "Enable", "name": "enable"}, {"description": "Disable extreme AVDB", "help": "Disable extreme AVDB.", "label": "Disable", "name": "disable"}]
VALID_BODY_GRAYWARE: Literal[{"description": "Enable grayware detection", "help": "Enable grayware detection.", "label": "Enable", "name": "enable"}, {"description": "Disable grayware detection", "help": "Disable grayware detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_CACHE_INFECTED_RESULT: Literal[{"description": "Enable cache of infected scan results", "help": "Enable cache of infected scan results.", "label": "Enable", "name": "enable"}, {"description": "Disable cache of infected scan results", "help": "Disable cache of infected scan results.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_MACHINE_LEARNING_DETECTION",
    "VALID_BODY_USE_EXTREME_DB",
    "VALID_BODY_GRAYWARE",
    "VALID_BODY_CACHE_INFECTED_RESULT",
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