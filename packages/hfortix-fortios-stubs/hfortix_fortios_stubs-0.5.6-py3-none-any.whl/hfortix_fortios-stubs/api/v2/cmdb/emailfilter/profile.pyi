from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ProfilePayload(TypedDict, total=False):
    """
    Type hints for emailfilter/profile payload fields.
    
    Configure Email Filter profiles.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.emailfilter.block-allow-list.BlockAllowListEndpoint` (via: spam-bal-table)
        - :class:`~.emailfilter.bword.BwordEndpoint` (via: spam-bword-table)
        - :class:`~.emailfilter.dnsbl.DnsblEndpoint` (via: spam-rbl-table)
        - :class:`~.emailfilter.iptrust.IptrustEndpoint` (via: spam-iptrust-table)
        - :class:`~.emailfilter.mheader.MheaderEndpoint` (via: spam-mheader-table)
        - :class:`~.system.replacemsg-group.ReplacemsgGroupEndpoint` (via: replacemsg-group)

    **Usage:**
        payload: ProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Profile name.
    comment: NotRequired[str]  # Comment.
    feature_set: NotRequired[Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}]]  # Flow/proxy feature set.
    replacemsg_group: NotRequired[str]  # Replacement message group.
    spam_log: NotRequired[Literal[{"description": "Disable spam logging for email filtering", "help": "Disable spam logging for email filtering.", "label": "Disable", "name": "disable"}, {"description": "Enable spam logging for email filtering", "help": "Enable spam logging for email filtering.", "label": "Enable", "name": "enable"}]]  # Enable/disable spam logging for email filtering.
    spam_log_fortiguard_response: NotRequired[Literal[{"description": "Disable logging FortiGuard spam response", "help": "Disable logging FortiGuard spam response.", "label": "Disable", "name": "disable"}, {"description": "Enable logging FortiGuard spam response", "help": "Enable logging FortiGuard spam response.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging FortiGuard spam response.
    spam_filtering: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable spam filtering.
    external: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable external Email inspection.
    options: NotRequired[Literal[{"description": "Content block", "help": "Content block.", "label": "Bannedword", "name": "bannedword"}, {"description": "Block/allow list", "help": "Block/allow list.", "label": "Spambal", "name": "spambal"}, {"description": "Email IP address FortiGuard AntiSpam block list check", "help": "Email IP address FortiGuard AntiSpam block list check.", "label": "Spamfsip", "name": "spamfsip"}, {"description": "Add FortiGuard AntiSpam spam submission text", "help": "Add FortiGuard AntiSpam spam submission text.", "label": "Spamfssubmit", "name": "spamfssubmit"}, {"description": "Email checksum FortiGuard AntiSpam check", "help": "Email checksum FortiGuard AntiSpam check.", "label": "Spamfschksum", "name": "spamfschksum"}, {"description": "Email content URL FortiGuard AntiSpam check", "help": "Email content URL FortiGuard AntiSpam check.", "label": "Spamfsurl", "name": "spamfsurl"}, {"description": "Email helo/ehlo domain DNS check", "help": "Email helo/ehlo domain DNS check.", "label": "Spamhelodns", "name": "spamhelodns"}, {"description": "Email return address DNS check", "help": "Email return address DNS check.", "label": "Spamraddrdns", "name": "spamraddrdns"}, {"description": "Email DNSBL \u0026 ORBL check", "help": "Email DNSBL \u0026 ORBL check.", "label": "Spamrbl", "name": "spamrbl"}, {"description": "Email mime header check", "help": "Email mime header check.", "label": "Spamhdrcheck", "name": "spamhdrcheck"}, {"description": "Email content phishing URL FortiGuard AntiSpam check", "help": "Email content phishing URL FortiGuard AntiSpam check.", "label": "Spamfsphish", "name": "spamfsphish"}]]  # Options.
    imap: NotRequired[str]  # IMAP.
    pop3: NotRequired[str]  # POP3.
    smtp: NotRequired[str]  # SMTP.
    mapi: NotRequired[str]  # MAPI.
    msn_hotmail: NotRequired[str]  # MSN Hotmail.
    yahoo_mail: NotRequired[str]  # Yahoo! Mail.
    gmail: NotRequired[str]  # Gmail.
    other_webmails: NotRequired[str]  # Other supported webmails.
    spam_bword_threshold: NotRequired[int]  # Spam banned word threshold.
    spam_bword_table: NotRequired[int]  # Anti-spam banned word table ID.
    spam_bal_table: NotRequired[int]  # Anti-spam block/allow list table ID.
    spam_mheader_table: NotRequired[int]  # Anti-spam MIME header table ID.
    spam_rbl_table: NotRequired[int]  # Anti-spam DNSBL table ID.
    spam_iptrust_table: NotRequired[int]  # Anti-spam IP trust table ID.


class Profile:
    """
    Configure Email Filter profiles.
    
    Path: emailfilter/profile
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
        spam_log: Literal[{"description": "Disable spam logging for email filtering", "help": "Disable spam logging for email filtering.", "label": "Disable", "name": "disable"}, {"description": "Enable spam logging for email filtering", "help": "Enable spam logging for email filtering.", "label": "Enable", "name": "enable"}] | None = ...,
        spam_log_fortiguard_response: Literal[{"description": "Disable logging FortiGuard spam response", "help": "Disable logging FortiGuard spam response.", "label": "Disable", "name": "disable"}, {"description": "Enable logging FortiGuard spam response", "help": "Enable logging FortiGuard spam response.", "label": "Enable", "name": "enable"}] | None = ...,
        spam_filtering: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        external: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        options: Literal[{"description": "Content block", "help": "Content block.", "label": "Bannedword", "name": "bannedword"}, {"description": "Block/allow list", "help": "Block/allow list.", "label": "Spambal", "name": "spambal"}, {"description": "Email IP address FortiGuard AntiSpam block list check", "help": "Email IP address FortiGuard AntiSpam block list check.", "label": "Spamfsip", "name": "spamfsip"}, {"description": "Add FortiGuard AntiSpam spam submission text", "help": "Add FortiGuard AntiSpam spam submission text.", "label": "Spamfssubmit", "name": "spamfssubmit"}, {"description": "Email checksum FortiGuard AntiSpam check", "help": "Email checksum FortiGuard AntiSpam check.", "label": "Spamfschksum", "name": "spamfschksum"}, {"description": "Email content URL FortiGuard AntiSpam check", "help": "Email content URL FortiGuard AntiSpam check.", "label": "Spamfsurl", "name": "spamfsurl"}, {"description": "Email helo/ehlo domain DNS check", "help": "Email helo/ehlo domain DNS check.", "label": "Spamhelodns", "name": "spamhelodns"}, {"description": "Email return address DNS check", "help": "Email return address DNS check.", "label": "Spamraddrdns", "name": "spamraddrdns"}, {"description": "Email DNSBL \u0026 ORBL check", "help": "Email DNSBL \u0026 ORBL check.", "label": "Spamrbl", "name": "spamrbl"}, {"description": "Email mime header check", "help": "Email mime header check.", "label": "Spamhdrcheck", "name": "spamhdrcheck"}, {"description": "Email content phishing URL FortiGuard AntiSpam check", "help": "Email content phishing URL FortiGuard AntiSpam check.", "label": "Spamfsphish", "name": "spamfsphish"}] | None = ...,
        imap: str | None = ...,
        pop3: str | None = ...,
        smtp: str | None = ...,
        mapi: str | None = ...,
        msn_hotmail: str | None = ...,
        yahoo_mail: str | None = ...,
        gmail: str | None = ...,
        other_webmails: str | None = ...,
        spam_bword_threshold: int | None = ...,
        spam_bword_table: int | None = ...,
        spam_bal_table: int | None = ...,
        spam_mheader_table: int | None = ...,
        spam_rbl_table: int | None = ...,
        spam_iptrust_table: int | None = ...,
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
        spam_log: Literal[{"description": "Disable spam logging for email filtering", "help": "Disable spam logging for email filtering.", "label": "Disable", "name": "disable"}, {"description": "Enable spam logging for email filtering", "help": "Enable spam logging for email filtering.", "label": "Enable", "name": "enable"}] | None = ...,
        spam_log_fortiguard_response: Literal[{"description": "Disable logging FortiGuard spam response", "help": "Disable logging FortiGuard spam response.", "label": "Disable", "name": "disable"}, {"description": "Enable logging FortiGuard spam response", "help": "Enable logging FortiGuard spam response.", "label": "Enable", "name": "enable"}] | None = ...,
        spam_filtering: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        external: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        options: Literal[{"description": "Content block", "help": "Content block.", "label": "Bannedword", "name": "bannedword"}, {"description": "Block/allow list", "help": "Block/allow list.", "label": "Spambal", "name": "spambal"}, {"description": "Email IP address FortiGuard AntiSpam block list check", "help": "Email IP address FortiGuard AntiSpam block list check.", "label": "Spamfsip", "name": "spamfsip"}, {"description": "Add FortiGuard AntiSpam spam submission text", "help": "Add FortiGuard AntiSpam spam submission text.", "label": "Spamfssubmit", "name": "spamfssubmit"}, {"description": "Email checksum FortiGuard AntiSpam check", "help": "Email checksum FortiGuard AntiSpam check.", "label": "Spamfschksum", "name": "spamfschksum"}, {"description": "Email content URL FortiGuard AntiSpam check", "help": "Email content URL FortiGuard AntiSpam check.", "label": "Spamfsurl", "name": "spamfsurl"}, {"description": "Email helo/ehlo domain DNS check", "help": "Email helo/ehlo domain DNS check.", "label": "Spamhelodns", "name": "spamhelodns"}, {"description": "Email return address DNS check", "help": "Email return address DNS check.", "label": "Spamraddrdns", "name": "spamraddrdns"}, {"description": "Email DNSBL \u0026 ORBL check", "help": "Email DNSBL \u0026 ORBL check.", "label": "Spamrbl", "name": "spamrbl"}, {"description": "Email mime header check", "help": "Email mime header check.", "label": "Spamhdrcheck", "name": "spamhdrcheck"}, {"description": "Email content phishing URL FortiGuard AntiSpam check", "help": "Email content phishing URL FortiGuard AntiSpam check.", "label": "Spamfsphish", "name": "spamfsphish"}] | None = ...,
        imap: str | None = ...,
        pop3: str | None = ...,
        smtp: str | None = ...,
        mapi: str | None = ...,
        msn_hotmail: str | None = ...,
        yahoo_mail: str | None = ...,
        gmail: str | None = ...,
        other_webmails: str | None = ...,
        spam_bword_threshold: int | None = ...,
        spam_bword_table: int | None = ...,
        spam_bal_table: int | None = ...,
        spam_mheader_table: int | None = ...,
        spam_rbl_table: int | None = ...,
        spam_iptrust_table: int | None = ...,
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