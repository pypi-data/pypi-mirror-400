"""."""

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_upd_for_loose_tracks2(tracker1: NdKkfTracker) -> None:
    """."""
    tracker1.update_for_loose_tracks({}, 1)
    assert len(tracker1.tracks) == 1
    assert tracker1.tracks[0].num_miss == 1

    tracker1.update_for_loose_tracks({}, 1)
    assert len(tracker1.tracks) == 1
    assert tracker1.tracks[0].num_miss == 2

    tracker1.update_for_loose_tracks({}, 1)
    assert len(tracker1.tracks) == 1
    assert tracker1.tracks[0].num_miss == 3

    tracker1.update_for_loose_tracks({}, 1)
    assert len(tracker1.tracks) == 0
