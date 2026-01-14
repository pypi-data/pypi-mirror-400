"""."""

import pytest

from kinematic_tracker.association.metric_giou_aligned import MetricGIoUAligned
from kinematic_tracker.association.metric_mahalanobis import MetricMahalanobis
from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_at_start(tracker: NdKkfTracker) -> None:
    """."""
    assert isinstance(tracker.metric_driver, MetricMahalanobis)


def test_set_association_metric_iou(tracker: NdKkfTracker) -> None:
    """."""
    tracker.set_association_metric('giou')
    assert isinstance(tracker.metric_driver, MetricGIoUAligned)
    assert tracker.association.mah_pre_factor == pytest.approx(1.0)


def test_set_association_metric_mahalanobis(tracker: NdKkfTracker) -> None:
    """."""
    tracker.set_association_metric('mahalanobis', 0.567)
    assert isinstance(tracker.metric_driver, MetricMahalanobis)
    assert tracker.association.mah_pre_factor == pytest.approx(0.567)
