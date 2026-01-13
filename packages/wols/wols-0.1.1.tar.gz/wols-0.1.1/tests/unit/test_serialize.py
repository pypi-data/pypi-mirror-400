"""Tests for wols.core.serialize."""

import json

import pytest

from wols import (
    GrowthStage,
    Specimen,
    SpecimenType,
    UrlScheme,
    WolsValidationError,
    to_compact_url,
    to_json,
)


class TestToJson:
    """Tests for to_json function."""

    def test_json_includes_context(self) -> None:
        """Test that JSON includes JSON-LD context."""
        specimen = Specimen(
            id="wemush:abc123def456ghijklmnopqr",
            version="1.1.0",
            type=SpecimenType.CULTURE,
            species="Test",
        )
        json_str = to_json(specimen)
        data = json.loads(json_str)
        assert data["@context"] == "https://wemush.com/wols/v1"
        assert data["@type"] == "Specimen"

    def test_json_indentation(self) -> None:
        """Test that indent parameter works."""
        specimen = Specimen(
            id="wemush:abc123def456ghijklmnopqr",
            version="1.1.0",
            type=SpecimenType.CULTURE,
            species="Test",
        )
        json_str = to_json(specimen, indent=2)
        assert "\n" in json_str


class TestToCompactUrl:
    """Tests for to_compact_url function."""

    def test_compact_url_default_scheme(self) -> None:
        """Test compact URL uses web+wemush scheme by default (PWA compatible)."""
        specimen = Specimen(
            id="wemush:abc123def456ghijklmnopqr",
            version="1.1.0",
            type=SpecimenType.SUBSTRATE,
            species="Pleurotus ostreatus",
            stage=GrowthStage.COLONIZATION,
        )
        url = to_compact_url(specimen)
        assert url.startswith("web+wemush://v1/")
        assert "abc123def456ghijklmnopqr" in url
        assert "s=PO" in url
        assert "st=COL" in url

    def test_compact_url_wemush_scheme(self) -> None:
        """Test compact URL with native wemush scheme."""
        specimen = Specimen(
            id="wemush:abc123def456ghijklmnopqr",
            version="1.1.0",
            type=SpecimenType.SUBSTRATE,
            species="Pleurotus ostreatus",
            stage=GrowthStage.COLONIZATION,
        )
        url = to_compact_url(specimen, scheme=UrlScheme.WEMUSH)
        assert url.startswith("wemush://v1/")
        assert "abc123def456ghijklmnopqr" in url
        assert "s=PO" in url

    def test_compact_url_web_wemush_scheme(self) -> None:
        """Test compact URL with PWA-compatible web+wemush scheme."""
        specimen = Specimen(
            id="wemush:abc123def456ghijklmnopqr",
            version="1.1.0",
            type=SpecimenType.SUBSTRATE,
            species="Pleurotus ostreatus",
        )
        url = to_compact_url(specimen, scheme=UrlScheme.WEB_WEMUSH)
        assert url.startswith("web+wemush://v1/")
        assert "abc123def456ghijklmnopqr" in url

    def test_compact_url_https_scheme(self) -> None:
        """Test compact URL with HTTPS scheme."""
        specimen = Specimen(
            id="wemush:abc123def456ghijklmnopqr",
            version="1.1.0",
            type=SpecimenType.SUBSTRATE,
            species="Pleurotus ostreatus",
        )
        url = to_compact_url(specimen, scheme=UrlScheme.HTTPS)
        assert url.startswith("https://wemush.com/s/v1/")
        assert "abc123def456ghijklmnopqr" in url

    def test_compact_url_https_custom_base(self) -> None:
        """Test compact URL with custom base URL for HTTPS scheme."""
        specimen = Specimen(
            id="wemush:abc123def456ghijklmnopqr",
            version="1.1.0",
            type=SpecimenType.SUBSTRATE,
            species="Pleurotus ostreatus",
        )
        url = to_compact_url(
            specimen,
            scheme=UrlScheme.HTTPS,
            base_url="https://example.com/specimens",
        )
        assert url.startswith("https://example.com/specimens/v1/")
        assert "abc123def456ghijklmnopqr" in url

    def test_compact_url_scheme_as_string(self) -> None:
        """Test that scheme can be passed as a string."""
        specimen = Specimen(
            id="wemush:abc123def456ghijklmnopqr",
            version="1.1.0",
            type=SpecimenType.SUBSTRATE,
            species="Pleurotus ostreatus",
        )
        url = to_compact_url(specimen, scheme="wemush")
        assert url.startswith("wemush://v1/")

    def test_unknown_species_raises(self) -> None:
        """Test that unknown species raises validation error."""
        specimen = Specimen(
            id="wemush:abc123def456ghijklmnopqr",
            version="1.1.0",
            type=SpecimenType.CULTURE,
            species="Unknown species",
        )
        with pytest.raises(WolsValidationError):
            to_compact_url(specimen)
