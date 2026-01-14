"""The module for computing Generalized Intersection over Union (GIoU) association metric.

This module provides functionality for computing the similarity score between detection reports
and Kalman filter states (targets) using the Generalized Intersection over Union (GIoU) metric.
The metric is computed between the 3D bounding boxes which are aligned with Cartesian axes.

The resulting rectangular matrix will have a shape of (num_reports, num_targets), and located
at the beginning of the pre-allocated buffer `metric_rt` of the base class `MetricDriverBase`.
The resulting matrix is contiguous in memory.

Classes:
    MetricGIoUAligned: Computes GIoU-based association metrics between detections
        and Kalman filter states in aligned coordinate space.
"""

from typing import Sequence

import numpy as np

from .det_type import DT, FT, MT
from .g_iou_scores_aligned import GIoUAux
from .metric_driver_base import MetricDriverBase


class MetricGIoUAligned(MetricDriverBase):
    """Computes GIoU-based association metrics between detections and Kalman filter states.

    This class inherits from MetricDriverBase and implements GIoU-based metric computation
    for data association between detection reports and Kalman filter states. The computation
    is performed between cuboids (3D bounding boxes) aligned with Cartesian axes.

    Attributes:
        aux_r: numpy array of helper object for detection reports.
        target_aux: Helper object for processing Kalman filter states (targets).

    Args:
        num_reports_max: Maximum number of detection reports to handle.
        num_targets_max: Maximum number of targets (Kalman filters) to handle.
        num_z: Dimension of the measurement vector.
    """

    def __init__(
        self, num_reports_max: int, num_targets_max: int, num_z: int, ind_pos_size: Sequence[int]
    ) -> None:
        """Initialize the MetricGIoUAligned instance.

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
        assert num_z > 5, 'Number of variables should be 6 or greater.'
        super().__init__(num_reports_max, num_targets_max, num_z)
        self.ind_pos_size = np.array(ind_pos_size, dtype=int)
        assert self.ind_pos_size.ndim == 1, 'Indices should be one-dimensional.'
        assert self.ind_pos_size.size == 6, 'There should be 6 fancy indices.'
        self.vec_pos_size = np.zeros(6)
        self.aux_r = np.empty(num_reports_max, dtype=object)
        self.aux_r[:] = [GIoUAux() for _ in range(num_reports_max)]
        self.target_aux = GIoUAux()

    def comp_report_aux(self, det_rz: DT) -> None:
        """Compute the GIoU helper structures.

        Args:
            det_rz: detection reports.
        """
        for r, det_z in enumerate(det_rz):
            np.take(det_z, indices=self.ind_pos_size, out=self.vec_pos_size)
            self.aux_r[r].set_vec_z(self.vec_pos_size)

    def compute_metric(self, det_rz: DT, filters: FT) -> MT:
        """Compute GIoU-based metrics between detections and Kalman filter states.

        Args:
            det_rz: Detection measurements, either as a sequence of numpy arrays
                or a single numpy array containing measurement vectors.
            filters: Sequence of OpenCV KalmanFilter objects representing tracked targets.

        Returns:
            np.ndarray: A matrix of GIoU scores between each detection-target pair,
                with shape (num_detections, num_targets).
        """
        nr = len(det_rz)
        rect_chunk = self.get_rect_chunk(nr, len(filters))
        self.comp_report_aux(det_rz)
        for t, vec_z in enumerate(self.gen_vec_z(filters)):
            np.take(vec_z, self.ind_pos_size, out=self.vec_pos_size)
            self.target_aux.set_vec_z(self.vec_pos_size)
            for r, report_aux in enumerate(self.aux_r[:nr]):
                rect_chunk[r, t] = self.target_aux.get_g_iou(report_aux)
        return rect_chunk
