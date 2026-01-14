"""The module for computing an averaged over dimensions GIoU association metric.

This module provides functionality for computing the similarity score between detection reports
and Kalman filter states (targets) using a within-dimensions average GIoU metric.
Due to its simplicity, the metric can be computed between objects of any dimensionality.

The resulting rectangular matrix will have a shape of (num_reports, num_targets), and located
at the beginning of the pre-allocated buffer `metric_rt` of the base class `MetricDriverBase`.
The resulting matrix is contiguous in memory.

Classes:
    MetricMeanDimGIoU: Computes GIoU-based association metrics between detections
                       and Kalman filter states in any dimensions.
"""

from typing import Sequence

import numpy as np

from .det_type import DT, FT, MT, VT
from .metric_driver_base import MetricDriverBase


class MetricMeanDimGIoU(MetricDriverBase):
    """Computes GIoU-based association metrics between detections and Kalman filter states.

    This class inherits from MetricDriverBase and implements GIoU-based metric computation
    for data association between detection reports and Kalman filter states. The computation
    is performed between cuboids of any dimensionality (segments, rectangles or cuboids).

    Args:
        num_reports_max: maximum number of detection reports to handle.
        num_targets_max: maximum number of targets (Kalman filters) to handle.
        num_z: number of variables in the measurement vector.
    """

    def __init__(
        self, num_reports_max: int, num_targets_max: int, num_z: int, ind_pos_size: Sequence[int]
    ) -> None:
        """Initialize the MetricMeanDimGIoU instance.

        Args:
            num_reports_max: maximum number of detection reports to handle.
            num_targets_max: maximum number of targets (Kalman filters) to handle.
            num_z: number of variables in the measurement vector.
            ind_pos_size: location of variables in the measurement vector.
                          By default, the indices should be 0,1,2,-3,-2,-1, i.e.
                          the center of the cuboid is taken as first three variables
                          of the measurement vector and sizes (dimensions) of the
                          cuboids are taken from the last three variables.
        """
        super().__init__(num_reports_max, num_targets_max, num_z)
        assert len(ind_pos_size) % 2 == 0, 'The number of indices should be even.'
        self.ind_pos_size = np.array(ind_pos_size, dtype=int)
        assert self.ind_pos_size.ndim == 1, 'Indices should be one-dimensional.'
        self.ns = self.ind_pos_size.size // 2
        self.pos_ind = self.ind_pos_size[: self.ns]
        self.size_ind = self.ind_pos_size[self.ns :]
        self.det_rz = np.zeros((self.num_reports_max, num_z))
        self.len_s: VT = np.zeros(self.ns)
        self.half_len_s: VT = np.zeros(self.ns)
        self.min_s: VT = np.zeros(self.ns)
        self.max_s: VT = np.zeros(self.ns)
        self.len_rs: MT = np.zeros((self.num_reports_max, self.ns))
        self.half_len_rs: MT = np.zeros((self.num_reports_max, self.ns))
        self.min_rs: MT = np.zeros((self.num_reports_max, self.ns))
        self.max_rs: MT = np.zeros((self.num_reports_max, self.ns))

    def fill_target_len_min_max(self, vec_z: VT, len_s: VT, min_s: VT, max_s: VT) -> None:
        np.take(vec_z, self.size_ind, out=len_s)
        np.take(vec_z, self.pos_ind, out=min_s)
        np.take(vec_z, self.pos_ind, out=max_s)
        np.multiply(len_s, 0.5, out=self.half_len_s)
        min_s -= self.half_len_s
        max_s += self.half_len_s

    def fill_det_len_min_max(self, det_rz: DT, len_rs: MT, min_rs: MT, max_rs: MT) -> None:
        nr = len(det_rz)
        if nr < 1:
            return

        det_lz, len_ls, half_len_ls = self.det_rz[:nr], len_rs[:nr], self.half_len_rs[:nr]
        np.copyto(det_lz, det_rz)  # det_lz is the output buffer
        np.take(det_lz, self.size_ind, axis=1, out=len_ls)
        np.take(det_lz, self.pos_ind, axis=1, out=min_rs[:nr])
        np.take(det_lz, self.pos_ind, axis=1, out=max_rs[:nr])
        np.multiply(len_ls, 0.5, out=half_len_ls)
        min_rs[:nr] -= half_len_ls
        max_rs[:nr] += half_len_ls

    def compute_metric(self, det_rz: DT, filters: FT) -> MT:
        """Compute the metric between detections and Kalman filter states.

        Args:
            det_rz: Detection measurements, either as a sequence of numpy arrays
                    or a single (2D) numpy array containing measurement vectors.
            filters: Sequence of OpenCV KalmanFilter objects representing tracked targets.

        Returns:
            np.ndarray: A matrix of GIoU scores between each detection-target pair,
                with shape (num_detections, num_targets).
        """
        self.fill_det_len_min_max(det_rz, self.len_rs, self.min_rs, self.max_rs)
        nr = len(det_rz)
        rect_chunk = self.get_rect_chunk(nr, len(filters))
        if nr < 1:
            return rect_chunk
        len_rs, min_rs, max_rs = self.len_rs[:nr], self.min_rs[:nr], self.max_rs[:nr]

        # Fighter-jet nightmare below
        inter_start_rs = np.zeros((nr, self.ns))
        inter_end_rs = np.zeros((nr, self.ns))
        intersection_rs = np.zeros((nr, self.ns))
        union_rs = np.zeros((nr, self.ns))
        iou_rs = np.zeros((nr, self.ns))

        hull_start_rs = np.zeros((nr, self.ns))
        hull_end_rs = np.zeros((nr, self.ns))
        hull_len_rs = np.zeros((nr, self.ns))
        diff_rs = np.zeros((nr, self.ns))
        ratio_rs = np.zeros((nr, self.ns))

        giou_rs = np.zeros((nr, self.ns))

        for t, vec_z in enumerate(self.gen_vec_z(filters)):
            self.fill_target_len_min_max(vec_z, self.len_s, self.min_s, self.max_s)
            np.maximum(self.min_s, min_rs, out=inter_start_rs)
            np.minimum(self.max_s, max_rs, out=inter_end_rs)
            np.subtract(inter_end_rs, inter_start_rs, out=intersection_rs)
            np.maximum(0.0, intersection_rs, out=intersection_rs)
            np.add(self.len_s, len_rs, out=union_rs)
            np.subtract(union_rs, intersection_rs, out=union_rs)
            iou_rs.fill(0.0)
            np.divide(intersection_rs, union_rs, out=iou_rs, where=union_rs > 0)

            np.minimum(self.min_s, min_rs, out=hull_start_rs)
            np.maximum(self.max_s, max_rs, out=hull_end_rs)
            np.subtract(hull_end_rs, hull_start_rs, out=hull_len_rs)
            np.maximum(0.0, hull_len_rs, out=hull_len_rs)
            np.subtract(hull_len_rs, union_rs, out=diff_rs)
            np.divide(diff_rs, hull_len_rs, out=ratio_rs)
            np.subtract(iou_rs, ratio_rs, out=giou_rs)
            giou_rs += 1.0
            giou_rs /= 2.0
            np.mean(giou_rs, axis=1, out=rect_chunk[:, t])
        return rect_chunk
