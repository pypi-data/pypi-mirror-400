from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_HOST_TYPE: Literal[{"description": "Match the pattern if a string contains the sub-string", "help": "Match the pattern if a string contains the sub-string.", "label": "Sub String", "name": "sub-string"}, {"description": "Match the pattern with wildcards", "help": "Match the pattern with wildcards.", "label": "Wildcard", "name": "wildcard"}]
VALID_BODY_EMPTY_CERT_ACTION: Literal[{"description": "Accept the SSL handshake if the client certificate is empty", "help": "Accept the SSL handshake if the client certificate is empty.", "label": "Accept", "name": "accept"}, {"description": "Block the SSL handshake if the client certificate is empty", "help": "Block the SSL handshake if the client certificate is empty.", "label": "Block", "name": "block"}, {"description": "Accept the SSL handshake only if the end-point is unmanageable", "help": "Accept the SSL handshake only if the end-point is unmanageable.", "label": "Accept Unmanageable", "name": "accept-unmanageable"}]
VALID_BODY_USER_AGENT_DETECT: Literal[{"description": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Disable", "name": "disable"}, {"description": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Enable", "name": "enable"}]
VALID_BODY_CLIENT_CERT: Literal[{"description": "Disable client certificate request", "help": "Disable client certificate request.", "label": "Disable", "name": "disable"}, {"description": "Enable client certificate request", "help": "Enable client certificate request.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_HOST_TYPE",
    "VALID_BODY_EMPTY_CERT_ACTION",
    "VALID_BODY_USER_AGENT_DETECT",
    "VALID_BODY_CLIENT_CERT",
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