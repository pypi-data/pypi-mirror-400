"""Tests for wols.core.create."""

import pytest

from wols import (
    GrowthStage,
    Specimen,
    SpecimenType,
    Strain,
    WolsValidationError,
    create_specimen,
)


class TestCreateSpecimen:
    """Tests for create_specimen function."""

    def test_minimal_creation(self) -> None:
        """Test creating specimen with minimal required fields."""
        specimen = create_specimen(
            input_type=SpecimenType.CULTURE,
            species="Pleurotus ostreatus",
        )
        assert isinstance(specimen, Specimen)
        assert specimen.id.startswith("wemush:")
        assert specimen.version == "1.1.0"
        assert specimen.type == SpecimenType.CULTURE
        assert specimen.species == "Pleurotus ostreatus"
        assert specimen.created is not None

    def test_full_creation(self) -> None:
        """Test creating specimen with all fields."""
        strain = Strain(name="Blue Oyster", generation=3)
        specimen = create_specimen(
            input_type=SpecimenType.SUBSTRATE,
            species="Pleurotus ostreatus",
            strain=strain,
            stage=GrowthStage.COLONIZATION,
            batch="BATCH-001",
            organization="WeMush",
            custom={"temp": 72},
        )
        assert specimen.type == SpecimenType.SUBSTRATE
        assert specimen.strain is not None
        assert specimen.strain.name == "Blue Oyster"
        assert specimen.batch == "BATCH-001"

    def test_string_type_conversion(self) -> None:
        """Test that string type is converted to enum."""
        specimen = create_specimen(
            input_type="SUBSTRATE",
            species="Pleurotus ostreatus",
        )
        assert specimen.type == SpecimenType.SUBSTRATE

    def test_string_strain_expansion(self) -> None:
        """Test that string strain is expanded to Strain object."""
        specimen = create_specimen(
            input_type=SpecimenType.CULTURE,
            species="Pleurotus ostreatus",
            strain="Blue Oyster",
        )
        assert specimen.strain is not None
        assert specimen.strain.name == "Blue Oyster"

    def test_unique_ids(self) -> None:
        """Test that each specimen gets a unique ID."""
        ids = set()
        for _ in range(10):
            specimen = create_specimen(
                input_type=SpecimenType.CULTURE,
                species="Test",
            )
            ids.add(specimen.id)
        assert len(ids) == 10

    def test_invalid_type_raises(self) -> None:
        """Test that invalid type raises validation error."""
        with pytest.raises(WolsValidationError) as exc_info:
            create_specimen(
                input_type="INVALID",
                species="Pleurotus ostreatus",
            )
        assert "VALIDATION_ERROR" in str(exc_info.value)
        assert "INVALID" in str(exc_info.value)

    def test_empty_species_raises(self) -> None:
        """Test that empty species raises validation error."""
        with pytest.raises(WolsValidationError) as exc_info:
            create_specimen(
                input_type=SpecimenType.CULTURE,
                species="",
            )
        assert "VALIDATION_ERROR" in str(exc_info.value)
        assert "species" in str(exc_info.value).lower()
