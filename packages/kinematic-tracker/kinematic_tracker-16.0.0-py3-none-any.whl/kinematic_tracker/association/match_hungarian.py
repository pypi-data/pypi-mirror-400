"""Module for the Hungarian bipartite matching.

This module provides a class `MatchDriverHungarian` that implements a necessary treatment of the
score matrix to be analyzed with a linear-sum assignment (Hungarian) algorithm. It extends
the `MatchDriverBase` class. The linear-sum assignment from SciPy is applied.
"""

import numpy as np

from scipy.optimize import linear_sum_assignment

from .match_driver_base import MatchDriverBase


class MatchDriverHungarian(MatchDriverBase):
    """Class for Hungarian algorithm-based matching.

    This class uses the Hungarian algorithm to compute optimal matches
    between reports and targets based on a given score matrix.
    """

    def __init__(self, num_rows_max: int, num_cols_max: int) -> None:
        """
        Initialize the MatchDriverHungarian instance.

        This constructor initializes the base class and allocates a buffer for the score matrix.
        The buffer is necessary to because we have to treat the score matrix with a threshold
        before applying the linear-sum optimization (we do not want to change the input array
        of scores).

        Args:
            num_rows_max: Maximum number of rows in the score matrix.
            num_cols_max: Maximum number of columns in the score matrix.
        """
        super().__init__(num_rows_max, num_cols_max)
        self.score_rc = np.zeros((num_rows_max, num_cols_max))  # The buffer storage.

    def compute_matches(self, score: np.ndarray, threshold: float) -> None:
        """
        Compute the association map using the Hungarian algorithm.

        This method computes the optimal assignment of reports to targets
        based on the provided score matrix. Matches with scores below the
        threshold are ignored.

        Args:
            score (np.ndarray): The array of likelihoods (report, target) -> score.
            threshold (float): The threshold to declare the loose pairs.

        Returns:
            None: Updates the `reports` and `targets` attributes with the matches.
        """
        # Ensure the input score matrix does not exceed the pre-allocated size.
        self.check_max_shape(score.shape)

        # Reshape and copy the input score matrix into the pre-allocated matrix.
        rect_chunk = self.score_rc.reshape(-1)[: score.size].reshape(score.shape)
        rect_chunk[:] = score

        # Set scores below the threshold to zero.
        rect_chunk[rect_chunk < threshold] = 0.0

        # Apply the Hungarian algorithm to find the optimal assignment.
        rows, cols = linear_sum_assignment(rect_chunk, maximize=True)

        # Store the matches with score values above the threshold.
        self.num_matches = 0
        for row, col in zip(rows, cols):
            if score[row, col] >= threshold:
                self.reports[self.num_matches] = row
                self.targets[self.num_matches] = col
                self.num_matches += 1
