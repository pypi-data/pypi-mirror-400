# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

"""
Type stubs for nss.nss module.

This file provides type hints for the C extension module nss.nss.
"""

from typing import Any, Callable, Optional, Union, Tuple, List, overload

# Version information
def nss_get_version() -> str:
    """Get the NSS library version string."""
    ...

def nss_version_check(version: str) -> bool:
    """Check if NSS version meets minimum requirement."""
    ...

# NSS initialization and shutdown
def nss_init(cert_dir: str) -> None:
    """Initialize NSS with a certificate database directory."""
    ...

def nss_init_nodb() -> None:
    """Initialize NSS without a certificate database."""
    ...

def nss_init_read_write(cert_dir: str) -> None:
    """Initialize NSS with read-write access to certificate database."""
    ...

def nss_shutdown() -> None:
    """Shutdown NSS and free resources."""
    ...

def nss_is_initialized() -> bool:
    """Check if NSS has been initialized."""
    ...

def set_shutdown_callback(
    callback: Optional[Callable[..., bool]],
    *args: Any
) -> None:
    """Set a callback function to be called when NSS shuts down."""
    ...

# Password callback
def set_password_callback(callback: Optional[Callable[..., str]]) -> None:
    """Set a callback function for password requests."""
    ...

# Certificate database
def get_default_certdb() -> Any:
    """Get the default certificate database."""
    ...

# Certificate lookup
def find_cert_from_nickname(nickname: str, *pin_args: Any) -> Certificate:
    """Find a certificate by its nickname."""
    ...

def find_certs_from_nickname(nickname: str, *pin_args: Any) -> List[Certificate]:
    """Find all certificates with the given nickname."""
    ...

def find_certs_from_email_addr(email: str, *pin_args: Any) -> List[Certificate]:
    """Find certificates associated with an email address."""
    ...

def find_key_by_any_cert(cert: Certificate, *pin_args: Any) -> Any:
    """Find the private key associated with a certificate."""
    ...

def get_cert_nicknames(certdb: Any, what: int, *user_data: Any) -> List[str]:
    """Get certificate nicknames from the database.

    Args:
        certdb: Certificate database object
        what: SEC_CERT_NICKNAMES_ALL, SEC_CERT_NICKNAMES_USER, or SEC_CERT_NICKNAMES_SERVER
        *user_data: Optional callback parameters

    Returns:
        List of certificate nicknames
    """
    ...

def generate_random(num_bytes: int) -> bytes:
    """Generate random bytes using NSS PRNG."""
    ...

def get_fips_mode() -> bool:
    """Check if FIPS mode is enabled."""
    ...

# Digest/hash functions
def md5_digest(data: bytes) -> bytes:
    """Compute MD5 digest of data."""
    ...

def sha1_digest(data: bytes) -> bytes:
    """Compute SHA-1 digest of data."""
    ...

def sha256_digest(data: bytes) -> bytes:
    """Compute SHA-256 digest of data."""
    ...

def sha512_digest(data: bytes) -> bytes:
    """Compute SHA-512 digest of data."""
    ...

def hash_buf(algorithm: int, data: bytes) -> bytes:
    """Compute hash of data using specified algorithm."""
    ...

# Utility functions
def read_hex(hex_string: str, separator: Optional[str] = None) -> bytes:
    """Convert hex string to bytes."""
    ...

def oid_str(oid: Union[int, SecItem]) -> str:
    """Get string representation of an OID."""
    ...

# OCSP and validation settings
def get_use_pkix_for_validation() -> bool:
    """Get whether PKIX validation is enabled."""
    ...

def set_use_pkix_for_validation(enable: bool) -> None:
    """Enable or disable PKIX validation."""
    ...

def enable_ocsp_checking(certdb: Optional[Any] = None) -> None:
    """Enable OCSP checking."""
    ...

def disable_ocsp_checking(certdb: Optional[Any] = None) -> None:
    """Disable OCSP checking."""
    ...

def set_ocsp_cache_settings(
    max_cache_entries: int,
    minimum_seconds_to_next_fetch: int,
    maximum_seconds_before_cached_response_reused: int
) -> None:
    """Set OCSP cache parameters."""
    ...

def set_ocsp_failure_mode(mode: int) -> None:
    """Set the OCSP failure mode."""
    ...

def set_ocsp_timeout(seconds: int) -> None:
    """Set the OCSP timeout in seconds."""
    ...

def clear_ocsp_cache() -> None:
    """Remove all items currently stored in the OCSP cache."""
    ...

