"""
This module defines the class WhiteNoiseMatCv, which computes and keeps a white-noise
covariance matrix for a constant velocity model. The covariance matrix is useful as
covariance of the process noise, typically after scaling by a variance prefactor.
"""

import numpy as np


class WhiteNoiseMatCv:
    """
    A class to compute the white-noise covariance matrix.

    Attributes:
        q_mat: A 2x2 matrix initialized with zeros used as result buffer.
    """

    def __init__(self) -> None:
        """Initializes the class by creating a 2x2 zeros buffer."""
        self.q_mat = np.zeros((2, 2))

    def compute(self, dt: float) -> None:
        """Computes the white-noise covariance for the given time step.

        Args:
            dt: The time step used to compute the covariance matrix.
        """
        dt2 = dt * dt
        q_mat = self.q_mat
        q_mat[0, 0] = dt2 / 3
        q_mat[0, 1] = dt / 2
        q_mat[1, 0] = q_mat[0, 1]
        q_mat[1, 1] = 1.0
        q_mat *= dt
