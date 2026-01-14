"""."""

import numpy as np
import pytest

from kinematic_tracker.tracker.tracker import NdKkfTracker


@pytest.fixture
def tracker() -> NdKkfTracker:
    """."""
    tracker = NdKkfTracker([3, 1], [3, 3])
    tracker.association.threshold = 0.56
    tracker.set_association_metric('mahalanobis', 0.22 * 6)
    tracker.set_association_method('greedy')
    tracker.num_det_min = 2
    return tracker


@pytest.fixture
def tracker1(tracker: NdKkfTracker) -> NdKkfTracker:
    """."""
    tracker.set_measurement_cov(0.01 * np.eye(6))
    tracker.association.threshold = 0.56
    r2z = [np.linspace(1.0, 6.0, num=6)]
    r2id = [123]
    tracker.advance(1234_000_000, r2z, r2id)
    return tracker
