"""
RevHold SDK Exceptions
"""

from typing import Any, Dict, Optional


class RevHoldError(Exception):
    """Base exception for all RevHold API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 0,
        error_code: str = "unknown_error",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a RevHold error.

        Args:
            message: Human-readable error message
            status_code: HTTP status code (0 for network errors)
            error_code: Machine-readable error code
            details: Additional error context
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        """String representation of the error."""
        if self.status_code:
            return f"[{self.status_code}] {self.error_code}: {self.message}"
        return f"{self.error_code}: {self.message}"

    def __repr__(self) -> str:
        """Developer representation of the error."""
        return (
            f"RevHoldError(message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"error_code={self.error_code!r})"
        )

    @property
    def is_rate_limit_error(self) -> bool:
        """Check if this is a rate limit error (429)."""
        return self.status_code == 429

    @property
    def is_payment_required_error(self) -> bool:
        """Check if this is a payment required error (402)."""
        return self.status_code == 402

    @property
    def is_authentication_error(self) -> bool:
        """Check if this is an authentication error (401)."""
        return self.status_code == 401

    @property
    def is_network_error(self) -> bool:
        """Check if this is a network error."""
        return self.status_code == 0 or self.error_code == "network_error"

