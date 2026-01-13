from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_INTER_CONTROLLER_MODE: Literal[{"description": "Disable inter-controller mode", "help": "Disable inter-controller mode.", "label": "Disable", "name": "disable"}, {"description": "Enable layer 2 roaming support between inter-controllers", "help": "Enable layer 2 roaming support between inter-controllers.", "label": "L2 Roaming", "name": "l2-roaming"}, {"description": "Enable 1+1 fast failover mode", "help": "Enable 1+1 fast failover mode.", "label": "1+1", "name": "1+1"}]
VALID_BODY_L3_ROAMING: Literal[{"description": "Enable layer 3 roaming", "help": "Enable layer 3 roaming.", "label": "Enable", "name": "enable"}, {"description": "Disable layer 3 roaming", "help": "Disable layer 3 roaming.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTER_CONTROLLER_PRI: Literal[{"description": "Primary fast failover mode", "help": "Primary fast failover mode.", "label": "Primary", "name": "primary"}, {"description": "Secondary fast failover mode", "help": "Secondary fast failover mode.", "label": "Secondary", "name": "secondary"}]

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
    "VALID_BODY_INTER_CONTROLLER_MODE",
    "VALID_BODY_L3_ROAMING",
    "VALID_BODY_INTER_CONTROLLER_PRI",
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