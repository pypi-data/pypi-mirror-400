"""
This module defines the `MatchDriverBase` class, which provides a common
functionality for validating the shapes of the input metric and storing result
of the association.
"""

import numpy as np


class MatchDriverBase:
    """
    A base class for managing associations between reports and targets.

    Attributes:
        num_reports_max: The maximum number of reports allowed.
        num_targets_max: The maximum number of targets allowed.
        reports: An integer array storing the indices of matched reports (result).
        targets: An integer array storing the indices of matched targets (result).
        num_matches: The current number of matches.
    """

    def __init__(self, num_rows_max: int, num_cols_max: int) -> None:
        """
        Initializes the MatchDriverBase instance.

        Args:
            num_rows_max: The maximum number of rows (reports).
            num_cols_max: The maximum number of columns (targets).
        """
        self.num_reports_max = num_rows_max
        self.num_targets_max = num_cols_max
        num_matches_max = min(num_rows_max, num_cols_max)
        self.reports = np.zeros(num_matches_max, dtype=int)
        self.targets = np.zeros(num_matches_max, dtype=int)
        self.num_matches = 0

    def check_max_shape(self, shape: tuple[int, int]) -> None:
        """
        Validates that the given shape does not exceed the maximum allowed dimensions.

        Args:
            shape (tuple[int, int]): A tuple representing the shape (rows, columns).

        Raises:
            ValueError: If the number of rows exceeds `num_reports_max` or
                        the number of columns exceeds `num_targets_max`.
        """
        if shape[0] > self.num_reports_max:
            raise ValueError(f'Too much reports? {shape[0]} {self.num_reports_max}')
        if shape[1] > self.num_targets_max:
            raise ValueError(f'Too much targets? {shape[1]} {self.num_targets_max}')

    def get_reports_targets(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Retrieves the matched reports and targets.

        Returns:
            tuple[np.ndarray, np.ndarray]: A tuple containing two arrays:
                                           - The (valid chunk of) matched reports.
                                           - The (valid chunk of) matched targets.
        """
        return self.reports[: self.num_matches], self.targets[: self.num_matches]
