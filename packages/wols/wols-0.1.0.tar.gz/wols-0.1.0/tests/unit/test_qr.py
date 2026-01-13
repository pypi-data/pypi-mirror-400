"""Tests for wols.qr module."""

import pytest

from wols import Specimen, SpecimenRef, SpecimenType

# Check if pyzbar/zbar is available for scanning tests
try:
    from pyzbar import pyzbar  # noqa: F401

    PYZBAR_AVAILABLE = True
except (ImportError, OSError):
    PYZBAR_AVAILABLE = False


@pytest.fixture
def qr_specimen() -> Specimen:
    """Specimen for QR tests."""
    return Specimen(
        id="wemush:abc123def456ghijklmnopqr",
        version="1.1.0",
        type=SpecimenType.SUBSTRATE,
        species="Pleurotus ostreatus",
    )


class TestGenerateQrPng:
    """Tests for generate_qr_png function."""

    def test_generates_png_bytes(self, qr_specimen: Specimen) -> None:
        """Test that PNG bytes are generated."""
        from wols.qr import generate_qr_png

        result = generate_qr_png(qr_specimen)
        assert isinstance(result, bytes)
        assert len(result) > 0
        # PNG magic bytes
        assert result[:8] == b"\x89PNG\r\n\x1a\n"

    def test_embedded_format(self, qr_specimen: Specimen) -> None:
        """Test embedded format generates valid QR."""
        from wols.qr import generate_qr_png

        result = generate_qr_png(qr_specimen, format_type="embedded")
        assert len(result) > 100

    def test_compact_format(self, qr_specimen: Specimen) -> None:
        """Test compact format generates smaller QR."""
        from wols.qr import generate_qr_png

        result = generate_qr_png(qr_specimen, format_type="compact")
        assert len(result) > 0

    def test_with_logo(self, qr_specimen: Specimen) -> None:
        """Test QR with logo watermark."""
        from wols.qr import generate_qr_png

        with_logo = generate_qr_png(qr_specimen, with_logo=True)
        without_logo = generate_qr_png(qr_specimen, with_logo=False)

        # Both should be valid PNGs
        assert with_logo[:8] == b"\x89PNG\r\n\x1a\n"
        assert without_logo[:8] == b"\x89PNG\r\n\x1a\n"

        # Logo version should be larger (more image data)
        assert len(with_logo) > len(without_logo)


class TestGenerateQrSvg:
    """Tests for generate_qr_svg function."""

    def test_generates_svg_string(self, qr_specimen: Specimen) -> None:
        """Test that SVG string is generated."""
        from wols.qr import generate_qr_svg

        result = generate_qr_svg(qr_specimen)
        assert isinstance(result, str)
        assert "<svg" in result or "<?xml" in result


class TestGenerateQrBase64:
    """Tests for generate_qr_base64 function."""

    def test_generates_data_url(self, qr_specimen: Specimen) -> None:
        """Test that base64 data URL is generated."""
        from wols.qr import generate_qr_base64

        result = generate_qr_base64(qr_specimen)
        assert isinstance(result, str)
        assert result.startswith("data:image/png;base64,")


@pytest.mark.skipif(not PYZBAR_AVAILABLE, reason="pyzbar/zbar library not installed")
class TestScanQr:
    """Tests for scan_qr function."""

    def test_scan_embedded_qr(self, qr_specimen: Specimen) -> None:
        """Test scanning QR with embedded JSON."""
        from wols.qr import generate_qr_png, scan_qr

        png_bytes = generate_qr_png(
            qr_specimen, format_type="embedded", with_logo=False
        )
        result = scan_qr(png_bytes)

        assert isinstance(result, Specimen)
        assert result.id == qr_specimen.id
        assert result.type == qr_specimen.type

    def test_scan_compact_qr(self, qr_specimen: Specimen) -> None:
        """Test scanning QR with compact URL."""
        from wols.qr import generate_qr_png, scan_qr

        png_bytes = generate_qr_png(qr_specimen, format_type="compact", with_logo=False)
        result = scan_qr(png_bytes)

        assert isinstance(result, SpecimenRef)
        assert "abc123def456ghijklmnopqr" in result.id
