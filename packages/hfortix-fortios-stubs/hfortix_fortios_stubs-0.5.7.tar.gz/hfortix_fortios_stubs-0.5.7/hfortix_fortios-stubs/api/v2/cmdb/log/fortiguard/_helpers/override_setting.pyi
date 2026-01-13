from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_OVERRIDE: Literal[{"description": "Override FortiCloud logging settings", "help": "Override FortiCloud logging settings.", "label": "Enable", "name": "enable"}, {"description": "Use global FortiCloud logging settings", "help": "Use global FortiCloud logging settings.", "label": "Disable", "name": "disable"}]
VALID_BODY_STATUS: Literal[{"description": "Enable logging to FortiCloud", "help": "Enable logging to FortiCloud.", "label": "Enable", "name": "enable"}, {"description": "Disable logging to FortiCloud", "help": "Disable logging to FortiCloud.", "label": "Disable", "name": "disable"}]
VALID_BODY_UPLOAD_OPTION: Literal[{"description": "Log to the hard disk and then upload logs to FortiCloud", "help": "Log to the hard disk and then upload logs to FortiCloud.", "label": "Store And Upload", "name": "store-and-upload"}, {"description": "Log directly to FortiCloud in real time", "help": "Log directly to FortiCloud in real time.", "label": "Realtime", "name": "realtime"}, {"description": "Log directly to FortiCloud at 1-minute intervals", "help": "Log directly to FortiCloud at 1-minute intervals.", "label": "1 Minute", "name": "1-minute"}, {"description": "Log directly to FortiCloud at 5-minute intervals", "help": "Log directly to FortiCloud at 5-minute intervals.", "label": "5 Minute", "name": "5-minute"}]
VALID_BODY_UPLOAD_INTERVAL: Literal[{"description": "Upload log files to FortiCloud once a day", "help": "Upload log files to FortiCloud once a day.", "label": "Daily", "name": "daily"}, {"description": "Upload log files to FortiCloud once a week", "help": "Upload log files to FortiCloud once a week.", "label": "Weekly", "name": "weekly"}, {"description": "Upload log files to FortiCloud once a month", "help": "Upload log files to FortiCloud once a month.", "label": "Monthly", "name": "monthly"}]
VALID_BODY_PRIORITY: Literal[{"description": "Set FortiCloud log transmission priority to default", "help": "Set FortiCloud log transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set FortiCloud log transmission priority to low", "help": "Set FortiCloud log transmission priority to low.", "label": "Low", "name": "low"}]
VALID_BODY_ACCESS_CONFIG: Literal[{"description": "Enable FortiCloud access to configuration and data", "help": "Enable FortiCloud access to configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud access to configuration and data", "help": "Disable FortiCloud access to configuration and data.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_OVERRIDE",
    "VALID_BODY_STATUS",
    "VALID_BODY_UPLOAD_OPTION",
    "VALID_BODY_UPLOAD_INTERVAL",
    "VALID_BODY_PRIORITY",
    "VALID_BODY_ACCESS_CONFIG",
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