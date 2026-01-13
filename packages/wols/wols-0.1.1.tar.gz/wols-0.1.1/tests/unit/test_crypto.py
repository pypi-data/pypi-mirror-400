"""Tests for wols.crypto module."""

import base64

import pytest

from wols import GrowthStage, Specimen, SpecimenType, Strain, WolsEncryptionError


@pytest.fixture
def crypto_specimen() -> Specimen:
    """Specimen for crypto tests."""
    return Specimen(
        id="wemush:abc123def456ghijklmnopqr",
        version="1.1.0",
        type=SpecimenType.SUBSTRATE,
        species="Pleurotus ostreatus",
    )


@pytest.fixture
def full_specimen() -> Specimen:
    """Full specimen with all fields for testing partial encryption."""
    return Specimen(
        id="wemush:abc123def456ghijklmnopqr",
        version="1.1.0",
        type=SpecimenType.SUBSTRATE,
        species="Pleurotus ostreatus",
        strain=Strain(name="Blue Oyster", generation=3),
        stage=GrowthStage.COLONIZATION,
        batch="BATCH-001",
        organization="WeMush",
        creator="test@example.com",
        custom={"temp": 72},
    )


@pytest.fixture
def encryption_key() -> bytes:
    """32-byte encryption key for testing."""
    return b"0123456789abcdef0123456789abcdef"


@pytest.fixture
def base64_key() -> str:
    """Base64-encoded 32-byte key."""
    return base64.b64encode(b"0123456789abcdef0123456789abcdef").decode()


class TestEncryptDecrypt:
    """Tests for encrypt/decrypt round-trip."""

    def test_encrypt_decrypt_roundtrip(
        self, crypto_specimen: Specimen, encryption_key: bytes
    ) -> None:
        """Test that encryption and decryption are reversible."""
        from wols.crypto import decrypt_specimen, encrypt_specimen

        encrypted = encrypt_specimen(crypto_specimen, encryption_key)
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0

        decrypted = decrypt_specimen(encrypted, encryption_key)
        assert decrypted.id == crypto_specimen.id
        assert decrypted.type == crypto_specimen.type
        assert decrypted.species == crypto_specimen.species

    def test_encrypt_produces_base64(
        self, crypto_specimen: Specimen, encryption_key: bytes
    ) -> None:
        """Test that encryption produces valid base64."""
        from wols.crypto import encrypt_specimen

        encrypted = encrypt_specimen(crypto_specimen, encryption_key)
        decoded = base64.b64decode(encrypted)
        assert len(decoded) > 12

    def test_wrong_key_fails(
        self, crypto_specimen: Specimen, encryption_key: bytes
    ) -> None:
        """Test that decryption with wrong key fails."""
        from wols.crypto import decrypt_specimen, encrypt_specimen

        encrypted = encrypt_specimen(crypto_specimen, encryption_key)

        # Use a different 32-byte key
        wrong_key = b"zyxwvutsrqponmlkzyxwvutsrqponmlk"
        with pytest.raises(WolsEncryptionError) as exc_info:
            decrypt_specimen(encrypted, wrong_key)
        assert "DECRYPTION_ERROR" in str(exc_info.value)

    def test_short_key_fails(self, crypto_specimen: Specimen) -> None:
        """Test that key shorter than 32 bytes fails."""
        from wols.crypto import encrypt_specimen

        short_key = b"too_short"
        with pytest.raises(WolsEncryptionError) as exc_info:
            encrypt_specimen(crypto_specimen, short_key)
        assert "INVALID_KEY" in str(exc_info.value)

    def test_base64_key(self, crypto_specimen: Specimen, base64_key: str) -> None:
        """Test that base64 encoded key works."""
        from wols.crypto import decrypt_specimen, encrypt_specimen

        encrypted = encrypt_specimen(crypto_specimen, base64_key)
        decrypted = decrypt_specimen(encrypted, base64_key)
        assert decrypted.id == crypto_specimen.id

    def test_invalid_base64_key(self, crypto_specimen: Specimen) -> None:
        """Test that invalid base64 key raises error."""
        from wols.crypto import encrypt_specimen

        with pytest.raises(WolsEncryptionError) as exc_info:
            encrypt_specimen(crypto_specimen, "not-valid-base64!!!")
        assert "INVALID_KEY" in str(exc_info.value)

    def test_corrupted_ciphertext(self, encryption_key: bytes) -> None:
        """Test that corrupted ciphertext fails."""
        from wols.crypto import decrypt_specimen

        # Valid base64 but invalid encrypted data
        with pytest.raises(WolsEncryptionError):
            decrypt_specimen("YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=", encryption_key)


class TestEncryptFields:
    """Tests for encrypt_specimen_fields function."""

    def test_encrypt_single_field(
        self, full_specimen: Specimen, encryption_key: bytes
    ) -> None:
        """Test encrypting a single field."""
        from wols.crypto import encrypt_specimen_fields

        result = encrypt_specimen_fields(full_specimen, encryption_key, ["batch"])
        # Batch should be encrypted (None after field encryption for strain/stage)
        assert result.id == full_specimen.id
        assert result.species == full_specimen.species

    def test_encrypt_multiple_fields(
        self, full_specimen: Specimen, encryption_key: bytes
    ) -> None:
        """Test encrypting multiple fields."""
        from wols.crypto import encrypt_specimen_fields

        result = encrypt_specimen_fields(
            full_specimen, encryption_key, ["batch", "organization", "custom"]
        )
        assert result.id == full_specimen.id

    def test_invalid_field_name(
        self, full_specimen: Specimen, encryption_key: bytes
    ) -> None:
        """Test that invalid field names raise ValueError."""
        from wols.crypto import encrypt_specimen_fields

        with pytest.raises(ValueError) as exc_info:
            encrypt_specimen_fields(full_specimen, encryption_key, ["invalid_field"])
        assert "Invalid field" in str(exc_info.value)

    def test_encrypt_none_field(
        self, crypto_specimen: Specimen, encryption_key: bytes
    ) -> None:
        """Test that None fields are handled gracefully."""
        from wols.crypto import encrypt_specimen_fields

        # crypto_specimen has no batch field (None)
        result = encrypt_specimen_fields(crypto_specimen, encryption_key, ["batch"])
        assert result.id == crypto_specimen.id
