"""."""

import numpy as np
import pytest

from kinematic_tracker.nd.gen_xz import NdKkfMatGenXz
from kinematic_tracker.nd.precursors import NdKkfPrecursors
from kinematic_tracker.tracker.kkf import NdKkf


def test_nd_kkf_correct(kkf_wn: NdKkf, pre: NdKkfPrecursors, gen_xz: NdKkfMatGenXz) -> None:
    """."""
    pre.compute(3.0)
    gen_x = gen_xz.gen_x
    gen_x.fill_f_mat(pre, kkf_wn.kalman_filter.transitionMatrix)
    kkf_wn.predict(pre)
    vec_z = 1.0 + np.linspace(1.0, 5.0, num=5)
    kkf_wn.correct(vec_z)
    x_ref = [1.979381443, 0.3195876288, 2.98, 0.32, 3.980582524, 0.3203883495, 4.5, 5.5]
    assert kkf_wn.kalman_filter.statePost[:, 0] == pytest.approx(x_ref)
    p_ref = [
        [5.876288659793814, 1.917525773195876, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [1.9175257731958761, 1.27835051546392, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 5.88, 1.9200000000000002, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.92, 1.2800000000000005, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 5.883495145631068, 1.9223300970873787, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 1.9223300970873785, 1.2815533980582536, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0],
    ]
    assert kkf_wn.kalman_filter.errorCovPost == pytest.approx(np.array(p_ref))
