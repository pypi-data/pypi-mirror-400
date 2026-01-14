"""Encryption utilities for sensitive data protection.

This module provides encryption/decryption functionality for sensitive
configuration data like database passwords, API keys, and tokens.

Uses Fernet symmetric encryption from the cryptography library.
Keys are automatically generated and stored securely.

Example:
    # Encrypt a value
    encrypted = encrypt_value("my_secret_password")

    # Decrypt a value
    decrypted = decrypt_value(encrypted)

    # Encrypt entire config
    config = {"password": "secret", "host": "localhost"}
    encrypted_config = encrypt_config(config)
"""

from __future__ import annotations

import base64
import hashlib
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Lazy import cryptography to make it optional
_fernet_available = True
try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    _fernet_available = False
    Fernet = None
    InvalidToken = Exception


# Fields that should be encrypted when storing
SENSITIVE_FIELDS = frozenset({
    "password",
    "secret",
    "token",
    "api_key",
    "private_key",
    "access_key",
    "secret_key",
    "webhook_url",
    "connection_string",
})


class EncryptionError(Exception):
    """Raised when encryption/decryption fails."""

    pass


class EncryptionKeyManager:
    """Manages encryption keys for the application.

    Handles key generation, storage, and retrieval with proper
    file permissions for security.
    """

    def __init__(self, key_path: Path | None = None) -> None:
        """Initialize key manager.

        Args:
            key_path: Path to store encryption key. Defaults to ~/.truthound/.key
        """
        from truthound_dashboard.config import get_settings

        settings = get_settings()
        self._key_path = key_path or (settings.data_dir / ".key")
        self._key: bytes | None = None

    def _ensure_directory(self) -> None:
        """Ensure key directory exists with proper permissions."""
        self._key_path.parent.mkdir(parents=True, exist_ok=True)

    def generate_key(self) -> bytes:
        """Generate a new encryption key.

        Returns:
            New Fernet key.
        """
        if not _fernet_available:
            raise EncryptionError(
                "cryptography package not installed. "
                "Install with: pip install cryptography"
            )
        return Fernet.generate_key()

    def derive_key(self, password: str, salt: bytes | None = None) -> bytes:
        """Derive encryption key from password.

        Uses PBKDF2-like derivation for key generation from password.

        Args:
            password: Password to derive key from.
            salt: Optional salt for derivation. Generates random if not provided.

        Returns:
            Derived encryption key.
        """
        if salt is None:
            salt = os.urandom(16)

        # Simple derivation using SHA-256
        # For production, consider using proper PBKDF2 or Argon2
        key_material = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(key_material)

    def get_key(self) -> bytes:
        """Get or create encryption key.

        Loads existing key from file or generates new one.

        Returns:
            Encryption key bytes.
        """
        if self._key is not None:
            return self._key

        if self._key_path.exists():
            self._key = self._key_path.read_bytes()
            return self._key

        # Generate new key
        self._ensure_directory()
        self._key = self.generate_key()
        self._key_path.write_bytes(self._key)

        # Restrict file permissions (Unix only)
        try:
            os.chmod(self._key_path, 0o600)
        except (OSError, AttributeError):
            # Windows doesn't support chmod
            pass

        logger.info(f"Generated new encryption key at {self._key_path}")
        return self._key

    def rotate_key(self, old_key: bytes | None = None) -> bytes:
        """Rotate encryption key.

        Args:
            old_key: Old key to backup. Current key used if not provided.

        Returns:
            New encryption key.
        """
        if old_key is None and self._key_path.exists():
            old_key = self._key_path.read_bytes()

        # Backup old key
        if old_key:
            backup_path = self._key_path.with_suffix(".key.bak")
            backup_path.write_bytes(old_key)
            logger.info(f"Backed up old key to {backup_path}")

        # Generate and save new key
        self._key = self.generate_key()
        self._ensure_directory()
        self._key_path.write_bytes(self._key)

        try:
            os.chmod(self._key_path, 0o600)
        except (OSError, AttributeError):
            pass

        logger.info("Encryption key rotated successfully")
        return self._key


