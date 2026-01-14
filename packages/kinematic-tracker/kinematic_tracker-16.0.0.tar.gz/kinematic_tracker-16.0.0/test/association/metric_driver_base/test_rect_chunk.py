"""."""

import numpy as np
import pytest

from kinematic_tracker.association.metric_driver_base import MetricDriverBase


def test_metric_driver_base_get_rect_chunk(driver: MetricDriverBase) -> None:
    rect_chunk = driver.get_rect_chunk(2, 3)
    assert rect_chunk.shape == (2, 3)
    assert np.shares_memory(rect_chunk, driver.metric_rt)
    driver.metric_rt[:] = 9
    rect_chunk[:] = np.linspace(1.0, 6.0, num=6).reshape((2, 3))
    # fmt: off
    ref = [1., 2., 3., 4., 5., 6., 9., 9., 9., 9., 9., 9., 9., 9., 9., 9., 9., 9., 9., 9.]
    # fmt: on
    assert ref == pytest.approx(driver.metric_rt.flatten())


def test_get_rect_chunk_exceptions(driver: MetricDriverBase) -> None:
    with pytest.raises(ValueError):
        driver.get_rect_chunk(5, 3)

    with pytest.raises(ValueError):
        driver.get_rect_chunk(3, 6)
