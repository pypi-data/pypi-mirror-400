from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class H2qpOsuProviderPayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/hotspot20/h2qp_osu_provider payload fields.
    
    Configure online sign up (OSU) provider list.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.wireless-controller.hotspot20.icon.IconEndpoint` (via: icon)

    **Usage:**
        payload: H2qpOsuProviderPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # OSU provider ID.
    friendly_name: NotRequired[list[dict[str, Any]]]  # OSU provider friendly name.
    server_uri: NotRequired[str]  # Server URI.
    osu_method: NotRequired[Literal[{"description": "OMA DM", "help": "OMA DM.", "label": "Oma Dm", "name": "oma-dm"}, {"description": "SOAP XML SPP", "help": "SOAP XML SPP.", "label": "Soap Xml Spp", "name": "soap-xml-spp"}, {"description": "Reserved", "help": "Reserved.", "label": "Reserved", "name": "reserved"}]]  # OSU method list.
    osu_nai: NotRequired[str]  # OSU NAI.
    service_description: NotRequired[list[dict[str, Any]]]  # OSU service name.
    icon: NotRequired[str]  # OSU provider icon.


class H2qpOsuProvider:
    """
    Configure online sign up (OSU) provider list.
    
    Path: wireless_controller/hotspot20/h2qp_osu_provider
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
        payload_dict: H2qpOsuProviderPayload | None = ...,
        name: str | None = ...,
        friendly_name: list[dict[str, Any]] | None = ...,
        server_uri: str | None = ...,
        osu_method: Literal[{"description": "OMA DM", "help": "OMA DM.", "label": "Oma Dm", "name": "oma-dm"}, {"description": "SOAP XML SPP", "help": "SOAP XML SPP.", "label": "Soap Xml Spp", "name": "soap-xml-spp"}, {"description": "Reserved", "help": "Reserved.", "label": "Reserved", "name": "reserved"}] | None = ...,
        osu_nai: str | None = ...,
        service_description: list[dict[str, Any]] | None = ...,
        icon: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: H2qpOsuProviderPayload | None = ...,
        name: str | None = ...,
        friendly_name: list[dict[str, Any]] | None = ...,
        server_uri: str | None = ...,
        osu_method: Literal[{"description": "OMA DM", "help": "OMA DM.", "label": "Oma Dm", "name": "oma-dm"}, {"description": "SOAP XML SPP", "help": "SOAP XML SPP.", "label": "Soap Xml Spp", "name": "soap-xml-spp"}, {"description": "Reserved", "help": "Reserved.", "label": "Reserved", "name": "reserved"}] | None = ...,
        osu_nai: str | None = ...,
        service_description: list[dict[str, Any]] | None = ...,
        icon: str | None = ...,
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
        payload_dict: H2qpOsuProviderPayload | None = ...,
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
    "H2qpOsuProvider",
    "H2qpOsuProviderPayload",
]