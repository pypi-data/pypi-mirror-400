from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ProfilePayload(TypedDict, total=False):
    """
    Type hints for webfilter/profile payload fields.
    
    Configure Web filter profiles.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.replacemsg-group.ReplacemsgGroupEndpoint` (via: replacemsg-group)

    **Usage:**
        payload: ProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Profile name.
    comment: NotRequired[str]  # Optional comments.
    feature_set: NotRequired[Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}]]  # Flow/proxy feature set.
    replacemsg_group: NotRequired[str]  # Replacement message group.
    options: NotRequired[Literal[{"description": "ActiveX filter", "help": "ActiveX filter.", "label": "Activexfilter", "name": "activexfilter"}, {"description": "Cookie filter", "help": "Cookie filter.", "label": "Cookiefilter", "name": "cookiefilter"}, {"description": "Java applet filter", "help": "Java applet filter.", "label": "Javafilter", "name": "javafilter"}, {"description": "Block sessions contained an invalid domain name", "help": "Block sessions contained an invalid domain name.", "label": "Block Invalid Url", "name": "block-invalid-url"}, {"description": "Javascript block", "help": "Javascript block.", "label": "Jscript", "name": "jscript"}, {"description": "JS block", "help": "JS block.", "label": "Js", "name": "js"}, {"description": "VB script block", "help": "VB script block.", "label": "Vbs", "name": "vbs"}, {"description": "Unknown script block", "help": "Unknown script block.", "label": "Unknown", "name": "unknown"}, {"description": "Intrinsic script block", "help": "Intrinsic script block.", "label": "Intrinsic", "name": "intrinsic"}, {"description": "Referring block", "help": "Referring block.", "label": "Wf Referer", "name": "wf-referer"}, {"description": "Cookie block", "help": "Cookie block.", "label": "Wf Cookie", "name": "wf-cookie"}, {"help": "Per-user block/allow list filter", "label": "Per User Bal", "name": "per-user-bal"}]]  # Options.
    https_replacemsg: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable replacement messages for HTTPS.
    web_flow_log_encoding: NotRequired[Literal[{"description": "UTF-8 encoding", "help": "UTF-8 encoding.", "label": "Utf 8", "name": "utf-8"}, {"description": "Punycode encoding", "help": "Punycode encoding.", "label": "Punycode", "name": "punycode"}]]  # Log encoding in flow mode.
    ovrd_perm: NotRequired[Literal[{"description": "Banned word override", "help": "Banned word override.", "label": "Bannedword Override", "name": "bannedword-override"}, {"description": "URL filter override", "help": "URL filter override.", "label": "Urlfilter Override", "name": "urlfilter-override"}, {"description": "FortiGuard Web Filter override", "help": "FortiGuard Web Filter override.", "label": "Fortiguard Wf Override", "name": "fortiguard-wf-override"}, {"description": "Content-type header override", "help": "Content-type header override.", "label": "Contenttype Check Override", "name": "contenttype-check-override"}]]  # Permitted override types.
    post_action: NotRequired[Literal[{"description": "Normal, POST requests are allowed", "help": "Normal, POST requests are allowed.", "label": "Normal", "name": "normal"}, {"description": "POST requests are blocked", "help": "POST requests are blocked.", "label": "Block", "name": "block"}]]  # Action taken for HTTP POST traffic.
    override: NotRequired[str]  # Web Filter override settings.
    web: NotRequired[str]  # Web content filtering settings.
    ftgd_wf: NotRequired[str]  # FortiGuard Web Filter settings.
    antiphish: NotRequired[str]  # AntiPhishing profile.
    wisp: NotRequired[Literal[{"description": "Enable web proxy WISP", "help": "Enable web proxy WISP.", "label": "Enable", "name": "enable"}, {"description": "Disable web proxy WISP", "help": "Disable web proxy WISP.", "label": "Disable", "name": "disable"}]]  # Enable/disable web proxy WISP.
    wisp_servers: NotRequired[list[dict[str, Any]]]  # WISP servers.
    wisp_algorithm: NotRequired[Literal[{"description": "Select the first healthy server in order", "help": "Select the first healthy server in order.", "label": "Primary Secondary", "name": "primary-secondary"}, {"description": "Select the next healthy server", "help": "Select the next healthy server.", "label": "Round Robin", "name": "round-robin"}, {"description": "Select the lightest loading healthy server", "help": "Select the lightest loading healthy server.", "label": "Auto Learning", "name": "auto-learning"}]]  # WISP server selection algorithm.
    log_all_url: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging all URLs visited.
    web_content_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging logging blocked web content.
    web_filter_activex_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging ActiveX.
    web_filter_command_block_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging blocked commands.
    web_filter_cookie_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging cookie filtering.
    web_filter_applet_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging Java applets.
    web_filter_jscript_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging JScripts.
    web_filter_js_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging Java scripts.
    web_filter_vbs_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging VBS scripts.
    web_filter_unknown_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging unknown scripts.
    web_filter_referer_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging referrers.
    web_filter_cookie_removal_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging blocked cookies.
    web_url_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging URL filtering.
    web_invalid_domain_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging invalid domain names.
    web_ftgd_err_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging rating errors.
    web_ftgd_quota_usage: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging daily quota usage.
    extended_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable extended logging for web filtering.
    web_extended_all_action_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable extended any filter action logging for web fi
    web_antiphishing_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging of AntiPhishing checks.


class Profile:
    """
    Configure Web filter profiles.
    
    Path: webfilter/profile
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
        payload_dict: ProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        feature_set: Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}] | None = ...,
        replacemsg_group: str | None = ...,
        options: Literal[{"description": "ActiveX filter", "help": "ActiveX filter.", "label": "Activexfilter", "name": "activexfilter"}, {"description": "Cookie filter", "help": "Cookie filter.", "label": "Cookiefilter", "name": "cookiefilter"}, {"description": "Java applet filter", "help": "Java applet filter.", "label": "Javafilter", "name": "javafilter"}, {"description": "Block sessions contained an invalid domain name", "help": "Block sessions contained an invalid domain name.", "label": "Block Invalid Url", "name": "block-invalid-url"}, {"description": "Javascript block", "help": "Javascript block.", "label": "Jscript", "name": "jscript"}, {"description": "JS block", "help": "JS block.", "label": "Js", "name": "js"}, {"description": "VB script block", "help": "VB script block.", "label": "Vbs", "name": "vbs"}, {"description": "Unknown script block", "help": "Unknown script block.", "label": "Unknown", "name": "unknown"}, {"description": "Intrinsic script block", "help": "Intrinsic script block.", "label": "Intrinsic", "name": "intrinsic"}, {"description": "Referring block", "help": "Referring block.", "label": "Wf Referer", "name": "wf-referer"}, {"description": "Cookie block", "help": "Cookie block.", "label": "Wf Cookie", "name": "wf-cookie"}, {"help": "Per-user block/allow list filter", "label": "Per User Bal", "name": "per-user-bal"}] | None = ...,
        https_replacemsg: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_flow_log_encoding: Literal[{"description": "UTF-8 encoding", "help": "UTF-8 encoding.", "label": "Utf 8", "name": "utf-8"}, {"description": "Punycode encoding", "help": "Punycode encoding.", "label": "Punycode", "name": "punycode"}] | None = ...,
        ovrd_perm: Literal[{"description": "Banned word override", "help": "Banned word override.", "label": "Bannedword Override", "name": "bannedword-override"}, {"description": "URL filter override", "help": "URL filter override.", "label": "Urlfilter Override", "name": "urlfilter-override"}, {"description": "FortiGuard Web Filter override", "help": "FortiGuard Web Filter override.", "label": "Fortiguard Wf Override", "name": "fortiguard-wf-override"}, {"description": "Content-type header override", "help": "Content-type header override.", "label": "Contenttype Check Override", "name": "contenttype-check-override"}] | None = ...,
        post_action: Literal[{"description": "Normal, POST requests are allowed", "help": "Normal, POST requests are allowed.", "label": "Normal", "name": "normal"}, {"description": "POST requests are blocked", "help": "POST requests are blocked.", "label": "Block", "name": "block"}] | None = ...,
        override: str | None = ...,
        web: str | None = ...,
        ftgd_wf: str | None = ...,
        antiphish: str | None = ...,
        wisp: Literal[{"description": "Enable web proxy WISP", "help": "Enable web proxy WISP.", "label": "Enable", "name": "enable"}, {"description": "Disable web proxy WISP", "help": "Disable web proxy WISP.", "label": "Disable", "name": "disable"}] | None = ...,
        wisp_servers: list[dict[str, Any]] | None = ...,
        wisp_algorithm: Literal[{"description": "Select the first healthy server in order", "help": "Select the first healthy server in order.", "label": "Primary Secondary", "name": "primary-secondary"}, {"description": "Select the next healthy server", "help": "Select the next healthy server.", "label": "Round Robin", "name": "round-robin"}, {"description": "Select the lightest loading healthy server", "help": "Select the lightest loading healthy server.", "label": "Auto Learning", "name": "auto-learning"}] | None = ...,
        log_all_url: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_content_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_activex_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_command_block_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_cookie_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_applet_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_jscript_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_js_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_vbs_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_unknown_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_referer_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_cookie_removal_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_url_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_invalid_domain_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_ftgd_err_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_ftgd_quota_usage: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        extended_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_extended_all_action_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_antiphishing_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        feature_set: Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}] | None = ...,
        replacemsg_group: str | None = ...,
        options: Literal[{"description": "ActiveX filter", "help": "ActiveX filter.", "label": "Activexfilter", "name": "activexfilter"}, {"description": "Cookie filter", "help": "Cookie filter.", "label": "Cookiefilter", "name": "cookiefilter"}, {"description": "Java applet filter", "help": "Java applet filter.", "label": "Javafilter", "name": "javafilter"}, {"description": "Block sessions contained an invalid domain name", "help": "Block sessions contained an invalid domain name.", "label": "Block Invalid Url", "name": "block-invalid-url"}, {"description": "Javascript block", "help": "Javascript block.", "label": "Jscript", "name": "jscript"}, {"description": "JS block", "help": "JS block.", "label": "Js", "name": "js"}, {"description": "VB script block", "help": "VB script block.", "label": "Vbs", "name": "vbs"}, {"description": "Unknown script block", "help": "Unknown script block.", "label": "Unknown", "name": "unknown"}, {"description": "Intrinsic script block", "help": "Intrinsic script block.", "label": "Intrinsic", "name": "intrinsic"}, {"description": "Referring block", "help": "Referring block.", "label": "Wf Referer", "name": "wf-referer"}, {"description": "Cookie block", "help": "Cookie block.", "label": "Wf Cookie", "name": "wf-cookie"}, {"help": "Per-user block/allow list filter", "label": "Per User Bal", "name": "per-user-bal"}] | None = ...,
        https_replacemsg: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_flow_log_encoding: Literal[{"description": "UTF-8 encoding", "help": "UTF-8 encoding.", "label": "Utf 8", "name": "utf-8"}, {"description": "Punycode encoding", "help": "Punycode encoding.", "label": "Punycode", "name": "punycode"}] | None = ...,
        ovrd_perm: Literal[{"description": "Banned word override", "help": "Banned word override.", "label": "Bannedword Override", "name": "bannedword-override"}, {"description": "URL filter override", "help": "URL filter override.", "label": "Urlfilter Override", "name": "urlfilter-override"}, {"description": "FortiGuard Web Filter override", "help": "FortiGuard Web Filter override.", "label": "Fortiguard Wf Override", "name": "fortiguard-wf-override"}, {"description": "Content-type header override", "help": "Content-type header override.", "label": "Contenttype Check Override", "name": "contenttype-check-override"}] | None = ...,
        post_action: Literal[{"description": "Normal, POST requests are allowed", "help": "Normal, POST requests are allowed.", "label": "Normal", "name": "normal"}, {"description": "POST requests are blocked", "help": "POST requests are blocked.", "label": "Block", "name": "block"}] | None = ...,
        override: str | None = ...,
        web: str | None = ...,
        ftgd_wf: str | None = ...,
        antiphish: str | None = ...,
        wisp: Literal[{"description": "Enable web proxy WISP", "help": "Enable web proxy WISP.", "label": "Enable", "name": "enable"}, {"description": "Disable web proxy WISP", "help": "Disable web proxy WISP.", "label": "Disable", "name": "disable"}] | None = ...,
        wisp_servers: list[dict[str, Any]] | None = ...,
        wisp_algorithm: Literal[{"description": "Select the first healthy server in order", "help": "Select the first healthy server in order.", "label": "Primary Secondary", "name": "primary-secondary"}, {"description": "Select the next healthy server", "help": "Select the next healthy server.", "label": "Round Robin", "name": "round-robin"}, {"description": "Select the lightest loading healthy server", "help": "Select the lightest loading healthy server.", "label": "Auto Learning", "name": "auto-learning"}] | None = ...,
        log_all_url: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_content_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_activex_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_command_block_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_cookie_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_applet_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_jscript_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_js_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_vbs_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_unknown_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_referer_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_filter_cookie_removal_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_url_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_invalid_domain_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_ftgd_err_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_ftgd_quota_usage: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        extended_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_extended_all_action_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        web_antiphishing_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: ProfilePayload | None = ...,
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
    "Profile",
    "ProfilePayload",
]