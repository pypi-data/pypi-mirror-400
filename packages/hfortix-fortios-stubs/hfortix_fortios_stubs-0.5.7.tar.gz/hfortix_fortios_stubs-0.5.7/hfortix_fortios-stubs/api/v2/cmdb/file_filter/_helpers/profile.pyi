from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_FEATURE_SET: Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}]
VALID_BODY_LOG: Literal[{"description": "Disable logging", "help": "Disable logging.", "label": "Disable", "name": "disable"}, {"description": "Enable logging", "help": "Enable logging.", "label": "Enable", "name": "enable"}]
VALID_BODY_EXTENDED_LOG: Literal[{"description": "Disable extended logging", "help": "Disable extended logging.", "label": "Disable", "name": "disable"}, {"description": "Enable extended logging", "help": "Enable extended logging.", "label": "Enable", "name": "enable"}]
VALID_BODY_SCAN_ARCHIVE_CONTENTS: Literal[{"description": "Disable scanning archive contents", "help": "Disable scanning archive contents.", "label": "Disable", "name": "disable"}, {"description": "Enable scanning archive contents", "help": "Enable scanning archive contents.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_FEATURE_SET",
    "VALID_BODY_LOG",
    "VALID_BODY_EXTENDED_LOG",
    "VALID_BODY_SCAN_ARCHIVE_CONTENTS",
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