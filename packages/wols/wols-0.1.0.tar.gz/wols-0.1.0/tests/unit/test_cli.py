"""Tests for wols.cli module."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from wols.cli.app import app

runner = CliRunner()


# Check if pyzbar/zbar is available for scanning tests
try:
    from pyzbar import pyzbar  # noqa: F401

    PYZBAR_AVAILABLE = True
except (ImportError, OSError):
    PYZBAR_AVAILABLE = False


class TestCliVersion:
    """Tests for CLI version command."""

    def test_version_flag(self) -> None:
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "wols version" in result.stdout


class TestCliCreate:
    """Tests for CLI create command."""

    def test_create_basic(self) -> None:
        """Test basic create command."""
        result = runner.invoke(
            app,
            [
                "create",
                "--species",
                "Pleurotus ostreatus",
                "--type",
                "CULTURE",
            ],
        )
        assert result.exit_code == 0
        assert "Specimen Created" in result.stdout
        assert "wemush:" in result.stdout

    def test_create_json_output(self) -> None:
        """Test create with JSON output."""
        result = runner.invoke(
            app,
            [
                "create",
                "--species",
                "Pleurotus ostreatus",
                "--type",
                "CULTURE",
                "--json",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["@context"] == "https://wemush.com/wols/v1"
        assert data["type"] == "CULTURE"

    def test_create_invalid_type(self) -> None:
        """Test create with invalid type."""
        result = runner.invoke(
            app,
            [
                "create",
                "--species",
                "Test",
                "--type",
                "INVALID",
            ],
        )
        assert result.exit_code == 2


class TestCliValidate:
    """Tests for CLI validate command."""

    def test_validate_valid_file(self, tmp_path: Path) -> None:
        """Test validate with valid file."""
        specimen_file = tmp_path / "specimen.json"
        specimen_file.write_text(
            """{
            "id": "wemush:abc123def456ghijklmnopqr",
            "type": "CULTURE",
            "species": "Pleurotus ostreatus"
        }"""
        )

        result = runner.invoke(app, ["validate", str(specimen_file)])
        assert result.exit_code == 0
        assert "PASSED" in result.stdout

    def test_validate_invalid_file(self, tmp_path: Path) -> None:
        """Test validate with invalid file."""
        specimen_file = tmp_path / "invalid.json"
        specimen_file.write_text('{"invalid": "json"}')

        result = runner.invoke(app, ["validate", str(specimen_file)])
        assert result.exit_code == 1

    def test_validate_nonexistent_file(self) -> None:
        """Test validate with nonexistent file."""
        result = runner.invoke(app, ["validate", "nonexistent.json"])
        assert result.exit_code == 2


class TestCliCreateAdvanced:
    """Advanced tests for CLI create command."""

    def test_create_with_all_options(self) -> None:
        """Test create with all options."""
        result = runner.invoke(
            app,
            [
                "create",
                "--species",
                "Pleurotus ostreatus",
                "--type",
                "SUBSTRATE",
                "--strain",
                "Blue Oyster",
                "--stage",
                "COLONIZATION",
                "--batch",
                "BATCH-001",
                "--organization",
                "WeMush",
                "--json",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["species"] == "Pleurotus ostreatus"
        assert data["type"] == "SUBSTRATE"

    def test_create_with_output_file(self, tmp_path: Path) -> None:
        """Test create with output file."""
        output_file = tmp_path / "output.json"
        result = runner.invoke(
            app,
            [
                "create",
                "--species",
                "Ganoderma lucidum",
                "--type",
                "CULTURE",
                "--json",
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data["species"] == "Ganoderma lucidum"

    def test_create_with_custom_json(self) -> None:
        """Test create with custom JSON fields."""
        result = runner.invoke(
            app,
            [
                "create",
                "--species",
                "Pleurotus ostreatus",
                "--type",
                "CULTURE",
                "--custom",
                '{"temp": 72, "humidity": 85}',
                "--json",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["custom"]["temp"] == 72

    def test_create_invalid_custom_json(self) -> None:
        """Test create with invalid custom JSON."""
        result = runner.invoke(
            app,
            [
                "create",
                "--species",
                "Test",
                "--type",
                "CULTURE",
                "--custom",
                "not-valid-json",
            ],
        )
        # typer returns exit code 2 for bad input
        assert result.exit_code != 0


class TestCliValidateAdvanced:
    """Advanced tests for CLI validate command."""

    def test_validate_json_output(self, tmp_path: Path) -> None:
        """Test validate with JSON output."""
        specimen_file = tmp_path / "specimen.json"
        specimen_file.write_text(
            """{
            "id": "wemush:abc123def456ghijklmnopqr",
            "type": "CULTURE",
            "species": "Pleurotus ostreatus"
        }"""
        )

        result = runner.invoke(app, ["validate", str(specimen_file), "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["valid"] is True

    def test_validate_with_warnings(self, tmp_path: Path) -> None:
        """Test validate with warnings but still valid."""
        specimen_file = tmp_path / "specimen.json"
        specimen_file.write_text(
            """{
            "id": "wemush:abc123def456ghijklmnopqr",
            "type": "CULTURE",
            "species": "Test",
            "unknownField": "value"
        }"""
        )

        result = runner.invoke(app, ["validate", str(specimen_file)])
        # Should pass (valid) but may have warnings
        assert result.exit_code == 0


class TestCliQr:
    """Tests for CLI QR command."""

    def test_qr_generate_png(self, tmp_path: Path) -> None:
        """Test QR generation to PNG file."""
        specimen_file = tmp_path / "specimen.json"
        specimen_file.write_text(
            """{
            "id": "wemush:abc123def456ghijklmnopqr",
            "type": "CULTURE",
            "species": "Pleurotus ostreatus"
        }"""
        )
        output_file = tmp_path / "qr.png"

        result = runner.invoke(
            app, ["qr", str(specimen_file), "--output", str(output_file)]
        )
        assert result.exit_code == 0
        assert output_file.exists()
        # Check PNG magic bytes
        assert output_file.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

    def test_qr_generate_svg(self, tmp_path: Path) -> None:
        """Test QR generation to SVG file."""
        specimen_file = tmp_path / "specimen.json"
        specimen_file.write_text(
            """{
            "id": "wemush:abc123def456ghijklmnopqr",
            "type": "CULTURE",
            "species": "Pleurotus ostreatus"
        }"""
        )
        output_file = tmp_path / "qr.svg"

        result = runner.invoke(
            app,
            ["qr", str(specimen_file), "--output", str(output_file), "--format", "svg"],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert "<svg" in content or "<?xml" in content

    def test_qr_compact_encoding(self, tmp_path: Path) -> None:
        """Test QR generation with compact encoding."""
        specimen_file = tmp_path / "specimen.json"
        specimen_file.write_text(
            """{
            "id": "wemush:abc123def456ghijklmnopqr",
            "type": "SUBSTRATE",
            "species": "Pleurotus ostreatus"
        }"""
        )
        output_file = tmp_path / "qr.png"

        result = runner.invoke(
            app,
            [
                "qr",
                str(specimen_file),
                "--output",
                str(output_file),
                "--encoding",
                "compact",
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()

    def test_qr_base64_format(self, tmp_path: Path) -> None:
        """Test QR base64 format output (prints to stdout, still needs output arg)."""
        specimen_file = tmp_path / "specimen.json"
        specimen_file.write_text(
            """{
            "id": "wemush:abc123def456ghijklmnopqr",
            "type": "CULTURE",
            "species": "Pleurotus ostreatus"
        }"""
        )
        # base64 format prints to stdout but still requires --output arg
        output_file = tmp_path / "dummy.txt"

        result = runner.invoke(
            app,
            [
                "qr",
                str(specimen_file),
                "--output",
                str(output_file),
                "--format",
                "base64",
            ],
        )
        assert result.exit_code == 0
        # base64 is printed to stdout
        assert "data:image/png;base64," in result.stdout


@pytest.mark.skipif(not PYZBAR_AVAILABLE, reason="pyzbar/zbar library not installed")
class TestCliScan:
    """Tests for CLI scan command."""

    def test_scan_qr_code(self, tmp_path: Path) -> None:
        """Test scanning a QR code."""
        from wols import create_specimen
        from wols.qr import generate_qr_png

        specimen = create_specimen(
            type="CULTURE",
            species="Pleurotus ostreatus",
        )
        qr_bytes = generate_qr_png(specimen, format="embedded")

        qr_file = tmp_path / "qr.png"
        qr_file.write_bytes(qr_bytes)

        result = runner.invoke(app, ["scan", str(qr_file)])
        assert result.exit_code == 0
