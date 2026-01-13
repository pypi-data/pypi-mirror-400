from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SecurityPolicyPayload(TypedDict, total=False):
    """
    Type hints for firewall/security_policy payload fields.
    
    Configure NGFW IPv4/IPv6 application policies.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.antivirus.profile.ProfileEndpoint` (via: av-profile)
        - :class:`~.application.list.ListEndpoint` (via: application-list)
        - :class:`~.casb.profile.ProfileEndpoint` (via: casb-profile)
        - :class:`~.diameter-filter.profile.ProfileEndpoint` (via: diameter-filter-profile)
        - :class:`~.dlp.profile.ProfileEndpoint` (via: dlp-profile)
        - :class:`~.dnsfilter.profile.ProfileEndpoint` (via: dnsfilter-profile)
        - :class:`~.emailfilter.profile.ProfileEndpoint` (via: emailfilter-profile)
        - :class:`~.file-filter.profile.ProfileEndpoint` (via: file-filter-profile)
        - :class:`~.firewall.profile-group.ProfileGroupEndpoint` (via: profile-group)
        - :class:`~.firewall.profile-protocol-options.ProfileProtocolOptionsEndpoint` (via: profile-protocol-options)
        - ... and 12 more dependencies

    **Usage:**
        payload: SecurityPolicyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    policyid: NotRequired[int]  # Policy ID.
    name: NotRequired[str]  # Policy name.
    comments: NotRequired[str]  # Comment.
    srcintf: list[dict[str, Any]]  # Incoming (ingress) interface.
    dstintf: list[dict[str, Any]]  # Outgoing (egress) interface.
    srcaddr: NotRequired[list[dict[str, Any]]]  # Source IPv4 address name and address group names.
    srcaddr_negate: NotRequired[Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negate", "help": "Disable source address negate.", "label": "Disable", "name": "disable"}]]  # When enabled srcaddr specifies what the source address must 
    dstaddr: NotRequired[list[dict[str, Any]]]  # Destination IPv4 address name and address group names.
    dstaddr_negate: NotRequired[Literal[{"description": "Enable destination address negate", "help": "Enable destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}]]  # When enabled dstaddr specifies what the destination address 
    srcaddr6: NotRequired[list[dict[str, Any]]]  # Source IPv6 address name and address group names.
    srcaddr6_negate: NotRequired[Literal[{"description": "Enable IPv6 source address negate", "help": "Enable IPv6 source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 source address negate", "help": "Disable IPv6 source address negate.", "label": "Disable", "name": "disable"}]]  # When enabled srcaddr6 specifies what the source address must
    dstaddr6: NotRequired[list[dict[str, Any]]]  # Destination IPv6 address name and address group names.
    dstaddr6_negate: NotRequired[Literal[{"description": "Enable IPv6 destination address negate", "help": "Enable IPv6 destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 destination address negate", "help": "Disable IPv6 destination address negate.", "label": "Disable", "name": "disable"}]]  # When enabled dstaddr6 specifies what the destination address
    internet_service: NotRequired[Literal[{"description": "Enable use of Internet Services in policy", "help": "Enable use of Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services in policy", "help": "Disable use of Internet Services in policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of Internet Services for this policy. If 
    internet_service_name: NotRequired[list[dict[str, Any]]]  # Internet Service name.
    internet_service_negate: NotRequired[Literal[{"description": "Enable negated Internet Service match", "help": "Enable negated Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service match", "help": "Disable negated Internet Service match.", "label": "Disable", "name": "disable"}]]  # When enabled internet-service specifies what the service mus
    internet_service_group: NotRequired[list[dict[str, Any]]]  # Internet Service group name.
    internet_service_custom: NotRequired[list[dict[str, Any]]]  # Custom Internet Service name.
    internet_service_custom_group: NotRequired[list[dict[str, Any]]]  # Custom Internet Service group name.
    internet_service_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard Internet Service name.
    internet_service_src: NotRequired[Literal[{"description": "Enable use of Internet Services source in policy", "help": "Enable use of Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services source in policy", "help": "Disable use of Internet Services source in policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of Internet Services in source for this p
    internet_service_src_name: NotRequired[list[dict[str, Any]]]  # Internet Service source name.
    internet_service_src_negate: NotRequired[Literal[{"description": "Enable negated Internet Service source match", "help": "Enable negated Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service source match", "help": "Disable negated Internet Service source match.", "label": "Disable", "name": "disable"}]]  # When enabled internet-service-src specifies what the service
    internet_service_src_group: NotRequired[list[dict[str, Any]]]  # Internet Service source group name.
    internet_service_src_custom: NotRequired[list[dict[str, Any]]]  # Custom Internet Service source name.
    internet_service_src_custom_group: NotRequired[list[dict[str, Any]]]  # Custom Internet Service source group name.
    internet_service_src_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard Internet Service source name.
    internet_service6: NotRequired[Literal[{"description": "Enable use of IPv6 Internet Services in policy", "help": "Enable use of IPv6 Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services in policy", "help": "Disable use of IPv6 Internet Services in policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of IPv6 Internet Services for this policy
    internet_service6_name: NotRequired[list[dict[str, Any]]]  # IPv6 Internet Service name.
    internet_service6_negate: NotRequired[Literal[{"description": "Enable negated IPv6 Internet Service match", "help": "Enable negated IPv6 Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service match", "help": "Disable negated IPv6 Internet Service match.", "label": "Disable", "name": "disable"}]]  # When enabled internet-service6 specifies what the service mu
    internet_service6_group: NotRequired[list[dict[str, Any]]]  # Internet Service group name.
    internet_service6_custom: NotRequired[list[dict[str, Any]]]  # Custom IPv6 Internet Service name.
    internet_service6_custom_group: NotRequired[list[dict[str, Any]]]  # Custom IPv6 Internet Service group name.
    internet_service6_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard IPv6 Internet Service name.
    internet_service6_src: NotRequired[Literal[{"description": "Enable use of IPv6 Internet Services source in policy", "help": "Enable use of IPv6 Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services source in policy", "help": "Disable use of IPv6 Internet Services source in policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of IPv6 Internet Services in source for t
    internet_service6_src_name: NotRequired[list[dict[str, Any]]]  # IPv6 Internet Service source name.
    internet_service6_src_negate: NotRequired[Literal[{"description": "Enable negated IPv6 Internet Service source match", "help": "Enable negated IPv6 Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service source match", "help": "Disable negated IPv6 Internet Service source match.", "label": "Disable", "name": "disable"}]]  # When enabled internet-service6-src specifies what the servic
    internet_service6_src_group: NotRequired[list[dict[str, Any]]]  # Internet Service6 source group name.
    internet_service6_src_custom: NotRequired[list[dict[str, Any]]]  # Custom IPv6 Internet Service source name.
    internet_service6_src_custom_group: NotRequired[list[dict[str, Any]]]  # Custom Internet Service6 source group name.
    internet_service6_src_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard IPv6 Internet Service source name.
    enforce_default_app_port: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable default application port enforcement for allo
    service: NotRequired[list[dict[str, Any]]]  # Service and service group names.
    service_negate: NotRequired[Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}]]  # When enabled service specifies what the service must NOT be.
    action: NotRequired[Literal[{"description": "Allows session that match the firewall policy", "help": "Allows session that match the firewall policy.", "label": "Accept", "name": "accept"}, {"description": "Blocks sessions that match the firewall policy", "help": "Blocks sessions that match the firewall policy.", "label": "Deny", "name": "deny"}]]  # Policy action (accept/deny).
    send_deny_packet: NotRequired[Literal[{"description": "Disable deny-packet sending", "help": "Disable deny-packet sending.", "label": "Disable", "name": "disable"}, {"description": "Enable deny-packet sending", "help": "Enable deny-packet sending.", "label": "Enable", "name": "enable"}]]  # Enable to send a reply when a session is denied or blocked b
    schedule: str  # Schedule name.
    status: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable or disable this policy.
    logtraffic: NotRequired[Literal[{"description": "Log all sessions accepted or denied by this policy", "help": "Log all sessions accepted or denied by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}]]  # Enable or disable logging. Log all sessions or security prof
    learning_mode: NotRequired[Literal[{"description": "Enable learning mode", "help": "Enable learning mode.", "label": "Enable", "name": "enable"}, {"description": "Disable learning mode", "help": "Disable learning mode.", "label": "Disable", "name": "disable"}]]  # Enable to allow everything, but log all of the meaningful da
    nat46: NotRequired[Literal[{"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}]]  # Enable/disable NAT46.
    nat64: NotRequired[Literal[{"description": "Enable NAT64", "help": "Enable NAT64.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT64", "help": "Disable NAT64.", "label": "Disable", "name": "disable"}]]  # Enable/disable NAT64.
    profile_type: NotRequired[Literal[{"description": "Do not allow security profile groups", "help": "Do not allow security profile groups.", "label": "Single", "name": "single"}, {"description": "Allow security profile groups", "help": "Allow security profile groups.", "label": "Group", "name": "group"}]]  # Determine whether the firewall policy allows security profil
    profile_group: NotRequired[str]  # Name of profile group.
    profile_protocol_options: NotRequired[str]  # Name of an existing Protocol options profile.
    ssl_ssh_profile: NotRequired[str]  # Name of an existing SSL SSH profile.
    av_profile: NotRequired[str]  # Name of an existing Antivirus profile.
    webfilter_profile: NotRequired[str]  # Name of an existing Web filter profile.
    dnsfilter_profile: NotRequired[str]  # Name of an existing DNS filter profile.
    emailfilter_profile: NotRequired[str]  # Name of an existing email filter profile.
    dlp_profile: NotRequired[str]  # Name of an existing DLP profile.
    file_filter_profile: NotRequired[str]  # Name of an existing file-filter profile.
    ips_sensor: NotRequired[str]  # Name of an existing IPS sensor.
    application_list: NotRequired[str]  # Name of an existing Application list.
    voip_profile: NotRequired[str]  # Name of an existing VoIP (voipd) profile.
    ips_voip_filter: NotRequired[str]  # Name of an existing VoIP (ips) profile.
    sctp_filter_profile: NotRequired[str]  # Name of an existing SCTP filter profile.
    diameter_filter_profile: NotRequired[str]  # Name of an existing Diameter filter profile.
    virtual_patch_profile: NotRequired[str]  # Name of an existing virtual-patch profile.
    icap_profile: NotRequired[str]  # Name of an existing ICAP profile.
    videofilter_profile: NotRequired[str]  # Name of an existing VideoFilter profile.
    ssh_filter_profile: NotRequired[str]  # Name of an existing SSH filter profile.
    casb_profile: NotRequired[str]  # Name of an existing CASB profile.
    application: NotRequired[list[dict[str, Any]]]  # Application ID list.
    app_category: NotRequired[list[dict[str, Any]]]  # Application category ID list.
    url_category: NotRequired[list[dict[str, Any]]]  # URL categories or groups.
    app_group: NotRequired[list[dict[str, Any]]]  # Application group names.
    groups: NotRequired[list[dict[str, Any]]]  # Names of user groups that can authenticate with this policy.
    users: NotRequired[list[dict[str, Any]]]  # Names of individual users that can authenticate with this po
    fsso_groups: NotRequired[list[dict[str, Any]]]  # Names of FSSO groups.


class SecurityPolicy:
    """
    Configure NGFW IPv4/IPv6 application policies.
    
    Path: firewall/security_policy
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
        payload_dict: SecurityPolicyPayload | None = ...,
        uuid: str | None = ...,
        policyid: int | None = ...,
        name: str | None = ...,
        comments: str | None = ...,
        srcintf: list[dict[str, Any]] | None = ...,
        dstintf: list[dict[str, Any]] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        srcaddr_negate: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negate", "help": "Disable source address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        dstaddr_negate: Literal[{"description": "Enable destination address negate", "help": "Enable destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        srcaddr6: list[dict[str, Any]] | None = ...,
        srcaddr6_negate: Literal[{"description": "Enable IPv6 source address negate", "help": "Enable IPv6 source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 source address negate", "help": "Disable IPv6 source address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        dstaddr6: list[dict[str, Any]] | None = ...,
        dstaddr6_negate: Literal[{"description": "Enable IPv6 destination address negate", "help": "Enable IPv6 destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 destination address negate", "help": "Disable IPv6 destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service: Literal[{"description": "Enable use of Internet Services in policy", "help": "Enable use of Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services in policy", "help": "Disable use of Internet Services in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_name: list[dict[str, Any]] | None = ...,
        internet_service_negate: Literal[{"description": "Enable negated Internet Service match", "help": "Enable negated Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service match", "help": "Disable negated Internet Service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_group: list[dict[str, Any]] | None = ...,
        internet_service_custom: list[dict[str, Any]] | None = ...,
        internet_service_custom_group: list[dict[str, Any]] | None = ...,
        internet_service_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service_src: Literal[{"description": "Enable use of Internet Services source in policy", "help": "Enable use of Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services source in policy", "help": "Disable use of Internet Services source in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_src_name: list[dict[str, Any]] | None = ...,
        internet_service_src_negate: Literal[{"description": "Enable negated Internet Service source match", "help": "Enable negated Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service source match", "help": "Disable negated Internet Service source match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_src_group: list[dict[str, Any]] | None = ...,
        internet_service_src_custom: list[dict[str, Any]] | None = ...,
        internet_service_src_custom_group: list[dict[str, Any]] | None = ...,
        internet_service_src_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service6: Literal[{"description": "Enable use of IPv6 Internet Services in policy", "help": "Enable use of IPv6 Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services in policy", "help": "Disable use of IPv6 Internet Services in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_name: list[dict[str, Any]] | None = ...,
        internet_service6_negate: Literal[{"description": "Enable negated IPv6 Internet Service match", "help": "Enable negated IPv6 Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service match", "help": "Disable negated IPv6 Internet Service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_group: list[dict[str, Any]] | None = ...,
        internet_service6_custom: list[dict[str, Any]] | None = ...,
        internet_service6_custom_group: list[dict[str, Any]] | None = ...,
        internet_service6_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service6_src: Literal[{"description": "Enable use of IPv6 Internet Services source in policy", "help": "Enable use of IPv6 Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services source in policy", "help": "Disable use of IPv6 Internet Services source in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_src_name: list[dict[str, Any]] | None = ...,
        internet_service6_src_negate: Literal[{"description": "Enable negated IPv6 Internet Service source match", "help": "Enable negated IPv6 Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service source match", "help": "Disable negated IPv6 Internet Service source match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_src_group: list[dict[str, Any]] | None = ...,
        internet_service6_src_custom: list[dict[str, Any]] | None = ...,
        internet_service6_src_custom_group: list[dict[str, Any]] | None = ...,
        internet_service6_src_fortiguard: list[dict[str, Any]] | None = ...,
        enforce_default_app_port: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        service_negate: Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}] | None = ...,
        action: Literal[{"description": "Allows session that match the firewall policy", "help": "Allows session that match the firewall policy.", "label": "Accept", "name": "accept"}, {"description": "Blocks sessions that match the firewall policy", "help": "Blocks sessions that match the firewall policy.", "label": "Deny", "name": "deny"}] | None = ...,
        send_deny_packet: Literal[{"description": "Disable deny-packet sending", "help": "Disable deny-packet sending.", "label": "Disable", "name": "disable"}, {"description": "Enable deny-packet sending", "help": "Enable deny-packet sending.", "label": "Enable", "name": "enable"}] | None = ...,
        schedule: str | None = ...,
        status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        logtraffic: Literal[{"description": "Log all sessions accepted or denied by this policy", "help": "Log all sessions accepted or denied by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        learning_mode: Literal[{"description": "Enable learning mode", "help": "Enable learning mode.", "label": "Enable", "name": "enable"}, {"description": "Disable learning mode", "help": "Disable learning mode.", "label": "Disable", "name": "disable"}] | None = ...,
        nat46: Literal[{"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}] | None = ...,
        nat64: Literal[{"description": "Enable NAT64", "help": "Enable NAT64.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT64", "help": "Disable NAT64.", "label": "Disable", "name": "disable"}] | None = ...,
        profile_type: Literal[{"description": "Do not allow security profile groups", "help": "Do not allow security profile groups.", "label": "Single", "name": "single"}, {"description": "Allow security profile groups", "help": "Allow security profile groups.", "label": "Group", "name": "group"}] | None = ...,
        profile_group: str | None = ...,
        profile_protocol_options: str | None = ...,
        ssl_ssh_profile: str | None = ...,
        av_profile: str | None = ...,
        webfilter_profile: str | None = ...,
        dnsfilter_profile: str | None = ...,
        emailfilter_profile: str | None = ...,
        dlp_profile: str | None = ...,
        file_filter_profile: str | None = ...,
        ips_sensor: str | None = ...,
        application_list: str | None = ...,
        voip_profile: str | None = ...,
        ips_voip_filter: str | None = ...,
        sctp_filter_profile: str | None = ...,
        diameter_filter_profile: str | None = ...,
        virtual_patch_profile: str | None = ...,
        icap_profile: str | None = ...,
        videofilter_profile: str | None = ...,
        ssh_filter_profile: str | None = ...,
        casb_profile: str | None = ...,
        application: list[dict[str, Any]] | None = ...,
        app_category: list[dict[str, Any]] | None = ...,
        url_category: list[dict[str, Any]] | None = ...,
        app_group: list[dict[str, Any]] | None = ...,
        groups: list[dict[str, Any]] | None = ...,
        users: list[dict[str, Any]] | None = ...,
        fsso_groups: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SecurityPolicyPayload | None = ...,
        uuid: str | None = ...,
        policyid: int | None = ...,
        name: str | None = ...,
        comments: str | None = ...,
        srcintf: list[dict[str, Any]] | None = ...,
        dstintf: list[dict[str, Any]] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        srcaddr_negate: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negate", "help": "Disable source address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        dstaddr_negate: Literal[{"description": "Enable destination address negate", "help": "Enable destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        srcaddr6: list[dict[str, Any]] | None = ...,
        srcaddr6_negate: Literal[{"description": "Enable IPv6 source address negate", "help": "Enable IPv6 source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 source address negate", "help": "Disable IPv6 source address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        dstaddr6: list[dict[str, Any]] | None = ...,
        dstaddr6_negate: Literal[{"description": "Enable IPv6 destination address negate", "help": "Enable IPv6 destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 destination address negate", "help": "Disable IPv6 destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service: Literal[{"description": "Enable use of Internet Services in policy", "help": "Enable use of Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services in policy", "help": "Disable use of Internet Services in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_name: list[dict[str, Any]] | None = ...,
        internet_service_negate: Literal[{"description": "Enable negated Internet Service match", "help": "Enable negated Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service match", "help": "Disable negated Internet Service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_group: list[dict[str, Any]] | None = ...,
        internet_service_custom: list[dict[str, Any]] | None = ...,
        internet_service_custom_group: list[dict[str, Any]] | None = ...,
        internet_service_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service_src: Literal[{"description": "Enable use of Internet Services source in policy", "help": "Enable use of Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services source in policy", "help": "Disable use of Internet Services source in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_src_name: list[dict[str, Any]] | None = ...,
        internet_service_src_negate: Literal[{"description": "Enable negated Internet Service source match", "help": "Enable negated Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service source match", "help": "Disable negated Internet Service source match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_src_group: list[dict[str, Any]] | None = ...,
        internet_service_src_custom: list[dict[str, Any]] | None = ...,
        internet_service_src_custom_group: list[dict[str, Any]] | None = ...,
        internet_service_src_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service6: Literal[{"description": "Enable use of IPv6 Internet Services in policy", "help": "Enable use of IPv6 Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services in policy", "help": "Disable use of IPv6 Internet Services in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_name: list[dict[str, Any]] | None = ...,
        internet_service6_negate: Literal[{"description": "Enable negated IPv6 Internet Service match", "help": "Enable negated IPv6 Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service match", "help": "Disable negated IPv6 Internet Service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_group: list[dict[str, Any]] | None = ...,
        internet_service6_custom: list[dict[str, Any]] | None = ...,
        internet_service6_custom_group: list[dict[str, Any]] | None = ...,
        internet_service6_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service6_src: Literal[{"description": "Enable use of IPv6 Internet Services source in policy", "help": "Enable use of IPv6 Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services source in policy", "help": "Disable use of IPv6 Internet Services source in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_src_name: list[dict[str, Any]] | None = ...,
        internet_service6_src_negate: Literal[{"description": "Enable negated IPv6 Internet Service source match", "help": "Enable negated IPv6 Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service source match", "help": "Disable negated IPv6 Internet Service source match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_src_group: list[dict[str, Any]] | None = ...,
        internet_service6_src_custom: list[dict[str, Any]] | None = ...,
        internet_service6_src_custom_group: list[dict[str, Any]] | None = ...,
        internet_service6_src_fortiguard: list[dict[str, Any]] | None = ...,
        enforce_default_app_port: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        service_negate: Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}] | None = ...,
        action: Literal[{"description": "Allows session that match the firewall policy", "help": "Allows session that match the firewall policy.", "label": "Accept", "name": "accept"}, {"description": "Blocks sessions that match the firewall policy", "help": "Blocks sessions that match the firewall policy.", "label": "Deny", "name": "deny"}] | None = ...,
        send_deny_packet: Literal[{"description": "Disable deny-packet sending", "help": "Disable deny-packet sending.", "label": "Disable", "name": "disable"}, {"description": "Enable deny-packet sending", "help": "Enable deny-packet sending.", "label": "Enable", "name": "enable"}] | None = ...,
        schedule: str | None = ...,
        status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        logtraffic: Literal[{"description": "Log all sessions accepted or denied by this policy", "help": "Log all sessions accepted or denied by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        learning_mode: Literal[{"description": "Enable learning mode", "help": "Enable learning mode.", "label": "Enable", "name": "enable"}, {"description": "Disable learning mode", "help": "Disable learning mode.", "label": "Disable", "name": "disable"}] | None = ...,
        nat46: Literal[{"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}] | None = ...,
        nat64: Literal[{"description": "Enable NAT64", "help": "Enable NAT64.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT64", "help": "Disable NAT64.", "label": "Disable", "name": "disable"}] | None = ...,
        profile_type: Literal[{"description": "Do not allow security profile groups", "help": "Do not allow security profile groups.", "label": "Single", "name": "single"}, {"description": "Allow security profile groups", "help": "Allow security profile groups.", "label": "Group", "name": "group"}] | None = ...,
        profile_group: str | None = ...,
        profile_protocol_options: str | None = ...,
        ssl_ssh_profile: str | None = ...,
        av_profile: str | None = ...,
        webfilter_profile: str | None = ...,
        dnsfilter_profile: str | None = ...,
        emailfilter_profile: str | None = ...,
        dlp_profile: str | None = ...,
        file_filter_profile: str | None = ...,
        ips_sensor: str | None = ...,
        application_list: str | None = ...,
        voip_profile: str | None = ...,
        ips_voip_filter: str | None = ...,
        sctp_filter_profile: str | None = ...,
        diameter_filter_profile: str | None = ...,
        virtual_patch_profile: str | None = ...,
        icap_profile: str | None = ...,
        videofilter_profile: str | None = ...,
        ssh_filter_profile: str | None = ...,
        casb_profile: str | None = ...,
        application: list[dict[str, Any]] | None = ...,
        app_category: list[dict[str, Any]] | None = ...,
        url_category: list[dict[str, Any]] | None = ...,
        app_group: list[dict[str, Any]] | None = ...,
        groups: list[dict[str, Any]] | None = ...,
        users: list[dict[str, Any]] | None = ...,
        fsso_groups: list[dict[str, Any]] | None = ...,
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
        payload_dict: SecurityPolicyPayload | None = ...,
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
    "SecurityPolicy",
    "SecurityPolicyPayload",
]