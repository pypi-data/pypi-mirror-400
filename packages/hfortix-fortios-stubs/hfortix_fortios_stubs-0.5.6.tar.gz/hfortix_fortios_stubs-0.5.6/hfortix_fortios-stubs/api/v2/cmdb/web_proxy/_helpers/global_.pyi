from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_FAST_POLICY_MATCH: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_LDAP_USER_CACHE: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_STRICT_WEB_CHECK: Literal[{"description": "Enable strict web checking", "help": "Enable strict web checking.", "label": "Enable", "name": "enable"}, {"description": "Disable strict web checking", "help": "Disable strict web checking.", "label": "Disable", "name": "disable"}]
VALID_BODY_FORWARD_PROXY_AUTH: Literal[{"description": "Enable forwarding proxy authentication headers", "help": "Enable forwarding proxy authentication headers.", "label": "Enable", "name": "enable"}, {"description": "Disable forwarding proxy authentication headers", "help": "Disable forwarding proxy authentication headers.", "label": "Disable", "name": "disable"}]
VALID_BODY_LEARN_CLIENT_IP: Literal[{"description": "Enable learning the client\u0027s IP address from headers", "help": "Enable learning the client\u0027s IP address from headers.", "label": "Enable", "name": "enable"}, {"description": "Disable learning the client\u0027s IP address from headers", "help": "Disable learning the client\u0027s IP address from headers.", "label": "Disable", "name": "disable"}]
VALID_BODY_ALWAYS_LEARN_CLIENT_IP: Literal[{"description": "Enable learning the client\u0027s IP address from headers for every request", "help": "Enable learning the client\u0027s IP address from headers for every request.", "label": "Enable", "name": "enable"}, {"description": "Disable learning the client\u0027s IP address from headers for every request", "help": "Disable learning the client\u0027s IP address from headers for every request.", "label": "Disable", "name": "disable"}]
VALID_BODY_LEARN_CLIENT_IP_FROM_HEADER: Literal[{"description": "Learn the client IP address from the True-Client-IP header", "help": "Learn the client IP address from the True-Client-IP header.", "label": "True Client Ip", "name": "true-client-ip"}, {"description": "Learn the client IP address from the X-Real-IP header", "help": "Learn the client IP address from the X-Real-IP header.", "label": "X Real Ip", "name": "x-real-ip"}, {"description": "Learn the client IP address from the X-Forwarded-For header", "help": "Learn the client IP address from the X-Forwarded-For header.", "label": "X Forwarded For", "name": "x-forwarded-for"}]
VALID_BODY_POLICY_PARTIAL_MATCH: Literal[{"description": "Enable policy partial matching", "help": "Enable policy partial matching.", "label": "Enable", "name": "enable"}, {"description": "Disable policy partial matching", "help": "Disable policy partial matching.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOG_POLICY_PENDING: Literal[{"description": "Enable logging sessions that are pending on policy matching", "help": "Enable logging sessions that are pending on policy matching.", "label": "Enable", "name": "enable"}, {"description": "Disable logging sessions that are pending on policy matching", "help": "Disable logging sessions that are pending on policy matching.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOG_FORWARD_SERVER: Literal[{"description": "Enable logging forward server name in forward traffic log", "help": "Enable logging forward server name in forward traffic log.", "label": "Enable", "name": "enable"}, {"description": "Disable logging forward server name in forward traffic log", "help": "Disable logging forward server name in forward traffic log.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOG_APP_ID: Literal[{"description": "Enable logging application type in traffic log", "help": "Enable logging application type in traffic log.", "label": "Enable", "name": "enable"}, {"description": "Disable logging application type in traffic log", "help": "Disable logging application type in traffic log.", "label": "Disable", "name": "disable"}]
VALID_BODY_PROXY_TRANSPARENT_CERT_INSPECTION: Literal[{"description": "Enable proxying certificate inspection in transparent mode", "help": "Enable proxying certificate inspection in transparent mode.", "label": "Enable", "name": "enable"}, {"description": "Disable proxying certificate inspection in transparent mode", "help": "Disable proxying certificate inspection in transparent mode.", "label": "Disable", "name": "disable"}]
VALID_BODY_REQUEST_OBS_FOLD: Literal[{"description": "Replace CRLF in obs-fold with SP in the request header for HTTP/1", "help": "Replace CRLF in obs-fold with SP in the request header for HTTP/1.x.", "label": "Replace With Sp", "name": "replace-with-sp"}, {"description": "Block HTTP/1", "help": "Block HTTP/1.x request with obs-fold.", "label": "Block", "name": "block"}, {"description": "Keep obs-fold in the request header for HTTP/1", "help": "Keep obs-fold in the request header for HTTP/1.x. There are known security risks.", "label": "Keep", "name": "keep"}]

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
    "VALID_BODY_FAST_POLICY_MATCH",
    "VALID_BODY_LDAP_USER_CACHE",
    "VALID_BODY_STRICT_WEB_CHECK",
    "VALID_BODY_FORWARD_PROXY_AUTH",
    "VALID_BODY_LEARN_CLIENT_IP",
    "VALID_BODY_ALWAYS_LEARN_CLIENT_IP",
    "VALID_BODY_LEARN_CLIENT_IP_FROM_HEADER",
    "VALID_BODY_POLICY_PARTIAL_MATCH",
    "VALID_BODY_LOG_POLICY_PENDING",
    "VALID_BODY_LOG_FORWARD_SERVER",
    "VALID_BODY_LOG_APP_ID",
    "VALID_BODY_PROXY_TRANSPARENT_CERT_INSPECTION",
    "VALID_BODY_REQUEST_OBS_FOLD",
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