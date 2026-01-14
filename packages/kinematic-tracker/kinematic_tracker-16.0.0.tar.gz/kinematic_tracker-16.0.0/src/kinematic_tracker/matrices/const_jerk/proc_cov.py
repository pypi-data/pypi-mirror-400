"""
This module defines the class WhiteNoiseMatCj, which computes and keeps a white-noise
covariance matrix for a constant-jerk point-motion. The covariance matrix is useful as
covariance of the process noise, typically after scaling by a variance prefactor.
"""

import numpy as np


class WhiteNoiseMatCj:
    """."""

    def __init__(self) -> None:
        """."""
        self.q_mat = np.zeros((4, 4))

    def compute(self, dt: float) -> None:
        """."""
        q_mat = self.q_mat
        dt2 = dt * dt
        dt3 = dt2 * dt
        dt4 = dt3 * dt
        dt5 = dt4 * dt
        dt6 = dt5 * dt
        q_mat[0, 0] = dt6 / 252
        q_mat[0, 1] = dt5 / 72
        q_mat[0, 2] = dt4 / 30
        q_mat[0, 3] = dt3 / 24
        q_mat[1, 0] = q_mat[0, 1]
        q_mat[1, 1] = dt4 / 20
        q_mat[1, 2] = dt3 / 8
        q_mat[1, 3] = dt2 / 6
        q_mat[2, 0] = q_mat[0, 2]
        q_mat[2, 1] = q_mat[1, 2]
        q_mat[2, 2] = dt2 / 3
        q_mat[2, 3] = dt / 2
        q_mat[3, 0] = q_mat[0, 3]
        q_mat[3, 1] = q_mat[1, 3]
        q_mat[3, 2] = q_mat[2, 3]
        q_mat[3, 3] = 1.0
        q_mat *= dt
