"""
This module defines the class WhiteNoiseMatCp, which computes and keeps a white-noise
covariance matrix for a constant position model. The covariance matrix is useful as
covariance of the process noise, typically after scaling by a variance prefactor.
"""

import numpy as np


class WhiteNoiseMatCp:
    """."""

    def __init__(self) -> None:
        """."""
        self.q_mat = np.zeros((1, 1))

    def compute(self, dt: float) -> None:
        """."""
        q_mat = self.q_mat
        q_mat[0, 0] = dt
