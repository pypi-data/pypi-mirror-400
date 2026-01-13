from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SSH_KEX_ALGO: Literal[{"description": "diffie-hellman-group1-sha1    diffie-hellman-group14-sha1:diffie-hellman-group14-sha1    diffie-hellman-group14-sha256:diffie-hellman-group14-sha256    diffie-hellman-group16-sha512:diffie-hellman-group16-sha512    diffie-hellman-group18-sha512:diffie-hellman-group18-sha512    diffie-hellman-group-exchange-sha1:diffie-hellman-group-exchange-sha1    diffie-hellman-group-exchange-sha256:diffie-hellman-group-exchange-sha256    curve25519-sha256@libssh", "help": "diffie-hellman-group1-sha1", "label": "Diffie Hellman Group1 Sha1", "name": "diffie-hellman-group1-sha1"}, {"help": "diffie-hellman-group14-sha1", "label": "Diffie Hellman Group14 Sha1", "name": "diffie-hellman-group14-sha1"}, {"help": "diffie-hellman-group14-sha256", "label": "Diffie Hellman Group14 Sha256", "name": "diffie-hellman-group14-sha256"}, {"help": "diffie-hellman-group16-sha512", "label": "Diffie Hellman Group16 Sha512", "name": "diffie-hellman-group16-sha512"}, {"help": "diffie-hellman-group18-sha512", "label": "Diffie Hellman Group18 Sha512", "name": "diffie-hellman-group18-sha512"}, {"help": "diffie-hellman-group-exchange-sha1", "label": "Diffie Hellman Group Exchange Sha1", "name": "diffie-hellman-group-exchange-sha1"}, {"help": "diffie-hellman-group-exchange-sha256", "label": "Diffie Hellman Group Exchange Sha256", "name": "diffie-hellman-group-exchange-sha256"}, {"help": "curve25519-sha256@libssh.org", "label": "Curve25519 Sha256@Libssh.Org", "name": "curve25519-sha256@libssh.org"}, {"help": "ecdh-sha2-nistp256", "label": "Ecdh Sha2 Nistp256", "name": "ecdh-sha2-nistp256"}, {"help": "ecdh-sha2-nistp384", "label": "Ecdh Sha2 Nistp384", "name": "ecdh-sha2-nistp384"}, {"help": "ecdh-sha2-nistp521", "label": "Ecdh Sha2 Nistp521", "name": "ecdh-sha2-nistp521"}]
VALID_BODY_SSH_ENC_ALGO: Literal[{"help": "chacha20-poly1305@openssh.com", "label": "Chacha20 Poly1305@Openssh.Com", "name": "chacha20-poly1305@openssh.com"}, {"help": "aes128-ctr", "label": "Aes128 Ctr", "name": "aes128-ctr"}, {"help": "aes192-ctr", "label": "Aes192 Ctr", "name": "aes192-ctr"}, {"help": "aes256-ctr", "label": "Aes256 Ctr", "name": "aes256-ctr"}, {"help": "arcfour256", "label": "Arcfour256", "name": "arcfour256"}, {"help": "arcfour128", "label": "Arcfour128", "name": "arcfour128"}, {"help": "aes128-cbc", "label": "Aes128 Cbc", "name": "aes128-cbc"}, {"help": "3des-cbc", "label": "3Des Cbc", "name": "3des-cbc"}, {"help": "blowfish-cbc", "label": "Blowfish Cbc", "name": "blowfish-cbc"}, {"help": "cast128-cbc", "label": "Cast128 Cbc", "name": "cast128-cbc"}, {"help": "aes192-cbc", "label": "Aes192 Cbc", "name": "aes192-cbc"}, {"help": "aes256-cbc", "label": "Aes256 Cbc", "name": "aes256-cbc"}, {"help": "arcfour", "label": "Arcfour", "name": "arcfour"}, {"help": "rijndael-cbc@lysator.liu.se", "label": "Rijndael Cbc@Lysator.Liu.Se", "name": "rijndael-cbc@lysator.liu.se"}, {"help": "aes128-gcm@openssh.com", "label": "Aes128 Gcm@Openssh.Com", "name": "aes128-gcm@openssh.com"}, {"help": "aes256-gcm@openssh.com", "label": "Aes256 Gcm@Openssh.Com", "name": "aes256-gcm@openssh.com"}]
VALID_BODY_SSH_MAC_ALGO: Literal[{"description": "hmac-md5    hmac-md5-etm@openssh", "help": "hmac-md5", "label": "Hmac Md5", "name": "hmac-md5"}, {"help": "hmac-md5-etm@openssh.com", "label": "Hmac Md5 Etm@Openssh.Com", "name": "hmac-md5-etm@openssh.com"}, {"help": "hmac-md5-96", "label": "Hmac Md5 96", "name": "hmac-md5-96"}, {"help": "hmac-md5-96-etm@openssh.com", "label": "Hmac Md5 96 Etm@Openssh.Com", "name": "hmac-md5-96-etm@openssh.com"}, {"help": "hmac-sha1", "label": "Hmac Sha1", "name": "hmac-sha1"}, {"help": "hmac-sha1-etm@openssh.com", "label": "Hmac Sha1 Etm@Openssh.Com", "name": "hmac-sha1-etm@openssh.com"}, {"help": "hmac-sha2-256", "label": "Hmac Sha2 256", "name": "hmac-sha2-256"}, {"help": "hmac-sha2-256-etm@openssh.com", "label": "Hmac Sha2 256 Etm@Openssh.Com", "name": "hmac-sha2-256-etm@openssh.com"}, {"help": "hmac-sha2-512", "label": "Hmac Sha2 512", "name": "hmac-sha2-512"}, {"help": "hmac-sha2-512-etm@openssh.com", "label": "Hmac Sha2 512 Etm@Openssh.Com", "name": "hmac-sha2-512-etm@openssh.com"}, {"help": "hmac-ripemd160", "label": "Hmac Ripemd160", "name": "hmac-ripemd160"}, {"help": "hmac-ripemd160@openssh.com", "label": "Hmac Ripemd160@Openssh.Com", "name": "hmac-ripemd160@openssh.com"}, {"help": "hmac-ripemd160-etm@openssh.com", "label": "Hmac Ripemd160 Etm@Openssh.Com", "name": "hmac-ripemd160-etm@openssh.com"}, {"help": "umac-64@openssh.com", "label": "Umac 64@Openssh.Com", "name": "umac-64@openssh.com"}, {"help": "umac-128@openssh.com", "label": "Umac 128@Openssh.Com", "name": "umac-128@openssh.com"}, {"help": "umac-64-etm@openssh.com", "label": "Umac 64 Etm@Openssh.Com", "name": "umac-64-etm@openssh.com"}, {"help": "umac-128-etm@openssh.com", "label": "Umac 128 Etm@Openssh.Com", "name": "umac-128-etm@openssh.com"}]
VALID_BODY_SSH_HSK_ALGO: Literal[{"description": "ssh-rsa    ecdsa-sha2-nistp521:ecdsa-sha2-nistp521    ecdsa-sha2-nistp384:ecdsa-sha2-nistp384    ecdsa-sha2-nistp256:ecdsa-sha2-nistp256    rsa-sha2-256:rsa-sha2-256    rsa-sha2-512:rsa-sha2-512    ssh-ed25519:ssh-ed25519", "help": "ssh-rsa", "label": "Ssh Rsa", "name": "ssh-rsa"}, {"help": "ecdsa-sha2-nistp521", "label": "Ecdsa Sha2 Nistp521", "name": "ecdsa-sha2-nistp521"}, {"help": "ecdsa-sha2-nistp384", "label": "Ecdsa Sha2 Nistp384", "name": "ecdsa-sha2-nistp384"}, {"help": "ecdsa-sha2-nistp256", "label": "Ecdsa Sha2 Nistp256", "name": "ecdsa-sha2-nistp256"}, {"help": "rsa-sha2-256", "label": "Rsa Sha2 256", "name": "rsa-sha2-256"}, {"help": "rsa-sha2-512", "label": "Rsa Sha2 512", "name": "rsa-sha2-512"}, {"help": "ssh-ed25519", "label": "Ssh Ed25519", "name": "ssh-ed25519"}]
VALID_BODY_SSH_HSK_OVERRIDE: Literal[{"description": "Disable SSH host key override in SSH daemon", "help": "Disable SSH host key override in SSH daemon.", "label": "Disable", "name": "disable"}, {"description": "Enable SSH host key override in SSH daemon", "help": "Enable SSH host key override in SSH daemon.", "label": "Enable", "name": "enable"}]

