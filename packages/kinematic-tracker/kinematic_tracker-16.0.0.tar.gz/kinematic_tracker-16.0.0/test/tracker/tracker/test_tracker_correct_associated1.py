"""."""

import numpy as np
import pytest

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_nd_kkf_tracker_correct_associated1(tracker1: NdKkfTracker) -> None:
    """."""
    tracker1.predict_all(5234_000_000)
    r2z = [0.1 + np.linspace(1.0, 6.0, num=6)]
    score_rt = tracker1.metric_driver.compute_metric(r2z, tracker1.get_filters())
    tracker1.match_driver.compute_matches(score_rt, tracker1.association.threshold)
    r2id = [456]
    reports, targets = tracker1.match_driver.get_reports_targets()
    tracker1.correct_associated(reports, targets, score_rt, r2z, r2id)
    assert len(tracker1.tracks) == 1
    track = tracker1.tracks[0]
    assert track.ann_id == 123
    assert track.upd_id == 456
    assert track.num_det == 1
    assert track.num_miss == 0
    # fmt: off
    vec_x_ref = [1.0999998750003126, 0.04499988750028129, 0.009999975000062509,
                 2.0999998750003126, 0.04499988750028129, 0.009999975000062509,
                 3.0999998750003126, 0.04499988750028129, 0.009999975000062509,
                 4.05, 5.05, 6.05]
    # fmt: on
    assert track.kkf.kalman_filter.statePost[:, 0] == pytest.approx(np.array(vec_x_ref))
    p_ref = [
        [0.0099999875, 0.00449998875, 0.0009999975, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.00449998875, 80.00405, 40.0009, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0009999975, 40.00089999775, 20.0002, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0099999875, 0.00449998875, 0.0009999975, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.00449998875, 80.00404998988, 40.0009, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0009999975, 40.00089999775, 20.0002, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0099999875, 0.00449998875, 0.0009999975, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.00449998875, 80.00405, 40.0009, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0009999975, 40.000899998, 20.0002, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.005, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.005, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.005],
    ]
    assert track.kkf.kalman_filter.errorCovPost == pytest.approx(np.array(p_ref))
