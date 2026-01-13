"""WOLS CLI application."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from wols import (
    DEFAULT_HTTPS_BASE_URL,
    UrlScheme,
    __version__,
    create_specimen,
    parse_specimen,
    to_json,
    validate_specimen,
)
from wols.models.enums import GrowthStage, SpecimenType

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="wols",
    help="WOLS - WeMush Open Labeling Standard CLI",
    no_args_is_help=True,
)

console = Console()
err_console = Console(stderr=True)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"wols version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """WOLS - WeMush Open Labeling Standard CLI."""
    logger.debug("Version: %s", version)


@app.command()
def create(
    species: Annotated[
        str, typer.Option("--species", "-s", help="Scientific species name")
    ],
    type_: Annotated[
        str,
        typer.Option(
            "--type",
            "-t",
            help="Specimen type (CULTURE, SPAWN, SUBSTRATE, FRUITING, HARVEST)",
        ),
    ],
    strain: Annotated[str | None, typer.Option("--strain", help="Strain name")] = None,
    stage: Annotated[
        str | None,
        typer.Option(
            "--stage",
            help="Growth stage (INOCULATION, COLONIZATION, FRUITING, HARVEST)",
        ),
    ] = None,
    batch: Annotated[
        str | None, typer.Option("--batch", help="Batch identifier")
    ] = None,
    organization: Annotated[
        str | None, typer.Option("--organization", help="Organization name")
    ] = None,
    creator: Annotated[
        str | None, typer.Option("--creator", help="Creator identifier")
    ] = None,
    custom: Annotated[
        str | None, typer.Option("--custom", help="Custom fields as JSON string")
    ] = None,
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="Write output to file")
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output as JSON (default: human-readable)"),
    ] = False,
) -> None:
    """Create a new specimen label."""
    try:
        # Parse custom fields if provided
        custom_fields = None
        if custom:
            try:
                custom_fields = json.loads(custom)
            except json.JSONDecodeError as e:
                err_console.print(
                    "[red]Error: INVALID_JSON - "
                    f"Failed to parse custom fields: {e}[/red]"
                )
                raise typer.Exit(2)

        # Validate type
        try:
            specimen_type = SpecimenType(type_.upper())
        except ValueError as exc:
            valid = ", ".join(t.value for t in SpecimenType)
            err_console.print(
                f"[red]Error: INVALID_TYPE - '{type_}'"
                " is not a valid specimen type[/red]"
            )
            err_console.print(f"Valid types: {valid}")
            raise typer.Exit(2) from exc

        # Validate stage if provided
        growth_stage = None
        if stage:
            try:
                growth_stage = GrowthStage(stage.upper())
            except ValueError as exc:
                valid = ", ".join(s.value for s in GrowthStage)
                err_console.print(
                    f"[red]Error: INVALID_STAGE - '{stage}'"
                    " is not a valid growth stage[/red]"
                )
                err_console.print(f"Valid stages: {valid}")
                raise typer.Exit(2) from exc

        # Create specimen
        specimen = create_specimen(
            input_type=specimen_type,
            species=species,
            strain=strain,
            stage=growth_stage,
            batch=batch,
            organization=organization,
            creator=creator,
            custom=custom_fields,
        )

        # Generate output
        if json_output or output:
            json_str = to_json(specimen, indent=2)
            if output:
                output.write_text(json_str)
                console.print(f"[green]Specimen saved to {output}[/green]")
            else:
                console.print(json_str)
        else:
            # Human-readable output
            console.print("\n[bold]Specimen Created[/bold]")
            console.print("=" * 40)
            console.print(f"[cyan]ID:[/cyan]       {specimen.id}")
            console.print(f"[cyan]Version:[/cyan]  {specimen.version}")
            console.print(f"[cyan]Type:[/cyan]     {specimen.type.value}")
            console.print(f"[cyan]Species:[/cyan]  {specimen.species}")
            if specimen.strain:
                console.print(f"[cyan]Strain:[/cyan]   {specimen.strain.name}")
            if specimen.stage:
                console.print(f"[cyan]Stage:[/cyan]    {specimen.stage.value}")
            if specimen.created:
                console.print(f"[cyan]Created:[/cyan]  {specimen.created.isoformat()}")
    except typer.Exit:
        raise
    except Exception as e:
        err_console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def validate(
    input_file: Annotated[
        Path | None,
        typer.Argument(help="Specimen JSON file or - for stdin"),
    ] = None,
    input_opt: Annotated[
        Path | None, typer.Option("--input", "-i", help="Read specimen from file")
    ] = None,
    strict: Annotated[
        bool, typer.Option("--strict", help="Treat unknown fields as errors")
    ] = False,
    json_output: Annotated[
        bool, typer.Option("--json", "-j", help="Output validation result as JSON")
    ] = False,
) -> None:
    """Validate specimen JSON against WOLS v1.1.0 schema."""
    # Determine input source
    file_path = input_file or input_opt

    try:
        if file_path is None or str(file_path) == "-":
            # Read from stdin
            json_str = sys.stdin.read()
        else:
            if not file_path.exists():
                err_console.print(
                    "[red]Error: FILE_NOT_FOUND - Could not read file"
                    f" '{file_path}'[/red]"
                )
                raise typer.Exit(2)
            json_str = file_path.read_text()

        # Parse specimen
        try:
            specimen = parse_specimen(json_str)
        except Exception as e:
            if json_output:
                error_result = {
                    "valid": False,
                    "errors": [
                        {
                            "path": "",
                            "code": "PARSE_ERROR",
                            "message": str(e),
                        }
                    ],
                    "warnings": [],
                }
                console.print(json.dumps(error_result, indent=2))
            else:
                console.print("[red]Validation: FAILED[/red]\n")
                console.print(f"[red]Parse Error: {e}[/red]")
            raise typer.Exit(1)

        # Validate specimen
        result = validate_specimen(specimen, strict=strict)

        if json_output:
            output = {
                "valid": result.valid,
                "errors": [
                    {"path": e.path, "code": e.code, "message": e.message}
                    for e in result.errors
                ],
                "warnings": [
                    {"path": w.path, "code": w.code, "message": w.message}
                    for w in result.warnings
                ],
            }
            console.print(json.dumps(output, indent=2))
        else:
            if result.valid:
                console.print("[green]Validation: PASSED[/green]")
                console.print(f"Specimen ID: {specimen.id}")
                console.print(f"Version: {specimen.version}")
            else:
                console.print("[red]Validation: FAILED[/red]\n")
                console.print("[bold]Errors:[/bold]")
                for error in result.errors:
                    console.print(f"  - {error.path}: [{error.code}] {error.message}")

            if result.warnings:
                console.print("\n[bold]Warnings:[/bold]")
                for warning in result.warnings:
                    console.print(
                        f"  - {warning.path}: [{warning.code}] {warning.message}"
                    )

        if not result.valid:
            raise typer.Exit(1)

    except typer.Exit:
        raise
    except Exception as e:
        err_console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def qr(
    input_file: Annotated[
        Path, typer.Argument(help="Specimen JSON file or - for stdin")
    ],
    output: Annotated[Path, typer.Option("--output", "-o", help="Output file path")],
    format_: Annotated[
        str, typer.Option("--format", "-f", help="Output format: png, svg, base64")
    ] = "png",
    encoding: Annotated[
        str, typer.Option("--encoding", help="QR encoding: embedded, compact")
    ] = "embedded",
    size: Annotated[int, typer.Option("--size", help="Image size in pixels")] = 300,
    error_correction: Annotated[
        str,
        typer.Option("--error-correction", help="Error correction level: L, M, Q, H"),
    ] = "M",
    scheme: Annotated[
        str,
        typer.Option(
            "--scheme",
            help="URL scheme for compact encoding: "
            "web+wemush (PWA, default), wemush (native), https (web)",
        ),
    ] = "web+wemush",
    base_url: Annotated[
        str | None,
        typer.Option(
            "--base-url",
            help=f"Base URL for https scheme (default: {DEFAULT_HTTPS_BASE_URL})",
        ),
    ] = None,
) -> None:
    """Generate QR code from specimen JSON."""
    try:
        from wols.qr import generate_qr_base64, generate_qr_png, generate_qr_svg
    except ImportError as imp_exc:
        err_console.print(
            "[red]Error: MODULE_NOT_INSTALLED - QR module not installed[/red]"
        )
        err_console.print("Install with: pip install wols\\[qr]")
        raise typer.Exit(2) from imp_exc

    try:
        # Read input
        if str(input_file) == "-":
            json_str = sys.stdin.read()
        else:
            if not input_file.exists():
                err_console.print(
                    f"[red]Error: FILE_NOT_FOUND - Could not read file"
                    f" '{input_file}'[/red]"
                )
                raise typer.Exit(2)
            json_str = input_file.read_text()

        # Parse specimen
        specimen = parse_specimen(json_str)

        # Validate format and encoding
        format_lower = format_.lower()
        if format_lower not in ("png", "svg", "base64"):
            err_console.print(
                f"[red]Error: INVALID_FORMAT - '{format_}' is not a valid format[/red]"
            )
            err_console.print("Valid formats: png, svg, base64")
            raise typer.Exit(2)

        encoding_lower = encoding.lower()
        if encoding_lower not in ("embedded", "compact"):
            err_console.print(
                f"[red]Error: INVALID_ENCODING - '{encoding}' is"
                " not a valid encoding[/red]"
            )
            err_console.print("Valid encodings: embedded, compact")
            raise typer.Exit(2)

        ec = error_correction.upper()
        if ec not in ("L", "M", "Q", "H"):
            err_console.print(
                f"[red]Error: INVALID_ERROR_CORRECTION -"
                f" '{error_correction}' is not valid[/red]"
            )
            err_console.print("Valid levels: L, M, Q, H")
            raise typer.Exit(2)

        # Validate URL scheme
        try:
            url_scheme = UrlScheme(scheme)
        except ValueError:
            valid_schemes = ", ".join(s.value for s in UrlScheme)
            err_console.print(
                f"[red]Error: INVALID_SCHEME - '{scheme}' is"
                " not a valid URL scheme[/red]"
            )
            err_console.print(f"Valid schemes: {valid_schemes}")
            raise typer.Exit(2)

        # Generate QR code
        if format_lower == "png":
            png_data = generate_qr_png(
                specimen,
                format_type=encoding_lower,  # type: ignore[arg-type]
                size=size,
                error_correction=ec,  # type: ignore[arg-type]
                scheme=url_scheme,
                base_url=base_url,
            )
            output.write_bytes(png_data)
        elif format_lower == "svg":
            svg_data = generate_qr_svg(
                specimen,
                format_type=encoding_lower,  # type: ignore[arg-type]
                error_correction=ec,  # type: ignore[arg-type]
                scheme=url_scheme,
                base_url=base_url,
            )
            output.write_text(svg_data)
        else:  # base64
            b64_data = generate_qr_base64(
                specimen,
                format_type=encoding_lower,  # type: ignore[arg-type]
                size=size,
                error_correction=ec,  # type: ignore[arg-type]
                scheme=url_scheme,
                base_url=base_url,
            )
            console.print(b64_data)
            return

        # Success output
        console.print("\n[bold]QR Code Generated[/bold]")
        console.print("=" * 40)
        console.print(f"[cyan]Output:[/cyan]    {output}")
        console.print(f"[cyan]Format:[/cyan]    {format_.upper()} ({size}x{size})")
        console.print(f"[cyan]Encoding:[/cyan]  {encoding_lower}")
        if encoding_lower == "compact":
            console.print(f"[cyan]Scheme:[/cyan]    {url_scheme.value}")
        file_size = output.stat().st_size
        console.print(f"[cyan]Size:[/cyan]      {file_size:,} bytes")

    except typer.Exit:
        raise
    except Exception as e:
        err_console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def scan(
    image: Annotated[
        Path,
        typer.Argument(help="QR code image file (PNG, JPEG)"),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Write specimen to file"),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output as JSON"),
    ] = False,
) -> None:
    """Scan QR code image to extract specimen data."""
    try:
        from wols.qr import scan_qr
    except ImportError as imp_exc:
        err_console.print(
            "[red]Error: MODULE_NOT_INSTALLED - QR scan module not installed[/red]"
        )
        err_console.print("Install with: pip install wols\\[qr]")
        raise typer.Exit(2) from imp_exc

    try:
        if not image.exists():
            err_console.print(
                f"[red]Error: FILE_NOT_FOUND - Could not read file '{image}'[/red]"
            )
            raise typer.Exit(2)

        # Scan QR code
        from wols.models.specimen import Specimen

        result = scan_qr(image)

        if isinstance(result, Specimen):
            # Full specimen
            if json_output or output:
                json_str = to_json(result, indent=2)
                if output:
                    output.write_text(json_str)
                    console.print(f"[green]Specimen saved to {output}[/green]")
                else:
                    console.print(json_str)
            else:
                console.print("\n[bold]Specimen Found[/bold]")
                console.print("=" * 40)
                console.print(f"[cyan]ID:[/cyan]       {result.id}")
                console.print(f"[cyan]Version:[/cyan]  {result.version}")
                console.print(f"[cyan]Type:[/cyan]     {result.type.value}")
                console.print(f"[cyan]Species:[/cyan]  {result.species}")
                if result.strain:
                    console.print(f"[cyan]Strain:[/cyan]   {result.strain.name}")
        else:
            # SpecimenRef (compact URL)
            if json_output:
                output_data = {
                    "id": result.id,
                    "species_code": result.species_code,
                    "stage": result.stage.value if result.stage else None,
                    "params": result.params,
                }
                console.print(json.dumps(output_data, indent=2))
            else:
                console.print("\n[bold]Specimen Reference Found[/bold]")
                console.print("=" * 40)
                console.print(f"[cyan]ID:[/cyan]           {result.id}")
                if result.species_code:
                    console.print(f"[cyan]Species Code:[/cyan] {result.species_code}")
                if result.stage:
                    console.print(f"[cyan]Stage:[/cyan]        {result.stage.value}")
                console.print(
                    "\n[dim]Note: Compact URL contains limited data."
                    " Use full embedded format for complete"
                    " specimen info.[/dim]"
                )
    except typer.Exit:
        raise
    except Exception as e:
        err_console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def main_cli() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main_cli()
