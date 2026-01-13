from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable the explicit FTP proxy", "help": "Enable the explicit FTP proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the explicit FTP proxy", "help": "Disable the explicit FTP proxy.", "label": "Disable", "name": "disable"}]
VALID_BODY_SEC_DEFAULT_ACTION: Literal[{"description": "Accept requests", "help": "Accept requests. All explicit FTP proxy traffic is accepted whether there is an explicit FTP proxy policy or not", "label": "Accept", "name": "accept"}, {"help": "Deny requests unless there is a matching explicit FTP proxy policy.", "label": "Deny", "name": "deny"}]
VALID_BODY_SERVER_DATA_MODE: Literal[{"description": "Use the same transmission mode for client and server data sessions", "help": "Use the same transmission mode for client and server data sessions.", "label": "Client", "name": "client"}, {"description": "Use passive mode on server data session", "help": "Use passive mode on server data session.", "label": "Passive", "name": "passive"}]
VALID_BODY_SSL: Literal[{"description": "Enable the explicit FTPS proxy", "help": "Enable the explicit FTPS proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the explicit FTPS proxy", "help": "Disable the explicit FTPS proxy.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSL_DH_BITS: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}]
VALID_BODY_SSL_ALGORITHM: Literal[{"description": "High encryption", "help": "High encryption. Allow only AES and ChaCha", "label": "High", "name": "high"}, {"help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}]

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
    "VALID_BODY_SEC_DEFAULT_ACTION",
    "VALID_BODY_SERVER_DATA_MODE",
    "VALID_BODY_SSL",
    "VALID_BODY_SSL_DH_BITS",
    "VALID_BODY_SSL_ALGORITHM",
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