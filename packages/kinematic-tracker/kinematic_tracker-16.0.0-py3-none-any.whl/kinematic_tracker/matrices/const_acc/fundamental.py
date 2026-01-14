"""This is the transition matrix for the constant-acceleration point-motion model."""

import numpy as np


class FundMatCa:
    """."""

    def __init__(self) -> None:
        """."""
        self.f_mat = np.eye(3)

    def compute(self, dt: float) -> None:
        """."""
        f_mat = self.f_mat
        f_mat[0, 1] = dt
        f_mat[0, 2] = dt * dt / 2.0
        f_mat[1, 2] = dt
