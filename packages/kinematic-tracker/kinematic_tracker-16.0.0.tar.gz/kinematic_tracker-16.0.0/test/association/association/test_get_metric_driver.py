"""."""

import pytest

from kinematic_tracker.association.association import Association
from kinematic_tracker.association.association_metric import AssociationMetric
from kinematic_tracker.association.metric_giou_aligned import MetricGIoUAligned
from kinematic_tracker.association.metric_mahalanobis import MetricMahalanobis
from kinematic_tracker.association.metric_mean_dim_giou import MetricMeanDimGIoU
from kinematic_tracker.association.metric_size_modulated_mahalanobis import (
    MetricSizeModulatedMahalanobis,
)


def test_get_association_metric_driver(association: Association) -> None:
    """."""
    association.metric = AssociationMetric.MAHALANOBIS
    assert isinstance(association.get_metric_driver(), MetricMahalanobis)

    association.metric = AssociationMetric.GIOU
    assert isinstance(association.get_metric_driver(), MetricGIoUAligned)

    association.metric = AssociationMetric.SIZE_MODULATED_MAHALANOBIS
    assert isinstance(association.get_metric_driver(), MetricSizeModulatedMahalanobis)

    association.metric = AssociationMetric.MEAN_DIM_GIOU
    assert isinstance(association.get_metric_driver(), MetricMeanDimGIoU)

    association.metric = AssociationMetric.UNKNOWN_METRIC
    with pytest.raises(ValueError):
        association.get_metric_driver()
