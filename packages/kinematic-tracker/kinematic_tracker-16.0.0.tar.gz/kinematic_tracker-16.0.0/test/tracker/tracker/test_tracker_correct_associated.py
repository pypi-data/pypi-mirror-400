"""."""

import numpy as np

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_correct_associated(tracker: NdKkfTracker) -> None:
    """."""
    r2z = [np.ones((6, 1))]
    r2id = [567]
    score_rt = np.zeros((1, 0))
    tracker.correct_associated([], [], score_rt, r2z, r2id)
    assert tracker.tracks == []
