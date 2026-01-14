"""."""

import numpy as np
import pytest

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_get_match(tracker: NdKkfTracker) -> None:
    """."""
    tracker.set_measurement_cov(np.eye(tracker.gen_xz.num_z))
    score_rt = tracker.metric_driver.compute_metric([np.ones(6)], [])
    tracker.match_driver.compute_matches(score_rt, tracker.association.threshold)
    assert tracker.match_driver.num_matches == 0


def test_nd_kkf_tracker_get_match1(tracker1: NdKkfTracker) -> None:
    """."""
    tracker1.predict_all(5234_000_000)
    score_rt = tracker1.metric_driver.compute_metric(
        [0.1 + np.linspace(1.0, 6.0, num=6)], tracker1.get_filters()
    )
    tracker1.match_driver.compute_matches(score_rt, tracker1.association.threshold)
    assert tracker1.match_driver.num_matches == 1
    assert score_rt == pytest.approx(0.84789335 * np.eye(1))
