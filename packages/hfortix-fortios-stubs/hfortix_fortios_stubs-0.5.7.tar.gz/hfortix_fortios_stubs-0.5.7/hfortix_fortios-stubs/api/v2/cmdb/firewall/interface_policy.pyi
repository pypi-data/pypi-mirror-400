from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class InterfacePolicyPayload(TypedDict, total=False):
    """
    Type hints for firewall/interface_policy payload fields.
    
    Configure IPv4 interface policies.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.antivirus.profile.ProfileEndpoint` (via: av-profile)
        - :class:`~.application.list.ListEndpoint` (via: application-list)
        - :class:`~.casb.profile.ProfileEndpoint` (via: casb-profile)
        - :class:`~.dlp.profile.ProfileEndpoint` (via: dlp-profile)
        - :class:`~.emailfilter.profile.ProfileEndpoint` (via: emailfilter-profile)
        - :class:`~.ips.sensor.SensorEndpoint` (via: ips-sensor)
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)
        - :class:`~.system.sdwan.zone.ZoneEndpoint` (via: interface)
        - :class:`~.system.zone.ZoneEndpoint` (via: interface)
        - :class:`~.webfilter.profile.ProfileEndpoint` (via: webfilter-profile)

    **Usage:**
        payload: InterfacePolicyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    policyid: NotRequired[int]  # Policy ID (0 - 4294967295).
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    status: NotRequired[Literal[{"description": "Enable this policy", "help": "Enable this policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy", "help": "Disable this policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable this policy.
    comments: NotRequired[str]  # Comments.
    logtraffic: NotRequired[Literal[{"description": "Log all sessions accepted or denied by this policy", "help": "Log all sessions accepted or denied by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}]]  # Logging type to be used in this policy (Options: all | utm |
    interface: str  # Monitored interface name from available interfaces.
    srcaddr: list[dict[str, Any]]  # Address object to limit traffic monitoring to network traffi
    dstaddr: list[dict[str, Any]]  # Address object to limit traffic monitoring to network traffi
    service: list[dict[str, Any]]  # Service object from available options.
    application_list_status: NotRequired[Literal[{"description": "Enable application control    disable:Disable application control", "help": "Enable application control", "label": "Enable", "name": "enable"}, {"help": "Disable application control", "label": "Disable", "name": "disable"}]]  # Enable/disable application control.
    application_list: str  # Application list name.
    ips_sensor_status: NotRequired[Literal[{"description": "Enable IPS", "help": "Enable IPS.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS", "help": "Disable IPS.", "label": "Disable", "name": "disable"}]]  # Enable/disable IPS.
    ips_sensor: str  # IPS sensor name.
    dsri: NotRequired[Literal[{"description": "Enable DSRI", "help": "Enable DSRI.", "label": "Enable", "name": "enable"}, {"description": "Disable DSRI", "help": "Disable DSRI.", "label": "Disable", "name": "disable"}]]  # Enable/disable DSRI.
    av_profile_status: NotRequired[Literal[{"description": "Enable antivirus    disable:Disable antivirus", "help": "Enable antivirus", "label": "Enable", "name": "enable"}, {"help": "Disable antivirus", "label": "Disable", "name": "disable"}]]  # Enable/disable antivirus.
    av_profile: str  # Antivirus profile.
    webfilter_profile_status: NotRequired[Literal[{"description": "Enable web filtering", "help": "Enable web filtering.", "label": "Enable", "name": "enable"}, {"description": "Disable web filtering", "help": "Disable web filtering.", "label": "Disable", "name": "disable"}]]  # Enable/disable web filtering.
    webfilter_profile: str  # Web filter profile.
    casb_profile_status: NotRequired[Literal[{"description": "Enable CASB", "help": "Enable CASB.", "label": "Enable", "name": "enable"}, {"description": "Disable CASB", "help": "Disable CASB.", "label": "Disable", "name": "disable"}]]  # Enable/disable CASB.
    casb_profile: str  # CASB profile.
    emailfilter_profile_status: NotRequired[Literal[{"description": "Enable Email filter", "help": "Enable Email filter.", "label": "Enable", "name": "enable"}, {"description": "Disable Email filter", "help": "Disable Email filter.", "label": "Disable", "name": "disable"}]]  # Enable/disable email filter.
    emailfilter_profile: str  # Email filter profile.
    dlp_profile_status: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable DLP.
    dlp_profile: str  # DLP profile name.


class InterfacePolicy:
    """
    Configure IPv4 interface policies.
    
    Path: firewall/interface_policy
    Category: cmdb
    Primary Key: policyid
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        policyid: int | None = ...,
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
        policyid: int,
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
        policyid: int | None = ...,
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
        policyid: int | None = ...,
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
        policyid: int | None = ...,
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
        payload_dict: InterfacePolicyPayload | None = ...,
        policyid: int | None = ...,
        uuid: str | None = ...,
        status: Literal[{"description": "Enable this policy", "help": "Enable this policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy", "help": "Disable this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        comments: str | None = ...,
        logtraffic: Literal[{"description": "Log all sessions accepted or denied by this policy", "help": "Log all sessions accepted or denied by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        interface: str | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        application_list_status: Literal[{"description": "Enable application control    disable:Disable application control", "help": "Enable application control", "label": "Enable", "name": "enable"}, {"help": "Disable application control", "label": "Disable", "name": "disable"}] | None = ...,
        application_list: str | None = ...,
        ips_sensor_status: Literal[{"description": "Enable IPS", "help": "Enable IPS.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS", "help": "Disable IPS.", "label": "Disable", "name": "disable"}] | None = ...,
        ips_sensor: str | None = ...,
        dsri: Literal[{"description": "Enable DSRI", "help": "Enable DSRI.", "label": "Enable", "name": "enable"}, {"description": "Disable DSRI", "help": "Disable DSRI.", "label": "Disable", "name": "disable"}] | None = ...,
        av_profile_status: Literal[{"description": "Enable antivirus    disable:Disable antivirus", "help": "Enable antivirus", "label": "Enable", "name": "enable"}, {"help": "Disable antivirus", "label": "Disable", "name": "disable"}] | None = ...,
        av_profile: str | None = ...,
        webfilter_profile_status: Literal[{"description": "Enable web filtering", "help": "Enable web filtering.", "label": "Enable", "name": "enable"}, {"description": "Disable web filtering", "help": "Disable web filtering.", "label": "Disable", "name": "disable"}] | None = ...,
        webfilter_profile: str | None = ...,
        casb_profile_status: Literal[{"description": "Enable CASB", "help": "Enable CASB.", "label": "Enable", "name": "enable"}, {"description": "Disable CASB", "help": "Disable CASB.", "label": "Disable", "name": "disable"}] | None = ...,
        casb_profile: str | None = ...,
        emailfilter_profile_status: Literal[{"description": "Enable Email filter", "help": "Enable Email filter.", "label": "Enable", "name": "enable"}, {"description": "Disable Email filter", "help": "Disable Email filter.", "label": "Disable", "name": "disable"}] | None = ...,
        emailfilter_profile: str | None = ...,
        dlp_profile_status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        dlp_profile: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: InterfacePolicyPayload | None = ...,
        policyid: int | None = ...,
        uuid: str | None = ...,
        status: Literal[{"description": "Enable this policy", "help": "Enable this policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this policy", "help": "Disable this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        comments: str | None = ...,
        logtraffic: Literal[{"description": "Log all sessions accepted or denied by this policy", "help": "Log all sessions accepted or denied by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        interface: str | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        application_list_status: Literal[{"description": "Enable application control    disable:Disable application control", "help": "Enable application control", "label": "Enable", "name": "enable"}, {"help": "Disable application control", "label": "Disable", "name": "disable"}] | None = ...,
        application_list: str | None = ...,
        ips_sensor_status: Literal[{"description": "Enable IPS", "help": "Enable IPS.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS", "help": "Disable IPS.", "label": "Disable", "name": "disable"}] | None = ...,
        ips_sensor: str | None = ...,
        dsri: Literal[{"description": "Enable DSRI", "help": "Enable DSRI.", "label": "Enable", "name": "enable"}, {"description": "Disable DSRI", "help": "Disable DSRI.", "label": "Disable", "name": "disable"}] | None = ...,
        av_profile_status: Literal[{"description": "Enable antivirus    disable:Disable antivirus", "help": "Enable antivirus", "label": "Enable", "name": "enable"}, {"help": "Disable antivirus", "label": "Disable", "name": "disable"}] | None = ...,
        av_profile: str | None = ...,
        webfilter_profile_status: Literal[{"description": "Enable web filtering", "help": "Enable web filtering.", "label": "Enable", "name": "enable"}, {"description": "Disable web filtering", "help": "Disable web filtering.", "label": "Disable", "name": "disable"}] | None = ...,
        webfilter_profile: str | None = ...,
        casb_profile_status: Literal[{"description": "Enable CASB", "help": "Enable CASB.", "label": "Enable", "name": "enable"}, {"description": "Disable CASB", "help": "Disable CASB.", "label": "Disable", "name": "disable"}] | None = ...,
        casb_profile: str | None = ...,
        emailfilter_profile_status: Literal[{"description": "Enable Email filter", "help": "Enable Email filter.", "label": "Enable", "name": "enable"}, {"description": "Disable Email filter", "help": "Disable Email filter.", "label": "Disable", "name": "disable"}] | None = ...,
        emailfilter_profile: str | None = ...,
        dlp_profile_status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        dlp_profile: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        policyid: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        policyid: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: InterfacePolicyPayload | None = ...,
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
    "InterfacePolicy",
    "InterfacePolicyPayload",
]