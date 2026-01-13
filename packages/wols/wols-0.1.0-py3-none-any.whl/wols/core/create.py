"""Specimen creation functionality."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from cuid2 import cuid_wrapper

from wols.constants import ID_PREFIX, WOLS_VERSION
from wols.exceptions import WolsValidationError
from wols.models.enums import GrowthStage, SpecimenType
from wols.models.specimen import Specimen, Strain
from wols.models.validation import ValidationError

# Configure CUID generator
_cuid = cuid_wrapper()


def create_specimen(
    *,
    input_type: SpecimenType | str,
    species: str,
    strain: Strain | str | None = None,
    stage: GrowthStage | str | None = None,
    batch: str | None = None,
    organization: str | None = None,
    creator: str | None = None,
    custom: dict[str, Any] | None = None,
    created: datetime | None = None,
) -> Specimen:
    """Create a new specimen with auto-generated CUID.

    Args:
        input_type: Specimen type (CULTURE, SPAWN, SUBSTRATE, FRUITING,
            HARVEST).
        species: Scientific species name.
        strain: Strain information (string shorthand or Strain object).
        stage: Current growth stage.
        batch: Batch identifier.
        organization: Organization name.
        creator: Creator identifier.
        custom: Custom namespace fields.
        created: Creation timestamp (defaults to current time).

    Returns:
        A new Specimen instance with generated ID.

    Raises:
        WolsValidationError: If required fields are invalid.

    Example:
        >>> specimen = create_specimen(
        ...     input_type=SpecimenType.SUBSTRATE,
        ...     species="Pleurotus ostreatus",
        ...     strain="Blue Oyster",
        ...     stage=GrowthStage.COLONIZATION,
        ... )
        >>> print(specimen.id)
        'wemush:clx1abc123def456'
    """
    errors: list[ValidationError] = []

    # Validate and convert type
    specimen_type: SpecimenType
    if isinstance(input_type, str):
        try:
            specimen_type = SpecimenType(input_type)
        except ValueError:
            valid_types = ", ".join(t.value for t in SpecimenType)
            errors.append(
                ValidationError(
                    path="type",
                    code="INVALID_VALUE",
                    message=f"Invalid specimen type '{input_type}'."
                    f" Valid types: {valid_types}",
                )
            )
            # Placeholder for type checking
            specimen_type = SpecimenType.CULTURE
    else:
        specimen_type = input_type

    # Validate species
    if not species or not species.strip():
        errors.append(
            ValidationError(
                path="species",
                code="REQUIRED_FIELD",
                message="Species is required and cannot be empty",
            )
        )

    # Convert strain if string
    strain_obj: Strain | None = None
    if strain is not None:
        if isinstance(strain, str):
            if strain.strip():
                strain_obj = Strain(name=strain)
            else:
                errors.append(
                    ValidationError(
                        path="strain",
                        code="INVALID_VALUE",
                        message="Strain name cannot be empty",
                    )
                )
        else:
            strain_obj = strain

    # Validate and convert stage
    growth_stage: GrowthStage | None = None
    if stage is not None:
        if isinstance(stage, str):
            try:
                growth_stage = GrowthStage(stage)
            except ValueError:
                valid_stages = ", ".join(s.value for s in GrowthStage)
                errors.append(
                    ValidationError(
                        path="stage",
                        code="INVALID_VALUE",
                        message=f"Invalid growth stage '{stage}'."
                        f" Valid stages: {valid_stages}",
                    )
                )
        else:
            growth_stage = stage

    # Validate optional string fields
    if batch is not None and not batch.strip():
        errors.append(
            ValidationError(
                path="batch",
                code="INVALID_VALUE",
                message="Batch cannot be empty if provided",
            )
        )

    if organization is not None and not organization.strip():
        errors.append(
            ValidationError(
                path="organization",
                code="INVALID_VALUE",
                message="Organization cannot be empty if provided",
            )
        )

    if creator is not None and not creator.strip():
        errors.append(
            ValidationError(
                path="creator",
                code="INVALID_VALUE",
                message="Creator cannot be empty if provided",
            )
        )

    # Raise if validation errors
    if errors:
        raise WolsValidationError(
            message=f"Failed to create specimen: {len(errors)} validation error(s)",
            errors=errors,
        )

    # Generate ID and timestamp
    specimen_id = f"{ID_PREFIX}:{_cuid()}"
    creation_time = created if created is not None else datetime.now(UTC)

    return Specimen(
        id=specimen_id,
        version=WOLS_VERSION,
        type=specimen_type,
        species=species,
        strain=strain_obj,
        stage=growth_stage,
        created=creation_time,
        batch=batch,
        organization=organization,
        creator=creator,
        custom=custom,
    )
