from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"description": "Microsoft Graph server", "help": "Microsoft Graph server.", "label": "Ms Graph", "name": "ms-graph"}]
VALID_BODY_VERSION: Literal[{"help": "MS Graph REST API v1.0.", "label": "V1.0", "name": "v1.0"}, {"description": "MS Graph REST API beta (debug build only)", "help": "MS Graph REST API beta (debug build only).", "label": "Beta", "name": "beta"}]
VALID_BODY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]
VALID_BODY_SERVER_IDENTITY_CHECK: Literal[{"description": "Do not check server\u0027s identity against its certificate and subject alternative name(s)", "help": "Do not check server\u0027s identity against its certificate and subject alternative name(s).", "label": "Disable", "name": "disable"}, {"description": "Check server\u0027s identity against its certificate and subject alternative name(s)", "help": "Check server\u0027s identity against its certificate and subject alternative name(s).", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_TYPE",
    "VALID_BODY_VERSION",
    "VALID_BODY_INTERFACE_SELECT_METHOD",
    "VALID_BODY_SERVER_IDENTITY_CHECK",
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