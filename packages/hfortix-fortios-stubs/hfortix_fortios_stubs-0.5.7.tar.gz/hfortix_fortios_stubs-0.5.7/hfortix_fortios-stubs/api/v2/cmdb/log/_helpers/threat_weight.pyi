from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable the threat weight feature", "help": "Enable the threat weight feature.", "label": "Enable", "name": "enable"}, {"description": "Disable the threat weight feature", "help": "Disable the threat weight feature.", "label": "Disable", "name": "disable"}]
VALID_BODY_BLOCKED_CONNECTION: Literal[{"description": "Disable threat weight scoring for blocked connections", "help": "Disable threat weight scoring for blocked connections.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for blocked connections", "help": "Use the low level score for blocked connections.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for blocked connections", "help": "Use the medium level score for blocked connections.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for blocked connections", "help": "Use the high level score for blocked connections.", "label": "High", "name": "high"}, {"description": "Use the critical level score for blocked connections", "help": "Use the critical level score for blocked connections.", "label": "Critical", "name": "critical"}]
VALID_BODY_FAILED_CONNECTION: Literal[{"description": "Disable threat weight scoring for failed connections", "help": "Disable threat weight scoring for failed connections.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for failed connections", "help": "Use the low level score for failed connections.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for failed connections", "help": "Use the medium level score for failed connections.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for failed connections", "help": "Use the high level score for failed connections.", "label": "High", "name": "high"}, {"description": "Use the critical level score for failed connections", "help": "Use the critical level score for failed connections.", "label": "Critical", "name": "critical"}]
VALID_BODY_URL_BLOCK_DETECTED: Literal[{"description": "Disable threat weight scoring for URL blocking", "help": "Disable threat weight scoring for URL blocking.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for URL blocking", "help": "Use the low level score for URL blocking.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for URL blocking", "help": "Use the medium level score for URL blocking.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for URL blocking", "help": "Use the high level score for URL blocking.", "label": "High", "name": "high"}, {"description": "Use the critical level score for URL blocking", "help": "Use the critical level score for URL blocking.", "label": "Critical", "name": "critical"}]
VALID_BODY_BOTNET_CONNECTION_DETECTED: Literal[{"description": "Disable threat weight scoring for detected botnet connections", "help": "Disable threat weight scoring for detected botnet connections.", "label": "Disable", "name": "disable"}, {"description": "Use the low level score for detected botnet connections", "help": "Use the low level score for detected botnet connections.", "label": "Low", "name": "low"}, {"description": "Use the medium level score for detected botnet connections", "help": "Use the medium level score for detected botnet connections.", "label": "Medium", "name": "medium"}, {"description": "Use the high level score for detected botnet connections", "help": "Use the high level score for detected botnet connections.", "label": "High", "name": "high"}, {"description": "Use the critical level score for detected botnet connections", "help": "Use the critical level score for detected botnet connections.", "label": "Critical", "name": "critical"}]

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
    "VALID_BODY_BLOCKED_CONNECTION",
    "VALID_BODY_FAILED_CONNECTION",
    "VALID_BODY_URL_BLOCK_DETECTED",
    "VALID_BODY_BOTNET_CONNECTION_DETECTED",
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