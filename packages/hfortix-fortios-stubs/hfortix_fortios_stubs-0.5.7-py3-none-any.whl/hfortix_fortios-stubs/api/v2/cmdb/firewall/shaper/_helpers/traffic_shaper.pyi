from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_BANDWIDTH_UNIT: Literal[{"description": "Kilobits per second", "help": "Kilobits per second.", "label": "Kbps", "name": "kbps"}, {"description": "Megabits per second", "help": "Megabits per second.", "label": "Mbps", "name": "mbps"}, {"description": "Gigabits per second", "help": "Gigabits per second.", "label": "Gbps", "name": "gbps"}]
VALID_BODY_PRIORITY: Literal[{"description": "Low priority", "help": "Low priority.", "label": "Low", "name": "low"}, {"description": "Medium priority", "help": "Medium priority.", "label": "Medium", "name": "medium"}, {"description": "High priority", "help": "High priority.", "label": "High", "name": "high"}]
VALID_BODY_PER_POLICY: Literal[{"description": "All referring policies share one traffic shaper", "help": "All referring policies share one traffic shaper.", "label": "Disable", "name": "disable"}, {"description": "Each referring policy has its own traffic shaper", "help": "Each referring policy has its own traffic shaper.", "label": "Enable", "name": "enable"}]
VALID_BODY_DIFFSERV: Literal[{"description": "Enable setting traffic DiffServ", "help": "Enable setting traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting traffic DiffServ", "help": "Disable setting traffic DiffServ.", "label": "Disable", "name": "disable"}]
VALID_BODY_DSCP_MARKING_METHOD: Literal[{"description": "Multistage marking", "help": "Multistage marking.", "label": "Multi Stage", "name": "multi-stage"}, {"description": "Static marking", "help": "Static marking.", "label": "Static", "name": "static"}]
VALID_BODY_COS_MARKING: Literal[{"description": "Enable VLAN CoS marking", "help": "Enable VLAN CoS marking.", "label": "Enable", "name": "enable"}, {"description": "Disable VLAN CoS marking", "help": "Disable VLAN CoS marking.", "label": "Disable", "name": "disable"}]
VALID_BODY_COS_MARKING_METHOD: Literal[{"description": "Multi stage marking", "help": "Multi stage marking.", "label": "Multi Stage", "name": "multi-stage"}, {"description": "Static marking", "help": "Static marking.", "label": "Static", "name": "static"}]

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
    "VALID_BODY_BANDWIDTH_UNIT",
    "VALID_BODY_PRIORITY",
    "VALID_BODY_PER_POLICY",
    "VALID_BODY_DIFFSERV",
    "VALID_BODY_DSCP_MARKING_METHOD",
    "VALID_BODY_COS_MARKING",
    "VALID_BODY_COS_MARKING_METHOD",
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