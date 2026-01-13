from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_IP_LOCAL_LEARNING: Literal[{"description": "Enable IP address local learning", "help": "Enable IP address local learning.", "label": "Enable", "name": "enable"}, {"description": "Disable IP address local learning", "help": "Disable IP address local learning.", "label": "Disable", "name": "disable"}]
VALID_BODY_ARP_SUPPRESSION: Literal[{"description": "Enable ARP suppression", "help": "Enable ARP suppression.", "label": "Enable", "name": "enable"}, {"description": "Disable ARP suppression", "help": "Disable ARP suppression.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_IP_LOCAL_LEARNING",
    "VALID_BODY_ARP_SUPPRESSION",
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