"""WOLS enumeration types.

Contains SpecimenType and GrowthStage enums per WOLS v1.1.0.
"""

from enum import Enum


class SpecimenType(str, Enum):
    """Valid specimen types per WOLS v1.1.0.

    Represents the physical form of the specimen in the cultivation lifecycle.
    """

    CULTURE = "CULTURE"
    """Pure culture (agar, liquid)."""

    SPAWN = "SPAWN"
    """Colonized grain/substrate for inoculation."""

    SUBSTRATE = "SUBSTRATE"
    """Bulk substrate (straw, sawdust, etc.)."""

    FRUITING = "FRUITING"
    """Fruiting container/block."""

    HARVEST = "HARVEST"
    """Harvested mushrooms."""


class GrowthStage(str, Enum):
    """Valid growth stages per WOLS v1.1.0.

    Represents the current stage in the growth lifecycle.
    """

    INOCULATION = "INOCULATION"
    """Just inoculated."""

    COLONIZATION = "COLONIZATION"
    """Mycelium spreading."""

    FRUITING = "FRUITING"
    """Pinning/fruiting initiated."""

    HARVEST = "HARVEST"
    """Ready for or post-harvest."""
