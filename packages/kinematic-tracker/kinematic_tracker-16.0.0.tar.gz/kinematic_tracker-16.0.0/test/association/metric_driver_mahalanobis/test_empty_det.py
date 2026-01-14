"""."""

import cv2

from kinematic_tracker.association.metric_mahalanobis import MetricMahalanobis


def test_empty_det(filters: list[cv2.KalmanFilter], driver: MetricMahalanobis) -> None:
    metric = driver.compute_metric([], filters)
    assert metric.shape == (0, 3)
