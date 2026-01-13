from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_ICMP_PORT: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]
VALID_BODY_FTP_PORT: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]
VALID_BODY_SSH_PORT: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]
VALID_BODY_HTTP_PORT: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]
VALID_BODY_TLS_PORT: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]
VALID_BODY_PPTP_VPN_PORT: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]
VALID_BODY_VOIP_TCP_PORT: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]
VALID_BODY_VOIP_UDP_PORT: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]
VALID_BODY_IKEV2_PORT: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]
VALID_BODY_IKEV2_XX_PORT: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]
VALID_BODY_ESP_PORT: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]

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
    "VALID_BODY_ICMP_PORT",
    "VALID_BODY_FTP_PORT",
    "VALID_BODY_SSH_PORT",
    "VALID_BODY_HTTP_PORT",
    "VALID_BODY_TLS_PORT",
    "VALID_BODY_PPTP_VPN_PORT",
    "VALID_BODY_VOIP_TCP_PORT",
    "VALID_BODY_VOIP_UDP_PORT",
    "VALID_BODY_IKEV2_PORT",
    "VALID_BODY_IKEV2_XX_PORT",
    "VALID_BODY_ESP_PORT",
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