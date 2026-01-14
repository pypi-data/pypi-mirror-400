"""."""

import numpy as np
import pytest

from kinematic_tracker.matrices.const_pos.fundamental import FundMatCp


def test_get_fund_mat_cp() -> None:
    """."""
    fu_mat = FundMatCp()
    fu_mat.compute(0.1)
    assert fu_mat.f_mat == pytest.approx(np.eye(1))
