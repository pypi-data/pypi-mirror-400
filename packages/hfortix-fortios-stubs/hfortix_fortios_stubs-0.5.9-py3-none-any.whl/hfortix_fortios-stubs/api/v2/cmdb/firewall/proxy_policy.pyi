from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ProxyPolicyPayload(TypedDict, total=False):
    """
    Type hints for firewall/proxy_policy payload fields.
    
    Configure proxy policies.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.antivirus.profile.ProfileEndpoint` (via: av-profile)
        - :class:`~.application.list.ListEndpoint` (via: application-list)
        - :class:`~.casb.profile.ProfileEndpoint` (via: casb-profile)
        - :class:`~.dlp.profile.ProfileEndpoint` (via: dlp-profile)
        - :class:`~.dnsfilter.profile.ProfileEndpoint` (via: dnsfilter-profile)
        - :class:`~.emailfilter.profile.ProfileEndpoint` (via: emailfilter-profile)
        - :class:`~.file-filter.profile.ProfileEndpoint` (via: file-filter-profile)
        - :class:`~.firewall.decrypted-traffic-mirror.DecryptedTrafficMirrorEndpoint` (via: decrypted-traffic-mirror)
        - :class:`~.firewall.profile-group.ProfileGroupEndpoint` (via: profile-group)
        - :class:`~.firewall.profile-protocol-options.ProfileProtocolOptionsEndpoint` (via: profile-protocol-options)
        - ... and 17 more dependencies

    **Usage:**
        payload: ProxyPolicyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    policyid: NotRequired[int]  # Policy ID.
    name: NotRequired[str]  # Policy name.
    proxy: Literal[{"description": "Explicit Web Proxy    transparent-web:Transparent Web Proxy    ftp:Explicit FTP Proxy    ssh:SSH Proxy    ssh-tunnel:SSH Tunnel    access-proxy:Access Proxy    ztna-proxy:ZTNA Proxy", "help": "Explicit Web Proxy", "label": "Explicit Web", "name": "explicit-web"}, {"help": "Transparent Web Proxy", "label": "Transparent Web", "name": "transparent-web"}, {"help": "Explicit FTP Proxy", "label": "Ftp", "name": "ftp"}, {"help": "SSH Proxy", "label": "Ssh", "name": "ssh"}, {"help": "SSH Tunnel", "label": "Ssh Tunnel", "name": "ssh-tunnel"}, {"help": "Access Proxy", "label": "Access Proxy", "name": "access-proxy"}, {"help": "ZTNA Proxy", "label": "Ztna Proxy", "name": "ztna-proxy"}, {"help": "WANopt Tunnel", "label": "Wanopt", "name": "wanopt"}]  # Type of explicit proxy.
    access_proxy: NotRequired[list[dict[str, Any]]]  # IPv4 access proxy.
    access_proxy6: NotRequired[list[dict[str, Any]]]  # IPv6 access proxy.
    ztna_proxy: NotRequired[list[dict[str, Any]]]  # ZTNA proxies.
    srcintf: list[dict[str, Any]]  # Source interface names.
    dstintf: list[dict[str, Any]]  # Destination interface names.
    srcaddr: NotRequired[list[dict[str, Any]]]  # Source address objects.
    poolname: NotRequired[list[dict[str, Any]]]  # Name of IP pool object.
    poolname6: NotRequired[list[dict[str, Any]]]  # Name of IPv6 pool object.
    dstaddr: NotRequired[list[dict[str, Any]]]  # Destination address objects.
    ztna_ems_tag: NotRequired[list[dict[str, Any]]]  # ZTNA EMS Tag names.
    ztna_tags_match_logic: NotRequired[Literal[{"description": "Match ZTNA tags using a logical OR operator", "help": "Match ZTNA tags using a logical OR operator.", "label": "Or", "name": "or"}, {"description": "Match ZTNA tags using a logical AND operator", "help": "Match ZTNA tags using a logical AND operator.", "label": "And", "name": "and"}]]  # ZTNA tag matching logic.
    device_ownership: NotRequired[Literal[{"description": "Enable device ownership", "help": "Enable device ownership.", "label": "Enable", "name": "enable"}, {"description": "Disable device ownership", "help": "Disable device ownership.", "label": "Disable", "name": "disable"}]]  # When enabled, the ownership enforcement will be done at poli
    url_risk: NotRequired[list[dict[str, Any]]]  # URL risk level name.
    internet_service: NotRequired[Literal[{"description": "Enable use of Internet Services in policy", "help": "Enable use of Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services in policy", "help": "Disable use of Internet Services in policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of Internet Services for this policy. If 
    internet_service_negate: NotRequired[Literal[{"description": "Enable negated Internet Service match", "help": "Enable negated Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service match", "help": "Disable negated Internet Service match.", "label": "Disable", "name": "disable"}]]  # When enabled, Internet Services match against any internet s
    internet_service_name: NotRequired[list[dict[str, Any]]]  # Internet Service name.
    internet_service_group: NotRequired[list[dict[str, Any]]]  # Internet Service group name.
    internet_service_custom: NotRequired[list[dict[str, Any]]]  # Custom Internet Service name.
    internet_service_custom_group: NotRequired[list[dict[str, Any]]]  # Custom Internet Service group name.
    internet_service_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard Internet Service name.
    internet_service6: NotRequired[Literal[{"description": "Enable use of IPv6 Internet Services in policy", "help": "Enable use of IPv6 Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services in policy", "help": "Disable use of IPv6 Internet Services in policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of Internet Services IPv6 for this policy
    internet_service6_negate: NotRequired[Literal[{"description": "Enable negated IPv6 Internet Service match", "help": "Enable negated IPv6 Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service match", "help": "Disable negated IPv6 Internet Service match.", "label": "Disable", "name": "disable"}]]  # When enabled, Internet Services match against any internet s
    internet_service6_name: NotRequired[list[dict[str, Any]]]  # Internet Service IPv6 name.
    internet_service6_group: NotRequired[list[dict[str, Any]]]  # Internet Service IPv6 group name.
    internet_service6_custom: NotRequired[list[dict[str, Any]]]  # Custom Internet Service IPv6 name.
    internet_service6_custom_group: NotRequired[list[dict[str, Any]]]  # Custom Internet Service IPv6 group name.
    internet_service6_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard Internet Service IPv6 name.
    service: NotRequired[list[dict[str, Any]]]  # Name of service objects.
    srcaddr_negate: NotRequired[Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}]]  # When enabled, source addresses match against any address EXC
    dstaddr_negate: NotRequired[Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}]]  # When enabled, destination addresses match against any addres
    ztna_ems_tag_negate: NotRequired[Literal[{"description": "Enable ZTNA EMS tags negate", "help": "Enable ZTNA EMS tags negate.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA EMS tags negate", "help": "Disable ZTNA EMS tags negate.", "label": "Disable", "name": "disable"}]]  # When enabled, ZTNA EMS tags match against any tag EXCEPT the
    service_negate: NotRequired[Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}]]  # When enabled, services match against any service EXCEPT the 
    action: NotRequired[Literal[{"description": "Action accept", "help": "Action accept.", "label": "Accept", "name": "accept"}, {"description": "Action deny", "help": "Action deny.", "label": "Deny", "name": "deny"}, {"description": "Action redirect", "help": "Action redirect.", "label": "Redirect", "name": "redirect"}, {"description": "Action isolate", "help": "Action isolate.", "label": "Isolate", "name": "isolate"}]]  # Accept or deny traffic matching the policy parameters.
    status: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable the active status of the policy.
    schedule: str  # Name of schedule object.
    logtraffic: NotRequired[Literal[{"description": "Log all sessions", "help": "Log all sessions.", "label": "All", "name": "all"}, {"description": "UTM event and matched application traffic log", "help": "UTM event and matched application traffic log.", "label": "Utm", "name": "utm"}, {"description": "Disable traffic and application log", "help": "Disable traffic and application log.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging traffic through the policy.
    session_ttl: NotRequired[int]  # TTL in seconds for sessions accepted by this policy (0 means
    srcaddr6: NotRequired[list[dict[str, Any]]]  # IPv6 source address objects.
    dstaddr6: NotRequired[list[dict[str, Any]]]  # IPv6 destination address objects.
    groups: NotRequired[list[dict[str, Any]]]  # Names of group objects.
    users: NotRequired[list[dict[str, Any]]]  # Names of user objects.
    http_tunnel_auth: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable HTTP tunnel authentication.
    ssh_policy_redirect: NotRequired[Literal[{"description": "Enable SSH policy redirect", "help": "Enable SSH policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable SSH policy redirect", "help": "Disable SSH policy redirect.", "label": "Disable", "name": "disable"}]]  # Redirect SSH traffic to matching transparent proxy policy.
    webproxy_forward_server: NotRequired[str]  # Web proxy forward server name.
    isolator_server: str  # Isolator server name.
    webproxy_profile: NotRequired[str]  # Name of web proxy profile.
    transparent: NotRequired[Literal[{"description": "Enable use of IP address of client to connect to server", "help": "Enable use of IP address of client to connect to server.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IP address of client to connect to server", "help": "Disable use of IP address of client to connect to server.", "label": "Disable", "name": "disable"}]]  # Enable to use the IP address of the client to connect to the
    webcache: NotRequired[Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable web caching.
    webcache_https: NotRequired[Literal[{"help": "Disable web cache for HTTPS.", "label": "Disable", "name": "disable"}, {"help": "Enable web cache for HTTPS.", "label": "Enable", "name": "enable"}]]  # Enable/disable web caching for HTTPS (Requires deep-inspecti
    disclaimer: NotRequired[Literal[{"description": "Disable disclaimer", "help": "Disable disclaimer.", "label": "Disable", "name": "disable"}, {"description": "Display disclaimer for domain    policy:Display disclaimer for policy    user:Display disclaimer for current user", "help": "Display disclaimer for domain", "label": "Domain", "name": "domain"}, {"help": "Display disclaimer for policy", "label": "Policy", "name": "policy"}, {"help": "Display disclaimer for current user", "label": "User", "name": "user"}]]  # Web proxy disclaimer setting: by domain, policy, or user.
    utm_status: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable the use of UTM profiles/sensors/lists.
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
    ips_voip_filter: NotRequired[str]  # Name of an existing VoIP (ips) profile.
    sctp_filter_profile: NotRequired[str]  # Name of an existing SCTP filter profile.
    icap_profile: NotRequired[str]  # Name of an existing ICAP profile.
    videofilter_profile: NotRequired[str]  # Name of an existing VideoFilter profile.
    waf_profile: NotRequired[str]  # Name of an existing Web application firewall profile.
    ssh_filter_profile: NotRequired[str]  # Name of an existing SSH filter profile.
    casb_profile: NotRequired[str]  # Name of an existing CASB profile.
    replacemsg_override_group: NotRequired[str]  # Authentication replacement message override group.
    logtraffic_start: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable policy log traffic start.
    log_http_transaction: NotRequired[Literal[{"description": "Enable HTTP transaction log", "help": "Enable HTTP transaction log.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP transaction log", "help": "Disable HTTP transaction log.", "label": "Disable", "name": "disable"}]]  # Enable/disable HTTP transaction log.
    comments: NotRequired[str]  # Optional comments.
    block_notification: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable block notification.
    redirect_url: NotRequired[str]  # Redirect URL for further explicit web proxy processing.
    https_sub_category: NotRequired[Literal[{"description": "Enable HTTPS sub-category policy matching", "help": "Enable HTTPS sub-category policy matching.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTPS sub-category policy matching", "help": "Disable HTTPS sub-category policy matching.", "label": "Disable", "name": "disable"}]]  # Enable/disable HTTPS sub-category policy matching.
    decrypted_traffic_mirror: NotRequired[str]  # Decrypted traffic mirror.
    detect_https_in_http_request: NotRequired[Literal[{"description": "Enable detection of HTTPS in HTTP request", "help": "Enable detection of HTTPS in HTTP request.", "label": "Enable", "name": "enable"}, {"description": "Disable detection of HTTPS in HTTP request", "help": "Disable detection of HTTPS in HTTP request.", "label": "Disable", "name": "disable"}]]  # Enable/disable detection of HTTPS in HTTP request.


class ProxyPolicy:
    """
    Configure proxy policies.
    
    Path: firewall/proxy_policy
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
        payload_dict: ProxyPolicyPayload | None = ...,
        uuid: str | None = ...,
        policyid: int | None = ...,
        name: str | None = ...,
        proxy: Literal[{"description": "Explicit Web Proxy    transparent-web:Transparent Web Proxy    ftp:Explicit FTP Proxy    ssh:SSH Proxy    ssh-tunnel:SSH Tunnel    access-proxy:Access Proxy    ztna-proxy:ZTNA Proxy", "help": "Explicit Web Proxy", "label": "Explicit Web", "name": "explicit-web"}, {"help": "Transparent Web Proxy", "label": "Transparent Web", "name": "transparent-web"}, {"help": "Explicit FTP Proxy", "label": "Ftp", "name": "ftp"}, {"help": "SSH Proxy", "label": "Ssh", "name": "ssh"}, {"help": "SSH Tunnel", "label": "Ssh Tunnel", "name": "ssh-tunnel"}, {"help": "Access Proxy", "label": "Access Proxy", "name": "access-proxy"}, {"help": "ZTNA Proxy", "label": "Ztna Proxy", "name": "ztna-proxy"}, {"help": "WANopt Tunnel", "label": "Wanopt", "name": "wanopt"}] | None = ...,
        access_proxy: list[dict[str, Any]] | None = ...,
        access_proxy6: list[dict[str, Any]] | None = ...,
        ztna_proxy: list[dict[str, Any]] | None = ...,
        srcintf: list[dict[str, Any]] | None = ...,
        dstintf: list[dict[str, Any]] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        poolname: list[dict[str, Any]] | None = ...,
        poolname6: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        ztna_ems_tag: list[dict[str, Any]] | None = ...,
        ztna_tags_match_logic: Literal[{"description": "Match ZTNA tags using a logical OR operator", "help": "Match ZTNA tags using a logical OR operator.", "label": "Or", "name": "or"}, {"description": "Match ZTNA tags using a logical AND operator", "help": "Match ZTNA tags using a logical AND operator.", "label": "And", "name": "and"}] | None = ...,
        device_ownership: Literal[{"description": "Enable device ownership", "help": "Enable device ownership.", "label": "Enable", "name": "enable"}, {"description": "Disable device ownership", "help": "Disable device ownership.", "label": "Disable", "name": "disable"}] | None = ...,
        url_risk: list[dict[str, Any]] | None = ...,
        internet_service: Literal[{"description": "Enable use of Internet Services in policy", "help": "Enable use of Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services in policy", "help": "Disable use of Internet Services in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_negate: Literal[{"description": "Enable negated Internet Service match", "help": "Enable negated Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service match", "help": "Disable negated Internet Service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_name: list[dict[str, Any]] | None = ...,
        internet_service_group: list[dict[str, Any]] | None = ...,
        internet_service_custom: list[dict[str, Any]] | None = ...,
        internet_service_custom_group: list[dict[str, Any]] | None = ...,
        internet_service_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service6: Literal[{"description": "Enable use of IPv6 Internet Services in policy", "help": "Enable use of IPv6 Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services in policy", "help": "Disable use of IPv6 Internet Services in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_negate: Literal[{"description": "Enable negated IPv6 Internet Service match", "help": "Enable negated IPv6 Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service match", "help": "Disable negated IPv6 Internet Service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_name: list[dict[str, Any]] | None = ...,
        internet_service6_group: list[dict[str, Any]] | None = ...,
        internet_service6_custom: list[dict[str, Any]] | None = ...,
        internet_service6_custom_group: list[dict[str, Any]] | None = ...,
        internet_service6_fortiguard: list[dict[str, Any]] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        srcaddr_negate: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        dstaddr_negate: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        ztna_ems_tag_negate: Literal[{"description": "Enable ZTNA EMS tags negate", "help": "Enable ZTNA EMS tags negate.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA EMS tags negate", "help": "Disable ZTNA EMS tags negate.", "label": "Disable", "name": "disable"}] | None = ...,
        service_negate: Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}] | None = ...,
        action: Literal[{"description": "Action accept", "help": "Action accept.", "label": "Accept", "name": "accept"}, {"description": "Action deny", "help": "Action deny.", "label": "Deny", "name": "deny"}, {"description": "Action redirect", "help": "Action redirect.", "label": "Redirect", "name": "redirect"}, {"description": "Action isolate", "help": "Action isolate.", "label": "Isolate", "name": "isolate"}] | None = ...,
        status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        schedule: str | None = ...,
        logtraffic: Literal[{"description": "Log all sessions", "help": "Log all sessions.", "label": "All", "name": "all"}, {"description": "UTM event and matched application traffic log", "help": "UTM event and matched application traffic log.", "label": "Utm", "name": "utm"}, {"description": "Disable traffic and application log", "help": "Disable traffic and application log.", "label": "Disable", "name": "disable"}] | None = ...,
        session_ttl: int | None = ...,
        srcaddr6: list[dict[str, Any]] | None = ...,
        dstaddr6: list[dict[str, Any]] | None = ...,
        groups: list[dict[str, Any]] | None = ...,
        users: list[dict[str, Any]] | None = ...,
        http_tunnel_auth: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ssh_policy_redirect: Literal[{"description": "Enable SSH policy redirect", "help": "Enable SSH policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable SSH policy redirect", "help": "Disable SSH policy redirect.", "label": "Disable", "name": "disable"}] | None = ...,
        webproxy_forward_server: str | None = ...,
        isolator_server: str | None = ...,
        webproxy_profile: str | None = ...,
        transparent: Literal[{"description": "Enable use of IP address of client to connect to server", "help": "Enable use of IP address of client to connect to server.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IP address of client to connect to server", "help": "Disable use of IP address of client to connect to server.", "label": "Disable", "name": "disable"}] | None = ...,
        webcache: Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        webcache_https: Literal[{"help": "Disable web cache for HTTPS.", "label": "Disable", "name": "disable"}, {"help": "Enable web cache for HTTPS.", "label": "Enable", "name": "enable"}] | None = ...,
        disclaimer: Literal[{"description": "Disable disclaimer", "help": "Disable disclaimer.", "label": "Disable", "name": "disable"}, {"description": "Display disclaimer for domain    policy:Display disclaimer for policy    user:Display disclaimer for current user", "help": "Display disclaimer for domain", "label": "Domain", "name": "domain"}, {"help": "Display disclaimer for policy", "label": "Policy", "name": "policy"}, {"help": "Display disclaimer for current user", "label": "User", "name": "user"}] | None = ...,
        utm_status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
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
        ips_voip_filter: str | None = ...,
        sctp_filter_profile: str | None = ...,
        icap_profile: str | None = ...,
        videofilter_profile: str | None = ...,
        waf_profile: str | None = ...,
        ssh_filter_profile: str | None = ...,
        casb_profile: str | None = ...,
        replacemsg_override_group: str | None = ...,
        logtraffic_start: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        log_http_transaction: Literal[{"description": "Enable HTTP transaction log", "help": "Enable HTTP transaction log.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP transaction log", "help": "Disable HTTP transaction log.", "label": "Disable", "name": "disable"}] | None = ...,
        comments: str | None = ...,
        block_notification: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        redirect_url: str | None = ...,
        https_sub_category: Literal[{"description": "Enable HTTPS sub-category policy matching", "help": "Enable HTTPS sub-category policy matching.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTPS sub-category policy matching", "help": "Disable HTTPS sub-category policy matching.", "label": "Disable", "name": "disable"}] | None = ...,
        decrypted_traffic_mirror: str | None = ...,
        detect_https_in_http_request: Literal[{"description": "Enable detection of HTTPS in HTTP request", "help": "Enable detection of HTTPS in HTTP request.", "label": "Enable", "name": "enable"}, {"description": "Disable detection of HTTPS in HTTP request", "help": "Disable detection of HTTPS in HTTP request.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ProxyPolicyPayload | None = ...,
        uuid: str | None = ...,
        policyid: int | None = ...,
        name: str | None = ...,
        proxy: Literal[{"description": "Explicit Web Proxy    transparent-web:Transparent Web Proxy    ftp:Explicit FTP Proxy    ssh:SSH Proxy    ssh-tunnel:SSH Tunnel    access-proxy:Access Proxy    ztna-proxy:ZTNA Proxy", "help": "Explicit Web Proxy", "label": "Explicit Web", "name": "explicit-web"}, {"help": "Transparent Web Proxy", "label": "Transparent Web", "name": "transparent-web"}, {"help": "Explicit FTP Proxy", "label": "Ftp", "name": "ftp"}, {"help": "SSH Proxy", "label": "Ssh", "name": "ssh"}, {"help": "SSH Tunnel", "label": "Ssh Tunnel", "name": "ssh-tunnel"}, {"help": "Access Proxy", "label": "Access Proxy", "name": "access-proxy"}, {"help": "ZTNA Proxy", "label": "Ztna Proxy", "name": "ztna-proxy"}, {"help": "WANopt Tunnel", "label": "Wanopt", "name": "wanopt"}] | None = ...,
        access_proxy: list[dict[str, Any]] | None = ...,
        access_proxy6: list[dict[str, Any]] | None = ...,
        ztna_proxy: list[dict[str, Any]] | None = ...,
        srcintf: list[dict[str, Any]] | None = ...,
        dstintf: list[dict[str, Any]] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        poolname: list[dict[str, Any]] | None = ...,
        poolname6: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        ztna_ems_tag: list[dict[str, Any]] | None = ...,
        ztna_tags_match_logic: Literal[{"description": "Match ZTNA tags using a logical OR operator", "help": "Match ZTNA tags using a logical OR operator.", "label": "Or", "name": "or"}, {"description": "Match ZTNA tags using a logical AND operator", "help": "Match ZTNA tags using a logical AND operator.", "label": "And", "name": "and"}] | None = ...,
        device_ownership: Literal[{"description": "Enable device ownership", "help": "Enable device ownership.", "label": "Enable", "name": "enable"}, {"description": "Disable device ownership", "help": "Disable device ownership.", "label": "Disable", "name": "disable"}] | None = ...,
        url_risk: list[dict[str, Any]] | None = ...,
        internet_service: Literal[{"description": "Enable use of Internet Services in policy", "help": "Enable use of Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services in policy", "help": "Disable use of Internet Services in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_negate: Literal[{"description": "Enable negated Internet Service match", "help": "Enable negated Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service match", "help": "Disable negated Internet Service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_name: list[dict[str, Any]] | None = ...,
        internet_service_group: list[dict[str, Any]] | None = ...,
        internet_service_custom: list[dict[str, Any]] | None = ...,
        internet_service_custom_group: list[dict[str, Any]] | None = ...,
        internet_service_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service6: Literal[{"description": "Enable use of IPv6 Internet Services in policy", "help": "Enable use of IPv6 Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services in policy", "help": "Disable use of IPv6 Internet Services in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_negate: Literal[{"description": "Enable negated IPv6 Internet Service match", "help": "Enable negated IPv6 Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service match", "help": "Disable negated IPv6 Internet Service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_name: list[dict[str, Any]] | None = ...,
        internet_service6_group: list[dict[str, Any]] | None = ...,
        internet_service6_custom: list[dict[str, Any]] | None = ...,
        internet_service6_custom_group: list[dict[str, Any]] | None = ...,
        internet_service6_fortiguard: list[dict[str, Any]] | None = ...,
        service: list[dict[str, Any]] | None = ...,
        srcaddr_negate: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        dstaddr_negate: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        ztna_ems_tag_negate: Literal[{"description": "Enable ZTNA EMS tags negate", "help": "Enable ZTNA EMS tags negate.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA EMS tags negate", "help": "Disable ZTNA EMS tags negate.", "label": "Disable", "name": "disable"}] | None = ...,
        service_negate: Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}] | None = ...,
        action: Literal[{"description": "Action accept", "help": "Action accept.", "label": "Accept", "name": "accept"}, {"description": "Action deny", "help": "Action deny.", "label": "Deny", "name": "deny"}, {"description": "Action redirect", "help": "Action redirect.", "label": "Redirect", "name": "redirect"}, {"description": "Action isolate", "help": "Action isolate.", "label": "Isolate", "name": "isolate"}] | None = ...,
        status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        schedule: str | None = ...,
        logtraffic: Literal[{"description": "Log all sessions", "help": "Log all sessions.", "label": "All", "name": "all"}, {"description": "UTM event and matched application traffic log", "help": "UTM event and matched application traffic log.", "label": "Utm", "name": "utm"}, {"description": "Disable traffic and application log", "help": "Disable traffic and application log.", "label": "Disable", "name": "disable"}] | None = ...,
        session_ttl: int | None = ...,
        srcaddr6: list[dict[str, Any]] | None = ...,
        dstaddr6: list[dict[str, Any]] | None = ...,
        groups: list[dict[str, Any]] | None = ...,
        users: list[dict[str, Any]] | None = ...,
        http_tunnel_auth: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ssh_policy_redirect: Literal[{"description": "Enable SSH policy redirect", "help": "Enable SSH policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable SSH policy redirect", "help": "Disable SSH policy redirect.", "label": "Disable", "name": "disable"}] | None = ...,
        webproxy_forward_server: str | None = ...,
        isolator_server: str | None = ...,
        webproxy_profile: str | None = ...,
        transparent: Literal[{"description": "Enable use of IP address of client to connect to server", "help": "Enable use of IP address of client to connect to server.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IP address of client to connect to server", "help": "Disable use of IP address of client to connect to server.", "label": "Disable", "name": "disable"}] | None = ...,
        webcache: Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        webcache_https: Literal[{"help": "Disable web cache for HTTPS.", "label": "Disable", "name": "disable"}, {"help": "Enable web cache for HTTPS.", "label": "Enable", "name": "enable"}] | None = ...,
        disclaimer: Literal[{"description": "Disable disclaimer", "help": "Disable disclaimer.", "label": "Disable", "name": "disable"}, {"description": "Display disclaimer for domain    policy:Display disclaimer for policy    user:Display disclaimer for current user", "help": "Display disclaimer for domain", "label": "Domain", "name": "domain"}, {"help": "Display disclaimer for policy", "label": "Policy", "name": "policy"}, {"help": "Display disclaimer for current user", "label": "User", "name": "user"}] | None = ...,
        utm_status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
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
        ips_voip_filter: str | None = ...,
        sctp_filter_profile: str | None = ...,
        icap_profile: str | None = ...,
        videofilter_profile: str | None = ...,
        waf_profile: str | None = ...,
        ssh_filter_profile: str | None = ...,
        casb_profile: str | None = ...,
        replacemsg_override_group: str | None = ...,
        logtraffic_start: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        log_http_transaction: Literal[{"description": "Enable HTTP transaction log", "help": "Enable HTTP transaction log.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP transaction log", "help": "Disable HTTP transaction log.", "label": "Disable", "name": "disable"}] | None = ...,
        comments: str | None = ...,
        block_notification: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        redirect_url: str | None = ...,
        https_sub_category: Literal[{"description": "Enable HTTPS sub-category policy matching", "help": "Enable HTTPS sub-category policy matching.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTPS sub-category policy matching", "help": "Disable HTTPS sub-category policy matching.", "label": "Disable", "name": "disable"}] | None = ...,
        decrypted_traffic_mirror: str | None = ...,
        detect_https_in_http_request: Literal[{"description": "Enable detection of HTTPS in HTTP request", "help": "Enable detection of HTTPS in HTTP request.", "label": "Enable", "name": "enable"}, {"description": "Disable detection of HTTPS in HTTP request", "help": "Disable detection of HTTPS in HTTP request.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: ProxyPolicyPayload | None = ...,
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
    "ProxyPolicy",
    "ProxyPolicyPayload",
]