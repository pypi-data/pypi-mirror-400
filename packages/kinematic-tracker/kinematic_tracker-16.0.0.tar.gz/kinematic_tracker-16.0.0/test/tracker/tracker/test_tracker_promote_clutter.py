"""."""

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_promote_clutter(tracker: NdKkfTracker) -> None:
    """."""
    tracker.promote_clutter_eventually()
    assert len(tracker.tracks) == 0
