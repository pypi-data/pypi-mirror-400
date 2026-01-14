"""."""

import numpy as np
import pytest

from kinematic_tracker.tracker.tracker import UNKNOWN_REPORT_ID, NdKkfTracker


@pytest.fixture
def tracker() -> NdKkfTracker:
    return NdKkfTracker([3, 1], [2, 2], [2, 1])


def test_set_max_reports_and_targets(tracker: NdKkfTracker) -> None:
    tracker.set_max_reports_and_targets(123, 765)
    assert len(tracker.unknown_report_ids) == 123
    assert np.all(tracker.unknown_report_ids == UNKNOWN_REPORT_ID)
    assert len(tracker.match_driver.reports) == 123
    assert len(tracker.match_driver.targets) == 123
    assert tracker.match_driver.score_rc.shape == (123, 765)
    assert tracker.metric_driver.metric_rt.shape == (123, 765)
