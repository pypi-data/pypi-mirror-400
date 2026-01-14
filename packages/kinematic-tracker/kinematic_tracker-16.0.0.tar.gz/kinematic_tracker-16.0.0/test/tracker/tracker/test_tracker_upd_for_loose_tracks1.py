"""."""

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_upd_for_loose_tracks1(tracker1: NdKkfTracker) -> None:
    """."""
    tracker1.update_for_loose_tracks({0: 0}, 1)
    assert len(tracker1.tracks) == 1
    assert tracker1.tracks[0].num_miss == 0
