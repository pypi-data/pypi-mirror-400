"""."""

import numpy as np
import pytest

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_get_track(tracker: NdKkfTracker) -> None:
    """."""
    tracker.gen_kf.f_mat[:] = np.eye(12)
    vec_z = np.linspace(1.0, 6.0, num=6)
    tracker.set_measurement_cov(0.01 * np.eye(6))
    track = tracker.get_track(vec_z, 123)
    vec_x_ref = [1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 5, 6]
    assert track.kkf.kalman_filter.statePost[:, 0] == pytest.approx(vec_x_ref)
    assert track.kkf.kalman_filter.transitionMatrix == pytest.approx(np.eye(12))
    assert track.ann_id == 123
    assert track.id == -1
    assert track.creation_id == 0
