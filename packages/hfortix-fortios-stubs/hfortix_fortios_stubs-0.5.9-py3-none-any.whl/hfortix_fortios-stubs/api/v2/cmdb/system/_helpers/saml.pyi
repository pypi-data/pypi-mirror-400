from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable SAML authentication", "help": "Enable SAML authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable SAML authentication", "help": "Disable SAML authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_ROLE: Literal[{"description": "Identity Provider", "help": "Identity Provider.", "label": "Identity Provider", "name": "identity-provider"}, {"description": "Service Provider", "help": "Service Provider.", "label": "Service Provider", "name": "service-provider"}]
VALID_BODY_DEFAULT_LOGIN_PAGE: Literal[{"description": "Use local login page as default", "help": "Use local login page as default.", "label": "Normal", "name": "normal"}, {"description": "Use IdP\u0027s Single Sign-On page as default", "help": "Use IdP\u0027s Single Sign-On page as default.", "label": "Sso", "name": "sso"}]
VALID_BODY_BINDING_PROTOCOL: Literal[{"description": "HTTP POST binding", "help": "HTTP POST binding.", "label": "Post", "name": "post"}, {"description": "HTTP Redirect binding", "help": "HTTP Redirect binding.", "label": "Redirect", "name": "redirect"}]
VALID_BODY_REQUIRE_SIGNED_RESP_AND_ASRT: Literal[{"description": "Both response and assertion must be signed and valid", "help": "Both response and assertion must be signed and valid.", "label": "Enable", "name": "enable"}, {"description": "At least one of response or assertion must be signed and valid", "help": "At least one of response or assertion must be signed and valid.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_STATUS",
    "VALID_BODY_ROLE",
    "VALID_BODY_DEFAULT_LOGIN_PAGE",
    "VALID_BODY_BINDING_PROTOCOL",
    "VALID_BODY_REQUIRE_SIGNED_RESP_AND_ASRT",
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