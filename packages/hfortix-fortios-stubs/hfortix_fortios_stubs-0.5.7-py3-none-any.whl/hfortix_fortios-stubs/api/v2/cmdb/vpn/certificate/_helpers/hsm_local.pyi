from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_VENDOR: Literal[{"description": "Unknown type of HSM", "help": "Unknown type of HSM.", "label": "Unknown", "name": "unknown"}, {"description": "Google Cloud HSM", "help": "Google Cloud HSM.", "label": "Gch", "name": "gch"}]
VALID_BODY_API_VERSION: Literal[{"description": "Unknown API version", "help": "Unknown API version.", "label": "Unknown", "name": "unknown"}, {"description": "Google Cloud HSM default API", "help": "Google Cloud HSM default API.", "label": "Gch Default", "name": "gch-default"}]
VALID_BODY_RANGE: Literal[{"description": "Global range", "help": "Global range.", "label": "Global", "name": "global"}, {"description": "VDOM IP address range", "help": "VDOM IP address range.", "label": "Vdom", "name": "vdom"}]
VALID_BODY_SOURCE: Literal[{"description": "Factory installed certificate", "help": "Factory installed certificate.", "label": "Factory", "name": "factory"}, {"description": "User generated certificate", "help": "User generated certificate.", "label": "User", "name": "user"}, {"description": "Bundle file certificate", "help": "Bundle file certificate.", "label": "Bundle", "name": "bundle"}]
VALID_BODY_GCH_CRYPTOKEY_ALGORITHM: Literal[{"description": "2048 bit RSA - PKCS#1 v1", "help": "2048 bit RSA - PKCS#1 v1.5 padding - SHA256 Digest.", "label": "Rsa Sign Pkcs1 2048 Sha256", "name": "rsa-sign-pkcs1-2048-sha256"}, {"description": "3072 bit RSA - PKCS#1 v1", "help": "3072 bit RSA - PKCS#1 v1.5 padding - SHA256 Digest.", "label": "Rsa Sign Pkcs1 3072 Sha256", "name": "rsa-sign-pkcs1-3072-sha256"}, {"description": "4096 bit RSA - PKCS#1 v1", "help": "4096 bit RSA - PKCS#1 v1.5 padding - SHA256 Digest.", "label": "Rsa Sign Pkcs1 4096 Sha256", "name": "rsa-sign-pkcs1-4096-sha256"}, {"description": "4096 bit RSA - PKCS#1 v1", "help": "4096 bit RSA - PKCS#1 v1.5 padding - SHA512 Digest.", "label": "Rsa Sign Pkcs1 4096 Sha512", "name": "rsa-sign-pkcs1-4096-sha512"}, {"description": "2048 bit RSA - PSS padding - SHA256 Digest", "help": "2048 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 2048 Sha256", "name": "rsa-sign-pss-2048-sha256"}, {"description": "3072 bit RSA - PSS padding - SHA256 Digest", "help": "3072 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 3072 Sha256", "name": "rsa-sign-pss-3072-sha256"}, {"description": "4096 bit RSA - PSS padding - SHA256 Digest", "help": "4096 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 4096 Sha256", "name": "rsa-sign-pss-4096-sha256"}, {"description": "4096 bit RSA - PSS padding - SHA256 Digest", "help": "4096 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 4096 Sha512", "name": "rsa-sign-pss-4096-sha512"}, {"description": "Elliptic Curve P-256 - SHA256 Digest", "help": "Elliptic Curve P-256 - SHA256 Digest.", "label": "Ec Sign P256 Sha256", "name": "ec-sign-p256-sha256"}, {"description": "Elliptic Curve P-384 - SHA384 Digest", "help": "Elliptic Curve P-384 - SHA384 Digest.", "label": "Ec Sign P384 Sha384", "name": "ec-sign-p384-sha384"}, {"description": "Elliptic Curvesecp256k1 - SHA256 Digest", "help": "Elliptic Curvesecp256k1 - SHA256 Digest.", "label": "Ec Sign Secp256K1 Sha256", "name": "ec-sign-secp256k1-sha256"}]

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
    "VALID_BODY_VENDOR",
    "VALID_BODY_API_VERSION",
    "VALID_BODY_RANGE",
    "VALID_BODY_SOURCE",
    "VALID_BODY_GCH_CRYPTOKEY_ALGORITHM",
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