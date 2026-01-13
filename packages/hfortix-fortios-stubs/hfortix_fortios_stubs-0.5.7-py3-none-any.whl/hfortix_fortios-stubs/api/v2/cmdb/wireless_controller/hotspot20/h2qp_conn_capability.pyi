from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class H2qpConnCapabilityPayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/hotspot20/h2qp_conn_capability payload fields.
    
    Configure connection capability.
    
    **Usage:**
        payload: H2qpConnCapabilityPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Connection capability name.
    icmp_port: NotRequired[Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]]  # Set ICMP port service status.
    ftp_port: NotRequired[Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]]  # Set FTP port service status.
    ssh_port: NotRequired[Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]]  # Set SSH port service status.
    http_port: NotRequired[Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]]  # Set HTTP port service status.
    tls_port: NotRequired[Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]]  # Set TLS VPN (HTTPS) port service status.
    pptp_vpn_port: NotRequired[Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]]  # Set Point to Point Tunneling Protocol (PPTP) VPN port servic
    voip_tcp_port: NotRequired[Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]]  # Set VoIP TCP port service status.
    voip_udp_port: NotRequired[Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]]  # Set VoIP UDP port service status.
    ikev2_port: NotRequired[Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]]  # Set IKEv2 port service for IPsec VPN status.
    ikev2_xx_port: NotRequired[Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]]  # Set UDP port 4500 (which may be used by IKEv2 for IPsec VPN)
    esp_port: NotRequired[Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}]]  # Set ESP port service (used by IPsec VPNs) status.


class H2qpConnCapability:
    """
    Configure connection capability.
    
    Path: wireless_controller/hotspot20/h2qp_conn_capability
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
        payload_dict: H2qpConnCapabilityPayload | None = ...,
        name: str | None = ...,
        icmp_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        ftp_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        ssh_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        http_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        tls_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        pptp_vpn_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        voip_tcp_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        voip_udp_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        ikev2_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        ikev2_xx_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        esp_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: H2qpConnCapabilityPayload | None = ...,
        name: str | None = ...,
        icmp_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        ftp_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        ssh_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        http_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        tls_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        pptp_vpn_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        voip_tcp_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        voip_udp_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        ikev2_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        ikev2_xx_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
        esp_port: Literal[{"description": "The port is not open for communication", "help": "The port is not open for communication.", "label": "Closed", "name": "closed"}, {"description": "The port is open for communication", "help": "The port is open for communication.", "label": "Open", "name": "open"}, {"description": "The port may or may not be open for communication", "help": "The port may or may not be open for communication.", "label": "Unknown", "name": "unknown"}] | None = ...,
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
        payload_dict: H2qpConnCapabilityPayload | None = ...,
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
    "H2qpConnCapability",
    "H2qpConnCapabilityPayload",
]