from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class AutomationTriggerPayload(TypedDict, total=False):
    """
    Type hints for system/automation_trigger payload fields.
    
    Trigger for automation stitches.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.automation-stitch.AutomationStitchEndpoint` (via: stitch-name)

    **Usage:**
        payload: AutomationTriggerPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Name.
    description: NotRequired[str]  # Description.
    trigger_type: NotRequired[Literal[{"description": "Event based trigger", "help": "Event based trigger.", "label": "Event Based", "name": "event-based"}, {"description": "Scheduled trigger", "help": "Scheduled trigger.", "label": "Scheduled", "name": "scheduled"}]]  # Trigger type.
    event_type: NotRequired[Literal[{"description": "Indicator of compromise detected", "help": "Indicator of compromise detected.", "label": "Ioc", "name": "ioc"}, {"description": "Use log ID as trigger", "help": "Use log ID as trigger.", "label": "Event Log", "name": "event-log"}, {"description": "Device reboot", "help": "Device reboot.", "label": "Reboot", "name": "reboot"}, {"description": "Conserve mode due to low memory", "help": "Conserve mode due to low memory.", "label": "Low Memory", "name": "low-memory"}, {"description": "High CPU usage", "help": "High CPU usage.", "label": "High Cpu", "name": "high-cpu"}, {"description": "License near expiration date", "help": "License near expiration date.", "label": "License Near Expiry", "name": "license-near-expiry"}, {"description": "The local certificate near expiration date", "help": "The local certificate near expiration date.", "label": "Local Cert Near Expiry", "name": "local-cert-near-expiry"}, {"description": "HA failover", "help": "HA failover.", "label": "Ha Failover", "name": "ha-failover"}, {"description": "Configuration change", "help": "Configuration change.", "label": "Config Change", "name": "config-change"}, {"description": "Security rating summary", "help": "Security rating summary.", "label": "Security Rating Summary", "name": "security-rating-summary"}, {"description": "Virus and IPS database updated", "help": "Virus and IPS database updated.", "label": "Virus Ips Db Updated", "name": "virus-ips-db-updated"}, {"description": "FortiAnalyzer event", "help": "FortiAnalyzer event.", "label": "Faz Event", "name": "faz-event"}, {"description": "Incoming webhook call", "help": "Incoming webhook call.", "label": "Incoming Webhook", "name": "incoming-webhook"}, {"description": "Fabric connector event", "help": "Fabric connector event.", "label": "Fabric Event", "name": "fabric-event"}, {"description": "IPS logs", "help": "IPS logs.", "label": "Ips Logs", "name": "ips-logs"}, {"description": "Anomaly logs", "help": "Anomaly logs.", "label": "Anomaly Logs", "name": "anomaly-logs"}, {"description": "Virus logs", "help": "Virus logs.", "label": "Virus Logs", "name": "virus-logs"}, {"description": "SSH logs", "help": "SSH logs.", "label": "Ssh Logs", "name": "ssh-logs"}, {"description": "Webfilter violation", "help": "Webfilter violation.", "label": "Webfilter Violation", "name": "webfilter-violation"}, {"description": "Traffic violation", "help": "Traffic violation.", "label": "Traffic Violation", "name": "traffic-violation"}, {"description": "Specified stitch has been triggered", "help": "Specified stitch has been triggered.", "label": "Stitch", "name": "stitch"}]]  # Event type.
    vdom: NotRequired[list[dict[str, Any]]]  # Virtual domain(s) that this trigger is valid for.
    license_type: NotRequired[Literal[{"description": "FortiCare support license", "help": "FortiCare support license.", "label": "Forticare Support", "name": "forticare-support"}, {"description": "FortiGuard web filter license", "help": "FortiGuard web filter license.", "label": "Fortiguard Webfilter", "name": "fortiguard-webfilter"}, {"description": "FortiGuard antispam license", "help": "FortiGuard antispam license.", "label": "Fortiguard Antispam", "name": "fortiguard-antispam"}, {"description": "FortiGuard AntiVirus license", "help": "FortiGuard AntiVirus license.", "label": "Fortiguard Antivirus", "name": "fortiguard-antivirus"}, {"description": "FortiGuard IPS license", "help": "FortiGuard IPS license.", "label": "Fortiguard Ips", "name": "fortiguard-ips"}, {"description": "FortiGuard management service license", "help": "FortiGuard management service license.", "label": "Fortiguard Management", "name": "fortiguard-management"}, {"description": "FortiCloud license", "help": "FortiCloud license.", "label": "Forticloud", "name": "forticloud"}, {"description": "Any license", "help": "Any license.", "label": "Any", "name": "any"}]]  # License type.
    report_type: NotRequired[Literal[{"description": "Posture report", "help": "Posture report.", "label": "Posture", "name": "posture"}, {"description": "Coverage report", "help": "Coverage report.", "label": "Coverage", "name": "coverage"}, {"description": "Optimization report    any:Any report", "help": "Optimization report", "label": "Optimization", "name": "optimization"}, {"help": "Any report.", "label": "Any", "name": "any"}]]  # Security Rating report.
    stitch_name: str  # Triggering stitch name.
    logid: NotRequired[list[dict[str, Any]]]  # Log IDs to trigger event.
    trigger_frequency: NotRequired[Literal[{"description": "Run hourly", "help": "Run hourly.", "label": "Hourly", "name": "hourly"}, {"description": "Run daily", "help": "Run daily.", "label": "Daily", "name": "daily"}, {"description": "Run weekly", "help": "Run weekly.", "label": "Weekly", "name": "weekly"}, {"description": "Run monthly", "help": "Run monthly.", "label": "Monthly", "name": "monthly"}, {"description": "Run once at specified date time", "help": "Run once at specified date time.", "label": "Once", "name": "once"}]]  # Scheduled trigger frequency (default = daily).
    trigger_weekday: NotRequired[Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}]]  # Day of week for trigger.
    trigger_day: NotRequired[int]  # Day within a month to trigger.
    trigger_hour: NotRequired[int]  # Hour of the day on which to trigger (0 - 23, default = 1).
    trigger_minute: NotRequired[int]  # Minute of the hour on which to trigger (0 - 59, default = 0)
    trigger_datetime: NotRequired[str]  # Trigger date and time (YYYY-MM-DD HH:MM:SS).
    fields: NotRequired[list[dict[str, Any]]]  # Customized trigger field settings.
    faz_event_name: str  # FortiAnalyzer event handler name.
    faz_event_severity: NotRequired[str]  # FortiAnalyzer event severity.
    faz_event_tags: NotRequired[str]  # FortiAnalyzer event tags.
    serial: str  # Fabric connector serial number.
    fabric_event_name: str  # Fabric connector event handler name.
    fabric_event_severity: NotRequired[str]  # Fabric connector event severity.


class AutomationTrigger:
    """
    Trigger for automation stitches.
    
    Path: system/automation_trigger
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
        payload_dict: AutomationTriggerPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        trigger_type: Literal[{"description": "Event based trigger", "help": "Event based trigger.", "label": "Event Based", "name": "event-based"}, {"description": "Scheduled trigger", "help": "Scheduled trigger.", "label": "Scheduled", "name": "scheduled"}] | None = ...,
        event_type: Literal[{"description": "Indicator of compromise detected", "help": "Indicator of compromise detected.", "label": "Ioc", "name": "ioc"}, {"description": "Use log ID as trigger", "help": "Use log ID as trigger.", "label": "Event Log", "name": "event-log"}, {"description": "Device reboot", "help": "Device reboot.", "label": "Reboot", "name": "reboot"}, {"description": "Conserve mode due to low memory", "help": "Conserve mode due to low memory.", "label": "Low Memory", "name": "low-memory"}, {"description": "High CPU usage", "help": "High CPU usage.", "label": "High Cpu", "name": "high-cpu"}, {"description": "License near expiration date", "help": "License near expiration date.", "label": "License Near Expiry", "name": "license-near-expiry"}, {"description": "The local certificate near expiration date", "help": "The local certificate near expiration date.", "label": "Local Cert Near Expiry", "name": "local-cert-near-expiry"}, {"description": "HA failover", "help": "HA failover.", "label": "Ha Failover", "name": "ha-failover"}, {"description": "Configuration change", "help": "Configuration change.", "label": "Config Change", "name": "config-change"}, {"description": "Security rating summary", "help": "Security rating summary.", "label": "Security Rating Summary", "name": "security-rating-summary"}, {"description": "Virus and IPS database updated", "help": "Virus and IPS database updated.", "label": "Virus Ips Db Updated", "name": "virus-ips-db-updated"}, {"description": "FortiAnalyzer event", "help": "FortiAnalyzer event.", "label": "Faz Event", "name": "faz-event"}, {"description": "Incoming webhook call", "help": "Incoming webhook call.", "label": "Incoming Webhook", "name": "incoming-webhook"}, {"description": "Fabric connector event", "help": "Fabric connector event.", "label": "Fabric Event", "name": "fabric-event"}, {"description": "IPS logs", "help": "IPS logs.", "label": "Ips Logs", "name": "ips-logs"}, {"description": "Anomaly logs", "help": "Anomaly logs.", "label": "Anomaly Logs", "name": "anomaly-logs"}, {"description": "Virus logs", "help": "Virus logs.", "label": "Virus Logs", "name": "virus-logs"}, {"description": "SSH logs", "help": "SSH logs.", "label": "Ssh Logs", "name": "ssh-logs"}, {"description": "Webfilter violation", "help": "Webfilter violation.", "label": "Webfilter Violation", "name": "webfilter-violation"}, {"description": "Traffic violation", "help": "Traffic violation.", "label": "Traffic Violation", "name": "traffic-violation"}, {"description": "Specified stitch has been triggered", "help": "Specified stitch has been triggered.", "label": "Stitch", "name": "stitch"}] | None = ...,
        license_type: Literal[{"description": "FortiCare support license", "help": "FortiCare support license.", "label": "Forticare Support", "name": "forticare-support"}, {"description": "FortiGuard web filter license", "help": "FortiGuard web filter license.", "label": "Fortiguard Webfilter", "name": "fortiguard-webfilter"}, {"description": "FortiGuard antispam license", "help": "FortiGuard antispam license.", "label": "Fortiguard Antispam", "name": "fortiguard-antispam"}, {"description": "FortiGuard AntiVirus license", "help": "FortiGuard AntiVirus license.", "label": "Fortiguard Antivirus", "name": "fortiguard-antivirus"}, {"description": "FortiGuard IPS license", "help": "FortiGuard IPS license.", "label": "Fortiguard Ips", "name": "fortiguard-ips"}, {"description": "FortiGuard management service license", "help": "FortiGuard management service license.", "label": "Fortiguard Management", "name": "fortiguard-management"}, {"description": "FortiCloud license", "help": "FortiCloud license.", "label": "Forticloud", "name": "forticloud"}, {"description": "Any license", "help": "Any license.", "label": "Any", "name": "any"}] | None = ...,
        report_type: Literal[{"description": "Posture report", "help": "Posture report.", "label": "Posture", "name": "posture"}, {"description": "Coverage report", "help": "Coverage report.", "label": "Coverage", "name": "coverage"}, {"description": "Optimization report    any:Any report", "help": "Optimization report", "label": "Optimization", "name": "optimization"}, {"help": "Any report.", "label": "Any", "name": "any"}] | None = ...,
        stitch_name: str | None = ...,
        logid: list[dict[str, Any]] | None = ...,
        trigger_frequency: Literal[{"description": "Run hourly", "help": "Run hourly.", "label": "Hourly", "name": "hourly"}, {"description": "Run daily", "help": "Run daily.", "label": "Daily", "name": "daily"}, {"description": "Run weekly", "help": "Run weekly.", "label": "Weekly", "name": "weekly"}, {"description": "Run monthly", "help": "Run monthly.", "label": "Monthly", "name": "monthly"}, {"description": "Run once at specified date time", "help": "Run once at specified date time.", "label": "Once", "name": "once"}] | None = ...,
        trigger_weekday: Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}] | None = ...,
        trigger_day: int | None = ...,
        trigger_hour: int | None = ...,
        trigger_minute: int | None = ...,
        trigger_datetime: str | None = ...,
        fields: list[dict[str, Any]] | None = ...,
        faz_event_name: str | None = ...,
        faz_event_severity: str | None = ...,
        faz_event_tags: str | None = ...,
        serial: str | None = ...,
        fabric_event_name: str | None = ...,
        fabric_event_severity: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: AutomationTriggerPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        trigger_type: Literal[{"description": "Event based trigger", "help": "Event based trigger.", "label": "Event Based", "name": "event-based"}, {"description": "Scheduled trigger", "help": "Scheduled trigger.", "label": "Scheduled", "name": "scheduled"}] | None = ...,
        event_type: Literal[{"description": "Indicator of compromise detected", "help": "Indicator of compromise detected.", "label": "Ioc", "name": "ioc"}, {"description": "Use log ID as trigger", "help": "Use log ID as trigger.", "label": "Event Log", "name": "event-log"}, {"description": "Device reboot", "help": "Device reboot.", "label": "Reboot", "name": "reboot"}, {"description": "Conserve mode due to low memory", "help": "Conserve mode due to low memory.", "label": "Low Memory", "name": "low-memory"}, {"description": "High CPU usage", "help": "High CPU usage.", "label": "High Cpu", "name": "high-cpu"}, {"description": "License near expiration date", "help": "License near expiration date.", "label": "License Near Expiry", "name": "license-near-expiry"}, {"description": "The local certificate near expiration date", "help": "The local certificate near expiration date.", "label": "Local Cert Near Expiry", "name": "local-cert-near-expiry"}, {"description": "HA failover", "help": "HA failover.", "label": "Ha Failover", "name": "ha-failover"}, {"description": "Configuration change", "help": "Configuration change.", "label": "Config Change", "name": "config-change"}, {"description": "Security rating summary", "help": "Security rating summary.", "label": "Security Rating Summary", "name": "security-rating-summary"}, {"description": "Virus and IPS database updated", "help": "Virus and IPS database updated.", "label": "Virus Ips Db Updated", "name": "virus-ips-db-updated"}, {"description": "FortiAnalyzer event", "help": "FortiAnalyzer event.", "label": "Faz Event", "name": "faz-event"}, {"description": "Incoming webhook call", "help": "Incoming webhook call.", "label": "Incoming Webhook", "name": "incoming-webhook"}, {"description": "Fabric connector event", "help": "Fabric connector event.", "label": "Fabric Event", "name": "fabric-event"}, {"description": "IPS logs", "help": "IPS logs.", "label": "Ips Logs", "name": "ips-logs"}, {"description": "Anomaly logs", "help": "Anomaly logs.", "label": "Anomaly Logs", "name": "anomaly-logs"}, {"description": "Virus logs", "help": "Virus logs.", "label": "Virus Logs", "name": "virus-logs"}, {"description": "SSH logs", "help": "SSH logs.", "label": "Ssh Logs", "name": "ssh-logs"}, {"description": "Webfilter violation", "help": "Webfilter violation.", "label": "Webfilter Violation", "name": "webfilter-violation"}, {"description": "Traffic violation", "help": "Traffic violation.", "label": "Traffic Violation", "name": "traffic-violation"}, {"description": "Specified stitch has been triggered", "help": "Specified stitch has been triggered.", "label": "Stitch", "name": "stitch"}] | None = ...,
        license_type: Literal[{"description": "FortiCare support license", "help": "FortiCare support license.", "label": "Forticare Support", "name": "forticare-support"}, {"description": "FortiGuard web filter license", "help": "FortiGuard web filter license.", "label": "Fortiguard Webfilter", "name": "fortiguard-webfilter"}, {"description": "FortiGuard antispam license", "help": "FortiGuard antispam license.", "label": "Fortiguard Antispam", "name": "fortiguard-antispam"}, {"description": "FortiGuard AntiVirus license", "help": "FortiGuard AntiVirus license.", "label": "Fortiguard Antivirus", "name": "fortiguard-antivirus"}, {"description": "FortiGuard IPS license", "help": "FortiGuard IPS license.", "label": "Fortiguard Ips", "name": "fortiguard-ips"}, {"description": "FortiGuard management service license", "help": "FortiGuard management service license.", "label": "Fortiguard Management", "name": "fortiguard-management"}, {"description": "FortiCloud license", "help": "FortiCloud license.", "label": "Forticloud", "name": "forticloud"}, {"description": "Any license", "help": "Any license.", "label": "Any", "name": "any"}] | None = ...,
        report_type: Literal[{"description": "Posture report", "help": "Posture report.", "label": "Posture", "name": "posture"}, {"description": "Coverage report", "help": "Coverage report.", "label": "Coverage", "name": "coverage"}, {"description": "Optimization report    any:Any report", "help": "Optimization report", "label": "Optimization", "name": "optimization"}, {"help": "Any report.", "label": "Any", "name": "any"}] | None = ...,
        stitch_name: str | None = ...,
        logid: list[dict[str, Any]] | None = ...,
        trigger_frequency: Literal[{"description": "Run hourly", "help": "Run hourly.", "label": "Hourly", "name": "hourly"}, {"description": "Run daily", "help": "Run daily.", "label": "Daily", "name": "daily"}, {"description": "Run weekly", "help": "Run weekly.", "label": "Weekly", "name": "weekly"}, {"description": "Run monthly", "help": "Run monthly.", "label": "Monthly", "name": "monthly"}, {"description": "Run once at specified date time", "help": "Run once at specified date time.", "label": "Once", "name": "once"}] | None = ...,
        trigger_weekday: Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}] | None = ...,
        trigger_day: int | None = ...,
        trigger_hour: int | None = ...,
        trigger_minute: int | None = ...,
        trigger_datetime: str | None = ...,
        fields: list[dict[str, Any]] | None = ...,
        faz_event_name: str | None = ...,
        faz_event_severity: str | None = ...,
        faz_event_tags: str | None = ...,
        serial: str | None = ...,
        fabric_event_name: str | None = ...,
        fabric_event_severity: str | None = ...,
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
        payload_dict: AutomationTriggerPayload | None = ...,
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
    "AutomationTrigger",
    "AutomationTriggerPayload",
]