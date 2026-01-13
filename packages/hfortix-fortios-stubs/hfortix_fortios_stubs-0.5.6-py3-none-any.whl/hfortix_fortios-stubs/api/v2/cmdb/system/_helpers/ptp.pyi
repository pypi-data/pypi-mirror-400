from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable synchronization with PTP Server", "help": "Enable synchronization with PTP Server.", "label": "Enable", "name": "enable"}, {"description": "Disable synchronization with PTP Server", "help": "Disable synchronization with PTP Server.", "label": "Disable", "name": "disable"}]
VALID_BODY_MODE: Literal[{"description": "Send PTP packets with multicast", "help": "Send PTP packets with multicast.", "label": "Multicast", "name": "multicast"}, {"description": "Send PTP packets with unicast and multicast", "help": "Send PTP packets with unicast and multicast.", "label": "Hybrid", "name": "hybrid"}]
VALID_BODY_DELAY_MECHANISM: Literal[{"description": "End to end delay detection", "help": "End to end delay detection.", "label": "E2E", "name": "E2E"}, {"description": "Peer to peer delay detection", "help": "Peer to peer delay detection.", "label": "P2P", "name": "P2P"}]
VALID_BODY_SERVER_MODE: Literal[{"description": "Enable FortiGate PTP server mode", "help": "Enable FortiGate PTP server mode.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGate PTP server mode", "help": "Disable FortiGate PTP server mode.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_DELAY_MECHANISM",
    "VALID_BODY_SERVER_MODE",
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