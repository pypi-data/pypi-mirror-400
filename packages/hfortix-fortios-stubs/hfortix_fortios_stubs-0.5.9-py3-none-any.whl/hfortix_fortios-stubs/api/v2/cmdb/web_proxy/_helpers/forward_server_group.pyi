from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_AFFINITY: Literal[{"description": "Enable affinity", "help": "Enable affinity.", "label": "Enable", "name": "enable"}, {"description": "Disable affinity", "help": "Disable affinity.", "label": "Disable", "name": "disable"}]
VALID_BODY_LDB_METHOD: Literal[{"description": "Load balance traffic to forward servers based on assigned weights", "help": "Load balance traffic to forward servers based on assigned weights. Weights are ratios of total number of sessions.", "label": "Weighted", "name": "weighted"}, {"description": "Send new sessions to the server with lowest session count", "help": "Send new sessions to the server with lowest session count.", "label": "Least Session", "name": "least-session"}, {"description": "Send new sessions to the next active server in the list", "help": "Send new sessions to the next active server in the list. Servers are selected with highest weight first and then in order as they are configured. Traffic switches back to the first server upon failure recovery.", "label": "Active Passive", "name": "active-passive"}]
VALID_BODY_GROUP_DOWN_OPTION: Literal[{"description": "Block sessions until at least one server in the group is back up", "help": "Block sessions until at least one server in the group is back up.", "label": "Block", "name": "block"}, {"description": "Pass sessions to their destination bypassing servers in the forward server group", "help": "Pass sessions to their destination bypassing servers in the forward server group.", "label": "Pass", "name": "pass"}]

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
    "VALID_BODY_AFFINITY",
    "VALID_BODY_LDB_METHOD",
    "VALID_BODY_GROUP_DOWN_OPTION",
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