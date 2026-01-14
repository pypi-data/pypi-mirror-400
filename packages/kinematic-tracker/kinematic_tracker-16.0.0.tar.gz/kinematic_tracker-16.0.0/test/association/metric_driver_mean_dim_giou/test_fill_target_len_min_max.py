"""."""

import numpy as np
import pytest

from kinematic_tracker.association.metric_mean_dim_giou import MetricMeanDimGIoU


def test_fill_target_len_min_max(driver: MetricMeanDimGIoU) -> None:
    vec_z = np.linspace(1.0, 6.0, num=6)
    driver.fill_target_len_min_max(vec_z, driver.len_s, driver.min_s, driver.max_s)
    assert driver.len_s == pytest.approx([4.0, 5.0, 6.0])
    assert driver.min_s == pytest.approx([-1.0, -0.5, 0.0])
    assert driver.max_s == pytest.approx([3.0, 4.5, 6.0])
