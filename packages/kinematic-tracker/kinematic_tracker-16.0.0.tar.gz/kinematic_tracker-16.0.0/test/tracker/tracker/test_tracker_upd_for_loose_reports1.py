"""."""

import numpy as np

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_upd_for_loose_reports1(tracker1: NdKkfTracker) -> None:
    """."""
    o2z = [0.1 + np.linspace(1.0, 6.0, num=6)]
    o2id = [124]
    tracker1.update_for_loose_reports({0: 0}, o2z, o2id)
    assert len(tracker1.tracks) == 1
