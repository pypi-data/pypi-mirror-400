from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_ADDR_MODE: Literal[{"description": "IPv4 mode", "help": "IPv4 mode.", "label": "Ipv4", "name": "ipv4"}, {"description": "IPv6 mode", "help": "IPv6 mode.", "label": "Ipv6", "name": "ipv6"}]
VALID_BODY_SERVER_CONFIG: Literal[{"description": "All servers share the same attributes", "help": "All servers share the same attributes.", "label": "Default", "name": "default"}, {"description": "Some attributes can be specified for individual servers", "help": "Some attributes can be specified for individual servers.", "label": "Individual", "name": "individual"}]
VALID_BODY_SERVER_TYPE: Literal[{"description": "Static servers", "help": "Static servers.", "label": "Static", "name": "static"}, {"description": "Dynamic servers", "help": "Dynamic servers.", "label": "Dynamic", "name": "dynamic"}]
VALID_BODY_PROTOCOL: Literal[{"description": "PING link monitor", "help": "PING link monitor.", "label": "Ping", "name": "ping"}, {"description": "TCP echo link monitor", "help": "TCP echo link monitor.", "label": "Tcp Echo", "name": "tcp-echo"}, {"description": "UDP echo link monitor", "help": "UDP echo link monitor.", "label": "Udp Echo", "name": "udp-echo"}, {"description": "HTTP-GET link monitor", "help": "HTTP-GET link monitor.", "label": "Http", "name": "http"}, {"description": "HTTPS-GET link monitor", "help": "HTTPS-GET link monitor.", "label": "Https", "name": "https"}, {"description": "TWAMP link monitor", "help": "TWAMP link monitor.", "label": "Twamp", "name": "twamp"}]
VALID_BODY_SECURITY_MODE: Literal[{"description": "Unauthenticated mode", "help": "Unauthenticated mode.", "label": "None", "name": "none"}, {"description": "Authenticated mode", "help": "Authenticated mode.", "label": "Authentication", "name": "authentication"}]
VALID_BODY_UPDATE_CASCADE_INTERFACE: Literal[{"description": "Enable update cascade interface", "help": "Enable update cascade interface.", "label": "Enable", "name": "enable"}, {"description": "Disable update cascade interface", "help": "Disable update cascade interface.", "label": "Disable", "name": "disable"}]
VALID_BODY_UPDATE_STATIC_ROUTE: Literal[{"description": "Enable updating the static route", "help": "Enable updating the static route.", "label": "Enable", "name": "enable"}, {"description": "Disable updating the static route", "help": "Disable updating the static route.", "label": "Disable", "name": "disable"}]
VALID_BODY_UPDATE_POLICY_ROUTE: Literal[{"description": "Enable updating the policy route", "help": "Enable updating the policy route.", "label": "Enable", "name": "enable"}, {"description": "Disable updating the policy route", "help": "Disable updating the policy route.", "label": "Disable", "name": "disable"}]
VALID_BODY_STATUS: Literal[{"description": "Enable this link monitor", "help": "Enable this link monitor.", "label": "Enable", "name": "enable"}, {"description": "Disable this link monitor", "help": "Disable this link monitor.", "label": "Disable", "name": "disable"}]
VALID_BODY_SERVICE_DETECTION: Literal[{"description": "Only use monitor for service-detection", "help": "Only use monitor for service-detection.", "label": "Enable", "name": "enable"}, {"description": "Monitor will update routes/interfaces on link failure", "help": "Monitor will update routes/interfaces on link failure.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_ADDR_MODE",
    "VALID_BODY_SERVER_CONFIG",
    "VALID_BODY_SERVER_TYPE",
    "VALID_BODY_PROTOCOL",
    "VALID_BODY_SECURITY_MODE",
    "VALID_BODY_UPDATE_CASCADE_INTERFACE",
    "VALID_BODY_UPDATE_STATIC_ROUTE",
    "VALID_BODY_UPDATE_POLICY_ROUTE",
    "VALID_BODY_STATUS",
    "VALID_BODY_SERVICE_DETECTION",
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