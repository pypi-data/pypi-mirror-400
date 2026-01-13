from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SamlPayload(TypedDict, total=False):
    """
    Type hints for system/saml payload fields.
    
    Global settings for SAML authentication.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.local.LocalEndpoint` (via: cert)
        - :class:`~.certificate.remote.RemoteEndpoint` (via: idp-cert)
        - :class:`~.system.accprofile.AccprofileEndpoint` (via: default-profile)

    **Usage:**
        payload: SamlPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: NotRequired[Literal[{"description": "Enable SAML authentication", "help": "Enable SAML authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable SAML authentication", "help": "Disable SAML authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable SAML authentication (default = disable).
    role: NotRequired[Literal[{"description": "Identity Provider", "help": "Identity Provider.", "label": "Identity Provider", "name": "identity-provider"}, {"description": "Service Provider", "help": "Service Provider.", "label": "Service Provider", "name": "service-provider"}]]  # SAML role.
    default_login_page: Literal[{"description": "Use local login page as default", "help": "Use local login page as default.", "label": "Normal", "name": "normal"}, {"description": "Use IdP\u0027s Single Sign-On page as default", "help": "Use IdP\u0027s Single Sign-On page as default.", "label": "Sso", "name": "sso"}]  # Choose default login page.
    default_profile: str  # Default profile for new SSO admin.
    cert: NotRequired[str]  # Certificate to sign SAML messages.
    binding_protocol: NotRequired[Literal[{"description": "HTTP POST binding", "help": "HTTP POST binding.", "label": "Post", "name": "post"}, {"description": "HTTP Redirect binding", "help": "HTTP Redirect binding.", "label": "Redirect", "name": "redirect"}]]  # IdP Binding protocol.
    portal_url: NotRequired[str]  # SP portal URL.
    entity_id: str  # SP entity ID.
    single_sign_on_url: NotRequired[str]  # SP single sign-on URL.
    single_logout_url: NotRequired[str]  # SP single logout URL.
    idp_entity_id: NotRequired[str]  # IDP entity ID.
    idp_single_sign_on_url: NotRequired[str]  # IDP single sign-on URL.
    idp_single_logout_url: NotRequired[str]  # IDP single logout URL.
    idp_cert: str  # IDP certificate name.
    server_address: str  # Server address.
    require_signed_resp_and_asrt: NotRequired[Literal[{"description": "Both response and assertion must be signed and valid", "help": "Both response and assertion must be signed and valid.", "label": "Enable", "name": "enable"}, {"description": "At least one of response or assertion must be signed and valid", "help": "At least one of response or assertion must be signed and valid.", "label": "Disable", "name": "disable"}]]  # Require both response and assertion from IDP to be signed wh
    tolerance: NotRequired[int]  # Tolerance to the range of time when the assertion is valid (
    life: NotRequired[int]  # Length of the range of time when the assertion is valid (in 
    service_providers: NotRequired[list[dict[str, Any]]]  # Authorized service providers.


class Saml:
    """
    Global settings for SAML authentication.
    
    Path: system/saml
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
        payload_dict: SamlPayload | None = ...,
        status: Literal[{"description": "Enable SAML authentication", "help": "Enable SAML authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable SAML authentication", "help": "Disable SAML authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        role: Literal[{"description": "Identity Provider", "help": "Identity Provider.", "label": "Identity Provider", "name": "identity-provider"}, {"description": "Service Provider", "help": "Service Provider.", "label": "Service Provider", "name": "service-provider"}] | None = ...,
        default_login_page: Literal[{"description": "Use local login page as default", "help": "Use local login page as default.", "label": "Normal", "name": "normal"}, {"description": "Use IdP\u0027s Single Sign-On page as default", "help": "Use IdP\u0027s Single Sign-On page as default.", "label": "Sso", "name": "sso"}] | None = ...,
        default_profile: str | None = ...,
        cert: str | None = ...,
        binding_protocol: Literal[{"description": "HTTP POST binding", "help": "HTTP POST binding.", "label": "Post", "name": "post"}, {"description": "HTTP Redirect binding", "help": "HTTP Redirect binding.", "label": "Redirect", "name": "redirect"}] | None = ...,
        portal_url: str | None = ...,
        entity_id: str | None = ...,
        single_sign_on_url: str | None = ...,
        single_logout_url: str | None = ...,
        idp_entity_id: str | None = ...,
        idp_single_sign_on_url: str | None = ...,
        idp_single_logout_url: str | None = ...,
        idp_cert: str | None = ...,
        server_address: str | None = ...,
        require_signed_resp_and_asrt: Literal[{"description": "Both response and assertion must be signed and valid", "help": "Both response and assertion must be signed and valid.", "label": "Enable", "name": "enable"}, {"description": "At least one of response or assertion must be signed and valid", "help": "At least one of response or assertion must be signed and valid.", "label": "Disable", "name": "disable"}] | None = ...,
        tolerance: int | None = ...,
        life: int | None = ...,
        service_providers: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SamlPayload | None = ...,
        status: Literal[{"description": "Enable SAML authentication", "help": "Enable SAML authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable SAML authentication", "help": "Disable SAML authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        role: Literal[{"description": "Identity Provider", "help": "Identity Provider.", "label": "Identity Provider", "name": "identity-provider"}, {"description": "Service Provider", "help": "Service Provider.", "label": "Service Provider", "name": "service-provider"}] | None = ...,
        default_login_page: Literal[{"description": "Use local login page as default", "help": "Use local login page as default.", "label": "Normal", "name": "normal"}, {"description": "Use IdP\u0027s Single Sign-On page as default", "help": "Use IdP\u0027s Single Sign-On page as default.", "label": "Sso", "name": "sso"}] | None = ...,
        default_profile: str | None = ...,
        cert: str | None = ...,
        binding_protocol: Literal[{"description": "HTTP POST binding", "help": "HTTP POST binding.", "label": "Post", "name": "post"}, {"description": "HTTP Redirect binding", "help": "HTTP Redirect binding.", "label": "Redirect", "name": "redirect"}] | None = ...,
        portal_url: str | None = ...,
        entity_id: str | None = ...,
        single_sign_on_url: str | None = ...,
        single_logout_url: str | None = ...,
        idp_entity_id: str | None = ...,
        idp_single_sign_on_url: str | None = ...,
        idp_single_logout_url: str | None = ...,
        idp_cert: str | None = ...,
        server_address: str | None = ...,
        require_signed_resp_and_asrt: Literal[{"description": "Both response and assertion must be signed and valid", "help": "Both response and assertion must be signed and valid.", "label": "Enable", "name": "enable"}, {"description": "At least one of response or assertion must be signed and valid", "help": "At least one of response or assertion must be signed and valid.", "label": "Disable", "name": "disable"}] | None = ...,
        tolerance: int | None = ...,
        life: int | None = ...,
        service_providers: list[dict[str, Any]] | None = ...,
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
        payload_dict: SamlPayload | None = ...,
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
    "Saml",
    "SamlPayload",
]