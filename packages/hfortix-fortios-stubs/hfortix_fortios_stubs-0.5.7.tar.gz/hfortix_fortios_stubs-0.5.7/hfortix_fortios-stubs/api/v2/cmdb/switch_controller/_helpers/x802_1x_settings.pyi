from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_LINK_DOWN_AUTH: Literal[{"description": "Interface set to unauth when down", "help": "Interface set to unauth when down. Reauthentication is needed.", "label": "Set Unauth", "name": "set-unauth"}, {"description": "Interface reauthentication is not needed", "help": "Interface reauthentication is not needed.", "label": "No Action", "name": "no-action"}]
VALID_BODY_MAB_REAUTH: Literal[{"description": "Disable MAB re-authentication", "help": "Disable MAB re-authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable MAB re-authentication", "help": "Enable MAB re-authentication.", "label": "Enable", "name": "enable"}]
VALID_BODY_MAC_USERNAME_DELIMITER: Literal[{"description": "Use colon as delimiter for MAC auth username", "help": "Use colon as delimiter for MAC auth username.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for MAC auth username", "help": "Use hyphen as delimiter for MAC auth username.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for MAC auth username", "help": "No delimiter for MAC auth username.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for MAC auth username", "help": "Use single hyphen as delimiter for MAC auth username.", "label": "Single Hyphen", "name": "single-hyphen"}]
VALID_BODY_MAC_PASSWORD_DELIMITER: Literal[{"description": "Use colon as delimiter for MAC auth password", "help": "Use colon as delimiter for MAC auth password.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for MAC auth password", "help": "Use hyphen as delimiter for MAC auth password.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for MAC auth password", "help": "No delimiter for MAC auth password.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for MAC auth password", "help": "Use single hyphen as delimiter for MAC auth password.", "label": "Single Hyphen", "name": "single-hyphen"}]
VALID_BODY_MAC_CALLING_STATION_DELIMITER: Literal[{"description": "Use colon as delimiter for calling station", "help": "Use colon as delimiter for calling station.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for calling station", "help": "Use hyphen as delimiter for calling station.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for calling station", "help": "No delimiter for calling station.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for calling station", "help": "Use single hyphen as delimiter for calling station.", "label": "Single Hyphen", "name": "single-hyphen"}]
VALID_BODY_MAC_CALLED_STATION_DELIMITER: Literal[{"description": "Use colon as delimiter for called station", "help": "Use colon as delimiter for called station.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for called station", "help": "Use hyphen as delimiter for called station.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for called station", "help": "No delimiter for called station.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for called station", "help": "Use single hyphen as delimiter for called station.", "label": "Single Hyphen", "name": "single-hyphen"}]
VALID_BODY_MAC_CASE: Literal[{"description": "Use lowercase MAC", "help": "Use lowercase MAC.", "label": "Lowercase", "name": "lowercase"}, {"description": "Use uppercase MAC", "help": "Use uppercase MAC.", "label": "Uppercase", "name": "uppercase"}]

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
    "VALID_BODY_LINK_DOWN_AUTH",
    "VALID_BODY_MAB_REAUTH",
    "VALID_BODY_MAC_USERNAME_DELIMITER",
    "VALID_BODY_MAC_PASSWORD_DELIMITER",
    "VALID_BODY_MAC_CALLING_STATION_DELIMITER",
    "VALID_BODY_MAC_CALLED_STATION_DELIMITER",
    "VALID_BODY_MAC_CASE",
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