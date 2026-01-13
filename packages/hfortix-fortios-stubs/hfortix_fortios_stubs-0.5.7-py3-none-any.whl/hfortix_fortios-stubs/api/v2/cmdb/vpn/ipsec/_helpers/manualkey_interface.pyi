from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_IP_VERSION: Literal[{"description": "Use IPv4 addressing for gateways", "help": "Use IPv4 addressing for gateways.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for gateways", "help": "Use IPv6 addressing for gateways.", "label": "6", "name": "6"}]
VALID_BODY_ADDR_TYPE: Literal[{"description": "Use IPv4 addressing for IP packets", "help": "Use IPv4 addressing for IP packets.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for IP packets", "help": "Use IPv6 addressing for IP packets.", "label": "6", "name": "6"}]
VALID_BODY_AUTH_ALG: Literal[{"description": "null    md5:md5    sha1:sha1    sha256:sha256    sha384:sha384    sha512:sha512", "help": "null", "label": "Null", "name": "null"}, {"help": "md5", "label": "Md5", "name": "md5"}, {"help": "sha1", "label": "Sha1", "name": "sha1"}, {"help": "sha256", "label": "Sha256", "name": "sha256"}, {"help": "sha384", "label": "Sha384", "name": "sha384"}, {"help": "sha512", "label": "Sha512", "name": "sha512"}]
VALID_BODY_ENC_ALG: Literal[{"description": "null    des:des    3des:3des    aes128:aes128    aes192:aes192    aes256:aes256    aria128:aria128    aria192:aria192    aria256:aria256    seed:seed", "help": "null", "label": "Null", "name": "null"}, {"help": "des", "label": "Des", "name": "des"}, {"help": "3des", "label": "3Des", "name": "3des"}, {"help": "aes128", "label": "Aes128", "name": "aes128"}, {"help": "aes192", "label": "Aes192", "name": "aes192"}, {"help": "aes256", "label": "Aes256", "name": "aes256"}, {"help": "aria128", "label": "Aria128", "name": "aria128"}, {"help": "aria192", "label": "Aria192", "name": "aria192"}, {"help": "aria256", "label": "Aria256", "name": "aria256"}, {"help": "seed", "label": "Seed", "name": "seed"}]
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
    "VALID_BODY_IP_VERSION",
    "VALID_BODY_ADDR_TYPE",
    "VALID_BODY_AUTH_ALG",
    "VALID_BODY_ENC_ALG",
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