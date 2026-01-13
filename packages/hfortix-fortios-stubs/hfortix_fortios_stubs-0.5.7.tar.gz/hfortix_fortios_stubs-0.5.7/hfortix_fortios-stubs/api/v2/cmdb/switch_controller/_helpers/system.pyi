from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_PARALLEL_PROCESS_OVERRIDE: Literal[{"description": "Disable maximum parallel process override", "help": "Disable maximum parallel process override.", "label": "Disable", "name": "disable"}, {"description": "Enable maximum parallel process override", "help": "Enable maximum parallel process override.", "label": "Enable", "name": "enable"}]
VALID_BODY_TUNNEL_MODE: Literal[{"description": "Least restrictive", "help": "Least restrictive. Supports the lowest levels of security but highest compatibility between all FortiSwitch and FortiGate devices. 3rd party certificates permitted.", "label": "Compatible", "name": "compatible"}, {"description": "Moderate level of security", "help": "Moderate level of security. 3rd party certificates permitted.", "label": "Moderate", "name": "moderate"}, {"description": "Highest level of security requirements", "help": "Highest level of security requirements. If enabled, the FortiGate device follows the same security mode requirements as in FIPS/CC mode.", "label": "Strict", "name": "strict"}]

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
    "VALID_BODY_PARALLEL_PROCESS_OVERRIDE",
    "VALID_BODY_TUNNEL_MODE",
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