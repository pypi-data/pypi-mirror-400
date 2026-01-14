"""."""

import numpy as np
import pytest

from kinematic_tracker.nd.precursors import NdKkfPrecursors


def test_nd_kkf_pre_compute(pre: NdKkfPrecursors) -> None:
    """."""
    pre.compute(3.0)
    assert pre.kin_mat_gen[1].q_mat_dt == pytest.approx(np.zeros((1, 1)))
    assert pre.kin_mat_gen[1].f_mat_dt == pytest.approx(np.eye(1))
    ref_f2 = [[1.0, 3.0], [0.0, 1.0]]
    ref_f3 = [[1.0, 3.0, 4.5], [0.0, 1.0, 3.0], [0.0, 0.0, 1.0]]
    assert pre.kin_mat_gen[2].f_mat_dt == pytest.approx(np.array(ref_f2))
    assert pre.kin_mat_gen[3].f_mat_dt == pytest.approx(np.array(ref_f3))
    ref_q2 = [[9.0, 4.5], [4.5, 3.0]]
    ref_q3 = [[12.149999999999999, 10.125, 4.5], [10.125, 9.0, 4.5], [4.5, 4.5, 3.0]]
    assert pre.kin_mat_gen[2].q_mat_dt == pytest.approx(np.array(ref_q2))
    assert pre.kin_mat_gen[3].q_mat_dt == pytest.approx(np.array(ref_q3))
    assert pre.kin_mat_gen[4].q_mat_dt == pytest.approx(np.zeros((4, 4)))
    assert pre.kin_mat_gen[4].f_mat_dt == pytest.approx(np.eye(4))
