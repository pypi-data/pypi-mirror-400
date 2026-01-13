from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_MEDIA_STATUS: Literal[{"description": "Storage is enabled", "help": "Storage is enabled.", "label": "Enable", "name": "enable"}, {"description": "Storage is disabled", "help": "Storage is disabled.", "label": "Disable", "name": "disable"}, {"description": "Storage have some fail sector", "help": "Storage have some fail sector.", "label": "Fail", "name": "fail"}]
VALID_BODY_USAGE: Literal[{"help": "Use hard disk for logging.", "label": "Log", "name": "log"}, {"help": "Use hard disk for WAN Optimization.", "label": "Wanopt", "name": "wanopt"}]
VALID_BODY_WANOPT_MODE: Literal[{"help": "Use hard disk for WAN Optimization mix mode.", "label": "Mix", "name": "mix"}, {"help": "Use hard disk for WAN Optimization wanopt mode.", "label": "Wanopt", "name": "wanopt"}, {"help": "Use hard disk for WAN Optimization webcache mode.", "label": "Webcache", "name": "webcache"}]

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
    "VALID_BODY_MEDIA_STATUS",
    "VALID_BODY_USAGE",
    "VALID_BODY_WANOPT_MODE",
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