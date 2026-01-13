"""Shared pytest fixtures."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from wols import GrowthStage, Specimen, SpecimenType, Strain


@pytest.fixture
def sample_strain() -> Strain:
    """Create a sample Strain for testing."""
    return Strain(
        name="Blue Oyster",
        generation=3,
        source="Wild clone - OR coast",
    )


@pytest.fixture
def sample_specimen(sample_strain: Strain) -> Specimen:
    """Create a sample Specimen for testing."""
    return Specimen(
        id="wemush:clx1abc123def456ghijklmn",
        version="1.1.0",
        type=SpecimenType.SUBSTRATE,
        species="Pleurotus ostreatus",
        strain=sample_strain,
        stage=GrowthStage.COLONIZATION,
        created=datetime(2026, 1, 4, 10, 30, 0, tzinfo=UTC),
        batch="BATCH-2026-001",
    )


@pytest.fixture
def minimal_specimen() -> Specimen:
    """Create a minimal Specimen with only required fields."""
    return Specimen(
        id="wemush:abcdefghij1234567890abcd",
        version="1.1.0",
        type=SpecimenType.CULTURE,
        species="Ganoderma lucidum",
    )


@pytest.fixture
def sample_json() -> str:
    """Create sample JSON-LD string."""
    return """{
    "@context": "https://wemush.com/wols/v1",
    "@type": "Specimen",
    "id": "wemush:clx1abc123def456ghijklmn",
    "version": "1.1.0",
    "type": "SUBSTRATE",
    "species": "Pleurotus ostreatus",
    "strain": {
        "name": "Blue Oyster",
        "generation": 3
    },
    "stage": "COLONIZATION",
    "created": "2026-01-04T10:30:00+00:00"
}"""


@pytest.fixture
def encryption_key() -> bytes:
    """Create a 32-byte encryption key for testing."""
    return b"0123456789abcdef0123456789abcdef"
