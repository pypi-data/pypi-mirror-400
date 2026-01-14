"""."""

import cv2

from kinematic_tracker.association.metric_mean_dim_giou import MetricMeanDimGIoU


def test_empty_det(filters: list[cv2.KalmanFilter], driver: MetricMeanDimGIoU) -> None:
    metric = driver.compute_metric([], filters)
    assert metric.shape == (0, 3)
