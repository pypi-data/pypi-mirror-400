from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "The public key is trusted", "help": "The public key is trusted.", "label": "Trusted", "name": "trusted"}, {"description": "The public key is revoked", "help": "The public key is revoked.", "label": "Revoked", "name": "revoked"}]
VALID_BODY_TYPE: Literal[{"description": "The type of the public key is RSA", "help": "The type of the public key is RSA.", "label": "Rsa", "name": "RSA"}, {"description": "The type of the public key is DSA", "help": "The type of the public key is DSA.", "label": "Dsa", "name": "DSA"}, {"description": "The type of the public key is ECDSA", "help": "The type of the public key is ECDSA.", "label": "Ecdsa", "name": "ECDSA"}, {"description": "The type of the public key is ED25519", "help": "The type of the public key is ED25519.", "label": "Ed25519", "name": "ED25519"}, {"description": "The type of the public key is from RSA CA", "help": "The type of the public key is from RSA CA.", "label": "Rsa Ca", "name": "RSA-CA"}, {"description": "The type of the public key is from DSA CA", "help": "The type of the public key is from DSA CA.", "label": "Dsa Ca", "name": "DSA-CA"}, {"description": "The type of the public key is from ECDSA CA", "help": "The type of the public key is from ECDSA CA.", "label": "Ecdsa Ca", "name": "ECDSA-CA"}, {"description": "The type of the public key is from ED25519 CA", "help": "The type of the public key is from ED25519 CA.", "label": "Ed25519 Ca", "name": "ED25519-CA"}]
VALID_BODY_NID: Literal[{"description": "The NID is ecdsa-sha2-nistp256", "help": "The NID is ecdsa-sha2-nistp256.", "label": "256", "name": "256"}, {"description": "The NID is ecdsa-sha2-nistp384", "help": "The NID is ecdsa-sha2-nistp384.", "label": "384", "name": "384"}, {"description": "The NID is ecdsa-sha2-nistp521", "help": "The NID is ecdsa-sha2-nistp521.", "label": "521", "name": "521"}]
VALID_BODY_USAGE: Literal[{"description": "Transparent proxy uses this public key to validate server", "help": "Transparent proxy uses this public key to validate server.", "label": "Transparent Proxy", "name": "transparent-proxy"}, {"description": "Access proxy uses this public key to validate server", "help": "Access proxy uses this public key to validate server.", "label": "Access Proxy", "name": "access-proxy"}]

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
    "VALID_BODY_TYPE",
    "VALID_BODY_NID",
    "VALID_BODY_USAGE",
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