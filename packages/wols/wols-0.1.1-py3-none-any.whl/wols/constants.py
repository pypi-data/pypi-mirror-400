"""WOLS constants and configuration values.

Contains species codes, stage codes, and JSON-LD context definitions.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

# WOLS specification version
WOLS_VERSION = "1.1.0"

# JSON-LD context URL
WOLS_CONTEXT = "https://wemush.com/wols/v1"

# ID prefix for specimen identifiers
ID_PREFIX = "wemush"


class UrlScheme(str, Enum):
    """URL scheme options for compact URLs.

    Attributes:
        WEMUSH: Native app scheme (wemush://) - for native mobile apps.
        WEB_WEMUSH: PWA-compatible scheme (web+wemush://) - for Progressive Web Apps.
        HTTPS: Universal web scheme - works everywhere, requires backend.
    """

    WEMUSH = "wemush"
    WEB_WEMUSH = "web+wemush"
    HTTPS = "https"


# Type alias for URL scheme literals
UrlSchemeLiteral = Literal["wemush", "web+wemush", "https"]

# Default URL scheme
DEFAULT_URL_SCHEME: UrlScheme = UrlScheme.WEB_WEMUSH

# Default base URL for HTTPS scheme (can be overridden)
DEFAULT_HTTPS_BASE_URL = "https://wemush.com/s"

# All valid URL schemes for parsing (we accept any of these)
VALID_URL_SCHEMES = frozenset({"wemush", "web+wemush", "https"})

# Species codes for compact URL format
# Maps 2-letter codes to full scientific names
SPECIES_CODES: dict[str, str] = {
    "PO": "Pleurotus ostreatus",
    "PE": "Pleurotus eryngii",
    "PC": "Pleurotus citrinopileatus",
    "PP": "Pleurotus pulmonarius",
    "GL": "Ganoderma lucidum",
    "GA": "Ganoderma applanatum",
    "LE": "Lentinula edodes",
    "HE": "Hericium erinaceus",
    "HC": "Hericium coralloides",
    "FL": "Flammulina velutipes",
    "AB": "Agaricus bisporus",
    "AA": "Agaricus arvensis",
    "PS": "Psilocybe cubensis",
    "CA": "Cordyceps militaris",
    "TA": "Trametes versicolor",
    "GF": "Grifola frondosa",
    "LP": "Laetiporus sulphureus",
    "CM": "Cyclocybe aegerita",
    "ST": "Stropharia rugosoannulata",
    "PH": "Pholiota nameko",
    "HY": "Hypsizygus tessellatus",
    "CO": "Coprinus comatus",
    "AM": "Armillaria mellea",
    "MO": "Morchella esculenta",
}

# Reverse mapping: scientific name to code
SPECIES_NAMES: dict[str, str] = {v: k for k, v in SPECIES_CODES.items()}

# Stage codes for compact URL format
STAGE_CODES: dict[str, str] = {
    "INO": "INOCULATION",
    "COL": "COLONIZATION",
    "FRU": "FRUITING",
    "HAR": "HARVEST",
}

# Reverse mapping: stage name to code
STAGE_NAMES: dict[str, str] = {v: k for k, v in STAGE_CODES.items()}