class Encryptor:
    """Handles encryption and decryption of values.

    Uses Fernet symmetric encryption for secure data protection.
    """

    def __init__(self, key: bytes | None = None) -> None:
        """Initialize encryptor.

        Args:
            key: Encryption key. Uses KeyManager if not provided.
        """
        if not _fernet_available:
            self._fernet = None
            return

        if key is None:
            key = EncryptionKeyManager().get_key()

        self._fernet = Fernet(key)

    def encrypt(self, value: str) -> str:
        """Encrypt a string value.

        Args:
            value: Plain text value to encrypt.

        Returns:
            Encrypted value as base64 string.

        Raises:
            EncryptionError: If encryption fails or not available.
        """
        if self._fernet is None:
            logger.warning("Encryption not available, returning plain value")
            return value

        try:
            encrypted = self._fernet.encrypt(value.encode())
            return encrypted.decode()
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {e}") from e

    def decrypt(self, encrypted: str) -> str:
        """Decrypt an encrypted value.

        Args:
            encrypted: Encrypted base64 string.

        Returns:
            Decrypted plain text value.

        Raises:
            EncryptionError: If decryption fails.
        """
        if self._fernet is None:
            logger.warning("Encryption not available, returning as-is")
            return encrypted

        try:
            decrypted = self._fernet.decrypt(encrypted.encode())
            return decrypted.decode()
        except InvalidToken as e:
            raise EncryptionError("Invalid encryption token or corrupted data") from e
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {e}") from e

    def is_encrypted(self, value: str) -> bool:
        """Check if a value appears to be encrypted.

        Args:
            value: Value to check.

        Returns:
            True if value appears to be Fernet encrypted.
        """
        if not value or len(value) < 32:
            return False

        try:
            # Fernet tokens are base64 encoded and start with 'gAAAAA'
            return value.startswith("gAAAAA")
        except Exception:
            return False


# Module-level singleton
_encryptor: Encryptor | None = None


def get_encryptor() -> Encryptor:
    """Get encryptor singleton.

    Returns:
        Encryptor instance.
    """
    global _encryptor
    if _encryptor is None:
        _encryptor = Encryptor()
    return _encryptor


def reset_encryptor() -> None:
    """Reset encryptor singleton (for testing)."""
    global _encryptor
    _encryptor = None


# Convenience functions


def encrypt_value(value: str) -> str:
    """Encrypt a string value.

    Args:
        value: Plain text value.

    Returns:
        Encrypted value.
    """
    return get_encryptor().encrypt(value)


def decrypt_value(encrypted: str) -> str:
    """Decrypt an encrypted value.

    Args:
        encrypted: Encrypted value.

    Returns:
        Decrypted plain text.
    """
    return get_encryptor().decrypt(encrypted)


def is_sensitive_field(field_name: str) -> bool:
    """Check if a field name indicates sensitive data.

    Args:
        field_name: Field name to check.

    Returns:
        True if field should be encrypted.
    """
    field_lower = field_name.lower()
    return any(sensitive in field_lower for sensitive in SENSITIVE_FIELDS)


def encrypt_config(config: dict[str, Any]) -> dict[str, Any]:
    """Encrypt sensitive fields in a configuration dictionary.

    Recursively encrypts values for fields that match sensitive field patterns.
    Encrypted values are stored with a special marker.

    Args:
        config: Configuration dictionary.

    Returns:
        New dictionary with sensitive fields encrypted.
    """
    encryptor = get_encryptor()
    encrypted = {}

    for key, value in config.items():
        if isinstance(value, dict):
            # Recursively encrypt nested dictionaries
            encrypted[key] = encrypt_config(value)
        elif isinstance(value, str) and value and is_sensitive_field(key):
            # Encrypt sensitive string values
            if not encryptor.is_encrypted(value):
                encrypted[key] = {"_encrypted": encryptor.encrypt(value)}
            else:
                encrypted[key] = {"_encrypted": value}
        else:
            encrypted[key] = value

    return encrypted


def decrypt_config(config: dict[str, Any]) -> dict[str, Any]:
    """Decrypt sensitive fields in a configuration dictionary.

    Recursively decrypts values that have the encryption marker.

    Args:
        config: Configuration dictionary with encrypted fields.

    Returns:
        New dictionary with sensitive fields decrypted.
    """
    encryptor = get_encryptor()
    decrypted = {}

    for key, value in config.items():
        if isinstance(value, dict):
            if "_encrypted" in value:
                # Decrypt marked field
                try:
                    decrypted[key] = encryptor.decrypt(value["_encrypted"])
                except EncryptionError:
                    # If decryption fails, keep the encrypted value
                    logger.warning(f"Failed to decrypt field: {key}")
                    decrypted[key] = value["_encrypted"]
            else:
                # Recursively decrypt nested dictionaries
                decrypted[key] = decrypt_config(value)
        else:
            decrypted[key] = value

    return decrypted


def mask_sensitive_value(value: str, visible_chars: int = 4) -> str:
    """Mask a sensitive value for display.

    Args:
        value: Value to mask.
        visible_chars: Number of characters to show at end.

    Returns:
        Masked value like '***abc'.
    """
    if len(value) <= visible_chars:
        return "***"
    return "***" + value[-visible_chars:]
