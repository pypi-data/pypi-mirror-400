"""
This module defines the `MetricSizeModulatedMahalanobis` class.
The class extends the `MetricDriverBase` class to compute a size-modulated
Mahalanobis-distance similarity score.
"""

from typing import Sequence

import cv2
import numpy as np

from .det_type import DT, FT, MT
from .inv_out import inv_out
from .metric_driver_base import MetricDriverBase


class MetricSizeModulatedMahalanobis(MetricDriverBase):
    """
    A class for computing a size-modulated Mahalanobis distance-based metric for association
    of detection reports and targets represented by Kalman filters.
    It extends the `MetricDriverBase` class.

    Attributes:
        mah_pre_factor: pre-factor for scaling the Mahalanobis distance.
        tmp_zx: temporary rectangular matrix for intermediate calculations.
        cov_zz: covariance matrix for the sum of the covariances.
        inv_zz: inverse of the covariance matrix.
        num_z: dimensionality of the measurement space (number of detection variables).
        ind_pos_size: location of variables in the measurement vector.
        det_rz: buffer for detections
    """

    def __init__(
        self,
        num_reports_max: int,
        num_targets_max: int,
        mah_pre_factor: float,
        num_x: int,
        num_z: int,
        ind_pos_size: Sequence[int],
    ) -> None:
        """
        Initializes the MetricSizeModulatedMahalanobis instance with the given parameters.

        Args:
            num_reports_max: maximum number of reports.
            num_targets_max: maximum number of targets.
            mah_pre_factor: pre-factor for scaling the (square) of Mahalanobis distance.
            num_x: dimensionality of the state space used for allocating auxiliary buffers.
            num_z: dimensionality of the measurement space used for allocating auxiliary buffers.
            ind_pos_size: Location of variables in the measurement vector.
                          By default, the indices will be 0,1,2,-3,-2,-1, i.e.
                          the center of the cuboid is taken as first three variables
                          of the measurement vector and sizes (dimensions) of the
                          cuboids are taken from the last three variables.

        Raises:
            AssertionError: If `num_x` is less than `num_z`.
        """
        assert num_x >= num_z, f'Mixed up x and z? num_x = {num_x} < {num_z} = num_z'
        super().__init__(num_reports_max, num_targets_max, num_z)
        self.ind_pos_size = np.array(ind_pos_size, dtype=int)
        assert self.ind_pos_size.ndim == 1, 'Sequence of should be one-dimensional'
        assert self.ind_pos_size.size % 2 == 0, 'Number of positions and sizes should be the same'
        assert self.ind_pos_size.size <= num_z, 'Number variables should verify inequality'
        num_sizes = self.ind_pos_size.size // 2
        self.pos_ind = self.ind_pos_size[:num_sizes]
        self.size_ind = self.ind_pos_size[num_sizes:]
        self.mah_pre_factor = mah_pre_factor
        self.tmp_zx = np.zeros((num_z, num_x))
        self.cov_zz = np.zeros((num_z, num_z))
        self.inv_zz = np.zeros((num_z, num_z))
        self.num_z = num_z
        self.det_rz = np.zeros((self.num_reports_max, num_z))
        self.sizes_dia_cov_rs = np.zeros((self.num_reports_max, num_sizes))
        self.sizes_dia_cov_s = np.zeros(num_sizes)
        self.size_indices = (self.size_ind, self.size_ind)
        self.pos_indices = (self.pos_ind, self.pos_ind)

    def comp_sizes_dia_cov_rs(self, det_rz: DT) -> None:
        num_r = len(det_rz)
        if num_r > 0:
            np.copyto(self.det_rz[:num_r], det_rz)
            np.take(self.det_rz[:num_r], self.size_ind, axis=1, out=self.sizes_dia_cov_rs[:num_r])
            np.square(self.sizes_dia_cov_rs[:num_r], out=self.sizes_dia_cov_rs[:num_r])
            np.divide(self.sizes_dia_cov_rs[:num_r], 4, out=self.sizes_dia_cov_rs[:num_r])

    def compute_metric(self, det_rz: DT, filters: FT) -> MT:
        """
        Computes the Mahalanobis distance-based metric for associating detections
        with Kalman filters.

        Args:
            det_rz: the input sequence of detection reports (measurements).
            filters: the input sequence of Kalman filters representing the tracked targets.

        Returns:
            np.ndarray[tuple[int, int], float]: A 2D array containing the computed metrics.
            The array has shape (num_reports, num_targets) and located at the beginning
            of the (larger) `self.metric_rt` buffer.

        Raises:
            np.linalg.LinAlgError: If the covariance matrix is singular and cannot be inverted.
        """
        self.comp_sizes_dia_cov_rs(det_rz)

        rect_chunk = self.get_rect_chunk(len(det_rz), len(filters))
        for t, kf in enumerate(filters):
            np.dot(kf.measurementMatrix, kf.statePre, out=self.vec_z)
            np.square(self.vec_z[self.size_ind, 0], out=self.sizes_dia_cov_s)  # xxx tmp buf
            np.divide(self.sizes_dia_cov_s, 4, out=self.sizes_dia_cov_s)
            np.dot(kf.measurementMatrix, kf.errorCovPre, out=self.tmp_zx)
            np.dot(self.tmp_zx, kf.measurementMatrix.T, out=self.cov_zz)
            np.add.at(self.cov_zz, self.size_indices, self.sizes_dia_cov_s)
            np.add.at(self.cov_zz, self.pos_indices, self.sizes_dia_cov_s)
            np.add(self.cov_zz, kf.measurementNoiseCov, out=self.cov_zz)
            for r, det_z in enumerate(det_rz):
                np.add.at(self.cov_zz, self.size_indices, self.sizes_dia_cov_rs[r])
                np.add.at(self.cov_zz, self.pos_indices, self.sizes_dia_cov_rs[r])
                inv_out(self.cov_zz, self.inv_zz)
                sqr_distance = cv2.Mahalanobis(self.vec_z, det_z, self.inv_zz) ** 2
                rect_chunk[r, t] = sqr_distance
        rect_chunk *= self.mah_pre_factor / (2.0 * self.num_z)  # xxx what factor is better?
        rect_chunk[rect_chunk > 150.0] = 150
        np.exp(-rect_chunk, out=rect_chunk)
        return rect_chunk
