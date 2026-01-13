from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SEVERITY: Literal[{"description": "Emergency level", "help": "Emergency level.", "label": "Emergency", "name": "emergency"}, {"description": "Alert level", "help": "Alert level.", "label": "Alert", "name": "alert"}, {"description": "Critical level", "help": "Critical level.", "label": "Critical", "name": "critical"}, {"description": "Error level", "help": "Error level.", "label": "Error", "name": "error"}, {"description": "Warning level", "help": "Warning level.", "label": "Warning", "name": "warning"}, {"description": "Notification level", "help": "Notification level.", "label": "Notification", "name": "notification"}, {"description": "Information level", "help": "Information level.", "label": "Information", "name": "information"}, {"description": "Debug level", "help": "Debug level.", "label": "Debug", "name": "debug"}]
VALID_BODY_FORWARD_TRAFFIC: Literal[{"description": "Enable forward traffic logging", "help": "Enable forward traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable forward traffic logging", "help": "Disable forward traffic logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOCAL_TRAFFIC: Literal[{"description": "Enable local in or out traffic logging", "help": "Enable local in or out traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local in or out traffic logging", "help": "Disable local in or out traffic logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_MULTICAST_TRAFFIC: Literal[{"description": "Enable multicast traffic logging", "help": "Enable multicast traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable multicast traffic logging", "help": "Disable multicast traffic logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_SNIFFER_TRAFFIC: Literal[{"description": "Enable sniffer traffic logging", "help": "Enable sniffer traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable sniffer traffic logging", "help": "Disable sniffer traffic logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_ZTNA_TRAFFIC: Literal[{"description": "Enable ztna traffic logging", "help": "Enable ztna traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable ztna traffic logging", "help": "Disable ztna traffic logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_HTTP_TRANSACTION: Literal[{"description": "Enable http transaction logging", "help": "Enable http transaction logging.", "label": "Enable", "name": "enable"}, {"description": "Disable http transaction logging", "help": "Disable http transaction logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_ANOMALY: Literal[{"description": "Enable anomaly logging", "help": "Enable anomaly logging.", "label": "Enable", "name": "enable"}, {"description": "Disable anomaly logging", "help": "Disable anomaly logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_VOIP: Literal[{"description": "Enable VoIP logging", "help": "Enable VoIP logging.", "label": "Enable", "name": "enable"}, {"description": "Disable VoIP logging", "help": "Disable VoIP logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_DLP_ARCHIVE: Literal[{"description": "Enable DLP archive logging", "help": "Enable DLP archive logging.", "label": "Enable", "name": "enable"}, {"description": "Disable DLP archive logging", "help": "Disable DLP archive logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_GTP: Literal[{"help": "Enable GTP messages logging.", "label": "Enable", "name": "enable"}, {"help": "Disable GTP messages logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_FORTI_SWITCH: Literal[{"description": "Enable Forti-Switch logging", "help": "Enable Forti-Switch logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Forti-Switch logging", "help": "Disable Forti-Switch logging.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_SEVERITY",
    "VALID_BODY_FORWARD_TRAFFIC",
    "VALID_BODY_LOCAL_TRAFFIC",
    "VALID_BODY_MULTICAST_TRAFFIC",
    "VALID_BODY_SNIFFER_TRAFFIC",
    "VALID_BODY_ZTNA_TRAFFIC",
    "VALID_BODY_HTTP_TRANSACTION",
    "VALID_BODY_ANOMALY",
    "VALID_BODY_VOIP",
    "VALID_BODY_DLP_ARCHIVE",
    "VALID_BODY_GTP",
    "VALID_BODY_FORTI_SWITCH",
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