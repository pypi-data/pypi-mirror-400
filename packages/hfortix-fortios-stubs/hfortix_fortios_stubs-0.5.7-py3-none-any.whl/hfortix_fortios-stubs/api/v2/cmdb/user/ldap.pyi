from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class LdapPayload(TypedDict, total=False):
    """
    Type hints for user/ldap payload fields.
    
    Configure LDAP server entries.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface, source-ip-interface)
        - :class:`~.user.exchange.ExchangeEndpoint` (via: user-info-exchange-server)
        - :class:`~.vpn.certificate.ca.CaEndpoint` (via: ca-cert)
        - :class:`~.vpn.certificate.local.LocalEndpoint` (via: client-cert)

    **Usage:**
        payload: LdapPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # LDAP server entry name.
    server: str  # LDAP server CN domain name or IP.
    secondary_server: NotRequired[str]  # Secondary LDAP server CN domain name or IP.
    tertiary_server: NotRequired[str]  # Tertiary LDAP server CN domain name or IP.
    status_ttl: NotRequired[int]  # Time for which server reachability is cached so that when a 
    server_identity_check: NotRequired[Literal[{"description": "Enable server identity check", "help": "Enable server identity check.", "label": "Enable", "name": "enable"}, {"description": "Disable server identity check", "help": "Disable server identity check.", "label": "Disable", "name": "disable"}]]  # Enable/disable LDAP server identity check (verify server dom
    source_ip: NotRequired[str]  # FortiGate IP address to be used for communication with the L
    source_ip_interface: NotRequired[str]  # Source interface for communication with the LDAP server.
    source_port: NotRequired[int]  # Source port to be used for communication with the LDAP serve
    cnid: NotRequired[str]  # Common name identifier for the LDAP server. The common name 
    dn: str  # Distinguished name used to look up entries on the LDAP serve
    type: NotRequired[Literal[{"description": "Simple password authentication without search", "help": "Simple password authentication without search.", "label": "Simple", "name": "simple"}, {"description": "Bind using anonymous user search", "help": "Bind using anonymous user search.", "label": "Anonymous", "name": "anonymous"}, {"description": "Bind using username/password and then search", "help": "Bind using username/password and then search.", "label": "Regular", "name": "regular"}]]  # Authentication type for LDAP searches.
    two_factor: NotRequired[Literal[{"description": "disable two-factor authentication", "help": "disable two-factor authentication.", "label": "Disable", "name": "disable"}, {"description": "FortiToken Cloud Service", "help": "FortiToken Cloud Service.", "label": "Fortitoken Cloud", "name": "fortitoken-cloud"}]]  # Enable/disable two-factor authentication.
    two_factor_authentication: NotRequired[Literal[{"description": "FortiToken authentication", "help": "FortiToken authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "Email one time password", "help": "Email one time password.", "label": "Email", "name": "email"}, {"description": "SMS one time password", "help": "SMS one time password.", "label": "Sms", "name": "sms"}]]  # Authentication method by FortiToken Cloud.
    two_factor_notification: NotRequired[Literal[{"description": "Email notification for activation code", "help": "Email notification for activation code.", "label": "Email", "name": "email"}, {"description": "SMS notification for activation code", "help": "SMS notification for activation code.", "label": "Sms", "name": "sms"}]]  # Notification method for user activation by FortiToken Cloud.
    two_factor_filter: NotRequired[str]  # Filter used to synchronize users to FortiToken Cloud.
    username: str  # Username (full DN) for initial binding.
    password: NotRequired[str]  # Password for initial binding.
    group_member_check: NotRequired[Literal[{"description": "User attribute checking", "help": "User attribute checking.", "label": "User Attr", "name": "user-attr"}, {"description": "Group object checking", "help": "Group object checking.", "label": "Group Object", "name": "group-object"}, {"description": "POSIX group object checking", "help": "POSIX group object checking.", "label": "Posix Group Object", "name": "posix-group-object"}]]  # Group member checking methods.
    group_search_base: NotRequired[str]  # Search base used for group searching.
    group_object_filter: NotRequired[str]  # Filter used for group searching.
    group_filter: NotRequired[str]  # Filter used for group matching.
    secure: NotRequired[Literal[{"description": "No SSL", "help": "No SSL.", "label": "Disable", "name": "disable"}, {"description": "Use StartTLS", "help": "Use StartTLS.", "label": "Starttls", "name": "starttls"}, {"description": "Use LDAPS", "help": "Use LDAPS.", "label": "Ldaps", "name": "ldaps"}]]  # Port to be used for authentication.
    ssl_min_proto_version: NotRequired[Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]]  # Minimum supported protocol version for SSL/TLS connections (
    ca_cert: NotRequired[str]  # CA certificate name.
    port: NotRequired[int]  # Port to be used for communication with the LDAP server (defa
    password_expiry_warning: NotRequired[Literal[{"description": "Enable password expiry warnings", "help": "Enable password expiry warnings.", "label": "Enable", "name": "enable"}, {"description": "Disable password expiry warnings", "help": "Disable password expiry warnings.", "label": "Disable", "name": "disable"}]]  # Enable/disable password expiry warnings.
    password_renewal: NotRequired[Literal[{"description": "Enable online password renewal", "help": "Enable online password renewal.", "label": "Enable", "name": "enable"}, {"description": "Disable online password renewal", "help": "Disable online password renewal.", "label": "Disable", "name": "disable"}]]  # Enable/disable online password renewal.
    member_attr: NotRequired[str]  # Name of attribute from which to get group membership.
    account_key_processing: NotRequired[Literal[{"description": "Same as subject identity field", "help": "Same as subject identity field.", "label": "Same", "name": "same"}, {"description": "Strip domain string from subject identity field", "help": "Strip domain string from subject identity field.", "label": "Strip", "name": "strip"}]]  # Account key processing operation. The FortiGate will keep ei
    account_key_cert_field: NotRequired[Literal[{"description": "Other name in SAN", "help": "Other name in SAN.", "label": "Othername", "name": "othername"}, {"description": "RFC822 email address in SAN", "help": "RFC822 email address in SAN.", "label": "Rfc822Name", "name": "rfc822name"}, {"description": "DNS name in SAN", "help": "DNS name in SAN.", "label": "Dnsname", "name": "dnsname"}, {"description": "CN in subject", "help": "CN in subject.", "label": "Cn", "name": "cn"}]]  # Define subject identity field in certificate for user access
    account_key_filter: NotRequired[str]  # Account key filter, using the UPN as the search filter.
    search_type: NotRequired[Literal[{"description": "Recursively retrieve the user-group chain information of a user in a particular Microsoft AD domain", "help": "Recursively retrieve the user-group chain information of a user in a particular Microsoft AD domain.", "label": "Recursive", "name": "recursive"}]]  # Search type.
    client_cert_auth: NotRequired[Literal[{"description": "Enable using client certificate for TLS authentication", "help": "Enable using client certificate for TLS authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable using client certificate for TLS authentication", "help": "Disable using client certificate for TLS authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable using client certificate for TLS authenticati
    client_cert: NotRequired[str]  # Client certificate name.
    obtain_user_info: NotRequired[Literal[{"description": "Enable obtaining of user information", "help": "Enable obtaining of user information.", "label": "Enable", "name": "enable"}, {"description": "Disable obtaining of user information", "help": "Disable obtaining of user information.", "label": "Disable", "name": "disable"}]]  # Enable/disable obtaining of user information.
    user_info_exchange_server: NotRequired[str]  # MS Exchange server from which to fetch user information.
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.
    antiphish: NotRequired[Literal[{"description": "Enable AntiPhishing credential backend", "help": "Enable AntiPhishing credential backend.", "label": "Enable", "name": "enable"}, {"description": "Disable AntiPhishing credential backend", "help": "Disable AntiPhishing credential backend.", "label": "Disable", "name": "disable"}]]  # Enable/disable AntiPhishing credential backend.
    password_attr: NotRequired[str]  # Name of attribute to get password hash.


class Ldap:
    """
    Configure LDAP server entries.
    
    Path: user/ldap
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
        payload_dict: LdapPayload | None = ...,
        name: str | None = ...,
        server: str | None = ...,
        secondary_server: str | None = ...,
        tertiary_server: str | None = ...,
        status_ttl: int | None = ...,
        server_identity_check: Literal[{"description": "Enable server identity check", "help": "Enable server identity check.", "label": "Enable", "name": "enable"}, {"description": "Disable server identity check", "help": "Disable server identity check.", "label": "Disable", "name": "disable"}] | None = ...,
        source_ip: str | None = ...,
        source_ip_interface: str | None = ...,
        source_port: int | None = ...,
        cnid: str | None = ...,
        dn: str | None = ...,
        type: Literal[{"description": "Simple password authentication without search", "help": "Simple password authentication without search.", "label": "Simple", "name": "simple"}, {"description": "Bind using anonymous user search", "help": "Bind using anonymous user search.", "label": "Anonymous", "name": "anonymous"}, {"description": "Bind using username/password and then search", "help": "Bind using username/password and then search.", "label": "Regular", "name": "regular"}] | None = ...,
        two_factor: Literal[{"description": "disable two-factor authentication", "help": "disable two-factor authentication.", "label": "Disable", "name": "disable"}, {"description": "FortiToken Cloud Service", "help": "FortiToken Cloud Service.", "label": "Fortitoken Cloud", "name": "fortitoken-cloud"}] | None = ...,
        two_factor_authentication: Literal[{"description": "FortiToken authentication", "help": "FortiToken authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "Email one time password", "help": "Email one time password.", "label": "Email", "name": "email"}, {"description": "SMS one time password", "help": "SMS one time password.", "label": "Sms", "name": "sms"}] | None = ...,
        two_factor_notification: Literal[{"description": "Email notification for activation code", "help": "Email notification for activation code.", "label": "Email", "name": "email"}, {"description": "SMS notification for activation code", "help": "SMS notification for activation code.", "label": "Sms", "name": "sms"}] | None = ...,
        two_factor_filter: str | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        group_member_check: Literal[{"description": "User attribute checking", "help": "User attribute checking.", "label": "User Attr", "name": "user-attr"}, {"description": "Group object checking", "help": "Group object checking.", "label": "Group Object", "name": "group-object"}, {"description": "POSIX group object checking", "help": "POSIX group object checking.", "label": "Posix Group Object", "name": "posix-group-object"}] | None = ...,
        group_search_base: str | None = ...,
        group_object_filter: str | None = ...,
        group_filter: str | None = ...,
        secure: Literal[{"description": "No SSL", "help": "No SSL.", "label": "Disable", "name": "disable"}, {"description": "Use StartTLS", "help": "Use StartTLS.", "label": "Starttls", "name": "starttls"}, {"description": "Use LDAPS", "help": "Use LDAPS.", "label": "Ldaps", "name": "ldaps"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        ca_cert: str | None = ...,
        port: int | None = ...,
        password_expiry_warning: Literal[{"description": "Enable password expiry warnings", "help": "Enable password expiry warnings.", "label": "Enable", "name": "enable"}, {"description": "Disable password expiry warnings", "help": "Disable password expiry warnings.", "label": "Disable", "name": "disable"}] | None = ...,
        password_renewal: Literal[{"description": "Enable online password renewal", "help": "Enable online password renewal.", "label": "Enable", "name": "enable"}, {"description": "Disable online password renewal", "help": "Disable online password renewal.", "label": "Disable", "name": "disable"}] | None = ...,
        member_attr: str | None = ...,
        account_key_processing: Literal[{"description": "Same as subject identity field", "help": "Same as subject identity field.", "label": "Same", "name": "same"}, {"description": "Strip domain string from subject identity field", "help": "Strip domain string from subject identity field.", "label": "Strip", "name": "strip"}] | None = ...,
        account_key_cert_field: Literal[{"description": "Other name in SAN", "help": "Other name in SAN.", "label": "Othername", "name": "othername"}, {"description": "RFC822 email address in SAN", "help": "RFC822 email address in SAN.", "label": "Rfc822Name", "name": "rfc822name"}, {"description": "DNS name in SAN", "help": "DNS name in SAN.", "label": "Dnsname", "name": "dnsname"}, {"description": "CN in subject", "help": "CN in subject.", "label": "Cn", "name": "cn"}] | None = ...,
        account_key_filter: str | None = ...,
        search_type: Literal[{"description": "Recursively retrieve the user-group chain information of a user in a particular Microsoft AD domain", "help": "Recursively retrieve the user-group chain information of a user in a particular Microsoft AD domain.", "label": "Recursive", "name": "recursive"}] | None = ...,
        client_cert_auth: Literal[{"description": "Enable using client certificate for TLS authentication", "help": "Enable using client certificate for TLS authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable using client certificate for TLS authentication", "help": "Disable using client certificate for TLS authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        client_cert: str | None = ...,
        obtain_user_info: Literal[{"description": "Enable obtaining of user information", "help": "Enable obtaining of user information.", "label": "Enable", "name": "enable"}, {"description": "Disable obtaining of user information", "help": "Disable obtaining of user information.", "label": "Disable", "name": "disable"}] | None = ...,
        user_info_exchange_server: str | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        antiphish: Literal[{"description": "Enable AntiPhishing credential backend", "help": "Enable AntiPhishing credential backend.", "label": "Enable", "name": "enable"}, {"description": "Disable AntiPhishing credential backend", "help": "Disable AntiPhishing credential backend.", "label": "Disable", "name": "disable"}] | None = ...,
        password_attr: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: LdapPayload | None = ...,
        name: str | None = ...,
        server: str | None = ...,
        secondary_server: str | None = ...,
        tertiary_server: str | None = ...,
        status_ttl: int | None = ...,
        server_identity_check: Literal[{"description": "Enable server identity check", "help": "Enable server identity check.", "label": "Enable", "name": "enable"}, {"description": "Disable server identity check", "help": "Disable server identity check.", "label": "Disable", "name": "disable"}] | None = ...,
        source_ip: str | None = ...,
        source_ip_interface: str | None = ...,
        source_port: int | None = ...,
        cnid: str | None = ...,
        dn: str | None = ...,
        type: Literal[{"description": "Simple password authentication without search", "help": "Simple password authentication without search.", "label": "Simple", "name": "simple"}, {"description": "Bind using anonymous user search", "help": "Bind using anonymous user search.", "label": "Anonymous", "name": "anonymous"}, {"description": "Bind using username/password and then search", "help": "Bind using username/password and then search.", "label": "Regular", "name": "regular"}] | None = ...,
        two_factor: Literal[{"description": "disable two-factor authentication", "help": "disable two-factor authentication.", "label": "Disable", "name": "disable"}, {"description": "FortiToken Cloud Service", "help": "FortiToken Cloud Service.", "label": "Fortitoken Cloud", "name": "fortitoken-cloud"}] | None = ...,
        two_factor_authentication: Literal[{"description": "FortiToken authentication", "help": "FortiToken authentication.", "label": "Fortitoken", "name": "fortitoken"}, {"description": "Email one time password", "help": "Email one time password.", "label": "Email", "name": "email"}, {"description": "SMS one time password", "help": "SMS one time password.", "label": "Sms", "name": "sms"}] | None = ...,
        two_factor_notification: Literal[{"description": "Email notification for activation code", "help": "Email notification for activation code.", "label": "Email", "name": "email"}, {"description": "SMS notification for activation code", "help": "SMS notification for activation code.", "label": "Sms", "name": "sms"}] | None = ...,
        two_factor_filter: str | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        group_member_check: Literal[{"description": "User attribute checking", "help": "User attribute checking.", "label": "User Attr", "name": "user-attr"}, {"description": "Group object checking", "help": "Group object checking.", "label": "Group Object", "name": "group-object"}, {"description": "POSIX group object checking", "help": "POSIX group object checking.", "label": "Posix Group Object", "name": "posix-group-object"}] | None = ...,
        group_search_base: str | None = ...,
        group_object_filter: str | None = ...,
        group_filter: str | None = ...,
        secure: Literal[{"description": "No SSL", "help": "No SSL.", "label": "Disable", "name": "disable"}, {"description": "Use StartTLS", "help": "Use StartTLS.", "label": "Starttls", "name": "starttls"}, {"description": "Use LDAPS", "help": "Use LDAPS.", "label": "Ldaps", "name": "ldaps"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        ca_cert: str | None = ...,
        port: int | None = ...,
        password_expiry_warning: Literal[{"description": "Enable password expiry warnings", "help": "Enable password expiry warnings.", "label": "Enable", "name": "enable"}, {"description": "Disable password expiry warnings", "help": "Disable password expiry warnings.", "label": "Disable", "name": "disable"}] | None = ...,
        password_renewal: Literal[{"description": "Enable online password renewal", "help": "Enable online password renewal.", "label": "Enable", "name": "enable"}, {"description": "Disable online password renewal", "help": "Disable online password renewal.", "label": "Disable", "name": "disable"}] | None = ...,
        member_attr: str | None = ...,
        account_key_processing: Literal[{"description": "Same as subject identity field", "help": "Same as subject identity field.", "label": "Same", "name": "same"}, {"description": "Strip domain string from subject identity field", "help": "Strip domain string from subject identity field.", "label": "Strip", "name": "strip"}] | None = ...,
        account_key_cert_field: Literal[{"description": "Other name in SAN", "help": "Other name in SAN.", "label": "Othername", "name": "othername"}, {"description": "RFC822 email address in SAN", "help": "RFC822 email address in SAN.", "label": "Rfc822Name", "name": "rfc822name"}, {"description": "DNS name in SAN", "help": "DNS name in SAN.", "label": "Dnsname", "name": "dnsname"}, {"description": "CN in subject", "help": "CN in subject.", "label": "Cn", "name": "cn"}] | None = ...,
        account_key_filter: str | None = ...,
        search_type: Literal[{"description": "Recursively retrieve the user-group chain information of a user in a particular Microsoft AD domain", "help": "Recursively retrieve the user-group chain information of a user in a particular Microsoft AD domain.", "label": "Recursive", "name": "recursive"}] | None = ...,
        client_cert_auth: Literal[{"description": "Enable using client certificate for TLS authentication", "help": "Enable using client certificate for TLS authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable using client certificate for TLS authentication", "help": "Disable using client certificate for TLS authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        client_cert: str | None = ...,
        obtain_user_info: Literal[{"description": "Enable obtaining of user information", "help": "Enable obtaining of user information.", "label": "Enable", "name": "enable"}, {"description": "Disable obtaining of user information", "help": "Disable obtaining of user information.", "label": "Disable", "name": "disable"}] | None = ...,
        user_info_exchange_server: str | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        antiphish: Literal[{"description": "Enable AntiPhishing credential backend", "help": "Enable AntiPhishing credential backend.", "label": "Enable", "name": "enable"}, {"description": "Disable AntiPhishing credential backend", "help": "Disable AntiPhishing credential backend.", "label": "Disable", "name": "disable"}] | None = ...,
        password_attr: str | None = ...,
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
        payload_dict: LdapPayload | None = ...,
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
    "Ldap",
    "LdapPayload",
]