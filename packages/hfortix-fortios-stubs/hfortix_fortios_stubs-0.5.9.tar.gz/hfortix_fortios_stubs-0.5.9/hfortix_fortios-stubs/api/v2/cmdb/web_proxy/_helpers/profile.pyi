from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_HEADER_CLIENT_IP: Literal[{"description": "Forward the same HTTP header", "help": "Forward the same HTTP header.", "label": "Pass", "name": "pass"}, {"description": "Add the HTTP header", "help": "Add the HTTP header.", "label": "Add", "name": "add"}, {"description": "Remove the HTTP header", "help": "Remove the HTTP header.", "label": "Remove", "name": "remove"}]
VALID_BODY_HEADER_VIA_REQUEST: Literal[{"description": "Forward the same HTTP header", "help": "Forward the same HTTP header.", "label": "Pass", "name": "pass"}, {"description": "Add the HTTP header", "help": "Add the HTTP header.", "label": "Add", "name": "add"}, {"description": "Remove the HTTP header", "help": "Remove the HTTP header.", "label": "Remove", "name": "remove"}]
VALID_BODY_HEADER_VIA_RESPONSE: Literal[{"description": "Forward the same HTTP header", "help": "Forward the same HTTP header.", "label": "Pass", "name": "pass"}, {"description": "Add the HTTP header", "help": "Add the HTTP header.", "label": "Add", "name": "add"}, {"description": "Remove the HTTP header", "help": "Remove the HTTP header.", "label": "Remove", "name": "remove"}]
VALID_BODY_HEADER_CLIENT_CERT: Literal[{"description": "Forward the same HTTP header", "help": "Forward the same HTTP header.", "label": "Pass", "name": "pass"}, {"description": "Add the HTTP header", "help": "Add the HTTP header.", "label": "Add", "name": "add"}, {"description": "Remove the HTTP header", "help": "Remove the HTTP header.", "label": "Remove", "name": "remove"}]
VALID_BODY_HEADER_X_FORWARDED_FOR: Literal[{"description": "Forward the same HTTP header", "help": "Forward the same HTTP header.", "label": "Pass", "name": "pass"}, {"description": "Add the HTTP header", "help": "Add the HTTP header.", "label": "Add", "name": "add"}, {"description": "Remove the HTTP header", "help": "Remove the HTTP header.", "label": "Remove", "name": "remove"}]
VALID_BODY_HEADER_X_FORWARDED_CLIENT_CERT: Literal[{"description": "Forward the same HTTP header", "help": "Forward the same HTTP header.", "label": "Pass", "name": "pass"}, {"description": "Add the HTTP header", "help": "Add the HTTP header.", "label": "Add", "name": "add"}, {"description": "Remove the HTTP header", "help": "Remove the HTTP header.", "label": "Remove", "name": "remove"}]
VALID_BODY_HEADER_FRONT_END_HTTPS: Literal[{"description": "Forward the same HTTP header", "help": "Forward the same HTTP header.", "label": "Pass", "name": "pass"}, {"description": "Add the HTTP header", "help": "Add the HTTP header.", "label": "Add", "name": "add"}, {"description": "Remove the HTTP header", "help": "Remove the HTTP header.", "label": "Remove", "name": "remove"}]
VALID_BODY_HEADER_X_AUTHENTICATED_USER: Literal[{"description": "Forward the same HTTP header", "help": "Forward the same HTTP header.", "label": "Pass", "name": "pass"}, {"description": "Add the HTTP header", "help": "Add the HTTP header.", "label": "Add", "name": "add"}, {"description": "Remove the HTTP header", "help": "Remove the HTTP header.", "label": "Remove", "name": "remove"}]
VALID_BODY_HEADER_X_AUTHENTICATED_GROUPS: Literal[{"description": "Forward the same HTTP header", "help": "Forward the same HTTP header.", "label": "Pass", "name": "pass"}, {"description": "Add the HTTP header", "help": "Add the HTTP header.", "label": "Add", "name": "add"}, {"description": "Remove the HTTP header", "help": "Remove the HTTP header.", "label": "Remove", "name": "remove"}]
VALID_BODY_STRIP_ENCODING: Literal[{"description": "Enable stripping of unsupported encoding from the request header", "help": "Enable stripping of unsupported encoding from the request header.", "label": "Enable", "name": "enable"}, {"description": "Disable stripping of unsupported encoding from the request header", "help": "Disable stripping of unsupported encoding from the request header.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOG_HEADER_CHANGE: Literal[{"description": "Enable Enable/disable logging HTTP header changes", "help": "Enable Enable/disable logging HTTP header changes.", "label": "Enable", "name": "enable"}, {"description": "Disable Enable/disable logging HTTP header changes", "help": "Disable Enable/disable logging HTTP header changes.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_HEADER_CLIENT_IP",
    "VALID_BODY_HEADER_VIA_REQUEST",
    "VALID_BODY_HEADER_VIA_RESPONSE",
    "VALID_BODY_HEADER_CLIENT_CERT",
    "VALID_BODY_HEADER_X_FORWARDED_FOR",
    "VALID_BODY_HEADER_X_FORWARDED_CLIENT_CERT",
    "VALID_BODY_HEADER_FRONT_END_HTTPS",
    "VALID_BODY_HEADER_X_AUTHENTICATED_USER",
    "VALID_BODY_HEADER_X_AUTHENTICATED_GROUPS",
    "VALID_BODY_STRIP_ENCODING",
    "VALID_BODY_LOG_HEADER_CHANGE",
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