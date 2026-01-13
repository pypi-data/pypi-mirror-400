from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_POE_STATUS: Literal[{"description": "Enable PoE status", "help": "Enable PoE status.", "label": "Enable", "name": "enable"}, {"description": "Disable PoE status", "help": "Disable PoE status.", "label": "Disable", "name": "disable"}]
VALID_BODY_IGMP_FLOOD_REPORT: Literal[{"description": "Enable IGMP flood report", "help": "Enable IGMP flood report.", "label": "Enable", "name": "enable"}, {"description": "Disable IGMP flood report", "help": "Disable IGMP flood report.", "label": "Disable", "name": "disable"}]
VALID_BODY_IGMP_FLOOD_TRAFFIC: Literal[{"description": "Enable IGMP flood traffic", "help": "Enable IGMP flood traffic.", "label": "Enable", "name": "enable"}, {"description": "Disable IGMP flood traffic", "help": "Disable IGMP flood traffic.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_POE_STATUS",
    "VALID_BODY_IGMP_FLOOD_REPORT",
    "VALID_BODY_IGMP_FLOOD_TRAFFIC",
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