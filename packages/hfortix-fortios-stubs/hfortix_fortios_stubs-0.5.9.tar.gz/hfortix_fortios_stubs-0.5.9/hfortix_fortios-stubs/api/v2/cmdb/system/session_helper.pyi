from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SessionHelperPayload(TypedDict, total=False):
    """
    Type hints for system/session_helper payload fields.
    
    Configure session helper.
    
    **Usage:**
        payload: SessionHelperPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    id: NotRequired[int]  # Session helper ID.
    name: Literal[{"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "TFTP", "help": "TFTP.", "label": "Tftp", "name": "tftp"}, {"description": "RAS", "help": "RAS.", "label": "Ras", "name": "ras"}, {"description": "H323", "help": "H323.", "label": "H323", "name": "h323"}, {"description": "TNS", "help": "TNS.", "label": "Tns", "name": "tns"}, {"description": "MMS", "help": "MMS.", "label": "Mms", "name": "mms"}, {"description": "SIP", "help": "SIP.", "label": "Sip", "name": "sip"}, {"description": "PPTP", "help": "PPTP.", "label": "Pptp", "name": "pptp"}, {"description": "RTSP", "help": "RTSP.", "label": "Rtsp", "name": "rtsp"}, {"description": "DNS UDP", "help": "DNS UDP.", "label": "Dns Udp", "name": "dns-udp"}, {"description": "DNS TCP", "help": "DNS TCP.", "label": "Dns Tcp", "name": "dns-tcp"}, {"description": "PMAP", "help": "PMAP.", "label": "Pmap", "name": "pmap"}, {"description": "RSH", "help": "RSH.", "label": "Rsh", "name": "rsh"}, {"description": "DCERPC", "help": "DCERPC.", "label": "Dcerpc", "name": "dcerpc"}, {"description": "MGCP", "help": "MGCP.", "label": "Mgcp", "name": "mgcp"}]  # Helper name.
    protocol: int  # Protocol number.
    port: int  # Protocol port.


class SessionHelper:
    """
    Configure session helper.
    
    Path: system/session_helper
    Category: cmdb
    Primary Key: id
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        id: int | None = ...,
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
        id: int,
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
        id: int | None = ...,
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
        id: int | None = ...,
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
        id: int | None = ...,
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
        payload_dict: SessionHelperPayload | None = ...,
        id: int | None = ...,
        name: Literal[{"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "TFTP", "help": "TFTP.", "label": "Tftp", "name": "tftp"}, {"description": "RAS", "help": "RAS.", "label": "Ras", "name": "ras"}, {"description": "H323", "help": "H323.", "label": "H323", "name": "h323"}, {"description": "TNS", "help": "TNS.", "label": "Tns", "name": "tns"}, {"description": "MMS", "help": "MMS.", "label": "Mms", "name": "mms"}, {"description": "SIP", "help": "SIP.", "label": "Sip", "name": "sip"}, {"description": "PPTP", "help": "PPTP.", "label": "Pptp", "name": "pptp"}, {"description": "RTSP", "help": "RTSP.", "label": "Rtsp", "name": "rtsp"}, {"description": "DNS UDP", "help": "DNS UDP.", "label": "Dns Udp", "name": "dns-udp"}, {"description": "DNS TCP", "help": "DNS TCP.", "label": "Dns Tcp", "name": "dns-tcp"}, {"description": "PMAP", "help": "PMAP.", "label": "Pmap", "name": "pmap"}, {"description": "RSH", "help": "RSH.", "label": "Rsh", "name": "rsh"}, {"description": "DCERPC", "help": "DCERPC.", "label": "Dcerpc", "name": "dcerpc"}, {"description": "MGCP", "help": "MGCP.", "label": "Mgcp", "name": "mgcp"}] | None = ...,
        protocol: int | None = ...,
        port: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SessionHelperPayload | None = ...,
        id: int | None = ...,
        name: Literal[{"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "TFTP", "help": "TFTP.", "label": "Tftp", "name": "tftp"}, {"description": "RAS", "help": "RAS.", "label": "Ras", "name": "ras"}, {"description": "H323", "help": "H323.", "label": "H323", "name": "h323"}, {"description": "TNS", "help": "TNS.", "label": "Tns", "name": "tns"}, {"description": "MMS", "help": "MMS.", "label": "Mms", "name": "mms"}, {"description": "SIP", "help": "SIP.", "label": "Sip", "name": "sip"}, {"description": "PPTP", "help": "PPTP.", "label": "Pptp", "name": "pptp"}, {"description": "RTSP", "help": "RTSP.", "label": "Rtsp", "name": "rtsp"}, {"description": "DNS UDP", "help": "DNS UDP.", "label": "Dns Udp", "name": "dns-udp"}, {"description": "DNS TCP", "help": "DNS TCP.", "label": "Dns Tcp", "name": "dns-tcp"}, {"description": "PMAP", "help": "PMAP.", "label": "Pmap", "name": "pmap"}, {"description": "RSH", "help": "RSH.", "label": "Rsh", "name": "rsh"}, {"description": "DCERPC", "help": "DCERPC.", "label": "Dcerpc", "name": "dcerpc"}, {"description": "MGCP", "help": "MGCP.", "label": "Mgcp", "name": "mgcp"}] | None = ...,
        protocol: int | None = ...,
        port: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        id: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        id: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: SessionHelperPayload | None = ...,
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
    "SessionHelper",
    "SessionHelperPayload",
]