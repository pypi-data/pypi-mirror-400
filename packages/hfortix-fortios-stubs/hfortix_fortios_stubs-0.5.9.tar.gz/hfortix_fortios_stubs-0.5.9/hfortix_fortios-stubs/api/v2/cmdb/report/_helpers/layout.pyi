from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_OPTIONS: Literal[{"description": "Include table of content in the report", "help": "Include table of content in the report.", "label": "Include Table Of Content", "name": "include-table-of-content"}, {"description": "Prepend heading with auto numbering", "help": "Prepend heading with auto numbering.", "label": "Auto Numbering Heading", "name": "auto-numbering-heading"}, {"description": "Auto add heading for each chart", "help": "Auto add heading for each chart.", "label": "View Chart As Heading", "name": "view-chart-as-heading"}, {"description": "Show HTML navigation bar before each heading", "help": "Show HTML navigation bar before each heading.", "label": "Show Html Navbar Before Heading", "name": "show-html-navbar-before-heading"}, {"description": "Use this option if you need none of the above options", "help": "Use this option if you need none of the above options.", "label": "Dummy Option", "name": "dummy-option"}]
VALID_BODY_FORMAT: Literal[{"description": "PDF", "help": "PDF.", "label": "Pdf", "name": "pdf"}]
VALID_BODY_SCHEDULE_TYPE: Literal[{"description": "Run on demand", "help": "Run on demand.", "label": "Demand", "name": "demand"}, {"description": "Schedule daily", "help": "Schedule daily.", "label": "Daily", "name": "daily"}, {"description": "Schedule weekly", "help": "Schedule weekly.", "label": "Weekly", "name": "weekly"}]
VALID_BODY_DAY: Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}]
VALID_BODY_CUTOFF_OPTION: Literal[{"description": "Run time", "help": "Run time.", "label": "Run Time", "name": "run-time"}, {"description": "Custom", "help": "Custom.", "label": "Custom", "name": "custom"}]
VALID_BODY_EMAIL_SEND: Literal[{"description": "Enable sending emails after generating reports", "help": "Enable sending emails after generating reports.", "label": "Enable", "name": "enable"}, {"description": "Disable sending emails after generating reports", "help": "Disable sending emails after generating reports.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_OPTIONS",
    "VALID_BODY_FORMAT",
    "VALID_BODY_SCHEDULE_TYPE",
    "VALID_BODY_DAY",
    "VALID_BODY_CUTOFF_OPTION",
    "VALID_BODY_EMAIL_SEND",
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