"""Tests for wols.core.validate."""

from wols import validate_specimen


class TestValidateSpecimen:
    """Tests for validate_specimen function."""

    def test_valid_specimen_dict(self) -> None:
        """Test validating a specimen as dict."""
        data = {
            "id": "wemush:abc123def456ghijklmnopqr",
            "type": "CULTURE",
            "species": "Pleurotus ostreatus",
        }
        result = validate_specimen(data)
        assert result.valid is True

    def test_missing_id(self) -> None:
        """Test that missing ID is an error."""
        data = {"type": "CULTURE", "species": "Test"}
        result = validate_specimen(data)
        assert result.valid is False
        assert any(e.code == "REQUIRED_FIELD" and e.path == "id" for e in result.errors)

    def test_missing_type(self) -> None:
        """Test that missing type is an error."""
        data = {"id": "wemush:abc123def456ghijklmnopqr", "species": "Test"}
        result = validate_specimen(data)
        assert result.valid is False
        assert any(
            e.code == "REQUIRED_FIELD" and e.path == "type" for e in result.errors
        )

    def test_invalid_type_value(self) -> None:
        """Test that invalid type value is an error."""
        data = {
            "id": "wemush:abc123def456ghijklmnopqr",
            "type": "INVALID",
            "species": "Test",
        }
        result = validate_specimen(data)
        assert result.valid is False
        assert any(
            e.code == "INVALID_VALUE" and e.path == "type" for e in result.errors
        )

    def test_unknown_field_warning(self) -> None:
        """Test that unknown fields produce warnings."""
        data = {
            "id": "wemush:abc123def456ghijklmnopqr",
            "type": "CULTURE",
            "species": "Test",
            "unknownField": "value",
        }
        result = validate_specimen(data)
        assert result.valid is True
        assert any(w.code == "UNKNOWN_FIELD" for w in result.warnings)

    def test_strict_mode_unknown_field_error(self) -> None:
        """Test that unknown fields are errors in strict mode."""
        data = {
            "id": "wemush:abc123def456ghijklmnopqr",
            "type": "CULTURE",
            "species": "Test",
            "unknownField": "value",
        }
        result = validate_specimen(data, strict=True)
        assert result.valid is False
        assert any(e.code == "UNKNOWN_FIELD" for e in result.errors)
