from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SERVER_STATUS: Literal[{"description": "Enable syslog server", "help": "Enable syslog server.", "label": "Enable", "name": "enable"}, {"description": "Disable syslog server", "help": "Disable syslog server.", "label": "Disable", "name": "disable"}]
VALID_BODY_SERVER_TYPE: Literal[{"description": "Standard syslog server hosted on an server endpoint", "help": "Standard syslog server hosted on an server endpoint.", "label": "Standard", "name": "standard"}, {"description": "Syslog server hosted on a FortiAnalyzer device", "help": "Syslog server hosted on a FortiAnalyzer device.", "label": "Fortianalyzer", "name": "fortianalyzer"}]
VALID_BODY_LOG_LEVEL: Literal[{"description": "Level 0    alert:Level 1    critical:Level 2    error:Level 3    warning:Level 4    notification:Level 5    information:Level 6    debugging:Level 7", "help": "Level 0", "label": "Emergency", "name": "emergency"}, {"help": "Level 1", "label": "Alert", "name": "alert"}, {"help": "Level 2", "label": "Critical", "name": "critical"}, {"help": "Level 3", "label": "Error", "name": "error"}, {"help": "Level 4", "label": "Warning", "name": "warning"}, {"help": "Level 5", "label": "Notification", "name": "notification"}, {"help": "Level 6", "label": "Information", "name": "information"}, {"help": "Level 7", "label": "Debugging", "name": "debugging"}]

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
    "VALID_BODY_SERVER_STATUS",
    "VALID_BODY_SERVER_TYPE",
    "VALID_BODY_LOG_LEVEL",
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