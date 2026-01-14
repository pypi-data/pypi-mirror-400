"""
This module defines the `MetricDriverBase` class. The class provides a common functionality
for managing the computation of association metric (similarity scores) between
detection reports and tracked targets.
"""

from typing import Iterator

import numpy as np

from .det_type import FT, MT, VT


class MetricDriverBase:
    """
    A base class for handling metrics between reports and targets. It provides methods
    to initialize and retrieve rectangular contiguous chunks of similarity scores.

    Attributes:
        num_reports_max: Maximum number of reports allowed.
        num_targets_max: Maximum number of targets allowed.
        num_reports: Current number of reports.
        num_targets: Current number of targets.
        num_elements: Total number of elements in the metric matrix.
        metric_rt: A 2D buffer for the similarity scores.
        vec_z: A vertical vector used as buffer in GIoU and Mahalanobis.
    """

    def __init__(self, num_reports_max: int, num_targets_max: int, num_z: int) -> None:
        """
        Initializes the MetricDriverBase instance with the given maximum limits
        for reports, targets, and additional data.

        Args:
            num_reports_max: Maximum number of reports.
            num_targets_max: Maximum number of targets.
            num_z: Number of variables in the measurement vectors.
        """
        self.num_reports_max = num_reports_max
        self.num_targets_max = num_targets_max
        self.num_reports = 0
        self.num_targets = 0
        self.num_elements = 0
        self.metric_rt = np.zeros((num_reports_max, num_targets_max))
        self.vec_z = np.zeros((num_z, 1))

    def get_rect_chunk(self, num_r: int, num_t: int) -> MT:
        """
        Retrieves a rectangular contiguous chunk of the metric matrix located in
        the buffer are carved precisely to store the similarity score between
        a given number of reports and targets.

        Args:
            num_r: number of detection reports to include in the chunk.
            num_t: number of tracked targets to include in the chunk.

        Returns:
            np.ndarray: A 2D array representing the requested rectangular chunk.

        Raises:
            ValueError: If the number of reports exceeds `num_reports_max`.
            ValueError: If the number of targets exceeds `num_targets_max`.
        """
        self.num_reports = num_r
        self.num_targets = num_t
        self.num_elements = num_r * num_t
        if num_r > self.num_reports_max:
            raise ValueError(f'Too much reports? {num_r} {self.num_reports_max}')

        if num_t > self.num_targets_max:
            raise ValueError(f'Too much targets? {num_t} {self.num_targets_max}')
        flat_chunk = self.metric_rt.reshape(-1)[: self.num_elements]
        rect_chunk = flat_chunk.reshape(num_r, num_t)
        return rect_chunk

    def gen_vec_z(self, filters: FT) -> Iterator[VT]:
        for t, kf in enumerate(filters):
            np.dot(kf.measurementMatrix, kf.statePre, out=self.vec_z)
            yield self.vec_z[:, 0]
