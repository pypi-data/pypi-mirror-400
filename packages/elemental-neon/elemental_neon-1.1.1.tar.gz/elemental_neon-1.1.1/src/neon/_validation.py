"""Internal validation utilities."""

from collections.abc import Sequence

from .exceptions import EmptyInputError


def validate_non_empty(seq: Sequence[float], name: str = "sequence") -> None:
    """Validate that a sequence is non-empty.

    Args:
        seq: Sequence to validate
        name: Name of the parameter for error messages

    Raises:
        EmptyInputError: If sequence is empty
    """
    if len(seq) == 0:
        raise EmptyInputError(f"Cannot operate on empty {name}")


def validate_equal_length(
    seq1: Sequence[float], seq2: Sequence[float], name1: str = "first", name2: str = "second"
) -> None:
    """Validate that two sequences have equal length.

    Args:
        seq1: First sequence to validate
        seq2: Second sequence to validate
        name1: Name of first parameter for error messages
        name2: Name of second parameter for error messages

    Raises:
        ValueError: If sequences have different lengths
    """
    if len(seq1) != len(seq2):
        raise ValueError(
            f"Input sequences must have equal length "
            f"(got {len(seq1)} for {name1} and {len(seq2)} for {name2})"
        )
