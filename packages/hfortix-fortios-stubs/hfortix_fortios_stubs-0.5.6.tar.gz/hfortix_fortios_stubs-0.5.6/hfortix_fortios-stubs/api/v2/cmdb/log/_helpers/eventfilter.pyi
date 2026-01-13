from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_EVENT: Literal[{"description": "Enable event logging", "help": "Enable event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable event logging", "help": "Disable event logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_SYSTEM: Literal[{"description": "Enable system event logging", "help": "Enable system event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable system event logging", "help": "Disable system event logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_VPN: Literal[{"description": "Enable VPN event logging", "help": "Enable VPN event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable VPN event logging", "help": "Disable VPN event logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_USER: Literal[{"description": "Enable user authentication event logging", "help": "Enable user authentication event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable user authentication event logging", "help": "Disable user authentication event logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_ROUTER: Literal[{"description": "Enable router event logging", "help": "Enable router event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable router event logging", "help": "Disable router event logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_WIRELESS_ACTIVITY: Literal[{"description": "Enable wireless event logging", "help": "Enable wireless event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable wireless event logging", "help": "Disable wireless event logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_WAN_OPT: Literal[{"description": "Enable WAN optimization event logging", "help": "Enable WAN optimization event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable WAN optimization event logging", "help": "Disable WAN optimization event logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_ENDPOINT: Literal[{"description": "Enable endpoint event logging", "help": "Enable endpoint event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable endpoint event logging", "help": "Disable endpoint event logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_HA: Literal[{"description": "Enable ha event logging", "help": "Enable ha event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable ha event logging", "help": "Disable ha event logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_SECURITY_RATING: Literal[{"description": "Enable Security Fabric audit result logging", "help": "Enable Security Fabric audit result logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Security Fabric audit result logging", "help": "Disable Security Fabric audit result logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_FORTIEXTENDER: Literal[{"description": "Enable Forti-Extender logging", "help": "Enable Forti-Extender logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Forti-Extender logging", "help": "Disable Forti-Extender logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_CONNECTOR: Literal[{"description": "Enable SDN connector logging", "help": "Enable SDN connector logging.", "label": "Enable", "name": "enable"}, {"description": "Disable SDN connector logging", "help": "Disable SDN connector logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_SDWAN: Literal[{"description": "Enable SD-WAN logging", "help": "Enable SD-WAN logging.", "label": "Enable", "name": "enable"}, {"description": "Disable SD-WAN logging", "help": "Disable SD-WAN logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_CIFS: Literal[{"description": "Enable CIFS logging", "help": "Enable CIFS logging.", "label": "Enable", "name": "enable"}, {"description": "Disable CIFS logging", "help": "Disable CIFS logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_SWITCH_CONTROLLER: Literal[{"description": "Enable Switch-Controller logging", "help": "Enable Switch-Controller logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Switch-Controller logging", "help": "Disable Switch-Controller logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_REST_API: Literal[{"description": "Enable REST API logging", "help": "Enable REST API logging.", "label": "Enable", "name": "enable"}, {"description": "Disable REST API logging", "help": "Disable REST API logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_SVC: Literal[{"description": "Enable web-svc daemon logging", "help": "Enable web-svc daemon logging.", "label": "Enable", "name": "enable"}, {"description": "Disable web-svc daemon logging", "help": "Disable web-svc daemon logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEBPROXY: Literal[{"help": "Enable Web Proxy event logging.", "label": "Enable", "name": "enable"}, {"help": "Disable Web Proxy event logging.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_EVENT",
    "VALID_BODY_SYSTEM",
    "VALID_BODY_VPN",
    "VALID_BODY_USER",
    "VALID_BODY_ROUTER",
    "VALID_BODY_WIRELESS_ACTIVITY",
    "VALID_BODY_WAN_OPT",
    "VALID_BODY_ENDPOINT",
    "VALID_BODY_HA",
    "VALID_BODY_SECURITY_RATING",
    "VALID_BODY_FORTIEXTENDER",
    "VALID_BODY_CONNECTOR",
    "VALID_BODY_SDWAN",
    "VALID_BODY_CIFS",
    "VALID_BODY_SWITCH_CONTROLLER",
    "VALID_BODY_REST_API",
    "VALID_BODY_WEB_SVC",
    "VALID_BODY_WEBPROXY",
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