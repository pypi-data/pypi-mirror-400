from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class AutomationActionPayload(TypedDict, total=False):
    """
    Type hints for system/automation_action payload fields.
    
    Action for automation stitches.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.local.LocalEndpoint` (via: tls-certificate)
        - :class:`~.system.accprofile.AccprofileEndpoint` (via: accprofile)
        - :class:`~.system.replacemsg-group.ReplacemsgGroupEndpoint` (via: replacemsg-group)

    **Usage:**
        payload: AutomationActionPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Name.
    description: NotRequired[str]  # Description.
    action_type: NotRequired[Literal[{"description": "Send notification email", "help": "Send notification email.", "label": "Email", "name": "email"}, {"description": "Send push notification to FortiExplorer", "help": "Send push notification to FortiExplorer.", "label": "Fortiexplorer Notification", "name": "fortiexplorer-notification"}, {"description": "Generate FortiOS dashboard alert", "help": "Generate FortiOS dashboard alert.", "label": "Alert", "name": "alert"}, {"description": "Disable interface", "help": "Disable interface.", "label": "Disable Ssid", "name": "disable-ssid"}, {"description": "Perform immediate system operations on this FortiGate unit", "help": "Perform immediate system operations on this FortiGate unit.", "label": "System Actions", "name": "system-actions"}, {"description": "Quarantine host", "help": "Quarantine host.", "label": "Quarantine", "name": "quarantine"}, {"description": "Quarantine FortiClient by EMS", "help": "Quarantine FortiClient by EMS.", "label": "Quarantine Forticlient", "name": "quarantine-forticlient"}, {"description": "Quarantine NSX instance", "help": "Quarantine NSX instance.", "label": "Quarantine Nsx", "name": "quarantine-nsx"}, {"description": "Quarantine host by FortiNAC", "help": "Quarantine host by FortiNAC.", "label": "Quarantine Fortinac", "name": "quarantine-fortinac"}, {"description": "Ban IP address", "help": "Ban IP address.", "label": "Ban Ip", "name": "ban-ip"}, {"description": "Send log data to integrated AWS service", "help": "Send log data to integrated AWS service.", "label": "Aws Lambda", "name": "aws-lambda"}, {"description": "Send log data to an Azure function", "help": "Send log data to an Azure function.", "label": "Azure Function", "name": "azure-function"}, {"description": "Send log data to a Google Cloud function", "help": "Send log data to a Google Cloud function.", "label": "Google Cloud Function", "name": "google-cloud-function"}, {"description": "Send log data to an AliCloud function", "help": "Send log data to an AliCloud function.", "label": "Alicloud Function", "name": "alicloud-function"}, {"description": "Send an HTTP request", "help": "Send an HTTP request.", "label": "Webhook", "name": "webhook"}, {"description": "Run CLI script", "help": "Run CLI script.", "label": "Cli Script", "name": "cli-script"}, {"description": "Run diagnose script", "help": "Run diagnose script.", "label": "Diagnose Script", "name": "diagnose-script"}, {"description": "Match pattern on input text", "help": "Match pattern on input text.", "label": "Regular Expression", "name": "regular-expression"}, {"description": "Send a notification message to a Slack incoming webhook", "help": "Send a notification message to a Slack incoming webhook.", "label": "Slack Notification", "name": "slack-notification"}, {"description": "Send a notification message to a Microsoft Teams incoming webhook", "help": "Send a notification message to a Microsoft Teams incoming webhook.", "label": "Microsoft Teams Notification", "name": "microsoft-teams-notification"}]]  # Action type.
    system_action: Literal[{"description": "Reboot this FortiGate unit", "help": "Reboot this FortiGate unit.", "label": "Reboot", "name": "reboot"}, {"description": "Shutdown this FortiGate unit", "help": "Shutdown this FortiGate unit.", "label": "Shutdown", "name": "shutdown"}, {"description": "Backup current configuration to the disk revisions", "help": "Backup current configuration to the disk revisions.", "label": "Backup Config", "name": "backup-config"}]  # System action type.
    tls_certificate: NotRequired[str]  # Custom TLS certificate for API request.
    forticare_email: Literal[{"description": "Enable use of your FortiCare email address as the email-to address", "help": "Enable use of your FortiCare email address as the email-to address.", "label": "Enable", "name": "enable"}, {"description": "Disable use of your FortiCare email address as the email-to address", "help": "Disable use of your FortiCare email address as the email-to address.", "label": "Disable", "name": "disable"}]  # Enable/disable use of your FortiCare email address as the em
    email_to: NotRequired[list[dict[str, Any]]]  # Email addresses.
    email_from: NotRequired[str]  # Email sender name.
    email_subject: NotRequired[str]  # Email subject.
    minimum_interval: NotRequired[int]  # Limit execution to no more than once in this interval (in se
    aws_api_key: str  # AWS API Gateway API key.
    azure_function_authorization: Literal[{"description": "Anonymous authorization level (No authorization required)", "help": "Anonymous authorization level (No authorization required).", "label": "Anonymous", "name": "anonymous"}, {"description": "Function authorization level (Function or Host Key required)", "help": "Function authorization level (Function or Host Key required).", "label": "Function", "name": "function"}, {"description": "Admin authorization level (Master Host Key required)", "help": "Admin authorization level (Master Host Key required).", "label": "Admin", "name": "admin"}]  # Azure function authorization level.
    azure_api_key: NotRequired[str]  # Azure function API key.
    alicloud_function_authorization: Literal[{"description": "Anonymous authorization (No authorization required)", "help": "Anonymous authorization (No authorization required).", "label": "Anonymous", "name": "anonymous"}, {"description": "Function authorization (Authorization required)", "help": "Function authorization (Authorization required).", "label": "Function", "name": "function"}]  # AliCloud function authorization type.
    alicloud_access_key_id: str  # AliCloud AccessKey ID.
    alicloud_access_key_secret: str  # AliCloud AccessKey secret.
    message_type: Literal[{"description": "Plaintext", "help": "Plaintext.", "label": "Text", "name": "text"}, {"description": "Custom JSON", "help": "Custom JSON.", "label": "Json", "name": "json"}, {"description": "Multipart/form-data", "help": "Multipart/form-data", "label": "Form Data", "name": "form-data"}]  # Message type.
    message: str  # Message content.
    replacement_message: Literal[{"description": "Enable replacement message", "help": "Enable replacement message.", "label": "Enable", "name": "enable"}, {"description": "Disable replacement message", "help": "Disable replacement message.", "label": "Disable", "name": "disable"}]  # Enable/disable replacement message.
    replacemsg_group: NotRequired[str]  # Replacement message group.
    protocol: Literal[{"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}]  # Request protocol.
    method: Literal[{"description": "POST", "help": "POST.", "label": "Post", "name": "post"}, {"description": "PUT", "help": "PUT.", "label": "Put", "name": "put"}, {"description": "GET", "help": "GET.", "label": "Get", "name": "get"}, {"description": "PATCH", "help": "PATCH.", "label": "Patch", "name": "patch"}, {"description": "DELETE", "help": "DELETE.", "label": "Delete", "name": "delete"}]  # Request method (POST, PUT, GET, PATCH or DELETE).
    uri: str  # Request API URI.
    http_body: NotRequired[str]  # Request body (if necessary). Should be serialized json strin
    port: NotRequired[int]  # Protocol port.
    http_headers: NotRequired[list[dict[str, Any]]]  # Request headers.
    form_data: NotRequired[list[dict[str, Any]]]  # Form data parts for content type multipart/form-data.
    verify_host_cert: NotRequired[Literal[{"description": "Enable verification of the remote host certificate", "help": "Enable verification of the remote host certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable verification of the remote host certificate", "help": "Disable verification of the remote host certificate.", "label": "Disable", "name": "disable"}]]  # Enable/disable verification of the remote host certificate.
    script: str  # CLI script.
    output_size: NotRequired[int]  # Number of megabytes to limit script output to (1 - 1024, def
    timeout: NotRequired[int]  # Maximum running time for this script in seconds (0 = no time
    duration: NotRequired[int]  # Maximum running time for this script in seconds.
    output_interval: NotRequired[int]  # Collect the outputs for each output-interval in seconds (0 =
    file_only: NotRequired[Literal[{"description": "The output of the diag CLI will only be files", "help": "The output of the diag CLI will only be files.", "label": "Enable", "name": "enable"}, {"description": "The output of the diag CLI will be in raw text, output larger than 64KB will be in files", "help": "The output of the diag CLI will be in raw text, output larger than 64KB will be in files.", "label": "Disable", "name": "disable"}]]  # Enable/disable the output in files only.
    execute_security_fabric: NotRequired[Literal[{"description": "CLI script executes on all FortiGate units in the Security Fabric", "help": "CLI script executes on all FortiGate units in the Security Fabric.", "label": "Enable", "name": "enable"}, {"description": "CLI script executes only on the FortiGate unit that the stitch is triggered", "help": "CLI script executes only on the FortiGate unit that the stitch is triggered.", "label": "Disable", "name": "disable"}]]  # Enable/disable execution of CLI script on all or only one Fo
    accprofile: NotRequired[str]  # Access profile for CLI script action to access FortiGate fea
    regular_expression: str  # Regular expression string.
    log_debug_print: NotRequired[Literal[{"description": "Enable logging debug print output from diagnose action", "help": "Enable logging debug print output from diagnose action.", "label": "Enable", "name": "enable"}, {"description": "Disable logging debug print output from diagnose action", "help": "Disable logging debug print output from diagnose action.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging debug print output from diagnose acti
    security_tag: str  # NSX security tag.
    sdn_connector: NotRequired[list[dict[str, Any]]]  # NSX SDN connector names.


class AutomationAction:
    """
    Action for automation stitches.
    
    Path: system/automation_action
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
        payload_dict: AutomationActionPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        action_type: Literal[{"description": "Send notification email", "help": "Send notification email.", "label": "Email", "name": "email"}, {"description": "Send push notification to FortiExplorer", "help": "Send push notification to FortiExplorer.", "label": "Fortiexplorer Notification", "name": "fortiexplorer-notification"}, {"description": "Generate FortiOS dashboard alert", "help": "Generate FortiOS dashboard alert.", "label": "Alert", "name": "alert"}, {"description": "Disable interface", "help": "Disable interface.", "label": "Disable Ssid", "name": "disable-ssid"}, {"description": "Perform immediate system operations on this FortiGate unit", "help": "Perform immediate system operations on this FortiGate unit.", "label": "System Actions", "name": "system-actions"}, {"description": "Quarantine host", "help": "Quarantine host.", "label": "Quarantine", "name": "quarantine"}, {"description": "Quarantine FortiClient by EMS", "help": "Quarantine FortiClient by EMS.", "label": "Quarantine Forticlient", "name": "quarantine-forticlient"}, {"description": "Quarantine NSX instance", "help": "Quarantine NSX instance.", "label": "Quarantine Nsx", "name": "quarantine-nsx"}, {"description": "Quarantine host by FortiNAC", "help": "Quarantine host by FortiNAC.", "label": "Quarantine Fortinac", "name": "quarantine-fortinac"}, {"description": "Ban IP address", "help": "Ban IP address.", "label": "Ban Ip", "name": "ban-ip"}, {"description": "Send log data to integrated AWS service", "help": "Send log data to integrated AWS service.", "label": "Aws Lambda", "name": "aws-lambda"}, {"description": "Send log data to an Azure function", "help": "Send log data to an Azure function.", "label": "Azure Function", "name": "azure-function"}, {"description": "Send log data to a Google Cloud function", "help": "Send log data to a Google Cloud function.", "label": "Google Cloud Function", "name": "google-cloud-function"}, {"description": "Send log data to an AliCloud function", "help": "Send log data to an AliCloud function.", "label": "Alicloud Function", "name": "alicloud-function"}, {"description": "Send an HTTP request", "help": "Send an HTTP request.", "label": "Webhook", "name": "webhook"}, {"description": "Run CLI script", "help": "Run CLI script.", "label": "Cli Script", "name": "cli-script"}, {"description": "Run diagnose script", "help": "Run diagnose script.", "label": "Diagnose Script", "name": "diagnose-script"}, {"description": "Match pattern on input text", "help": "Match pattern on input text.", "label": "Regular Expression", "name": "regular-expression"}, {"description": "Send a notification message to a Slack incoming webhook", "help": "Send a notification message to a Slack incoming webhook.", "label": "Slack Notification", "name": "slack-notification"}, {"description": "Send a notification message to a Microsoft Teams incoming webhook", "help": "Send a notification message to a Microsoft Teams incoming webhook.", "label": "Microsoft Teams Notification", "name": "microsoft-teams-notification"}] | None = ...,
        system_action: Literal[{"description": "Reboot this FortiGate unit", "help": "Reboot this FortiGate unit.", "label": "Reboot", "name": "reboot"}, {"description": "Shutdown this FortiGate unit", "help": "Shutdown this FortiGate unit.", "label": "Shutdown", "name": "shutdown"}, {"description": "Backup current configuration to the disk revisions", "help": "Backup current configuration to the disk revisions.", "label": "Backup Config", "name": "backup-config"}] | None = ...,
        tls_certificate: str | None = ...,
        forticare_email: Literal[{"description": "Enable use of your FortiCare email address as the email-to address", "help": "Enable use of your FortiCare email address as the email-to address.", "label": "Enable", "name": "enable"}, {"description": "Disable use of your FortiCare email address as the email-to address", "help": "Disable use of your FortiCare email address as the email-to address.", "label": "Disable", "name": "disable"}] | None = ...,
        email_to: list[dict[str, Any]] | None = ...,
        email_from: str | None = ...,
        email_subject: str | None = ...,
        minimum_interval: int | None = ...,
        aws_api_key: str | None = ...,
        azure_function_authorization: Literal[{"description": "Anonymous authorization level (No authorization required)", "help": "Anonymous authorization level (No authorization required).", "label": "Anonymous", "name": "anonymous"}, {"description": "Function authorization level (Function or Host Key required)", "help": "Function authorization level (Function or Host Key required).", "label": "Function", "name": "function"}, {"description": "Admin authorization level (Master Host Key required)", "help": "Admin authorization level (Master Host Key required).", "label": "Admin", "name": "admin"}] | None = ...,
        azure_api_key: str | None = ...,
        alicloud_function_authorization: Literal[{"description": "Anonymous authorization (No authorization required)", "help": "Anonymous authorization (No authorization required).", "label": "Anonymous", "name": "anonymous"}, {"description": "Function authorization (Authorization required)", "help": "Function authorization (Authorization required).", "label": "Function", "name": "function"}] | None = ...,
        alicloud_access_key_id: str | None = ...,
        alicloud_access_key_secret: str | None = ...,
        message_type: Literal[{"description": "Plaintext", "help": "Plaintext.", "label": "Text", "name": "text"}, {"description": "Custom JSON", "help": "Custom JSON.", "label": "Json", "name": "json"}, {"description": "Multipart/form-data", "help": "Multipart/form-data", "label": "Form Data", "name": "form-data"}] | None = ...,
        message: str | None = ...,
        replacement_message: Literal[{"description": "Enable replacement message", "help": "Enable replacement message.", "label": "Enable", "name": "enable"}, {"description": "Disable replacement message", "help": "Disable replacement message.", "label": "Disable", "name": "disable"}] | None = ...,
        replacemsg_group: str | None = ...,
        protocol: Literal[{"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}] | None = ...,
        method: Literal[{"description": "POST", "help": "POST.", "label": "Post", "name": "post"}, {"description": "PUT", "help": "PUT.", "label": "Put", "name": "put"}, {"description": "GET", "help": "GET.", "label": "Get", "name": "get"}, {"description": "PATCH", "help": "PATCH.", "label": "Patch", "name": "patch"}, {"description": "DELETE", "help": "DELETE.", "label": "Delete", "name": "delete"}] | None = ...,
        uri: str | None = ...,
        http_body: str | None = ...,
        port: int | None = ...,
        http_headers: list[dict[str, Any]] | None = ...,
        form_data: list[dict[str, Any]] | None = ...,
        verify_host_cert: Literal[{"description": "Enable verification of the remote host certificate", "help": "Enable verification of the remote host certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable verification of the remote host certificate", "help": "Disable verification of the remote host certificate.", "label": "Disable", "name": "disable"}] | None = ...,
        script: str | None = ...,
        output_size: int | None = ...,
        timeout: int | None = ...,
        duration: int | None = ...,
        output_interval: int | None = ...,
        file_only: Literal[{"description": "The output of the diag CLI will only be files", "help": "The output of the diag CLI will only be files.", "label": "Enable", "name": "enable"}, {"description": "The output of the diag CLI will be in raw text, output larger than 64KB will be in files", "help": "The output of the diag CLI will be in raw text, output larger than 64KB will be in files.", "label": "Disable", "name": "disable"}] | None = ...,
        execute_security_fabric: Literal[{"description": "CLI script executes on all FortiGate units in the Security Fabric", "help": "CLI script executes on all FortiGate units in the Security Fabric.", "label": "Enable", "name": "enable"}, {"description": "CLI script executes only on the FortiGate unit that the stitch is triggered", "help": "CLI script executes only on the FortiGate unit that the stitch is triggered.", "label": "Disable", "name": "disable"}] | None = ...,
        accprofile: str | None = ...,
        regular_expression: str | None = ...,
        log_debug_print: Literal[{"description": "Enable logging debug print output from diagnose action", "help": "Enable logging debug print output from diagnose action.", "label": "Enable", "name": "enable"}, {"description": "Disable logging debug print output from diagnose action", "help": "Disable logging debug print output from diagnose action.", "label": "Disable", "name": "disable"}] | None = ...,
        security_tag: str | None = ...,
        sdn_connector: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: AutomationActionPayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        action_type: Literal[{"description": "Send notification email", "help": "Send notification email.", "label": "Email", "name": "email"}, {"description": "Send push notification to FortiExplorer", "help": "Send push notification to FortiExplorer.", "label": "Fortiexplorer Notification", "name": "fortiexplorer-notification"}, {"description": "Generate FortiOS dashboard alert", "help": "Generate FortiOS dashboard alert.", "label": "Alert", "name": "alert"}, {"description": "Disable interface", "help": "Disable interface.", "label": "Disable Ssid", "name": "disable-ssid"}, {"description": "Perform immediate system operations on this FortiGate unit", "help": "Perform immediate system operations on this FortiGate unit.", "label": "System Actions", "name": "system-actions"}, {"description": "Quarantine host", "help": "Quarantine host.", "label": "Quarantine", "name": "quarantine"}, {"description": "Quarantine FortiClient by EMS", "help": "Quarantine FortiClient by EMS.", "label": "Quarantine Forticlient", "name": "quarantine-forticlient"}, {"description": "Quarantine NSX instance", "help": "Quarantine NSX instance.", "label": "Quarantine Nsx", "name": "quarantine-nsx"}, {"description": "Quarantine host by FortiNAC", "help": "Quarantine host by FortiNAC.", "label": "Quarantine Fortinac", "name": "quarantine-fortinac"}, {"description": "Ban IP address", "help": "Ban IP address.", "label": "Ban Ip", "name": "ban-ip"}, {"description": "Send log data to integrated AWS service", "help": "Send log data to integrated AWS service.", "label": "Aws Lambda", "name": "aws-lambda"}, {"description": "Send log data to an Azure function", "help": "Send log data to an Azure function.", "label": "Azure Function", "name": "azure-function"}, {"description": "Send log data to a Google Cloud function", "help": "Send log data to a Google Cloud function.", "label": "Google Cloud Function", "name": "google-cloud-function"}, {"description": "Send log data to an AliCloud function", "help": "Send log data to an AliCloud function.", "label": "Alicloud Function", "name": "alicloud-function"}, {"description": "Send an HTTP request", "help": "Send an HTTP request.", "label": "Webhook", "name": "webhook"}, {"description": "Run CLI script", "help": "Run CLI script.", "label": "Cli Script", "name": "cli-script"}, {"description": "Run diagnose script", "help": "Run diagnose script.", "label": "Diagnose Script", "name": "diagnose-script"}, {"description": "Match pattern on input text", "help": "Match pattern on input text.", "label": "Regular Expression", "name": "regular-expression"}, {"description": "Send a notification message to a Slack incoming webhook", "help": "Send a notification message to a Slack incoming webhook.", "label": "Slack Notification", "name": "slack-notification"}, {"description": "Send a notification message to a Microsoft Teams incoming webhook", "help": "Send a notification message to a Microsoft Teams incoming webhook.", "label": "Microsoft Teams Notification", "name": "microsoft-teams-notification"}] | None = ...,
        system_action: Literal[{"description": "Reboot this FortiGate unit", "help": "Reboot this FortiGate unit.", "label": "Reboot", "name": "reboot"}, {"description": "Shutdown this FortiGate unit", "help": "Shutdown this FortiGate unit.", "label": "Shutdown", "name": "shutdown"}, {"description": "Backup current configuration to the disk revisions", "help": "Backup current configuration to the disk revisions.", "label": "Backup Config", "name": "backup-config"}] | None = ...,
        tls_certificate: str | None = ...,
        forticare_email: Literal[{"description": "Enable use of your FortiCare email address as the email-to address", "help": "Enable use of your FortiCare email address as the email-to address.", "label": "Enable", "name": "enable"}, {"description": "Disable use of your FortiCare email address as the email-to address", "help": "Disable use of your FortiCare email address as the email-to address.", "label": "Disable", "name": "disable"}] | None = ...,
        email_to: list[dict[str, Any]] | None = ...,
        email_from: str | None = ...,
        email_subject: str | None = ...,
        minimum_interval: int | None = ...,
        aws_api_key: str | None = ...,
        azure_function_authorization: Literal[{"description": "Anonymous authorization level (No authorization required)", "help": "Anonymous authorization level (No authorization required).", "label": "Anonymous", "name": "anonymous"}, {"description": "Function authorization level (Function or Host Key required)", "help": "Function authorization level (Function or Host Key required).", "label": "Function", "name": "function"}, {"description": "Admin authorization level (Master Host Key required)", "help": "Admin authorization level (Master Host Key required).", "label": "Admin", "name": "admin"}] | None = ...,
        azure_api_key: str | None = ...,
        alicloud_function_authorization: Literal[{"description": "Anonymous authorization (No authorization required)", "help": "Anonymous authorization (No authorization required).", "label": "Anonymous", "name": "anonymous"}, {"description": "Function authorization (Authorization required)", "help": "Function authorization (Authorization required).", "label": "Function", "name": "function"}] | None = ...,
        alicloud_access_key_id: str | None = ...,
        alicloud_access_key_secret: str | None = ...,
        message_type: Literal[{"description": "Plaintext", "help": "Plaintext.", "label": "Text", "name": "text"}, {"description": "Custom JSON", "help": "Custom JSON.", "label": "Json", "name": "json"}, {"description": "Multipart/form-data", "help": "Multipart/form-data", "label": "Form Data", "name": "form-data"}] | None = ...,
        message: str | None = ...,
        replacement_message: Literal[{"description": "Enable replacement message", "help": "Enable replacement message.", "label": "Enable", "name": "enable"}, {"description": "Disable replacement message", "help": "Disable replacement message.", "label": "Disable", "name": "disable"}] | None = ...,
        replacemsg_group: str | None = ...,
        protocol: Literal[{"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}] | None = ...,
        method: Literal[{"description": "POST", "help": "POST.", "label": "Post", "name": "post"}, {"description": "PUT", "help": "PUT.", "label": "Put", "name": "put"}, {"description": "GET", "help": "GET.", "label": "Get", "name": "get"}, {"description": "PATCH", "help": "PATCH.", "label": "Patch", "name": "patch"}, {"description": "DELETE", "help": "DELETE.", "label": "Delete", "name": "delete"}] | None = ...,
        uri: str | None = ...,
        http_body: str | None = ...,
        port: int | None = ...,
        http_headers: list[dict[str, Any]] | None = ...,
        form_data: list[dict[str, Any]] | None = ...,
        verify_host_cert: Literal[{"description": "Enable verification of the remote host certificate", "help": "Enable verification of the remote host certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable verification of the remote host certificate", "help": "Disable verification of the remote host certificate.", "label": "Disable", "name": "disable"}] | None = ...,
        script: str | None = ...,
        output_size: int | None = ...,
        timeout: int | None = ...,
        duration: int | None = ...,
        output_interval: int | None = ...,
        file_only: Literal[{"description": "The output of the diag CLI will only be files", "help": "The output of the diag CLI will only be files.", "label": "Enable", "name": "enable"}, {"description": "The output of the diag CLI will be in raw text, output larger than 64KB will be in files", "help": "The output of the diag CLI will be in raw text, output larger than 64KB will be in files.", "label": "Disable", "name": "disable"}] | None = ...,
        execute_security_fabric: Literal[{"description": "CLI script executes on all FortiGate units in the Security Fabric", "help": "CLI script executes on all FortiGate units in the Security Fabric.", "label": "Enable", "name": "enable"}, {"description": "CLI script executes only on the FortiGate unit that the stitch is triggered", "help": "CLI script executes only on the FortiGate unit that the stitch is triggered.", "label": "Disable", "name": "disable"}] | None = ...,
        accprofile: str | None = ...,
        regular_expression: str | None = ...,
        log_debug_print: Literal[{"description": "Enable logging debug print output from diagnose action", "help": "Enable logging debug print output from diagnose action.", "label": "Enable", "name": "enable"}, {"description": "Disable logging debug print output from diagnose action", "help": "Disable logging debug print output from diagnose action.", "label": "Disable", "name": "disable"}] | None = ...,
        security_tag: str | None = ...,
        sdn_connector: list[dict[str, Any]] | None = ...,
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
        payload_dict: AutomationActionPayload | None = ...,
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
    "AutomationAction",
    "AutomationActionPayload",
]