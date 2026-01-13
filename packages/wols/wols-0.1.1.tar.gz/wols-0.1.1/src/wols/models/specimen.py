"""WOLS specimen data models.

Contains Specimen, Strain, and SpecimenRef dataclasses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from wols.constants import WOLS_CONTEXT, WOLS_VERSION
from wols.models.enums import GrowthStage, SpecimenType


@dataclass(frozen=True)
class Strain:
    """Strain/lineage information.

    Attributes:
        name: Strain name (e.g., "Blue Oyster").
        generation: Transfer generation count.
        clonal_generation: Clonal generation count.
        lineage: Parent strain reference.
        source: Origin (lab, wild, vendor).
    """

    name: str
    generation: int | None = None
    clonal_generation: int | None = None
    lineage: str | None = None
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        result: dict[str, Any] = {"name": self.name}
        if self.generation is not None:
            result["generation"] = self.generation
        if self.clonal_generation is not None:
            result["clonalGeneration"] = self.clonal_generation
        if self.lineage is not None:
            result["lineage"] = self.lineage
        if self.source is not None:
            result["source"] = self.source
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Strain:
        """Create from dictionary."""
        return cls(
            name=data["name"],
            generation=data.get("generation"),
            clonal_generation=data.get("clonalGeneration"),
            lineage=data.get("lineage"),
            source=data.get("source"),
        )


@dataclass(frozen=True)
class Specimen:
    """WOLS specimen entity.

    Attributes:
        id: Unique identifier (format: wemush:{cuid}).
        version: WOLS spec version (always "1.1.0").
        type: Specimen type.
        species: Scientific species name.
        strain: Optional genetic info.
        stage: Optional growth stage.
        created: ISO 8601 timestamp.
        batch: Batch identifier.
        organization: Organization name.
        creator: Creator identifier.
        custom: Namespace for custom fields.
        signature: Digital signature.
    """

    id: str
    version: str
    type: SpecimenType
    species: str
    strain: Strain | None = None
    stage: GrowthStage | None = None
    created: datetime | None = None
    batch: str | None = None
    organization: str | None = None
    creator: str | None = None
    custom: dict[str, Any] | None = None
    signature: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary with JSON-LD context."""
        result: dict[str, Any] = {
            "@context": WOLS_CONTEXT,
            "@type": "Specimen",
            "id": self.id,
            "version": self.version,
            "type": self.type.value,
            "species": self.species,
        }

        if self.strain is not None and not isinstance(self.strain, dict):
            result["strain"] = self.strain.to_dict()
        if self.stage is not None:
            result["stage"] = self.stage.value
        if self.created is not None:
            result["created"] = self.created.isoformat()
        if self.batch is not None:
            result["batch"] = self.batch
        if self.organization is not None:
            result["organization"] = self.organization
        if self.creator is not None:
            result["creator"] = self.creator
        if self.custom is not None:
            result["custom"] = self.custom
        if self.signature is not None:
            result["signature"] = self.signature
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Specimen:
        """Create from dictionary."""
        strain_data = data.get("strain")
        strain: Strain | None = None
        if strain_data is not None:
            if isinstance(strain_data, str):
                strain = Strain(name=strain_data)
            else:
                strain = Strain.from_dict(strain_data)

        stage_value = data.get("stage")
        stage: GrowthStage | None = None
        if stage_value is not None:
            stage = GrowthStage(stage_value)

        created_value = data.get("created")
        created: datetime | None = None
        if created_value is not None:
            if isinstance(created_value, datetime):
                created = created_value
            else:
                created = datetime.fromisoformat(created_value.replace("Z", "+00:00"))

        return cls(
            id=data["id"],
            version=data.get("version", WOLS_VERSION),
            type=SpecimenType(data["type"]),
            species=data["species"],
            strain=strain,
            stage=stage,
            created=created,
            batch=data.get("batch"),
            organization=data.get("organization"),
            creator=data.get("creator"),
            custom=data.get("custom"),
            signature=data.get("signature"),
        )


@dataclass(frozen=True)
class SpecimenRef:
    """Lightweight reference from compact URL.

    Attributes:
        id: Specimen ID (without wemush: prefix).
        species_code: Species code from URL (e.g., "PO").
        stage: Stage from URL.
        params: All URL query parameters.
    """

    id: str
    species_code: str | None = None
    stage: GrowthStage | None = None
    params: dict[str, str] = field(default_factory=dict)
