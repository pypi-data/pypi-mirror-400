"""."""

import numpy as np
import pytest

from kinematic_tracker.matrices.const_acc.fundamental import FundMatCa
from kinematic_tracker.matrices.const_acc.proc_cov import WhiteNoiseMatCa


def test_proc_cov_ca() -> None:
    """."""
    wn_gen = WhiteNoiseMatCa()
    wn_gen.compute(30.0)
    cov = wn_gen.q_mat
    ref = np.array(
        [(1215000.0, 101250.0, 4500.0), (101250.0, 9000.0, 450.0), (4500.0, 450.0, 30.0)]
    )
    assert cov == pytest.approx(np.array(ref))


def test_proc_cov_add() -> None:
    """."""
    wn_gen = WhiteNoiseMatCa()
    wn_gen.compute(0.1)
    q1 = wn_gen.q_mat.copy()
    wn_gen.compute(0.2)
    q2 = wn_gen.q_mat.copy()
    wn_gen.compute(0.3)
    q3 = wn_gen.q_mat.copy()
    fu_gen = FundMatCa()
    fu_gen.compute(0.2)
    f_mat = fu_gen.f_mat
    diff = np.dot(f_mat, np.dot(q1, f_mat.T)) + q2 - q3
    assert diff == pytest.approx(0.0)
