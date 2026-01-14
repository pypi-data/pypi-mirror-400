"""."""

import cv2
import numpy as np
import pytest

from kinematic_tracker.association.det_type import DT
from kinematic_tracker.association.metric_mahalanobis import MetricMahalanobis


def test_compute(det_rz: DT, filters: list[cv2.KalmanFilter], driver: MetricMahalanobis) -> None:
    metric = driver.compute_metric(det_rz, filters)
    ref = [
        [1.0, 0.9048374180359595],
        [0.9200444146293233, 1.0],
        [0.751477293075286, 0.9310627797040227],
    ]
    assert metric == pytest.approx(np.array(ref).T)
    assert np.shares_memory(metric, driver.metric_rt)


def test_wrong_inv(det_rz: DT, driver: MetricMahalanobis) -> None:
    kf = cv2.KalmanFilter(12, 6, 0, cv2.CV_64F)
    kf.errorCovPre = np.ones((12, 12))
    kf.measurementMatrix = np.eye(6, 12)
    kf.measurementNoiseCov = np.zeros((6, 6))
    with pytest.raises(np.linalg.LinAlgError):
        driver.compute_metric(det_rz, [kf])
