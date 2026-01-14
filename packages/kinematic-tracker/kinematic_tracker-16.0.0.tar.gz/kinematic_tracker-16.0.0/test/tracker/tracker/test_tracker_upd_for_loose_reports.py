"""."""

import numpy as np
import pytest

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_upd_for_loose_reports(tracker: NdKkfTracker) -> None:
    """."""
    o2z = [np.linspace(1.0, 6.0, num=6)]
    o2id = [123]
    tracker.set_measurement_cov(0.01 * np.eye(6))
    tracker.update_for_loose_reports({}, o2z, o2id)
    assert len(tracker.tracks) == 1
    vec_x_ref = [1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 5, 6]
    track = tracker.tracks[0]
    assert track.kkf.kalman_filter.statePre[:, 0] == pytest.approx(vec_x_ref)
    r_ref = [
        [0.01, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.01, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.01, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.01, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.01, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.01],
    ]
    assert track.kkf.kalman_filter.measurementNoiseCov == pytest.approx(np.array(r_ref))
    p_ref = [
        [0.01, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01],
    ]
    assert track.kkf.kalman_filter.errorCovPre == pytest.approx(np.array(p_ref))
    assert track.kkf.kalman_filter.transitionMatrix == pytest.approx(np.zeros((12, 12)))
    assert track.kkf.kalman_filter.processNoiseCov == pytest.approx(np.zeros((12, 12)))
