from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"description": "Uses the IP prefix to define a range of IPv6 addresses", "help": "Uses the IP prefix to define a range of IPv6 addresses.", "label": "Ipprefix", "name": "ipprefix"}, {"description": "Range of IPv6 addresses between two specified addresses (inclusive)", "help": "Range of IPv6 addresses between two specified addresses (inclusive).", "label": "Iprange", "name": "iprange"}, {"description": "Fully qualified domain name", "help": "Fully qualified domain name.", "label": "Fqdn", "name": "fqdn"}, {"description": "IPv6 addresses from a specified country", "help": "IPv6 addresses from a specified country.", "label": "Geography", "name": "geography"}, {"description": "Dynamic address object for SDN", "help": "Dynamic address object for SDN.", "label": "Dynamic", "name": "dynamic"}, {"description": "Template", "help": "Template.", "label": "Template", "name": "template"}, {"description": "Range of MAC addresses", "help": "Range of MAC addresses.", "label": "Mac", "name": "mac"}, {"description": "route-tag addresses", "help": "route-tag addresses.", "label": "Route Tag", "name": "route-tag"}, {"description": "Standard IPv6 using a wildcard subnet mask", "help": "Standard IPv6 using a wildcard subnet mask.", "label": "Wildcard", "name": "wildcard"}]
VALID_BODY_HOST_TYPE: Literal[{"description": "Wildcard", "help": "Wildcard.", "label": "Any", "name": "any"}, {"description": "Specific host address", "help": "Specific host address.", "label": "Specific", "name": "specific"}]
VALID_BODY_SDN_ADDR_TYPE: Literal[{"description": "Collect private addresses only", "help": "Collect private addresses only.", "label": "Private", "name": "private"}, {"description": "Collect public addresses only", "help": "Collect public addresses only.", "label": "Public", "name": "public"}, {"description": "Collect both public and private addresses", "help": "Collect both public and private addresses.", "label": "All", "name": "all"}]
VALID_BODY_PASSIVE_FQDN_LEARNING: Literal[{"description": "Disable passive learning of FQDNs", "help": "Disable passive learning of FQDNs.", "label": "Disable", "name": "disable"}, {"description": "Enable passive learning of FQDNs", "help": "Enable passive learning of FQDNs.", "label": "Enable", "name": "enable"}]
VALID_BODY_FABRIC_OBJECT: Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_HOST_TYPE",
    "VALID_BODY_SDN_ADDR_TYPE",
    "VALID_BODY_PASSIVE_FQDN_LEARNING",
    "VALID_BODY_FABRIC_OBJECT",
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