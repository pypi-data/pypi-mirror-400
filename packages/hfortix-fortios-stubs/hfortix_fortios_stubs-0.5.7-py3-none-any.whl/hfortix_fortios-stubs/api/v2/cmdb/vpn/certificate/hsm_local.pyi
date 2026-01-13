from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class HsmLocalPayload(TypedDict, total=False):
    """
    Type hints for vpn/certificate/hsm_local payload fields.
    
    Local certificates whose keys are stored on HSM.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.cloud-service.CloudServiceEndpoint` (via: gch-cloud-service-name)

    **Usage:**
        payload: HsmLocalPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Name.
    comments: NotRequired[str]  # Comment.
    vendor: Literal[{"description": "Unknown type of HSM", "help": "Unknown type of HSM.", "label": "Unknown", "name": "unknown"}, {"description": "Google Cloud HSM", "help": "Google Cloud HSM.", "label": "Gch", "name": "gch"}]  # HSM vendor.
    api_version: NotRequired[Literal[{"description": "Unknown API version", "help": "Unknown API version.", "label": "Unknown", "name": "unknown"}, {"description": "Google Cloud HSM default API", "help": "Google Cloud HSM default API.", "label": "Gch Default", "name": "gch-default"}]]  # API version for communicating with HSM.
    certificate: NotRequired[str]  # PEM format certificate.
    range: NotRequired[Literal[{"description": "Global range", "help": "Global range.", "label": "Global", "name": "global"}, {"description": "VDOM IP address range", "help": "VDOM IP address range.", "label": "Vdom", "name": "vdom"}]]  # Either a global or VDOM IP address range for the certificate
    source: NotRequired[Literal[{"description": "Factory installed certificate", "help": "Factory installed certificate.", "label": "Factory", "name": "factory"}, {"description": "User generated certificate", "help": "User generated certificate.", "label": "User", "name": "user"}, {"description": "Bundle file certificate", "help": "Bundle file certificate.", "label": "Bundle", "name": "bundle"}]]  # Certificate source type.
    gch_url: NotRequired[str]  # Google Cloud HSM key URL (e.g. "https://cloudkms.googleapis.
    gch_project: NotRequired[str]  # Google Cloud HSM project ID.
    gch_location: NotRequired[str]  # Google Cloud HSM location.
    gch_keyring: NotRequired[str]  # Google Cloud HSM keyring.
    gch_cryptokey: NotRequired[str]  # Google Cloud HSM cryptokey.
    gch_cryptokey_version: NotRequired[str]  # Google Cloud HSM cryptokey version.
    gch_cloud_service_name: NotRequired[str]  # Cloud service config name to generate access token.
    gch_cryptokey_algorithm: NotRequired[Literal[{"description": "2048 bit RSA - PKCS#1 v1", "help": "2048 bit RSA - PKCS#1 v1.5 padding - SHA256 Digest.", "label": "Rsa Sign Pkcs1 2048 Sha256", "name": "rsa-sign-pkcs1-2048-sha256"}, {"description": "3072 bit RSA - PKCS#1 v1", "help": "3072 bit RSA - PKCS#1 v1.5 padding - SHA256 Digest.", "label": "Rsa Sign Pkcs1 3072 Sha256", "name": "rsa-sign-pkcs1-3072-sha256"}, {"description": "4096 bit RSA - PKCS#1 v1", "help": "4096 bit RSA - PKCS#1 v1.5 padding - SHA256 Digest.", "label": "Rsa Sign Pkcs1 4096 Sha256", "name": "rsa-sign-pkcs1-4096-sha256"}, {"description": "4096 bit RSA - PKCS#1 v1", "help": "4096 bit RSA - PKCS#1 v1.5 padding - SHA512 Digest.", "label": "Rsa Sign Pkcs1 4096 Sha512", "name": "rsa-sign-pkcs1-4096-sha512"}, {"description": "2048 bit RSA - PSS padding - SHA256 Digest", "help": "2048 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 2048 Sha256", "name": "rsa-sign-pss-2048-sha256"}, {"description": "3072 bit RSA - PSS padding - SHA256 Digest", "help": "3072 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 3072 Sha256", "name": "rsa-sign-pss-3072-sha256"}, {"description": "4096 bit RSA - PSS padding - SHA256 Digest", "help": "4096 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 4096 Sha256", "name": "rsa-sign-pss-4096-sha256"}, {"description": "4096 bit RSA - PSS padding - SHA256 Digest", "help": "4096 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 4096 Sha512", "name": "rsa-sign-pss-4096-sha512"}, {"description": "Elliptic Curve P-256 - SHA256 Digest", "help": "Elliptic Curve P-256 - SHA256 Digest.", "label": "Ec Sign P256 Sha256", "name": "ec-sign-p256-sha256"}, {"description": "Elliptic Curve P-384 - SHA384 Digest", "help": "Elliptic Curve P-384 - SHA384 Digest.", "label": "Ec Sign P384 Sha384", "name": "ec-sign-p384-sha384"}, {"description": "Elliptic Curvesecp256k1 - SHA256 Digest", "help": "Elliptic Curvesecp256k1 - SHA256 Digest.", "label": "Ec Sign Secp256K1 Sha256", "name": "ec-sign-secp256k1-sha256"}]]  # Google Cloud HSM cryptokey algorithm.
    details: NotRequired[str]  # Print hsm-local certificate detailed information.


class HsmLocal:
    """
    Local certificates whose keys are stored on HSM.
    
    Path: vpn/certificate/hsm_local
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
        payload_dict: HsmLocalPayload | None = ...,
        name: str | None = ...,
        comments: str | None = ...,
        vendor: Literal[{"description": "Unknown type of HSM", "help": "Unknown type of HSM.", "label": "Unknown", "name": "unknown"}, {"description": "Google Cloud HSM", "help": "Google Cloud HSM.", "label": "Gch", "name": "gch"}] | None = ...,
        api_version: Literal[{"description": "Unknown API version", "help": "Unknown API version.", "label": "Unknown", "name": "unknown"}, {"description": "Google Cloud HSM default API", "help": "Google Cloud HSM default API.", "label": "Gch Default", "name": "gch-default"}] | None = ...,
        certificate: str | None = ...,
        range: Literal[{"description": "Global range", "help": "Global range.", "label": "Global", "name": "global"}, {"description": "VDOM IP address range", "help": "VDOM IP address range.", "label": "Vdom", "name": "vdom"}] | None = ...,
        source: Literal[{"description": "Factory installed certificate", "help": "Factory installed certificate.", "label": "Factory", "name": "factory"}, {"description": "User generated certificate", "help": "User generated certificate.", "label": "User", "name": "user"}, {"description": "Bundle file certificate", "help": "Bundle file certificate.", "label": "Bundle", "name": "bundle"}] | None = ...,
        gch_url: str | None = ...,
        gch_project: str | None = ...,
        gch_location: str | None = ...,
        gch_keyring: str | None = ...,
        gch_cryptokey: str | None = ...,
        gch_cryptokey_version: str | None = ...,
        gch_cloud_service_name: str | None = ...,
        gch_cryptokey_algorithm: Literal[{"description": "2048 bit RSA - PKCS#1 v1", "help": "2048 bit RSA - PKCS#1 v1.5 padding - SHA256 Digest.", "label": "Rsa Sign Pkcs1 2048 Sha256", "name": "rsa-sign-pkcs1-2048-sha256"}, {"description": "3072 bit RSA - PKCS#1 v1", "help": "3072 bit RSA - PKCS#1 v1.5 padding - SHA256 Digest.", "label": "Rsa Sign Pkcs1 3072 Sha256", "name": "rsa-sign-pkcs1-3072-sha256"}, {"description": "4096 bit RSA - PKCS#1 v1", "help": "4096 bit RSA - PKCS#1 v1.5 padding - SHA256 Digest.", "label": "Rsa Sign Pkcs1 4096 Sha256", "name": "rsa-sign-pkcs1-4096-sha256"}, {"description": "4096 bit RSA - PKCS#1 v1", "help": "4096 bit RSA - PKCS#1 v1.5 padding - SHA512 Digest.", "label": "Rsa Sign Pkcs1 4096 Sha512", "name": "rsa-sign-pkcs1-4096-sha512"}, {"description": "2048 bit RSA - PSS padding - SHA256 Digest", "help": "2048 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 2048 Sha256", "name": "rsa-sign-pss-2048-sha256"}, {"description": "3072 bit RSA - PSS padding - SHA256 Digest", "help": "3072 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 3072 Sha256", "name": "rsa-sign-pss-3072-sha256"}, {"description": "4096 bit RSA - PSS padding - SHA256 Digest", "help": "4096 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 4096 Sha256", "name": "rsa-sign-pss-4096-sha256"}, {"description": "4096 bit RSA - PSS padding - SHA256 Digest", "help": "4096 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 4096 Sha512", "name": "rsa-sign-pss-4096-sha512"}, {"description": "Elliptic Curve P-256 - SHA256 Digest", "help": "Elliptic Curve P-256 - SHA256 Digest.", "label": "Ec Sign P256 Sha256", "name": "ec-sign-p256-sha256"}, {"description": "Elliptic Curve P-384 - SHA384 Digest", "help": "Elliptic Curve P-384 - SHA384 Digest.", "label": "Ec Sign P384 Sha384", "name": "ec-sign-p384-sha384"}, {"description": "Elliptic Curvesecp256k1 - SHA256 Digest", "help": "Elliptic Curvesecp256k1 - SHA256 Digest.", "label": "Ec Sign Secp256K1 Sha256", "name": "ec-sign-secp256k1-sha256"}] | None = ...,
        details: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: HsmLocalPayload | None = ...,
        name: str | None = ...,
        comments: str | None = ...,
        vendor: Literal[{"description": "Unknown type of HSM", "help": "Unknown type of HSM.", "label": "Unknown", "name": "unknown"}, {"description": "Google Cloud HSM", "help": "Google Cloud HSM.", "label": "Gch", "name": "gch"}] | None = ...,
        api_version: Literal[{"description": "Unknown API version", "help": "Unknown API version.", "label": "Unknown", "name": "unknown"}, {"description": "Google Cloud HSM default API", "help": "Google Cloud HSM default API.", "label": "Gch Default", "name": "gch-default"}] | None = ...,
        certificate: str | None = ...,
        range: Literal[{"description": "Global range", "help": "Global range.", "label": "Global", "name": "global"}, {"description": "VDOM IP address range", "help": "VDOM IP address range.", "label": "Vdom", "name": "vdom"}] | None = ...,
        source: Literal[{"description": "Factory installed certificate", "help": "Factory installed certificate.", "label": "Factory", "name": "factory"}, {"description": "User generated certificate", "help": "User generated certificate.", "label": "User", "name": "user"}, {"description": "Bundle file certificate", "help": "Bundle file certificate.", "label": "Bundle", "name": "bundle"}] | None = ...,
        gch_url: str | None = ...,
        gch_project: str | None = ...,
        gch_location: str | None = ...,
        gch_keyring: str | None = ...,
        gch_cryptokey: str | None = ...,
        gch_cryptokey_version: str | None = ...,
        gch_cloud_service_name: str | None = ...,
        gch_cryptokey_algorithm: Literal[{"description": "2048 bit RSA - PKCS#1 v1", "help": "2048 bit RSA - PKCS#1 v1.5 padding - SHA256 Digest.", "label": "Rsa Sign Pkcs1 2048 Sha256", "name": "rsa-sign-pkcs1-2048-sha256"}, {"description": "3072 bit RSA - PKCS#1 v1", "help": "3072 bit RSA - PKCS#1 v1.5 padding - SHA256 Digest.", "label": "Rsa Sign Pkcs1 3072 Sha256", "name": "rsa-sign-pkcs1-3072-sha256"}, {"description": "4096 bit RSA - PKCS#1 v1", "help": "4096 bit RSA - PKCS#1 v1.5 padding - SHA256 Digest.", "label": "Rsa Sign Pkcs1 4096 Sha256", "name": "rsa-sign-pkcs1-4096-sha256"}, {"description": "4096 bit RSA - PKCS#1 v1", "help": "4096 bit RSA - PKCS#1 v1.5 padding - SHA512 Digest.", "label": "Rsa Sign Pkcs1 4096 Sha512", "name": "rsa-sign-pkcs1-4096-sha512"}, {"description": "2048 bit RSA - PSS padding - SHA256 Digest", "help": "2048 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 2048 Sha256", "name": "rsa-sign-pss-2048-sha256"}, {"description": "3072 bit RSA - PSS padding - SHA256 Digest", "help": "3072 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 3072 Sha256", "name": "rsa-sign-pss-3072-sha256"}, {"description": "4096 bit RSA - PSS padding - SHA256 Digest", "help": "4096 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 4096 Sha256", "name": "rsa-sign-pss-4096-sha256"}, {"description": "4096 bit RSA - PSS padding - SHA256 Digest", "help": "4096 bit RSA - PSS padding - SHA256 Digest.", "label": "Rsa Sign Pss 4096 Sha512", "name": "rsa-sign-pss-4096-sha512"}, {"description": "Elliptic Curve P-256 - SHA256 Digest", "help": "Elliptic Curve P-256 - SHA256 Digest.", "label": "Ec Sign P256 Sha256", "name": "ec-sign-p256-sha256"}, {"description": "Elliptic Curve P-384 - SHA384 Digest", "help": "Elliptic Curve P-384 - SHA384 Digest.", "label": "Ec Sign P384 Sha384", "name": "ec-sign-p384-sha384"}, {"description": "Elliptic Curvesecp256k1 - SHA256 Digest", "help": "Elliptic Curvesecp256k1 - SHA256 Digest.", "label": "Ec Sign Secp256K1 Sha256", "name": "ec-sign-secp256k1-sha256"}] | None = ...,
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
        payload_dict: HsmLocalPayload | None = ...,
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
    "HsmLocal",
    "HsmLocalPayload",
]