from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_RANGE: Literal[{"description": "Global range", "help": "Global range.", "label": "Global", "name": "global"}, {"description": "VDOM IP address range", "help": "VDOM IP address range.", "label": "Vdom", "name": "vdom"}]
VALID_BODY_SOURCE: Literal[{"description": "Factory installed certificate", "help": "Factory installed certificate.", "label": "Factory", "name": "factory"}, {"description": "User generated certificate", "help": "User generated certificate.", "label": "User", "name": "user"}, {"description": "Bundle file certificate", "help": "Bundle file certificate.", "label": "Bundle", "name": "bundle"}]
VALID_BODY_NAME_ENCODING: Literal[{"description": "Printable encoding (default)", "help": "Printable encoding (default).", "label": "Printable", "name": "printable"}, {"description": "UTF-8 encoding", "help": "UTF-8 encoding.", "label": "Utf8", "name": "utf8"}]
VALID_BODY_IKE_LOCALID_TYPE: Literal[{"description": "ASN", "help": "ASN.1 distinguished name.", "label": "Asn1Dn", "name": "asn1dn"}, {"description": "Fully qualified domain name", "help": "Fully qualified domain name.", "label": "Fqdn", "name": "fqdn"}]
VALID_BODY_ENROLL_PROTOCOL: Literal[{"description": "None (default)", "help": "None (default).", "label": "None", "name": "none"}, {"description": "Simple Certificate Enrollment Protocol", "help": "Simple Certificate Enrollment Protocol.", "label": "Scep", "name": "scep"}, {"description": "Certificate Management Protocol Version 2", "help": "Certificate Management Protocol Version 2.", "label": "Cmpv2", "name": "cmpv2"}, {"description": "Automated Certificate Management Environment Version 2", "help": "Automated Certificate Management Environment Version 2.", "label": "Acme2", "name": "acme2"}, {"description": "Enrollment over Secure Transport", "help": "Enrollment over Secure Transport.", "label": "Est", "name": "est"}]
VALID_BODY_PRIVATE_KEY_RETAIN: Literal[{"description": "Keep the existing private key during SCEP renewal", "help": "Keep the existing private key during SCEP renewal.", "label": "Enable", "name": "enable"}, {"description": "Generate a new private key during SCEP renewal", "help": "Generate a new private key during SCEP renewal.", "label": "Disable", "name": "disable"}]
VALID_BODY_CMP_REGENERATION_METHOD: Literal[{"description": "Key Update", "help": "Key Update.", "label": "Keyupate", "name": "keyupate"}, {"description": "Renewal", "help": "Renewal.", "label": "Renewal", "name": "renewal"}]
VALID_BODY_EST_REGENERATION_METHOD: Literal[{"description": "Create new private key during re-enrollment", "help": "Create new private key during re-enrollment.", "label": "Create New Key", "name": "create-new-key"}, {"description": "Reuse existing private key during re-enrollment", "help": "Reuse existing private key during re-enrollment.", "label": "Use Existing Key", "name": "use-existing-key"}]

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
    "VALID_BODY_RANGE",
    "VALID_BODY_SOURCE",
    "VALID_BODY_NAME_ENCODING",
    "VALID_BODY_IKE_LOCALID_TYPE",
    "VALID_BODY_ENROLL_PROTOCOL",
    "VALID_BODY_PRIVATE_KEY_RETAIN",
    "VALID_BODY_CMP_REGENERATION_METHOD",
    "VALID_BODY_EST_REGENERATION_METHOD",
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