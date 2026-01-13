from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class HostKeyPayload(TypedDict, total=False):
    """
    Type hints for firewall/ssh/host_key payload fields.
    
    SSH proxy host public keys.
    
    **Usage:**
        payload: HostKeyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # SSH public key name.
    status: NotRequired[Literal[{"description": "The public key is trusted", "help": "The public key is trusted.", "label": "Trusted", "name": "trusted"}, {"description": "The public key is revoked", "help": "The public key is revoked.", "label": "Revoked", "name": "revoked"}]]  # Set the trust status of the public key.
    type: NotRequired[Literal[{"description": "The type of the public key is RSA", "help": "The type of the public key is RSA.", "label": "Rsa", "name": "RSA"}, {"description": "The type of the public key is DSA", "help": "The type of the public key is DSA.", "label": "Dsa", "name": "DSA"}, {"description": "The type of the public key is ECDSA", "help": "The type of the public key is ECDSA.", "label": "Ecdsa", "name": "ECDSA"}, {"description": "The type of the public key is ED25519", "help": "The type of the public key is ED25519.", "label": "Ed25519", "name": "ED25519"}, {"description": "The type of the public key is from RSA CA", "help": "The type of the public key is from RSA CA.", "label": "Rsa Ca", "name": "RSA-CA"}, {"description": "The type of the public key is from DSA CA", "help": "The type of the public key is from DSA CA.", "label": "Dsa Ca", "name": "DSA-CA"}, {"description": "The type of the public key is from ECDSA CA", "help": "The type of the public key is from ECDSA CA.", "label": "Ecdsa Ca", "name": "ECDSA-CA"}, {"description": "The type of the public key is from ED25519 CA", "help": "The type of the public key is from ED25519 CA.", "label": "Ed25519 Ca", "name": "ED25519-CA"}]]  # Set the type of the public key.
    nid: NotRequired[Literal[{"description": "The NID is ecdsa-sha2-nistp256", "help": "The NID is ecdsa-sha2-nistp256.", "label": "256", "name": "256"}, {"description": "The NID is ecdsa-sha2-nistp384", "help": "The NID is ecdsa-sha2-nistp384.", "label": "384", "name": "384"}, {"description": "The NID is ecdsa-sha2-nistp521", "help": "The NID is ecdsa-sha2-nistp521.", "label": "521", "name": "521"}]]  # Set the nid of the ECDSA key.
    usage: NotRequired[Literal[{"description": "Transparent proxy uses this public key to validate server", "help": "Transparent proxy uses this public key to validate server.", "label": "Transparent Proxy", "name": "transparent-proxy"}, {"description": "Access proxy uses this public key to validate server", "help": "Access proxy uses this public key to validate server.", "label": "Access Proxy", "name": "access-proxy"}]]  # Usage for this public key.
    ip: NotRequired[str]  # IP address of the SSH server.
    port: NotRequired[int]  # Port of the SSH server.
    hostname: NotRequired[str]  # Hostname of the SSH server to match SSH certificate principa
    public_key: NotRequired[str]  # SSH public key.


class HostKey:
    """
    SSH proxy host public keys.
    
    Path: firewall/ssh/host_key
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
        payload_dict: HostKeyPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "The public key is trusted", "help": "The public key is trusted.", "label": "Trusted", "name": "trusted"}, {"description": "The public key is revoked", "help": "The public key is revoked.", "label": "Revoked", "name": "revoked"}] | None = ...,
        type: Literal[{"description": "The type of the public key is RSA", "help": "The type of the public key is RSA.", "label": "Rsa", "name": "RSA"}, {"description": "The type of the public key is DSA", "help": "The type of the public key is DSA.", "label": "Dsa", "name": "DSA"}, {"description": "The type of the public key is ECDSA", "help": "The type of the public key is ECDSA.", "label": "Ecdsa", "name": "ECDSA"}, {"description": "The type of the public key is ED25519", "help": "The type of the public key is ED25519.", "label": "Ed25519", "name": "ED25519"}, {"description": "The type of the public key is from RSA CA", "help": "The type of the public key is from RSA CA.", "label": "Rsa Ca", "name": "RSA-CA"}, {"description": "The type of the public key is from DSA CA", "help": "The type of the public key is from DSA CA.", "label": "Dsa Ca", "name": "DSA-CA"}, {"description": "The type of the public key is from ECDSA CA", "help": "The type of the public key is from ECDSA CA.", "label": "Ecdsa Ca", "name": "ECDSA-CA"}, {"description": "The type of the public key is from ED25519 CA", "help": "The type of the public key is from ED25519 CA.", "label": "Ed25519 Ca", "name": "ED25519-CA"}] | None = ...,
        nid: Literal[{"description": "The NID is ecdsa-sha2-nistp256", "help": "The NID is ecdsa-sha2-nistp256.", "label": "256", "name": "256"}, {"description": "The NID is ecdsa-sha2-nistp384", "help": "The NID is ecdsa-sha2-nistp384.", "label": "384", "name": "384"}, {"description": "The NID is ecdsa-sha2-nistp521", "help": "The NID is ecdsa-sha2-nistp521.", "label": "521", "name": "521"}] | None = ...,
        usage: Literal[{"description": "Transparent proxy uses this public key to validate server", "help": "Transparent proxy uses this public key to validate server.", "label": "Transparent Proxy", "name": "transparent-proxy"}, {"description": "Access proxy uses this public key to validate server", "help": "Access proxy uses this public key to validate server.", "label": "Access Proxy", "name": "access-proxy"}] | None = ...,
        ip: str | None = ...,
        port: int | None = ...,
        hostname: str | None = ...,
        public_key: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: HostKeyPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "The public key is trusted", "help": "The public key is trusted.", "label": "Trusted", "name": "trusted"}, {"description": "The public key is revoked", "help": "The public key is revoked.", "label": "Revoked", "name": "revoked"}] | None = ...,
        type: Literal[{"description": "The type of the public key is RSA", "help": "The type of the public key is RSA.", "label": "Rsa", "name": "RSA"}, {"description": "The type of the public key is DSA", "help": "The type of the public key is DSA.", "label": "Dsa", "name": "DSA"}, {"description": "The type of the public key is ECDSA", "help": "The type of the public key is ECDSA.", "label": "Ecdsa", "name": "ECDSA"}, {"description": "The type of the public key is ED25519", "help": "The type of the public key is ED25519.", "label": "Ed25519", "name": "ED25519"}, {"description": "The type of the public key is from RSA CA", "help": "The type of the public key is from RSA CA.", "label": "Rsa Ca", "name": "RSA-CA"}, {"description": "The type of the public key is from DSA CA", "help": "The type of the public key is from DSA CA.", "label": "Dsa Ca", "name": "DSA-CA"}, {"description": "The type of the public key is from ECDSA CA", "help": "The type of the public key is from ECDSA CA.", "label": "Ecdsa Ca", "name": "ECDSA-CA"}, {"description": "The type of the public key is from ED25519 CA", "help": "The type of the public key is from ED25519 CA.", "label": "Ed25519 Ca", "name": "ED25519-CA"}] | None = ...,
        nid: Literal[{"description": "The NID is ecdsa-sha2-nistp256", "help": "The NID is ecdsa-sha2-nistp256.", "label": "256", "name": "256"}, {"description": "The NID is ecdsa-sha2-nistp384", "help": "The NID is ecdsa-sha2-nistp384.", "label": "384", "name": "384"}, {"description": "The NID is ecdsa-sha2-nistp521", "help": "The NID is ecdsa-sha2-nistp521.", "label": "521", "name": "521"}] | None = ...,
        usage: Literal[{"description": "Transparent proxy uses this public key to validate server", "help": "Transparent proxy uses this public key to validate server.", "label": "Transparent Proxy", "name": "transparent-proxy"}, {"description": "Access proxy uses this public key to validate server", "help": "Access proxy uses this public key to validate server.", "label": "Access Proxy", "name": "access-proxy"}] | None = ...,
        ip: str | None = ...,
        port: int | None = ...,
        hostname: str | None = ...,
        public_key: str | None = ...,
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
        payload_dict: HostKeyPayload | None = ...,
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
    "HostKey",
    "HostKeyPayload",
]