"""."""

import numpy as np
import pytest

from kinematic_tracker.matrices.const_vel.fundamental import FundMatCv
from kinematic_tracker.matrices.const_vel.proc_cov import WhiteNoiseMatCv


def test_proc_cov_cv() -> None:
    """."""
    wn_mat = WhiteNoiseMatCv()
    wn_mat.compute(6.0)
    assert wn_mat.q_mat == pytest.approx(np.array(((72.0, 18.0), (18.0, 6.0))))


def test_proc_cov_add_cv() -> None:
    """."""
    wn_mat = WhiteNoiseMatCv()
    wn_mat.compute(0.1)
    q1 = wn_mat.q_mat.copy()
    wn_mat.compute(0.2)
    q2 = wn_mat.q_mat.copy()
    wn_mat.compute(0.3)
    q3 = wn_mat.q_mat.copy()
    fu_mat = FundMatCv()
    fu_mat.compute(0.2)
    f_mat = fu_mat.f_mat
    diff = np.dot(f_mat, np.dot(q1, f_mat.T)) + q2 - q3
    assert diff == pytest.approx(0.0)
