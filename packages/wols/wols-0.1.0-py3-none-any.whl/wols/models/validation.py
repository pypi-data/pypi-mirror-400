"""WOLS validation result types.

Contains ValidationResult and ValidationError dataclasses.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ValidationError:
    """Validation error detail.

    Attributes:
        path: JSON path to the invalid field (e.g., "strain.generation").
        code: Error code (e.g., "INVALID_TYPE", "REQUIRED_FIELD").
        message: Human-readable error message.
    """

    path: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: [{self.code}] {self.message}"


@dataclass(frozen=True)
class ValidationResult:
    """Result of specimen validation.

    Attributes:
        valid: Overall validity status.
        errors: List of validation errors.
        warnings: List of validation warnings.
    """

    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid
