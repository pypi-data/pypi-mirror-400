from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SAMPLE_MODE: Literal[{"description": "Set local mode which samples on the specific switch port", "help": "Set local mode which samples on the specific switch port.", "label": "Local", "name": "local"}, {"description": "Set perimeter mode which samples on all switch fabric ports and fortilink port at the ingress", "help": "Set perimeter mode which samples on all switch fabric ports and fortilink port at the ingress.", "label": "Perimeter", "name": "perimeter"}, {"description": "Set device -ingress mode which samples across all switch ports at the ingress", "help": "Set device -ingress mode which samples across all switch ports at the ingress.", "label": "Device Ingress", "name": "device-ingress"}]
VALID_BODY_FORMAT: Literal[{"description": "Netflow version 1 sampling", "help": "Netflow version 1 sampling.", "label": "Netflow1", "name": "netflow1"}, {"description": "Netflow version 5 sampling", "help": "Netflow version 5 sampling.", "label": "Netflow5", "name": "netflow5"}, {"description": "Netflow version 9 sampling", "help": "Netflow version 9 sampling.", "label": "Netflow9", "name": "netflow9"}, {"description": "Ipfix sampling", "help": "Ipfix sampling.", "label": "Ipfix", "name": "ipfix"}]
VALID_BODY_LEVEL: Literal[{"description": "Collects srcip/dstip/srcport/dstport/protocol/tos/vlan from the sample packet", "help": "Collects srcip/dstip/srcport/dstport/protocol/tos/vlan from the sample packet.", "label": "Vlan", "name": "vlan"}, {"description": "Collects srcip/dstip from the sample packet", "help": "Collects srcip/dstip from the sample packet.", "label": "Ip", "name": "ip"}, {"description": "Collects srcip/dstip/srcport/dstport/protocol from the sample packet", "help": "Collects srcip/dstip/srcport/dstport/protocol from the sample packet.", "label": "Port", "name": "port"}, {"description": "Collects srcip/dstip/protocol from the sample packet", "help": "Collects srcip/dstip/protocol from the sample packet.", "label": "Proto", "name": "proto"}, {"description": "Collects smac/dmac from the sample packet", "help": "Collects smac/dmac from the sample packet.", "label": "Mac", "name": "mac"}]

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
    "VALID_BODY_SAMPLE_MODE",
    "VALID_BODY_FORMAT",
    "VALID_BODY_LEVEL",
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