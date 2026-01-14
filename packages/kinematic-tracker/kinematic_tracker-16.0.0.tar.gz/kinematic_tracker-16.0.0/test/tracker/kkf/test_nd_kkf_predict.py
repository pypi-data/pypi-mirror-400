"""."""

import numpy as np
import pytest

from kinematic_tracker.nd.gen_xz import NdKkfMatGenXz
from kinematic_tracker.nd.precursors import NdKkfPrecursors
from kinematic_tracker.tracker.kkf import NdKkf


def test_predict_at_zero_vel(kkf_wn: NdKkf, pre: NdKkfPrecursors, gen_xz: NdKkfMatGenXz) -> None:
    """."""
    pre.compute(3.0)
    gen_x = gen_xz.gen_x
    gen_x.fill_f_mat(pre, kkf_wn.kalman_filter.transitionMatrix)
    kkf_wn.predict(pre)
    assert kkf_wn.proc_noise.der_mixer.derivatives == pytest.approx(np.zeros(5))
    assert kkf_wn.kalman_filter.processNoiseCov == pytest.approx(np.zeros((8, 8)))
    p_ref = [
        [285.0, 93.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [93.0, 31.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 294.0, 96.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 96.0, 32.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 303.0, 99.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 99.0, 33.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0],
    ]
    assert kkf_wn.kalman_filter.errorCovPre == pytest.approx(np.array(p_ref))
    assert kkf_wn.kalman_filter.statePre[:, 0] == pytest.approx([1, 0, 2, 0, 3, 0, 4, 5])


def test_predict_nonzero_vel(kkf_wn: NdKkf, pre: NdKkfPrecursors, gen_xz: NdKkfMatGenXz) -> None:
    """."""
    pre.compute(3.0)
    gen_x = gen_xz.gen_x
    gen_x.fill_f_mat(pre, kkf_wn.kalman_filter.transitionMatrix)
    kkf_wn.kalman_filter.statePost[:, 0] = np.linspace(1.0, 8.0, num=8)
    kkf_wn.predict(pre)
    q_ref = [
        [12.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [6.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 48.0, 24.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 24.0, 16.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 108.0, 54.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 54.0, 36.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0],
    ]
    p_ref = [
        [297.0, 99.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [99.0, 35.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 342.0, 120.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 120.0, 48.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 411.0, 153.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 153.0, 69.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 9.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 9.0],
    ]
    assert kkf_wn.kalman_filter.errorCovPre == pytest.approx(np.array(p_ref))
    assert kkf_wn.kalman_filter.processNoiseCov == pytest.approx(np.array(q_ref))
    assert kkf_wn.kalman_filter.statePre[:, 0] == pytest.approx(
        [7.0, 2.0, 15.0, 4.0, 23.0, 6.0, 7.0, 8.0]
    )
