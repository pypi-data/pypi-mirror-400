"""."""

import cv2

from kinematic_tracker.association.metric_size_modulated_mahalanobis import (
    MetricSizeModulatedMahalanobis,
)


def test_no_det(filters: list[cv2.KalmanFilter], driver: MetricSizeModulatedMahalanobis) -> None:
    metric = driver.compute_metric([], filters)
    assert metric.shape == (0, 3)
