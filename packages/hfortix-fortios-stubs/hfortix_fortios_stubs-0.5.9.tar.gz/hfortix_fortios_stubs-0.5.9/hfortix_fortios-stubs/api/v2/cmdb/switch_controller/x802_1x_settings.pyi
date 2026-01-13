from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class X8021xSettingsPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/x802_1x_settings payload fields.
    
    Configure global 802.1X settings.
    
    **Usage:**
        payload: X8021xSettingsPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    link_down_auth: NotRequired[Literal[{"description": "Interface set to unauth when down", "help": "Interface set to unauth when down. Reauthentication is needed.", "label": "Set Unauth", "name": "set-unauth"}, {"description": "Interface reauthentication is not needed", "help": "Interface reauthentication is not needed.", "label": "No Action", "name": "no-action"}]]  # Interface-reauthentication state to set if a link is down.
    reauth_period: NotRequired[int]  # Period of time to allow for reauthentication (1 - 1440 sec, 
    max_reauth_attempt: NotRequired[int]  # Maximum number of authentication attempts (0 - 15, default =
    tx_period: NotRequired[int]  # 802.1X Tx period (seconds, default=30).
    mab_reauth: NotRequired[Literal[{"description": "Disable MAB re-authentication", "help": "Disable MAB re-authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable MAB re-authentication", "help": "Enable MAB re-authentication.", "label": "Enable", "name": "enable"}]]  # Enable/disable MAB re-authentication.
    mac_username_delimiter: NotRequired[Literal[{"description": "Use colon as delimiter for MAC auth username", "help": "Use colon as delimiter for MAC auth username.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for MAC auth username", "help": "Use hyphen as delimiter for MAC auth username.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for MAC auth username", "help": "No delimiter for MAC auth username.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for MAC auth username", "help": "Use single hyphen as delimiter for MAC auth username.", "label": "Single Hyphen", "name": "single-hyphen"}]]  # MAC authentication username delimiter (default = hyphen).
    mac_password_delimiter: NotRequired[Literal[{"description": "Use colon as delimiter for MAC auth password", "help": "Use colon as delimiter for MAC auth password.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for MAC auth password", "help": "Use hyphen as delimiter for MAC auth password.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for MAC auth password", "help": "No delimiter for MAC auth password.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for MAC auth password", "help": "Use single hyphen as delimiter for MAC auth password.", "label": "Single Hyphen", "name": "single-hyphen"}]]  # MAC authentication password delimiter (default = hyphen).
    mac_calling_station_delimiter: NotRequired[Literal[{"description": "Use colon as delimiter for calling station", "help": "Use colon as delimiter for calling station.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for calling station", "help": "Use hyphen as delimiter for calling station.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for calling station", "help": "No delimiter for calling station.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for calling station", "help": "Use single hyphen as delimiter for calling station.", "label": "Single Hyphen", "name": "single-hyphen"}]]  # MAC calling station delimiter (default = hyphen).
    mac_called_station_delimiter: NotRequired[Literal[{"description": "Use colon as delimiter for called station", "help": "Use colon as delimiter for called station.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for called station", "help": "Use hyphen as delimiter for called station.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for called station", "help": "No delimiter for called station.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for called station", "help": "Use single hyphen as delimiter for called station.", "label": "Single Hyphen", "name": "single-hyphen"}]]  # MAC called station delimiter (default = hyphen).
    mac_case: NotRequired[Literal[{"description": "Use lowercase MAC", "help": "Use lowercase MAC.", "label": "Lowercase", "name": "lowercase"}, {"description": "Use uppercase MAC", "help": "Use uppercase MAC.", "label": "Uppercase", "name": "uppercase"}]]  # MAC case (default = lowercase).


