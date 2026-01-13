from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class CloudServicePayload(TypedDict, total=False):
    """
    Type hints for system/cloud_service payload fields.
    
    Configure system cloud service.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.vdom.VdomEndpoint` (via: traffic-vdom)

    **Usage:**
        payload: CloudServicePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Name.
    vendor: NotRequired[Literal[{"description": "Unknown type of cloud service vendor", "help": "Unknown type of cloud service vendor.", "label": "Unknown", "name": "unknown"}, {"description": "Google Cloud KMS service", "help": "Google Cloud KMS service.", "label": "Google Cloud Kms", "name": "google-cloud-kms"}]]  # Cloud service vendor.
    traffic_vdom: NotRequired[str]  # Vdom used to communicate with cloud service.
    gck_service_account: NotRequired[str]  # Service account (e.g. "account-id@sampledomain.com").
    gck_private_key: NotRequired[str]  # Service account private key in PEM format (e.g. "-----BEGIN 
    gck_keyid: NotRequired[str]  # Key id, also referred as "kid".
    gck_access_token_lifetime: NotRequired[int]  # Lifetime of automatically generated access tokens in minutes


class CloudService:
    """
    Configure system cloud service.
    
    Path: system/cloud_service
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
        payload_dict: CloudServicePayload | None = ...,
        name: str | None = ...,
        vendor: Literal[{"description": "Unknown type of cloud service vendor", "help": "Unknown type of cloud service vendor.", "label": "Unknown", "name": "unknown"}, {"description": "Google Cloud KMS service", "help": "Google Cloud KMS service.", "label": "Google Cloud Kms", "name": "google-cloud-kms"}] | None = ...,
        traffic_vdom: str | None = ...,
        gck_service_account: str | None = ...,
        gck_private_key: str | None = ...,
        gck_keyid: str | None = ...,
        gck_access_token_lifetime: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: CloudServicePayload | None = ...,
        name: str | None = ...,
        vendor: Literal[{"description": "Unknown type of cloud service vendor", "help": "Unknown type of cloud service vendor.", "label": "Unknown", "name": "unknown"}, {"description": "Google Cloud KMS service", "help": "Google Cloud KMS service.", "label": "Google Cloud Kms", "name": "google-cloud-kms"}] | None = ...,
        traffic_vdom: str | None = ...,
        gck_service_account: str | None = ...,
        gck_private_key: str | None = ...,
        gck_keyid: str | None = ...,
        gck_access_token_lifetime: int | None = ...,
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
        payload_dict: CloudServicePayload | None = ...,
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
    "CloudService",
    "CloudServicePayload",
]