# Metadata dictionaries
FIELD_TYPES: dict[str, str]
FIELD_DESCRIPTIONS: dict[str, str]
FIELD_CONSTRAINTS: dict[str, dict[str, Any]]
NESTED_SCHEMAS: dict[str, dict[str, Any]]
FIELDS_WITH_DEFAULTS: dict[str, Any]

# Helper functions
def get_field_type(field_name: str) -> str | None: ...
def get_field_description(field_name: str) -> str | None: ...
def get_field_default(field_name: str) -> Any: ...
def get_field_constraints(field_name: str) -> dict[str, Any]: ...
def get_nested_schema(field_name: str) -> dict[str, Any] | None: ...
def get_field_metadata(field_name: str) -> dict[str, Any]: ...
def validate_field_value(field_name: str, value: Any) -> bool: ...
def get_all_fields() -> list[str]: ...
def get_required_fields() -> list[str]: ...
def get_schema_info() -> dict[str, Any]: ...


__all__ = [
    "VALID_BODY_SSH_KEX_ALGO",
    "VALID_BODY_SSH_ENC_ALGO",
    "VALID_BODY_SSH_MAC_ALGO",
    "VALID_BODY_SSH_HSK_ALGO",
    "VALID_BODY_SSH_HSK_OVERRIDE",
    "FIELD_TYPES",
    "FIELD_DESCRIPTIONS",
    "FIELD_CONSTRAINTS",
    "NESTED_SCHEMAS",
    "FIELDS_WITH_DEFAULTS",
    "get_field_type",
    "get_field_description",
    "get_field_default",
    "get_field_constraints",
    "get_nested_schema",
    "get_field_metadata",
    "validate_field_value",
    "get_all_fields",
    "get_required_fields",
    "get_schema_info",
]