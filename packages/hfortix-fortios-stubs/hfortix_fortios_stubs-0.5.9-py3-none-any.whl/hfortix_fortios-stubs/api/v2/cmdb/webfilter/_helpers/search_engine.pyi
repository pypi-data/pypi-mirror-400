from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SAFESEARCH: Literal[{"description": "Site does not support safe search", "help": "Site does not support safe search.", "label": "Disable", "name": "disable"}, {"description": "Safe search selected with a parameter in the URL", "help": "Safe search selected with a parameter in the URL.", "label": "Url", "name": "url"}, {"description": "Safe search selected by search header (i", "help": "Safe search selected by search header (i.e. youtube.edu).", "label": "Header", "name": "header"}, {"description": "Perform URL FortiGuard check on translated URL", "help": "Perform URL FortiGuard check on translated URL.", "label": "Translate", "name": "translate"}, {"description": "Pattern to match YouTube channel ID", "help": "Pattern to match YouTube channel ID.", "label": "Yt Pattern", "name": "yt-pattern"}, {"description": "Perform IPS scan", "help": "Perform IPS scan.", "label": "Yt Scan", "name": "yt-scan"}, {"description": "Pattern to match YouTube video name", "help": "Pattern to match YouTube video name.", "label": "Yt Video", "name": "yt-video"}, {"description": "Pattern to match YouTube channel name", "help": "Pattern to match YouTube channel name.", "label": "Yt Channel", "name": "yt-channel"}]
VALID_BODY_CHARSET: Literal[{"description": "UTF-8 encoding", "help": "UTF-8 encoding.", "label": "Utf 8", "name": "utf-8"}, {"description": "GB2312 encoding", "help": "GB2312 encoding.", "label": "Gb2312", "name": "gb2312"}]

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
    "VALID_BODY_SAFESEARCH",
    "VALID_BODY_CHARSET",
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