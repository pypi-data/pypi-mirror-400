from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_OCSP_STATUS: Literal[{"description": "OCSP is performed if CRL is not checked", "help": "OCSP is performed if CRL is not checked.", "label": "Enable", "name": "enable"}, {"description": "If cert is not revoked by CRL, OCSP is performed", "help": "If cert is not revoked by CRL, OCSP is performed.", "label": "Mandatory", "name": "mandatory"}, {"description": "OCSP is not performed", "help": "OCSP is not performed.", "label": "Disable", "name": "disable"}]
VALID_BODY_OCSP_OPTION: Literal[{"description": "Use URL from certificate", "help": "Use URL from certificate.", "label": "Certificate", "name": "certificate"}, {"description": "Use URL from configured OCSP server", "help": "Use URL from configured OCSP server.", "label": "Server", "name": "server"}]
VALID_BODY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]
VALID_BODY_CHECK_CA_CERT: Literal[{"description": "Enable verification of the user certificate", "help": "Enable verification of the user certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable verification of the user certificate", "help": "Disable verification of the user certificate.", "label": "Disable", "name": "disable"}]
VALID_BODY_CHECK_CA_CHAIN: Literal[{"description": "Enable verification of the entire certificate chain", "help": "Enable verification of the entire certificate chain.", "label": "Enable", "name": "enable"}, {"description": "Disable verification of the entire certificate chain", "help": "Disable verification of the entire certificate chain.", "label": "Disable", "name": "disable"}]
VALID_BODY_SUBJECT_MATCH: Literal[{"description": "Find a match if the name being searched for is a part or the same as a certificate subject RDN", "help": "Find a match if the name being searched for is a part or the same as a certificate subject RDN.", "label": "Substring", "name": "substring"}, {"description": "Find a match if the name being searched for is same as a certificate subject RDN", "help": "Find a match if the name being searched for is same as a certificate subject RDN.", "label": "Value", "name": "value"}]
VALID_BODY_SUBJECT_SET: Literal[{"description": "Find a match if the name being searched for is a subset of a certificate subject", "help": "Find a match if the name being searched for is a subset of a certificate subject.", "label": "Subset", "name": "subset"}, {"description": "Find a match if the name being searched for is a superset of a certificate subject", "help": "Find a match if the name being searched for is a superset of a certificate subject.", "label": "Superset", "name": "superset"}]
VALID_BODY_CN_MATCH: Literal[{"description": "Find a match if the name being searched for is a part or the same as a certificate CN", "help": "Find a match if the name being searched for is a part or the same as a certificate CN.", "label": "Substring", "name": "substring"}, {"description": "Find a match if the name being searched for is same as a certificate CN", "help": "Find a match if the name being searched for is same as a certificate CN.", "label": "Value", "name": "value"}]
VALID_BODY_CN_ALLOW_MULTI: Literal[{"description": "Does not allow multiple CN entries in certificate matching", "help": "Does not allow multiple CN entries in certificate matching.", "label": "Disable", "name": "disable"}, {"description": "Allow multiple CN entries in certificate matching", "help": "Allow multiple CN entries in certificate matching.", "label": "Enable", "name": "enable"}]
VALID_BODY_STRICT_OCSP_CHECK: Literal[{"description": "Enable strict mode OCSP checking", "help": "Enable strict mode OCSP checking.", "label": "Enable", "name": "enable"}, {"description": "Disable strict mode OCSP checking", "help": "Disable strict mode OCSP checking.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSL_MIN_PROTO_VERSION: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]
VALID_BODY_CMP_SAVE_EXTRA_CERTS: Literal[{"description": "Enable saving extra certificates in CMP mode", "help": "Enable saving extra certificates in CMP mode.", "label": "Enable", "name": "enable"}, {"description": "Disable saving extra certificates in CMP mode", "help": "Disable saving extra certificates in CMP mode.", "label": "Disable", "name": "disable"}]
VALID_BODY_CMP_KEY_USAGE_CHECKING: Literal[{"description": "Enable server certificate key usage checking in CMP mode", "help": "Enable server certificate key usage checking in CMP mode.", "label": "Enable", "name": "enable"}, {"description": "Disable server certificate key usage checking in CMP mode", "help": "Disable server certificate key usage checking in CMP mode.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_OCSP_STATUS",
    "VALID_BODY_OCSP_OPTION",
    "VALID_BODY_INTERFACE_SELECT_METHOD",
    "VALID_BODY_CHECK_CA_CERT",
    "VALID_BODY_CHECK_CA_CHAIN",
    "VALID_BODY_SUBJECT_MATCH",
    "VALID_BODY_SUBJECT_SET",
    "VALID_BODY_CN_MATCH",
    "VALID_BODY_CN_ALLOW_MULTI",
    "VALID_BODY_STRICT_OCSP_CHECK",
    "VALID_BODY_SSL_MIN_PROTO_VERSION",
    "VALID_BODY_CMP_SAVE_EXTRA_CERTS",
    "VALID_BODY_CMP_KEY_USAGE_CHECKING",
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