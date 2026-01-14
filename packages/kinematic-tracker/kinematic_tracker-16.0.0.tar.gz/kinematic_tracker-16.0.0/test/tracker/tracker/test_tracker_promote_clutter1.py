"""."""

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_promote_clutter1(tracker1: NdKkfTracker) -> None:
    """."""
    tracker1.tracks[0].num_det = 5
    tracker1.promote_clutter_eventually()
    assert tracker1.tracks[0].id == 0
