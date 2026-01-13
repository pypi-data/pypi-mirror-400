from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ScimPayload(TypedDict, total=False):
    """
    Type hints for user/scim payload fields.
    
    Configure SCIM client entries.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.ca.CaEndpoint` (via: certificate)
        - :class:`~.certificate.remote.RemoteEndpoint` (via: certificate)
        - :class:`~.vpn.certificate.ca.CaEndpoint` (via: certificate)
        - :class:`~.vpn.certificate.local.LocalEndpoint` (via: token-certificate)
        - :class:`~.vpn.certificate.remote.RemoteEndpoint` (via: certificate, token-certificate)

    **Usage:**
        payload: ScimPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # SCIM client name.
    id: NotRequired[int]  # SCIM client ID.
    status: Literal[{"description": "Enable System for Cross-domain Identity Management (SCIM)", "help": "Enable System for Cross-domain Identity Management (SCIM).", "label": "Enable", "name": "enable"}, {"description": "Disable System for Cross-domain Identity Management (SCIM)", "help": "Disable System for Cross-domain Identity Management (SCIM).", "label": "Disable", "name": "disable"}]  # Enable/disable System for Cross-domain Identity Management (
    base_url: NotRequired[str]  # Server URL to receive SCIM create, read, update, delete (CRU
    auth_method: NotRequired[Literal[{"description": "Bearer token", "help": "Bearer token.", "label": "Token", "name": "token"}, {"description": "Base", "help": "Base.", "label": "Base", "name": "base"}]]  # TLS client authentication methods (default = bearer token).
    token_certificate: NotRequired[str]  # Certificate for token verification.
    secret: NotRequired[str]  # Secret for token verification or base authentication.
    certificate: NotRequired[str]  # Certificate for client verification during TLS handshake.
    client_identity_check: NotRequired[Literal[{"description": "Enable client identity check", "help": "Enable client identity check.", "label": "Enable", "name": "enable"}, {"description": "Disable client identity check", "help": "Disable client identity check.", "label": "Disable", "name": "disable"}]]  # Enable/disable client identity check.
    cascade: NotRequired[Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}]]  # Enable/disable to follow SCIM users/groups changes in IDP.


class Scim:
    """
    Configure SCIM client entries.
    
    Path: user/scim
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
        payload_dict: ScimPayload | None = ...,
        name: str | None = ...,
        id: int | None = ...,
        status: Literal[{"description": "Enable System for Cross-domain Identity Management (SCIM)", "help": "Enable System for Cross-domain Identity Management (SCIM).", "label": "Enable", "name": "enable"}, {"description": "Disable System for Cross-domain Identity Management (SCIM)", "help": "Disable System for Cross-domain Identity Management (SCIM).", "label": "Disable", "name": "disable"}] | None = ...,
        base_url: str | None = ...,
        auth_method: Literal[{"description": "Bearer token", "help": "Bearer token.", "label": "Token", "name": "token"}, {"description": "Base", "help": "Base.", "label": "Base", "name": "base"}] | None = ...,
        token_certificate: str | None = ...,
        secret: str | None = ...,
        certificate: str | None = ...,
        client_identity_check: Literal[{"description": "Enable client identity check", "help": "Enable client identity check.", "label": "Enable", "name": "enable"}, {"description": "Disable client identity check", "help": "Disable client identity check.", "label": "Disable", "name": "disable"}] | None = ...,
        cascade: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ScimPayload | None = ...,
        name: str | None = ...,
        id: int | None = ...,
        status: Literal[{"description": "Enable System for Cross-domain Identity Management (SCIM)", "help": "Enable System for Cross-domain Identity Management (SCIM).", "label": "Enable", "name": "enable"}, {"description": "Disable System for Cross-domain Identity Management (SCIM)", "help": "Disable System for Cross-domain Identity Management (SCIM).", "label": "Disable", "name": "disable"}] | None = ...,
        base_url: str | None = ...,
        auth_method: Literal[{"description": "Bearer token", "help": "Bearer token.", "label": "Token", "name": "token"}, {"description": "Base", "help": "Base.", "label": "Base", "name": "base"}] | None = ...,
        token_certificate: str | None = ...,
        secret: str | None = ...,
        certificate: str | None = ...,
        client_identity_check: Literal[{"description": "Enable client identity check", "help": "Enable client identity check.", "label": "Enable", "name": "enable"}, {"description": "Disable client identity check", "help": "Disable client identity check.", "label": "Disable", "name": "disable"}] | None = ...,
        cascade: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}] | None = ...,
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
        payload_dict: ScimPayload | None = ...,
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
    "Scim",
    "ScimPayload",
]