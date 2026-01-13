from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_MODE: Literal[{"description": "Manage and configure this FortiGate from FortiManager", "help": "Manage and configure this FortiGate from FortiManager.", "label": "Normal", "name": "normal"}, {"description": "Manage and configure this FortiGate locally and back up its configuration to FortiManager", "help": "Manage and configure this FortiGate locally and back up its configuration to FortiManager.", "label": "Backup", "name": "backup"}]
VALID_BODY_TYPE: Literal[{"description": "FortiManager", "help": "FortiManager.", "label": "Fortimanager", "name": "fortimanager"}, {"description": "Central management of this FortiGate using FortiCloud", "help": "Central management of this FortiGate using FortiCloud.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "No central management", "help": "No central management.", "label": "None", "name": "none"}]
VALID_BODY_SCHEDULE_CONFIG_RESTORE: Literal[{"description": "Enable scheduled configuration restore", "help": "Enable scheduled configuration restore.", "label": "Enable", "name": "enable"}, {"description": "Disable scheduled configuration restore", "help": "Disable scheduled configuration restore.", "label": "Disable", "name": "disable"}]
VALID_BODY_SCHEDULE_SCRIPT_RESTORE: Literal[{"description": "Enable scheduled script restore", "help": "Enable scheduled script restore.", "label": "Enable", "name": "enable"}, {"description": "Disable scheduled script restore", "help": "Disable scheduled script restore.", "label": "Disable", "name": "disable"}]
VALID_BODY_ALLOW_PUSH_CONFIGURATION: Literal[{"description": "Enable push configuration", "help": "Enable push configuration.", "label": "Enable", "name": "enable"}, {"description": "Disable push configuration", "help": "Disable push configuration.", "label": "Disable", "name": "disable"}]
VALID_BODY_ALLOW_PUSH_FIRMWARE: Literal[{"description": "Enable push firmware", "help": "Enable push firmware.", "label": "Enable", "name": "enable"}, {"description": "Disable push firmware", "help": "Disable push firmware.", "label": "Disable", "name": "disable"}]
VALID_BODY_ALLOW_REMOTE_FIRMWARE_UPGRADE: Literal[{"description": "Enable remote firmware upgrade", "help": "Enable remote firmware upgrade.", "label": "Enable", "name": "enable"}, {"description": "Disable remote firmware upgrade", "help": "Disable remote firmware upgrade.", "label": "Disable", "name": "disable"}]
VALID_BODY_ALLOW_MONITOR: Literal[{"description": "Enable remote monitoring of device", "help": "Enable remote monitoring of device.", "label": "Enable", "name": "enable"}, {"description": "Disable remote monitoring of device", "help": "Disable remote monitoring of device.", "label": "Disable", "name": "disable"}]
VALID_BODY_FMG_UPDATE_PORT: Literal[{"description": "Use port 8890 to communicate with FortiManager that is acting as a FortiGuard update server", "help": "Use port 8890 to communicate with FortiManager that is acting as a FortiGuard update server.", "label": "8890", "name": "8890"}, {"description": "Use port 443 to communicate with FortiManager that is acting as a FortiGuard update server", "help": "Use port 443 to communicate with FortiManager that is acting as a FortiGuard update server.", "label": "443", "name": "443"}]
VALID_BODY_FMG_UPDATE_HTTP_HEADER: Literal[{"description": "Enable inclusion of HTTP header in update request", "help": "Enable inclusion of HTTP header in update request.", "label": "Enable", "name": "enable"}, {"description": "Disable inclusion of HTTP header in update request", "help": "Disable inclusion of HTTP header in update request.", "label": "Disable", "name": "disable"}]
VALID_BODY_INCLUDE_DEFAULT_SERVERS: Literal[{"description": "Enable inclusion of public FortiGuard servers in the override server list", "help": "Enable inclusion of public FortiGuard servers in the override server list.", "label": "Enable", "name": "enable"}, {"description": "Disable inclusion of public FortiGuard servers in the override server list", "help": "Disable inclusion of public FortiGuard servers in the override server list.", "label": "Disable", "name": "disable"}]
VALID_BODY_ENC_ALGORITHM: Literal[{"description": "High strength algorithms and medium-strength 128-bit key length algorithms", "help": "High strength algorithms and medium-strength 128-bit key length algorithms.", "label": "Default", "name": "default"}, {"description": "128-bit and larger key length algorithms", "help": "128-bit and larger key length algorithms.", "label": "High", "name": "high"}, {"description": "64-bit or 56-bit key length algorithms without export restrictions", "help": "64-bit or 56-bit key length algorithms without export restrictions.", "label": "Low", "name": "low"}]
VALID_BODY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]

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
    "VALID_BODY_MODE",
    "VALID_BODY_TYPE",
    "VALID_BODY_SCHEDULE_CONFIG_RESTORE",
    "VALID_BODY_SCHEDULE_SCRIPT_RESTORE",
    "VALID_BODY_ALLOW_PUSH_CONFIGURATION",
    "VALID_BODY_ALLOW_PUSH_FIRMWARE",
    "VALID_BODY_ALLOW_REMOTE_FIRMWARE_UPGRADE",
    "VALID_BODY_ALLOW_MONITOR",
    "VALID_BODY_FMG_UPDATE_PORT",
    "VALID_BODY_FMG_UPDATE_HTTP_HEADER",
    "VALID_BODY_INCLUDE_DEFAULT_SERVERS",
    "VALID_BODY_ENC_ALGORITHM",
    "VALID_BODY_INTERFACE_SELECT_METHOD",
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