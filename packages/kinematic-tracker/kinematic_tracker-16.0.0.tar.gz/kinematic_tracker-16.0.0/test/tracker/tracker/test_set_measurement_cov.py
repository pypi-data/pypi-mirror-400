"""."""

import numpy as np
import pytest

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_set_measurement_cov_normal(tracker: NdKkfTracker) -> None:
    """."""
    assert tracker.cov_zz is None
    tracker.set_measurement_cov(0.678 * np.eye(6))
    assert tracker.cov_zz == pytest.approx(0.678 * np.eye(6))


def test_set_measurement_cov_wrong_shape(tracker: NdKkfTracker) -> None:
    """."""
    with pytest.raises(ValueError):
        tracker.set_measurement_cov(np.ones(6))

    with pytest.raises(ValueError):
        tracker.set_measurement_cov(np.eye(5))

    with pytest.raises(ValueError):
        tracker.set_measurement_cov(np.zeros((6, 6, 6)))
