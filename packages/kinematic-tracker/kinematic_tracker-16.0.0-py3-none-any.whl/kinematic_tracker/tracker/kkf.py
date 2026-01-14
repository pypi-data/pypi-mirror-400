"""Module for N-dimensional kinematic Kalman filtering.

This module provides the `NdKkf` class, which implements an N-dimensional
Kalman filter for kinematic tracking. It includes methods for prediction
and correction steps, leveraging the computation of the process-noise
covariance.
"""

import copy

from typing import Any

import numpy as np

from cv2 import KalmanFilter

from kinematic_tracker.core.kalman_cv2_copy import get_copy
from kinematic_tracker.nd.precursors import NdKkfPrecursors
from kinematic_tracker.proc_noise.nd_kkf_proc_noise_factory import TT_PN


class NdKkf:
    """N-dimensional kinematic Kalman filter.

    This class encapsulates the functionality of an N-dimensional kinematic Kalman
    filters handling several kinds of process-noise.
    """

    def __init__(self, kalman_filter: KalmanFilter, proc_noise: TT_PN) -> None:
        """Initialize the N-dimensional Kalman filter.

        Args:
            kalman_filter: An initialized OpenCV Kalman filter instance.
            proc_noise: An initialized process-noise driver.
        """
        self.proc_noise = proc_noise
        self.kalman_filter = kalman_filter

    def __repr__(self) -> str:
        """Return a string representation of the NdKkf instance.

        Returns:
            str: A string representation of the instance, including process noise details.
        """
        return f'NdKkf({self.proc_noise})'

    def __deepcopy__(self, memo: dict[str, Any]) -> 'NdKkf':
        """Create a deep copy of the NdKkf instance.

        Args:
            memo: A dictionary of objects already copied.

        Returns:
            NdKkf: A deep copy of the current instance.
        """
        return NdKkf(get_copy(self.kalman_filter), copy.deepcopy(self.proc_noise))

    def predict(self, pre: NdKkfPrecursors) -> None:
        """Perform the prediction step of the Kalman filter.

        This step updates the state prediction using the pre-computed
        1D kinematic matrices from the precursor and applying the current
        process-noise model.

        Args:
            pre: A kinematic-matrix precursor containing 1-dimensional fundamental
                 and white-noise matrices, calculated for the current time step `dt`.

        Note:
            The fundamental matrix in the precursor should already be computed
            before calling this method.

            The white-noise matrices are not used for the diagonal process-noise
            kind, but they should be computed for the other process-noise kinds.
        """
        self.proc_noise.fill_proc_cov(
            pre, self.kalman_filter.statePost[:, 0], self.kalman_filter.processNoiseCov
        )
        self.kalman_filter.predict()

    def correct(self, vec_z: np.ndarray) -> None:
        """Perform the correction step of the Kalman filter.

        This step updates the state estimate based on the provided measurement.

        Args:
            vec_z: The observation reading (measurement vector).
        """
        self.proc_noise.save_values(self.kalman_filter.statePre[:, 0])
        self.kalman_filter.correct(vec_z)
