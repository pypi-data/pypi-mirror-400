"""."""

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_get_filters(tracker1: NdKkfTracker) -> None:
    """."""
    filters = tracker1.get_filters()
    assert len(filters) == 1
