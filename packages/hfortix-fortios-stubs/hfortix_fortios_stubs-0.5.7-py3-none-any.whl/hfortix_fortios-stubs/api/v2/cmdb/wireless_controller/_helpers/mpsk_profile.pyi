from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_MPSK_EXTERNAL_SERVER_AUTH: Literal[{"description": "Enable MPSK external server authentication", "help": "Enable MPSK external server authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable MPSK external server authentication", "help": "Disable MPSK external server authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_MPSK_TYPE: Literal[{"description": "WPA2 personal", "help": "WPA2 personal.", "label": "Wpa2 Personal", "name": "wpa2-personal"}, {"description": "WPA3 SAE", "help": "WPA3 SAE.", "label": "Wpa3 Sae", "name": "wpa3-sae"}, {"description": "WPA3 SAE transition", "help": "WPA3 SAE transition.", "label": "Wpa3 Sae Transition", "name": "wpa3-sae-transition"}]

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
    "VALID_BODY_MPSK_EXTERNAL_SERVER_AUTH",
    "VALID_BODY_MPSK_TYPE",
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