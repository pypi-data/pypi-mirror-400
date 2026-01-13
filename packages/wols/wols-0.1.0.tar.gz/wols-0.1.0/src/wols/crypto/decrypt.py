"""Specimen decryption functionality."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from wols.core.parse import parse_specimen
from wols.exceptions import WolsEncryptionError

if TYPE_CHECKING:
    from wols.models.specimen import Specimen


def _get_key_bytes(key: bytes | str) -> bytes:
    """Convert key to bytes, handling base64 strings."""
    if isinstance(key, bytes):
        if len(key) != 32:
            raise WolsEncryptionError(
                message=f"Key must be 32 bytes, got {len(key)}",
                code="INVALID_KEY",
            )
        return key
    else:
        try:
            key_bytes = base64.b64decode(key)
            if len(key_bytes) != 32:
                raise WolsEncryptionError(
                    message=f"Decoded key must be 32 bytes, got {len(key_bytes)}",
                    code="INVALID_KEY",
                )
            return key_bytes
        except Exception as e:
            raise WolsEncryptionError(
                message=f"Failed to decode key: {e}",
                code="INVALID_KEY",
            ) from e


def decrypt_specimen(
    payload: str,
    key: bytes | str,
) -> Specimen:
    """Decrypt an encrypted specimen payload.

    Args:
        payload: Base64-encoded encrypted payload.
        key: 32-byte key or base64-encoded key string.

    Returns:
        Decrypted Specimen.

    Raises:
        WolsEncryptionError: If decryption fails (wrong key, corrupted data).

    Example:
        >>> specimen = decrypt_specimen(encrypted, key)
    """
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as e:
        raise ImportError(
            "Crypto module not installed. Install with: pip install wols\\[crypto]"
        ) from e

    key_bytes = _get_key_bytes(key)

    # Decode payload
    try:
        encrypted_data = base64.b64decode(payload)
    except Exception as e:
        raise WolsEncryptionError(
            message=f"Failed to decode payload: {e}",
            code="INVALID_PAYLOAD",
        ) from e

    if len(encrypted_data) < 12:
        raise WolsEncryptionError(
            message="Encrypted payload too short",
            code="INVALID_PAYLOAD",
        )

    # Extract nonce and ciphertext
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]

    # Decrypt
    try:
        aesgcm = AESGCM(key_bytes)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise WolsEncryptionError(
            message=f"Decryption failed: {e}",
            code="DECRYPTION_ERROR",
        ) from e

    # Parse decrypted JSON
    json_str = plaintext.decode("utf-8")
    return parse_specimen(json_str)
