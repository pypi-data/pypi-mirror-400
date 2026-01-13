from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_DAY: Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}, {"description": "None", "help": "None.", "label": "None", "name": "none"}]
VALID_BODY_LABEL_DAY: Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "1 AM - 4 AM    early-morning:4 AM - 7 AM", "help": "1 AM - 4 AM", "label": "Over Night", "name": "over-night"}, {"help": "4 AM - 7 AM.", "label": "Early Morning", "name": "early-morning"}, {"description": "7 AM - 10 AM", "help": "7 AM - 10 AM.", "label": "Morning", "name": "morning"}, {"description": "10 AM - 1 PM", "help": "10 AM - 1 PM.", "label": "Midday", "name": "midday"}, {"description": "1 PM - 4 PM", "help": "1 PM - 4 PM.", "label": "Afternoon", "name": "afternoon"}, {"description": "4 PM - 7 PM", "help": "4 PM - 7 PM.", "label": "Evening", "name": "evening"}, {"description": "7 PM - 10 PM", "help": "7 PM - 10 PM.", "label": "Night", "name": "night"}, {"description": "10 PM - 1 AM", "help": "10 PM - 1 AM.", "label": "Late Night", "name": "late-night"}]
VALID_BODY_FABRIC_OBJECT: Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_DAY",
    "VALID_BODY_LABEL_DAY",
    "VALID_BODY_FABRIC_OBJECT",
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