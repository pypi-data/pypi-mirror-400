from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_PLATFORM_TYPE: Literal[{"description": "Default 11n AP", "help": "Default 11n AP.", "label": "Ap 11N", "name": "AP-11N"}, {"description": "FAPC24JE", "help": "FAPC24JE.", "label": "C24Je", "name": "C24JE"}, {"description": "FAP421E", "help": "FAP421E.", "label": "421E", "name": "421E"}, {"description": "FAP423E", "help": "FAP423E.", "label": "423E", "name": "423E"}, {"description": "FAP221E", "help": "FAP221E.", "label": "221E", "name": "221E"}, {"description": "FAP222E", "help": "FAP222E.", "label": "222E", "name": "222E"}, {"description": "FAP223E", "help": "FAP223E.", "label": "223E", "name": "223E"}, {"description": "FAP224E", "help": "FAP224E.", "label": "224E", "name": "224E"}, {"description": "FAP231E", "help": "FAP231E.", "label": "231E", "name": "231E"}, {"description": "FAP321E", "help": "FAP321E.", "label": "321E", "name": "321E"}, {"description": "FAP431F", "help": "FAP431F.", "label": "431F", "name": "431F"}, {"description": "FAP431FL", "help": "FAP431FL.", "label": "431Fl", "name": "431FL"}, {"description": "FAP432F", "help": "FAP432F.", "label": "432F", "name": "432F"}, {"description": "FAP432FR", "help": "FAP432FR.", "label": "432Fr", "name": "432FR"}, {"description": "FAP433F", "help": "FAP433F.", "label": "433F", "name": "433F"}, {"description": "FAP433FL", "help": "FAP433FL.", "label": "433Fl", "name": "433FL"}, {"description": "FAP231F", "help": "FAP231F.", "label": "231F", "name": "231F"}, {"description": "FAP231FL", "help": "FAP231FL.", "label": "231Fl", "name": "231FL"}, {"description": "FAP234F", "help": "FAP234F.", "label": "234F", "name": "234F"}, {"description": "FAP23JF", "help": "FAP23JF.", "label": "23Jf", "name": "23JF"}, {"description": "FAP831F", "help": "FAP831F.", "label": "831F", "name": "831F"}, {"description": "FAP231G", "help": "FAP231G.", "label": "231G", "name": "231G"}, {"description": "FAP233G", "help": "FAP233G.", "label": "233G", "name": "233G"}, {"description": "FAP234G", "help": "FAP234G.", "label": "234G", "name": "234G"}, {"description": "FAP431G", "help": "FAP431G.", "label": "431G", "name": "431G"}, {"description": "FAP432G", "help": "FAP432G.", "label": "432G", "name": "432G"}, {"description": "FAP433G", "help": "FAP433G.", "label": "433G", "name": "433G"}, {"description": "FAP231K", "help": "FAP231K.", "label": "231K", "name": "231K"}, {"description": "FAP231KD", "help": "FAP231KD.", "label": "231Kd", "name": "231KD"}, {"description": "FAP23JK", "help": "FAP23JK.", "label": "23Jk", "name": "23JK"}, {"description": "FAP222KL", "help": "FAP222KL.", "label": "222Kl", "name": "222KL"}, {"description": "FAP241K", "help": "FAP241K.", "label": "241K", "name": "241K"}, {"description": "FAP243K", "help": "FAP243K.", "label": "243K", "name": "243K"}, {"description": "FAP244K", "help": "FAP244K.", "label": "244K", "name": "244K"}, {"description": "FAP441K", "help": "FAP441K.", "label": "441K", "name": "441K"}, {"description": "FAP432K", "help": "FAP432K.", "label": "432K", "name": "432K"}, {"description": "FAP443K", "help": "FAP443K.", "label": "443K", "name": "443K"}, {"description": "FAPU421EV", "help": "FAPU421EV.", "label": "U421E", "name": "U421E"}, {"description": "FAPU422EV", "help": "FAPU422EV.", "label": "U422Ev", "name": "U422EV"}, {"description": "FAPU423EV", "help": "FAPU423EV.", "label": "U423E", "name": "U423E"}, {"description": "FAPU221EV", "help": "FAPU221EV.", "label": "U221Ev", "name": "U221EV"}, {"description": "FAPU223EV", "help": "FAPU223EV.", "label": "U223Ev", "name": "U223EV"}, {"description": "FAPU24JEV", "help": "FAPU24JEV.", "label": "U24Jev", "name": "U24JEV"}, {"description": "FAPU321EV", "help": "FAPU321EV.", "label": "U321Ev", "name": "U321EV"}, {"description": "FAPU323EV", "help": "FAPU323EV.", "label": "U323Ev", "name": "U323EV"}, {"description": "FAPU431F", "help": "FAPU431F.", "label": "U431F", "name": "U431F"}, {"description": "FAPU433F", "help": "FAPU433F.", "label": "U433F", "name": "U433F"}, {"description": "FAPU231F", "help": "FAPU231F.", "label": "U231F", "name": "U231F"}, {"description": "FAPU234F", "help": "FAPU234F.", "label": "U234F", "name": "U234F"}, {"description": "FAPU432F", "help": "FAPU432F.", "label": "U432F", "name": "U432F"}, {"description": "FAPU231G", "help": "FAPU231G.", "label": "U231G", "name": "U231G"}, {"description": "FAP MVP", "help": "FAP MVP.", "label": "Mvp", "name": "MVP"}]

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
    "VALID_BODY_PLATFORM_TYPE",
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