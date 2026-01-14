"""."""

import numpy as np
import pytest

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_internal_check_undefined_cov_zz(tracker: NdKkfTracker) -> None:
    """."""
    with pytest.raises(RuntimeError):
        tracker.internal_check()


def test_internal_check_incomplete_cov_zz(tracker: NdKkfTracker) -> None:
    """."""
    tracker.cov_zz = np.eye(6)
    tracker.cov_zz[1, 2] = np.nan
    with pytest.raises(RuntimeError):
        tracker.internal_check()
