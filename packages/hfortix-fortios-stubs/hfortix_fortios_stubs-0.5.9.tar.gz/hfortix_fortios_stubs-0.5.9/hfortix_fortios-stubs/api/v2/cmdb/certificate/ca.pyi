from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class CaPayload(TypedDict, total=False):
    """
    Type hints for certificate/ca payload fields.
    
    CA certificate.
    
    **Usage:**
        payload: CaPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Name.
    ca: str  # CA certificate as a PEM file.
    range: NotRequired[Literal[{"description": "Global range", "help": "Global range.", "label": "Global", "name": "global"}, {"description": "VDOM IP address range", "help": "VDOM IP address range.", "label": "Vdom", "name": "vdom"}]]  # Either global or VDOM IP address range for the CA certificat
    source: NotRequired[Literal[{"description": "Factory installed certificate", "help": "Factory installed certificate.", "label": "Factory", "name": "factory"}, {"description": "User generated certificate", "help": "User generated certificate.", "label": "User", "name": "user"}, {"description": "Bundle file certificate", "help": "Bundle file certificate.", "label": "Bundle", "name": "bundle"}]]  # CA certificate source type.
    ssl_inspection_trusted: NotRequired[Literal[{"description": "Trusted CA for SSL inspection", "help": "Trusted CA for SSL inspection.", "label": "Enable", "name": "enable"}, {"description": "Untrusted CA for SSL inspection", "help": "Untrusted CA for SSL inspection.", "label": "Disable", "name": "disable"}]]  # Enable/disable this CA as a trusted CA for SSL inspection.
    scep_url: NotRequired[str]  # URL of the SCEP server.
    est_url: NotRequired[str]  # URL of the EST server.
    auto_update_days: NotRequired[int]  # Number of days to wait before requesting an updated CA certi
    auto_update_days_warning: NotRequired[int]  # Number of days before an expiry-warning message is generated
    source_ip: NotRequired[str]  # Source IP address for communications to the SCEP server.
    ca_identifier: NotRequired[str]  # CA identifier of the SCEP server.
    obsolete: NotRequired[Literal[{"description": "Alive", "help": "Alive.", "label": "Disable", "name": "disable"}, {"description": "Obsolete", "help": "Obsolete.", "label": "Enable", "name": "enable"}]]  # Enable/disable this CA as obsoleted.
    fabric_ca: NotRequired[Literal[{"description": "Disable synchronization of CA across Security Fabric", "help": "Disable synchronization of CA across Security Fabric.", "label": "Disable", "name": "disable"}, {"description": "Enable synchronization of CA across Security Fabric", "help": "Enable synchronization of CA across Security Fabric.", "label": "Enable", "name": "enable"}]]  # Enable/disable synchronization of CA across Security Fabric.
    details: NotRequired[str]  # Print CA certificate detailed information.


class Ca:
    """
    CA certificate.
    
    Path: certificate/ca
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
        payload_dict: CaPayload | None = ...,
        name: str | None = ...,
        ca: str | None = ...,
        range: Literal[{"description": "Global range", "help": "Global range.", "label": "Global", "name": "global"}, {"description": "VDOM IP address range", "help": "VDOM IP address range.", "label": "Vdom", "name": "vdom"}] | None = ...,
        source: Literal[{"description": "Factory installed certificate", "help": "Factory installed certificate.", "label": "Factory", "name": "factory"}, {"description": "User generated certificate", "help": "User generated certificate.", "label": "User", "name": "user"}, {"description": "Bundle file certificate", "help": "Bundle file certificate.", "label": "Bundle", "name": "bundle"}] | None = ...,
        ssl_inspection_trusted: Literal[{"description": "Trusted CA for SSL inspection", "help": "Trusted CA for SSL inspection.", "label": "Enable", "name": "enable"}, {"description": "Untrusted CA for SSL inspection", "help": "Untrusted CA for SSL inspection.", "label": "Disable", "name": "disable"}] | None = ...,
        scep_url: str | None = ...,
        est_url: str | None = ...,
        auto_update_days: int | None = ...,
        auto_update_days_warning: int | None = ...,
        source_ip: str | None = ...,
        ca_identifier: str | None = ...,
        obsolete: Literal[{"description": "Alive", "help": "Alive.", "label": "Disable", "name": "disable"}, {"description": "Obsolete", "help": "Obsolete.", "label": "Enable", "name": "enable"}] | None = ...,
        fabric_ca: Literal[{"description": "Disable synchronization of CA across Security Fabric", "help": "Disable synchronization of CA across Security Fabric.", "label": "Disable", "name": "disable"}, {"description": "Enable synchronization of CA across Security Fabric", "help": "Enable synchronization of CA across Security Fabric.", "label": "Enable", "name": "enable"}] | None = ...,
        details: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: CaPayload | None = ...,
        name: str | None = ...,
        ca: str | None = ...,
        range: Literal[{"description": "Global range", "help": "Global range.", "label": "Global", "name": "global"}, {"description": "VDOM IP address range", "help": "VDOM IP address range.", "label": "Vdom", "name": "vdom"}] | None = ...,
        source: Literal[{"description": "Factory installed certificate", "help": "Factory installed certificate.", "label": "Factory", "name": "factory"}, {"description": "User generated certificate", "help": "User generated certificate.", "label": "User", "name": "user"}, {"description": "Bundle file certificate", "help": "Bundle file certificate.", "label": "Bundle", "name": "bundle"}] | None = ...,
        ssl_inspection_trusted: Literal[{"description": "Trusted CA for SSL inspection", "help": "Trusted CA for SSL inspection.", "label": "Enable", "name": "enable"}, {"description": "Untrusted CA for SSL inspection", "help": "Untrusted CA for SSL inspection.", "label": "Disable", "name": "disable"}] | None = ...,
        scep_url: str | None = ...,
        est_url: str | None = ...,
        auto_update_days: int | None = ...,
        auto_update_days_warning: int | None = ...,
        source_ip: str | None = ...,
        ca_identifier: str | None = ...,
        obsolete: Literal[{"description": "Alive", "help": "Alive.", "label": "Disable", "name": "disable"}, {"description": "Obsolete", "help": "Obsolete.", "label": "Enable", "name": "enable"}] | None = ...,
        fabric_ca: Literal[{"description": "Disable synchronization of CA across Security Fabric", "help": "Disable synchronization of CA across Security Fabric.", "label": "Disable", "name": "disable"}, {"description": "Enable synchronization of CA across Security Fabric", "help": "Enable synchronization of CA across Security Fabric.", "label": "Enable", "name": "enable"}] | None = ...,
        details: str | None = ...,
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
        payload_dict: CaPayload | None = ...,
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
    "Ca",
    "CaPayload",
]