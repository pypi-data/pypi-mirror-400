from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_QUERIES: Literal[{"description": "Disable SNMP queries for this user", "help": "Disable SNMP queries for this user.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP queries for this user", "help": "Enable SNMP queries for this user.", "label": "Enable", "name": "enable"}]
VALID_BODY_SECURITY_LEVEL: Literal[{"description": "Message with no authentication and no privacy (encryption)", "help": "Message with no authentication and no privacy (encryption).", "label": "No Auth No Priv", "name": "no-auth-no-priv"}, {"description": "Message with authentication but no privacy (encryption)", "help": "Message with authentication but no privacy (encryption).", "label": "Auth No Priv", "name": "auth-no-priv"}, {"description": "Message with authentication and privacy (encryption)", "help": "Message with authentication and privacy (encryption).", "label": "Auth Priv", "name": "auth-priv"}]
VALID_BODY_AUTH_PROTO: Literal[{"description": "HMAC-MD5-96 authentication protocol", "help": "HMAC-MD5-96 authentication protocol.", "label": "Md5", "name": "md5"}, {"description": "HMAC-SHA-1 authentication protocol", "help": "HMAC-SHA-1 authentication protocol.", "label": "Sha1", "name": "sha1"}, {"description": "HMAC-SHA-224 authentication protocol", "help": "HMAC-SHA-224 authentication protocol.", "label": "Sha224", "name": "sha224"}, {"description": "HMAC-SHA-256 authentication protocol", "help": "HMAC-SHA-256 authentication protocol.", "label": "Sha256", "name": "sha256"}, {"description": "HMAC-SHA-384 authentication protocol", "help": "HMAC-SHA-384 authentication protocol.", "label": "Sha384", "name": "sha384"}, {"description": "HMAC-SHA-512 authentication protocol", "help": "HMAC-SHA-512 authentication protocol.", "label": "Sha512", "name": "sha512"}]
VALID_BODY_PRIV_PROTO: Literal[{"description": "CFB128-AES-128 symmetric encryption protocol", "help": "CFB128-AES-128 symmetric encryption protocol.", "label": "Aes128", "name": "aes128"}, {"description": "CFB128-AES-192 symmetric encryption protocol", "help": "CFB128-AES-192 symmetric encryption protocol.", "label": "Aes192", "name": "aes192"}, {"description": "CFB128-AES-192-C symmetric encryption protocol", "help": "CFB128-AES-192-C symmetric encryption protocol.", "label": "Aes192C", "name": "aes192c"}, {"description": "CFB128-AES-256 symmetric encryption protocol", "help": "CFB128-AES-256 symmetric encryption protocol.", "label": "Aes256", "name": "aes256"}, {"description": "CFB128-AES-256-C symmetric encryption protocol", "help": "CFB128-AES-256-C symmetric encryption protocol.", "label": "Aes256C", "name": "aes256c"}, {"description": "CBC-DES symmetric encryption protocol", "help": "CBC-DES symmetric encryption protocol.", "label": "Des", "name": "des"}]

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
    "VALID_BODY_QUERIES",
    "VALID_BODY_SECURITY_LEVEL",
    "VALID_BODY_AUTH_PROTO",
    "VALID_BODY_PRIV_PROTO",
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