from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SSL_MODE: Literal[{"description": "Client to FortiGate SSL", "help": "Client to FortiGate SSL.", "label": "Half", "name": "half"}, {"description": "Client to FortiGate and FortiGate to Server SSL", "help": "Client to FortiGate and FortiGate to Server SSL.", "label": "Full", "name": "full"}]
VALID_BODY_ADD_HEADER_X_FORWARDED_PROTO: Literal[{"description": "Add X-Forwarded-Proto header", "help": "Add X-Forwarded-Proto header.", "label": "Enable", "name": "enable"}, {"description": "Do not add X-Forwarded-Proto header", "help": "Do not add X-Forwarded-Proto header.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSL_DH_BITS: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}]
VALID_BODY_SSL_ALGORITHM: Literal[{"description": "High encryption", "help": "High encryption. Allow only AES and ChaCha", "label": "High", "name": "high"}, {"help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}]
VALID_BODY_SSL_CLIENT_RENEGOTIATION: Literal[{"description": "Allow a SSL client to renegotiate", "help": "Allow a SSL client to renegotiate.", "label": "Allow", "name": "allow"}, {"description": "Abort any SSL connection that attempts to renegotiate", "help": "Abort any SSL connection that attempts to renegotiate.", "label": "Deny", "name": "deny"}, {"description": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication", "help": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication.", "label": "Secure", "name": "secure"}]
VALID_BODY_SSL_MIN_VERSION: Literal[{"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}]
VALID_BODY_SSL_MAX_VERSION: Literal[{"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}]
VALID_BODY_SSL_SEND_EMPTY_FRAGS: Literal[{"description": "Send empty fragments", "help": "Send empty fragments.", "label": "Enable", "name": "enable"}, {"description": "Do not send empty fragments", "help": "Do not send empty fragments.", "label": "Disable", "name": "disable"}]
VALID_BODY_URL_REWRITE: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_SSL_MODE",
    "VALID_BODY_ADD_HEADER_X_FORWARDED_PROTO",
    "VALID_BODY_SSL_DH_BITS",
    "VALID_BODY_SSL_ALGORITHM",
    "VALID_BODY_SSL_CLIENT_RENEGOTIATION",
    "VALID_BODY_SSL_MIN_VERSION",
    "VALID_BODY_SSL_MAX_VERSION",
    "VALID_BODY_SSL_SEND_EMPTY_FRAGS",
    "VALID_BODY_URL_REWRITE",
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