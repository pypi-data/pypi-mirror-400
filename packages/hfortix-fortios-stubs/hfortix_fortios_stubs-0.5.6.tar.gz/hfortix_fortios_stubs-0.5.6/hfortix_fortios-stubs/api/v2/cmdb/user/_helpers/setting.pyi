from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_AUTH_TYPE: Literal[{"description": "Allow HTTP authentication", "help": "Allow HTTP authentication.", "label": "Http", "name": "http"}, {"description": "Allow HTTPS authentication", "help": "Allow HTTPS authentication.", "label": "Https", "name": "https"}, {"description": "Allow FTP authentication", "help": "Allow FTP authentication.", "label": "Ftp", "name": "ftp"}, {"description": "Allow TELNET authentication", "help": "Allow TELNET authentication.", "label": "Telnet", "name": "telnet"}]
VALID_BODY_AUTH_SECURE_HTTP: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTH_HTTP_BASIC: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTH_SSL_ALLOW_RENEGOTIATION: Literal[{"description": "Allow SSL re-negotiation", "help": "Allow SSL re-negotiation.", "label": "Enable", "name": "enable"}, {"description": "Forbid SSL re-negotiation", "help": "Forbid SSL re-negotiation.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTH_SRC_MAC: Literal[{"description": "Enable source MAC for user identity", "help": "Enable source MAC for user identity.", "label": "Enable", "name": "enable"}, {"description": "Disable source MAC for user identity", "help": "Disable source MAC for user identity.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTH_ON_DEMAND: Literal[{"description": "Always trigger firewall authentication on demand", "help": "Always trigger firewall authentication on demand.", "label": "Always", "name": "always"}, {"description": "Implicitly trigger firewall authentication on demand", "help": "Implicitly trigger firewall authentication on demand.", "label": "Implicitly", "name": "implicitly"}]
VALID_BODY_AUTH_TIMEOUT_TYPE: Literal[{"description": "Idle timeout", "help": "Idle timeout.", "label": "Idle Timeout", "name": "idle-timeout"}, {"description": "Hard timeout", "help": "Hard timeout.", "label": "Hard Timeout", "name": "hard-timeout"}, {"description": "New session timeout", "help": "New session timeout.", "label": "New Session", "name": "new-session"}]
VALID_BODY_RADIUS_SES_TIMEOUT_ACT: Literal[{"description": "Use session timeout from RADIUS as hard-timeout", "help": "Use session timeout from RADIUS as hard-timeout.", "label": "Hard Timeout", "name": "hard-timeout"}, {"description": "Ignore session timeout from RADIUS", "help": "Ignore session timeout from RADIUS.", "label": "Ignore Timeout", "name": "ignore-timeout"}]
VALID_BODY_PER_POLICY_DISCLAIMER: Literal[{"description": "Enable per policy disclaimer", "help": "Enable per policy disclaimer.", "label": "Enable", "name": "enable"}, {"description": "Disable per policy disclaimer", "help": "Disable per policy disclaimer.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTH_SSL_MIN_PROTO_VERSION: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]
VALID_BODY_AUTH_SSL_MAX_PROTO_VERSION: Literal[{"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "sslv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "tlsv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "tlsv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "tlsv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "tlsv1-3"}]
VALID_BODY_AUTH_SSL_SIGALGS: Literal[{"description": "Disable RSA-PSS signature algorithms for HTTPS authentication", "help": "Disable RSA-PSS signature algorithms for HTTPS authentication.", "label": "No Rsa Pss", "name": "no-rsa-pss"}, {"description": "Enable all supported signature algorithms for HTTPS authentication", "help": "Enable all supported signature algorithms for HTTPS authentication.", "label": "All", "name": "all"}]
VALID_BODY_CORS: Literal[{"description": "Disable allowed origins white list for CORS", "help": "Disable allowed origins white list for CORS.", "label": "Disable", "name": "disable"}, {"description": "Enable allowed origins white list for CORS", "help": "Enable allowed origins white list for CORS.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_AUTH_TYPE",
    "VALID_BODY_AUTH_SECURE_HTTP",
    "VALID_BODY_AUTH_HTTP_BASIC",
    "VALID_BODY_AUTH_SSL_ALLOW_RENEGOTIATION",
    "VALID_BODY_AUTH_SRC_MAC",
    "VALID_BODY_AUTH_ON_DEMAND",
    "VALID_BODY_AUTH_TIMEOUT_TYPE",
    "VALID_BODY_RADIUS_SES_TIMEOUT_ACT",
    "VALID_BODY_PER_POLICY_DISCLAIMER",
    "VALID_BODY_AUTH_SSL_MIN_PROTO_VERSION",
    "VALID_BODY_AUTH_SSL_MAX_PROTO_VERSION",
    "VALID_BODY_AUTH_SSL_SIGALGS",
    "VALID_BODY_CORS",
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