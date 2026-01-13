"""QR code generation functionality."""

from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from wols.constants import DEFAULT_URL_SCHEME, UrlScheme
from wols.core.serialize import to_compact_url, to_json

if TYPE_CHECKING:
    from PIL import Image

    from wols.models.specimen import Specimen

# Path to the embedded logo
LOGO_PATH = Path(__file__).parent.parent / "logo.png"

# Error correction level mapping
ERROR_CORRECTION_MAP = {
    "L": 1,  # qrcode.constants.ERROR_CORRECT_L
    "M": 0,  # qrcode.constants.ERROR_CORRECT_M
    "Q": 3,  # qrcode.constants.ERROR_CORRECT_Q
    "H": 2,  # qrcode.constants.ERROR_CORRECT_H
}

# Logo covers ~25% of QR code area for good balance of visibility and scannability
LOGO_SIZE_RATIO = 0.25


def _add_logo_watermark(
    qr_image: Image.Image, logo_ratio: float = LOGO_SIZE_RATIO
) -> Image.Image:
    """Add the wols logo watermark to the center of a QR code image.

    Args:
        qr_image: The QR code PIL Image.
        logo_ratio: Ratio of logo size to QR code size (default 0.25).

    Returns:
        QR code image with logo overlay.
    """
    from PIL import Image as PILImage

    if not LOGO_PATH.exists():
        return qr_image

    # Open and prepare logo
    logo = PILImage.open(LOGO_PATH)

    # Calculate logo size (as ratio of QR code size)
    qr_width, qr_height = qr_image.size
    logo_size = int(min(qr_width, qr_height) * logo_ratio)

    # Resize logo maintaining aspect ratio
    logo.thumbnail((logo_size, logo_size), PILImage.Resampling.LANCZOS)

    # Calculate position to center logo
    logo_width, logo_height = logo.size
    pos_x = (qr_width - logo_width) // 2
    pos_y = (qr_height - logo_height) // 2

    # Create a copy to avoid modifying original
    result = qr_image.copy()

    # Convert to RGBA if needed for transparency support
    if result.mode != "RGBA":
        result = result.convert("RGBA")

    # Handle logo with transparency
    if logo.mode == "RGBA":
        result.paste(logo, (pos_x, pos_y), logo)
    else:
        result.paste(logo, (pos_x, pos_y))

    # Convert back to RGB for PNG output
    return result.convert("RGB")


def _get_qr_data(
    specimen: Specimen,
    format_type: Literal["embedded", "compact"],
    scheme: UrlScheme | str = DEFAULT_URL_SCHEME,
    base_url: str | None = None,
) -> str:
    """Get the data to encode in the QR code."""
    if format_type == "compact":
        return to_compact_url(specimen, scheme=scheme, base_url=base_url)
    else:
        return to_json(specimen)


def generate_qr_png(
    specimen: Specimen,
    *,
    format_type: Literal["embedded", "compact"] = "embedded",
    size: int = 300,
    error_correction: Literal["L", "M", "Q", "H"] = "M",
    with_logo: bool = True,
    scheme: UrlScheme | str = DEFAULT_URL_SCHEME,
    base_url: str | None = None,
) -> bytes:
    """Generate a QR code as PNG bytes.

    Args:
        specimen: Specimen to encode.
        format_type: "embedded" for full JSON-LD, "compact" for URL.
        size: Image size in pixels (default 300).
        error_correction: Error correction level (default M, forced to H when logo is used).
        with_logo: Include wols logo watermark in center (default True).
        scheme: URL scheme for compact format. Options:
            - UrlScheme.WEB_WEMUSH (default): "web+wemush://" - PWA compatible
            - UrlScheme.WEMUSH: "wemush://" - Native app deep links
            - UrlScheme.HTTPS: "https://" - Universal web URLs
        base_url: Base URL for HTTPS scheme (only used when scheme is HTTPS).

    Returns:
        PNG image as bytes.

    Raises:
        WolsValidationError: If specimen is invalid.
        ImportError: If qrcode/pillow not installed.

    Example:
        >>> png_bytes = generate_qr_png(specimen)
        >>> with open("label.png", "wb") as f:
        ...     f.write(png_bytes)
    """
    try:
        import qrcode  # type: ignore[import-untyped]
        from qrcode.image.pil import PilImage  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError(
            "QR module not installed. Install with: pip install wols\\[qr]"
        ) from e

    data = _get_qr_data(
        specimen, format_type=format_type, scheme=scheme, base_url=base_url
    )

    # Use high error correction when logo is enabled (logo covers ~7% of QR area)
    effective_error_correction = "H" if with_logo else error_correction

    qr = qrcode.QRCode(
        version=None,  # Auto-determine
        error_correction=ERROR_CORRECTION_MAP[effective_error_correction],
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img: PilImage = qr.make_image(
        image_factory=PilImage, fill_color="black", back_color="white"
    )

    # Resize to requested size
    img = img.resize((size, size))

    # Add logo watermark if requested
    if with_logo:
        img = _add_logo_watermark(img)

    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def generate_qr_svg(
    specimen: Specimen,
    *,
    format_type: Literal["embedded", "compact"] = "embedded",
    error_correction: Literal["L", "M", "Q", "H"] = "M",
    scheme: UrlScheme | str = DEFAULT_URL_SCHEME,
    base_url: str | None = None,
) -> str:
    """Generate a QR code as SVG string.

    Args:
        specimen: Specimen to encode.
        format_type: "embedded" for full JSON-LD, "compact" for URL.
        error_correction: Error correction level (default M).
        scheme: URL scheme for compact format (see generate_qr_png for options).
        base_url: Base URL for HTTPS scheme.

    Returns:
        SVG string.

    Example:
        >>> svg = generate_qr_svg(specimen)
        >>> with open("label.svg", "w") as f:
        ...     f.write(svg)
    """
    try:
        import qrcode
        from qrcode.image.svg import SvgImage  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError(
            "QR module not installed. Install with: pip install wols\\[qr]"
        ) from e

    data = _get_qr_data(
        specimen, format_type=format_type, scheme=scheme, base_url=base_url
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECTION_MAP[error_correction],
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img: SvgImage = qr.make_image(image_factory=SvgImage)

    # Convert to string
    buffer = io.BytesIO()
    img.save(buffer)
    return buffer.getvalue().decode("utf-8")


def generate_qr_base64(
    specimen: Specimen,
    *,
    format_type: Literal["embedded", "compact"] = "embedded",
    size: int = 300,
    error_correction: Literal["L", "M", "Q", "H"] = "M",
    with_logo: bool = True,
    scheme: UrlScheme | str = DEFAULT_URL_SCHEME,
    base_url: str | None = None,
) -> str:
    """Generate a QR code as base64 data URL.

    Args:
        specimen: Specimen to encode.
        format_type: "embedded" for full JSON-LD, "compact" for URL.
        size: Image size in pixels.
        error_correction: Error correction level (forced to H when logo is used).
        with_logo: Include wols logo watermark in center (default True).
        scheme: URL scheme for compact format (see generate_qr_png for options).
        base_url: Base URL for HTTPS scheme.

    Returns:
        Base64 data URL (data:image/png;base64,...).

    Example:
        >>> data_url = generate_qr_base64(specimen)
        >>> # Use in HTML: <img src="{data_url}">
    """
    png_bytes = generate_qr_png(
        specimen,
        format_type=format_type,
        size=size,
        error_correction=error_correction,
        with_logo=with_logo,
        scheme=scheme,
        base_url=base_url,
    )
    b64 = base64.b64encode(png_bytes).decode("ascii")
    return f"data:image/png;base64,{b64}"
