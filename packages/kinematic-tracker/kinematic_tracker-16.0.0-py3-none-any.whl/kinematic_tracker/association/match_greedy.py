"""Module implementing a greedy matching algorithm for associating reports and targets."""

import numpy as np

from .match_driver_base import MatchDriverBase


class MatchDriverGreedy(MatchDriverBase):
    """Class implementing a greedy matching algorithm for associating reports and targets."""

    def __init__(self, num_rows_max: int, num_cols_max: int) -> None:
        """
        Initialize the MatchDriverGreedy instance.

        Args:
            num_rows_max: Maximum number of rows allowed in the score matrix.
            num_cols_max: Maximum number of columns allowed in the score matrix.
        """
        super().__init__(num_rows_max, num_cols_max)

    def compute_matches(self, score: np.ndarray, threshold: float) -> None:
        """
        Compute the association map using the greedy algorithm.

        Args:
            score: A 2D array of likelihoods where each element represents
                   the similarity score between a report and a target.
            threshold: The minimum score required to consider a pair as associated.

        Returns:
            None: Updates the `reports` and `targets` attributes with the associations.
        """
        self.check_max_shape(score.shape)
        self.num_matches = 0
        this_num_matches_max = min(score.shape)

        # Flatten the score matrix and sort indices in descending order of scores.
        args_sort = np.argsort(-score, axis=None)

        # Iterate over sorted indices to find valid associations.
        for arg in args_sort:
            # Convert the flattened index back to 2D indices (row, column).
            target_report = np.unravel_index(arg, score.shape)
            r, c = int(target_report[0]), int(target_report[1])

            # Check if the score meets the threshold and the row/column are not already associated.
            if (
                score[r, c] >= threshold
                and (r not in self.reports[: self.num_matches])
                and (c not in self.targets[: self.num_matches])
            ):
                self.reports[self.num_matches] = r
                self.targets[self.num_matches] = c
                self.num_matches += 1

            # Stop if the maximum number of matches is reached.
            if self.num_matches >= this_num_matches_max:
                break
