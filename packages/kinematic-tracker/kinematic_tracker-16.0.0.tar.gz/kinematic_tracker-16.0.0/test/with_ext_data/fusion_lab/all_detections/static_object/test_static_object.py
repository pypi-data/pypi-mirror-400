"""."""

from kinematic_tracker.tracker.tracker import NdKkfTracker

from .conftest import assert_quality


def test_static_object_diagonal(tracker: NdKkfTracker) -> None:
    """."""
    tracker.pn_meta.noise_kind = tracker.pn_meta.noise_kind.DIAGONAL
    tracker.pn_meta.factor = 0.25
    assert_quality(tracker, 0.0130804)  # CTL shows 0.013080343950653894


def test_static_object_fini_diff(tracker: NdKkfTracker) -> None:
    """."""
    assert_quality(tracker, 0.010221)  # In CTL ATE is 0.010220974499285867
