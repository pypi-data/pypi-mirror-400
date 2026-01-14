"""."""

import numpy as np
import pytest

from kinematic_tracker.association.det_type import DT
from kinematic_tracker.association.metric_mean_dim_giou import MetricMeanDimGIoU


def test_fill_det_len_min_max(det_rz: DT, driver: MetricMeanDimGIoU) -> None:
    driver.fill_det_len_min_max(det_rz, driver.len_rs, driver.min_rs, driver.max_rs)
    assert driver.len_rs[:2] == pytest.approx(np.array([[4.0, 5.0, 6.0], [5.0, 6.0, 7.0]]))
    assert driver.len_rs[2:] == pytest.approx(0.0)
    assert driver.min_rs[:2] == pytest.approx(np.array([[-1.0, -0.5, 0.0], [-0.5, 0.0, 0.5]]))
    assert driver.min_rs[2:] == pytest.approx(0.0)
    assert driver.max_rs[2:] == pytest.approx(0.0)
    assert driver.max_rs[:2] == pytest.approx(np.array([[3.0, 4.5, 6.0], [4.5, 6.0, 7.5]]))
