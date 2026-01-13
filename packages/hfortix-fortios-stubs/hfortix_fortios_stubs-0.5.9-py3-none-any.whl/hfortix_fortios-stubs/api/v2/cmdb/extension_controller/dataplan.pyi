from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class DataplanPayload(TypedDict, total=False):
    """
    Type hints for extension_controller/dataplan payload fields.
    
    FortiExtender dataplan configuration.
    
    **Usage:**
        payload: DataplanPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # FortiExtender data plan name.
    modem_id: NotRequired[Literal[{"description": "Modem one", "help": "Modem one.", "label": "Modem1", "name": "modem1"}, {"description": "Modem two", "help": "Modem two.", "label": "Modem2", "name": "modem2"}, {"description": "All modems", "help": "All modems.", "label": "All", "name": "all"}]]  # Dataplan's modem specifics, if any.
    type: Literal[{"description": "Assign by SIM carrier", "help": "Assign by SIM carrier.", "label": "Carrier", "name": "carrier"}, {"description": "Assign to SIM slot 1 or 2", "help": "Assign to SIM slot 1 or 2.", "label": "Slot", "name": "slot"}, {"description": "Assign to a specific SIM by ICCID", "help": "Assign to a specific SIM by ICCID.", "label": "Iccid", "name": "iccid"}, {"description": "Compatible with any SIM", "help": "Compatible with any SIM. Assigned if no other dataplan matches the chosen SIM.", "label": "Generic", "name": "generic"}]  # Type preferences configuration.
    slot: Literal[{"description": "Sim slot one", "help": "Sim slot one.", "label": "Sim1", "name": "sim1"}, {"description": "Sim slot two", "help": "Sim slot two.", "label": "Sim2", "name": "sim2"}]  # SIM slot configuration.
    iccid: str  # ICCID configuration.
    carrier: str  # Carrier configuration.
    apn: NotRequired[str]  # APN configuration.
    auth_type: NotRequired[Literal[{"description": "No authentication", "help": "No authentication.", "label": "None", "name": "none"}, {"description": "PAP", "help": "PAP.", "label": "Pap", "name": "pap"}, {"description": "CHAP", "help": "CHAP.", "label": "Chap", "name": "chap"}]]  # Authentication type.
    username: str  # Username.
    password: str  # Password.
    pdn: NotRequired[Literal[{"description": "IPv4 only PDN activation", "help": "IPv4 only PDN activation.", "label": "Ipv4 Only", "name": "ipv4-only"}, {"description": "IPv6 only PDN activation", "help": "IPv6 only PDN activation.", "label": "Ipv6 Only", "name": "ipv6-only"}, {"description": "Both IPv4 and IPv6 PDN activations", "help": "Both IPv4 and IPv6 PDN activations.", "label": "Ipv4 Ipv6", "name": "ipv4-ipv6"}]]  # PDN type.
    signal_threshold: NotRequired[int]  # Signal threshold. Specify the range between 50 - 100, where 
    signal_period: NotRequired[int]  # Signal period (600 to 18000 seconds).
    capacity: NotRequired[int]  # Capacity in MB (0 - 102400000).
    monthly_fee: NotRequired[int]  # Monthly fee of dataplan (0 - 100000, in local currency).
    billing_date: NotRequired[int]  # Billing day of the month (1 - 31).
    overage: NotRequired[Literal[{"description": "Disable dataplan overage detection", "help": "Disable dataplan overage detection.", "label": "Disable", "name": "disable"}, {"description": "Enable dataplan overage detection", "help": "Enable dataplan overage detection.", "label": "Enable", "name": "enable"}]]  # Enable/disable dataplan overage detection.
    preferred_subnet: NotRequired[int]  # Preferred subnet mask (0 - 32).
    private_network: NotRequired[Literal[{"description": "Disable dataplan private network support", "help": "Disable dataplan private network support.", "label": "Disable", "name": "disable"}, {"description": "Enable dataplan private network support", "help": "Enable dataplan private network support.", "label": "Enable", "name": "enable"}]]  # Enable/disable dataplan private network support.


class Dataplan:
    """
    FortiExtender dataplan configuration.
    
    Path: extension_controller/dataplan
    Category: cmdb
    Primary Key: name
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: Literal[False] = ...,
        response_mode: Literal["object"] = ...,
        **kwargs: Any,
    ) -> list[FortiObject]: ...
    
    @overload
    def get(
        self,
        name: str,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: Literal[False] = ...,
        response_mode: Literal["object"] = ...,
        **kwargs: Any,
    ) -> FortiObject: ...
    
    @overload
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: Literal[True] = ...,
        response_mode: Literal["object"] = ...,
        **kwargs: Any,
    ) -> dict[str, Any]: ...
    
    # Default overload for dict mode
    @overload
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        response_mode: Literal["dict"] | None = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], list[dict[str, Any]]]: ...
    
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        response_mode: str | None = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], list[dict[str, Any]], FortiObject, list[FortiObject]]: ...
    
    def get_schema(
        self,
        vdom: str | None = ...,
        format: str = ...,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def post(
        self,
        payload_dict: DataplanPayload | None = ...,
        name: str | None = ...,
        modem_id: Literal[{"description": "Modem one", "help": "Modem one.", "label": "Modem1", "name": "modem1"}, {"description": "Modem two", "help": "Modem two.", "label": "Modem2", "name": "modem2"}, {"description": "All modems", "help": "All modems.", "label": "All", "name": "all"}] | None = ...,
        type: Literal[{"description": "Assign by SIM carrier", "help": "Assign by SIM carrier.", "label": "Carrier", "name": "carrier"}, {"description": "Assign to SIM slot 1 or 2", "help": "Assign to SIM slot 1 or 2.", "label": "Slot", "name": "slot"}, {"description": "Assign to a specific SIM by ICCID", "help": "Assign to a specific SIM by ICCID.", "label": "Iccid", "name": "iccid"}, {"description": "Compatible with any SIM", "help": "Compatible with any SIM. Assigned if no other dataplan matches the chosen SIM.", "label": "Generic", "name": "generic"}] | None = ...,
        slot: Literal[{"description": "Sim slot one", "help": "Sim slot one.", "label": "Sim1", "name": "sim1"}, {"description": "Sim slot two", "help": "Sim slot two.", "label": "Sim2", "name": "sim2"}] | None = ...,
        iccid: str | None = ...,
        carrier: str | None = ...,
        apn: str | None = ...,
        auth_type: Literal[{"description": "No authentication", "help": "No authentication.", "label": "None", "name": "none"}, {"description": "PAP", "help": "PAP.", "label": "Pap", "name": "pap"}, {"description": "CHAP", "help": "CHAP.", "label": "Chap", "name": "chap"}] | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        pdn: Literal[{"description": "IPv4 only PDN activation", "help": "IPv4 only PDN activation.", "label": "Ipv4 Only", "name": "ipv4-only"}, {"description": "IPv6 only PDN activation", "help": "IPv6 only PDN activation.", "label": "Ipv6 Only", "name": "ipv6-only"}, {"description": "Both IPv4 and IPv6 PDN activations", "help": "Both IPv4 and IPv6 PDN activations.", "label": "Ipv4 Ipv6", "name": "ipv4-ipv6"}] | None = ...,
        signal_threshold: int | None = ...,
        signal_period: int | None = ...,
        capacity: int | None = ...,
        monthly_fee: int | None = ...,
        billing_date: int | None = ...,
        overage: Literal[{"description": "Disable dataplan overage detection", "help": "Disable dataplan overage detection.", "label": "Disable", "name": "disable"}, {"description": "Enable dataplan overage detection", "help": "Enable dataplan overage detection.", "label": "Enable", "name": "enable"}] | None = ...,
        preferred_subnet: int | None = ...,
        private_network: Literal[{"description": "Disable dataplan private network support", "help": "Disable dataplan private network support.", "label": "Disable", "name": "disable"}, {"description": "Enable dataplan private network support", "help": "Enable dataplan private network support.", "label": "Enable", "name": "enable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: DataplanPayload | None = ...,
        name: str | None = ...,
        modem_id: Literal[{"description": "Modem one", "help": "Modem one.", "label": "Modem1", "name": "modem1"}, {"description": "Modem two", "help": "Modem two.", "label": "Modem2", "name": "modem2"}, {"description": "All modems", "help": "All modems.", "label": "All", "name": "all"}] | None = ...,
        type: Literal[{"description": "Assign by SIM carrier", "help": "Assign by SIM carrier.", "label": "Carrier", "name": "carrier"}, {"description": "Assign to SIM slot 1 or 2", "help": "Assign to SIM slot 1 or 2.", "label": "Slot", "name": "slot"}, {"description": "Assign to a specific SIM by ICCID", "help": "Assign to a specific SIM by ICCID.", "label": "Iccid", "name": "iccid"}, {"description": "Compatible with any SIM", "help": "Compatible with any SIM. Assigned if no other dataplan matches the chosen SIM.", "label": "Generic", "name": "generic"}] | None = ...,
        slot: Literal[{"description": "Sim slot one", "help": "Sim slot one.", "label": "Sim1", "name": "sim1"}, {"description": "Sim slot two", "help": "Sim slot two.", "label": "Sim2", "name": "sim2"}] | None = ...,
        iccid: str | None = ...,
        carrier: str | None = ...,
        apn: str | None = ...,
        auth_type: Literal[{"description": "No authentication", "help": "No authentication.", "label": "None", "name": "none"}, {"description": "PAP", "help": "PAP.", "label": "Pap", "name": "pap"}, {"description": "CHAP", "help": "CHAP.", "label": "Chap", "name": "chap"}] | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        pdn: Literal[{"description": "IPv4 only PDN activation", "help": "IPv4 only PDN activation.", "label": "Ipv4 Only", "name": "ipv4-only"}, {"description": "IPv6 only PDN activation", "help": "IPv6 only PDN activation.", "label": "Ipv6 Only", "name": "ipv6-only"}, {"description": "Both IPv4 and IPv6 PDN activations", "help": "Both IPv4 and IPv6 PDN activations.", "label": "Ipv4 Ipv6", "name": "ipv4-ipv6"}] | None = ...,
        signal_threshold: int | None = ...,
        signal_period: int | None = ...,
        capacity: int | None = ...,
        monthly_fee: int | None = ...,
        billing_date: int | None = ...,
        overage: Literal[{"description": "Disable dataplan overage detection", "help": "Disable dataplan overage detection.", "label": "Disable", "name": "disable"}, {"description": "Enable dataplan overage detection", "help": "Enable dataplan overage detection.", "label": "Enable", "name": "enable"}] | None = ...,
        preferred_subnet: int | None = ...,
        private_network: Literal[{"description": "Disable dataplan private network support", "help": "Disable dataplan private network support.", "label": "Disable", "name": "disable"}, {"description": "Enable dataplan private network support", "help": "Enable dataplan private network support.", "label": "Enable", "name": "enable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        name: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        name: str,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: DataplanPayload | None = ...,
        vdom: str | bool | None = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    # Helper methods
    @staticmethod
    def help(field_name: str | None = ...) -> str: ...
    
    @staticmethod
    def fields(detailed: bool = ...) -> Union[list[str], list[dict[str, Any]]]: ...
    
    @staticmethod
    def field_info(field_name: str) -> dict[str, Any]: ...
    
    @staticmethod
    def validate_field(name: str, value: Any) -> bool: ...
    
    @staticmethod
    def required_fields() -> list[str]: ...
    
    @staticmethod
    def defaults() -> dict[str, Any]: ...
    
    @staticmethod
    def schema() -> dict[str, Any]: ...


__all__ = [
    "Dataplan",
    "DataplanPayload",
]