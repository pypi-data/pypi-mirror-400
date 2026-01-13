"""WOLS encryption and decryption.

Optional module - requires: pip install wols[crypto]
"""

from wols.crypto.decrypt import decrypt_specimen
from wols.crypto.encrypt import encrypt_specimen, encrypt_specimen_fields

__all__ = [
    "decrypt_specimen",
    "encrypt_specimen",
    "encrypt_specimen_fields",
]
