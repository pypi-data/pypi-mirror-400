"""."""

import cv2
import numpy as np
import pytest

from kinematic_tracker.association.metric_giou_aligned import DT, FT, MetricGIoUAligned


@pytest.fixture
def filters() -> list[cv2.KalmanFilter]:
    """."""
    kf = cv2.KalmanFilter(16, 10, 0, cv2.CV_64F)
    kf.measurementMatrix = np.eye(10, 16)
    kf.statePre = np.linspace(1.0, 16.0, num=16).reshape(16, 1)
    vec_x = np.array(
        (1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 4.0, 5.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0)
    ).reshape(16, 1)
    kf.statePre = vec_x
    filters = [kf]

    kf2 = cv2.KalmanFilter(16, 10, 0, cv2.CV_64F)
    kf2.measurementMatrix = np.eye(10, 16)
    vec_x = np.array(
        (2.0, 3.0, 4.0, 0.0, 0.0, 0.0, 0.0, 5.0, 6.0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0)
    ).reshape(16, 1)
    kf2.statePre = vec_x
    filters.append(kf2)

    kf3 = cv2.KalmanFilter(16, 10, 0, cv2.CV_64F)
    kf3.measurementMatrix = np.eye(10, 16)
    vec_x = np.array(
        (3.0, 4.0, 5.0, 0.0, 0.0, 0.0, 0.0, 6.0, 7.0, 8.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0)
    ).reshape(16, 1)
    kf3.statePre = vec_x
    filters.append(kf3)

    return filters


@pytest.fixture
def det_rz() -> list[np.ndarray]:
    """."""
    vec_z1 = np.array((1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 4.0, 5.0, 6.0))
    vec_z2 = np.array((2.0, 3.0, 4.0, 0.0, 0.0, 0.0, 0.0, 5.0, 6.0, 7.0))
    return [vec_z1, vec_z2]


def test_at_end(det_rz: DT, filters: FT) -> None:
    """."""
    driver = MetricGIoUAligned(100, 500, 10, (0, 1, 2, -3, -2, -1))
    assert driver.ind_pos_size == pytest.approx((0, 1, 2, -3, -2, -1))
    assert driver.ind_pos_size.dtype == int
    metric = driver.compute_metric(det_rz, filters)
    ref = [
        [1.0, 0.6318122555410691],
        [0.6318122555410691, 1.0],
        [0.4686147186147186, 0.6735666418466121],
    ]
    assert metric == pytest.approx(np.array(ref).T)
    assert np.shares_memory(metric, driver.metric_rt)
