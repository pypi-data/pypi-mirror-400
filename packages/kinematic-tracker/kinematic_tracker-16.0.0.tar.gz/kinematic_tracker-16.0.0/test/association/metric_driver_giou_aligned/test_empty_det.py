"""."""

from kinematic_tracker.association.metric_giou_aligned import FT, MetricGIoUAligned


def test_empty_det(filters: FT, driver: MetricGIoUAligned) -> None:
    metric = driver.compute_metric([], filters)
    assert metric.shape == (0, 3)
