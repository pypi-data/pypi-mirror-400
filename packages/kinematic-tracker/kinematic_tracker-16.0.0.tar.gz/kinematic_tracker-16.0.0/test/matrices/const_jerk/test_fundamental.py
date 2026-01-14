"""."""

import numpy as np
import pytest

from kinematic_tracker.matrices.const_jerk.fundamental import FundMatCj


def test_get_fund_mat_cj() -> None:
    """."""
    gen = FundMatCj()
    gen.compute(12.0)
    f_mat = gen.f_mat
    ref = [1.0, 12.0, 72.0, 288.0, 0.0, 1.0, 12.0, 72.0, 0.0, 0.0, 1.0, 12.0, 0.0, 0.0, 0.0, 1.0]
    assert f_mat == pytest.approx(np.array(ref).reshape(4, 4))
