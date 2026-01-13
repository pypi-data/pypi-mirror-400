from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class AddrgrpPayload(TypedDict, total=False):
    """
    Type hints for firewall/addrgrp payload fields.
    
    Configure IPv4 address groups.
    
    **Usage:**
        payload: AddrgrpPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Address group name.
    type: NotRequired[Literal[{"description": "Default address group type (address may belong to multiple groups)", "help": "Default address group type (address may belong to multiple groups).", "label": "Default", "name": "default"}, {"description": "Address folder group (members may not belong to any other group)", "help": "Address folder group (members may not belong to any other group).", "label": "Folder", "name": "folder"}]]  # Address group type.
    category: NotRequired[Literal[{"description": "Default address group category (cannot be used as ztna-ems-tag/ztna-geo-tag in policy)", "help": "Default address group category (cannot be used as ztna-ems-tag/ztna-geo-tag in policy).", "label": "Default", "name": "default"}, {"description": "Members must be ztna-ems-tag group or ems-tag address, can be used as ztna-ems-tag in policy", "help": "Members must be ztna-ems-tag group or ems-tag address, can be used as ztna-ems-tag in policy.", "label": "Ztna Ems Tag", "name": "ztna-ems-tag"}, {"description": "Members must be ztna-geo-tag group or geographic address, can be used as ztna-geo-tag in policy", "help": "Members must be ztna-geo-tag group or geographic address, can be used as ztna-geo-tag in policy.", "label": "Ztna Geo Tag", "name": "ztna-geo-tag"}]]  # Address group category.
    allow_routing: NotRequired[Literal[{"description": "Enable use of this group in routing configurations", "help": "Enable use of this group in routing configurations.", "label": "Enable", "name": "enable"}, {"description": "Disable use of this group in routing configurations", "help": "Disable use of this group in routing configurations.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of this group in routing configurations.
    member: NotRequired[list[dict[str, Any]]]  # Address objects contained within the group.
    comment: NotRequired[str]  # Comment.
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    exclude: NotRequired[Literal[{"description": "Enable address exclusion", "help": "Enable address exclusion.", "label": "Enable", "name": "enable"}, {"description": "Disable address exclusion", "help": "Disable address exclusion.", "label": "Disable", "name": "disable"}]]  # Enable/disable address exclusion.
    exclude_member: list[dict[str, Any]]  # Address exclusion member.
    color: NotRequired[int]  # Color of icon on the GUI.
    tagging: NotRequired[list[dict[str, Any]]]  # Config object tagging.
    fabric_object: NotRequired[Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}]]  # Security Fabric global object setting.


class Addrgrp:
    """
    Configure IPv4 address groups.
    
    Path: firewall/addrgrp
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
        payload_dict: AddrgrpPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "Default address group type (address may belong to multiple groups)", "help": "Default address group type (address may belong to multiple groups).", "label": "Default", "name": "default"}, {"description": "Address folder group (members may not belong to any other group)", "help": "Address folder group (members may not belong to any other group).", "label": "Folder", "name": "folder"}] | None = ...,
        category: Literal[{"description": "Default address group category (cannot be used as ztna-ems-tag/ztna-geo-tag in policy)", "help": "Default address group category (cannot be used as ztna-ems-tag/ztna-geo-tag in policy).", "label": "Default", "name": "default"}, {"description": "Members must be ztna-ems-tag group or ems-tag address, can be used as ztna-ems-tag in policy", "help": "Members must be ztna-ems-tag group or ems-tag address, can be used as ztna-ems-tag in policy.", "label": "Ztna Ems Tag", "name": "ztna-ems-tag"}, {"description": "Members must be ztna-geo-tag group or geographic address, can be used as ztna-geo-tag in policy", "help": "Members must be ztna-geo-tag group or geographic address, can be used as ztna-geo-tag in policy.", "label": "Ztna Geo Tag", "name": "ztna-geo-tag"}] | None = ...,
        allow_routing: Literal[{"description": "Enable use of this group in routing configurations", "help": "Enable use of this group in routing configurations.", "label": "Enable", "name": "enable"}, {"description": "Disable use of this group in routing configurations", "help": "Disable use of this group in routing configurations.", "label": "Disable", "name": "disable"}] | None = ...,
        member: list[dict[str, Any]] | None = ...,
        comment: str | None = ...,
        uuid: str | None = ...,
        exclude: Literal[{"description": "Enable address exclusion", "help": "Enable address exclusion.", "label": "Enable", "name": "enable"}, {"description": "Disable address exclusion", "help": "Disable address exclusion.", "label": "Disable", "name": "disable"}] | None = ...,
        exclude_member: list[dict[str, Any]] | None = ...,
        color: int | None = ...,
        tagging: list[dict[str, Any]] | None = ...,
        fabric_object: Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: AddrgrpPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "Default address group type (address may belong to multiple groups)", "help": "Default address group type (address may belong to multiple groups).", "label": "Default", "name": "default"}, {"description": "Address folder group (members may not belong to any other group)", "help": "Address folder group (members may not belong to any other group).", "label": "Folder", "name": "folder"}] | None = ...,
        category: Literal[{"description": "Default address group category (cannot be used as ztna-ems-tag/ztna-geo-tag in policy)", "help": "Default address group category (cannot be used as ztna-ems-tag/ztna-geo-tag in policy).", "label": "Default", "name": "default"}, {"description": "Members must be ztna-ems-tag group or ems-tag address, can be used as ztna-ems-tag in policy", "help": "Members must be ztna-ems-tag group or ems-tag address, can be used as ztna-ems-tag in policy.", "label": "Ztna Ems Tag", "name": "ztna-ems-tag"}, {"description": "Members must be ztna-geo-tag group or geographic address, can be used as ztna-geo-tag in policy", "help": "Members must be ztna-geo-tag group or geographic address, can be used as ztna-geo-tag in policy.", "label": "Ztna Geo Tag", "name": "ztna-geo-tag"}] | None = ...,
        allow_routing: Literal[{"description": "Enable use of this group in routing configurations", "help": "Enable use of this group in routing configurations.", "label": "Enable", "name": "enable"}, {"description": "Disable use of this group in routing configurations", "help": "Disable use of this group in routing configurations.", "label": "Disable", "name": "disable"}] | None = ...,
        member: list[dict[str, Any]] | None = ...,
        comment: str | None = ...,
        uuid: str | None = ...,
        exclude: Literal[{"description": "Enable address exclusion", "help": "Enable address exclusion.", "label": "Enable", "name": "enable"}, {"description": "Disable address exclusion", "help": "Disable address exclusion.", "label": "Disable", "name": "disable"}] | None = ...,
        exclude_member: list[dict[str, Any]] | None = ...,
        color: int | None = ...,
        tagging: list[dict[str, Any]] | None = ...,
        fabric_object: Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: AddrgrpPayload | None = ...,
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
    "Addrgrp",
    "AddrgrpPayload",
]