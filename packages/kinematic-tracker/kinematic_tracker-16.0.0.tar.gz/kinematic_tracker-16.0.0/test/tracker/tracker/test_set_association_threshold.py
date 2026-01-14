"""."""

import pytest

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_set_association_threshold(tracker: NdKkfTracker) -> None:
    """."""
    tracker.set_association_threshold(0.4567)
    assert tracker.association.threshold == pytest.approx(0.4567)

    for invalid_value in (-1.0, 0.0, 1.0, 2.0):
        with pytest.raises(ValueError):
            tracker.set_association_threshold(invalid_value)
