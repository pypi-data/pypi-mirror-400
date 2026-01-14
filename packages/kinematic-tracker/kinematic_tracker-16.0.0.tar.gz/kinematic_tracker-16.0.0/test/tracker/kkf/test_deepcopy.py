"""Check the magic method __deepcopy__."""

import copy

from kinematic_tracker.tracker.kkf import NdKkf


def test_nd_kkf_deepcopy(kkf_wn: NdKkf) -> None:
    """."""
    assert kkf_wn.kalman_filter.gain.shape == (8, 5)
    kkf_cp = copy.deepcopy(kkf_wn)
    assert kkf_cp.kalman_filter.measurementMatrix.shape == (5, 8)
    assert kkf_cp.kalman_filter.measurementNoiseCov.shape == (5, 5)
    assert kkf_cp.kalman_filter.gain.shape == (8, 5)
