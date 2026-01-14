"""."""

import numpy as np
import pytest

from kinematic_tracker.association.inv_out import inv_out


def test_inv_out_normal() -> None:
    mat = np.array([[1.0, 2.0, 0.0], [2.0, 3.0, 4.0], [0.0, 4.0, 5.0]])
    res = np.zeros((3, 3))
    inv_out(mat, res)
    ref = [
        [0.047619047619047616, 0.47619047619047616, -0.38095238095238093],
        [0.47619047619047616, -0.23809523809523808, 0.19047619047619047],
        [-0.38095238095238093, 0.19047619047619047, 0.047619047619047616],
    ]
    assert res == pytest.approx(np.array(ref))


def test_inv_out_singular() -> None:
    mat = np.linspace(1.0, 9.0, num=9).reshape(3, 3)
    res = np.zeros((3, 3))
    with pytest.raises(np.linalg.LinAlgError):
        inv_out(mat, res)
