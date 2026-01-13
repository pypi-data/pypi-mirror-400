from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_PORTS_DEFINED: Literal[{"description": "Source port match", "help": "Source port match.", "label": "Source", "name": "source"}, {"description": "Destination port match", "help": "Destination port match.", "label": "Destination", "name": "destination"}]
VALID_BODY_SERVER_TYPE: Literal[{"description": "Forward server", "help": "Forward server.", "label": "Forward", "name": "forward"}, {"description": "Proxy server", "help": "Proxy server.", "label": "Proxy", "name": "proxy"}]
VALID_BODY_AUTHENTICATION: Literal[{"description": "Enable MD5 authentication", "help": "Enable MD5 authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable MD5 authentication", "help": "Disable MD5 authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_FORWARD_METHOD: Literal[{"description": "GRE encapsulation", "help": "GRE encapsulation.", "label": "Gre", "name": "GRE"}, {"description": "L2 rewrite", "help": "L2 rewrite.", "label": "L2", "name": "L2"}, {"description": "GRE or L2", "help": "GRE or L2.", "label": "Any", "name": "any"}]
VALID_BODY_CACHE_ENGINE_METHOD: Literal[{"description": "GRE encapsulation", "help": "GRE encapsulation.", "label": "Gre", "name": "GRE"}, {"description": "L2 rewrite", "help": "L2 rewrite.", "label": "L2", "name": "L2"}]
VALID_BODY_SERVICE_TYPE: Literal[{"description": "auto    standard:Standard service", "help": "auto", "label": "Auto", "name": "auto"}, {"help": "Standard service.", "label": "Standard", "name": "standard"}, {"description": "Dynamic service", "help": "Dynamic service.", "label": "Dynamic", "name": "dynamic"}]
VALID_BODY_PRIMARY_HASH: Literal[{"description": "Source IP hash", "help": "Source IP hash.", "label": "Src Ip", "name": "src-ip"}, {"description": "Destination IP hash", "help": "Destination IP hash.", "label": "Dst Ip", "name": "dst-ip"}, {"description": "Source port hash", "help": "Source port hash.", "label": "Src Port", "name": "src-port"}, {"description": "Destination port hash", "help": "Destination port hash.", "label": "Dst Port", "name": "dst-port"}]
VALID_BODY_ASSIGNMENT_BUCKET_FORMAT: Literal[{"description": "WCCP-v2 bucket format", "help": "WCCP-v2 bucket format.", "label": "Wccp V2", "name": "wccp-v2"}, {"description": "Cisco bucket format", "help": "Cisco bucket format.", "label": "Cisco Implementation", "name": "cisco-implementation"}]
VALID_BODY_RETURN_METHOD: Literal[{"description": "GRE encapsulation", "help": "GRE encapsulation.", "label": "Gre", "name": "GRE"}, {"description": "L2 rewrite", "help": "L2 rewrite.", "label": "L2", "name": "L2"}, {"description": "GRE or L2", "help": "GRE or L2.", "label": "Any", "name": "any"}]
VALID_BODY_ASSIGNMENT_METHOD: Literal[{"description": "HASH assignment method", "help": "HASH assignment method.", "label": "Hash", "name": "HASH"}, {"description": "MASK assignment method", "help": "MASK assignment method.", "label": "Mask", "name": "MASK"}, {"description": "HASH or MASK", "help": "HASH or MASK.", "label": "Any", "name": "any"}]

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
    "VALID_BODY_PORTS_DEFINED",
    "VALID_BODY_SERVER_TYPE",
    "VALID_BODY_AUTHENTICATION",
    "VALID_BODY_FORWARD_METHOD",
    "VALID_BODY_CACHE_ENGINE_METHOD",
    "VALID_BODY_SERVICE_TYPE",
    "VALID_BODY_PRIMARY_HASH",
    "VALID_BODY_ASSIGNMENT_BUCKET_FORMAT",
    "VALID_BODY_RETURN_METHOD",
    "VALID_BODY_ASSIGNMENT_METHOD",
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