"""."""

import numpy as np
import pytest

from kinematic_tracker.matrices.const_acc.fundamental import FundMatCa


def test_get_fund_mat_ca() -> None:
    """."""
    fu_gen = FundMatCa()
    fu_gen.compute(0.1)
    f_mat = fu_gen.f_mat
    ref = [[1.0, 0.1, 0.005], [0.0, 1.0, 0.1], [0.0, 0.0, 1.0]]
    assert f_mat == pytest.approx(np.array(ref))
