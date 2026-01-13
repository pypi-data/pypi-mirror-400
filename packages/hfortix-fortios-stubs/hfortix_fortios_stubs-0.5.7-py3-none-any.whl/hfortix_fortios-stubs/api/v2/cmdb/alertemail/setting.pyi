from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingPayload(TypedDict, total=False):
    """
    Type hints for alertemail/setting payload fields.
    
    Configure alert email settings.
    
    **Usage:**
        payload: SettingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    username: NotRequired[str]  # Name that appears in the From: field of alert emails (max. 6
    mailto1: NotRequired[str]  # Email address to send alert email to (usually a system admin
    mailto2: NotRequired[str]  # Optional second email address to send alert email to (max. 6
    mailto3: NotRequired[str]  # Optional third email address to send alert email to (max. 63
    filter_mode: NotRequired[Literal[{"description": "Filter based on category", "help": "Filter based on category.", "label": "Category", "name": "category"}, {"description": "Filter based on severity", "help": "Filter based on severity.", "label": "Threshold", "name": "threshold"}]]  # How to filter log messages that are sent to alert emails.
    email_interval: NotRequired[int]  # Interval between sending alert emails (1 - 99999 min, defaul
    IPS_logs: NotRequired[Literal[{"description": "Enable IPS logs in alert email", "help": "Enable IPS logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS logs in alert email", "help": "Disable IPS logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable IPS logs in alert email.
    firewall_authentication_failure_logs: NotRequired[Literal[{"description": "Enable firewall authentication failure logs in alert email", "help": "Enable firewall authentication failure logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable firewall authentication failure logs in alert email", "help": "Disable firewall authentication failure logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable firewall authentication failure logs in alert
    HA_logs: NotRequired[Literal[{"description": "Enable HA logs in alert email", "help": "Enable HA logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable HA logs in alert email", "help": "Disable HA logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable HA logs in alert email.
    IPsec_errors_logs: NotRequired[Literal[{"description": "Enable IPsec error logs in alert email", "help": "Enable IPsec error logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable IPsec error logs in alert email", "help": "Disable IPsec error logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable IPsec error logs in alert email.
    FDS_update_logs: NotRequired[Literal[{"description": "Enable FortiGuard update logs in alert email", "help": "Enable FortiGuard update logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard update logs in alert email", "help": "Disable FortiGuard update logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiGuard update logs in alert email.
    PPP_errors_logs: NotRequired[Literal[{"description": "Enable PPP error logs in alert email", "help": "Enable PPP error logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable PPP error logs in alert email", "help": "Disable PPP error logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable PPP error logs in alert email.
    sslvpn_authentication_errors_logs: NotRequired[Literal[{"help": "Enable Agentless VPN authentication error logs in alert email.", "label": "Enable", "name": "enable"}, {"help": "Disable Agentless VPN authentication error logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable Agentless VPN authentication error logs in al
    antivirus_logs: NotRequired[Literal[{"description": "Enable antivirus logs in alert email", "help": "Enable antivirus logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable antivirus logs in alert email", "help": "Disable antivirus logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable antivirus logs in alert email.
    webfilter_logs: NotRequired[Literal[{"description": "Enable web filter logs in alert email", "help": "Enable web filter logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable web filter logs in alert email", "help": "Disable web filter logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable web filter logs in alert email.
    configuration_changes_logs: NotRequired[Literal[{"description": "Enable configuration change logs in alert email", "help": "Enable configuration change logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable configuration change logs in alert email", "help": "Disable configuration change logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable configuration change logs in alert email.
    violation_traffic_logs: NotRequired[Literal[{"description": "Enable violation traffic logs in alert email", "help": "Enable violation traffic logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable violation traffic logs in alert email", "help": "Disable violation traffic logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable violation traffic logs in alert email.
    admin_login_logs: NotRequired[Literal[{"description": "Enable administrator login/logout logs in alert email", "help": "Enable administrator login/logout logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable administrator login/logout logs in alert email", "help": "Disable administrator login/logout logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable administrator login/logout logs in alert emai
    FDS_license_expiring_warning: NotRequired[Literal[{"description": "Enable FortiGuard license expiration warnings in alert email", "help": "Enable FortiGuard license expiration warnings in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard license expiration warnings in alert email", "help": "Disable FortiGuard license expiration warnings in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiGuard license expiration warnings in ale
    log_disk_usage_warning: NotRequired[Literal[{"description": "Enable disk usage warnings in alert email", "help": "Enable disk usage warnings in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable disk usage warnings in alert email", "help": "Disable disk usage warnings in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable disk usage warnings in alert email.
    fortiguard_log_quota_warning: NotRequired[Literal[{"description": "Enable FortiCloud log quota warnings in alert email", "help": "Enable FortiCloud log quota warnings in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud log quota warnings in alert email", "help": "Disable FortiCloud log quota warnings in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiCloud log quota warnings in alert email.
    amc_interface_bypass_mode: NotRequired[Literal[{"description": "Enable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email", "help": "Enable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email", "help": "Disable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable Fortinet Advanced Mezzanine Card (AMC) interf
    FIPS_CC_errors: NotRequired[Literal[{"description": "Enable FIPS and Common Criteria error logs in alert email", "help": "Enable FIPS and Common Criteria error logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FIPS and Common Criteria error logs in alert email", "help": "Disable FIPS and Common Criteria error logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable FIPS and Common Criteria error logs in alert 
    FSSO_disconnect_logs: NotRequired[Literal[{"description": "Enable logging of FSSO collector agent disconnect", "help": "Enable logging of FSSO collector agent disconnect.", "label": "Enable", "name": "enable"}, {"description": "Disable logging of FSSO collector agent disconnect", "help": "Disable logging of FSSO collector agent disconnect.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging of FSSO collector agent disconnect.
    ssh_logs: NotRequired[Literal[{"description": "Enable SSH logs in alert email", "help": "Enable SSH logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable SSH logs in alert email", "help": "Disable SSH logs in alert email.", "label": "Disable", "name": "disable"}]]  # Enable/disable SSH logs in alert email.
    local_disk_usage: NotRequired[int]  # Disk usage percentage at which to send alert email (1 - 99 p
    emergency_interval: NotRequired[int]  # Emergency alert interval in minutes.
    alert_interval: NotRequired[int]  # Alert alert interval in minutes.
    critical_interval: NotRequired[int]  # Critical alert interval in minutes.
    error_interval: NotRequired[int]  # Error alert interval in minutes.
    warning_interval: NotRequired[int]  # Warning alert interval in minutes.
    notification_interval: NotRequired[int]  # Notification alert interval in minutes.
    information_interval: NotRequired[int]  # Information alert interval in minutes.
    debug_interval: NotRequired[int]  # Debug alert interval in minutes.
    severity: NotRequired[Literal[{"description": "Emergency level", "help": "Emergency level.", "label": "Emergency", "name": "emergency"}, {"description": "Alert level", "help": "Alert level.", "label": "Alert", "name": "alert"}, {"description": "Critical level", "help": "Critical level.", "label": "Critical", "name": "critical"}, {"description": "Error level", "help": "Error level.", "label": "Error", "name": "error"}, {"description": "Warning level", "help": "Warning level.", "label": "Warning", "name": "warning"}, {"description": "Notification level", "help": "Notification level.", "label": "Notification", "name": "notification"}, {"description": "Information level", "help": "Information level.", "label": "Information", "name": "information"}, {"description": "Debug level", "help": "Debug level.", "label": "Debug", "name": "debug"}]]  # Lowest severity level to log.


class Setting:
    """
    Configure alert email settings.
    
    Path: alertemail/setting
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
        username: str | None = ...,
        mailto1: str | None = ...,
        mailto2: str | None = ...,
        mailto3: str | None = ...,
        filter_mode: Literal[{"description": "Filter based on category", "help": "Filter based on category.", "label": "Category", "name": "category"}, {"description": "Filter based on severity", "help": "Filter based on severity.", "label": "Threshold", "name": "threshold"}] | None = ...,
        email_interval: int | None = ...,
        IPS_logs: Literal[{"description": "Enable IPS logs in alert email", "help": "Enable IPS logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS logs in alert email", "help": "Disable IPS logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        firewall_authentication_failure_logs: Literal[{"description": "Enable firewall authentication failure logs in alert email", "help": "Enable firewall authentication failure logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable firewall authentication failure logs in alert email", "help": "Disable firewall authentication failure logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        HA_logs: Literal[{"description": "Enable HA logs in alert email", "help": "Enable HA logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable HA logs in alert email", "help": "Disable HA logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        IPsec_errors_logs: Literal[{"description": "Enable IPsec error logs in alert email", "help": "Enable IPsec error logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable IPsec error logs in alert email", "help": "Disable IPsec error logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        FDS_update_logs: Literal[{"description": "Enable FortiGuard update logs in alert email", "help": "Enable FortiGuard update logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard update logs in alert email", "help": "Disable FortiGuard update logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        PPP_errors_logs: Literal[{"description": "Enable PPP error logs in alert email", "help": "Enable PPP error logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable PPP error logs in alert email", "help": "Disable PPP error logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        sslvpn_authentication_errors_logs: Literal[{"help": "Enable Agentless VPN authentication error logs in alert email.", "label": "Enable", "name": "enable"}, {"help": "Disable Agentless VPN authentication error logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        antivirus_logs: Literal[{"description": "Enable antivirus logs in alert email", "help": "Enable antivirus logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable antivirus logs in alert email", "help": "Disable antivirus logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        webfilter_logs: Literal[{"description": "Enable web filter logs in alert email", "help": "Enable web filter logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable web filter logs in alert email", "help": "Disable web filter logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        configuration_changes_logs: Literal[{"description": "Enable configuration change logs in alert email", "help": "Enable configuration change logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable configuration change logs in alert email", "help": "Disable configuration change logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        violation_traffic_logs: Literal[{"description": "Enable violation traffic logs in alert email", "help": "Enable violation traffic logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable violation traffic logs in alert email", "help": "Disable violation traffic logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        admin_login_logs: Literal[{"description": "Enable administrator login/logout logs in alert email", "help": "Enable administrator login/logout logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable administrator login/logout logs in alert email", "help": "Disable administrator login/logout logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        FDS_license_expiring_warning: Literal[{"description": "Enable FortiGuard license expiration warnings in alert email", "help": "Enable FortiGuard license expiration warnings in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard license expiration warnings in alert email", "help": "Disable FortiGuard license expiration warnings in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        log_disk_usage_warning: Literal[{"description": "Enable disk usage warnings in alert email", "help": "Enable disk usage warnings in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable disk usage warnings in alert email", "help": "Disable disk usage warnings in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        fortiguard_log_quota_warning: Literal[{"description": "Enable FortiCloud log quota warnings in alert email", "help": "Enable FortiCloud log quota warnings in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud log quota warnings in alert email", "help": "Disable FortiCloud log quota warnings in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        amc_interface_bypass_mode: Literal[{"description": "Enable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email", "help": "Enable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email", "help": "Disable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        FIPS_CC_errors: Literal[{"description": "Enable FIPS and Common Criteria error logs in alert email", "help": "Enable FIPS and Common Criteria error logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FIPS and Common Criteria error logs in alert email", "help": "Disable FIPS and Common Criteria error logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        FSSO_disconnect_logs: Literal[{"description": "Enable logging of FSSO collector agent disconnect", "help": "Enable logging of FSSO collector agent disconnect.", "label": "Enable", "name": "enable"}, {"description": "Disable logging of FSSO collector agent disconnect", "help": "Disable logging of FSSO collector agent disconnect.", "label": "Disable", "name": "disable"}] | None = ...,
        ssh_logs: Literal[{"description": "Enable SSH logs in alert email", "help": "Enable SSH logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable SSH logs in alert email", "help": "Disable SSH logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        local_disk_usage: int | None = ...,
        emergency_interval: int | None = ...,
        alert_interval: int | None = ...,
        critical_interval: int | None = ...,
        error_interval: int | None = ...,
        warning_interval: int | None = ...,
        notification_interval: int | None = ...,
        information_interval: int | None = ...,
        debug_interval: int | None = ...,
        severity: Literal[{"description": "Emergency level", "help": "Emergency level.", "label": "Emergency", "name": "emergency"}, {"description": "Alert level", "help": "Alert level.", "label": "Alert", "name": "alert"}, {"description": "Critical level", "help": "Critical level.", "label": "Critical", "name": "critical"}, {"description": "Error level", "help": "Error level.", "label": "Error", "name": "error"}, {"description": "Warning level", "help": "Warning level.", "label": "Warning", "name": "warning"}, {"description": "Notification level", "help": "Notification level.", "label": "Notification", "name": "notification"}, {"description": "Information level", "help": "Information level.", "label": "Information", "name": "information"}, {"description": "Debug level", "help": "Debug level.", "label": "Debug", "name": "debug"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SettingPayload | None = ...,
        username: str | None = ...,
        mailto1: str | None = ...,
        mailto2: str | None = ...,
        mailto3: str | None = ...,
        filter_mode: Literal[{"description": "Filter based on category", "help": "Filter based on category.", "label": "Category", "name": "category"}, {"description": "Filter based on severity", "help": "Filter based on severity.", "label": "Threshold", "name": "threshold"}] | None = ...,
        email_interval: int | None = ...,
        IPS_logs: Literal[{"description": "Enable IPS logs in alert email", "help": "Enable IPS logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS logs in alert email", "help": "Disable IPS logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        firewall_authentication_failure_logs: Literal[{"description": "Enable firewall authentication failure logs in alert email", "help": "Enable firewall authentication failure logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable firewall authentication failure logs in alert email", "help": "Disable firewall authentication failure logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        HA_logs: Literal[{"description": "Enable HA logs in alert email", "help": "Enable HA logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable HA logs in alert email", "help": "Disable HA logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        IPsec_errors_logs: Literal[{"description": "Enable IPsec error logs in alert email", "help": "Enable IPsec error logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable IPsec error logs in alert email", "help": "Disable IPsec error logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        FDS_update_logs: Literal[{"description": "Enable FortiGuard update logs in alert email", "help": "Enable FortiGuard update logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard update logs in alert email", "help": "Disable FortiGuard update logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        PPP_errors_logs: Literal[{"description": "Enable PPP error logs in alert email", "help": "Enable PPP error logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable PPP error logs in alert email", "help": "Disable PPP error logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        sslvpn_authentication_errors_logs: Literal[{"help": "Enable Agentless VPN authentication error logs in alert email.", "label": "Enable", "name": "enable"}, {"help": "Disable Agentless VPN authentication error logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        antivirus_logs: Literal[{"description": "Enable antivirus logs in alert email", "help": "Enable antivirus logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable antivirus logs in alert email", "help": "Disable antivirus logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        webfilter_logs: Literal[{"description": "Enable web filter logs in alert email", "help": "Enable web filter logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable web filter logs in alert email", "help": "Disable web filter logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        configuration_changes_logs: Literal[{"description": "Enable configuration change logs in alert email", "help": "Enable configuration change logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable configuration change logs in alert email", "help": "Disable configuration change logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        violation_traffic_logs: Literal[{"description": "Enable violation traffic logs in alert email", "help": "Enable violation traffic logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable violation traffic logs in alert email", "help": "Disable violation traffic logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        admin_login_logs: Literal[{"description": "Enable administrator login/logout logs in alert email", "help": "Enable administrator login/logout logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable administrator login/logout logs in alert email", "help": "Disable administrator login/logout logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        FDS_license_expiring_warning: Literal[{"description": "Enable FortiGuard license expiration warnings in alert email", "help": "Enable FortiGuard license expiration warnings in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard license expiration warnings in alert email", "help": "Disable FortiGuard license expiration warnings in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        log_disk_usage_warning: Literal[{"description": "Enable disk usage warnings in alert email", "help": "Enable disk usage warnings in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable disk usage warnings in alert email", "help": "Disable disk usage warnings in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        fortiguard_log_quota_warning: Literal[{"description": "Enable FortiCloud log quota warnings in alert email", "help": "Enable FortiCloud log quota warnings in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud log quota warnings in alert email", "help": "Disable FortiCloud log quota warnings in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        amc_interface_bypass_mode: Literal[{"description": "Enable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email", "help": "Enable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email", "help": "Disable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        FIPS_CC_errors: Literal[{"description": "Enable FIPS and Common Criteria error logs in alert email", "help": "Enable FIPS and Common Criteria error logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FIPS and Common Criteria error logs in alert email", "help": "Disable FIPS and Common Criteria error logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        FSSO_disconnect_logs: Literal[{"description": "Enable logging of FSSO collector agent disconnect", "help": "Enable logging of FSSO collector agent disconnect.", "label": "Enable", "name": "enable"}, {"description": "Disable logging of FSSO collector agent disconnect", "help": "Disable logging of FSSO collector agent disconnect.", "label": "Disable", "name": "disable"}] | None = ...,
        ssh_logs: Literal[{"description": "Enable SSH logs in alert email", "help": "Enable SSH logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable SSH logs in alert email", "help": "Disable SSH logs in alert email.", "label": "Disable", "name": "disable"}] | None = ...,
        local_disk_usage: int | None = ...,
        emergency_interval: int | None = ...,
        alert_interval: int | None = ...,
        critical_interval: int | None = ...,
        error_interval: int | None = ...,
        warning_interval: int | None = ...,
        notification_interval: int | None = ...,
        information_interval: int | None = ...,
        debug_interval: int | None = ...,
        severity: Literal[{"description": "Emergency level", "help": "Emergency level.", "label": "Emergency", "name": "emergency"}, {"description": "Alert level", "help": "Alert level.", "label": "Alert", "name": "alert"}, {"description": "Critical level", "help": "Critical level.", "label": "Critical", "name": "critical"}, {"description": "Error level", "help": "Error level.", "label": "Error", "name": "error"}, {"description": "Warning level", "help": "Warning level.", "label": "Warning", "name": "warning"}, {"description": "Notification level", "help": "Notification level.", "label": "Notification", "name": "notification"}, {"description": "Information level", "help": "Information level.", "label": "Information", "name": "information"}, {"description": "Debug level", "help": "Debug level.", "label": "Debug", "name": "debug"}] | None = ...,
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