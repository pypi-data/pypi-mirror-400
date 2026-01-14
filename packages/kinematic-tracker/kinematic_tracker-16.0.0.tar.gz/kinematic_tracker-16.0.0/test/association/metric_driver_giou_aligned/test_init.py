"""."""

import pytest

from kinematic_tracker.association.metric_giou_aligned import MetricGIoUAligned


def test_init(driver: MetricGIoUAligned) -> None:
    assert driver.aux_r.shape == (100,)


def test_num_z_ge_6() -> None:
    with pytest.raises(AssertionError):
        MetricGIoUAligned(10, 10, 5, (0, 1, 2, -3, -2, -1))
