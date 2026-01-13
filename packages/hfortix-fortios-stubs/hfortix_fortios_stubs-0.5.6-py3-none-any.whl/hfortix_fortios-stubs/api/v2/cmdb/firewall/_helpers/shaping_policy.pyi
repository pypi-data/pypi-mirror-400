from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable traffic shaping policy", "help": "Enable traffic shaping policy.", "label": "Enable", "name": "enable"}, {"description": "Disable traffic shaping policy", "help": "Disable traffic shaping policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_IP_VERSION: Literal[{"description": "Use IPv4 addressing for Configuration Method", "help": "Use IPv4 addressing for Configuration Method.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for Configuration Method", "help": "Use IPv6 addressing for Configuration Method.", "label": "6", "name": "6"}]
VALID_BODY_TRAFFIC_TYPE: Literal[{"description": "Forwarding traffic", "help": "Forwarding traffic.", "label": "Forwarding", "name": "forwarding"}, {"description": "Local-in traffic", "help": "Local-in traffic.", "label": "Local In", "name": "local-in"}, {"description": "Local-out traffic", "help": "Local-out traffic.", "label": "Local Out", "name": "local-out"}]
VALID_BODY_INTERNET_SERVICE: Literal[{"description": "Enable use of Internet Service in shaping-policy", "help": "Enable use of Internet Service in shaping-policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Service in shaping-policy", "help": "Disable use of Internet Service in shaping-policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE_SRC: Literal[{"description": "Enable use of Internet Service source in shaping-policy", "help": "Enable use of Internet Service source in shaping-policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Service source in shaping-policy", "help": "Disable use of Internet Service source in shaping-policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_TOS_NEGATE: Literal[{"description": "Enable TOS match negate", "help": "Enable TOS match negate.", "label": "Enable", "name": "enable"}, {"description": "Disable TOS match negate", "help": "Disable TOS match negate.", "label": "Disable", "name": "disable"}]
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
    "VALID_BODY_STATUS",
    "VALID_BODY_IP_VERSION",
    "VALID_BODY_TRAFFIC_TYPE",
    "VALID_BODY_INTERNET_SERVICE",
    "VALID_BODY_INTERNET_SERVICE_SRC",
    "VALID_BODY_TOS_NEGATE",
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