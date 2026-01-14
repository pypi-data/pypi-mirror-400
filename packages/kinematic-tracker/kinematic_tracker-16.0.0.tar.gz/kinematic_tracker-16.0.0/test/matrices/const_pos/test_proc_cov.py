"""."""

import numpy as np
import pytest

from kinematic_tracker.matrices.const_pos.fundamental import FundMatCp
from kinematic_tracker.matrices.const_pos.proc_cov import WhiteNoiseMatCp


def test_proc_cov_cp() -> None:
    """."""
    wn_mat = WhiteNoiseMatCp()
    wn_mat.compute(2.0)
    assert wn_mat.q_mat == pytest.approx(np.array([[2.0]]))


def test_proc_cov_add_cp() -> None:
    """."""
    wn_mat = WhiteNoiseMatCp()
    wn_mat.compute(0.1)
    q1 = wn_mat.q_mat.copy()
    wn_mat.compute(0.2)
    q2 = wn_mat.q_mat.copy()
    wn_mat.compute(0.3)
    q3 = wn_mat.q_mat.copy()
    fu_mat = FundMatCp()
    f_mat = fu_mat.f_mat
    diff = np.dot(f_mat, np.dot(q1, f_mat.T)) + q2 - q3
    assert diff == pytest.approx(0.0)
