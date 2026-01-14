"""."""

import numpy as np
import pytest

from kinematic_tracker.matrices.const_vel.fundamental import FundMatCv


def test_get_fund_mat_cv() -> None:
    """."""
    fu_mat = FundMatCv()
    fu_mat.compute(0.1)
    assert fu_mat.f_mat == pytest.approx(np.array([[1.0, 0.1], [0.0, 1.0]]))
