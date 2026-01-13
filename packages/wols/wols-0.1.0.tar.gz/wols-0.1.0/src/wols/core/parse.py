"""Specimen parsing functionality."""

from __future__ import annotations

import contextlib
import json
from urllib.parse import parse_qs, urlparse

from wols.constants import STAGE_CODES, VALID_URL_SCHEMES
from wols.exceptions import WolsParseError
from wols.models.enums import GrowthStage
from wols.models.specimen import Specimen, SpecimenRef


def parse_specimen(json_str: str) -> Specimen:
    """Parse a JSON-LD string into a Specimen object.

    Args:
        json_str: JSON-LD formatted specimen string.

    Returns:
        Parsed Specimen instance.

    Raises:
        WolsParseError: If JSON is invalid or missing required fields.

    Example:
        >>> json_str = '{"@context": "https://wemush.com/wols/v1", ...}'
        >>> specimen = parse_specimen(json_str)
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise WolsParseError(
            message=f"Invalid JSON: {e.msg} at line {e.lineno}, column {e.colno}",
            code="INVALID_JSON",
            input=json_str,
        ) from e

    if not isinstance(data, dict):
        raise WolsParseError(
            message="Expected JSON object, got " + type(data).__name__,
            code="INVALID_TYPE",
            input=json_str,
        )

    # Check required fields
    required_fields = ["id", "type", "species"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise WolsParseError(
            message=f"Missing required field(s): {', '.join(missing)}",
            code="REQUIRED_FIELD",
            input=json_str,
        )

    try:
        return Specimen.from_dict(data)
    except (KeyError, ValueError) as e:
        raise WolsParseError(
            message=f"Failed to parse specimen: {e}",
            code="PARSE_ERROR",
            input=json_str,
        ) from e


def parse_compact_url(url: str) -> SpecimenRef:
    """Parse a compact WOLS URL into a SpecimenRef.

    Supports multiple URL schemes:
        - wemush://v1/{id}?s={species}&st={stage} (native app)
        - web+wemush://v1/{id}?s={species}&st={stage} (PWA)
        - https://domain/path/v1/{id}?s={species}&st={stage} (web)

    Args:
        url: Compact URL in any supported scheme.

    Returns:
        SpecimenRef with extracted parameters.

    Raises:
        WolsParseError: If URL format is invalid.

    Example:
        >>> ref = parse_compact_url("web+wemush://v1/abc123?s=PO&st=COL")
        >>> print(ref.id)
        'abc123'
        >>> print(ref.species_code)
        'PO'

        >>> ref = parse_compact_url("https://wemush.com/s/v1/abc123?s=PO")
        >>> print(ref.id)
        'abc123'
    """
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise WolsParseError(
            message=f"Invalid URL format: {e}",
            code="INVALID_URL",
            input=url,
        ) from e

    # Validate scheme
    if parsed.scheme not in VALID_URL_SCHEMES:
        valid_schemes = ", ".join(sorted(VALID_URL_SCHEMES))
        raise WolsParseError(
            message=f"Invalid URL scheme: expected one of "
            f"[{valid_schemes}], got '{parsed.scheme}'",
            code="INVALID_SCHEME",
            input=url,
        )

    # Parse path based on scheme type
    # HTTPS: path is like /s/v1/{id} or /specimen/v1/{id}
    # Custom schemes: netloc contains the path start (v1/...)
    path = parsed.path if parsed.scheme == "https" else parsed.netloc + parsed.path

    path_parts = [p for p in path.split("/") if p]

    # Find the version marker (v1) in the path
    try:
        v1_index = path_parts.index("v1")
    except ValueError:
        raise WolsParseError(
            message=f"Invalid URL path: missing 'v1' version marker in '{path}'",
            code="INVALID_PATH",
            input=url,
        ) from None

    # Specimen ID should follow v1
    if len(path_parts) <= v1_index + 1:
        raise WolsParseError(
            message=f"Invalid URL path: missing specimen ID after 'v1' in '{path}'",
            code="INVALID_PATH",
            input=url,
        )

    specimen_id = path_parts[v1_index + 1]

    # Parse query parameters
    query_params: dict[str, str] = {}
    if parsed.query:
        raw_params = parse_qs(parsed.query)
        # Flatten single-value lists (always take first value)
        query_params = {k: v[0] for k, v in raw_params.items()}

    # Extract species code
    species_code = query_params.get("s")

    # Extract and convert stage
    stage: GrowthStage | None = None
    stage_code = query_params.get("st")
    if stage_code:
        stage_value = STAGE_CODES.get(stage_code.upper())
        if stage_value:
            with contextlib.suppress(ValueError):
                stage = GrowthStage(stage_value)

    return SpecimenRef(
        id=specimen_id,
        species_code=species_code,
        stage=stage,
        params=query_params,
    )
