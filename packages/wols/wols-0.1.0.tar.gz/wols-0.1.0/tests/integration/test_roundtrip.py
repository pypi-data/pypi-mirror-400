"""Integration tests for full round-trip operations."""

import pytest

from wols import (
    GrowthStage,
    Specimen,
    SpecimenRef,
    SpecimenType,
    Strain,
    create_specimen,
    parse_compact_url,
    parse_specimen,
    to_compact_url,
    to_json,
    validate_specimen,
)

# Check if pyzbar/zbar is available for scanning tests
try:
    from pyzbar import pyzbar  # noqa: F401

    PYZBAR_AVAILABLE = True
except (ImportError, OSError):
    PYZBAR_AVAILABLE = False


class TestJsonRoundTrip:
    """Test JSON serialization round-trip."""

    def test_full_specimen_roundtrip(self) -> None:
        """Test creating, serializing, and parsing a full specimen."""
        # Create
        original = create_specimen(
            input_type=SpecimenType.SUBSTRATE,
            species="Pleurotus ostreatus",
            strain=Strain(
                name="Blue Oyster",
                generation=3,
                source="Wild clone",
            ),
            stage=GrowthStage.COLONIZATION,
            batch="BATCH-2026-001",
            organization="WeMush",
            custom={"temp": 72, "humidity": 85},
        )

        # Serialize
        json_str = to_json(original)

        # Parse
        parsed = parse_specimen(json_str)

        # Verify
        assert parsed.id == original.id
        assert parsed.type == original.type
        assert parsed.species == original.species
        assert parsed.strain is not None
        assert parsed.strain.name == original.strain.name  # type: ignore[union-attr]
        assert parsed.strain.generation == original.strain.generation  # type: ignore[union-attr]
        assert parsed.stage == original.stage
        assert parsed.batch == original.batch

        # Validate
        result = validate_specimen(parsed)
        assert result.valid

    def test_minimal_specimen_roundtrip(self) -> None:
        """Test minimal specimen round-trip."""
        original = create_specimen(
            input_type=SpecimenType.CULTURE,
            species="Ganoderma lucidum",
        )

        json_str = to_json(original)
        parsed = parse_specimen(json_str)

        assert parsed.id == original.id
        assert parsed.type == original.type
        assert parsed.species == original.species


class TestCompactUrlRoundTrip:
    """Test compact URL round-trip."""

    def test_compact_url_roundtrip(self) -> None:
        """Test creating specimen and parsing its compact URL."""
        original = create_specimen(
            input_type=SpecimenType.SUBSTRATE,
            species="Pleurotus ostreatus",
            stage=GrowthStage.COLONIZATION,
        )

        # Generate compact URL
        url = to_compact_url(original)

        # Parse it back
        ref = parse_compact_url(url)

        # Verify reference contains expected data
        assert isinstance(ref, SpecimenRef)
        assert original.id.endswith(ref.id)
        assert ref.species_code == "PO"
        assert ref.stage == GrowthStage.COLONIZATION


@pytest.mark.skipif(not PYZBAR_AVAILABLE, reason="pyzbar/zbar library not installed")
class TestQrRoundTrip:
    """Test QR code round-trip."""

    @pytest.mark.integration
    def test_qr_embedded_roundtrip(self) -> None:
        """Test QR generation and scanning with embedded format."""
        from wols.qr import generate_qr_png, scan_qr

        original = create_specimen(
            input_type=SpecimenType.CULTURE,
            species="Pleurotus ostreatus",
            strain="Blue Oyster",
        )

        # Generate QR
        qr_bytes = generate_qr_png(original, format="embedded")

        # Scan it back
        scanned = scan_qr(qr_bytes)

        assert isinstance(scanned, Specimen)
        assert scanned.id == original.id
        assert scanned.species == original.species

    @pytest.mark.integration
    def test_qr_compact_roundtrip(self) -> None:
        """Test QR generation and scanning with compact format."""
        from wols.qr import generate_qr_png, scan_qr

        original = create_specimen(
            input_type=SpecimenType.SUBSTRATE,
            species="Pleurotus ostreatus",
            stage=GrowthStage.FRUITING,
        )

        # Generate compact QR
        qr_bytes = generate_qr_png(original, format="compact")

        # Scan it back
        scanned = scan_qr(qr_bytes)

        assert isinstance(scanned, SpecimenRef)
        assert original.id.endswith(scanned.id)
        assert scanned.species_code == "PO"


class TestCryptoRoundTrip:
    """Test encryption round-trip."""

    @pytest.mark.integration
    def test_encryption_roundtrip(self) -> None:
        """Test encrypting and decrypting a specimen."""
        import os

        from wols.crypto import decrypt_specimen, encrypt_specimen

        original = create_specimen(
            input_type=SpecimenType.CULTURE,
            species="Pleurotus ostreatus",
            strain="Blue Oyster",
            custom={"secret": "data"},
        )

        key = os.urandom(32)

        # Encrypt
        encrypted = encrypt_specimen(original, key)
        assert isinstance(encrypted, str)

        # Decrypt
        decrypted = decrypt_specimen(encrypted, key)

        assert decrypted.id == original.id
        assert decrypted.species == original.species
        assert decrypted.custom == original.custom
