from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Disable scheduled speed test", "help": "Disable scheduled speed test.", "label": "Disable", "name": "disable"}, {"description": "Enable scheduled speed test", "help": "Enable scheduled speed test.", "label": "Enable", "name": "enable"}]
VALID_BODY_MODE: Literal[{"description": "Protocol UDP for speed test", "help": "Protocol UDP for speed test.", "label": "Udp", "name": "UDP"}, {"description": "Protocol TCP for speed test", "help": "Protocol TCP for speed test.", "label": "Tcp", "name": "TCP"}, {"description": "Dynamically selects TCP or UDP based on the speed test setting", "help": "Dynamically selects TCP or UDP based on the speed test setting", "label": "Auto", "name": "Auto"}]
VALID_BODY_DYNAMIC_SERVER: Literal[{"description": "Disable dynamic server", "help": "Disable dynamic server.", "label": "Disable", "name": "disable"}, {"description": "Enable dynamic server", "help": "Enable dynamic server.The speed test server will be found automatically.", "label": "Enable", "name": "enable"}]
VALID_BODY_UPDATE_SHAPER: Literal[{"description": "Disable updating egress shaper", "help": "Disable updating egress shaper.", "label": "Disable", "name": "disable"}, {"description": "Update local-side egress shaper", "help": "Update local-side egress shaper.", "label": "Local", "name": "local"}, {"description": "Update remote-side egress shaper", "help": "Update remote-side egress shaper.", "label": "Remote", "name": "remote"}, {"description": "Update both local-side and remote-side egress shaper", "help": "Update both local-side and remote-side egress shaper.", "label": "Both", "name": "both"}]
VALID_BODY_UPDATE_INBANDWIDTH: Literal[{"description": "Honor interface\u0027s inbandwidth shaping", "help": "Honor interface\u0027s inbandwidth shaping.", "label": "Disable", "name": "disable"}, {"description": "Ignore interface\u0027s inbandwidth shaping", "help": "Ignore interface\u0027s inbandwidth shaping.", "label": "Enable", "name": "enable"}]
VALID_BODY_UPDATE_OUTBANDWIDTH: Literal[{"description": "Honor interface\u0027s outbandwidth shaping", "help": "Honor interface\u0027s outbandwidth shaping.", "label": "Disable", "name": "disable"}, {"description": "Ignore updating interface\u0027s outbandwidth shaping", "help": "Ignore updating interface\u0027s outbandwidth shaping.", "label": "Enable", "name": "enable"}]
VALID_BODY_UPDATE_INTERFACE_SHAPING: Literal[{"description": "Disable updating interface shaping", "help": "Disable updating interface shaping.", "label": "Disable", "name": "disable"}, {"description": "Enable updating interface shaping", "help": "Enable updating interface shaping.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_MODE",
    "VALID_BODY_DYNAMIC_SERVER",
    "VALID_BODY_UPDATE_SHAPER",
    "VALID_BODY_UPDATE_INBANDWIDTH",
    "VALID_BODY_UPDATE_OUTBANDWIDTH",
    "VALID_BODY_UPDATE_INTERFACE_SHAPING",
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