"""
This module defines the `ProcNoiseKind` enumeration. The enumerable
represents different types of process noise used in tracking.
"""

from enum import Enum


class ProcNoiseKind(Enum):
    """
    An enumeration to represent various kinds of process noise.

    Attributes:
        FINITE_DIFF: Represents the white-noise-based adaptive process noise.
        CONST: Represents the white-noise-based fixed-variance process noise.
        DIAGONAL: Represents diagonal process noise (with fixed variance).
        UNKNOWN: Represents an unknown type of process noise.
    """

    FINITE_DIFF = 'finite_diff'
    CONST = 'const'
    DIAGONAL = 'diagonal'
    UNKNOWN = 'unknown'
