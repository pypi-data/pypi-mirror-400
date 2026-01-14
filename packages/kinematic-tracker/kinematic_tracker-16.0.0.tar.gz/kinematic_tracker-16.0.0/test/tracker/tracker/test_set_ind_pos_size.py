"""."""

import pytest

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_set_ind_pos_size(tracker1: NdKkfTracker) -> None:
    """."""
    tracker1.set_association_metric('giou')
    assert len(tracker1.tracks) == 1
    assert tracker1.metric_driver.ind_pos_size == pytest.approx((0, 1, 2, -3, -2, -1))
    tracker1.set_ind_pos_size((0, 1, 2, 3, 4, 5))
    assert len(tracker1.tracks) == 0
    assert tracker1.metric_driver.ind_pos_size == pytest.approx((0, 1, 2, 3, 4, 5))
