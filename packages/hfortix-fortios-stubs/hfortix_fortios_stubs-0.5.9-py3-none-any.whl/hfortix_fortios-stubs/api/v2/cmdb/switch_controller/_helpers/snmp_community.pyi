from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Disable SNMP community", "help": "Disable SNMP community.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP community", "help": "Enable SNMP community.", "label": "Enable", "name": "enable"}]
VALID_BODY_QUERY_V1_STATUS: Literal[{"description": "Disable SNMP v1 queries", "help": "Disable SNMP v1 queries.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v1 queries", "help": "Enable SNMP v1 queries.", "label": "Enable", "name": "enable"}]
VALID_BODY_QUERY_V2C_STATUS: Literal[{"description": "Disable SNMP v2c queries", "help": "Disable SNMP v2c queries.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v2c queries", "help": "Enable SNMP v2c queries.", "label": "Enable", "name": "enable"}]
VALID_BODY_TRAP_V1_STATUS: Literal[{"description": "Disable SNMP v1 traps", "help": "Disable SNMP v1 traps.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v1 traps", "help": "Enable SNMP v1 traps.", "label": "Enable", "name": "enable"}]
VALID_BODY_TRAP_V2C_STATUS: Literal[{"description": "Disable SNMP v2c traps", "help": "Disable SNMP v2c traps.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP v2c traps", "help": "Enable SNMP v2c traps.", "label": "Enable", "name": "enable"}]
VALID_BODY_EVENTS: Literal[{"description": "Send a trap when CPU usage too high", "help": "Send a trap when CPU usage too high.", "label": "Cpu High", "name": "cpu-high"}, {"description": "Send a trap when available memory is low", "help": "Send a trap when available memory is low.", "label": "Mem Low", "name": "mem-low"}, {"description": "Send a trap when log disk space becomes low", "help": "Send a trap when log disk space becomes low.", "label": "Log Full", "name": "log-full"}, {"description": "Send a trap when an interface IP address is changed", "help": "Send a trap when an interface IP address is changed.", "label": "Intf Ip", "name": "intf-ip"}, {"description": "Send a trap when an entity MIB change occurs (RFC4133)", "help": "Send a trap when an entity MIB change occurs (RFC4133).", "label": "Ent Conf Change", "name": "ent-conf-change"}, {"description": "Send a trap for Learning event (add/delete/movefrom/moveto)", "help": "Send a trap for Learning event (add/delete/movefrom/moveto).", "label": "L2Mac", "name": "l2mac"}]

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
    "VALID_BODY_QUERY_V1_STATUS",
    "VALID_BODY_QUERY_V2C_STATUS",
    "VALID_BODY_TRAP_V1_STATUS",
    "VALID_BODY_TRAP_V2C_STATUS",
    "VALID_BODY_EVENTS",
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