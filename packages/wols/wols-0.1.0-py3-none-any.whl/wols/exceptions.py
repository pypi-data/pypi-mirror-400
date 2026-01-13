"""WOLS exception classes.

All custom exceptions for the WOLS library.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from wols.models.validation import ValidationError


class WolsError(Exception):
    """Base exception for WOLS errors.

    Args:
        message: Human-readable error message.
        code: Error code for programmatic handling.
        details: Additional context information.
    """

    def __init__(
        self,
        message: str,
        code: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(message={self.message!r}, code={self.code!r})"
        )


class WolsParseError(WolsError):
    """Raised when parsing fails.

    Args:
        message: What went wrong.
        code: Error code (default: PARSE_ERROR).
        input: The input that failed to parse.
    """

    def __init__(
        self,
        message: str,
        code: str = "PARSE_ERROR",
        input: str | None = None,
    ) -> None:
        details = {"input": input} if input else None
        super().__init__(message, code, details)
        self.input = input


class WolsValidationError(WolsError):
    """Raised when validation fails.

    Args:
        message: Summary of validation failure.
        errors: Detailed error list.
    """

    def __init__(
        self,
        message: str,
        errors: list[ValidationError],
    ) -> None:
        super().__init__(message, "VALIDATION_ERROR")
        self.errors = errors

    def __str__(self) -> str:
        error_lines = [f"  - {e.path}: {e.message}" for e in self.errors]
        return f"[{self.code}] {self.message}\n" + "\n".join(error_lines)


class WolsEncryptionError(WolsError):
    """Raised when encryption/decryption fails.

    Args:
        message: What went wrong.
        code: Error code (default: ENCRYPTION_ERROR).
    """

    def __init__(
        self,
        message: str,
        code: str = "ENCRYPTION_ERROR",
    ) -> None:
        super().__init__(message, code)
