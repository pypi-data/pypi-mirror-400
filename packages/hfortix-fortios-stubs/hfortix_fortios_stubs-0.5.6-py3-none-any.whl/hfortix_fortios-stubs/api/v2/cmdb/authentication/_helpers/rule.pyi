from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable this authentication rule", "help": "Enable this authentication rule.", "label": "Enable", "name": "enable"}, {"description": "Disable this authentication rule", "help": "Disable this authentication rule.", "label": "Disable", "name": "disable"}]
VALID_BODY_PROTOCOL: Literal[{"description": "HTTP traffic is matched and authentication is required", "help": "HTTP traffic is matched and authentication is required.", "label": "Http", "name": "http"}, {"description": "FTP traffic is matched and authentication is required", "help": "FTP traffic is matched and authentication is required.", "label": "Ftp", "name": "ftp"}, {"description": "SOCKS traffic is matched and authentication is required", "help": "SOCKS traffic is matched and authentication is required.", "label": "Socks", "name": "socks"}, {"description": "SSH traffic is matched and authentication is required", "help": "SSH traffic is matched and authentication is required.", "label": "Ssh", "name": "ssh"}, {"description": "ZTNA portal traffic is matched and authentication is required", "help": "ZTNA portal traffic is matched and authentication is required.", "label": "Ztna Portal", "name": "ztna-portal"}]
VALID_BODY_IP_BASED: Literal[{"description": "Enable IP-based authentication", "help": "Enable IP-based authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable IP-based authentication", "help": "Disable IP-based authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_AUTH_COOKIE: Literal[{"description": "Enable Web authentication cookie", "help": "Enable Web authentication cookie.", "label": "Enable", "name": "enable"}, {"description": "Disable Web authentication cookie", "help": "Disable Web authentication cookie.", "label": "Disable", "name": "disable"}]
VALID_BODY_CORS_STATEFUL: Literal[{"description": "Enable allowance of CORS access    disable:Disable allowance of CORS access", "help": "Enable allowance of CORS access", "label": "Enable", "name": "enable"}, {"help": "Disable allowance of CORS access", "label": "Disable", "name": "disable"}]
VALID_BODY_CERT_AUTH_COOKIE: Literal[{"description": "Enable device certificate as authentication cookie", "help": "Enable device certificate as authentication cookie.", "label": "Enable", "name": "enable"}, {"description": "Disable device certificate as authentication cookie", "help": "Disable device certificate as authentication cookie.", "label": "Disable", "name": "disable"}]
VALID_BODY_TRANSACTION_BASED: Literal[{"description": "Enable transaction based authentication", "help": "Enable transaction based authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable transaction based authentication", "help": "Disable transaction based authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_PORTAL: Literal[{"description": "Enable web-portal", "help": "Enable web-portal.", "label": "Enable", "name": "enable"}, {"description": "Disable web-portal", "help": "Disable web-portal.", "label": "Disable", "name": "disable"}]
VALID_BODY_SESSION_LOGOUT: Literal[{"description": "Enable logout of a user from the current session", "help": "Enable logout of a user from the current session.", "label": "Enable", "name": "enable"}, {"description": "Disable logout of a user from the current session", "help": "Disable logout of a user from the current session.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_PROTOCOL",
    "VALID_BODY_IP_BASED",
    "VALID_BODY_WEB_AUTH_COOKIE",
    "VALID_BODY_CORS_STATEFUL",
    "VALID_BODY_CERT_AUTH_COOKIE",
    "VALID_BODY_TRANSACTION_BASED",
    "VALID_BODY_WEB_PORTAL",
    "VALID_BODY_SESSION_LOGOUT",
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