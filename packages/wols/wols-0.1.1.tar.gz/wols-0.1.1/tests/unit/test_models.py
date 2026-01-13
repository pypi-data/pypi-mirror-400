"""Tests for wols models."""

import pytest

from wols import (
    GrowthStage,
    Specimen,
    SpecimenRef,
    SpecimenType,
    Strain,
    ValidationError,
    ValidationResult,
)


class TestSpecimenType:
    """Tests for SpecimenType enum."""

    def test_all_types_exist(self) -> None:
        """Verify all specimen types are defined."""
        assert SpecimenType.CULTURE == "CULTURE"
        assert SpecimenType.SPAWN == "SPAWN"
        assert SpecimenType.SUBSTRATE == "SUBSTRATE"
        assert SpecimenType.FRUITING == "FRUITING"
        assert SpecimenType.HARVEST == "HARVEST"

    def test_type_count(self) -> None:
        """Verify correct number of types."""
        assert len(SpecimenType) == 5

    def test_from_string(self) -> None:
        """Test creating type from string value."""
        assert SpecimenType("CULTURE") == SpecimenType.CULTURE

    def test_invalid_type_raises(self) -> None:
        """Test that invalid types raise ValueError."""
        with pytest.raises(ValueError):
            SpecimenType("INVALID")


class TestGrowthStage:
    """Tests for GrowthStage enum."""

    def test_all_stages_exist(self) -> None:
        """Verify all growth stages are defined."""
        assert GrowthStage.INOCULATION == "INOCULATION"
        assert GrowthStage.COLONIZATION == "COLONIZATION"
        assert GrowthStage.FRUITING == "FRUITING"
        assert GrowthStage.HARVEST == "HARVEST"

    def test_stage_count(self) -> None:
        """Verify correct number of stages."""
        assert len(GrowthStage) == 4

    def test_invalid_stage_raises(self) -> None:
        """Test that invalid stages raise ValueError."""
        with pytest.raises(ValueError):
            GrowthStage("INVALID")


class TestStrain:
    """Tests for Strain dataclass."""

    def test_minimal_strain(self) -> None:
        """Test creating strain with only required fields."""
        strain = Strain(name="Blue Oyster")
        assert strain.name == "Blue Oyster"
        assert strain.generation is None

    def test_full_strain(self) -> None:
        """Test creating strain with all fields."""
        strain = Strain(
            name="Blue Oyster",
            generation=3,
            clonal_generation=1,
            source="Wild clone",
        )
        assert strain.generation == 3
        assert strain.clonal_generation == 1

    def test_to_dict(self) -> None:
        """Test to_dict conversion."""
        strain = Strain(name="Blue Oyster", generation=3)
        result = strain.to_dict()
        assert result["name"] == "Blue Oyster"
        assert result["generation"] == 3

    def test_from_dict(self) -> None:
        """Test creating strain from dict."""
        data = {"name": "Blue Oyster", "generation": 3}
        strain = Strain.from_dict(data)
        assert strain.name == "Blue Oyster"
        assert strain.generation == 3


class TestSpecimen:
    """Tests for Specimen dataclass."""

    def test_minimal_specimen(self) -> None:
        """Test creating specimen with only required fields."""
        specimen = Specimen(
            id="wemush:abc123def456ghijklmnopqr",
            version="1.1.0",
            type=SpecimenType.CULTURE,
            species="Pleurotus ostreatus",
        )
        assert specimen.id == "wemush:abc123def456ghijklmnopqr"
        assert specimen.version == "1.1.0"
        assert specimen.type == SpecimenType.CULTURE
        assert specimen.species == "Pleurotus ostreatus"

    def test_to_dict_includes_context(self) -> None:
        """Test that to_dict includes JSON-LD context."""
        specimen = Specimen(
            id="wemush:abc123def456ghijklmnopqr",
            version="1.1.0",
            type=SpecimenType.CULTURE,
            species="Test",
        )
        result = specimen.to_dict()
        assert result["@context"] == "https://wemush.com/wols/v1"
        assert result["@type"] == "Specimen"

    def test_from_dict(self) -> None:
        """Test creating specimen from dict."""
        data = {
            "id": "wemush:abc123def456ghijklmnopqr",
            "type": "SUBSTRATE",
            "species": "Pleurotus ostreatus",
            "strain": {"name": "Blue Oyster"},
        }
        specimen = Specimen.from_dict(data)
        assert specimen.type == SpecimenType.SUBSTRATE
        assert specimen.strain is not None
        assert specimen.strain.name == "Blue Oyster"


class TestSpecimenRef:
    """Tests for SpecimenRef dataclass."""

    def test_minimal_ref(self) -> None:
        """Test creating minimal SpecimenRef."""
        ref = SpecimenRef(id="abc123")
        assert ref.id == "abc123"
        assert ref.species_code is None

    def test_full_ref(self) -> None:
        """Test creating full SpecimenRef."""
        ref = SpecimenRef(
            id="abc123",
            species_code="PO",
            stage=GrowthStage.COLONIZATION,
            params={"s": "PO"},
        )
        assert ref.species_code == "PO"
        assert ref.stage == GrowthStage.COLONIZATION


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_valid_result(self) -> None:
        """Test creating a valid result."""
        result = ValidationResult(valid=True)
        assert result.valid is True
        assert bool(result) is True

    def test_invalid_result(self) -> None:
        """Test creating an invalid result."""
        errors = [ValidationError(path="type", code="REQUIRED", message="Required")]
        result = ValidationResult(valid=False, errors=errors)
        assert result.valid is False
        assert len(result.errors) == 1
