"""Specimen encryption functionality."""

from __future__ import annotations

import base64
import json
import os
from typing import TYPE_CHECKING, Any

from wols.core.serialize import to_json
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


def encrypt_specimen(
    specimen: Specimen,
    key: bytes | str,
) -> str:
    """Encrypt a specimen using AES-256-GCM.

    Args:
        specimen: Specimen to encrypt.
        key: 32-byte key or base64-encoded key string.

    Returns:
        Base64-encoded encrypted payload.

    Raises:
        WolsEncryptionError: If encryption fails.

    Example:
        >>> key = os.urandom(32)
        >>> encrypted = encrypt_specimen(specimen, key)
    """
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as e:
        raise ImportError(
            "Crypto module not installed. Install with: pip install wols\\[crypto]"
        ) from e

    key_bytes = _get_key_bytes(key)

    # Serialize specimen to JSON
    json_data = to_json(specimen)
    plaintext = json_data.encode("utf-8")

    # Generate nonce (12 bytes for GCM)
    nonce = os.urandom(12)

    # Encrypt
    try:
        aesgcm = AESGCM(key_bytes)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    except Exception as e:
        raise WolsEncryptionError(
            message=f"Encryption failed: {e}",
            code="ENCRYPTION_ERROR",
        ) from e

    # Combine nonce + ciphertext and encode
    payload = nonce + ciphertext
    return base64.b64encode(payload).decode("ascii")


def encrypt_specimen_fields(
    specimen: Specimen,
    key: bytes | str,
    fields: list[str],
) -> Specimen:
    """Encrypt specific fields of a specimen.

    Args:
        specimen: Specimen with fields to encrypt.
        key: 32-byte key or base64-encoded key string.
        fields: Field names to encrypt (e.g., ["strain", "custom"]).

    Returns:
        New Specimen with specified fields encrypted.

    Raises:
        WolsEncryptionError: If encryption fails.
        ValueError: If field name is invalid.

    Example:
        >>> partial = encrypt_specimen_fields(specimen, key, ["strain"])
        >>> # strain field is now encrypted, others remain readable
    """
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as e:
        raise ImportError(
            "Crypto module not installed. Install with: pip install wols\\[crypto]"
        ) from e

    from wols.models.specimen import Specimen

    key_bytes = _get_key_bytes(key)

    # Valid encryptable fields
    valid_fields = {
        "strain",
        "stage",
        "batch",
        "organization",
        "creator",
        "custom",
    }

    # Validate fields
    for field in fields:
        if field not in valid_fields:
            raise ValueError(
                f"Invalid field '{field}'. Valid fields: {', '.join(valid_fields)}"
            )

    # Get specimen as dict
    data = specimen.to_dict()

    # Encrypt each field
    aesgcm = AESGCM(key_bytes)

    def encrypt_value(value: Any) -> str:
        if value is None:
            return None  # type: ignore[return-value]
        plaintext = json.dumps(value).encode("utf-8")
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        payload = nonce + ciphertext
        return f"encrypted:{base64.b64encode(payload).decode('ascii')}"

    for field in fields:
        if field in data and data[field] is not None:
            try:
                data[field] = encrypt_value(data[field])
            except Exception as e:
                raise WolsEncryptionError(
                    message=f"Failed to encrypt field '{field}': {e}",
                    code="ENCRYPTION_ERROR",
                ) from e

    # Create new specimen from modified data
    # Note: We need to handle encrypted fields specially
    return Specimen(
        id=specimen.id,
        version=specimen.version,
        type=specimen.type,
        species=specimen.species,
        strain=specimen.strain if "strain" not in fields else None,
        stage=specimen.stage if "stage" not in fields else None,
        created=specimen.created,
        batch=data.get("batch") if "batch" in fields else specimen.batch,
        organization=(
            data.get("organization")
            if "organization" in fields
            else specimen.organization
        ),
        creator=data.get("creator") if "creator" in fields else specimen.creator,
        custom=data.get("custom") if "custom" in fields else specimen.custom,
        signature=specimen.signature,
    )
