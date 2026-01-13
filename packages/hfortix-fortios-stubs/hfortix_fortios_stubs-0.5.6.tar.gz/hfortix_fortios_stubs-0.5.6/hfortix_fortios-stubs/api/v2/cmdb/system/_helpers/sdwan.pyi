from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Disable SD-WAN", "help": "Disable SD-WAN.", "label": "Disable", "name": "disable"}, {"description": "Enable SD-WAN", "help": "Enable SD-WAN.", "label": "Enable", "name": "enable"}]
VALID_BODY_LOAD_BALANCE_MODE: Literal[{"description": "Source IP load balancing", "help": "Source IP load balancing. All traffic from a source IP is sent to the same interface.", "label": "Source Ip Based", "name": "source-ip-based"}, {"description": "Weight-based load balancing", "help": "Weight-based load balancing. Interfaces with higher weights have higher priority and get more traffic.", "label": "Weight Based", "name": "weight-based"}, {"description": "Usage-based load balancing", "help": "Usage-based load balancing. All traffic is sent to the first interface on the list. When the bandwidth on that interface exceeds the spill-over limit new traffic is sent to the next interface.", "label": "Usage Based", "name": "usage-based"}, {"description": "Source and destination IP load balancing", "help": "Source and destination IP load balancing. All traffic from a source IP to a destination IP is sent to the same interface.", "label": "Source Dest Ip Based", "name": "source-dest-ip-based"}, {"description": "Volume-based load balancing", "help": "Volume-based load balancing. Traffic is load balanced based on traffic volume (in bytes). More traffic is sent to interfaces with higher volume ratios.", "label": "Measured Volume Based", "name": "measured-volume-based"}]
VALID_BODY_SPEEDTEST_BYPASS_ROUTING: Literal[{"description": "Disable SD-WAN", "help": "Disable SD-WAN.", "label": "Disable", "name": "disable"}, {"description": "Enable SD-WAN", "help": "Enable SD-WAN.", "label": "Enable", "name": "enable"}]
VALID_BODY_NEIGHBOR_HOLD_DOWN: Literal[{"description": "Enable hold switching from the secondary neighbor to the primary neighbor", "help": "Enable hold switching from the secondary neighbor to the primary neighbor.", "label": "Enable", "name": "enable"}, {"description": "Disable hold switching from the secondary neighbor to the primary neighbor", "help": "Disable hold switching from the secondary neighbor to the primary neighbor.", "label": "Disable", "name": "disable"}]
VALID_BODY_FAIL_DETECT: Literal[{"description": "Enable status checking", "help": "Enable status checking.", "label": "Enable", "name": "enable"}, {"description": "Disable status checking", "help": "Disable status checking.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_LOAD_BALANCE_MODE",
    "VALID_BODY_SPEEDTEST_BYPASS_ROUTING",
    "VALID_BODY_NEIGHBOR_HOLD_DOWN",
    "VALID_BODY_FAIL_DETECT",
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