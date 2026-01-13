"""Tests for wols.core.parse."""

import pytest

from wols import (
    GrowthStage,
    Specimen,
    SpecimenRef,
    SpecimenType,
    WolsParseError,
    parse_compact_url,
    parse_specimen,
)


class TestParseSpecimen:
    """Tests for parse_specimen function."""

    def test_parse_valid_json(self) -> None:
        """Test parsing valid JSON-LD."""
        json_str = """{
            "@context": "https://wemush.com/wols/v1",
            "@type": "Specimen",
            "id": "wemush:clx1abc123def456ghijklmn",
            "version": "1.1.0",
            "type": "SUBSTRATE",
            "species": "Pleurotus ostreatus"
        }"""
        specimen = parse_specimen(json_str)
        assert isinstance(specimen, Specimen)
        assert specimen.id == "wemush:clx1abc123def456ghijklmn"
        assert specimen.type == SpecimenType.SUBSTRATE

    def test_parse_with_strain(self) -> None:
        """Test parsing JSON with strain object."""
        json_str = """{
            "id": "wemush:abc123def456ghijklmnopqr",
            "type": "CULTURE",
            "species": "Pleurotus ostreatus",
            "strain": {"name": "Blue Oyster", "generation": 3}
        }"""
        specimen = parse_specimen(json_str)
        assert specimen.strain is not None
        assert specimen.strain.name == "Blue Oyster"
        assert specimen.strain.generation == 3

    def test_invalid_json_raises(self) -> None:
        """Test that invalid JSON raises parse error."""
        with pytest.raises(WolsParseError) as exc_info:
            parse_specimen("{invalid json}")
        assert "INVALID_JSON" in str(exc_info.value)

    def test_missing_required_field_raises(self) -> None:
        """Test that missing required field raises parse error."""
        with pytest.raises(WolsParseError) as exc_info:
            parse_specimen('{"id": "wemush:abc123"}')
        assert "REQUIRED_FIELD" in str(exc_info.value)


class TestParseCompactUrl:
    """Tests for parse_compact_url function."""

    def test_parse_wemush_url(self) -> None:
        """Test parsing native wemush:// URL."""
        ref = parse_compact_url("wemush://v1/abc123?s=PO&st=COL")
        assert isinstance(ref, SpecimenRef)
        assert ref.id == "abc123"
        assert ref.species_code == "PO"
        assert ref.stage == GrowthStage.COLONIZATION

    def test_parse_web_wemush_url(self) -> None:
        """Test parsing PWA-compatible web+wemush:// URL."""
        ref = parse_compact_url("web+wemush://v1/abc123?s=PO&st=COL")
        assert isinstance(ref, SpecimenRef)
        assert ref.id == "abc123"
        assert ref.species_code == "PO"
        assert ref.stage == GrowthStage.COLONIZATION

    def test_parse_https_url(self) -> None:
        """Test parsing HTTPS URL."""
        ref = parse_compact_url("https://wemush.com/s/v1/abc123?s=PO&st=COL")
        assert isinstance(ref, SpecimenRef)
        assert ref.id == "abc123"
        assert ref.species_code == "PO"
        assert ref.stage == GrowthStage.COLONIZATION

    def test_parse_https_url_custom_base(self) -> None:
        """Test parsing HTTPS URL with custom base path."""
        ref = parse_compact_url("https://example.com/specimens/v1/abc123?s=HE")
        assert ref.id == "abc123"
        assert ref.species_code == "HE"

    def test_parse_url_without_query(self) -> None:
        """Test parsing URL without query parameters."""
        ref = parse_compact_url("wemush://v1/abc123def456")
        assert ref.id == "abc123def456"
        assert ref.species_code is None

    def test_parse_web_wemush_url_without_query(self) -> None:
        """Test parsing web+wemush URL without query parameters."""
        ref = parse_compact_url("web+wemush://v1/abc123def456")
        assert ref.id == "abc123def456"
        assert ref.species_code is None

    def test_invalid_scheme_raises(self) -> None:
        """Test that invalid scheme raises parse error."""
        with pytest.raises(WolsParseError) as exc_info:
            parse_compact_url("http://v1/abc123")
        assert "INVALID_SCHEME" in str(exc_info.value)

    def test_missing_version_raises(self) -> None:
        """Test that missing v1 marker raises parse error."""
        with pytest.raises(WolsParseError) as exc_info:
            parse_compact_url("wemush://abc123")
        assert "INVALID_PATH" in str(exc_info.value)
