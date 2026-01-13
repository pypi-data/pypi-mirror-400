from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_PROTOCOL: Literal[{"description": "DNS over UDP/53, DNS over TCP/53", "help": "DNS over UDP/53, DNS over TCP/53.", "label": "Cleartext", "name": "cleartext"}, {"description": "DNS over TLS/853", "help": "DNS over TLS/853.", "label": "Dot", "name": "dot"}, {"description": "DNS over HTTPS/443", "help": "DNS over HTTPS/443.", "label": "Doh", "name": "doh"}]
VALID_BODY_CACHE_NOTFOUND_RESPONSES: Literal[{"description": "Disable cache NOTFOUND responses from DNS server", "help": "Disable cache NOTFOUND responses from DNS server.", "label": "Disable", "name": "disable"}, {"description": "Enable cache NOTFOUND responses from DNS server", "help": "Enable cache NOTFOUND responses from DNS server.", "label": "Enable", "name": "enable"}]
VALID_BODY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]
VALID_BODY_SERVER_SELECT_METHOD: Literal[{"description": "Select servers based on least round trip time", "help": "Select servers based on least round trip time.", "label": "Least Rtt", "name": "least-rtt"}, {"description": "Select servers based on the order they are configured", "help": "Select servers based on the order they are configured.", "label": "Failover", "name": "failover"}]
VALID_BODY_LOG: Literal[{"description": "Disable", "help": "Disable.", "label": "Disable", "name": "disable"}, {"description": "Enable local DNS error log", "help": "Enable local DNS error log.", "label": "Error", "name": "error"}, {"description": "Enable local DNS log", "help": "Enable local DNS log.", "label": "All", "name": "all"}]

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
    "VALID_BODY_CACHE_NOTFOUND_RESPONSES",
    "VALID_BODY_INTERFACE_SELECT_METHOD",
    "VALID_BODY_SERVER_SELECT_METHOD",
    "VALID_BODY_LOG",
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