from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable Fabric VPN", "help": "Enable Fabric VPN.", "label": "Enable", "name": "enable"}, {"description": "Disable Fabric VPN", "help": "Disable Fabric VPN.", "label": "Disable", "name": "disable"}]
VALID_BODY_SYNC_MODE: Literal[{"description": "Enable fabric led configuration synchronization", "help": "Enable fabric led configuration synchronization.", "label": "Enable", "name": "enable"}, {"description": "Disable fabric led configuration synchronization", "help": "Disable fabric led configuration synchronization.", "label": "Disable", "name": "disable"}]
VALID_BODY_POLICY_RULE: Literal[{"description": "Create health check policy automatically", "help": "Create health check policy automatically.", "label": "Health Check", "name": "health-check"}, {"description": "All policies will be created manually", "help": "All policies will be created manually.", "label": "Manual", "name": "manual"}, {"description": "Automatically create allow policies", "help": "Automatically create allow policies.", "label": "Auto", "name": "auto"}]
VALID_BODY_VPN_ROLE: Literal[{"description": "VPN hub", "help": "VPN hub.", "label": "Hub", "name": "hub"}, {"description": "VPN spoke", "help": "VPN spoke.", "label": "Spoke", "name": "spoke"}]

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
    "VALID_BODY_SYNC_MODE",
    "VALID_BODY_POLICY_RULE",
    "VALID_BODY_VPN_ROLE",
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