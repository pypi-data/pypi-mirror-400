from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_FAIL_OPEN: Literal[{"description": "Enable IPS fail open", "help": "Enable IPS fail open.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS fail open", "help": "Disable IPS fail open.", "label": "Disable", "name": "disable"}]
VALID_BODY_DATABASE: Literal[{"description": "IPS regular database package", "help": "IPS regular database package.", "label": "Regular", "name": "regular"}, {"description": "IPS extended database package", "help": "IPS extended database package.", "label": "Extended", "name": "extended"}]
VALID_BODY_TRAFFIC_SUBMIT: Literal[{"description": "Enable traffic submit", "help": "Enable traffic submit.", "label": "Enable", "name": "enable"}, {"description": "Disable traffic submit", "help": "Disable traffic submit.", "label": "Disable", "name": "disable"}]
VALID_BODY_ANOMALY_MODE: Literal[{"description": "After an anomaly is detected, allow the number of packets per second according to the anomaly configuration", "help": "After an anomaly is detected, allow the number of packets per second according to the anomaly configuration.", "label": "Periodical", "name": "periodical"}, {"description": "Block packets once an anomaly is detected", "help": "Block packets once an anomaly is detected. Overrides individual anomaly settings.", "label": "Continuous", "name": "continuous"}]
VALID_BODY_SESSION_LIMIT_MODE: Literal[{"description": "Accurately count concurrent sessions, demands more resources", "help": "Accurately count concurrent sessions, demands more resources.", "label": "Accurate", "name": "accurate"}, {"description": "Use heuristics to estimate the number of concurrent sessions", "help": "Use heuristics to estimate the number of concurrent sessions. Acceptable in most cases.", "label": "Heuristic", "name": "heuristic"}]
VALID_BODY_SYNC_SESSION_TTL: Literal[{"description": "Enable use of kernel session TTL for IPS sessions", "help": "Enable use of kernel session TTL for IPS sessions.", "label": "Enable", "name": "enable"}, {"description": "Disable use of kernel session TTL for IPS sessions", "help": "Disable use of kernel session TTL for IPS sessions.", "label": "Disable", "name": "disable"}]
VALID_BODY_EXCLUDE_SIGNATURES: Literal[{"description": "No signatures excluded", "help": "No signatures excluded.", "label": "None", "name": "none"}, {"description": "Exclude ot signatures", "help": "Exclude ot signatures.", "label": "Ot", "name": "ot"}]
VALID_BODY_MACHINE_LEARNING_DETECTION: Literal[{"description": "Enable ML detection", "help": "Enable ML detection.", "label": "Enable", "name": "enable"}, {"description": "Disable ML detection", "help": "Disable ML detection.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_FAIL_OPEN",
    "VALID_BODY_DATABASE",
    "VALID_BODY_TRAFFIC_SUBMIT",
    "VALID_BODY_ANOMALY_MODE",
    "VALID_BODY_SESSION_LIMIT_MODE",
    "VALID_BODY_SYNC_SESSION_TTL",
    "VALID_BODY_EXCLUDE_SIGNATURES",
    "VALID_BODY_MACHINE_LEARNING_DETECTION",
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