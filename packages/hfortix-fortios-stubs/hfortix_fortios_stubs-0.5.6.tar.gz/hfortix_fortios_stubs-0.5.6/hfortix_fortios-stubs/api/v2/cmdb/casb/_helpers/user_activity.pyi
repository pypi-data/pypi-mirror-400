from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_TYPE: Literal[{"description": "Built-in CASB user-activity", "help": "Built-in CASB user-activity.", "label": "Built In", "name": "built-in"}, {"description": "User customized CASB user-activity", "help": "User customized CASB user-activity.", "label": "Customized", "name": "customized"}]
VALID_BODY_CATEGORY: Literal[{"description": "Activity control", "help": "Activity control.", "label": "Activity Control", "name": "activity-control"}, {"description": "Tenant control", "help": "Tenant control.", "label": "Tenant Control", "name": "tenant-control"}, {"description": "Domain control", "help": "Domain control.", "label": "Domain Control", "name": "domain-control"}, {"description": "Safe search control", "help": "Safe search control.", "label": "Safe Search Control", "name": "safe-search-control"}, {"description": "Advanced tenant control", "help": "Advanced tenant control.", "label": "Advanced Tenant Control", "name": "advanced-tenant-control"}, {"description": "User customized category", "help": "User customized category.", "label": "Other", "name": "other"}]
VALID_BODY_MATCH_STRATEGY: Literal[{"description": "Match user activity using a logical AND operator", "help": "Match user activity using a logical AND operator.", "label": "And", "name": "and"}, {"description": "Match user activity using a logical OR operator", "help": "Match user activity using a logical OR operator.", "label": "Or", "name": "or"}]

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
    "VALID_BODY_STATUS",
    "VALID_BODY_TYPE",
    "VALID_BODY_CATEGORY",
    "VALID_BODY_MATCH_STRATEGY",
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