def set_ocsp_default_responder(url: str) -> None:
    """Set the default OCSP responder URL."""
    ...

def enable_ocsp_default_responder(certdb: Optional[Any] = None) -> None:
    """Enable the default OCSP responder."""
    ...

def disable_ocsp_default_responder(certdb: Optional[Any] = None) -> None:
    """Disable the default OCSP responder."""
    ...

# Digest and cryptographic operations
def create_digest_context(algorithm: int) -> Any:
    """Create a digest context for the specified algorithm."""
    ...

def create_context_by_sym_key(
    mechanism: int,
    operation: int,
    key: Any,
    params: Optional[Any] = None
) -> Any:
    """Create a cryptographic context using a symmetric key."""
    ...

def create_pbev2_algorithm_id(
    pbe_alg: int,
    cipher_alg: int,
    prf_alg: int,
    key_length: int,
    iterations: int,
    salt: Optional[bytes] = None
) -> AlgorithmID:
    """Create a PBKDF2 algorithm ID."""
    ...

# Algorithm constants for digest
SEC_OID_MD5: int
SEC_OID_SHA1: int
SEC_OID_SHA256: int
SEC_OID_SHA384: int
SEC_OID_SHA512: int

# PK11 slot and token operations
def get_best_slot(mechanism: int) -> PK11Slot:
    """Get the best slot for a given mechanism."""
    ...

def get_internal_slot() -> PK11Slot:
    """Get the internal cryptographic slot."""
    ...

def get_internal_key_slot() -> PK11Slot:
    """Get the internal key slot."""
    ...

def get_all_tokens(
    mechanism: int = 0,
    need_rw: bool = False,
    load_certs: bool = False,
    *pin_args: Any
) -> List[PK11Slot]:
    """Get all available tokens."""
    ...

def find_slot_by_name(name: str) -> PK11Slot:
    """Find a slot by its name."""
    ...

def pk11_logout_all() -> None:
    """Log out from all slots."""
    ...

def need_pw_init() -> bool:
    """Check if password initialization is needed."""
    ...

def token_exists(mechanism: int) -> bool:
    """Check if a token exists for the given mechanism."""
    ...

def is_fips() -> bool:
    """Check if FIPS mode is enabled."""
    ...

# Key and parameter operations
def import_sym_key(
    slot: PK11Slot,
    mechanism: int,
    origin: int,
    operation: int,
    key_data: bytes
) -> Any:
    """Import a symmetric key."""
    ...

def pub_wrap_sym_key(
    mechanism: int,
    pub_key: Any,
    sym_key: Any
) -> bytes:
    """Wrap a symmetric key with a public key."""
    ...

def param_from_iv(mechanism: int, iv: Optional[bytes] = None) -> SecItem:
    """Create parameters from an initialization vector."""
    ...

def param_from_algid(alg_id: AlgorithmID) -> SecItem:
    """Create parameters from an algorithm ID."""
    ...

def generate_new_param(mechanism: int, sym_key: Optional[Any] = None) -> SecItem:
    """Generate new parameters for a mechanism."""
    ...

def algtag_to_mechanism(algtag: int) -> int:
    """Convert an algorithm tag to a mechanism."""
    ...

def mechanism_to_algtag(mechanism: int) -> int:
    """Convert a mechanism to an algorithm tag."""
    ...

def get_iv_length(mechanism: int) -> int:
    """Get the IV length for a mechanism."""
    ...

def get_block_size(mechanism: int, params: Optional[SecItem] = None) -> int:
    """Get the block size for a mechanism."""
    ...

def get_pad_mechanism(mechanism: int) -> int:
    """Get the padding mechanism for a given mechanism."""
    ...

# Data conversion utilities
def data_to_hex(data: bytes, octets_per_line: int = 16) -> str:
    """Convert binary data to hexadecimal string."""
    ...

def make_line_fmt_tuples(
    level: int,
    *lines: str
) -> List[Tuple[int, str]]:
    """Create formatted line tuples for indented output."""
    ...

def indented_format(tuples: List[Tuple[int, str]]) -> str:
    """Format indented text from line tuples."""
    ...

def read_der_from_file(filepath: str, ascii: bool = False) -> bytes:
    """Read DER-encoded data from a file."""
    ...

def base64_to_binary(data: str) -> bytes:
    """Convert base64 string to binary data."""
    ...

