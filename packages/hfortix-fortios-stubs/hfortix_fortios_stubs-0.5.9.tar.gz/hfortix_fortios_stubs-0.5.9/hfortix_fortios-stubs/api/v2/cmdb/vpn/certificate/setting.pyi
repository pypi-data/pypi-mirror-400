from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingPayload(TypedDict, total=False):
    """
    Type hints for vpn/certificate/setting payload fields.
    
    VPN certificate setting.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)
        - :class:`~.vpn.certificate.local.LocalEndpoint` (via: certname-dsa1024, certname-dsa2048, certname-ecdsa256, +7 more)
        - :class:`~.vpn.certificate.ocsp-server.OcspServerEndpoint` (via: ocsp-default-server)

    **Usage:**
        payload: SettingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    ocsp_status: NotRequired[Literal[{"description": "OCSP is performed if CRL is not checked", "help": "OCSP is performed if CRL is not checked.", "label": "Enable", "name": "enable"}, {"description": "If cert is not revoked by CRL, OCSP is performed", "help": "If cert is not revoked by CRL, OCSP is performed.", "label": "Mandatory", "name": "mandatory"}, {"description": "OCSP is not performed", "help": "OCSP is not performed.", "label": "Disable", "name": "disable"}]]  # Enable/disable receiving certificates using the OCSP.
    ocsp_option: NotRequired[Literal[{"description": "Use URL from certificate", "help": "Use URL from certificate.", "label": "Certificate", "name": "certificate"}, {"description": "Use URL from configured OCSP server", "help": "Use URL from configured OCSP server.", "label": "Server", "name": "server"}]]  # Specify whether the OCSP URL is from certificate or configur
    proxy: NotRequired[str]  # Proxy server FQDN or IP for OCSP/CA queries during certifica
    proxy_port: NotRequired[int]  # Proxy server port (1 - 65535, default = 8080).
    proxy_username: NotRequired[str]  # Proxy server user name.
    proxy_password: NotRequired[str]  # Proxy server password.
    source_ip: NotRequired[str]  # Source IP address for dynamic AIA and OCSP queries.
    ocsp_default_server: NotRequired[str]  # Default OCSP server.
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.
    check_ca_cert: NotRequired[Literal[{"description": "Enable verification of the user certificate", "help": "Enable verification of the user certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable verification of the user certificate", "help": "Disable verification of the user certificate.", "label": "Disable", "name": "disable"}]]  # Enable/disable verification of the user certificate and pass
    check_ca_chain: NotRequired[Literal[{"description": "Enable verification of the entire certificate chain", "help": "Enable verification of the entire certificate chain.", "label": "Enable", "name": "enable"}, {"description": "Disable verification of the entire certificate chain", "help": "Disable verification of the entire certificate chain.", "label": "Disable", "name": "disable"}]]  # Enable/disable verification of the entire certificate chain 
    subject_match: NotRequired[Literal[{"description": "Find a match if the name being searched for is a part or the same as a certificate subject RDN", "help": "Find a match if the name being searched for is a part or the same as a certificate subject RDN.", "label": "Substring", "name": "substring"}, {"description": "Find a match if the name being searched for is same as a certificate subject RDN", "help": "Find a match if the name being searched for is same as a certificate subject RDN.", "label": "Value", "name": "value"}]]  # When searching for a matching certificate, control how to do
    subject_set: NotRequired[Literal[{"description": "Find a match if the name being searched for is a subset of a certificate subject", "help": "Find a match if the name being searched for is a subset of a certificate subject.", "label": "Subset", "name": "subset"}, {"description": "Find a match if the name being searched for is a superset of a certificate subject", "help": "Find a match if the name being searched for is a superset of a certificate subject.", "label": "Superset", "name": "superset"}]]  # When searching for a matching certificate, control how to do
    cn_match: NotRequired[Literal[{"description": "Find a match if the name being searched for is a part or the same as a certificate CN", "help": "Find a match if the name being searched for is a part or the same as a certificate CN.", "label": "Substring", "name": "substring"}, {"description": "Find a match if the name being searched for is same as a certificate CN", "help": "Find a match if the name being searched for is same as a certificate CN.", "label": "Value", "name": "value"}]]  # When searching for a matching certificate, control how to do
    cn_allow_multi: NotRequired[Literal[{"description": "Does not allow multiple CN entries in certificate matching", "help": "Does not allow multiple CN entries in certificate matching.", "label": "Disable", "name": "disable"}, {"description": "Allow multiple CN entries in certificate matching", "help": "Allow multiple CN entries in certificate matching.", "label": "Enable", "name": "enable"}]]  # When searching for a matching certificate, allow multiple CN
    crl_verification: NotRequired[str]  # CRL verification options.
    strict_ocsp_check: NotRequired[Literal[{"description": "Enable strict mode OCSP checking", "help": "Enable strict mode OCSP checking.", "label": "Enable", "name": "enable"}, {"description": "Disable strict mode OCSP checking", "help": "Disable strict mode OCSP checking.", "label": "Disable", "name": "disable"}]]  # Enable/disable strict mode OCSP checking.
    ssl_min_proto_version: NotRequired[Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]]  # Minimum supported protocol version for SSL/TLS connections (
    cmp_save_extra_certs: NotRequired[Literal[{"description": "Enable saving extra certificates in CMP mode", "help": "Enable saving extra certificates in CMP mode.", "label": "Enable", "name": "enable"}, {"description": "Disable saving extra certificates in CMP mode", "help": "Disable saving extra certificates in CMP mode.", "label": "Disable", "name": "disable"}]]  # Enable/disable saving extra certificates in CMP mode (defaul
    cmp_key_usage_checking: NotRequired[Literal[{"description": "Enable server certificate key usage checking in CMP mode", "help": "Enable server certificate key usage checking in CMP mode.", "label": "Enable", "name": "enable"}, {"description": "Disable server certificate key usage checking in CMP mode", "help": "Disable server certificate key usage checking in CMP mode.", "label": "Disable", "name": "disable"}]]  # Enable/disable server certificate key usage checking in CMP 
    cert_expire_warning: NotRequired[int]  # Number of days before a certificate expires to send a warnin
    certname_rsa1024: str  # 1024 bit RSA key certificate for re-signing server certifica
    certname_rsa2048: str  # 2048 bit RSA key certificate for re-signing server certifica
    certname_rsa4096: str  # 4096 bit RSA key certificate for re-signing server certifica
    certname_dsa1024: str  # 1024 bit DSA key certificate for re-signing server certifica
    certname_dsa2048: str  # 2048 bit DSA key certificate for re-signing server certifica
    certname_ecdsa256: str  # 256 bit ECDSA key certificate for re-signing server certific
    certname_ecdsa384: str  # 384 bit ECDSA key certificate for re-signing server certific
    certname_ecdsa521: str  # 521 bit ECDSA key certificate for re-signing server certific
    certname_ed25519: str  # 253 bit EdDSA key certificate for re-signing server certific
    certname_ed448: str  # 456 bit EdDSA key certificate for re-signing server certific


class Setting:
    """
    VPN certificate setting.
    
    Path: vpn/certificate/setting
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
        payload_dict: SettingPayload | None = ...,
        ocsp_status: Literal[{"description": "OCSP is performed if CRL is not checked", "help": "OCSP is performed if CRL is not checked.", "label": "Enable", "name": "enable"}, {"description": "If cert is not revoked by CRL, OCSP is performed", "help": "If cert is not revoked by CRL, OCSP is performed.", "label": "Mandatory", "name": "mandatory"}, {"description": "OCSP is not performed", "help": "OCSP is not performed.", "label": "Disable", "name": "disable"}] | None = ...,
        ocsp_option: Literal[{"description": "Use URL from certificate", "help": "Use URL from certificate.", "label": "Certificate", "name": "certificate"}, {"description": "Use URL from configured OCSP server", "help": "Use URL from configured OCSP server.", "label": "Server", "name": "server"}] | None = ...,
        proxy: str | None = ...,
        proxy_port: int | None = ...,
        proxy_username: str | None = ...,
        proxy_password: str | None = ...,
        source_ip: str | None = ...,
        ocsp_default_server: str | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        check_ca_cert: Literal[{"description": "Enable verification of the user certificate", "help": "Enable verification of the user certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable verification of the user certificate", "help": "Disable verification of the user certificate.", "label": "Disable", "name": "disable"}] | None = ...,
        check_ca_chain: Literal[{"description": "Enable verification of the entire certificate chain", "help": "Enable verification of the entire certificate chain.", "label": "Enable", "name": "enable"}, {"description": "Disable verification of the entire certificate chain", "help": "Disable verification of the entire certificate chain.", "label": "Disable", "name": "disable"}] | None = ...,
        subject_match: Literal[{"description": "Find a match if the name being searched for is a part or the same as a certificate subject RDN", "help": "Find a match if the name being searched for is a part or the same as a certificate subject RDN.", "label": "Substring", "name": "substring"}, {"description": "Find a match if the name being searched for is same as a certificate subject RDN", "help": "Find a match if the name being searched for is same as a certificate subject RDN.", "label": "Value", "name": "value"}] | None = ...,
        subject_set: Literal[{"description": "Find a match if the name being searched for is a subset of a certificate subject", "help": "Find a match if the name being searched for is a subset of a certificate subject.", "label": "Subset", "name": "subset"}, {"description": "Find a match if the name being searched for is a superset of a certificate subject", "help": "Find a match if the name being searched for is a superset of a certificate subject.", "label": "Superset", "name": "superset"}] | None = ...,
        cn_match: Literal[{"description": "Find a match if the name being searched for is a part or the same as a certificate CN", "help": "Find a match if the name being searched for is a part or the same as a certificate CN.", "label": "Substring", "name": "substring"}, {"description": "Find a match if the name being searched for is same as a certificate CN", "help": "Find a match if the name being searched for is same as a certificate CN.", "label": "Value", "name": "value"}] | None = ...,
        cn_allow_multi: Literal[{"description": "Does not allow multiple CN entries in certificate matching", "help": "Does not allow multiple CN entries in certificate matching.", "label": "Disable", "name": "disable"}, {"description": "Allow multiple CN entries in certificate matching", "help": "Allow multiple CN entries in certificate matching.", "label": "Enable", "name": "enable"}] | None = ...,
        crl_verification: str | None = ...,
        strict_ocsp_check: Literal[{"description": "Enable strict mode OCSP checking", "help": "Enable strict mode OCSP checking.", "label": "Enable", "name": "enable"}, {"description": "Disable strict mode OCSP checking", "help": "Disable strict mode OCSP checking.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        cmp_save_extra_certs: Literal[{"description": "Enable saving extra certificates in CMP mode", "help": "Enable saving extra certificates in CMP mode.", "label": "Enable", "name": "enable"}, {"description": "Disable saving extra certificates in CMP mode", "help": "Disable saving extra certificates in CMP mode.", "label": "Disable", "name": "disable"}] | None = ...,
        cmp_key_usage_checking: Literal[{"description": "Enable server certificate key usage checking in CMP mode", "help": "Enable server certificate key usage checking in CMP mode.", "label": "Enable", "name": "enable"}, {"description": "Disable server certificate key usage checking in CMP mode", "help": "Disable server certificate key usage checking in CMP mode.", "label": "Disable", "name": "disable"}] | None = ...,
        cert_expire_warning: int | None = ...,
        certname_rsa1024: str | None = ...,
        certname_rsa2048: str | None = ...,
        certname_rsa4096: str | None = ...,
        certname_dsa1024: str | None = ...,
        certname_dsa2048: str | None = ...,
        certname_ecdsa256: str | None = ...,
        certname_ecdsa384: str | None = ...,
        certname_ecdsa521: str | None = ...,
        certname_ed25519: str | None = ...,
        certname_ed448: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SettingPayload | None = ...,
        ocsp_status: Literal[{"description": "OCSP is performed if CRL is not checked", "help": "OCSP is performed if CRL is not checked.", "label": "Enable", "name": "enable"}, {"description": "If cert is not revoked by CRL, OCSP is performed", "help": "If cert is not revoked by CRL, OCSP is performed.", "label": "Mandatory", "name": "mandatory"}, {"description": "OCSP is not performed", "help": "OCSP is not performed.", "label": "Disable", "name": "disable"}] | None = ...,
        ocsp_option: Literal[{"description": "Use URL from certificate", "help": "Use URL from certificate.", "label": "Certificate", "name": "certificate"}, {"description": "Use URL from configured OCSP server", "help": "Use URL from configured OCSP server.", "label": "Server", "name": "server"}] | None = ...,
        proxy: str | None = ...,
        proxy_port: int | None = ...,
        proxy_username: str | None = ...,
        proxy_password: str | None = ...,
        source_ip: str | None = ...,
        ocsp_default_server: str | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        check_ca_cert: Literal[{"description": "Enable verification of the user certificate", "help": "Enable verification of the user certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable verification of the user certificate", "help": "Disable verification of the user certificate.", "label": "Disable", "name": "disable"}] | None = ...,
        check_ca_chain: Literal[{"description": "Enable verification of the entire certificate chain", "help": "Enable verification of the entire certificate chain.", "label": "Enable", "name": "enable"}, {"description": "Disable verification of the entire certificate chain", "help": "Disable verification of the entire certificate chain.", "label": "Disable", "name": "disable"}] | None = ...,
        subject_match: Literal[{"description": "Find a match if the name being searched for is a part or the same as a certificate subject RDN", "help": "Find a match if the name being searched for is a part or the same as a certificate subject RDN.", "label": "Substring", "name": "substring"}, {"description": "Find a match if the name being searched for is same as a certificate subject RDN", "help": "Find a match if the name being searched for is same as a certificate subject RDN.", "label": "Value", "name": "value"}] | None = ...,
        subject_set: Literal[{"description": "Find a match if the name being searched for is a subset of a certificate subject", "help": "Find a match if the name being searched for is a subset of a certificate subject.", "label": "Subset", "name": "subset"}, {"description": "Find a match if the name being searched for is a superset of a certificate subject", "help": "Find a match if the name being searched for is a superset of a certificate subject.", "label": "Superset", "name": "superset"}] | None = ...,
        cn_match: Literal[{"description": "Find a match if the name being searched for is a part or the same as a certificate CN", "help": "Find a match if the name being searched for is a part or the same as a certificate CN.", "label": "Substring", "name": "substring"}, {"description": "Find a match if the name being searched for is same as a certificate CN", "help": "Find a match if the name being searched for is same as a certificate CN.", "label": "Value", "name": "value"}] | None = ...,
        cn_allow_multi: Literal[{"description": "Does not allow multiple CN entries in certificate matching", "help": "Does not allow multiple CN entries in certificate matching.", "label": "Disable", "name": "disable"}, {"description": "Allow multiple CN entries in certificate matching", "help": "Allow multiple CN entries in certificate matching.", "label": "Enable", "name": "enable"}] | None = ...,
        crl_verification: str | None = ...,
        strict_ocsp_check: Literal[{"description": "Enable strict mode OCSP checking", "help": "Enable strict mode OCSP checking.", "label": "Enable", "name": "enable"}, {"description": "Disable strict mode OCSP checking", "help": "Disable strict mode OCSP checking.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        cmp_save_extra_certs: Literal[{"description": "Enable saving extra certificates in CMP mode", "help": "Enable saving extra certificates in CMP mode.", "label": "Enable", "name": "enable"}, {"description": "Disable saving extra certificates in CMP mode", "help": "Disable saving extra certificates in CMP mode.", "label": "Disable", "name": "disable"}] | None = ...,
        cmp_key_usage_checking: Literal[{"description": "Enable server certificate key usage checking in CMP mode", "help": "Enable server certificate key usage checking in CMP mode.", "label": "Enable", "name": "enable"}, {"description": "Disable server certificate key usage checking in CMP mode", "help": "Disable server certificate key usage checking in CMP mode.", "label": "Disable", "name": "disable"}] | None = ...,
        cert_expire_warning: int | None = ...,
        certname_rsa1024: str | None = ...,
        certname_rsa2048: str | None = ...,
        certname_rsa4096: str | None = ...,
        certname_dsa1024: str | None = ...,
        certname_dsa2048: str | None = ...,
        certname_ecdsa256: str | None = ...,
        certname_ecdsa384: str | None = ...,
        certname_ecdsa521: str | None = ...,
        certname_ed25519: str | None = ...,
        certname_ed448: str | None = ...,
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
        payload_dict: SettingPayload | None = ...,
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
    "Setting",
    "SettingPayload",
]