"""."""

import numpy as np
import pytest

from kinematic_tracker.nd.precursors import NdKkfPrecursors
from kinematic_tracker.proc_noise.nd_kkf_dia_noise import NdKkfDiaNoise


def test_fill_proc_cov_diagonal(dia_n: NdKkfDiaNoise, pre: NdKkfPrecursors) -> None:
    """."""
    cov_xx = 1.3 * np.ones((8, 8))
    pre.compute(9.0)
    dia_n.fill_proc_cov(pre, np.empty(8), cov_xx)
    assert cov_xx == pytest.approx(5.678 * np.eye(8))
