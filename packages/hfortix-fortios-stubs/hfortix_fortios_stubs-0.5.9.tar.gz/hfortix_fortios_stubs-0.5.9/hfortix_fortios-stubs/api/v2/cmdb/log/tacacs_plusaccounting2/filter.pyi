from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class FilterPayload(TypedDict, total=False):
    """
    Type hints for log/tacacs_plusaccounting2/filter payload fields.
    
    Settings for TACACS+ accounting events filter.
    
    **Usage:**
        payload: FilterPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    login_audit: NotRequired[Literal[{"description": "Enable TACACS+ accounting for login events audit", "help": "Enable TACACS+ accounting for login events audit.", "label": "Enable", "name": "enable"}, {"description": "Disable TACACS+ accounting for login events audit", "help": "Disable TACACS+ accounting for login events audit.", "label": "Disable", "name": "disable"}]]  # Enable/disable TACACS+ accounting for login events audit.
    config_change_audit: NotRequired[Literal[{"description": "Enable TACACS+ accounting for configuration change events audit", "help": "Enable TACACS+ accounting for configuration change events audit.", "label": "Enable", "name": "enable"}, {"description": "Disable TACACS+ accounting for configuration change events audit", "help": "Disable TACACS+ accounting for configuration change events audit.", "label": "Disable", "name": "disable"}]]  # Enable/disable TACACS+ accounting for configuration change e
    cli_cmd_audit: NotRequired[Literal[{"description": "Enable TACACS+ accounting for CLI commands audit", "help": "Enable TACACS+ accounting for CLI commands audit.", "label": "Enable", "name": "enable"}, {"description": "Disable TACACS+ accounting for CLI commands audit", "help": "Disable TACACS+ accounting for CLI commands audit.", "label": "Disable", "name": "disable"}]]  # Enable/disable TACACS+ accounting for CLI commands audit.


class Filter:
    """
    Settings for TACACS+ accounting events filter.
    
    Path: log/tacacs_plusaccounting2/filter
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
        payload_dict: FilterPayload | None = ...,
        login_audit: Literal[{"description": "Enable TACACS+ accounting for login events audit", "help": "Enable TACACS+ accounting for login events audit.", "label": "Enable", "name": "enable"}, {"description": "Disable TACACS+ accounting for login events audit", "help": "Disable TACACS+ accounting for login events audit.", "label": "Disable", "name": "disable"}] | None = ...,
        config_change_audit: Literal[{"description": "Enable TACACS+ accounting for configuration change events audit", "help": "Enable TACACS+ accounting for configuration change events audit.", "label": "Enable", "name": "enable"}, {"description": "Disable TACACS+ accounting for configuration change events audit", "help": "Disable TACACS+ accounting for configuration change events audit.", "label": "Disable", "name": "disable"}] | None = ...,
        cli_cmd_audit: Literal[{"description": "Enable TACACS+ accounting for CLI commands audit", "help": "Enable TACACS+ accounting for CLI commands audit.", "label": "Enable", "name": "enable"}, {"description": "Disable TACACS+ accounting for CLI commands audit", "help": "Disable TACACS+ accounting for CLI commands audit.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: FilterPayload | None = ...,
        login_audit: Literal[{"description": "Enable TACACS+ accounting for login events audit", "help": "Enable TACACS+ accounting for login events audit.", "label": "Enable", "name": "enable"}, {"description": "Disable TACACS+ accounting for login events audit", "help": "Disable TACACS+ accounting for login events audit.", "label": "Disable", "name": "disable"}] | None = ...,
        config_change_audit: Literal[{"description": "Enable TACACS+ accounting for configuration change events audit", "help": "Enable TACACS+ accounting for configuration change events audit.", "label": "Enable", "name": "enable"}, {"description": "Disable TACACS+ accounting for configuration change events audit", "help": "Disable TACACS+ accounting for configuration change events audit.", "label": "Disable", "name": "disable"}] | None = ...,
        cli_cmd_audit: Literal[{"description": "Enable TACACS+ accounting for CLI commands audit", "help": "Enable TACACS+ accounting for CLI commands audit.", "label": "Enable", "name": "enable"}, {"description": "Disable TACACS+ accounting for CLI commands audit", "help": "Disable TACACS+ accounting for CLI commands audit.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: FilterPayload | None = ...,
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
    "Filter",
    "FilterPayload",
]