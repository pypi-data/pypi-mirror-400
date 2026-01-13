from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_BANDWIDTH_UNIT: Literal[{"description": "Kilobits per second", "help": "Kilobits per second.", "label": "Kbps", "name": "kbps"}, {"description": "Megabits per second", "help": "Megabits per second.", "label": "Mbps", "name": "mbps"}, {"description": "Gigabits per second", "help": "Gigabits per second.", "label": "Gbps", "name": "gbps"}]
VALID_BODY_DIFFSERV_FORWARD: Literal[{"description": "Enable setting forward (original) traffic DiffServ", "help": "Enable setting forward (original) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting forward (original) traffic DiffServ", "help": "Disable setting forward (original) traffic DiffServ.", "label": "Disable", "name": "disable"}]
VALID_BODY_DIFFSERV_REVERSE: Literal[{"description": "Enable setting reverse (reply) traffic DiffServ", "help": "Enable setting reverse (reply) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting reverse (reply) traffic DiffServ", "help": "Disable setting reverse (reply) traffic DiffServ.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_DIFFSERV_FORWARD",
    "VALID_BODY_DIFFSERV_REVERSE",
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