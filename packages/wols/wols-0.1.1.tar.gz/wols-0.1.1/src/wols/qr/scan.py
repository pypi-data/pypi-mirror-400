"""QR code scanning functionality."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from wols.core.parse import parse_compact_url, parse_specimen
from wols.exceptions import WolsParseError

if TYPE_CHECKING:
    from wols.models.specimen import Specimen, SpecimenRef


def scan_qr(
    image: bytes | str | Path,
) -> Specimen | SpecimenRef:
    """Scan a QR code image and extract specimen data.

    Args:
        image: PNG/JPEG bytes, file path, or Path object.

    Returns:
        Specimen (if embedded format) or SpecimenRef (if compact URL).

    Raises:
        WolsParseError: If QR code cannot be decoded or contains invalid data.
        ImportError: If pyzbar/pillow not installed.

    Example:
        >>> result = scan_qr("label.png")
        >>> if isinstance(result, Specimen):
        ...     print(f"Full specimen: {result.species}")
        >>> else:
        ...     print(f"Reference: {result.id}")
    """
    try:
        from PIL import Image
        from pyzbar import pyzbar  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError(
            "QR scanning module not installed. Install with: pip install wols\\[qr]"
        ) from e

    # Load image
    if isinstance(image, bytes):
        import io

        img = Image.open(io.BytesIO(image))
    elif isinstance(image, (str, Path)):
        try:
            img = Image.open(image)
        except FileNotFoundError as e:
            raise WolsParseError(
                message=f"Image file not found: {image}",
                code="FILE_NOT_FOUND",
            ) from e
        except Exception as e:
            raise WolsParseError(
                message=f"Failed to open image: {e}",
                code="IMAGE_ERROR",
            ) from e
    else:
        raise WolsParseError(
            message=f"Invalid image type: {type(image).__name__}",
            code="INVALID_TYPE",
        )

    # Decode QR codes
    decoded = pyzbar.decode(img)

    if not decoded:
        raise WolsParseError(
            message="No QR code found in image",
            code="NO_QR_FOUND",
        )

    # Get the first QR code's data
    qr_data = decoded[0].data.decode("utf-8")

    # Determine format and parse
    # Check for all valid URL schemes: wemush://, web+wemush://, https://
    if (
        qr_data.startswith("wemush://")
        or qr_data.startswith("web+wemush://")
        or qr_data.startswith("https://")
    ):
        # Compact URL format
        return parse_compact_url(qr_data)
    elif qr_data.startswith("{"):
        # JSON format
        return parse_specimen(qr_data)
    else:
        raise WolsParseError(
            message=f"Unknown QR data format: {qr_data[:50]}...",
            code="INVALID_FORMAT",
            input=qr_data,
        )
