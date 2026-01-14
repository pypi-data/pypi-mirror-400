"""
This module defines the `MetricMahalanobis` class. The class extends the `MetricDriverBase` class
to compute Mahalanobis-distance similarity score.
"""

import cv2
import numpy as np

from .det_type import DT, FT, MT
from .inv_out import inv_out
from .metric_driver_base import MetricDriverBase


class MetricMahalanobis(MetricDriverBase):
    """
    A class for computing Mahalanobis distance-based metrics for associating detections
    targets represented by Kalman filters. It extends the `MetricDriverBase` class.

    Attributes:
        mah_pre_factor: Pre-factor for scaling the Mahalanobis distance.
        tmp_zx: Temporary rectangular matrix for intermediate calculations.
        cov_zz: Covariance matrix for the sum of the covariances.
        inv_zz: Inverse of the covariance matrix.
        num_z: Dimensionality of the measurement space (number of detection variables).
    """

    def __init__(
        self,
        num_reports_max: int,
        num_targets_max: int,
        mah_pre_factor: float,
        num_x: int,
        num_z: int,
    ) -> None:
        """
        Initializes the MetricMahalanobis instance with the given parameters.

        Args:
            num_reports_max: Maximum number of reports.
            num_targets_max: Maximum number of targets.
            mah_pre_factor: Pre-factor for scaling the (square) of Mahalanobis distance.
            num_x: Dimensionality of the state space used for allocating auxiliary buffers.
            num_z: Dimensionality of the measurement space used for allocating auxiliary buffers.

        Raises:
            AssertionError: If `num_x` is less than `num_z`.
        """
        assert num_x >= num_z, f'Mixed up x and z? num_x = {num_x} < {num_z} = num_z'
        super().__init__(num_reports_max, num_targets_max, num_z)
        self.mah_pre_factor = mah_pre_factor
        self.tmp_zx = np.zeros((num_z, num_x))
        self.cov_zz = np.zeros((num_z, num_z))
        self.inv_zz = np.zeros((num_z, num_z))
        self.num_z = num_z

    def compute_metric(self, det_rz: DT, filters: FT) -> MT:
        """
        Computes the Mahalanobis distance-based metric for associating detections
        with Kalman filters.

        Args:
            det_rz: The input sequence of detection reports (measurements).
            filters: The input sequence of Kalman filters representing the tracked targets.

        Returns:
            np.ndarray[tuple[int, int], float]: A 2D array containing the computed metrics.
            The array has shape (num_reports, num_targets) and located at the beginning
            of the (larger) `self.metric_rt` buffer.

        Raises:
            np.linalg.LinAlgError: If the covariance matrix is singular and cannot be inverted.
        """
        rect_chunk = self.get_rect_chunk(len(det_rz), len(filters))
        for t, kf in enumerate(filters):
            np.dot(kf.measurementMatrix, kf.statePre, out=self.vec_z)
            np.dot(kf.measurementMatrix, kf.errorCovPre, out=self.tmp_zx)
            np.dot(self.tmp_zx, kf.measurementMatrix.T, out=self.cov_zz)
            np.add(self.cov_zz, kf.measurementNoiseCov, out=self.cov_zz)
            # detection does not have its noise covariance...

            inv_out(self.cov_zz, self.inv_zz)

            for r, det_z in enumerate(det_rz):
                sqr_distance = cv2.Mahalanobis(self.vec_z, det_z, self.inv_zz) ** 2
                rect_chunk[r, t] = sqr_distance
        rect_chunk *= self.mah_pre_factor / (2.0 * self.num_z)
        rect_chunk[rect_chunk > 150.0] = 150
        np.exp(-rect_chunk, out=rect_chunk)
        return rect_chunk