def fingerprint_format_lines(
    fingerprint: bytes,
    level: int = 0
) -> List[Tuple[int, str]]:
    """Format fingerprint as indented lines."""
    ...

# Name and type conversion functions
def key_mechanism_type_name(mechanism: int) -> str:
    """Get the name of a key mechanism type."""
    ...

def key_mechanism_type_from_name(name: str) -> int:
    """Get the mechanism type from its name."""
    ...

def pk11_attribute_type_name(attr_type: int) -> str:
    """Get the name of a PK11 attribute type."""
    ...

def pk11_attribute_type_from_name(name: str) -> int:
    """Get the PK11 attribute type from its name."""
    ...

def pk11_disabled_reason_str(reason: int) -> str:
    """Get the string description of a disabled reason."""
    ...

def pk11_disabled_reason_name(reason: int) -> str:
    """Get the name of a disabled reason."""
    ...

def oid_tag_name(tag: int) -> str:
    """Get the name of an OID tag."""
    ...

def oid_tag(oid: Union[str, SecItem]) -> int:
    """Get the tag for an OID."""
    ...

def oid_dotted_decimal(oid: Union[int, SecItem]) -> str:
    """Get the dotted decimal representation of an OID."""
    ...

def list_certs(certdb: Any, *user_data: Any) -> List[Certificate]:
    """List all certificates in the database."""
    ...

def cert_crl_reason_name(reason: int) -> str:
    """Get the name of a CRL reason code."""
    ...

def cert_crl_reason_from_name(name: str) -> int:
    """Get the CRL reason code from its name."""
    ...

def cert_general_name_type_name(name_type: int) -> str:
    """Get the name of a general name type."""
    ...

def cert_general_name_type_from_name(name: str) -> int:
    """Get the general name type from its name."""
    ...

# Certificate and key usage flags
def cert_usage_flags(usage: int) -> List[str]:
    """Get list of certificate usage flag names."""
    ...

def key_usage_flags(usage: int) -> List[str]:
    """Get list of key usage flag names."""
    ...

def cert_type_flags(cert_type: int) -> List[str]:
    """Get list of certificate type flag names."""
    ...

def nss_init_flags(flags: int) -> List[str]:
    """Get list of NSS init flag names."""
    ...

def x509_key_usage(flags: int, repr_kind: int = 0) -> Union[str, List[str]]:
    """Get X.509 key usage representation."""
    ...

def x509_cert_type(flags: int, repr_kind: int = 0) -> Union[str, List[str]]:
    """Get X.509 certificate type representation."""
    ...

def x509_ext_key_usage(oid_seq: SecItem, repr_kind: int = 0) -> Union[str, List[str]]:
    """Get X.509 extended key usage representation."""
    ...

def x509_alt_name(gen_names: Any, repr_kind: int = 0) -> Union[str, List[str]]:
    """Get X.509 alternative name representation."""
    ...

# CRL operations
def import_crl(
    certdb: Any,
    der_crl: bytes,
    url: Optional[str] = None,
    crl_type: int = 0
) -> Any:
    """Import a CRL into the certificate database."""
    ...

def decode_der_crl(der_crl: bytes, crl_type: int = 0) -> Any:
    """Decode a DER-encoded CRL."""
    ...

# PKCS#12 operations
def pkcs12_enable_cipher(cipher: int, enable: bool) -> None:
    """Enable or disable a PKCS#12 cipher."""
    ...

def pkcs12_enable_all_ciphers() -> None:
    """Enable all PKCS#12 ciphers."""
    ...

def pkcs12_set_preferred_cipher(cipher: int, enable: bool) -> None:
    """Set the preferred PKCS#12 cipher."""
    ...

def pkcs12_cipher_name(cipher: int) -> str:
    """Get the name of a PKCS#12 cipher."""
    ...

def pkcs12_cipher_from_name(name: str) -> int:
    """Get the PKCS#12 cipher from its name."""
    ...

def pkcs12_map_cipher(old_cipher: int, prefer_des: bool = False) -> int:
    """Map a PKCS#12 cipher to a new cipher."""
    ...

def pkcs12_set_nickname_collision_callback(callback: Callable[..., str]) -> None:
    """Set a callback for handling nickname collisions during PKCS#12 import."""
    ...

def pkcs12_export(
    nickname: str,
    output_file: str,
    pk12_passwd: str,
    cert_db_passwd: Optional[str] = None
) -> None:
    """Export a certificate and its private key to a PKCS#12 file."""
    ...

# Constants
CKA_ENCRYPT: int
CKA_DECRYPT: int
CKA_SIGN: int
CKA_VERIFY: int

