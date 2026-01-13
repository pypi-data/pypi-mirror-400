from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_PROTOCOL: Literal[{"description": "Use PING to test the link with the server", "help": "Use PING to test the link with the server.", "label": "Ping", "name": "ping"}, {"description": "Use TCP echo to test the link with the server", "help": "Use TCP echo to test the link with the server.", "label": "Tcp Echo", "name": "tcp-echo"}, {"description": "Use UDP echo to test the link with the server", "help": "Use UDP echo to test the link with the server.", "label": "Udp Echo", "name": "udp-echo"}, {"description": "Use HTTP-GET to test the link with the server", "help": "Use HTTP-GET to test the link with the server.", "label": "Http", "name": "http"}, {"description": "Use HTTPS-GET to test the link with the server", "help": "Use HTTPS-GET to test the link with the server.", "label": "Https", "name": "https"}, {"description": "Use TWAMP to test the link with the server", "help": "Use TWAMP to test the link with the server.", "label": "Twamp", "name": "twamp"}, {"description": "Use DNS query to test the link with the server", "help": "Use DNS query to test the link with the server.", "label": "Dns", "name": "dns"}, {"description": "Use a full TCP connection to test the link with the server", "help": "Use a full TCP connection to test the link with the server.", "label": "Tcp Connect", "name": "tcp-connect"}, {"description": "Use FTP to test the link with the server", "help": "Use FTP to test the link with the server.", "label": "Ftp", "name": "ftp"}]

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
    "VALID_BODY_PROTOCOL",
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