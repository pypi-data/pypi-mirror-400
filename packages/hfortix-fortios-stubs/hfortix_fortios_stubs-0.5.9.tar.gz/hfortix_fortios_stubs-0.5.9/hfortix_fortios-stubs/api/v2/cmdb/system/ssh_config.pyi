from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SshConfigPayload(TypedDict, total=False):
    """
    Type hints for system/ssh_config payload fields.
    
    Configure SSH config.
    
    **Usage:**
        payload: SshConfigPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    ssh_kex_algo: NotRequired[Literal[{"description": "diffie-hellman-group1-sha1    diffie-hellman-group14-sha1:diffie-hellman-group14-sha1    diffie-hellman-group14-sha256:diffie-hellman-group14-sha256    diffie-hellman-group16-sha512:diffie-hellman-group16-sha512    diffie-hellman-group18-sha512:diffie-hellman-group18-sha512    diffie-hellman-group-exchange-sha1:diffie-hellman-group-exchange-sha1    diffie-hellman-group-exchange-sha256:diffie-hellman-group-exchange-sha256    curve25519-sha256@libssh", "help": "diffie-hellman-group1-sha1", "label": "Diffie Hellman Group1 Sha1", "name": "diffie-hellman-group1-sha1"}, {"help": "diffie-hellman-group14-sha1", "label": "Diffie Hellman Group14 Sha1", "name": "diffie-hellman-group14-sha1"}, {"help": "diffie-hellman-group14-sha256", "label": "Diffie Hellman Group14 Sha256", "name": "diffie-hellman-group14-sha256"}, {"help": "diffie-hellman-group16-sha512", "label": "Diffie Hellman Group16 Sha512", "name": "diffie-hellman-group16-sha512"}, {"help": "diffie-hellman-group18-sha512", "label": "Diffie Hellman Group18 Sha512", "name": "diffie-hellman-group18-sha512"}, {"help": "diffie-hellman-group-exchange-sha1", "label": "Diffie Hellman Group Exchange Sha1", "name": "diffie-hellman-group-exchange-sha1"}, {"help": "diffie-hellman-group-exchange-sha256", "label": "Diffie Hellman Group Exchange Sha256", "name": "diffie-hellman-group-exchange-sha256"}, {"help": "curve25519-sha256@libssh.org", "label": "Curve25519 Sha256@Libssh.Org", "name": "curve25519-sha256@libssh.org"}, {"help": "ecdh-sha2-nistp256", "label": "Ecdh Sha2 Nistp256", "name": "ecdh-sha2-nistp256"}, {"help": "ecdh-sha2-nistp384", "label": "Ecdh Sha2 Nistp384", "name": "ecdh-sha2-nistp384"}, {"help": "ecdh-sha2-nistp521", "label": "Ecdh Sha2 Nistp521", "name": "ecdh-sha2-nistp521"}]]  # Select one or more SSH kex algorithms.
    ssh_enc_algo: NotRequired[Literal[{"help": "chacha20-poly1305@openssh.com", "label": "Chacha20 Poly1305@Openssh.Com", "name": "chacha20-poly1305@openssh.com"}, {"help": "aes128-ctr", "label": "Aes128 Ctr", "name": "aes128-ctr"}, {"help": "aes192-ctr", "label": "Aes192 Ctr", "name": "aes192-ctr"}, {"help": "aes256-ctr", "label": "Aes256 Ctr", "name": "aes256-ctr"}, {"help": "arcfour256", "label": "Arcfour256", "name": "arcfour256"}, {"help": "arcfour128", "label": "Arcfour128", "name": "arcfour128"}, {"help": "aes128-cbc", "label": "Aes128 Cbc", "name": "aes128-cbc"}, {"help": "3des-cbc", "label": "3Des Cbc", "name": "3des-cbc"}, {"help": "blowfish-cbc", "label": "Blowfish Cbc", "name": "blowfish-cbc"}, {"help": "cast128-cbc", "label": "Cast128 Cbc", "name": "cast128-cbc"}, {"help": "aes192-cbc", "label": "Aes192 Cbc", "name": "aes192-cbc"}, {"help": "aes256-cbc", "label": "Aes256 Cbc", "name": "aes256-cbc"}, {"help": "arcfour", "label": "Arcfour", "name": "arcfour"}, {"help": "rijndael-cbc@lysator.liu.se", "label": "Rijndael Cbc@Lysator.Liu.Se", "name": "rijndael-cbc@lysator.liu.se"}, {"help": "aes128-gcm@openssh.com", "label": "Aes128 Gcm@Openssh.Com", "name": "aes128-gcm@openssh.com"}, {"help": "aes256-gcm@openssh.com", "label": "Aes256 Gcm@Openssh.Com", "name": "aes256-gcm@openssh.com"}]]  # Select one or more SSH ciphers.
    ssh_mac_algo: NotRequired[Literal[{"description": "hmac-md5    hmac-md5-etm@openssh", "help": "hmac-md5", "label": "Hmac Md5", "name": "hmac-md5"}, {"help": "hmac-md5-etm@openssh.com", "label": "Hmac Md5 Etm@Openssh.Com", "name": "hmac-md5-etm@openssh.com"}, {"help": "hmac-md5-96", "label": "Hmac Md5 96", "name": "hmac-md5-96"}, {"help": "hmac-md5-96-etm@openssh.com", "label": "Hmac Md5 96 Etm@Openssh.Com", "name": "hmac-md5-96-etm@openssh.com"}, {"help": "hmac-sha1", "label": "Hmac Sha1", "name": "hmac-sha1"}, {"help": "hmac-sha1-etm@openssh.com", "label": "Hmac Sha1 Etm@Openssh.Com", "name": "hmac-sha1-etm@openssh.com"}, {"help": "hmac-sha2-256", "label": "Hmac Sha2 256", "name": "hmac-sha2-256"}, {"help": "hmac-sha2-256-etm@openssh.com", "label": "Hmac Sha2 256 Etm@Openssh.Com", "name": "hmac-sha2-256-etm@openssh.com"}, {"help": "hmac-sha2-512", "label": "Hmac Sha2 512", "name": "hmac-sha2-512"}, {"help": "hmac-sha2-512-etm@openssh.com", "label": "Hmac Sha2 512 Etm@Openssh.Com", "name": "hmac-sha2-512-etm@openssh.com"}, {"help": "hmac-ripemd160", "label": "Hmac Ripemd160", "name": "hmac-ripemd160"}, {"help": "hmac-ripemd160@openssh.com", "label": "Hmac Ripemd160@Openssh.Com", "name": "hmac-ripemd160@openssh.com"}, {"help": "hmac-ripemd160-etm@openssh.com", "label": "Hmac Ripemd160 Etm@Openssh.Com", "name": "hmac-ripemd160-etm@openssh.com"}, {"help": "umac-64@openssh.com", "label": "Umac 64@Openssh.Com", "name": "umac-64@openssh.com"}, {"help": "umac-128@openssh.com", "label": "Umac 128@Openssh.Com", "name": "umac-128@openssh.com"}, {"help": "umac-64-etm@openssh.com", "label": "Umac 64 Etm@Openssh.Com", "name": "umac-64-etm@openssh.com"}, {"help": "umac-128-etm@openssh.com", "label": "Umac 128 Etm@Openssh.Com", "name": "umac-128-etm@openssh.com"}]]  # Select one or more SSH MAC algorithms.
    ssh_hsk_algo: NotRequired[Literal[{"description": "ssh-rsa    ecdsa-sha2-nistp521:ecdsa-sha2-nistp521    ecdsa-sha2-nistp384:ecdsa-sha2-nistp384    ecdsa-sha2-nistp256:ecdsa-sha2-nistp256    rsa-sha2-256:rsa-sha2-256    rsa-sha2-512:rsa-sha2-512    ssh-ed25519:ssh-ed25519", "help": "ssh-rsa", "label": "Ssh Rsa", "name": "ssh-rsa"}, {"help": "ecdsa-sha2-nistp521", "label": "Ecdsa Sha2 Nistp521", "name": "ecdsa-sha2-nistp521"}, {"help": "ecdsa-sha2-nistp384", "label": "Ecdsa Sha2 Nistp384", "name": "ecdsa-sha2-nistp384"}, {"help": "ecdsa-sha2-nistp256", "label": "Ecdsa Sha2 Nistp256", "name": "ecdsa-sha2-nistp256"}, {"help": "rsa-sha2-256", "label": "Rsa Sha2 256", "name": "rsa-sha2-256"}, {"help": "rsa-sha2-512", "label": "Rsa Sha2 512", "name": "rsa-sha2-512"}, {"help": "ssh-ed25519", "label": "Ssh Ed25519", "name": "ssh-ed25519"}]]  # Select one or more SSH hostkey algorithms.
    ssh_hsk_override: NotRequired[Literal[{"description": "Disable SSH host key override in SSH daemon", "help": "Disable SSH host key override in SSH daemon.", "label": "Disable", "name": "disable"}, {"description": "Enable SSH host key override in SSH daemon", "help": "Enable SSH host key override in SSH daemon.", "label": "Enable", "name": "enable"}]]  # Enable/disable SSH host key override in SSH daemon.
    ssh_hsk_password: NotRequired[str]  # Password for ssh-hostkey.
    ssh_hsk: str  # Config SSH host key.


class SshConfig:
    """
    Configure SSH config.
    
    Path: system/ssh_config
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
        payload_dict: SshConfigPayload | None = ...,
        ssh_kex_algo: Literal[{"description": "diffie-hellman-group1-sha1    diffie-hellman-group14-sha1:diffie-hellman-group14-sha1    diffie-hellman-group14-sha256:diffie-hellman-group14-sha256    diffie-hellman-group16-sha512:diffie-hellman-group16-sha512    diffie-hellman-group18-sha512:diffie-hellman-group18-sha512    diffie-hellman-group-exchange-sha1:diffie-hellman-group-exchange-sha1    diffie-hellman-group-exchange-sha256:diffie-hellman-group-exchange-sha256    curve25519-sha256@libssh", "help": "diffie-hellman-group1-sha1", "label": "Diffie Hellman Group1 Sha1", "name": "diffie-hellman-group1-sha1"}, {"help": "diffie-hellman-group14-sha1", "label": "Diffie Hellman Group14 Sha1", "name": "diffie-hellman-group14-sha1"}, {"help": "diffie-hellman-group14-sha256", "label": "Diffie Hellman Group14 Sha256", "name": "diffie-hellman-group14-sha256"}, {"help": "diffie-hellman-group16-sha512", "label": "Diffie Hellman Group16 Sha512", "name": "diffie-hellman-group16-sha512"}, {"help": "diffie-hellman-group18-sha512", "label": "Diffie Hellman Group18 Sha512", "name": "diffie-hellman-group18-sha512"}, {"help": "diffie-hellman-group-exchange-sha1", "label": "Diffie Hellman Group Exchange Sha1", "name": "diffie-hellman-group-exchange-sha1"}, {"help": "diffie-hellman-group-exchange-sha256", "label": "Diffie Hellman Group Exchange Sha256", "name": "diffie-hellman-group-exchange-sha256"}, {"help": "curve25519-sha256@libssh.org", "label": "Curve25519 Sha256@Libssh.Org", "name": "curve25519-sha256@libssh.org"}, {"help": "ecdh-sha2-nistp256", "label": "Ecdh Sha2 Nistp256", "name": "ecdh-sha2-nistp256"}, {"help": "ecdh-sha2-nistp384", "label": "Ecdh Sha2 Nistp384", "name": "ecdh-sha2-nistp384"}, {"help": "ecdh-sha2-nistp521", "label": "Ecdh Sha2 Nistp521", "name": "ecdh-sha2-nistp521"}] | None = ...,
        ssh_enc_algo: Literal[{"help": "chacha20-poly1305@openssh.com", "label": "Chacha20 Poly1305@Openssh.Com", "name": "chacha20-poly1305@openssh.com"}, {"help": "aes128-ctr", "label": "Aes128 Ctr", "name": "aes128-ctr"}, {"help": "aes192-ctr", "label": "Aes192 Ctr", "name": "aes192-ctr"}, {"help": "aes256-ctr", "label": "Aes256 Ctr", "name": "aes256-ctr"}, {"help": "arcfour256", "label": "Arcfour256", "name": "arcfour256"}, {"help": "arcfour128", "label": "Arcfour128", "name": "arcfour128"}, {"help": "aes128-cbc", "label": "Aes128 Cbc", "name": "aes128-cbc"}, {"help": "3des-cbc", "label": "3Des Cbc", "name": "3des-cbc"}, {"help": "blowfish-cbc", "label": "Blowfish Cbc", "name": "blowfish-cbc"}, {"help": "cast128-cbc", "label": "Cast128 Cbc", "name": "cast128-cbc"}, {"help": "aes192-cbc", "label": "Aes192 Cbc", "name": "aes192-cbc"}, {"help": "aes256-cbc", "label": "Aes256 Cbc", "name": "aes256-cbc"}, {"help": "arcfour", "label": "Arcfour", "name": "arcfour"}, {"help": "rijndael-cbc@lysator.liu.se", "label": "Rijndael Cbc@Lysator.Liu.Se", "name": "rijndael-cbc@lysator.liu.se"}, {"help": "aes128-gcm@openssh.com", "label": "Aes128 Gcm@Openssh.Com", "name": "aes128-gcm@openssh.com"}, {"help": "aes256-gcm@openssh.com", "label": "Aes256 Gcm@Openssh.Com", "name": "aes256-gcm@openssh.com"}] | None = ...,
        ssh_mac_algo: Literal[{"description": "hmac-md5    hmac-md5-etm@openssh", "help": "hmac-md5", "label": "Hmac Md5", "name": "hmac-md5"}, {"help": "hmac-md5-etm@openssh.com", "label": "Hmac Md5 Etm@Openssh.Com", "name": "hmac-md5-etm@openssh.com"}, {"help": "hmac-md5-96", "label": "Hmac Md5 96", "name": "hmac-md5-96"}, {"help": "hmac-md5-96-etm@openssh.com", "label": "Hmac Md5 96 Etm@Openssh.Com", "name": "hmac-md5-96-etm@openssh.com"}, {"help": "hmac-sha1", "label": "Hmac Sha1", "name": "hmac-sha1"}, {"help": "hmac-sha1-etm@openssh.com", "label": "Hmac Sha1 Etm@Openssh.Com", "name": "hmac-sha1-etm@openssh.com"}, {"help": "hmac-sha2-256", "label": "Hmac Sha2 256", "name": "hmac-sha2-256"}, {"help": "hmac-sha2-256-etm@openssh.com", "label": "Hmac Sha2 256 Etm@Openssh.Com", "name": "hmac-sha2-256-etm@openssh.com"}, {"help": "hmac-sha2-512", "label": "Hmac Sha2 512", "name": "hmac-sha2-512"}, {"help": "hmac-sha2-512-etm@openssh.com", "label": "Hmac Sha2 512 Etm@Openssh.Com", "name": "hmac-sha2-512-etm@openssh.com"}, {"help": "hmac-ripemd160", "label": "Hmac Ripemd160", "name": "hmac-ripemd160"}, {"help": "hmac-ripemd160@openssh.com", "label": "Hmac Ripemd160@Openssh.Com", "name": "hmac-ripemd160@openssh.com"}, {"help": "hmac-ripemd160-etm@openssh.com", "label": "Hmac Ripemd160 Etm@Openssh.Com", "name": "hmac-ripemd160-etm@openssh.com"}, {"help": "umac-64@openssh.com", "label": "Umac 64@Openssh.Com", "name": "umac-64@openssh.com"}, {"help": "umac-128@openssh.com", "label": "Umac 128@Openssh.Com", "name": "umac-128@openssh.com"}, {"help": "umac-64-etm@openssh.com", "label": "Umac 64 Etm@Openssh.Com", "name": "umac-64-etm@openssh.com"}, {"help": "umac-128-etm@openssh.com", "label": "Umac 128 Etm@Openssh.Com", "name": "umac-128-etm@openssh.com"}] | None = ...,
        ssh_hsk_algo: Literal[{"description": "ssh-rsa    ecdsa-sha2-nistp521:ecdsa-sha2-nistp521    ecdsa-sha2-nistp384:ecdsa-sha2-nistp384    ecdsa-sha2-nistp256:ecdsa-sha2-nistp256    rsa-sha2-256:rsa-sha2-256    rsa-sha2-512:rsa-sha2-512    ssh-ed25519:ssh-ed25519", "help": "ssh-rsa", "label": "Ssh Rsa", "name": "ssh-rsa"}, {"help": "ecdsa-sha2-nistp521", "label": "Ecdsa Sha2 Nistp521", "name": "ecdsa-sha2-nistp521"}, {"help": "ecdsa-sha2-nistp384", "label": "Ecdsa Sha2 Nistp384", "name": "ecdsa-sha2-nistp384"}, {"help": "ecdsa-sha2-nistp256", "label": "Ecdsa Sha2 Nistp256", "name": "ecdsa-sha2-nistp256"}, {"help": "rsa-sha2-256", "label": "Rsa Sha2 256", "name": "rsa-sha2-256"}, {"help": "rsa-sha2-512", "label": "Rsa Sha2 512", "name": "rsa-sha2-512"}, {"help": "ssh-ed25519", "label": "Ssh Ed25519", "name": "ssh-ed25519"}] | None = ...,
        ssh_hsk_override: Literal[{"description": "Disable SSH host key override in SSH daemon", "help": "Disable SSH host key override in SSH daemon.", "label": "Disable", "name": "disable"}, {"description": "Enable SSH host key override in SSH daemon", "help": "Enable SSH host key override in SSH daemon.", "label": "Enable", "name": "enable"}] | None = ...,
        ssh_hsk_password: str | None = ...,
        ssh_hsk: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SshConfigPayload | None = ...,
        ssh_kex_algo: Literal[{"description": "diffie-hellman-group1-sha1    diffie-hellman-group14-sha1:diffie-hellman-group14-sha1    diffie-hellman-group14-sha256:diffie-hellman-group14-sha256    diffie-hellman-group16-sha512:diffie-hellman-group16-sha512    diffie-hellman-group18-sha512:diffie-hellman-group18-sha512    diffie-hellman-group-exchange-sha1:diffie-hellman-group-exchange-sha1    diffie-hellman-group-exchange-sha256:diffie-hellman-group-exchange-sha256    curve25519-sha256@libssh", "help": "diffie-hellman-group1-sha1", "label": "Diffie Hellman Group1 Sha1", "name": "diffie-hellman-group1-sha1"}, {"help": "diffie-hellman-group14-sha1", "label": "Diffie Hellman Group14 Sha1", "name": "diffie-hellman-group14-sha1"}, {"help": "diffie-hellman-group14-sha256", "label": "Diffie Hellman Group14 Sha256", "name": "diffie-hellman-group14-sha256"}, {"help": "diffie-hellman-group16-sha512", "label": "Diffie Hellman Group16 Sha512", "name": "diffie-hellman-group16-sha512"}, {"help": "diffie-hellman-group18-sha512", "label": "Diffie Hellman Group18 Sha512", "name": "diffie-hellman-group18-sha512"}, {"help": "diffie-hellman-group-exchange-sha1", "label": "Diffie Hellman Group Exchange Sha1", "name": "diffie-hellman-group-exchange-sha1"}, {"help": "diffie-hellman-group-exchange-sha256", "label": "Diffie Hellman Group Exchange Sha256", "name": "diffie-hellman-group-exchange-sha256"}, {"help": "curve25519-sha256@libssh.org", "label": "Curve25519 Sha256@Libssh.Org", "name": "curve25519-sha256@libssh.org"}, {"help": "ecdh-sha2-nistp256", "label": "Ecdh Sha2 Nistp256", "name": "ecdh-sha2-nistp256"}, {"help": "ecdh-sha2-nistp384", "label": "Ecdh Sha2 Nistp384", "name": "ecdh-sha2-nistp384"}, {"help": "ecdh-sha2-nistp521", "label": "Ecdh Sha2 Nistp521", "name": "ecdh-sha2-nistp521"}] | None = ...,
        ssh_enc_algo: Literal[{"help": "chacha20-poly1305@openssh.com", "label": "Chacha20 Poly1305@Openssh.Com", "name": "chacha20-poly1305@openssh.com"}, {"help": "aes128-ctr", "label": "Aes128 Ctr", "name": "aes128-ctr"}, {"help": "aes192-ctr", "label": "Aes192 Ctr", "name": "aes192-ctr"}, {"help": "aes256-ctr", "label": "Aes256 Ctr", "name": "aes256-ctr"}, {"help": "arcfour256", "label": "Arcfour256", "name": "arcfour256"}, {"help": "arcfour128", "label": "Arcfour128", "name": "arcfour128"}, {"help": "aes128-cbc", "label": "Aes128 Cbc", "name": "aes128-cbc"}, {"help": "3des-cbc", "label": "3Des Cbc", "name": "3des-cbc"}, {"help": "blowfish-cbc", "label": "Blowfish Cbc", "name": "blowfish-cbc"}, {"help": "cast128-cbc", "label": "Cast128 Cbc", "name": "cast128-cbc"}, {"help": "aes192-cbc", "label": "Aes192 Cbc", "name": "aes192-cbc"}, {"help": "aes256-cbc", "label": "Aes256 Cbc", "name": "aes256-cbc"}, {"help": "arcfour", "label": "Arcfour", "name": "arcfour"}, {"help": "rijndael-cbc@lysator.liu.se", "label": "Rijndael Cbc@Lysator.Liu.Se", "name": "rijndael-cbc@lysator.liu.se"}, {"help": "aes128-gcm@openssh.com", "label": "Aes128 Gcm@Openssh.Com", "name": "aes128-gcm@openssh.com"}, {"help": "aes256-gcm@openssh.com", "label": "Aes256 Gcm@Openssh.Com", "name": "aes256-gcm@openssh.com"}] | None = ...,
        ssh_mac_algo: Literal[{"description": "hmac-md5    hmac-md5-etm@openssh", "help": "hmac-md5", "label": "Hmac Md5", "name": "hmac-md5"}, {"help": "hmac-md5-etm@openssh.com", "label": "Hmac Md5 Etm@Openssh.Com", "name": "hmac-md5-etm@openssh.com"}, {"help": "hmac-md5-96", "label": "Hmac Md5 96", "name": "hmac-md5-96"}, {"help": "hmac-md5-96-etm@openssh.com", "label": "Hmac Md5 96 Etm@Openssh.Com", "name": "hmac-md5-96-etm@openssh.com"}, {"help": "hmac-sha1", "label": "Hmac Sha1", "name": "hmac-sha1"}, {"help": "hmac-sha1-etm@openssh.com", "label": "Hmac Sha1 Etm@Openssh.Com", "name": "hmac-sha1-etm@openssh.com"}, {"help": "hmac-sha2-256", "label": "Hmac Sha2 256", "name": "hmac-sha2-256"}, {"help": "hmac-sha2-256-etm@openssh.com", "label": "Hmac Sha2 256 Etm@Openssh.Com", "name": "hmac-sha2-256-etm@openssh.com"}, {"help": "hmac-sha2-512", "label": "Hmac Sha2 512", "name": "hmac-sha2-512"}, {"help": "hmac-sha2-512-etm@openssh.com", "label": "Hmac Sha2 512 Etm@Openssh.Com", "name": "hmac-sha2-512-etm@openssh.com"}, {"help": "hmac-ripemd160", "label": "Hmac Ripemd160", "name": "hmac-ripemd160"}, {"help": "hmac-ripemd160@openssh.com", "label": "Hmac Ripemd160@Openssh.Com", "name": "hmac-ripemd160@openssh.com"}, {"help": "hmac-ripemd160-etm@openssh.com", "label": "Hmac Ripemd160 Etm@Openssh.Com", "name": "hmac-ripemd160-etm@openssh.com"}, {"help": "umac-64@openssh.com", "label": "Umac 64@Openssh.Com", "name": "umac-64@openssh.com"}, {"help": "umac-128@openssh.com", "label": "Umac 128@Openssh.Com", "name": "umac-128@openssh.com"}, {"help": "umac-64-etm@openssh.com", "label": "Umac 64 Etm@Openssh.Com", "name": "umac-64-etm@openssh.com"}, {"help": "umac-128-etm@openssh.com", "label": "Umac 128 Etm@Openssh.Com", "name": "umac-128-etm@openssh.com"}] | None = ...,
        ssh_hsk_algo: Literal[{"description": "ssh-rsa    ecdsa-sha2-nistp521:ecdsa-sha2-nistp521    ecdsa-sha2-nistp384:ecdsa-sha2-nistp384    ecdsa-sha2-nistp256:ecdsa-sha2-nistp256    rsa-sha2-256:rsa-sha2-256    rsa-sha2-512:rsa-sha2-512    ssh-ed25519:ssh-ed25519", "help": "ssh-rsa", "label": "Ssh Rsa", "name": "ssh-rsa"}, {"help": "ecdsa-sha2-nistp521", "label": "Ecdsa Sha2 Nistp521", "name": "ecdsa-sha2-nistp521"}, {"help": "ecdsa-sha2-nistp384", "label": "Ecdsa Sha2 Nistp384", "name": "ecdsa-sha2-nistp384"}, {"help": "ecdsa-sha2-nistp256", "label": "Ecdsa Sha2 Nistp256", "name": "ecdsa-sha2-nistp256"}, {"help": "rsa-sha2-256", "label": "Rsa Sha2 256", "name": "rsa-sha2-256"}, {"help": "rsa-sha2-512", "label": "Rsa Sha2 512", "name": "rsa-sha2-512"}, {"help": "ssh-ed25519", "label": "Ssh Ed25519", "name": "ssh-ed25519"}] | None = ...,
        ssh_hsk_override: Literal[{"description": "Disable SSH host key override in SSH daemon", "help": "Disable SSH host key override in SSH daemon.", "label": "Disable", "name": "disable"}, {"description": "Enable SSH host key override in SSH daemon", "help": "Enable SSH host key override in SSH daemon.", "label": "Enable", "name": "enable"}] | None = ...,
        ssh_hsk_password: str | None = ...,
        ssh_hsk: str | None = ...,
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
        payload_dict: SshConfigPayload | None = ...,
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
    "SshConfig",
    "SshConfigPayload",
]