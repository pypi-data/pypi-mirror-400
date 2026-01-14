"""
This module provides a utility function to determine which sequential indices
are absent in a given list.
"""

from typing import Sequence


def get_loose_indices(indices: Sequence[int], num_indices: int) -> set[int]:
    """
    Calculate the set of indices that are not included in the given sequence of indices.

    Args:
        indices: A sequence of integers representing the indices to exclude.
        num_indices: The total number of indices to consider.

    Returns:
        set[int]: A set of indices that are not in the input sequence.
    """
    return set(range(num_indices)) - set(indices)
