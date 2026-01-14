"""."""

import pytest

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_init_no_measurement_orders() -> None:
    """."""
    tracker = NdKkfTracker([3, 1], [3, 3])
    assert tracker.cov_zz is None
    assert tracker.gen_xz.orders_z == pytest.approx([1, 1])
    assert tracker.gen_xz.gen_x.num_x == 12
    assert tracker.gen_xz.num_z == 6

    assert tracker.match_driver.num_reports_max == 100
    assert tracker.match_driver.num_targets_max == 500
    assert tracker.metric_driver.num_reports_max == 100
    assert tracker.metric_driver.num_targets_max == 500


def test_nd_kkf_tracker_init_with_measurement_orders() -> None:
    """."""
    tracker = NdKkfTracker([3, 1], [3, 3], [2, 1])
    assert tracker.cov_zz is None
    assert tracker.gen_xz.orders_z == pytest.approx([2, 1])
    assert tracker.gen_xz.gen_x.num_x == 12
    assert tracker.gen_xz.num_z == 9


def test_nd_kkf_tracker_repr(tracker: NdKkfTracker) -> None:
    """."""
    ref = """NdKkfTracker(
    Association(greedy mahalanobis threshold 0.56 mah_pre_factor 1.32)
    num_misses_max 3
    num_det_min 2)"""
    assert repr(tracker) == ref
