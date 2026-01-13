from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable integration with IP address management services", "help": "Enable integration with IP address management services.", "label": "Enable", "name": "enable"}, {"description": "Disable integration with IP address management services", "help": "Disable integration with IP address management services.", "label": "Disable", "name": "disable"}]
VALID_BODY_SERVER_TYPE: Literal[{"description": "Use the IPAM server running on the Security Fabric root", "help": "Use the IPAM server running on the Security Fabric root.", "label": "Fabric Root", "name": "fabric-root"}]
VALID_BODY_AUTOMATIC_CONFLICT_RESOLUTION: Literal[{"description": "Disable automatic conflict resolution", "help": "Disable automatic conflict resolution.", "label": "Disable", "name": "disable"}, {"description": "Enable automatic conflict resolution", "help": "Enable automatic conflict resolution.", "label": "Enable", "name": "enable"}]
VALID_BODY_REQUIRE_SUBNET_SIZE_MATCH: Literal[{"description": "Disable requiring subnet sizes to match", "help": "Disable requiring subnet sizes to match.", "label": "Disable", "name": "disable"}, {"description": "Enable requiring subnet sizes to match", "help": "Enable requiring subnet sizes to match.", "label": "Enable", "name": "enable"}]
VALID_BODY_MANAGE_LAN_ADDRESSES: Literal[{"description": "Disable LAN interface address management by default", "help": "Disable LAN interface address management by default.", "label": "Disable", "name": "disable"}, {"description": "Enable LAN interface address management by default", "help": "Enable LAN interface address management by default.", "label": "Enable", "name": "enable"}]
VALID_BODY_MANAGE_LAN_EXTENSION_ADDRESSES: Literal[{"description": "Disable FortiExtender LAN extension interface address management by default", "help": "Disable FortiExtender LAN extension interface address management by default.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiExtender LAN extension interface address management by default", "help": "Enable FortiExtender LAN extension interface address management by default.", "label": "Enable", "name": "enable"}]
VALID_BODY_MANAGE_SSID_ADDRESSES: Literal[{"description": "Disable FortiAP SSID address management by default", "help": "Disable FortiAP SSID address management by default.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiAP SSID address management by default", "help": "Enable FortiAP SSID address management by default.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_SERVER_TYPE",
    "VALID_BODY_AUTOMATIC_CONFLICT_RESOLUTION",
    "VALID_BODY_REQUIRE_SUBNET_SIZE_MATCH",
    "VALID_BODY_MANAGE_LAN_ADDRESSES",
    "VALID_BODY_MANAGE_LAN_EXTENSION_ADDRESSES",
    "VALID_BODY_MANAGE_SSID_ADDRESSES",
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