"""."""

import cv2
import numpy as np

from kinematic_tracker.association.metric_mean_dim_giou import MetricMeanDimGIoU


def test_normal(filters: list[cv2.KalmanFilter], driver: MetricMeanDimGIoU) -> None:
    det_rz = [(1, 2, 3, 4, 5, 6), (2, 12, 13, 4, 5, 6)]
    metric = driver.compute_metric(det_rz, filters)
    ref = [
        [1.0, 0.8436674436674436, 0.7473544973544973],
        [0.5027777777777778, 0.5662217278457545, 0.5761904761904763],
    ]
    assert np.allclose(metric, ref)