# Certificate usage constants
certificateUsageSSLClient: int
certificateUsageSSLServer: int
certificateUsageSSLServerWithStepUp: int
certificateUsageSSLCA: int
certificateUsageEmailSigner: int
certificateUsageEmailRecipient: int
certificateUsageObjectSigner: int
certificateUsageUserCertImport: int
certificateUsageVerifyCA: int
certificateUsageProtectedObjectSigner: int
certificateUsageStatusResponder: int
certificateUsageAnyCA: int

# Certificate nickname types
SEC_CERT_NICKNAMES_ALL: int
SEC_CERT_NICKNAMES_USER: int
SEC_CERT_NICKNAMES_SERVER: int

# OCSP mode constants
ocspMode_FailureIsVerificationFailure: int
ocspMode_FailureIsNotAVerificationFailure: int

# Algorithm OIDs (examples - add more as needed)
SEC_OID_PKCS5_PBKDF2: int
SEC_OID_AES_256_CBC: int
SEC_OID_HMAC_SHA1: int

class SecItem:
    """Represents a security item (binary data)."""

    def __init__(
        self,
        data: Optional[Union[bytes, str]] = None,
        ascii: bool = False
    ) -> None:
        """
        Create a SecItem.

        Args:
            data: Binary data or base64 string
            ascii: If True, data is treated as base64
        """
        ...

    def to_base64(self, chars_per_line: int = 64) -> str:
        """Convert to base64 string."""
        ...

    @property
    def data(self) -> bytes:
        """Get the raw binary data."""
        ...

class Certificate:
    """Represents an X.509 certificate."""

    def __init__(self, data: bytes) -> None:
        """Create a certificate from DER-encoded data."""
        ...

    @staticmethod
    def new_from_der(data: bytes) -> Certificate:
        """Create a certificate from DER-encoded data."""
        ...

    @property
    def subject(self) -> str:
        """Get the certificate subject."""
        ...

    @property
    def issuer(self) -> str:
        """Get the certificate issuer."""
        ...

    @property
    def serial_number(self) -> int:
        """Get the certificate serial number."""
        ...

    def verify_now(
        self,
        certdb: Any,
        check_sig: bool,
        usage: int,
        *pin_args: Any
    ) -> int:
        """Verify the certificate."""
        ...

    def verify_hostname(self, hostname: str) -> bool:
        """Verify that the certificate matches the hostname."""
        ...

    def format_lines(self, level: int = 0) -> List[Tuple[int, str]]:
        """Format certificate information as indented lines."""
        ...

class SymKey:
    """Represents a symmetric cryptographic key."""

    @property
    def key_type(self) -> int:
        """Get the key type."""
        ...

    @property
    def key_length(self) -> int:
        """Get the key length in bits."""
        ...

    def format_lines(self, level: int = 0) -> List[Tuple[int, str]]:
        """Format key information as indented lines."""
        ...

class AlgorithmID:
    """Represents a cryptographic algorithm identifier."""

    def get_pbe_crypto_mechanism(self, key: SymKey) -> Tuple[int, SecItem]:
        """Get the cryptographic mechanism and parameters."""
        ...

    def format_lines(self, level: int = 0) -> List[Tuple[int, str]]:
        """Format algorithm ID information as indented lines."""
        ...

class Context:
    """Represents a cryptographic context."""

    def cipher_op(self, data: bytes) -> bytes:
        """Perform a cipher operation on data."""
        ...

    def digest_final(self) -> bytes:
        """Finalize the digest and return remaining data."""
        ...

