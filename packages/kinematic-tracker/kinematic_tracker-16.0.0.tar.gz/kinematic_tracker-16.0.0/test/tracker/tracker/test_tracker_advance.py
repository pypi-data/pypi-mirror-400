"""."""

import numpy as np
import pytest

from kinematic_tracker.tracker.tracker import UNKNOWN_REPORT_ID, NdKkfTracker


def test_nd_kkf_tracker_advance(tracker1: NdKkfTracker) -> None:
    """."""
    assert tracker1.last_ts_ns == 1234_000_000
    assert tracker1.pre.last_dt == pytest.approx(1.234)
    assert len(tracker1.tracks) == 1
    assert tracker1.tracks[0].ann_id == 123
    assert tracker1.tracks[0].upd_id == 123
    assert tracker1.tracks[0].num_miss == 0
    assert tracker1.tracks[0].num_det == 0
    vec_x_ref = [1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 5, 6]
    assert tracker1.tracks[0].kkf.kalman_filter.statePost[:, 0] == pytest.approx(vec_x_ref)


def test_advance_without_report_ids(tracker: NdKkfTracker) -> None:
    """."""
    tracker.set_measurement_cov(0.01 * np.eye(6))
    tracker.advance(1000_000_000, [np.linspace(1.0, 6.0, num=6)])
    assert len(tracker.tracks) == 1
    assert tracker.tracks[0].ann_id == UNKNOWN_REPORT_ID
    assert tracker.tracks[0].upd_id == UNKNOWN_REPORT_ID
