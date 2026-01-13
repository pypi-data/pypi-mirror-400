from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_NTPSYNC: Literal[{"description": "Enable synchronization with NTP Server", "help": "Enable synchronization with NTP Server.", "label": "Enable", "name": "enable"}, {"description": "Disable synchronization with NTP Server", "help": "Disable synchronization with NTP Server.", "label": "Disable", "name": "disable"}]
VALID_BODY_TYPE: Literal[{"description": "Use the FortiGuard NTP server", "help": "Use the FortiGuard NTP server.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Use any other available NTP server", "help": "Use any other available NTP server.", "label": "Custom", "name": "custom"}]
VALID_BODY_SERVER_MODE: Literal[{"description": "Enable FortiGate NTP Server Mode", "help": "Enable FortiGate NTP Server Mode.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGate NTP Server Mode", "help": "Disable FortiGate NTP Server Mode.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTHENTICATION: Literal[{"description": "Enable authentication", "help": "Enable authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication", "help": "Disable authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_KEY_TYPE: Literal[{"description": "Use MD5 to authenticate the message", "help": "Use MD5 to authenticate the message.", "label": "Md5", "name": "MD5"}, {"description": "Use SHA1 to authenticate the message", "help": "Use SHA1 to authenticate the message.", "label": "Sha1", "name": "SHA1"}, {"description": "Use SHA256 to authenticate the message", "help": "Use SHA256 to authenticate the message.", "label": "Sha256", "name": "SHA256"}]

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
    "VALID_BODY_NTPSYNC",
    "VALID_BODY_TYPE",
    "VALID_BODY_SERVER_MODE",
    "VALID_BODY_AUTHENTICATION",
    "VALID_BODY_KEY_TYPE",
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