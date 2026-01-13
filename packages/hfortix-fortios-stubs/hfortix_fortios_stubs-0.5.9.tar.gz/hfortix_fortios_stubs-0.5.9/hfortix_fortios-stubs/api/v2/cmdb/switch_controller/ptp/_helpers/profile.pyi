from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_MODE: Literal[{"description": "End-to-end transparent clock", "help": "End-to-end transparent clock.", "label": "Transparent E2E", "name": "transparent-e2e"}, {"description": "Peer-to-peer transparent clock", "help": "Peer-to-peer transparent clock.", "label": "Transparent P2P", "name": "transparent-p2p"}]
VALID_BODY_PTP_PROFILE: Literal[{"help": "C37.238-2017 power profile.", "label": "C37.238 2017", "name": "C37.238-2017"}]
VALID_BODY_TRANSPORT: Literal[{"description": "L2 multicast", "help": "L2 multicast.", "label": "L2 Mcast", "name": "l2-mcast"}]
VALID_BODY_PDELAY_REQ_INTERVAL: Literal[{"description": "1 sec", "help": "1 sec.", "label": "1Sec", "name": "1sec"}, {"description": "2 sec", "help": "2 sec.", "label": "2Sec", "name": "2sec"}, {"description": "4 sec", "help": "4 sec.", "label": "4Sec", "name": "4sec"}, {"description": "8 sec", "help": "8 sec.", "label": "8Sec", "name": "8sec"}, {"description": "16 sec", "help": "16 sec.", "label": "16Sec", "name": "16sec"}, {"description": "32 sec", "help": "32 sec.", "label": "32Sec", "name": "32sec"}]

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
    "VALID_BODY_PTP_PROFILE",
    "VALID_BODY_TRANSPORT",
    "VALID_BODY_PDELAY_REQ_INTERVAL",
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