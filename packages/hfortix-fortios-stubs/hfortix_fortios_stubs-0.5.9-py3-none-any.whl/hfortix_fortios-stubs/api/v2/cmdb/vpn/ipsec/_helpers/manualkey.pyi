from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_AUTHENTICATION: Literal[{"description": "Null", "help": "Null.", "label": "Null", "name": "null"}, {"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}, {"description": "SHA1", "help": "SHA1.", "label": "Sha1", "name": "sha1"}, {"description": "SHA256", "help": "SHA256.", "label": "Sha256", "name": "sha256"}, {"description": "SHA384", "help": "SHA384.", "label": "Sha384", "name": "sha384"}, {"description": "SHA512", "help": "SHA512.", "label": "Sha512", "name": "sha512"}]
VALID_BODY_ENCRYPTION: Literal[{"description": "Null", "help": "Null.", "label": "Null", "name": "null"}, {"description": "DES", "help": "DES.", "label": "Des", "name": "des"}, {"description": "3DES", "help": "3DES.", "label": "3Des", "name": "3des"}, {"description": "AES128", "help": "AES128.", "label": "Aes128", "name": "aes128"}, {"description": "AES192", "help": "AES192.", "label": "Aes192", "name": "aes192"}, {"description": "AES256", "help": "AES256.", "label": "Aes256", "name": "aes256"}, {"description": "ARIA128", "help": "ARIA128.", "label": "Aria128", "name": "aria128"}, {"description": "ARIA192", "help": "ARIA192.", "label": "Aria192", "name": "aria192"}, {"description": "ARIA256", "help": "ARIA256.", "label": "Aria256", "name": "aria256"}, {"description": "Seed", "help": "Seed.", "label": "Seed", "name": "seed"}]
VALID_BODY_NPU_OFFLOAD: Literal[{"description": "Enable NPU offloading", "help": "Enable NPU offloading.", "label": "Enable", "name": "enable"}, {"description": "Disable NPU offloading", "help": "Disable NPU offloading.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_AUTHENTICATION",
    "VALID_BODY_ENCRYPTION",
    "VALID_BODY_NPU_OFFLOAD",
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