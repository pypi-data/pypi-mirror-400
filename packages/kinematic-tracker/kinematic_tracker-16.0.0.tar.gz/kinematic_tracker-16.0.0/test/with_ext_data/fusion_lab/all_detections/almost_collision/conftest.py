"""."""

import pytest

from kinematic_tracker.tracker.tracker import NdKkfTracker


@pytest.fixture
def tracker() -> NdKkfTracker:
    """."""
    tracker = NdKkfTracker([3, 1], [3, 3])
    tracker.set_measurement_std_dev(0, 0.5)
    tracker.set_measurement_std_dev(1, 0.02)
    tracker.set_association_metric('mahalanobis')
    tracker.num_det_min = 5
    tracker.num_misses_max = 5
    return tracker
