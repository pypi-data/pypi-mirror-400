"""WOLS - WeMush Open Labeling Standard.

Python implementation of the WOLS v1.1.0 specification for specimen tracking.

Example:
    >>> from wols import create_specimen, SpecimenType, to_json
    >>> specimen = create_specimen(
    ...     type=SpecimenType.SUBSTRATE,
    ...     species="Pleurotus ostreatus",
    ... )
    >>> print(to_json(specimen, indent=2))
"""

from wols.constants import (
    DEFAULT_HTTPS_BASE_URL,
    DEFAULT_URL_SCHEME,
    WOLS_CONTEXT,
    WOLS_VERSION,
    UrlScheme,
)
from wols.core.create import create_specimen
from wols.core.parse import parse_compact_url, parse_specimen
from wols.core.serialize import to_compact_url, to_json
from wols.core.validate import validate_specimen
from wols.exceptions import (
    WolsEncryptionError,
    WolsError,
    WolsParseError,
    WolsValidationError,
)
from wols.models.enums import GrowthStage, SpecimenType
from wols.models.specimen import Specimen, SpecimenRef, Strain
from wols.models.validation import ValidationError, ValidationResult

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_HTTPS_BASE_URL",
    "DEFAULT_URL_SCHEME",
    "WOLS_CONTEXT",
    "WOLS_VERSION",
    "GrowthStage",
    "Specimen",
    "SpecimenRef",
    "SpecimenType",
    "Strain",
    "UrlScheme",
    "ValidationError",
    "ValidationResult",
    "WolsEncryptionError",
    "WolsError",
    "WolsParseError",
    "WolsValidationError",
    "__version__",
    "create_specimen",
    "parse_compact_url",
    "parse_specimen",
    "to_compact_url",
    "to_json",
    "validate_specimen",
]
