"""This is the transition matrix for the constant-velocity motion model for Cartesian point."""

import numpy as np


class FundMatCv:
    """."""

    def __init__(self) -> None:
        """."""
        self.f_mat = np.eye(2)

    def compute(self, dt: float) -> None:
        """."""
        self.f_mat[0, 1] = dt
