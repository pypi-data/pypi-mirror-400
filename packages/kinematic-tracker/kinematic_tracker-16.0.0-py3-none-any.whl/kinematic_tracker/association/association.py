"""
This module defines the `Association` class. The `Association` class holds
parameters to for computing an association metric (scores) and for computing
the bipartite matching between (detection) reports and (tracked) targets.
Apart from the parameter storage, the class provides methods to generate
the metric and match drivers based on the selected types of metric and
matching method.
"""

from typing import Sequence, Union

from .association_method import AssociationMethod
from .association_metric import AssociationMetric
from .match_greedy import MatchDriverGreedy
from .match_hungarian import MatchDriverHungarian
from .metric_giou_aligned import MetricGIoUAligned
from .metric_mahalanobis import MetricMahalanobis
from .metric_mean_dim_giou import MetricMeanDimGIoU
from .metric_size_modulated_mahalanobis import MetricSizeModulatedMahalanobis


MDT = Union[MetricMahalanobis, MetricGIoUAligned, MetricSizeModulatedMahalanobis, MetricMeanDimGIoU]


class Association:
    """
    Represents an association mechanism for matching reports and targets
    using configurable metrics and methods. Generates metric and match drivers.
    """

    def __init__(
        self, num_x: int, num_z: int, ind_pos_size: Sequence[int] = (0, 1, 2, -3, -2, -1)
    ) -> None:
        """
        Initializes the `Association` object with default parameters.

        Args:
            num_x: Number of variables in the state vector.
            num_z: Number of variables in the measurement vector.
            ind_pos_size: indices to get positions and sizes of cuboids for GIoU.
                          By default, the indices will be 0,1,2,-3,-2,-1, i.e.
                          the center of the cuboid is taken as first three variables
                          of the measurement vector and sizes (dimensions) of the
                          cuboids are taken from the last three variables.
        """
        self.threshold = 0.25  # Threshold for association
        self.mah_pre_factor = 1.0  # Pre-factor for Mahalanobis distance
        self.method = AssociationMethod.HUNGARIAN  # Default matching method
        self.metric = AssociationMetric.MAHALANOBIS  # Default association metric
        self.num_reports_max = 100  # Maximum number of reports
        self.num_targets_max = 500  # Maximum number of targets
        self.num_x = num_x  # State vector dimensionality
        self.num_z = num_z  # Measurement vector dimensionality
        self.ind_pos_size = ind_pos_size  # Distribution of variables in the measurement vector.

    def __repr__(self) -> str:
        """
        Returns a string representation of the `Association` object.

        Returns:
            str: A string describing the association configuration.
        """
        return (
            f'Association({self.method.value} '
            f'{self.metric.value} '
            f'threshold {self.threshold} '
            f'mah_pre_factor {self.mah_pre_factor})'
        )

    def get_metric_driver(self) -> MDT:
        """
        Initializes and returns the metric driver based on the selected metric type.

        Returns:
            MetricMahalanobis | MetricGIoUAligned: The metric driver instance.

        Raises:
            ValueError: If the metric is not supported.
        """
        if self.metric == AssociationMetric.MAHALANOBIS:
            return MetricMahalanobis(
                self.num_reports_max,
                self.num_targets_max,
                self.mah_pre_factor,
                self.num_x,
                self.num_z,
            )
        elif self.metric == AssociationMetric.GIOU:
            return MetricGIoUAligned(
                self.num_reports_max, self.num_targets_max, self.num_z, self.ind_pos_size
            )
        elif self.metric == AssociationMetric.SIZE_MODULATED_MAHALANOBIS:
            return MetricSizeModulatedMahalanobis(
                self.num_reports_max,
                self.num_targets_max,
                self.mah_pre_factor,
                self.num_x,
                self.num_z,
                self.ind_pos_size,
            )
        elif self.metric == AssociationMetric.MEAN_DIM_GIOU:
            return MetricMeanDimGIoU(
                self.num_reports_max, self.num_targets_max, self.num_z, self.ind_pos_size
            )
        else:
            raise ValueError('Unsupported metric.')

    def get_match_driver(self) -> MatchDriverGreedy | MatchDriverHungarian:
        """
        Initializes and returns the match driver based on the selected matching method.

        Returns:
            MatchDriverGreedy | MatchDriverHungarian: The match driver instance.

        Raises:
            ValueError: If the method is not supported.
        """
        method = self.method
        if method == AssociationMethod.GREEDY:
            return MatchDriverGreedy(self.num_reports_max, self.num_targets_max)
        elif method == AssociationMethod.HUNGARIAN:
            return MatchDriverHungarian(self.num_reports_max, self.num_targets_max)
        else:
            raise ValueError('Unsupported matching method.')
