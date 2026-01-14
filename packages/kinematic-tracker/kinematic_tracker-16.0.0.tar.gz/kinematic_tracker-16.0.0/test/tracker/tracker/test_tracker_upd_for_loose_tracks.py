"""."""

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_upd_for_loose_tracks(tracker: NdKkfTracker) -> None:
    """."""
    tracker.update_for_loose_tracks({}, 0)
    assert tracker.tracks == []
