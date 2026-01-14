"""."""

import numpy as np

from kinematic_tracker.nd.gen_x import NdKkfMatGenX
from kinematic_tracker.nd.precursors import NdKkfPrecursors


class NdKkfWhiteNoiseConst:
    """."""

    def __init__(self, gen_x: NdKkfMatGenX, factor: float) -> None:
        """Constructor.

        Args:
            gen_x: driver of the matrix generation for kinematic states.
            factor: the pre-factor to multiply the eye.
        """
        self.gen_x = gen_x
        self.factor = factor
        self.factors = factor * np.ones(gen_x.num_d)

    def __repr__(self) -> str:
        """."""
        return f'NdKkfWhiteNoiseConst({self.factor})'

    def fill_proc_cov(self, pre: NdKkfPrecursors, _vec_x: np.ndarray, cov_xx: np.ndarray) -> None:
        """."""
        self.gen_x.fill_q_mat(pre, self.factors, cov_xx)

    def save_values(self, vec_x: np.ndarray) -> None:
        """."""
