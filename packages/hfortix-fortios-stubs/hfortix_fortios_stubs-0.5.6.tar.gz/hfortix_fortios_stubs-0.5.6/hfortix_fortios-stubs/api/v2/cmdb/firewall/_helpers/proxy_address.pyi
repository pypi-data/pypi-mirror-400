from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"description": "Host regular expression", "help": "Host regular expression.", "label": "Host Regex", "name": "host-regex"}, {"description": "HTTP URL", "help": "HTTP URL.", "label": "Url", "name": "url"}, {"description": "FortiGuard URL catgegory", "help": "FortiGuard URL catgegory.", "label": "Category", "name": "category"}, {"description": "HTTP request method", "help": "HTTP request method.", "label": "Method", "name": "method"}, {"description": "HTTP request user agent", "help": "HTTP request user agent.", "label": "Ua", "name": "ua"}, {"description": "HTTP request header", "help": "HTTP request header.", "label": "Header", "name": "header"}, {"description": "HTTP advanced source criteria", "help": "HTTP advanced source criteria.", "label": "Src Advanced", "name": "src-advanced"}, {"description": "HTTP advanced destination criteria", "help": "HTTP advanced destination criteria.", "label": "Dst Advanced", "name": "dst-advanced"}, {"description": "SaaS application", "help": "SaaS application.", "label": "Saas", "name": "saas"}]
VALID_BODY_REFERRER: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_METHOD: Literal[{"description": "GET method", "help": "GET method.", "label": "Get", "name": "get"}, {"description": "POST method", "help": "POST method.", "label": "Post", "name": "post"}, {"description": "PUT method", "help": "PUT method.", "label": "Put", "name": "put"}, {"description": "HEAD method", "help": "HEAD method.", "label": "Head", "name": "head"}, {"description": "CONNECT method", "help": "CONNECT method.", "label": "Connect", "name": "connect"}, {"description": "TRACE method", "help": "TRACE method.", "label": "Trace", "name": "trace"}, {"description": "OPTIONS method", "help": "OPTIONS method.", "label": "Options", "name": "options"}, {"description": "DELETE method", "help": "DELETE method.", "label": "Delete", "name": "delete"}, {"description": "UPDATE method", "help": "UPDATE method.", "label": "Update", "name": "update"}, {"description": "PATCH method", "help": "PATCH method.", "label": "Patch", "name": "patch"}, {"description": "Other methods", "help": "Other methods.", "label": "Other", "name": "other"}]
VALID_BODY_UA: Literal[{"description": "Google Chrome", "help": "Google Chrome.", "label": "Chrome", "name": "chrome"}, {"description": "Microsoft Internet Explorer or EDGE", "help": "Microsoft Internet Explorer or EDGE.", "label": "Ms", "name": "ms"}, {"description": "Mozilla Firefox", "help": "Mozilla Firefox.", "label": "Firefox", "name": "firefox"}, {"description": "Apple Safari", "help": "Apple Safari.", "label": "Safari", "name": "safari"}, {"description": "Microsoft Internet Explorer", "help": "Microsoft Internet Explorer.", "label": "Ie", "name": "ie"}, {"description": "Microsoft Edge", "help": "Microsoft Edge.", "label": "Edge", "name": "edge"}, {"description": "Other browsers", "help": "Other browsers.", "label": "Other", "name": "other"}]
VALID_BODY_CASE_SENSITIVITY: Literal[{"description": "Case insensitive in pattern", "help": "Case insensitive in pattern.", "label": "Disable", "name": "disable"}, {"description": "Case sensitive in pattern", "help": "Case sensitive in pattern.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_TYPE",
    "VALID_BODY_REFERRER",
    "VALID_BODY_METHOD",
    "VALID_BODY_UA",
    "VALID_BODY_CASE_SENSITIVITY",
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