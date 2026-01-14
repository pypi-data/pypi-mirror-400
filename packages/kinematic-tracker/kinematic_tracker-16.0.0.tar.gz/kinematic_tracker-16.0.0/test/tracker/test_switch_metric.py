"""."""

from kinematic_tracker.association.association_metric import AssociationMetric
from kinematic_tracker.association.metric_size_modulated_mahalanobis import (
    MetricSizeModulatedMahalanobis,
)
from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_switch_metric() -> None:
    """."""
    tracker = NdKkfTracker([2, 2], [2, 2])
    name = AssociationMetric.SIZE_MODULATED_MAHALANOBIS.value
    tracker.set_association_metric(name, ind_pos_size=(0, 1, 2, 3))
    assert isinstance(tracker.metric_driver, MetricSizeModulatedMahalanobis)
