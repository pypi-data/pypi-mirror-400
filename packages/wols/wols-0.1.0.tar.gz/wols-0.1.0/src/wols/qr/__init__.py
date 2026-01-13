"""WOLS QR code generation and scanning.

Optional module - requires: pip install wols[qr]
"""

from wols.qr.generate import generate_qr_base64, generate_qr_png, generate_qr_svg
from wols.qr.scan import scan_qr

__all__ = [
    "generate_qr_base64",
    "generate_qr_png",
    "generate_qr_svg",
    "scan_qr",
]