class X8021xSettings:
    """
    Configure global 802.1X settings.
    
    Path: switch_controller/x802_1x_settings
    Category: cmdb
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
        payload_dict: X8021xSettingsPayload | None = ...,
        link_down_auth: Literal[{"description": "Interface set to unauth when down", "help": "Interface set to unauth when down. Reauthentication is needed.", "label": "Set Unauth", "name": "set-unauth"}, {"description": "Interface reauthentication is not needed", "help": "Interface reauthentication is not needed.", "label": "No Action", "name": "no-action"}] | None = ...,
        reauth_period: int | None = ...,
        max_reauth_attempt: int | None = ...,
        tx_period: int | None = ...,
        mab_reauth: Literal[{"description": "Disable MAB re-authentication", "help": "Disable MAB re-authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable MAB re-authentication", "help": "Enable MAB re-authentication.", "label": "Enable", "name": "enable"}] | None = ...,
        mac_username_delimiter: Literal[{"description": "Use colon as delimiter for MAC auth username", "help": "Use colon as delimiter for MAC auth username.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for MAC auth username", "help": "Use hyphen as delimiter for MAC auth username.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for MAC auth username", "help": "No delimiter for MAC auth username.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for MAC auth username", "help": "Use single hyphen as delimiter for MAC auth username.", "label": "Single Hyphen", "name": "single-hyphen"}] | None = ...,
        mac_password_delimiter: Literal[{"description": "Use colon as delimiter for MAC auth password", "help": "Use colon as delimiter for MAC auth password.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for MAC auth password", "help": "Use hyphen as delimiter for MAC auth password.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for MAC auth password", "help": "No delimiter for MAC auth password.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for MAC auth password", "help": "Use single hyphen as delimiter for MAC auth password.", "label": "Single Hyphen", "name": "single-hyphen"}] | None = ...,
        mac_calling_station_delimiter: Literal[{"description": "Use colon as delimiter for calling station", "help": "Use colon as delimiter for calling station.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for calling station", "help": "Use hyphen as delimiter for calling station.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for calling station", "help": "No delimiter for calling station.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for calling station", "help": "Use single hyphen as delimiter for calling station.", "label": "Single Hyphen", "name": "single-hyphen"}] | None = ...,
        mac_called_station_delimiter: Literal[{"description": "Use colon as delimiter for called station", "help": "Use colon as delimiter for called station.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for called station", "help": "Use hyphen as delimiter for called station.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for called station", "help": "No delimiter for called station.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for called station", "help": "Use single hyphen as delimiter for called station.", "label": "Single Hyphen", "name": "single-hyphen"}] | None = ...,
        mac_case: Literal[{"description": "Use lowercase MAC", "help": "Use lowercase MAC.", "label": "Lowercase", "name": "lowercase"}, {"description": "Use uppercase MAC", "help": "Use uppercase MAC.", "label": "Uppercase", "name": "uppercase"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: X8021xSettingsPayload | None = ...,
        link_down_auth: Literal[{"description": "Interface set to unauth when down", "help": "Interface set to unauth when down. Reauthentication is needed.", "label": "Set Unauth", "name": "set-unauth"}, {"description": "Interface reauthentication is not needed", "help": "Interface reauthentication is not needed.", "label": "No Action", "name": "no-action"}] | None = ...,
        reauth_period: int | None = ...,
        max_reauth_attempt: int | None = ...,
        tx_period: int | None = ...,
        mab_reauth: Literal[{"description": "Disable MAB re-authentication", "help": "Disable MAB re-authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable MAB re-authentication", "help": "Enable MAB re-authentication.", "label": "Enable", "name": "enable"}] | None = ...,
        mac_username_delimiter: Literal[{"description": "Use colon as delimiter for MAC auth username", "help": "Use colon as delimiter for MAC auth username.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for MAC auth username", "help": "Use hyphen as delimiter for MAC auth username.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for MAC auth username", "help": "No delimiter for MAC auth username.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for MAC auth username", "help": "Use single hyphen as delimiter for MAC auth username.", "label": "Single Hyphen", "name": "single-hyphen"}] | None = ...,
        mac_password_delimiter: Literal[{"description": "Use colon as delimiter for MAC auth password", "help": "Use colon as delimiter for MAC auth password.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for MAC auth password", "help": "Use hyphen as delimiter for MAC auth password.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for MAC auth password", "help": "No delimiter for MAC auth password.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for MAC auth password", "help": "Use single hyphen as delimiter for MAC auth password.", "label": "Single Hyphen", "name": "single-hyphen"}] | None = ...,
        mac_calling_station_delimiter: Literal[{"description": "Use colon as delimiter for calling station", "help": "Use colon as delimiter for calling station.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for calling station", "help": "Use hyphen as delimiter for calling station.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for calling station", "help": "No delimiter for calling station.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for calling station", "help": "Use single hyphen as delimiter for calling station.", "label": "Single Hyphen", "name": "single-hyphen"}] | None = ...,
        mac_called_station_delimiter: Literal[{"description": "Use colon as delimiter for called station", "help": "Use colon as delimiter for called station.", "label": "Colon", "name": "colon"}, {"description": "Use hyphen as delimiter for called station", "help": "Use hyphen as delimiter for called station.", "label": "Hyphen", "name": "hyphen"}, {"description": "No delimiter for called station", "help": "No delimiter for called station.", "label": "None", "name": "none"}, {"description": "Use single hyphen as delimiter for called station", "help": "Use single hyphen as delimiter for called station.", "label": "Single Hyphen", "name": "single-hyphen"}] | None = ...,
        mac_case: Literal[{"description": "Use lowercase MAC", "help": "Use lowercase MAC.", "label": "Lowercase", "name": "lowercase"}, {"description": "Use uppercase MAC", "help": "Use uppercase MAC.", "label": "Uppercase", "name": "uppercase"}] | None = ...,
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
        payload_dict: X8021xSettingsPayload | None = ...,
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
    "X8021xSettings",
    "X8021xSettingsPayload",
]