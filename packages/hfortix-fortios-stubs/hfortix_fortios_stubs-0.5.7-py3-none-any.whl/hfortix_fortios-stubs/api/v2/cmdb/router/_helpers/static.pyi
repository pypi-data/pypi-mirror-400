from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable static route", "help": "Enable static route.", "label": "Enable", "name": "enable"}, {"description": "Disable static route", "help": "Disable static route.", "label": "Disable", "name": "disable"}]
VALID_BODY_BLACKHOLE: Literal[{"description": "Enable black hole", "help": "Enable black hole.", "label": "Enable", "name": "enable"}, {"description": "Disable black hole", "help": "Disable black hole.", "label": "Disable", "name": "disable"}]
VALID_BODY_DYNAMIC_GATEWAY: Literal[{"description": "Enable dynamic gateway", "help": "Enable dynamic gateway.", "label": "Enable", "name": "enable"}, {"description": "Disable dynamic gateway", "help": "Disable dynamic gateway.", "label": "Disable", "name": "disable"}]
VALID_BODY_LINK_MONITOR_EXEMPT: Literal[{"description": "Keep this static route when link monitor or health check is down", "help": "Keep this static route when link monitor or health check is down.", "label": "Enable", "name": "enable"}, {"description": "Withdraw this static route when link monitor or health check is down", "help": "Withdraw this static route when link monitor or health check is down. (default)", "label": "Disable", "name": "disable"}]
VALID_BODY_BFD: Literal[{"description": "Enable Bidirectional Forwarding Detection (BFD)", "help": "Enable Bidirectional Forwarding Detection (BFD).", "label": "Enable", "name": "enable"}, {"description": "Disable Bidirectional Forwarding Detection (BFD)", "help": "Disable Bidirectional Forwarding Detection (BFD).", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_BLACKHOLE",
    "VALID_BODY_DYNAMIC_GATEWAY",
    "VALID_BODY_LINK_MONITOR_EXEMPT",
    "VALID_BODY_BFD",
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