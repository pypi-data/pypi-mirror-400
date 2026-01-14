"""."""

from kinematic_tracker.association.metric_driver_base import MetricDriverBase


def test_metric_driver_base_init(driver: MetricDriverBase) -> None:
    assert driver.metric_rt.shape == (4, 5)
    assert driver.vec_z.shape == (6, 1)
