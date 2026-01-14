"""This is the transition matrix for the constant-jerk motion model for Cartesian point."""

import numpy as np


class FundMatCj:
    """."""

    def __init__(self) -> None:
        """."""
        self.f_mat = np.eye(4)

    def compute(self, dt: float) -> None:
        """."""
        sqr_dt2 = dt * dt / 2.0
        cub_dt6 = sqr_dt2 * dt / 3.0
        f_mat = self.f_mat
        f_mat[0, 1] = dt
        f_mat[0, 2] = sqr_dt2
        f_mat[0, 3] = cub_dt6
        f_mat[1, 2] = dt
        f_mat[1, 3] = sqr_dt2
        f_mat[2, 3] = dt