class PK11Slot:
    """Represents a PKCS#11 cryptographic slot."""

    @property
    def token_name(self) -> str:
        """Get the token name."""
        ...

    @property
    def slot_name(self) -> str:
        """Get the slot name."""
        ...

    def is_hw(self) -> bool:
        """Check if this is a hardware slot."""
        ...

    def is_present(self) -> bool:
        """Check if the token is present in the slot."""
        ...

    def is_read_only(self) -> bool:
        """Check if the slot is read-only."""
        ...

    def is_internal(self) -> bool:
        """Check if this is an internal slot."""
        ...

    def need_login(self) -> bool:
        """Check if login is needed."""
        ...

    def need_user_init(self) -> bool:
        """Check if user initialization is needed."""
        ...

    def is_friendly(self) -> bool:
        """Check if the slot is friendly."""
        ...

    def is_removable(self) -> bool:
        """Check if the token is removable."""
        ...

    def is_logged_in(self) -> bool:
        """Check if logged in to the slot."""
        ...

    def has_protected_authentication_path(self) -> bool:
        """Check if the slot has a protected authentication path."""
        ...

    def is_disabled(self) -> bool:
        """Check if the slot is disabled."""
        ...

    def has_root_certs(self) -> bool:
        """Check if the slot has root certificates."""
        ...

    def get_disabled_reason(self) -> int:
        """Get the reason why the slot is disabled."""
        ...

    def user_disable(self) -> None:
        """Disable the slot."""
        ...

    def user_enable(self) -> None:
        """Enable the slot."""
        ...

    def authenticate(self, force: bool = False, *pin_args: Any) -> None:
        """Authenticate to the slot."""
        ...

    def check_security_officer_passwd(self, password: str) -> None:
        """Check the security officer password."""
        ...

    def check_user_passwd(self, password: str) -> None:
        """Check the user password."""
        ...

    def change_passwd(
        self,
        old_passwd: Optional[str] = None,
        new_passwd: Optional[str] = None
    ) -> None:
        """Change the slot password."""
        ...

    def init_pin(
        self,
        passwd: Optional[str] = None
    ) -> None:
        """Initialize the PIN."""
        ...

    def logout(self) -> None:
        """Log out from the slot."""
        ...

    def get_best_wrap_mechanism(self) -> int:
        """Get the best wrap mechanism for this slot."""
        ...

    def get_best_key_length(self, mechanism: int) -> int:
        """Get the best key length for a mechanism."""
        ...

    def key_gen(
        self,
        mechanism: int,
        params: Optional[SecItem] = None,
        key_size: int = 0,
        *pin_args: Any
    ) -> Any:
        """Generate a key."""
        ...

    def generate_key_pair(
        self,
        mechanism: int,
        params: Optional[Any] = None,
        *pin_args: Any
    ) -> Tuple[Any, Any]:
        """Generate a key pair."""
        ...

    def list_certs(self) -> List[Certificate]:
        """List all certificates in the slot."""
        ...

    def pbe_key_gen(
        self,
        alg_id: AlgorithmID,
        password: str
    ) -> Any:
        """Generate a password-based encryption key."""
        ...

    def format_lines(self, level: int = 0) -> List[Tuple[int, str]]:
        """Format slot information as indented lines."""
        ...

    def format(self, level: int = 0, indent: str = "    ") -> str:
        """Format slot information as a string."""
        ...

class PK11SymKey:
    """Represents a PKCS#11 symmetric key."""

    @property
    def key_type(self) -> int:
        """Get the key type."""
        ...

    @property
    def key_length(self) -> int:
        """Get the key length in bits."""
        ...

    @property
    def slot(self) -> PK11Slot:
        """Get the slot containing this key."""
        ...

    def derive(
        self,
        mechanism: int,
        params: Optional[SecItem] = None,
        target: int = 0,
        operation: int = 0,
        key_size: int = 0
    ) -> PK11SymKey:
        """Derive a new key from this key."""
        ...

    def wrap_sym_key(
        self,
        mechanism: int,
        params: Optional[SecItem],
        wrapping_key: PK11SymKey
    ) -> bytes:
        """Wrap this symmetric key with another key."""
        ...

    def unwrap_sym_key(
        self,
        mechanism: int,
        params: Optional[SecItem],
        wrapped_key: bytes,
        target: int,
        operation: int,
        key_size: int
    ) -> PK11SymKey:
        """Unwrap a symmetric key."""
        ...

    def format_lines(self, level: int = 0) -> List[Tuple[int, str]]:
        """Format key information as indented lines."""
        ...

    def format(self, level: int = 0, indent: str = "    ") -> str:
        """Format key information as a string."""
        ...

class PK11Context:
    """Represents a PKCS#11 cryptographic context."""

    def digest_key(self, key: PK11SymKey) -> None:
        """Digest a key."""
        ...

    def clone_context(self) -> PK11Context:
        """Clone this context."""
        ...

    def digest_begin(self) -> None:
        """Begin a digest operation."""
        ...

    def digest_op(self, data: bytes) -> None:
        """Update the digest with data."""
        ...

    def cipher_op(self, data: bytes) -> bytes:
        """Perform a cipher operation on data."""
        ...

    def finalize(self) -> bytes:
        """Finalize the operation and return remaining data."""
        ...

    def digest_final(self) -> bytes:
        """Finalize the digest and return the hash."""
        ...

