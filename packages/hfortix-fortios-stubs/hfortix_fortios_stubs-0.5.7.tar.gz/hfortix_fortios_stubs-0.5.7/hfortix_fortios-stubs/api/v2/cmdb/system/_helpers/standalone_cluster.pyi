from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_LAYER2_CONNECTION: Literal[{"description": "There exist layer 2 connections among FGSP members", "help": "There exist layer 2 connections among FGSP members.", "label": "Available", "name": "available"}, {"description": "There does not exist layer 2 connection among FGSP members", "help": "There does not exist layer 2 connection among FGSP members.", "label": "Unavailable", "name": "unavailable"}]
VALID_BODY_ENCRYPTION: Literal[{"description": "Enable encryption when synchronizing sessions", "help": "Enable encryption when synchronizing sessions.", "label": "Enable", "name": "enable"}, {"description": "Disable encryption when synchronizing sessions", "help": "Disable encryption when synchronizing sessions.", "label": "Disable", "name": "disable"}]
VALID_BODY_ASYMMETRIC_TRAFFIC_CONTROL: Literal[{"description": "Connection per second (CPS) preferred", "help": "Connection per second (CPS) preferred.", "label": "Cps Preferred", "name": "cps-preferred"}, {"description": "Strict anti-replay check", "help": "Strict anti-replay check.", "label": "Strict Anti Replay", "name": "strict-anti-replay"}]
VALID_BODY_HELPER_TRAFFIC_BOUNCE: Literal[{"description": "Enable helper related traffic bounce", "help": "Enable helper related traffic bounce.", "label": "Enable", "name": "enable"}, {"description": "Disable helper related traffic bounce", "help": "Disable helper related traffic bounce.", "label": "Disable", "name": "disable"}]
VALID_BODY_UTM_TRAFFIC_BOUNCE: Literal[{"description": "Enable UTM related traffic bounce", "help": "Enable UTM related traffic bounce.", "label": "Enable", "name": "enable"}, {"description": "Disable UTM related traffic bounce", "help": "Disable UTM related traffic bounce.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_LAYER2_CONNECTION",
    "VALID_BODY_ENCRYPTION",
    "VALID_BODY_ASYMMETRIC_TRAFFIC_CONTROL",
    "VALID_BODY_HELPER_TRAFFIC_BOUNCE",
    "VALID_BODY_UTM_TRAFFIC_BOUNCE",
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