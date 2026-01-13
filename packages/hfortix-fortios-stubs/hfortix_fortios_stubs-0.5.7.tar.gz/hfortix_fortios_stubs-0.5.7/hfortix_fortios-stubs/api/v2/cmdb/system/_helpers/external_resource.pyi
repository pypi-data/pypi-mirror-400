from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable user resource", "help": "Enable user resource.", "label": "Enable", "name": "enable"}, {"description": "Disable user resource", "help": "Disable user resource.", "label": "Disable", "name": "disable"}]
VALID_BODY_TYPE: Literal[{"description": "FortiGuard category", "help": "FortiGuard category.", "label": "Category", "name": "category"}, {"description": "Domain Name", "help": "Domain Name.", "label": "Domain", "name": "domain"}, {"description": "Malware hash", "help": "Malware hash.", "label": "Malware", "name": "malware"}, {"description": "Firewall IP address", "help": "Firewall IP address.", "label": "Address", "name": "address"}, {"description": "Firewall MAC address", "help": "Firewall MAC address.", "label": "Mac Address", "name": "mac-address"}, {"description": "Data file", "help": "Data file.", "label": "Data", "name": "data"}, {"description": "Generic addresses", "help": "Generic addresses.", "label": "Generic Address", "name": "generic-address"}]
VALID_BODY_UPDATE_METHOD: Literal[{"description": "FortiGate unit will pull update from the external resource", "help": "FortiGate unit will pull update from the external resource.", "label": "Feed", "name": "feed"}, {"description": "External Resource update is pushed to the FortiGate unit through the FortiGate unit\u0027s RESTAPI/CLI", "help": "External Resource update is pushed to the FortiGate unit through the FortiGate unit\u0027s RESTAPI/CLI.", "label": "Push", "name": "push"}]
VALID_BODY_CLIENT_CERT_AUTH: Literal[{"description": "Enable using client certificate for TLS authentication", "help": "Enable using client certificate for TLS authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable using client certificate for TLS authentication", "help": "Disable using client certificate for TLS authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_SERVER_IDENTITY_CHECK: Literal[{"description": "No certificate verification", "help": "No certificate verification.", "label": "None", "name": "none"}, {"description": "Check server certifcate only", "help": "Check server certifcate only.", "label": "Basic", "name": "basic"}, {"description": "Check server certificate and verify the domain matches in the server certificate", "help": "Check server certificate and verify the domain matches in the server certificate.", "label": "Full", "name": "full"}]
VALID_BODY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]

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
    "VALID_BODY_TYPE",
    "VALID_BODY_UPDATE_METHOD",
    "VALID_BODY_CLIENT_CERT_AUTH",
    "VALID_BODY_SERVER_IDENTITY_CHECK",
    "VALID_BODY_INTERFACE_SELECT_METHOD",
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