class CertDB:
    """Represents a certificate database."""

    def find_crl_by_name(self, name: str, crl_type: int = 0) -> Any:
        """Find a CRL by name."""
        ...

    def find_crl_by_cert(self, cert: Certificate, crl_type: int = 0) -> Any:
        """Find a CRL by certificate."""
        ...

class DN:
    """Represents a Distinguished Name."""

    def __str__(self) -> str:
        """Get string representation."""
        ...

    def has_key(self, key: str) -> bool:
        """Check if the DN has a specific key."""
        ...

    def add_rdn(self, rdn: Any) -> None:
        """Add an RDN to the DN."""
        ...

class RDN:
    """Represents a Relative Distinguished Name."""

    def has_key(self, key: str) -> bool:
        """Check if the RDN has a specific key."""
        ...

class GeneralName:
    """Represents a general name in a certificate."""

    def get_name(self, repr_kind: int = 0) -> Union[str, Tuple[int, str]]:
        """Get the name representation."""
        ...

class CRLDistributionPt:
    """Represents a CRL distribution point."""

    def get_general_names(self, repr_kind: int = 0) -> Any:
        """Get the general names."""
        ...

    def get_reasons(self, repr_kind: int = 0) -> Any:
        """Get the reasons."""
        ...

    def format_lines(self, level: int = 0) -> List[Tuple[int, str]]:
        """Format as indented lines."""
        ...

    def format(self, level: int = 0, indent: str = "    ") -> str:
        """Format as a string."""
        ...

class SignedCRL:
    """Represents a signed CRL."""

    def delete_permanently(self) -> None:
        """Delete this CRL permanently from the database."""
        ...

class CertificateExtension:
    """Represents a certificate extension."""

    @property
    def oid(self) -> int:
        """Get the extension OID."""
        ...

    @property
    def critical(self) -> bool:
        """Check if the extension is critical."""
        ...

    @property
    def value(self) -> SecItem:
        """Get the extension value."""
        ...

    def format_lines(self, level: int = 0) -> List[Tuple[int, str]]:
        """Format as indented lines."""
        ...

    def format(self, level: int = 0, indent: str = "    ") -> str:
        """Format as a string."""
        ...

class PrivateKey:
    """Represents a private key."""

    @property
    def key_type(self) -> int:
        """Get the key type."""
        ...

class PublicKey:
    """Represents a public key."""

    @property
    def key_type(self) -> int:
        """Get the key type."""
        ...

    def format_lines(self, level: int = 0) -> List[Tuple[int, str]]:
        """Format as indented lines."""
        ...

    def format(self, level: int = 0, indent: str = "    ") -> str:
        """Format as a string."""
        ...

class RSAPublicKey:
    """Represents an RSA public key."""

    @property
    def modulus(self) -> SecItem:
        """Get the modulus."""
        ...

    @property
    def exponent(self) -> SecItem:
        """Get the exponent."""
        ...

    def format_lines(self, level: int = 0) -> List[Tuple[int, str]]:
        """Format as indented lines."""
        ...

    def format(self, level: int = 0, indent: str = "    ") -> str:
        """Format as a string."""
        ...

class DSAPublicKey:
    """Represents a DSA public key."""

    def format_lines(self, level: int = 0) -> List[Tuple[int, str]]:
        """Format as indented lines."""
        ...

    def format(self, level: int = 0, indent: str = "    ") -> str:
        """Format as a string."""
        ...

class SignedData:
    """Represents signed data."""

    @property
    def data(self) -> SecItem:
        """Get the data."""
        ...

    @property
    def signature(self) -> SecItem:
        """Get the signature."""
        ...

    def format_lines(self, level: int = 0) -> List[Tuple[int, str]]:
        """Format as indented lines."""
        ...

    def format(self, level: int = 0, indent: str = "    ") -> str:
        """Format as a string."""
        ...

class SubjectPublicKeyInfo:
    """Represents subject public key info."""

    def format_lines(self, level: int = 0) -> List[Tuple[int, str]]:
        """Format as indented lines."""
        ...

    def format(self, level: int = 0, indent: str = "    ") -> str:
        """Format as a string."""
        ...

class KEYPQGParams:
    """Represents PQG parameters for key generation."""

    def format_lines(self, level: int = 0) -> List[Tuple[int, str]]:
        """Format as indented lines."""
        ...

    def format(self, level: int = 0, indent: str = "    ") -> str:
        """Format as a string."""
        ...
