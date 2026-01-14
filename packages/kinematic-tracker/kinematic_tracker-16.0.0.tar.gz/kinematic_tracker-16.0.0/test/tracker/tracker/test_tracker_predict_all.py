"""."""

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_predict_all(tracker: NdKkfTracker) -> None:
    """."""
    tracker.predict_all(1234_000_000)
    assert tracker.last_ts_ns == 1234_000_000
    assert tracker.pre.last_dt == 1.234
    assert len(tracker.tracks) == 0
