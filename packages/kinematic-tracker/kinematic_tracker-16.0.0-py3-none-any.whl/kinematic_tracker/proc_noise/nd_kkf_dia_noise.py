"""."""

import numpy as np

from kinematic_tracker.nd.precursors import NdKkfPrecursors


class NdKkfDiaNoise:
    """."""

    def __init__(self, factor: float) -> None:
        """Constructor.

        Args:
            factor: pre-factor to multiply the eye matrix.
        """
        self.factor = factor

    def __repr__(self) -> str:
        """."""
        return f'NdKkfDiaNoise({self.factor})'

    def fill_proc_cov(self, _pre: NdKkfPrecursors, _vec_x: np.ndarray, cov_xx: np.ndarray) -> None:
        """."""
        num_x = cov_xx.shape[0]
        cov_xx[:, :] = self.factor * np.eye(num_x)

    def save_values(self, vec_x: np.ndarray) -> None:
        """."""
