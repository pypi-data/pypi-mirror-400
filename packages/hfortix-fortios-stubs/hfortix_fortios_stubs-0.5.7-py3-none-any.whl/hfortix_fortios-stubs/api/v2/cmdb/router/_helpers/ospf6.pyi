from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_ABR_TYPE: Literal[{"description": "Cisco", "help": "Cisco.", "label": "Cisco", "name": "cisco"}, {"description": "IBM", "help": "IBM.", "label": "Ibm", "name": "ibm"}, {"description": "Standard", "help": "Standard.", "label": "Standard", "name": "standard"}]
VALID_BODY_DEFAULT_INFORMATION_ORIGINATE: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Always advertise the default router", "help": "Always advertise the default router.", "label": "Always", "name": "always"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOG_NEIGHBOUR_CHANGES: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_DEFAULT_INFORMATION_METRIC_TYPE: Literal[{"description": "Type 1", "help": "Type 1.", "label": "1", "name": "1"}, {"description": "Type 2", "help": "Type 2.", "label": "2", "name": "2"}]
VALID_BODY_BFD: Literal[{"description": "Enable Bidirectional Forwarding Detection (BFD)", "help": "Enable Bidirectional Forwarding Detection (BFD).", "label": "Enable", "name": "enable"}, {"description": "Disable Bidirectional Forwarding Detection (BFD)", "help": "Disable Bidirectional Forwarding Detection (BFD).", "label": "Disable", "name": "disable"}]
VALID_BODY_RESTART_MODE: Literal[{"description": "Disable hitless restart", "help": "Disable hitless restart.", "label": "None", "name": "none"}, {"description": "Enable graceful restart mode", "help": "Enable graceful restart mode.", "label": "Graceful Restart", "name": "graceful-restart"}]
VALID_BODY_RESTART_ON_TOPOLOGY_CHANGE: Literal[{"description": "Continue graceful restart upon topology change", "help": "Continue graceful restart upon topology change.", "label": "Enable", "name": "enable"}, {"description": "Exit graceful restart upon topology change", "help": "Exit graceful restart upon topology change.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_ABR_TYPE",
    "VALID_BODY_DEFAULT_INFORMATION_ORIGINATE",
    "VALID_BODY_LOG_NEIGHBOUR_CHANGES",
    "VALID_BODY_DEFAULT_INFORMATION_METRIC_TYPE",
    "VALID_BODY_BFD",
    "VALID_BODY_RESTART_MODE",
    "VALID_BODY_RESTART_ON_TOPOLOGY_CHANGE",
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