"""
This module defines the class WhiteNoiseMatCa, which computes and keeps a white-noise
covariance matrix for a constant-acceleration point-motion. The covariance matrix is useful as
covariance of the process noise, typically after scaling by a variance prefactor.
"""

import numpy as np


class WhiteNoiseMatCa:
    """."""

    def __init__(self) -> None:
        """."""
        self.q_mat = np.zeros((3, 3))

    def compute(self, dt: float) -> None:
        """."""
        mat = self.q_mat
        sqr = dt * dt
        cub = sqr * dt
        qua = cub * dt
        mat[0, :] = qua / 20, cub / 8, sqr / 6
        mat[1, :] = mat[0, 1], sqr / 3, dt / 2
        mat[2, :] = mat[0, 2], mat[1, 2], 1
        mat *= dt
