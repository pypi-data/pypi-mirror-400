"""."""

import numpy as np
import pytest

from kinematic_tracker.matrices.const_jerk.fundamental import FundMatCj
from kinematic_tracker.matrices.const_jerk.proc_cov import WhiteNoiseMatCj


def test_proc_cov_cj() -> None:
    """."""
    wn_gen = WhiteNoiseMatCj()
    wn_gen.compute(252.0)
    cov = wn_gen.q_mat
    # fmt: off
    ref = [256096265048064., 3556892570112., 33875167334.4, 168031584.,
           3556892570112.,  50812751001.6,    504094752.,   2667168.,
           33875167334.4,     504094752.,      5334336.,     31752.,
           168031584.,       2667168.,        31752.,       252.]
    # fmt: on
    assert cov == pytest.approx(np.array(ref).reshape(4, 4))


def test_proc_cov_add() -> None:
    """."""
    wn_gen = WhiteNoiseMatCj()
    wn_gen.compute(0.1)
    q1 = wn_gen.q_mat.copy()
    wn_gen.compute(0.2)
    q2 = wn_gen.q_mat.copy()
    wn_gen.compute(0.3)
    q3 = wn_gen.q_mat.copy()
    fu_gen = FundMatCj()
    fu_gen.compute(0.2)
    f_mat = fu_gen.f_mat
    diff = np.dot(f_mat, np.dot(q1, f_mat.T)) + q2 - q3
    assert diff == pytest.approx(0.0)
