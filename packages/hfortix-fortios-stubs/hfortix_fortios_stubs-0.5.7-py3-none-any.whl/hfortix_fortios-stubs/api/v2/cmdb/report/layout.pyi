from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class LayoutPayload(TypedDict, total=False):
    """
    Type hints for report/layout payload fields.
    
    Report layout configuration.
    
    **Usage:**
        payload: LayoutPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Report layout name.
    title: NotRequired[str]  # Report title.
    subtitle: NotRequired[str]  # Report subtitle.
    description: NotRequired[str]  # Description.
    style_theme: str  # Report style theme.
    options: NotRequired[Literal[{"description": "Include table of content in the report", "help": "Include table of content in the report.", "label": "Include Table Of Content", "name": "include-table-of-content"}, {"description": "Prepend heading with auto numbering", "help": "Prepend heading with auto numbering.", "label": "Auto Numbering Heading", "name": "auto-numbering-heading"}, {"description": "Auto add heading for each chart", "help": "Auto add heading for each chart.", "label": "View Chart As Heading", "name": "view-chart-as-heading"}, {"description": "Show HTML navigation bar before each heading", "help": "Show HTML navigation bar before each heading.", "label": "Show Html Navbar Before Heading", "name": "show-html-navbar-before-heading"}, {"description": "Use this option if you need none of the above options", "help": "Use this option if you need none of the above options.", "label": "Dummy Option", "name": "dummy-option"}]]  # Report layout options.
    format: NotRequired[Literal[{"description": "PDF", "help": "PDF.", "label": "Pdf", "name": "pdf"}]]  # Report format.
    schedule_type: NotRequired[Literal[{"description": "Run on demand", "help": "Run on demand.", "label": "Demand", "name": "demand"}, {"description": "Schedule daily", "help": "Schedule daily.", "label": "Daily", "name": "daily"}, {"description": "Schedule weekly", "help": "Schedule weekly.", "label": "Weekly", "name": "weekly"}]]  # Report schedule type.
    day: NotRequired[Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}]]  # Schedule days of week to generate report.
    time: NotRequired[str]  # Schedule time to generate report (format = hh:mm).
    cutoff_option: NotRequired[Literal[{"description": "Run time", "help": "Run time.", "label": "Run Time", "name": "run-time"}, {"description": "Custom", "help": "Custom.", "label": "Custom", "name": "custom"}]]  # Cutoff-option is either run-time or custom.
    cutoff_time: NotRequired[str]  # Custom cutoff time to generate report (format = hh:mm).
    email_send: NotRequired[Literal[{"description": "Enable sending emails after generating reports", "help": "Enable sending emails after generating reports.", "label": "Enable", "name": "enable"}, {"description": "Disable sending emails after generating reports", "help": "Disable sending emails after generating reports.", "label": "Disable", "name": "disable"}]]  # Enable/disable sending emails after reports are generated.
    email_recipients: NotRequired[str]  # Email recipients for generated reports.
    max_pdf_report: NotRequired[int]  # Maximum number of PDF reports to keep at one time (oldest re
    page: NotRequired[str]  # Configure report page.
    body_item: NotRequired[list[dict[str, Any]]]  # Configure report body item.


class Layout:
    """
    Report layout configuration.
    
    Path: report/layout
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
        payload_dict: LayoutPayload | None = ...,
        name: str | None = ...,
        title: str | None = ...,
        subtitle: str | None = ...,
        description: str | None = ...,
        style_theme: str | None = ...,
        options: Literal[{"description": "Include table of content in the report", "help": "Include table of content in the report.", "label": "Include Table Of Content", "name": "include-table-of-content"}, {"description": "Prepend heading with auto numbering", "help": "Prepend heading with auto numbering.", "label": "Auto Numbering Heading", "name": "auto-numbering-heading"}, {"description": "Auto add heading for each chart", "help": "Auto add heading for each chart.", "label": "View Chart As Heading", "name": "view-chart-as-heading"}, {"description": "Show HTML navigation bar before each heading", "help": "Show HTML navigation bar before each heading.", "label": "Show Html Navbar Before Heading", "name": "show-html-navbar-before-heading"}, {"description": "Use this option if you need none of the above options", "help": "Use this option if you need none of the above options.", "label": "Dummy Option", "name": "dummy-option"}] | None = ...,
        format: Literal[{"description": "PDF", "help": "PDF.", "label": "Pdf", "name": "pdf"}] | None = ...,
        schedule_type: Literal[{"description": "Run on demand", "help": "Run on demand.", "label": "Demand", "name": "demand"}, {"description": "Schedule daily", "help": "Schedule daily.", "label": "Daily", "name": "daily"}, {"description": "Schedule weekly", "help": "Schedule weekly.", "label": "Weekly", "name": "weekly"}] | None = ...,
        day: Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}] | None = ...,
        time: str | None = ...,
        cutoff_option: Literal[{"description": "Run time", "help": "Run time.", "label": "Run Time", "name": "run-time"}, {"description": "Custom", "help": "Custom.", "label": "Custom", "name": "custom"}] | None = ...,
        cutoff_time: str | None = ...,
        email_send: Literal[{"description": "Enable sending emails after generating reports", "help": "Enable sending emails after generating reports.", "label": "Enable", "name": "enable"}, {"description": "Disable sending emails after generating reports", "help": "Disable sending emails after generating reports.", "label": "Disable", "name": "disable"}] | None = ...,
        email_recipients: str | None = ...,
        max_pdf_report: int | None = ...,
        page: str | None = ...,
        body_item: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: LayoutPayload | None = ...,
        name: str | None = ...,
        title: str | None = ...,
        subtitle: str | None = ...,
        description: str | None = ...,
        style_theme: str | None = ...,
        options: Literal[{"description": "Include table of content in the report", "help": "Include table of content in the report.", "label": "Include Table Of Content", "name": "include-table-of-content"}, {"description": "Prepend heading with auto numbering", "help": "Prepend heading with auto numbering.", "label": "Auto Numbering Heading", "name": "auto-numbering-heading"}, {"description": "Auto add heading for each chart", "help": "Auto add heading for each chart.", "label": "View Chart As Heading", "name": "view-chart-as-heading"}, {"description": "Show HTML navigation bar before each heading", "help": "Show HTML navigation bar before each heading.", "label": "Show Html Navbar Before Heading", "name": "show-html-navbar-before-heading"}, {"description": "Use this option if you need none of the above options", "help": "Use this option if you need none of the above options.", "label": "Dummy Option", "name": "dummy-option"}] | None = ...,
        format: Literal[{"description": "PDF", "help": "PDF.", "label": "Pdf", "name": "pdf"}] | None = ...,
        schedule_type: Literal[{"description": "Run on demand", "help": "Run on demand.", "label": "Demand", "name": "demand"}, {"description": "Schedule daily", "help": "Schedule daily.", "label": "Daily", "name": "daily"}, {"description": "Schedule weekly", "help": "Schedule weekly.", "label": "Weekly", "name": "weekly"}] | None = ...,
        day: Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}] | None = ...,
        time: str | None = ...,
        cutoff_option: Literal[{"description": "Run time", "help": "Run time.", "label": "Run Time", "name": "run-time"}, {"description": "Custom", "help": "Custom.", "label": "Custom", "name": "custom"}] | None = ...,
        cutoff_time: str | None = ...,
        email_send: Literal[{"description": "Enable sending emails after generating reports", "help": "Enable sending emails after generating reports.", "label": "Enable", "name": "enable"}, {"description": "Disable sending emails after generating reports", "help": "Disable sending emails after generating reports.", "label": "Disable", "name": "disable"}] | None = ...,
        email_recipients: str | None = ...,
        max_pdf_report: int | None = ...,
        page: str | None = ...,
        body_item: list[dict[str, Any]] | None = ...,
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
        payload_dict: LayoutPayload | None = ...,
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
    "Layout",
    "LayoutPayload",
]