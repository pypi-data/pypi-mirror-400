from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_RESOLVE_HOSTS: Literal[{"description": "Enable resolving IP addresses to hostnames", "help": "Enable resolving IP addresses to hostnames.", "label": "Enable", "name": "enable"}, {"description": "Disable resolving IP addresses to hostnames", "help": "Disable resolving IP addresses to hostnames.", "label": "Disable", "name": "disable"}]
VALID_BODY_RESOLVE_APPS: Literal[{"description": "Enable unknown applications on the GUI", "help": "Enable unknown applications on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable unknown applications on the GUI", "help": "Disable unknown applications on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_FORTIVIEW_UNSCANNED_APPS: Literal[{"description": "Enable showing unscanned traffic", "help": "Enable showing unscanned traffic.", "label": "Enable", "name": "enable"}, {"description": "Disable showing unscanned traffic", "help": "Disable showing unscanned traffic.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_RESOLVE_HOSTS",
    "VALID_BODY_RESOLVE_APPS",
    "VALID_BODY_FORTIVIEW_UNSCANNED_APPS",
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