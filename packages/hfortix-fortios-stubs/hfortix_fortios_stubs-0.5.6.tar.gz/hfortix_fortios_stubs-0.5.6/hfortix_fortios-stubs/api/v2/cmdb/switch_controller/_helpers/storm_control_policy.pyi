from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STORM_CONTROL_MODE: Literal[{"description": "Apply Global or switch level storm control configuration", "help": "Apply Global or switch level storm control configuration.", "label": "Global", "name": "global"}, {"description": "Override global and switch level storm control to use port level configuration", "help": "Override global and switch level storm control to use port level configuration.", "label": "Override", "name": "override"}, {"description": "Disable storm control on the port entirely overriding global and switch level storm control", "help": "Disable storm control on the port entirely overriding global and switch level storm control.", "label": "Disabled", "name": "disabled"}]
VALID_BODY_UNKNOWN_UNICAST: Literal[{"description": "Enable storm control for unknown unicast traffic to drop packets which exceed configured rate limits", "help": "Enable storm control for unknown unicast traffic to drop packets which exceed configured rate limits.", "label": "Enable", "name": "enable"}, {"description": "Disable storm control for unknown unicast traffic to allow all packets", "help": "Disable storm control for unknown unicast traffic to allow all packets.", "label": "Disable", "name": "disable"}]
VALID_BODY_UNKNOWN_MULTICAST: Literal[{"description": "Enable storm control for unknown multicast traffic to drop packets which exceed configured rate limits", "help": "Enable storm control for unknown multicast traffic to drop packets which exceed configured rate limits.", "label": "Enable", "name": "enable"}, {"description": "Disable storm control for unknown multicast traffic to allow all packets", "help": "Disable storm control for unknown multicast traffic to allow all packets.", "label": "Disable", "name": "disable"}]
VALID_BODY_BROADCAST: Literal[{"description": "Enable storm control for broadcast traffic to drop packets which exceed configured rate limits", "help": "Enable storm control for broadcast traffic to drop packets which exceed configured rate limits.", "label": "Enable", "name": "enable"}, {"description": "Disable storm control for broadcast traffic to allow all packets", "help": "Disable storm control for broadcast traffic to allow all packets.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_STORM_CONTROL_MODE",
    "VALID_BODY_UNKNOWN_UNICAST",
    "VALID_BODY_UNKNOWN_MULTICAST",
    "VALID_BODY_BROADCAST",
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