from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SSL_DH_BITS: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}]
VALID_BODY_SSL_SEND_EMPTY_FRAGS: Literal[{"description": "Send empty fragments", "help": "Send empty fragments.", "label": "Enable", "name": "enable"}, {"description": "Do not send empty fragments", "help": "Do not send empty fragments.", "label": "Disable", "name": "disable"}]
VALID_BODY_NO_MATCHING_CIPHER_ACTION: Literal[{"description": "Bypass connection", "help": "Bypass connection.", "label": "Bypass", "name": "bypass"}, {"description": "Drop connection", "help": "Drop connection.", "label": "Drop", "name": "drop"}]
VALID_BODY_RESIGNED_SHORT_LIVED_CERTIFICATE: Literal[{"description": "Enable short-lived certificate: re-signed certificate will remain valid until either the origin server ceritificate expires or cache timeouts", "help": "Enable short-lived certificate: re-signed certificate will remain valid until either the origin server ceritificate expires or cache timeouts.", "label": "Enable", "name": "enable"}, {"description": "Disable short-lived certificate: re-signed certificate will have the same validation period as the origin server ceritificate", "help": "Disable short-lived certificate: re-signed certificate will have the same validation period as the origin server ceritificate.", "label": "Disable", "name": "disable"}]
VALID_BODY_ABBREVIATE_HANDSHAKE: Literal[{"description": "Enable use of SSL abbreviated handshake", "help": "Enable use of SSL abbreviated handshake.", "label": "Enable", "name": "enable"}, {"description": "Disable use of SSL abbreviated handshake", "help": "Disable use of SSL abbreviated handshake.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_SSL_DH_BITS",
    "VALID_BODY_SSL_SEND_EMPTY_FRAGS",
    "VALID_BODY_NO_MATCHING_CIPHER_ACTION",
    "VALID_BODY_RESIGNED_SHORT_LIVED_CERTIFICATE",
    "VALID_BODY_ABBREVIATE_HANDSHAKE",
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