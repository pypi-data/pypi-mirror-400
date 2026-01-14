"""Exception hierarchy for neon."""

from typing import Optional


class NeonError(Exception):
    """Base class for all neon errors."""

    pass


class InvalidValueError(NeonError):
    """Raised when a value is NaN or otherwise invalid for an operation."""

    def __init__(self, message: str, value: Optional[float] = None) -> None:
        super().__init__(message)
        self.value = value


class EmptyInputError(NeonError):
    """Raised when an empty sequence is provided where not allowed."""

    pass
