from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class PasswordPolicyPayload(TypedDict, total=False):
    """
    Type hints for user/password_policy payload fields.
    
    Configure user password policy.
    
    **Usage:**
        payload: PasswordPolicyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Password policy name.
    expire_status: NotRequired[Literal[{"description": "Passwords expire after expire-day days", "help": "Passwords expire after expire-day days.", "label": "Enable", "name": "enable"}, {"description": "Passwords do not expire", "help": "Passwords do not expire.", "label": "Disable", "name": "disable"}]]  # Enable/disable password expiration.
    expire_days: NotRequired[int]  # Time in days before the user's password expires.
    warn_days: NotRequired[int]  # Time in days before a password expiration warning message is
    expired_password_renewal: NotRequired[Literal[{"description": "Enable renewal of a password that already is expired", "help": "Enable renewal of a password that already is expired.", "label": "Enable", "name": "enable"}, {"description": "Disable renewal of a password that already is expired", "help": "Disable renewal of a password that already is expired.", "label": "Disable", "name": "disable"}]]  # Enable/disable renewal of a password that already is expired
    minimum_length: NotRequired[int]  # Minimum password length (8 - 128, default = 8).
    min_lower_case_letter: NotRequired[int]  # Minimum number of lowercase characters in password (0 - 128,
    min_upper_case_letter: NotRequired[int]  # Minimum number of uppercase characters in password (0 - 128,
    min_non_alphanumeric: NotRequired[int]  # Minimum number of non-alphanumeric characters in password (0
    min_number: NotRequired[int]  # Minimum number of numeric characters in password (0 - 128, d
    min_change_characters: NotRequired[int]  # Minimum number of unique characters in new password which do
    reuse_password: NotRequired[Literal[{"description": "Users are allowed to reuse the same password up to a limit", "help": "Users are allowed to reuse the same password up to a limit.", "label": "Enable", "name": "enable"}, {"description": "Users must create a new password", "help": "Users must create a new password.", "label": "Disable", "name": "disable"}]]  # Enable/disable reuse of password. If both reuse-password and
    reuse_password_limit: NotRequired[int]  # Number of times passwords can be reused (0 - 20, default = 0


class PasswordPolicy:
    """
    Configure user password policy.
    
    Path: user/password_policy
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
        payload_dict: PasswordPolicyPayload | None = ...,
        name: str | None = ...,
        expire_status: Literal[{"description": "Passwords expire after expire-day days", "help": "Passwords expire after expire-day days.", "label": "Enable", "name": "enable"}, {"description": "Passwords do not expire", "help": "Passwords do not expire.", "label": "Disable", "name": "disable"}] | None = ...,
        expire_days: int | None = ...,
        warn_days: int | None = ...,
        expired_password_renewal: Literal[{"description": "Enable renewal of a password that already is expired", "help": "Enable renewal of a password that already is expired.", "label": "Enable", "name": "enable"}, {"description": "Disable renewal of a password that already is expired", "help": "Disable renewal of a password that already is expired.", "label": "Disable", "name": "disable"}] | None = ...,
        minimum_length: int | None = ...,
        min_lower_case_letter: int | None = ...,
        min_upper_case_letter: int | None = ...,
        min_non_alphanumeric: int | None = ...,
        min_number: int | None = ...,
        min_change_characters: int | None = ...,
        reuse_password: Literal[{"description": "Users are allowed to reuse the same password up to a limit", "help": "Users are allowed to reuse the same password up to a limit.", "label": "Enable", "name": "enable"}, {"description": "Users must create a new password", "help": "Users must create a new password.", "label": "Disable", "name": "disable"}] | None = ...,
        reuse_password_limit: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: PasswordPolicyPayload | None = ...,
        name: str | None = ...,
        expire_status: Literal[{"description": "Passwords expire after expire-day days", "help": "Passwords expire after expire-day days.", "label": "Enable", "name": "enable"}, {"description": "Passwords do not expire", "help": "Passwords do not expire.", "label": "Disable", "name": "disable"}] | None = ...,
        expire_days: int | None = ...,
        warn_days: int | None = ...,
        expired_password_renewal: Literal[{"description": "Enable renewal of a password that already is expired", "help": "Enable renewal of a password that already is expired.", "label": "Enable", "name": "enable"}, {"description": "Disable renewal of a password that already is expired", "help": "Disable renewal of a password that already is expired.", "label": "Disable", "name": "disable"}] | None = ...,
        minimum_length: int | None = ...,
        min_lower_case_letter: int | None = ...,
        min_upper_case_letter: int | None = ...,
        min_non_alphanumeric: int | None = ...,
        min_number: int | None = ...,
        min_change_characters: int | None = ...,
        reuse_password: Literal[{"description": "Users are allowed to reuse the same password up to a limit", "help": "Users are allowed to reuse the same password up to a limit.", "label": "Enable", "name": "enable"}, {"description": "Users must create a new password", "help": "Users must create a new password.", "label": "Disable", "name": "disable"}] | None = ...,
        reuse_password_limit: int | None = ...,
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
        payload_dict: PasswordPolicyPayload | None = ...,
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
    "PasswordPolicy",
    "PasswordPolicyPayload",
]