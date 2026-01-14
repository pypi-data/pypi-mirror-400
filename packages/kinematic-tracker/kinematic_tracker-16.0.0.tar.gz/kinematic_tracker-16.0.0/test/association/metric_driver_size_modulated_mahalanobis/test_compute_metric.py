"""."""

import cv2
import numpy as np
import pytest

from kinematic_tracker.association.metric_size_modulated_mahalanobis import (
    DT,
    MetricSizeModulatedMahalanobis,
)


def test_compute_metric(
    det_rz: DT, filters: list[cv2.KalmanFilter], driver: MetricSizeModulatedMahalanobis
) -> None:
    metric = driver.compute_metric(det_rz, filters)
    ref = [
        [1.0, 0.9706538336790667, 0.9059403058024592],
        [0.976089688786271, 1.0, 0.9817836396190168],
    ]
    assert metric == pytest.approx(np.array(ref))
    assert np.shares_memory(metric, driver.metric_rt)
