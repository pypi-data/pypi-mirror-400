from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class LocalPayload(TypedDict, total=False):
    """
    Type hints for certificate/local payload fields.
    
    Local keys and certificates.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.ca.CaEndpoint` (via: cmp-server-cert, est-server-cert)
        - :class:`~.certificate.local.LocalEndpoint` (via: est-client-cert)
        - :class:`~.certificate.remote.RemoteEndpoint` (via: cmp-server-cert, est-server-cert)

    **Usage:**
        payload: LocalPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Name.
    password: NotRequired[str]  # Password as a PEM file.
    comments: NotRequired[str]  # Comment.
    private_key: str  # PEM format key encrypted with a password.
    certificate: NotRequired[str]  # PEM format certificate.
    csr: NotRequired[str]  # Certificate Signing Request.
    state: NotRequired[str]  # Certificate Signing Request State.
    scep_url: NotRequired[str]  # SCEP server URL.
    range: NotRequired[Literal[{"description": "Global range", "help": "Global range.", "label": "Global", "name": "global"}, {"description": "VDOM IP address range", "help": "VDOM IP address range.", "label": "Vdom", "name": "vdom"}]]  # Either a global or VDOM IP address range for the certificate
    source: NotRequired[Literal[{"description": "Factory installed certificate", "help": "Factory installed certificate.", "label": "Factory", "name": "factory"}, {"description": "User generated certificate", "help": "User generated certificate.", "label": "User", "name": "user"}, {"description": "Bundle file certificate", "help": "Bundle file certificate.", "label": "Bundle", "name": "bundle"}]]  # Certificate source type.
    auto_regenerate_days: NotRequired[int]  # Number of days to wait before expiry of an updated local cer
    auto_regenerate_days_warning: NotRequired[int]  # Number of days to wait before an expiry warning message is g
    scep_password: NotRequired[str]  # SCEP server challenge password for auto-regeneration.
    ca_identifier: NotRequired[str]  # CA identifier of the CA server for signing via SCEP.
    name_encoding: NotRequired[Literal[{"description": "Printable encoding (default)", "help": "Printable encoding (default).", "label": "Printable", "name": "printable"}, {"description": "UTF-8 encoding", "help": "UTF-8 encoding.", "label": "Utf8", "name": "utf8"}]]  # Name encoding method for auto-regeneration.
    source_ip: NotRequired[str]  # Source IP address for communications to the SCEP server.
    ike_localid: NotRequired[str]  # Local ID the FortiGate uses for authentication as a VPN clie
    ike_localid_type: NotRequired[Literal[{"description": "ASN", "help": "ASN.1 distinguished name.", "label": "Asn1Dn", "name": "asn1dn"}, {"description": "Fully qualified domain name", "help": "Fully qualified domain name.", "label": "Fqdn", "name": "fqdn"}]]  # IKE local ID type.
    enroll_protocol: NotRequired[Literal[{"description": "None (default)", "help": "None (default).", "label": "None", "name": "none"}, {"description": "Simple Certificate Enrollment Protocol", "help": "Simple Certificate Enrollment Protocol.", "label": "Scep", "name": "scep"}, {"description": "Certificate Management Protocol Version 2", "help": "Certificate Management Protocol Version 2.", "label": "Cmpv2", "name": "cmpv2"}, {"description": "Automated Certificate Management Environment Version 2", "help": "Automated Certificate Management Environment Version 2.", "label": "Acme2", "name": "acme2"}, {"description": "Enrollment over Secure Transport", "help": "Enrollment over Secure Transport.", "label": "Est", "name": "est"}]]  # Certificate enrollment protocol.
    private_key_retain: NotRequired[Literal[{"description": "Keep the existing private key during SCEP renewal", "help": "Keep the existing private key during SCEP renewal.", "label": "Enable", "name": "enable"}, {"description": "Generate a new private key during SCEP renewal", "help": "Generate a new private key during SCEP renewal.", "label": "Disable", "name": "disable"}]]  # Enable/disable retention of private key during SCEP renewal 
    cmp_server: NotRequired[str]  # Address and port for CMP server (format = address:port).
    cmp_path: NotRequired[str]  # Path location inside CMP server.
    cmp_server_cert: NotRequired[str]  # CMP server certificate.
    cmp_regeneration_method: NotRequired[Literal[{"description": "Key Update", "help": "Key Update.", "label": "Keyupate", "name": "keyupate"}, {"description": "Renewal", "help": "Renewal.", "label": "Renewal", "name": "renewal"}]]  # CMP auto-regeneration method.
    acme_ca_url: str  # The URL for the ACME CA server (Let's Encrypt is the default
    acme_domain: str  # A valid domain that resolves to this FortiGate unit.
    acme_email: str  # Contact email address that is required by some CAs like Lets
    acme_eab_key_id: NotRequired[str]  # External Account Binding Key ID (optional setting).
    acme_eab_key_hmac: NotRequired[str]  # External Account Binding HMAC Key (URL-encoded base64).
    acme_rsa_key_size: NotRequired[int]  # Length of the RSA private key of the generated cert (Minimum
    acme_renew_window: NotRequired[int]  # Beginning of the renewal window (in days before certificate 
    est_server: NotRequired[str]  # Address and port for EST server (e.g. https://example.com:12
    est_ca_id: NotRequired[str]  # CA identifier of the CA server for signing via EST.
    est_http_username: NotRequired[str]  # HTTP Authentication username for signing via EST.
    est_http_password: NotRequired[str]  # HTTP Authentication password for signing via EST.
    est_client_cert: NotRequired[str]  # Certificate used to authenticate this FortiGate to EST serve
    est_server_cert: NotRequired[str]  # EST server's certificate must be verifiable by this certific
    est_srp_username: NotRequired[str]  # EST SRP authentication username.
    est_srp_password: NotRequired[str]  # EST SRP authentication password.
    est_regeneration_method: NotRequired[Literal[{"description": "Create new private key during re-enrollment", "help": "Create new private key during re-enrollment.", "label": "Create New Key", "name": "create-new-key"}, {"description": "Reuse existing private key during re-enrollment", "help": "Reuse existing private key during re-enrollment.", "label": "Use Existing Key", "name": "use-existing-key"}]]  # EST behavioral options during re-enrollment.
    details: NotRequired[str]  # Print local certificate detailed information.


class Local:
    """
    Local keys and certificates.
    
    Path: certificate/local
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
        payload_dict: LocalPayload | None = ...,
        name: str | None = ...,
        password: str | None = ...,
        comments: str | None = ...,
        private_key: str | None = ...,
        certificate: str | None = ...,
        csr: str | None = ...,
        state: str | None = ...,
        scep_url: str | None = ...,
        range: Literal[{"description": "Global range", "help": "Global range.", "label": "Global", "name": "global"}, {"description": "VDOM IP address range", "help": "VDOM IP address range.", "label": "Vdom", "name": "vdom"}] | None = ...,
        source: Literal[{"description": "Factory installed certificate", "help": "Factory installed certificate.", "label": "Factory", "name": "factory"}, {"description": "User generated certificate", "help": "User generated certificate.", "label": "User", "name": "user"}, {"description": "Bundle file certificate", "help": "Bundle file certificate.", "label": "Bundle", "name": "bundle"}] | None = ...,
        auto_regenerate_days: int | None = ...,
        auto_regenerate_days_warning: int | None = ...,
        scep_password: str | None = ...,
        ca_identifier: str | None = ...,
        name_encoding: Literal[{"description": "Printable encoding (default)", "help": "Printable encoding (default).", "label": "Printable", "name": "printable"}, {"description": "UTF-8 encoding", "help": "UTF-8 encoding.", "label": "Utf8", "name": "utf8"}] | None = ...,
        source_ip: str | None = ...,
        ike_localid: str | None = ...,
        ike_localid_type: Literal[{"description": "ASN", "help": "ASN.1 distinguished name.", "label": "Asn1Dn", "name": "asn1dn"}, {"description": "Fully qualified domain name", "help": "Fully qualified domain name.", "label": "Fqdn", "name": "fqdn"}] | None = ...,
        enroll_protocol: Literal[{"description": "None (default)", "help": "None (default).", "label": "None", "name": "none"}, {"description": "Simple Certificate Enrollment Protocol", "help": "Simple Certificate Enrollment Protocol.", "label": "Scep", "name": "scep"}, {"description": "Certificate Management Protocol Version 2", "help": "Certificate Management Protocol Version 2.", "label": "Cmpv2", "name": "cmpv2"}, {"description": "Automated Certificate Management Environment Version 2", "help": "Automated Certificate Management Environment Version 2.", "label": "Acme2", "name": "acme2"}, {"description": "Enrollment over Secure Transport", "help": "Enrollment over Secure Transport.", "label": "Est", "name": "est"}] | None = ...,
        private_key_retain: Literal[{"description": "Keep the existing private key during SCEP renewal", "help": "Keep the existing private key during SCEP renewal.", "label": "Enable", "name": "enable"}, {"description": "Generate a new private key during SCEP renewal", "help": "Generate a new private key during SCEP renewal.", "label": "Disable", "name": "disable"}] | None = ...,
        cmp_server: str | None = ...,
        cmp_path: str | None = ...,
        cmp_server_cert: str | None = ...,
        cmp_regeneration_method: Literal[{"description": "Key Update", "help": "Key Update.", "label": "Keyupate", "name": "keyupate"}, {"description": "Renewal", "help": "Renewal.", "label": "Renewal", "name": "renewal"}] | None = ...,
        acme_ca_url: str | None = ...,
        acme_domain: str | None = ...,
        acme_email: str | None = ...,
        acme_eab_key_id: str | None = ...,
        acme_eab_key_hmac: str | None = ...,
        acme_rsa_key_size: int | None = ...,
        acme_renew_window: int | None = ...,
        est_server: str | None = ...,
        est_ca_id: str | None = ...,
        est_http_username: str | None = ...,
        est_http_password: str | None = ...,
        est_client_cert: str | None = ...,
        est_server_cert: str | None = ...,
        est_srp_username: str | None = ...,
        est_srp_password: str | None = ...,
        est_regeneration_method: Literal[{"description": "Create new private key during re-enrollment", "help": "Create new private key during re-enrollment.", "label": "Create New Key", "name": "create-new-key"}, {"description": "Reuse existing private key during re-enrollment", "help": "Reuse existing private key during re-enrollment.", "label": "Use Existing Key", "name": "use-existing-key"}] | None = ...,
        details: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: LocalPayload | None = ...,
        name: str | None = ...,
        password: str | None = ...,
        comments: str | None = ...,
        private_key: str | None = ...,
        certificate: str | None = ...,
        csr: str | None = ...,
        state: str | None = ...,
        scep_url: str | None = ...,
        range: Literal[{"description": "Global range", "help": "Global range.", "label": "Global", "name": "global"}, {"description": "VDOM IP address range", "help": "VDOM IP address range.", "label": "Vdom", "name": "vdom"}] | None = ...,
        source: Literal[{"description": "Factory installed certificate", "help": "Factory installed certificate.", "label": "Factory", "name": "factory"}, {"description": "User generated certificate", "help": "User generated certificate.", "label": "User", "name": "user"}, {"description": "Bundle file certificate", "help": "Bundle file certificate.", "label": "Bundle", "name": "bundle"}] | None = ...,
        auto_regenerate_days: int | None = ...,
        auto_regenerate_days_warning: int | None = ...,
        scep_password: str | None = ...,
        ca_identifier: str | None = ...,
        name_encoding: Literal[{"description": "Printable encoding (default)", "help": "Printable encoding (default).", "label": "Printable", "name": "printable"}, {"description": "UTF-8 encoding", "help": "UTF-8 encoding.", "label": "Utf8", "name": "utf8"}] | None = ...,
        source_ip: str | None = ...,
        ike_localid: str | None = ...,
        ike_localid_type: Literal[{"description": "ASN", "help": "ASN.1 distinguished name.", "label": "Asn1Dn", "name": "asn1dn"}, {"description": "Fully qualified domain name", "help": "Fully qualified domain name.", "label": "Fqdn", "name": "fqdn"}] | None = ...,
        enroll_protocol: Literal[{"description": "None (default)", "help": "None (default).", "label": "None", "name": "none"}, {"description": "Simple Certificate Enrollment Protocol", "help": "Simple Certificate Enrollment Protocol.", "label": "Scep", "name": "scep"}, {"description": "Certificate Management Protocol Version 2", "help": "Certificate Management Protocol Version 2.", "label": "Cmpv2", "name": "cmpv2"}, {"description": "Automated Certificate Management Environment Version 2", "help": "Automated Certificate Management Environment Version 2.", "label": "Acme2", "name": "acme2"}, {"description": "Enrollment over Secure Transport", "help": "Enrollment over Secure Transport.", "label": "Est", "name": "est"}] | None = ...,
        private_key_retain: Literal[{"description": "Keep the existing private key during SCEP renewal", "help": "Keep the existing private key during SCEP renewal.", "label": "Enable", "name": "enable"}, {"description": "Generate a new private key during SCEP renewal", "help": "Generate a new private key during SCEP renewal.", "label": "Disable", "name": "disable"}] | None = ...,
        cmp_server: str | None = ...,
        cmp_path: str | None = ...,
        cmp_server_cert: str | None = ...,
        cmp_regeneration_method: Literal[{"description": "Key Update", "help": "Key Update.", "label": "Keyupate", "name": "keyupate"}, {"description": "Renewal", "help": "Renewal.", "label": "Renewal", "name": "renewal"}] | None = ...,
        acme_ca_url: str | None = ...,
        acme_domain: str | None = ...,
        acme_email: str | None = ...,
        acme_eab_key_id: str | None = ...,
        acme_eab_key_hmac: str | None = ...,
        acme_rsa_key_size: int | None = ...,
        acme_renew_window: int | None = ...,
        est_server: str | None = ...,
        est_ca_id: str | None = ...,
        est_http_username: str | None = ...,
        est_http_password: str | None = ...,
        est_client_cert: str | None = ...,
        est_server_cert: str | None = ...,
        est_srp_username: str | None = ...,
        est_srp_password: str | None = ...,
        est_regeneration_method: Literal[{"description": "Create new private key during re-enrollment", "help": "Create new private key during re-enrollment.", "label": "Create New Key", "name": "create-new-key"}, {"description": "Reuse existing private key during re-enrollment", "help": "Reuse existing private key during re-enrollment.", "label": "Use Existing Key", "name": "use-existing-key"}] | None = ...,
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
        payload_dict: LocalPayload | None = ...,
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
    "Local",
    "LocalPayload",
]