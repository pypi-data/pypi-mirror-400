"""."""

import numpy as np
import pytest

from .conftest import KinematicMatrices, get_is_order_implemented


def test_is_order_implemented() -> None:
    """."""
    assert not get_is_order_implemented(0)
    for o in range(1, 5):
        assert get_is_order_implemented(o)
    assert not get_is_order_implemented(5)


def test_kinematic_matrices_compute() -> None:
    """."""
    km = KinematicMatrices(3)
    km.compute_f_mat(8.0)
    km.compute_q_mat(2.0)
    f_mat_ref = [[1.0, 8.0, 32.0], [0.0, 1.0, 8.0], [0.0, 0.0, 1.0]]
    q_mat_ref = [
        [1.6, 2.0, 1.3333333333333333],
        [2.0, 2.6666666666666665, 2.0],
        [1.3333333333333333, 2.0, 2.0],
    ]
    assert km.f_mat_dt == pytest.approx(np.array(f_mat_ref))
    assert km.q_mat_dt == pytest.approx(np.array(q_mat_ref))
